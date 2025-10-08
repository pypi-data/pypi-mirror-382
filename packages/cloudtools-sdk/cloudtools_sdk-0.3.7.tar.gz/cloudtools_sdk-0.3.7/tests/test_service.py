"""Tests for the core CloudService primitives."""
from __future__ import annotations

from typing import Optional

import pytest

from cloudtools import (
    CloudService,
    DuplicateRegistrationError,
    ServiceContext,
    UnknownActionError,
    UnknownTaskError,
)
from cloudtools.runtime import ServiceRuntime


@pytest.mark.asyncio
async def test_action_registration_and_invocation() -> None:
    service = CloudService("demo")

    @service.action
    async def greet(name: str) -> str:
        return f"Hello, {name}!"

    result = await service.ctx.action("greet", "Alice")
    assert result == "Hello, Alice!"


@pytest.mark.asyncio
async def test_actions_must_be_unique() -> None:
    service = CloudService("demo")

    @service.action(name="greet")
    async def _greet(name: str) -> str:
        return f"Hello, {name}!"

    with pytest.raises(DuplicateRegistrationError):
        @service.action(name="greet")
        async def _dup(name: str) -> str:  # pragma: no cover - never executed
            return f"Hi, {name}"


@pytest.mark.asyncio
async def test_task_invocation_provides_context() -> None:
    service = CloudService("demo")
    seen_ctx: Optional[ServiceContext] = None

    @service.task("ping")
    async def ping(payload: dict, ctx: ServiceContext) -> dict:
        nonlocal seen_ctx
        seen_ctx = ctx
        return {"echo": payload["message"]}

    result = await service.execute_task("ping", {"message": "pong"})

    assert isinstance(seen_ctx, ServiceContext)
    assert result == {"echo": "pong"}


@pytest.mark.asyncio
async def test_unknown_action_raises() -> None:
    service = CloudService("demo")
    with pytest.raises(UnknownActionError):
        await service.execute_action("missing")


@pytest.mark.asyncio
async def test_unknown_task_raises() -> None:
    service = CloudService("demo")
    with pytest.raises(UnknownTaskError):
        await service.execute_task("missing", {})


class DummyRuntime(ServiceRuntime):
    def __init__(self) -> None:
        super().__init__()
        self.ran = False
        self.args = None
        self.kwargs = None

    def run(self, *args: object, **kwargs: object) -> None:
        # Ensure the runtime was bound to the service before execution.
        assert self.service.name == "demo"
        self.ran = True
        self.args = args
        self.kwargs = kwargs


def test_runtime_attachment_and_run_delegation() -> None:
    service = CloudService("demo")
    runtime = DummyRuntime()

    service.attach_runtime(runtime)
    service.run(1, hello="world")

    assert runtime.ran is True
    assert runtime.args == (1,)
    assert runtime.kwargs == {"hello": "world"}


class FactoryRuntime(ServiceRuntime):
    def __init__(self) -> None:
        super().__init__()
        self.ran = False

    def run(self, *args: object, **kwargs: object) -> None:
        self.ran = True


def test_run_uses_runtime_factory_when_not_attached() -> None:
    service = CloudService("demo")
    runtime = FactoryRuntime()

    def factory(_service: CloudService) -> ServiceRuntime:
        return runtime

    service.set_runtime_factory(factory)
    service.run()

    assert runtime.ran is True


class CountingFactoryRuntime(ServiceRuntime):
    def __init__(self) -> None:
        super().__init__()
        self.ran = False

    def run(self, *args: object, **kwargs: object) -> None:
        self.ran = True


def test_runtime_factory_not_used_when_runtime_already_attached() -> None:
    service = CloudService("demo")
    runtime = DummyRuntime()
    factory_runtime = CountingFactoryRuntime()

    service.attach_runtime(runtime)

    def factory(_service: CloudService) -> ServiceRuntime:
        return factory_runtime

    service.set_runtime_factory(factory)
    service.run()

    assert runtime.ran is True
    assert factory_runtime.ran is False
