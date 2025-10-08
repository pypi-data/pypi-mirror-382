"""Workflow-aware service context utilities."""
from __future__ import annotations

from datetime import timedelta
from typing import Any, Optional, TYPE_CHECKING
from uuid import uuid4

from temporalio import workflow
from temporalio.common import RetryPolicy

from ..constants import WORKFLOW_ID_PREFIX
from ..context import ServiceContext

if TYPE_CHECKING:  # pragma: no cover - for static analysis only
    from ..service import CloudService, UnknownTaskError
    from .queue import TaskQueueRuntime


class WorkflowServiceContext(ServiceContext):
    """Service context that proxies actions via workflow activities."""

    def __init__(
        self,
        service: "CloudService",
        runtime: "TaskQueueRuntime",
        *,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        self._runtime = runtime
        super().__init__(
            service,
            metadata=metadata,
            action_handler=self._execute_action,
            call_handler=self._call_service,
            emit_handler=self._emit_event,
        )

    async def _execute_action(self, name: str, *args: Any, **kwargs: Any) -> Any:
        activity_name = self._runtime.activity_name(self.service.name, name)
        payload = {
            "args": args,
            "kwargs": kwargs,
        }
        
        # Get timeout and attempts for this specific action
        action_func = self.service.actions.get(name)
        timeout = self._runtime.config.activity_timeout  # Default timeout
        attempts = None  # Default attempts (no retry)
        schedule_timeout = timeout
        has_total_timeout = False

        if action_func:
            if hasattr(action_func, "__cloudtools_action_timeout__"):
                timeout = getattr(action_func, "__cloudtools_action_timeout__")
                schedule_timeout = timeout
            if hasattr(action_func, "__cloudtools_action_attempts__"):
                attempts = getattr(action_func, "__cloudtools_action_attempts__")
            if hasattr(action_func, "__cloudtools_action_total_timeout__"):
                schedule_timeout = getattr(
                    action_func, "__cloudtools_action_total_timeout__"
                )
                has_total_timeout = True

        if schedule_timeout is None:
            schedule_timeout = timeout

        if (
            not has_total_timeout
            and schedule_timeout == timeout
            and attempts is not None
            and attempts > 1
            and timeout is not None
        ):
            schedule_timeout = timeout * attempts

        retry_options = self._retry_policy_from_attempts(attempts)

        result = await workflow.execute_activity(
            activity_name,
            payload,
            schedule_to_close_timeout=schedule_timeout,
            start_to_close_timeout=timeout,
            retry_policy=retry_options,
        )
        return result

    async def execute_child_task(self, name: str, payload: Any, **kwargs: Any) -> Any:
        """Start a child workflow for a task and wait for the result."""
        service_name, task_name, workflow_name = self._resolve_target(name)
        options = self._compose_child_options(service_name, task_name, kwargs)
        return await workflow.execute_child_workflow(
            workflow_name,
            payload,
            **options,
        )

    async def start_child_task(
        self,
        name: str,
        payload: Any,
        **kwargs: Any,
    ) -> workflow.ChildWorkflowHandle[Any, Any]:
        """Start a child workflow for a task and return its handle."""
        service_name, task_name, workflow_name = self._resolve_target(name)
        options = self._compose_child_options(service_name, task_name, kwargs)
        return await workflow.start_child_workflow(
            workflow_name,
            payload,
            **options,
        )

    async def _call_service(self, target: str, payload: Any) -> Any:
        return await self.execute_child_task(target, payload)

    async def _emit_event(self, topic: str, payload: Any) -> None:
        event_bus = self._runtime.event_bus
        if event_bus is None:
            raise NotImplementedError("EventBus is not configured for this runtime.")
        await event_bus.publish(topic, payload, metadata=dict(self.metadata))

    def _resolve_target(self, name: str) -> tuple[str, str, str]:
        service_name, task_name = self._parse_target(name)
        routed_service = self._map_service_name(service_name)
        if routed_service == self.service.name and task_name not in self.service.tasks:
            from ..service import UnknownTaskError

            raise UnknownTaskError(f"Task '{task_name}' is not registered.")
        workflow_name = self._runtime.workflow_name(routed_service, task_name)
        return routed_service, task_name, workflow_name

    def _parse_target(self, raw: str) -> tuple[str, str]:
        if "." in raw:
            service_name, task_name = raw.split(".", 1)
            return service_name, task_name
        return self.service.name, raw

    def _map_service_name(self, requested: str) -> str:
        from ..router import RouterStartupError, get_router_client

        try:
            router = get_router_client()
        except RouterStartupError as exc:  # pragma: no cover - should be ready
            raise RuntimeError(
                "Router client is not ready for workflow call resolution."
            ) from exc
        return router.resolve_service(requested)

    def _compose_child_options(
        self,
        service_name: str,
        task_name: str,
        options: dict[str, Any],
    ) -> dict[str, Any]:
        merged = dict(options)
        if "task_queue" not in merged and service_name != self.service.name:
            merged["task_queue"] = f"{service_name}-queue"
        runtime = self._runtime

        timeout = runtime.config.workflow_run_timeout
        attempts: Optional[int] = None

        if service_name == self.service.name:
            task_func = self.service.tasks.get(task_name)
            if task_func is not None:
                timeout = getattr(
                    task_func,
                    "__cloudtools_task_timeout__",
                    timeout,
                )
                attempts = getattr(
                    task_func,
                    "__cloudtools_task_attempts__",
                    None,
                )

        if "run_timeout" not in merged and timeout is not None:
            merged["run_timeout"] = timeout

        retry_policy = self._retry_policy_from_attempts(attempts)
        if "retry_policy" not in merged and retry_policy is not None:
            merged["retry_policy"] = retry_policy

        if "id" not in merged:
            merged["id"] = f"{WORKFLOW_ID_PREFIX}-{service_name}-{task_name}-{uuid4()}"
        return merged

    def _retry_policy_from_attempts(
        self, attempts: Optional[int]
    ) -> Optional[RetryPolicy]:
        if attempts is None or attempts <= 0:
            return None
        return RetryPolicy(
            maximum_attempts=attempts,
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=10),
            backoff_coefficient=2.0,
        )
