"""Core primitives for defining CloudTools services."""
from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any, Callable, Dict, List, Optional, Union

from .context import ServiceContext
from .eventbus import ServiceEventBus
from .runtime import ServiceRuntime
from .runtime.defaults import default_runtime_factory

ActionCallable = Callable[..., Any]
TaskCallable = Callable[..., Any]
SubscriberCallable = Callable[[Any, ServiceContext], Any]
RuntimeFactory = Callable[["CloudService"], ServiceRuntime]


@dataclass(frozen=True)
class ExposureSpec:
    """Specification provided via @service.expose."""

    path: str
    method: str
    auth: str
    mode: str
    domain: Optional[str] = None
    revision: Optional[str | int] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_metadata(self, service: str, task: str) -> "ExposureMetadata":
        return ExposureMetadata(
            service=service,
            task=task,
            path=self.path,
            method=self.method,
            auth=self.auth,
            mode=self.mode,
            domain=self.domain,
            revision=self.revision,
            extra=dict(self.extra),
        )


@dataclass(frozen=True)
class ExposureMetadata:
    """Resolved exposure metadata bound to a specific task."""

    service: str
    task: str
    path: str
    method: str
    auth: str
    mode: str
    domain: Optional[str] = None
    revision: Optional[str | int] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        """Return a serialisable view for persistence or APIs."""
        return {
            "service": self.service,
            "task": self.task,
            "path": self.path,
            "method": self.method,
            "auth": self.auth,
            "mode": self.mode,
            "domain": self.domain,
            "revision": self.revision,
            "extra": dict(self.extra),
        }


class CloudServiceError(Exception):
    """Base class for CloudService-related errors."""


class DuplicateRegistrationError(CloudServiceError):
    """Raised when trying to register an action or task with an existing name."""


class UnknownActionError(CloudServiceError):
    """Raised when attempting to invoke an unknown action."""


class UnknownTaskError(CloudServiceError):
    """Raised when attempting to invoke an unknown task."""


class RuntimeNotConfiguredError(CloudServiceError):
    """Raised when run() is called without an attached runtime backend."""


