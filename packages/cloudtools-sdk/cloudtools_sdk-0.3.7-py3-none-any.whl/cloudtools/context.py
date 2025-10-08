"""Runtime context passed into CloudTools service callables."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, Optional

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from .service import CloudService

ActionHandler = Callable[..., Awaitable[Any]]
CallHandler = Callable[..., Awaitable[Any]]
EmitHandler = Callable[..., Awaitable[None]]


class ServiceContext:
    """Provides helpers for interacting with the owning service."""

    def __init__(
        self,
        service: "CloudService",
        *,
        metadata: Optional[Dict[str, Any]] = None,
        action_handler: Optional[ActionHandler] = None,
        call_handler: Optional[CallHandler] = None,
        emit_handler: Optional[EmitHandler] = None,
    ) -> None:
        self._service = service
        self._metadata = metadata or {}
        self._action_handler = action_handler or self._default_action_handler
        self._call_handler = call_handler or self._default_call_handler
        self._emit_handler = emit_handler or self._default_emit_handler

    @property
    def service(self) -> "CloudService":
        """Return the owning service instance."""
        return self._service

    @property
    def metadata(self) -> Dict[str, Any]:
        """Arbitrary metadata associated with the current execution."""
        return self._metadata

    async def action(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Invoke a registered local action by name."""
        return await self._action_handler(name, *args, **kwargs)

    async def call(self, target: str, payload: Any) -> Any:
        """Delegate to the configured cross-service call handler."""
        return await self._call_handler(target, payload)

    async def emit(self, topic: str, payload: Any) -> None:
        """Delegate to the configured event publication handler."""
        await self._emit_handler(topic, payload)

    async def _default_action_handler(
        self, name: str, *args: Any, **kwargs: Any
    ) -> Any:
        return await self._service.execute_action(name, *args, **kwargs)

    async def _default_call_handler(self, target: str, payload: Any) -> Any:
        requested_service, task_name = self._split_target(target)
        from .router import RouterStartupError, get_router_client

        try:
            router = get_router_client()
        except RouterStartupError as exc:  # pragma: no cover - should be initialised
            raise RuntimeError(
                "Router client is not ready for cross-service calls."
            ) from exc

        routed_service = router.resolve_service(requested_service)
        if routed_service == self._service.name:
            return await self._service.execute_task(task_name, payload, ctx=self)
        return await router.call_service(requested_service, task_name, payload)

    async def _default_emit_handler(self, topic: str, payload: Any) -> None:
        event_bus = getattr(self._service, "event_bus", None)
        if event_bus is None:
            raise NotImplementedError("Event publishing requires an EventBus instance.")
        await event_bus.publish(topic, payload, metadata=dict(self._metadata))

    def _split_target(self, raw: str) -> tuple[str, str]:
        if "." in raw:
            service_name, task_name = raw.split(".", 1)
            return service_name, task_name
        return self._service.name, raw
