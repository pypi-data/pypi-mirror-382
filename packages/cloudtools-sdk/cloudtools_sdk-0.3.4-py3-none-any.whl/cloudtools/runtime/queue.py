"""Queue-backed runtime built on top of a workflow engine."""
from __future__ import annotations

import asyncio
import contextlib
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Callable, Dict, List, Optional

from temporalio import activity, workflow
from temporalio.exceptions import ApplicationError
from temporalio.client import Client
from temporalio.worker import Worker

from .base import ServiceRuntime
from .workflow_context import WorkflowServiceContext
from ..eventbus import ServiceEventBus
from datetime import datetime, timezone
from typing import TYPE_CHECKING
if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..service import ExposureMetadata


def workflow_name(service_name: str, task_name: str) -> str:
    return f"{service_name}.{task_name}"


def activity_name(service_name: str, action_name: str) -> str:
    return f"{service_name}.actions.{action_name}"


DEFAULT_ACTIVITY_TIMEOUT = timedelta(seconds=30)
DEFAULT_WORKFLOW_TIMEOUT = timedelta(minutes=15)


async def _workflow_run(self, payload: Any) -> Any:
    runtime = type(self).runtime
    service = runtime.service
    ctx = WorkflowServiceContext(service, runtime)
    task_callable = service.tasks[type(self).task_name]

    task_name = type(self).task_name
    task_func = service.tasks.get(task_name)
    timeout = runtime.config.workflow_run_timeout

    if task_func and hasattr(task_func, "__cloudtools_task_timeout__"):
        timeout = getattr(task_func, "__cloudtools_task_timeout__")

    task_future = workflow.asyncio.create_task(
        service._invoke(task_callable, payload, ctx)
    )

    # When no timeout is configured we just await the task future directly.
    if timeout is None:
        return await task_future

    timeout_seconds = timeout.total_seconds() if isinstance(timeout, timedelta) else float(timeout)

    # Non-positive values mean the workflow should time out immediately.
    if timeout_seconds <= 0:
        task_future.cancel()
        with contextlib.suppress(workflow.asyncio.CancelledError):
            await task_future
        raise ApplicationError(
            f"Workflow task '{service.name}.{task_name}' exceeded its timeout",
            type="WorkflowTimeoutError",
        )

    timer_task = workflow.asyncio.create_task(workflow.sleep(timeout_seconds))
    done, pending = await workflow.wait(
        [task_future, timer_task],
        return_when=workflow.asyncio.FIRST_COMPLETED,
    )

    if task_future in done:
        timer_task.cancel()
        with contextlib.suppress(workflow.asyncio.CancelledError):
            await timer_task
        return await task_future

    # Timer fired first – cancel the task and raise an ApplicationError to fail deliberately.
    task_future.cancel()
    with contextlib.suppress(workflow.asyncio.CancelledError):
        await task_future
    raise ApplicationError(
        f"Workflow task '{service.name}.{task_name}' exceeded its timeout",
        type="WorkflowTimeoutError",
    )


@dataclass
class QueueRuntimeConfig:
    address: str = "127.0.0.1:7233"
    namespace: str = "default"
    task_queue: Optional[str] = None
    activity_timeout: timedelta = DEFAULT_ACTIVITY_TIMEOUT
    workflow_run_timeout: timedelta = DEFAULT_WORKFLOW_TIMEOUT


