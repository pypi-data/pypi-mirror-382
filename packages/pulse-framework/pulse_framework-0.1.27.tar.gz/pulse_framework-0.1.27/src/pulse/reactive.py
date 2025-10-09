import asyncio
import copy
import inspect
from contextvars import ContextVar
from typing import (
    Any,
    Callable,
    Coroutine,
    Generic,
    Optional,
    ParamSpec,
    TypeVar,
    cast,
)


from pulse.helpers import create_task, schedule_on_loop, values_equal

T = TypeVar("T")
P = ParamSpec("P")


class Signal(Generic[T]):
    def __init__(self, value: T, name: Optional[str] = None):
        self.value = value
        self.name = name
        self.obs: list[Computed | Effect] = []
        self._obs_change_listeners: list[Callable[[int], None]] = []
        self.last_change = -1

    def read(self) -> T:
        rc = REACTIVE_CONTEXT.get()
        if rc.scope is not None:
            rc.scope.register_dep(self)
        return self.value

    def __call__(self) -> T:
        return self.read()

    def unwrap(self) -> T:
        """Return the current value while registering subscriptions."""
        return self.read()

    def __copy__(self):
        return self.__class__(self.value, name=self.name)

    def __deepcopy__(self, memo):
        if id(self) in memo:
            return memo[id(self)]
        new_value = copy.deepcopy(self.value, memo)
        new_signal = self.__class__(new_value, name=self.name)
        memo[id(self)] = new_signal
        return new_signal

    def _add_obs(self, obs: "Computed | Effect"):
        prev = len(self.obs)
        self.obs.append(obs)
        if prev == 0 and len(self.obs) == 1:
            for cb in list(self._obs_change_listeners):
                cb(len(self.obs))

    def _remove_obs(self, obs: "Computed | Effect"):
        if obs in self.obs:
            self.obs.remove(obs)
            if len(self.obs) == 0:
                for cb in list(self._obs_change_listeners):
                    cb(0)

    def on_observer_change(self, cb: Callable[[int], None]) -> Callable[[], None]:
        self._obs_change_listeners.append(cb)

        def off():
            try:
                self._obs_change_listeners.remove(cb)
            except ValueError:
                pass

        return off

    def write(self, value: T):
        if values_equal(value, self.value):
            return
        increment_epoch()
        self.value = value
        self.last_change = epoch()
        for obs in self.obs:
            obs._push_change()


class Computed(Generic[T]):
    def __init__(self, fn: Callable[..., T], name: Optional[str] = None):
        self.fn = fn
        self.value: T = None  # type: ignore
        self.name = name
        self.dirty = False
        self.on_stack = False
        self.last_change: int = -1
        # Dep -> last_change
        self.deps: dict[Signal | Computed, int] = {}
        self.obs: list[Computed | Effect] = []
        self._obs_change_listeners: list[Callable[[int], None]] = []

    def read(self) -> T:
        if self.on_stack:
            raise RuntimeError("Circular dependency detected")

        rc = REACTIVE_CONTEXT.get()
        # Ensure this computed is up-to-date before registering as a dep
        self._recompute_if_necessary()
        if rc.scope is not None:
            # Register after potential recompute so the scope records the
            # latest observed version for this computed
            rc.scope.register_dep(self)
        return self.value

    def __call__(self) -> T:
        return self.read()

    def unwrap(self) -> T:
        """Return the current value while registering subscriptions."""
        return self.read()

    def __copy__(self):
        return self.__class__(self.fn, name=self.name)

    def __deepcopy__(self, memo):
        if id(self) in memo:
            return memo[id(self)]
        fn_copy = copy.deepcopy(self.fn, memo)
        name_copy = copy.deepcopy(self.name, memo)
        new_computed = self.__class__(fn_copy, name=name_copy)
        memo[id(self)] = new_computed
        return new_computed

    def _push_change(self):
        if self.dirty:
            return

        self.dirty = True
        for obs in self.obs:
            obs._push_change()

    def _recompute(self):
        prev_value = self.value
        prev_deps = set(self.deps)
        with Scope() as scope:
            if self.on_stack:
                raise RuntimeError("Circular dependency detected")
            self.on_stack = True
            execution_epoch = epoch()
            self.value = self.fn()
            if epoch() != execution_epoch:
                raise RuntimeError(
                    f"Detected write to a signal in computed {self.name}. Computeds should be read-only."
                )
            self.on_stack = False
            self.dirty = False
            if not values_equal(prev_value, self.value):
                self.last_change = execution_epoch

            if len(scope.effects) > 0:
                raise RuntimeError(
                    "An effect was created within a computed variable's function. "
                    "This behavior is not allowed, computed variables should be pure calculations."
                )

        # Update deps and their observed versions to the values seen during this recompute
        self.deps = scope.deps
        new_deps = set(self.deps)
        add_deps = new_deps - prev_deps
        remove_deps = prev_deps - new_deps
        for dep in add_deps:
            dep._add_obs(self)
        for dep in remove_deps:
            dep._remove_obs(self)

    def _recompute_if_necessary(self):
        if self.last_change < 0:
            self._recompute()
            return
        if not self.dirty:
            return

        for dep in self.deps:
            if isinstance(dep, Computed):
                dep._recompute_if_necessary()
            # Only recompute if a dependency has changed beyond the version
            # we last observed during our previous recompute
            last_seen = self.deps.get(dep, -1)
            if dep.last_change > last_seen:
                self._recompute()
                return

        self.dirty = False

    def _add_obs(self, obs: "Computed | Effect"):
        prev = len(self.obs)
        self.obs.append(obs)
        if prev == 0 and len(self.obs) == 1:
            for cb in list(self._obs_change_listeners):
                cb(len(self.obs))

    def _remove_obs(self, obs: "Computed | Effect"):
        if obs in self.obs:
            self.obs.remove(obs)
            if len(self.obs) == 0:
                for cb in list(self._obs_change_listeners):
                    cb(0)

    def on_observer_change(self, cb: Callable[[int], None]) -> Callable[[], None]:
        self._obs_change_listeners.append(cb)

        def off():
            try:
                self._obs_change_listeners.remove(cb)
            except ValueError:
                pass

        return off


