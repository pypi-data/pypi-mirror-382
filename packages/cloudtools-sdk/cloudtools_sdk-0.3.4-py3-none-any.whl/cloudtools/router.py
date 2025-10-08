"""Router integration for CloudTools services."""
from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import weakref
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx

from .client import ServiceClient, ServiceClientConfig
from .config import get_config_value
from .eventbus import ServiceEventBus
from .service import CloudService

LOGGER = logging.getLogger(__name__)

_POLL_INTERVAL = float(os.getenv("ROUTER_POLL_INTERVAL_SEC", "5"))


@dataclass
class RouterConfig:
    kv_url: str
    temporal_address: str
    nats_url: str
    gateway_url: str
    router_url: str

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> "RouterConfig":
        return cls(
            kv_url=get_config_value(
                "KV_URL", "KV_SERVICE_ADDRESS",
                default=payload.get("kvUrl", "http://127.0.0.1:8000"),
                strip_slash=True
            ),
            temporal_address=get_config_value(
                "TEMPORAL_ADDRESS",
                default=payload.get("temporalAddress", "127.0.0.1:7233")
            ),
            nats_url=get_config_value(
                "NATS_URL",
                default=payload.get("natsUrl", "nats://127.0.0.1:4222")
            ),
            gateway_url=get_config_value(
                "GATEWAY_URL",
                default=payload.get("gatewayUrl", "http://127.0.0.1:9090"),
                strip_slash=True
            ),
            router_url=get_config_value(
                "ROUTER_URL",
                default=payload.get("routerUrl", "http://127.0.0.1:9000"),
                strip_slash=True
            ),
        )


class RouterStartupError(RuntimeError):
    """Raised when Router configuration cannot be loaded on startup."""


class ServiceRegistrationError(RuntimeError):
    """Base error for Router service registration failures."""


class DuplicateServiceRegistrationError(ServiceRegistrationError):
    """Raised when attempting to register a service name that is already active."""