class TaskQueueRuntime(ServiceRuntime):
    """Runtime that dispatches tasks onto a shared workflow/queue backend."""

    def __init__(self, config: Optional[QueueRuntimeConfig] = None) -> None:
        super().__init__()
        self._config = config or QueueRuntimeConfig()
        self._client: Optional[Client] = None
        self._worker: Optional[Worker] = None
        self._ready = asyncio.Event()
        self._event_bus: Optional[ServiceEventBus] = None
        self._heartbeat_task: Optional[asyncio.Task[None]] = None
        self._stop_event = asyncio.Event()
        self._bound_tasks: set[str] = set()

    @property
    def config(self) -> QueueRuntimeConfig:
        return self._config

    @property
    def task_queue(self) -> str:
        if self._config.task_queue is None:
            raise RuntimeError("Runtime not yet attached to a service.")
        return self._config.task_queue

    async def serve(self) -> None:
        """Run the worker until shutdown is requested."""
        if self._config.task_queue is None:
            self._config.task_queue = f"{self.service.name}-queue"

        router_client = None
        from ..router import ensure_router_client  # Lazy import to avoid circular
        from ..kv import ensure_kv_client  # Lazy import to avoid circular

        router_client = await ensure_router_client()
        await router_client.register_service(self.service)
        router_config = router_client.config
        if router_config.temporal_address:
            self._config.address = router_config.temporal_address

        if router_config.kv_url:
            kv_client = await ensure_kv_client(router_config.kv_url)
        else:
            kv_client = await ensure_kv_client()

        bus = self._event_bus
        if bus is not None:
            # Start the event bus and announce exposures BEFORE connecting to Temporal,
            # so that Gateway routes become available even if Temporal is unavailable.
            await bus.start()
            try:
                await self._announce_exposures()
            except Exception:
                pass

            # Subscribe to bound events to adjust heartbeat behavior.
            try:
                service = self.service

                async def _on_bound(payload, ctx):
                    if not isinstance(payload, dict):
                        return
                    if payload.get("service") != service.name:
                        return
                    task_name = payload.get("task")
                    if isinstance(task_name, str):
                        self._bound_tasks.add(task_name)

                # Register subscriber dynamically
                service.subscribe("gateway.expose.bound")(_on_bound)
            except Exception:
                pass

            # Start heartbeat loop
            self._stop_event.clear()
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop(), name="expose-heartbeat")

        self._client = await Client.connect(
            self._config.address,
            namespace=self._config.namespace,
        )

        workflows = [self._build_workflow(name) for name in self.service.tasks]
        activities = [self._build_activity(name) for name in self.service.actions]

        self._worker = Worker(
            self._client,
            task_queue=self._config.task_queue,
            workflows=workflows,
            activities=activities,
        )

        self._ready.set()

        try:
            await self._worker.run()
        finally:
            self._ready.clear()
            self._worker = None
            # Stop heartbeat
            self._stop_event.set()
            if self._heartbeat_task is not None:
                with contextlib.suppress(Exception):
                    await asyncio.wait_for(self._heartbeat_task, timeout=2.0)
                self._heartbeat_task = None
            if self._client is not None:
                close = getattr(self._client, "close", None)
                if callable(close):
                    maybe_awaitable = close()
                    if hasattr(maybe_awaitable, "__await__"):
                        await maybe_awaitable
                self._client = None
            if bus is not None:
                await bus.stop()
            if router_client is not None:
                await router_client.unregister_service(self.service)

    async def _announce_exposures(self) -> None:
        """Publish exposure announcements for all tasks marked with @service.expose.

        The Gateway listens to the 'gateway.expose.announce' subject and will
        dynamically register HTTP routes when it receives these announcements.
        """
        bus = self._event_bus
        if bus is None:
            return
        exposures = list(self.service.exposures.values())
        if not exposures:
            return
        now_iso = datetime.now(timezone.utc).isoformat()
        for meta in exposures:
            payload: Dict[str, Any] = {
                "service": meta.service,
                "task": meta.task,
                "path": meta.path,
                "method": meta.method,
                "auth": meta.auth,
                "mode": meta.mode,
                "domain": meta.domain,
                "revision": meta.revision or 1,
                "ts": now_iso,
            }
            await bus.publish("gateway.expose.announce", payload, metadata={"service": self.service.name})

    async def _heartbeat_loop(self) -> None:
        bus = self._event_bus
        if bus is None:
            return
        while not self._stop_event.is_set():
            try:
                exposures = list(self.service.exposures.values())
                now_iso = datetime.now(timezone.utc).isoformat()
                for meta in exposures:
                    payload: Dict[str, Any] = {
                        "service": meta.service,
                        "task": meta.task,
                        "path": meta.path,
                        "method": meta.method,
                        "auth": meta.auth,
                        "mode": meta.mode,
                        "domain": meta.domain,
                        "revision": meta.revision or 1,
                        "heartbeat": True,
                        "ts": now_iso,
                    }
                    await bus.publish("gateway.expose.announce", payload, metadata={"service": self.service.name})
            except asyncio.CancelledError:
                break
            except Exception:
                # Best effort heartbeat; keep looping
                pass
            # Faster cadence until any task is bound, then slower
            interval = 3.0 if not self._bound_tasks else 10.0
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=interval)
            except asyncio.TimeoutError:
                continue

    def run(self, *args: Any, **kwargs: Any) -> None:
        """Synchronously serve the worker."""
        asyncio.run(self.serve())

    async def shutdown(self) -> None:
        if self._worker is not None:
            await self._worker.shutdown()

    async def wait_until_ready(self, timeout: Optional[float] = None) -> None:
        await asyncio.wait_for(self._ready.wait(), timeout=timeout)

    def activity_name(self, service_name: str, action_name: str) -> str:
        return activity_name(service_name, action_name)

    def workflow_name(self, service_name: str, task_name: str) -> str:
        return workflow_name(service_name, task_name)

    def set_event_bus(self, bus: ServiceEventBus) -> None:
        """Attach an event bus that should be managed alongside the worker."""
        self._event_bus = bus

    @property
    def event_bus(self) -> Optional[ServiceEventBus]:
        return self._event_bus

    def _build_activity(self, action_name: str) -> Callable[[Dict[str, Any]], Any]:
        service = self.service
        action_callable = service.actions[action_name]
        activity_id = self.activity_name(service.name, action_name)

        @activity.defn(name=activity_id)
        async def _activity(payload: Dict[str, Any]) -> Any:
            args = payload.get("args", ())
            kwargs = payload.get("kwargs", {})
            return await service._invoke(action_callable, *args, **kwargs)

        return _activity

    def _build_workflow(self, task_name: str) -> type:
        runtime = self
        service = self.service
        workflow_id = self.workflow_name(service.name, task_name)

        class_name = f"{service.name}_{task_name}_Workflow".replace(".", "_").replace(
            "-", "_"
        )

        async def run(self, payload: Any) -> Any:
            return await _workflow_run(self, payload)

        run.__name__ = "run"
        run.__qualname__ = f"{class_name}.run"
        run.__module__ = __name__

        # Get timeout and attempts for this specific task
        task_func = service.tasks.get(task_name)
        workflow_timeout = runtime.config.workflow_run_timeout  # Default timeout
        workflow_attempts = None  # Default attempts (no retry)
        
        if task_func:
            if hasattr(task_func, "__cloudtools_task_timeout__"):
                workflow_timeout = getattr(task_func, "__cloudtools_task_timeout__")
            if hasattr(task_func, "__cloudtools_task_attempts__"):
                workflow_attempts = getattr(task_func, "__cloudtools_task_attempts__")

        attrs = {
            "runtime": runtime,
            "task_name": task_name,
            "run": workflow.run(run),
            "workflow_timeout": workflow_timeout,
            "workflow_attempts": workflow_attempts,
        }
        workflow_class = type(class_name, (), attrs)
        workflow_class.__module__ = __name__

        # Generated classes rely on runtime state attached pre-execution, so we
        # disable the Temporal sandbox to keep imports from reloading.
        decorated = workflow.defn(name=workflow_id, sandboxed=False)(workflow_class)
        globals()[class_name] = decorated
        return decorated