EffectCleanup = Callable[[], None]
# Split effect function types into sync and async for clearer typing
EffectFn = Callable[[], Optional[EffectCleanup]]
AsyncEffectFn = Callable[[], Coroutine[Any, Any, Optional[EffectCleanup]]]


class Effect:
    """
    Synchronous effect and base class. Use AsyncEffect for async effects.
    Both are isinstance(Effect).
    """

    def __init__(
        self,
        fn: EffectFn,
        name: Optional[str] = None,
        immediate: bool = False,
        lazy: bool = False,
        on_error: Optional[Callable[[Exception], None]] = None,
        deps: Optional[list[Signal | Computed]] = None,
    ):
        self.fn = fn  # type: ignore[assignment]
        self.name = name
        self.on_error = on_error
        self.cleanup_fn: Optional[EffectCleanup] = None
        self.deps: dict[Signal | Computed, int] = {}
        self.children: list[Effect] = []
        self.parent: Optional[Effect] = None
        self.runs = 0
        self.last_run = -1
        self.scope: Optional[Scope] = None
        self.batch: Optional[Batch] = None
        self._explicit_deps: Optional[list[Signal | Computed]] = deps
        self.immediate = immediate
        self._lazy = lazy

        if immediate and lazy:
            raise ValueError("An effect cannot be boht immediate and lazy")

        rc = REACTIVE_CONTEXT.get()
        if rc.scope is not None:
            rc.scope.register_effect(self)

        if immediate:
            self.run()
        elif not lazy:
            self.schedule()

    def _cleanup_before_run(self):
        for child in self.children:
            child._cleanup_before_run()
        if self.cleanup_fn:
            self.cleanup_fn()

    def dispose(self):
        self.unschedule()
        for child in self.children.copy():
            child.dispose()
        if self.cleanup_fn:
            self.cleanup_fn()
        for dep in self.deps:
            dep.obs.remove(self)
        if self.parent:
            self.parent.children.remove(self)

    def schedule(self):
        # Immediate effects run right away when scheduled and do not enter a batch
        if self.immediate:
            self.run()
            return
        rc = REACTIVE_CONTEXT.get()
        batch = rc.batch
        batch.register_effect(self)
        self.batch = batch

    def unschedule(self):
        if self.batch is not None:
            self.batch.effects.remove(self)
            self.batch = None

    def _push_change(self):
        self.schedule()

    def _should_run(self):
        return self.runs == 0 or self._deps_changed_since_last_run()

    def _deps_changed_since_last_run(self):
        for dep in self.deps:
            if isinstance(dep, Computed):
                dep._recompute_if_necessary()
            last_seen = self.deps.get(dep, -1)
            if dep.last_change > last_seen:
                return True
        return False

    def __call__(self):
        self.run()

    def flush(self) -> None:
        """If scheduled in a batch, remove and run immediately."""
        if self.batch is not None:
            self.batch.effects.remove(self)
            self.batch = None
            # Run now (respects IS_PRERENDERING and error handling)
            self.run()

    def _handle_error(self, exc: Exception) -> None:
        if callable(self.on_error):
            self.on_error(exc)
            return
        handler = getattr(REACTIVE_CONTEXT.get(), "on_effect_error", None)
        if callable(handler):
            handler(self, exc)
            return
        raise exc

    def _apply_scope_results(self, scope: "Scope") -> None:
        self.children = scope.effects
        for child in self.children:
            child.parent = self

        prev_deps = set(self.deps)
        if self._explicit_deps is not None:
            self.deps = {dep: dep.last_change for dep in self._explicit_deps}
        else:
            self.deps = scope.deps
        new_deps = set(self.deps)
        add_deps = new_deps - prev_deps
        remove_deps = prev_deps - new_deps
        for dep in add_deps:
            dep._add_obs(self)
            is_dirty = isinstance(dep, Computed) and dep.dirty
            has_changed = isinstance(dep, Signal) and dep.last_change > self.deps.get(
                dep, -1
            )
            if is_dirty or has_changed:
                self.schedule()
        for dep in remove_deps:
            dep._remove_obs(self)

    def _copy_kwargs(self):
        deps = None
        if self._explicit_deps is not None:
            deps = list(self._explicit_deps)
        return {
            "fn": self.fn,
            "name": self.name,
            "immediate": self.immediate,
            "lazy": self._lazy,
            "on_error": self.on_error,
            "deps": deps,
        }

    def __copy__(self):
        kwargs = self._copy_kwargs()
        return type(self)(**kwargs)

    def __deepcopy__(self, memo):
        if id(self) in memo:
            return memo[id(self)]
        kwargs = self._copy_kwargs()
        kwargs["fn"] = copy.deepcopy(self.fn, memo)
        kwargs["name"] = copy.deepcopy(self.name, memo)
        kwargs["on_error"] = copy.deepcopy(self.on_error, memo)
        deps = kwargs.get("deps")
        if deps is not None:
            kwargs["deps"] = list(deps)
        new_effect = type(self)(**kwargs)
        memo[id(self)] = new_effect
        return new_effect

    def run(self):
        with Untrack():
            try:
                self._cleanup_before_run()
            except Exception as e:
                self._handle_error(e)
        self._execute()

    def _execute(self) -> None:
        execution_epoch = epoch()
        with Scope() as scope:
            # Clear batch *before* running as we may update a signal that causes
            # this effect to be rescheduled.
            self.batch = None
            try:
                self.cleanup_fn = self.fn()
            except Exception as e:
                self._handle_error(e)
            self.runs += 1
            self.last_run = execution_epoch
        self._apply_scope_results(scope)


