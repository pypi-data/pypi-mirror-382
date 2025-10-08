from __future__ import annotations

from cloudtools import CloudService


def test_exposure_registers_with_task_decorator_order() -> None:
    service = CloudService("hello")

    @service.task("say_hello")
    @service.expose(
        path="/api/hello",
        method="post",
        auth="none",
        mode="sync",
        domain="hello.example.com",
        tags=["beta"],
    )
    async def say_hello(payload, ctx):  # pragma: no cover - invoked indirectly in tests
        return {"ok": True}

    exposure = service.get_exposure("say_hello")
    assert exposure is not None
    assert exposure.service == "hello"
    assert exposure.task == "say_hello"
    assert exposure.path == "/api/hello"
    assert exposure.method == "POST"
    assert exposure.auth == "none"
    assert exposure.mode == "sync"
    assert exposure.domain == "hello.example.com"
    assert exposure.extra == {"tags": ["beta"]}

    exposures = service.exposures
    assert set(exposures.keys()) == {"say_hello"}


def test_exposure_registers_when_expose_applied_last() -> None:
    service = CloudService("metrics")

    @service.expose(path="/metrics", method="GET", auth="none", mode="sync")
    @service.task("fetch")
    async def fetch_metrics(payload, ctx):  # pragma: no cover - invoked indirectly in tests
        return {"metrics": []}

    exposure = service.get_exposure("fetch")
    assert exposure is not None
    assert exposure.method == "GET"
    assert exposure.extra == {}