class RouterClient:
    """Manages Router configuration, routes cache, and update propagation."""

    def __init__(
        self, router_url: str, *, poll_interval: float = _POLL_INTERVAL
    ) -> None:
        self._router_url = router_url.rstrip("/")
        self._poll_interval = max(1.0, poll_interval)
        self._http: Optional[httpx.AsyncClient] = None
        self._lock = asyncio.Lock()
        self._config: Optional[RouterConfig] = None
        self._routes: Dict[str, str] = {}
        self._ready = asyncio.Event()
        self._poll_task: Optional[asyncio.Task[None]] = None
        self._stopping = asyncio.Event()
        self._service_client = ServiceClient()
        self._event_buses: "weakref.WeakSet[ServiceEventBus]" = weakref.WeakSet()
        self._services_registered: set[str] = set()
        self._initializing: Optional[asyncio.Task[None]] = None

    @property
    def router_url(self) -> str:
        return self._router_url

    @property
    def config(self) -> RouterConfig:
        if self._config is None:
            raise RouterStartupError("Router configuration not loaded")
        return self._config

    def resolve_service(self, name: str) -> str:
        return self._routes.get(name, name)

    async def ensure_started(self) -> None:
        if self._ready.is_set():
            return
        async with self._lock:
            if self._ready.is_set():
                return
            if self._initializing is None:
                self._initializing = asyncio.create_task(self._initialize())
            task = self._initializing
        await task

    async def _initialize(self) -> None:
        try:
            await self._refresh_snapshot(initial=True)
        except Exception as exc:  # pragma: no cover - depends on router availability
            raise RouterStartupError(
                f"Unable to load router configuration from {self._router_url}: {exc}"
            ) from exc
        else:
            self._ready.set()
            self._stopping.clear()
            self._poll_task = asyncio.create_task(
                self._poll_loop(), name="router-poll-loop"
            )
        finally:
            async with self._lock:
                self._initializing = None

    async def stop(self) -> None:
        self._stopping.set()
        if self._poll_task is not None:
            poll_task = self._poll_task
            self._poll_task = None
            try:
                poll_task.cancel()
                # Give the task a moment to cancel gracefully
                with contextlib.suppress(asyncio.CancelledError, RuntimeError):
                    await asyncio.wait_for(poll_task, timeout=1.0)
            except (RuntimeError, asyncio.TimeoutError):
                # Task didn't cancel in time, that's okay
                pass
        if self._http is not None:
            await self._http.aclose()
            self._http = None
        await self._service_client.close()
        self._ready.clear()
        self._stopping = asyncio.Event()

    async def register_service(self, service: CloudService) -> None:
        await self.ensure_started()
        async with self._lock:
            if service.name in self._services_registered:
                raise DuplicateServiceRegistrationError(
                    f"Service '{service.name}' is already registered; stop it before starting again."
                )
            service.subscribe("router.updated")(self._on_router_event)
            self._services_registered.add(service.name)
        bus = service.ensure_event_bus()
        self._event_buses.add(bus)
        self._apply_config_to_bus(bus, self.config if self._config else None)
        bus.register_topic("router.updated")

    async def unregister_service(self, service: CloudService) -> None:
        async with self._lock:
            self._services_registered.discard(service.name)

    async def call_service(
        self,
        service_name: str,
        task_name: str,
        payload: Any,
        *,
        task_queue: Optional[str] = None,
        workflow_id: Optional[str] = None,
    ) -> Any:
        await self.ensure_started()
        routed_service = self.resolve_service(service_name)
        return await self._service_client.call(
            routed_service,
            task_name,
            payload,
            task_queue=task_queue,
            id=workflow_id,
        )

    async def refresh_now(self) -> None:
        LOGGER.debug("[router-client] refresh_now() called")
        try:
            await self._refresh_snapshot(initial=False)
            LOGGER.debug("[router-client] refresh_now() completed")
        except RuntimeError as exc:
            if "Event loop is closed" in str(exc):
                LOGGER.warning("[router-client] refresh_now() skipped: event loop is closed")
                return
            raise

    async def _get_http(self) -> httpx.AsyncClient:
        if self._http is None:
            # Suppress httpx INFO logs to avoid verbose HTTP request logging
            httpx_logger = logging.getLogger("httpx")
            httpx_logger.setLevel(logging.WARNING)
            
            timeout = httpx.Timeout(5.0, read=5.0, connect=5.0)
            self._http = httpx.AsyncClient(base_url=self._router_url, timeout=timeout)
        return self._http

    async def _poll_loop(self) -> None:
        while not self._stopping.is_set():
            await asyncio.sleep(self._poll_interval)
            try:
                await self._refresh_snapshot(initial=False)
            except Exception as exc:
                LOGGER.warning(
                    "Router poll failed: %s",
                    exc,
                    exc_info=LOGGER.isEnabledFor(logging.DEBUG),
                )

    async def _refresh_snapshot(self, *, initial: bool) -> None:
        LOGGER.debug("[router-client] _refresh_snapshot starting (initial=%s)", initial)
        http = await self._get_http()
        LOGGER.debug("[router-client] fetching config")
        config_data = await self._fetch_config(http)
        LOGGER.debug("[router-client] fetching routes")
        routes_data = await self._fetch_routes(http)
        LOGGER.debug("[router-client] applying snapshot")
        await self._apply_snapshot(config_data, routes_data, initial=initial)
        LOGGER.debug("[router-client] _refresh_snapshot completed")

    async def _fetch_config(self, http: httpx.AsyncClient) -> RouterConfig:
        try:
            # Check if event loop is still running
            loop = asyncio.get_running_loop()
            if loop.is_closed():
                raise RuntimeError("Event loop is closed")
        except RuntimeError:
            raise RuntimeError("Event loop is closed or not available")
            
        response = await http.get("/config")
        response.raise_for_status()
        payload = response.json()
        return (
            RouterConfig.from_payload(payload["config"])
            if "config" in payload
            else RouterConfig.from_payload(payload)
        )

    async def _fetch_routes(self, http: httpx.AsyncClient) -> Dict[str, str]:
        try:
            # Check if event loop is still running
            loop = asyncio.get_running_loop()
            if loop.is_closed():
                raise RuntimeError("Event loop is closed")
        except RuntimeError:
            raise RuntimeError("Event loop is closed or not available")
            
        response = await http.get("/routes")
        response.raise_for_status()
        payload = response.json()
        routes: Dict[str, str] = {}
        for entry in payload.get("routes", []):
            service = entry.get("service")
            target = entry.get("target")
            if service and target:
                routes[service] = target
        return routes

    async def _apply_snapshot(
        self,
        config: RouterConfig,
        routes: Dict[str, str],
        *,
        initial: bool,
    ) -> None:
        async with self._lock:
            self._config = config
            self._routes = dict(routes)
            await self._update_service_client(config)
            await self._update_kv_client(config)
            for bus in list(self._event_buses):
                self._apply_config_to_bus(bus, config)
            if initial:
                LOGGER.info("Router configuration loaded from %s", self._router_url)

    async def _update_service_client(self, config: RouterConfig) -> None:
        current = self._service_client.config
        new_config = ServiceClientConfig(
            address=config.temporal_address,
            namespace=current.namespace,
            workflow_run_timeout=current.workflow_run_timeout,
        )
        if current != new_config:
            await self._service_client.reconfigure(new_config)

    async def _update_kv_client(self, config: RouterConfig) -> None:
        try:
            from .kv import ensure_kv_client
            kv_client = await ensure_kv_client(config.kv_url)
            LOGGER.debug("[router-client] KV client updated to %s", config.kv_url)
        except Exception as e:
            LOGGER.warning("[router-client] Failed to update KV client: %s", e)

    def _apply_config_to_bus(
        self,
        bus: ServiceEventBus,
        config: Optional[RouterConfig] = None,
    ) -> None:
        try:
            cfg = config or self.config
            LOGGER.debug(
                "[router-client] applying NATS %s to bus %s",
                cfg.nats_url,
                bus.service.name,
            )
            bus.update_settings(nats_url=cfg.nats_url)
        except Exception as exc:
            LOGGER.warning("Failed to apply router config to event bus: %s", exc)

    async def _on_router_event(self, payload: Dict[str, Any], ctx: Any) -> None:
        if not payload:
            return
        kind = payload.get("kind")
        if kind not in {"route_set", "route_unset", "config_updated"}:
            return
        async with self._lock:
            if kind == "route_set":
                service = payload.get("service")
                target = payload.get("target")
                if service and target:
                    self._routes[service] = target
            elif kind == "route_unset":
                service = payload.get("service")
                if service:
                    self._routes.pop(service, None)
            elif kind == "config_updated":
                config_payload = payload.get("config")
                if isinstance(config_payload, dict):
                    config = RouterConfig.from_payload(config_payload)
                    self._config = config
                    await self._update_service_client(config)
                    for bus in list(self._event_buses):
                        self._apply_config_to_bus(bus, config)


_router_client: Optional[RouterClient] = None
_router_lock = asyncio.Lock()


async def ensure_router_client(router_url: Optional[str] = None) -> RouterClient:
    global _router_client
    resolved_url = get_config_value(
        "ROUTER_URL",
        default="http://127.0.0.1:9000",
        explicit=router_url,
        strip_slash=True
    )
    async with _router_lock:
        if _router_client is None:
            _router_client = RouterClient(resolved_url)
            await _router_client.ensure_started()
    return _router_client


def get_router_client() -> RouterClient:
    if _router_client is None or not _router_client._ready.is_set():
        raise RouterStartupError("Router client is not ready")
    return _router_client


async def stop_router_client() -> None:
    global _router_client
    if _router_client is not None:
        await _router_client.stop()
        _router_client = None