class CloudService:
    """Container for actions, tasks, and runtime orchestration."""

    def __init__(
        self,
        name: str,
        *,
        activity_timeout: Optional[Union[int, timedelta]] = None,
        workflow_run_timeout: Optional[Union[int, timedelta]] = None,
    ) -> None:
        self.name = name
        self._actions: Dict[str, ActionCallable] = {}
        self._tasks: Dict[str, TaskCallable] = {}
        self._subscriptions: Dict[str, List[SubscriberCallable]] = {}
        self._runtime: Optional[ServiceRuntime] = None
        self._runtime_factory: RuntimeFactory = default_runtime_factory
        self._event_bus: Optional[ServiceEventBus] = None
        self._exposures: Dict[str, ExposureMetadata] = {}
        self._default_activity_timeout = self._normalise_timeout(activity_timeout)
        self._default_workflow_run_timeout = self._normalise_timeout(
            workflow_run_timeout
        )

    @property
    def actions(self) -> Dict[str, ActionCallable]:
        """Return the registered actions."""
        return dict(self._actions)

    @property
    def tasks(self) -> Dict[str, TaskCallable]:
        """Return the registered tasks."""
        return dict(self._tasks)

    @property
    def subscriptions(self) -> Dict[str, List[SubscriberCallable]]:
        """Return the registered event subscriptions."""
        return {topic: list(callbacks) for topic, callbacks in self._subscriptions.items()}

    @property
    def subscription_topics(self) -> List[str]:
        """Return the list of topics that have registered subscribers."""
        return list(self._subscriptions.keys())

    @property
    def exposures(self) -> Dict[str, ExposureMetadata]:
        """Return the registered task exposures."""
        return dict(self._exposures)

    def get_exposure(self, task_name: str) -> Optional[ExposureMetadata]:
        """Return exposure metadata for a task if available."""
        return self._exposures.get(task_name)

    @property
    def ctx(self) -> ServiceContext:
        """Create a fresh execution context."""
        self.ensure_event_bus()
        return ServiceContext(self)

    @property
    def default_activity_timeout(self) -> Optional[timedelta]:
        """Default activity timeout applied when creating runtimes."""
        return self._default_activity_timeout

    @property
    def default_workflow_run_timeout(self) -> Optional[timedelta]:
        """Default workflow run timeout applied when creating runtimes."""
        return self._default_workflow_run_timeout

    @property
    def runtime(self) -> Optional[ServiceRuntime]:
        """Return the currently attached runtime backend, if any."""
        return self._runtime

    @property
    def event_bus(self) -> Optional[ServiceEventBus]:
        """Return the event bus associated with the service, if configured."""
        return self._event_bus

    def set_runtime_factory(self, factory: RuntimeFactory) -> None:
        """Override the factory used when auto-attaching a runtime."""
        self._runtime_factory = factory

    def attach_runtime(self, runtime: ServiceRuntime) -> None:
        """Attach a runtime backend that will manage service execution."""
        runtime.attach(self)
        bus = self.ensure_event_bus()
        if hasattr(runtime, "set_event_bus"):
            runtime.set_event_bus(bus)
        self._runtime = runtime

    def action(
        self,
        func: Optional[ActionCallable] = None,
        *,
        name: Optional[str] = None,
        timeout: Optional[Union[int, timedelta]] = None,
        total_timeout: Optional[Union[int, timedelta]] = None,
        attempts: Optional[int] = 1,
    ) -> Callable[[ActionCallable], ActionCallable]:
        """Decorator for registering a local action.
        
        Args:
            func: The action function to register
            name: Optional name for the action (defaults to function name)
            timeout: Optional timeout in seconds (int) or timedelta for this specific action
            total_timeout: Optional total timeout across retries in seconds or timedelta
            attempts: Optional number of retry attempts for this specific action
        """

        def decorator(target: ActionCallable) -> ActionCallable:
            action_name = name or target.__name__
            if action_name in self._actions:
                raise DuplicateRegistrationError(f"Action '{action_name}' is already registered.")
            
            # Store timeout metadata on the function
            if timeout is not None:
                timeout_val = timeout
                if isinstance(timeout_val, int):
                    timeout_val = timedelta(seconds=timeout_val)
                setattr(target, "__cloudtools_action_timeout__", timeout_val)

            if total_timeout is not None:
                total_timeout_val = total_timeout
                if isinstance(total_timeout_val, int):
                    total_timeout_val = timedelta(seconds=total_timeout_val)
                setattr(target, "__cloudtools_action_total_timeout__", total_timeout_val)
            
            # Store attempts metadata on the function
            if attempts is not None:
                setattr(target, "__cloudtools_action_attempts__", attempts)
            
            self._actions[action_name] = target
            return target

        if func is not None:
            return decorator(func)
        return decorator

    def task(self, name: Optional[str] = None, timeout: Optional[Union[int, timedelta]] = None, attempts: Optional[int] = None) -> Callable[[TaskCallable], TaskCallable]:
        """Decorator for registering a task.
        
        Args:
            name: Optional name for the task (defaults to function name)
            timeout: Optional timeout in seconds (int) or timedelta for this specific task
            attempts: Optional number of retry attempts for this specific task
        """

        def decorator(target: TaskCallable) -> TaskCallable:
            task_name = name or target.__name__
            if task_name in self._tasks:
                raise DuplicateRegistrationError(f"Task '{task_name}' is already registered.")
            
            # Store timeout metadata on the function
            if timeout is not None:
                timeout_val = timeout
                if isinstance(timeout_val, int):
                    timeout_val = timedelta(seconds=timeout_val)
                setattr(target, "__cloudtools_task_timeout__", timeout_val)
            
            # Store attempts metadata on the function
            if attempts is not None:
                setattr(target, "__cloudtools_task_attempts__", attempts)
            
            self._tasks[task_name] = target
            setattr(target, "__cloudtools_task_name__", task_name)
            self._bind_exposure(target, task_name)
            return target

        return decorator

    def subscribe(self, topic: str) -> Callable[[SubscriberCallable], SubscriberCallable]:
        """Decorator for registering an event subscriber."""

        def decorator(target: SubscriberCallable) -> SubscriberCallable:
            callbacks = self._subscriptions.setdefault(topic, [])
            callbacks.append(target)
            if self._event_bus is not None:
                self._event_bus.register_topic(topic)
            return target

        return decorator

    def expose(
        self,
        *,
        path: str,
        method: str,
        auth: str,
        mode: str,
        domain: Optional[str] = None,
        revision: Optional[str | int] = None,
        **extra: Any,
    ) -> Callable[[TaskCallable], TaskCallable]:
        """Decorator for declaring that a task should be exposed via the Gateway."""

        method_normalised = method.upper()
        spec = ExposureSpec(
            path=path,
            method=method_normalised,
            auth=auth,
            mode=mode,
            domain=domain,
            revision=revision,
            extra=dict(extra),
        )

        def decorator(target: TaskCallable) -> TaskCallable:
            setattr(target, "__cloudtools_exposure_spec__", spec)
            task_name = getattr(target, "__cloudtools_task_name__", None)
            if task_name is not None:
                self._register_exposure(task_name, spec)
            return target

        return decorator

    async def execute_action(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Invoke a registered action by name."""
        try:
            action = self._actions[name]
        except KeyError as exc:
            raise UnknownActionError(f"Action '{name}' is not registered.") from exc
        return await self._invoke(action, *args, **kwargs)

    async def execute_task(
        self,
        name: str,
        payload: Any,
        ctx: Optional[ServiceContext] = None,
    ) -> Any:
        """Invoke a registered task by name, creating a context if needed."""
        try:
            task = self._tasks[name]
        except KeyError as exc:
            raise UnknownTaskError(f"Task '{name}' is not registered.") from exc

        execution_ctx = ctx or ServiceContext(self)
        return await self._invoke(task, payload, execution_ctx)

    def subscribers_for(self, topic: str) -> List[SubscriberCallable]:
        """Return the subscribers registered for a topic."""
        return list(self._subscriptions.get(topic, ()))

    def _bind_exposure(self, target: TaskCallable, task_name: str) -> None:
        spec: Optional[ExposureSpec] = getattr(
            target, "__cloudtools_exposure_spec__", None
        )
        if spec is None:
            return
        self._register_exposure(task_name, spec)

    def _register_exposure(self, task_name: str, spec: ExposureSpec) -> None:
        metadata = spec.to_metadata(self.name, task_name)
        self._exposures[task_name] = metadata

    async def _invoke(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Invoke a callable and await the result if needed."""
        result = func(*args, **kwargs)
        if inspect.isawaitable(result):
            return await result
        return result

    def run(self, *args: Any, **kwargs: Any) -> None:
        """Delegate service execution to the attached runtime backend."""
        if self._runtime is None:
            runtime = self._runtime_factory(self)
            self.attach_runtime(runtime)
        if self._runtime is None:
            raise RuntimeNotConfiguredError("Runtime attachment failed.")
        self.ensure_event_bus()
        self._runtime.run(*args, **kwargs)

    async def shutdown(self) -> None:
        """Shutdown the attached runtime backend if it exposes a hook."""
        if self._runtime is not None:
            await self._runtime.shutdown()
        if self._event_bus is not None:
            await self._event_bus.stop()

    def ensure_event_bus(self) -> ServiceEventBus:
        """Ensure an event bus instance is available for the service."""
        if self._event_bus is None:
            self._event_bus = ServiceEventBus(self)
            if self._runtime is not None and hasattr(self._runtime, "set_event_bus"):
                self._runtime.set_event_bus(self._event_bus)
        return self._event_bus

    @staticmethod
    def _normalise_timeout(value: Optional[Union[int, timedelta]]) -> Optional[timedelta]:
        if value is None:
            return None
        if isinstance(value, timedelta):
            return value
        return timedelta(seconds=int(value))
