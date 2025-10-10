"""Event bus helpers for CloudTools services."""
from __future__ import annotations

import asyncio
import inspect
import json
import logging
import os
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, Optional, Set

try:  # pragma: no cover - optional dependency
    import nats
except ImportError:  # pragma: no cover - optional dependency
    nats = None  # type: ignore
    ConnectionClosedError = TimeoutError = NoServersError = None  # type: ignore
else:  # pragma: no cover - optional dependency
    try:
        from nats.errors import ConnectionClosedError, NoServersError, TimeoutError
    except (ImportError, AttributeError):  # pragma: no cover - optional dependency
        ConnectionClosedError = TimeoutError = NoServersError = None  # type: ignore

from .config import get_config_value
from .context import ServiceContext

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from .service import CloudService

LOGGER = logging.getLogger(__name__)

DEFAULT_CLIENT_NAME = "cloudtools-service"
DEFAULT_PUBLISH_TIMEOUT = 2.0

SubscriberCallable = Callable[[Any, "ServiceContext"], Awaitable[Any] | Any]


@dataclass
class EventBusSettings:
    """Runtime configuration for connecting to the EventBus."""

    nats_url: str = ""
    client_name: str = DEFAULT_CLIENT_NAME
    publish_timeout: float = DEFAULT_PUBLISH_TIMEOUT

    @classmethod
    def from_env(cls) -> "EventBusSettings":
        """Build settings from environment variables."""
        return cls(
            nats_url=get_config_value(
                "EVENTBUS_NATS_URL", "NATS_URL",
                default="nats://127.0.0.1:4222"
            ),
            client_name=os.getenv("EVENTBUS_CLIENT_NAME", DEFAULT_CLIENT_NAME),
            publish_timeout=float(
                os.getenv("EVENTBUS_PUBLISH_TIMEOUT", DEFAULT_PUBLISH_TIMEOUT)
            ),
        )


