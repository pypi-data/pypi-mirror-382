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


def test_exposure_with_different_response_types() -> None:
    service = CloudService("web")

    @service.task("html_page")
    @service.expose(
        path="/page",
        method="GET",
        auth="none",
        mode="sync",
        response_type="html"
    )
    async def html_page(payload, ctx):  # pragma: no cover - invoked indirectly in tests
        return "<html><body>Hello World</body></html>"

    @service.task("text_response")
    @service.expose(
        path="/text",
        method="GET",
        auth="none",
        mode="sync",
        response_type="text"
    )
    async def text_response(payload, ctx):  # pragma: no cover - invoked indirectly in tests
        return "Plain text response"

    @service.task("raw_response")
    @service.expose(
        path="/raw",
        method="GET",
        auth="none",
        mode="sync",
        response_type="raw"
    )
    async def raw_response(payload, ctx):  # pragma: no cover - invoked indirectly in tests
        return "Raw response"

    # Test HTML response type
    html_exposure = service.get_exposure("html_page")
    assert html_exposure is not None
    assert html_exposure.response_type == "html"

    # Test text response type
    text_exposure = service.get_exposure("text_response")
    assert text_exposure is not None
    assert text_exposure.response_type == "text"

    # Test raw response type
    raw_exposure = service.get_exposure("raw_response")
    assert raw_exposure is not None
    assert raw_exposure.response_type == "raw"

    # Test default response type (should be json)
    @service.task("default_response")
    @service.expose(
        path="/default",
        method="GET",
        auth="none",
        mode="sync"
    )
    async def default_response(payload, ctx):  # pragma: no cover - invoked indirectly in tests
        return {"message": "default json"}

    default_exposure = service.get_exposure("default_response")
    assert default_exposure is not None
    assert default_exposure.response_type == "json"