class AsyncEffect(Effect):
    def __init__(
        self,
        fn: AsyncEffectFn,
        name: Optional[str] = None,
        lazy: bool = False,
        on_error: Optional[Callable[[Exception], None]] = None,
        deps: Optional[list[Signal | Computed]] = None,
    ):
        super().__init__(
            fn=fn,  # type: ignore[arg-type]
            name=name,
            immediate=False,
            lazy=lazy,
            on_error=on_error,
            deps=deps,
        )
        # Track an async task when running async effects
        self._task: Optional[asyncio.Task] = None

    def _task_name(self) -> str:
        base = self.name or "effect"
        return f"effect:{base}"

    def _copy_kwargs(self):
        kwargs = super()._copy_kwargs()
        kwargs.pop("immediate", None)
        return kwargs

    def _execute(self) -> None:
        execution_epoch = epoch()

        # Clear batch *before* running as we may update a signal that causes
        # this effect to be rescheduled.
        self.batch = None

        # Cancel any previous run still in flight
        self.cancel()

        async def _runner():
            nonlocal execution_epoch
            with Scope() as scope:
                try:
                    result = cast(AsyncEffectFn, self.fn)()
                    if inspect.isawaitable(result):
                        self.cleanup_fn = await result
                    else:
                        # Support accidental non-async returns in async-annotated fns
                        self.cleanup_fn = result
                except asyncio.CancelledError:
                    # Swallow cancellation
                    return
                except Exception as e:  # noqa: BLE001
                    self._handle_error(e)
                self.runs += 1
                self.last_run = execution_epoch
            self._apply_scope_results(scope)

        self._task = create_task(_runner(), name=self._task_name())

    def cancel(self) -> None:
        self.unschedule()
        if self._task and not self._task.done():
            self._task.cancel()

    def dispose(self):
        # Run children cleanups first, then cancel in-flight task
        self.unschedule()
        if self._task and not self._task.done():
            self._task.cancel()
        for child in self.children.copy():
            child.dispose()
        if self.cleanup_fn:
            self.cleanup_fn()
        for dep in self.deps:
            dep.obs.remove(self)
        if self.parent:
            self.parent.children.remove(self)


