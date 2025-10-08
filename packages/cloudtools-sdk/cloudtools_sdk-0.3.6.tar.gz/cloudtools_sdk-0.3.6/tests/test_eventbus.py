"""Tests for the CloudTools EventBus integrations."""
from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace
from typing import Any, Dict

import pytest

from cloudtools import CloudService
from cloudtools.context import ServiceContext
from cloudtools.eventbus import ServiceEventBus


@pytest.mark.asyncio
async def test_subscribe_registration_and_lookup() -> None:
    service = CloudService("demo")

    @service.subscribe("demo.topic")
    async def _handler(payload: Dict[str, Any], ctx: ServiceContext) -> None:
        ctx.metadata["seen"] = payload["value"]

    subscribers = service.subscribers_for("demo.topic")
    assert len(subscribers) == 1
    assert subscribers[0].__name__ == "_handler"


@pytest.mark.asyncio
async def test_context_emit_passes_metadata_to_eventbus() -> None:
    service = CloudService("demo")
    published: list[tuple[str, Dict[str, Any], Dict[str, Any]]] = []

    class DummyBus:
        async def publish(
            self,
            topic: str,
            payload: Dict[str, Any],
            *,
            metadata: Dict[str, Any] | None = None,
        ) -> None:
            published.append((topic, payload, metadata or {}))

    service._event_bus = DummyBus()  # type: ignore[attr-defined]

    ctx = ServiceContext(service, metadata={"trace_id": "abc"})
    await ctx.emit("demo.topic", {"value": 42})

    assert published == [
        ("demo.topic", {"value": 42}, {"trace_id": "abc"}),
    ]


@pytest.mark.asyncio
async def test_eventbus_dispatches_payload_to_subscribers() -> None:
    service = CloudService("demo")
    received: list[tuple[Dict[str, Any], Dict[str, Any]]] = []

    @service.subscribe("demo.topic")
    async def on_event(payload: Dict[str, Any], ctx: ServiceContext) -> None:
        received.append((payload, dict(ctx.metadata)))

    bus = ServiceEventBus(service)
    service._event_bus = bus  # type: ignore[attr-defined]

    envelope = {
        "topic": "demo.topic",
        "payload": {"value": 1},
        "metadata": {"source": "test"},
    }
    message = SimpleNamespace(data=json.dumps(envelope).encode("utf-8"))

    await bus._handle_message("demo.topic", message)
    await asyncio.sleep(0)  # let subscriber task run

    assert received == [({"value": 1}, {"source": "test", "topic": "demo.topic"})]

    await bus.stop()


@pytest.mark.asyncio
async def test_eventbus_publish_wraps_envelope_with_metadata() -> None:
    service = CloudService("demo")
    bus = ServiceEventBus(service)
    service._event_bus = bus  # type: ignore[attr-defined]

    class StubNATS:
        def __init__(self) -> None:
            self.is_connected = True
            self.published: list[tuple[str, bytes]] = []
            self.flushed = False
            self.drained = False
            self.closed = False

        async def publish(self, topic: str, data: bytes) -> None:
            self.published.append((topic, data))

        async def flush(self, timeout: float | None = None) -> None:
            self.flushed = True

        async def drain(self) -> None:
            self.drained = True

        async def close(self) -> None:
            self.closed = True

    stub = StubNATS()
    bus._nats = stub  # type: ignore[attr-defined]
    bus._connected.set()

    await bus.publish("demo.topic", {"value": 7}, metadata={"extra": True})

    assert stub.flushed is True
    assert stub.published, "publish() should enqueue at least one message"

    topic, data = stub.published[0]
    payload = json.loads(data.decode("utf-8"))

    assert topic == "demo.topic"
    assert payload["topic"] == "demo.topic"
    assert payload["payload"] == {"value": 7}
    assert payload["metadata"]["service"] == "demo"
    assert payload["metadata"]["extra"] is True

    await bus.stop()
