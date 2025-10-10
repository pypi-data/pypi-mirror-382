from __future__ import annotations

import httpx
import pytest

from cloudtools import CloudService
from cloudtools.router import DuplicateServiceRegistrationError, RouterClient


@pytest.mark.asyncio
async def test_router_client_initial_snapshot_and_events() -> None:
    config_payload = {
        "kvUrl": "http://kv",
        "temporalAddress": "127.0.0.1:7233",
        "natsUrl": "nats://127.0.0.1:4222",
        "gatewayUrl": "http://gateway",
        "routerUrl": "http://router",
    }
    routes_payload = {
        "routes": [
            {
                "service": "alpha",
                "target": "alpha-v2",
                "updatedAt": "2023-01-01T00:00:00Z",
            },
        ]
    }

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/config":
            return httpx.Response(200, json={"config": config_payload})
        if request.url.path == "/routes":
            return httpx.Response(200, json=routes_payload)
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    client = RouterClient("http://router")
    client._http = httpx.AsyncClient(transport=transport, base_url="http://router")  # type: ignore[attr-defined]

    await client.ensure_started()
    assert client.resolve_service("alpha") == "alpha-v2"

    await client._on_router_event({"kind": "route_unset", "service": "alpha"}, None)
    assert client.resolve_service("alpha") == "alpha"

    await client._on_router_event(
        {"kind": "route_set", "service": "beta", "target": "beta-v2"}, None
    )
    assert client.resolve_service("beta") == "beta-v2"

    await client.stop()


@pytest.mark.asyncio
async def test_router_client_prevents_duplicate_service_registration() -> None:
    config_payload = {
        "kvUrl": "http://kv",
        "temporalAddress": "127.0.0.1:7233",
        "natsUrl": "nats://127.0.0.1:4222",
        "gatewayUrl": "http://gateway",
        "routerUrl": "http://router",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/config":
            return httpx.Response(200, json={"config": config_payload})
        if request.url.path == "/routes":
            return httpx.Response(200, json={"routes": []})
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    client = RouterClient("http://router")
    client._http = httpx.AsyncClient(transport=transport, base_url="http://router")  # type: ignore[attr-defined]

    service_primary = CloudService("duplicate")
    service_duplicate = CloudService("duplicate")

    try:
        await client.register_service(service_primary)
        with pytest.raises(DuplicateServiceRegistrationError):
            await client.register_service(service_duplicate)
        await client.unregister_service(service_primary)
    finally:
        await client.stop()