class Batch:
    def __init__(
        self, effects: Optional[list[Effect]] = None, name: Optional[str] = None
    ) -> None:
        self.effects: list[Effect] = effects or []
        self.name = name

    def register_effect(self, effect: Effect):
        if effect not in self.effects:
            self.effects.append(effect)

    def flush(self):
        token = None
        rc = REACTIVE_CONTEXT.get()
        if rc.batch is not self:
            token = REACTIVE_CONTEXT.set(ReactiveContext(rc.epoch, self, rc.scope))

        MAX_ITERS = 10000
        iters = 0

        while len(self.effects) > 0:
            if iters > MAX_ITERS:
                raise RuntimeError(
                    f"Pulse's reactive system registered more than {MAX_ITERS} iterations. There is likely an update cycle in your application.\n"
                    "This is most often caused through a state update during rerender or in an effect that ends up triggering the same rerender or effect."
                )

            # This ensures the epoch is incremented *after* all the signal
            # writes and associated effects have been run.

            current_effects = self.effects
            self.effects = []

            for effect in current_effects:
                effect.batch = None
                if not effect._should_run():
                    continue
                try:
                    effect.run()
                except Exception as exc:
                    effect._handle_error(exc)

            iters += 1

        if token:
            REACTIVE_CONTEXT.reset(token)

    def __enter__(self):
        rc = REACTIVE_CONTEXT.get()
        # Create a new immutable reactive context with updated batch
        self._token = REACTIVE_CONTEXT.set(
            ReactiveContext(rc.epoch, self, rc.scope, rc.on_effect_error)
        )
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.flush()
        # Restore previous reactive context
        REACTIVE_CONTEXT.reset(self._token)


class GlobalBatch(Batch):
    def __init__(self) -> None:
        self.is_scheduled = False
        super().__init__()

    def register_effect(self, effect: Effect):
        if not self.is_scheduled:
            schedule_on_loop(self.flush)
            self.is_scheduled = True
        return super().register_effect(effect)

    def flush(self):
        super().flush()
        self.is_scheduled = False


class IgnoreBatch(Batch):
    """
    A batch that ignores effect registrations and does nothing when flushed.
    Used during State initialization to prevent effects from running during setup.
    """

    def register_effect(self, effect: Effect):
        # Silently ignore effect registrations during initialization
        pass

    def flush(self):
        # No-op: don't run any effects
        pass


class Epoch:
    def __init__(self, current: int = 0) -> None:
        self.current = current


# Used to track dependencies and effects created within a certain function or
# context.
class Scope:
    def __init__(self):
        # Dict preserves insertion order. Maps dependency -> last_change
        self.deps: dict[Signal | Computed, int] = {}
        self.effects: list[Effect] = []

    def register_effect(self, effect: "Effect"):
        if effect not in self.effects:
            self.effects.append(effect)

    def register_dep(self, value: "Signal | Computed"):
        self.deps[value] = value.last_change

    def __enter__(self):
        rc = REACTIVE_CONTEXT.get()
        # Create a new immutable reactive context with updated scope
        self._token = REACTIVE_CONTEXT.set(
            ReactiveContext(rc.epoch, rc.batch, self, rc.on_effect_error)
        )
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        # Restore previous reactive context
        REACTIVE_CONTEXT.reset(self._token)


class Untrack(Scope): ...


# --- Reactive Context (composite of epoch, batch, scope) ---
class ReactiveContext:
    def __init__(
        self,
        epoch: Optional[Epoch] = None,
        batch: Optional[Batch] = None,
        scope: Optional[Scope] = None,
        on_effect_error: Optional[Callable[[Effect, Exception], None]] = None,
    ) -> None:
        self.epoch = epoch or Epoch()
        self.batch = batch or GlobalBatch()
        self.scope = scope
        # Optional effect error handler set by integrators (e.g., session)
        self.on_effect_error = on_effect_error
        self._tokens = []

    def get_epoch(self) -> int:
        return self.epoch.current

    def increment_epoch(self) -> None:
        self.epoch.current += 1

    def __enter__(self):
        self._tokens.append(REACTIVE_CONTEXT.set(self))
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        REACTIVE_CONTEXT.reset(self._tokens.pop())


def epoch():
    return REACTIVE_CONTEXT.get().get_epoch()


def increment_epoch():
    return REACTIVE_CONTEXT.get().increment_epoch()


# Default global context (used in tests / outside app)
REACTIVE_CONTEXT: ContextVar[ReactiveContext] = ContextVar(
    "pulse_reactive_context", default=ReactiveContext(Epoch(), GlobalBatch())
)


def flush_effects():
    REACTIVE_CONTEXT.get().batch.flush()


class InvariantError(Exception): ...