class ServiceEventBus:
    """Wrapper around NATS that wires subscriptions to CloudService callbacks."""

    def __init__(
        self,
        service: "CloudService",
        settings: Optional[EventBusSettings] = None,
    ) -> None:
        self._service = service
        self._settings = settings or EventBusSettings.from_env()
        self._nats: Any = None
        self._connected = asyncio.Event()
        self._subscription_ids: Dict[str, int] = {}
        self._pending_tasks: Set[asyncio.Task[Any]] = set()
        self._lock = asyncio.Lock()
        self._known_topics: Set[str] = set()

    @property
    def service(self) -> "CloudService":
        return self._service

    @property
    def settings(self) -> EventBusSettings:
        return self._settings

    @property
    def is_connected(self) -> bool:
        return self._connected.is_set()

    async def start(self) -> None:
        """Ensure there is an active NATS connection and registered subscriptions."""
        async with self._lock:
            if self._nats is not None and getattr(self._nats, "is_connected", False):
                self._connected.set()
                return

            if nats is None or not hasattr(nats, "connect"):
                raise RuntimeError(
                    "The 'nats-py' package (version 2.0 or later) is required to use the EventBus."
                )

            client_name = f"{self._settings.client_name}.{self._service.name}"
            LOGGER.info(
                "[eventbus] %s connecting to NATS %s",
                self._service.name,
                self._settings.nats_url,
            )
            
            # Retry connection with exponential backoff for remote servers
            last_error = None
            for attempt in range(1, 6):  # 5 attempts
                try:
                    self._nats = await nats.connect(
                        servers=[self._settings.nats_url],
                        name=client_name,
                        connect_timeout=10.0,  # 10 second timeout
                        reconnect_time_wait=2.0,  # 2 second wait between reconnects
                        max_reconnect_attempts=10,  # Allow up to 10 reconnects
                        ping_interval=20,  # Ping every 20 seconds
                        max_outstanding_pings=2,  # Max 2 outstanding pings
                    )
                    self._connected.set()
                    await self._ensure_all_subscriptions()
                    LOGGER.info(
                        "[eventbus] %s successfully connected to NATS on attempt %d",
                        self._service.name,
                        attempt,
                    )
                    return
                except Exception as exc:
                    last_error = exc
                    if attempt < 5:
                        wait_time = min(2 ** attempt, 30)  # Exponential backoff, max 30s
                        LOGGER.warning(
                            "[eventbus] %s NATS connection attempt %d failed: %s, retrying in %ds",
                            self._service.name,
                            attempt,
                            exc,
                            wait_time,
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        LOGGER.error(
                            "[eventbus] %s failed to connect to NATS after 5 attempts: %s",
                            self._service.name,
                            last_error,
                        )
                        raise RuntimeError(f"Unable to connect to NATS: {last_error}") from last_error

    async def stop(self) -> None:
        """Shutdown the NATS connection and wait for subscriber tasks."""
        self._connected.clear()

        # Cancel any subscriber tasks still running.
        if self._pending_tasks:
            for task in list(self._pending_tasks):
                task.cancel()
            await asyncio.gather(*self._pending_tasks, return_exceptions=True)
            self._pending_tasks.clear()

        if self._nats is None:
            return

        try:
            if getattr(self._nats, "is_connected", False):
                try:
                    await self._nats.drain()
                except Exception as exc:  # pragma: no cover - depends on runtime
                    # Handle common NATS connection errors gracefully
                    if (ConnectionClosedError is not None and isinstance(exc, ConnectionClosedError)) or \
                       (hasattr(exc, '__class__') and 'UnexpectedEOF' in str(exc)) or \
                       (hasattr(exc, '__class__') and 'ConnectionClosed' in str(exc)):
                        LOGGER.debug("[eventbus] %s NATS connection already closed: %s", self._service.name, exc)
                        pass
                    else:
                        LOGGER.warning("[eventbus] %s error during NATS drain: %s", self._service.name, exc)
                        raise
        finally:
            try:
                await self._nats.close()
            finally:
                self._nats = None
                self._subscription_ids.clear()

    async def publish(
        self,
        topic: str,
        payload: Any,
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Publish an event to the bus, ensuring the connection is ready."""
        self.register_topic(topic)
        if not self._connected.is_set():
            await self.start()
        await self._connected.wait()

        # Check connection health and reconnect if needed
        if self._nats is None or not getattr(self._nats, "is_connected", False):
            LOGGER.warning("[eventbus] %s NATS connection lost, attempting to reconnect", self._service.name)
            await self._restart()
            if self._nats is None or not getattr(self._nats, "is_connected", False):
                raise RuntimeError("EventBus client is not connected and reconnection failed.")

        envelope = {
            "topic": topic,
            "payload": payload,
            "metadata": self._build_metadata(metadata),
        }
        data = json.dumps(envelope).encode("utf-8")

        try:
            await self._nats.publish(topic, data)
            await self._nats.flush(timeout=self._settings.publish_timeout)
        except Exception as exc:  # pragma: no cover - depends on runtime
            if TimeoutError is None or isinstance(exc, TimeoutError):
                # Flush may time out if the server is slow; ignore to avoid blocking producers.
                LOGGER.debug("[eventbus] %s NATS flush timeout (non-critical)", self._service.name)
            elif (hasattr(exc, '__class__') and 'UnexpectedEOF' in str(exc)) or \
                 (hasattr(exc, '__class__') and 'ConnectionClosed' in str(exc)):
                LOGGER.warning("[eventbus] %s NATS connection lost during publish, will retry on next call", self._service.name)
                self._connected.clear()
                raise RuntimeError("EventBus connection lost during publish") from exc
            else:
                raise

    async def _ensure_all_subscriptions(self) -> None:
        """Subscribe to all topics registered on the service."""
        topics = set(self._service.subscription_topics)
        topics.update(self._known_topics)
        for topic in topics:
            await self._ensure_subscription(topic)
        if self._nats is not None:
            try:
                await self._nats.flush(timeout=self._settings.publish_timeout)
            except Exception as exc:  # pragma: no cover - depends on runtime
                if TimeoutError is None or isinstance(exc, TimeoutError):
                    pass
                else:
                    raise

    async def _ensure_subscription(self, topic: str) -> None:
        if topic in self._subscription_ids:
            return
        if self._nats is None:
            return

        async def handler(message):
            await self._handle_message(topic, message)

        sid = await self._nats.subscribe(topic, cb=handler)
        self._subscription_ids[topic] = sid
        self._known_topics.add(topic)
        LOGGER.info("[eventbus] %s subscribed to %s", self._service.name, topic)

    def register_topic(self, topic: str) -> None:
        """Record a topic so an active bus can attach a subscription."""
        if topic in self._known_topics:
            return
        self._known_topics.add(topic)
        if self._nats is not None and topic not in self._subscription_ids:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:  # pragma: no cover - no running loop
                return
            try:
                if loop.is_running():
                    loop.create_task(self._ensure_subscription(topic))
            except NotImplementedError:
                # Some Python versions don't support is_running()
                loop.create_task(self._ensure_subscription(topic))

    def update_settings(
        self,
        *,
        nats_url: Optional[str] = None,
        client_name: Optional[str] = None,
        publish_timeout: Optional[float] = None,
    ) -> None:
        """Override connection settings and reconnect if already running."""
        reconnect_required = False

        if nats_url and nats_url != self._settings.nats_url:
            LOGGER.info(
                "[eventbus] %s updating NATS URL %s -> %s",
                self._service.name,
                self._settings.nats_url,
                nats_url,
            )
            self._settings.nats_url = nats_url
            reconnect_required = True

        if client_name and client_name != self._settings.client_name:
            self._settings.client_name = client_name
            reconnect_required = True

        if (
            publish_timeout is not None
            and publish_timeout != self._settings.publish_timeout
        ):
            self._settings.publish_timeout = publish_timeout

        if reconnect_required and self._nats is not None:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:  # pragma: no cover - no running loop
                return
            loop.create_task(self._restart())

    async def _restart(self) -> None:
        LOGGER.info(
            "[eventbus] %s restart requested, stopping connection",
            self._service.name,
        )
        await self.stop()
        # Increased delay to allow NATS cleanup to complete
        await asyncio.sleep(0.5)
        LOGGER.info(
            "[eventbus] %s restarting connection to %s",
            self._service.name,
            self._settings.nats_url,
        )
        await self.start()
        LOGGER.info(
            "[eventbus] %s restart completed successfully",
            self._service.name,
        )

    async def _handle_message(self, topic: str, message: Any) -> None:
        try:
            envelope = json.loads(message.data.decode("utf-8"))
        except Exception:  # pragma: no cover - defensive parsing
            LOGGER.exception('Failed to decode message received on topic "%s"', topic)
            return

        payload = envelope.get("payload")
        metadata = envelope.get("metadata") or {}
        metadata.setdefault("topic", envelope.get("topic", topic))

        subscribers = list(self._service.subscribers_for(topic))
        if not subscribers:
            return

        for subscriber in subscribers:
            ctx = ServiceContext(self._service, metadata=dict(metadata))
            task = asyncio.create_task(
                self._invoke_subscriber(topic, subscriber, payload, ctx)
            )
            self._pending_tasks.add(task)
            task.add_done_callback(self._pending_tasks.discard)

    async def _invoke_subscriber(
        self,
        topic: str,
        subscriber: SubscriberCallable,
        payload: Any,
        ctx: "ServiceContext",
    ) -> None:
        try:
            result = subscriber(payload, ctx)
            if inspect.isawaitable(result):
                await result
        except asyncio.CancelledError:  # pragma: no cover - cancellation path
            raise
        except Exception:  # pragma: no cover - subscriber errors should not crash bus
            LOGGER.exception(
                'Subscriber %r raised while handling topic "%s"',
                subscriber,
                topic,
            )

    def _build_metadata(self, override: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        base = {"service": self._service.name, "ts": int(time.time())}
        if override:
            base.update(dict(override))
        return base


__all__ = [
    "EventBusSettings",
    "ServiceEventBus",
]
