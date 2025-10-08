"""Integration tests for the queue runtime built on Temporal."""
from __future__ import annotations

import asyncio
import socket
from contextlib import suppress

import pytest

pytestmark = pytest.mark.usefixtures("router_stub")

from cloudtools import (
    CloudService,
    QueueRuntimeConfig,
    ServiceClient,
    ServiceContext,
    TaskQueueRuntime,
    WORKFLOW_ID_PREFIX,
)


def _temporal_available(address: str) -> bool:
    host, _, port = address.partition(":")
    if not port:
        port = "7233"
    try:
        with socket.create_connection((host, int(port)), timeout=1):
            return True
    except OSError:
        return False


@pytest.mark.asyncio
async def test_runtime_executes_task_via_queue() -> None:
    config = QueueRuntimeConfig()
    if not _temporal_available(config.address):
        pytest.skip(f"Temporal dev server is not reachable on {config.address}.")

    service = CloudService("ping-test")

    @service.action
    async def make_reply(message: str) -> str:
        return f"reply:{message}"

    @service.task("ping")
    async def ping(payload: dict, ctx: ServiceContext) -> dict:
        response = await ctx.action("make_reply", payload["message"])
        return {"reply": response}

    runtime = TaskQueueRuntime(config)
    service.attach_runtime(runtime)

    worker_task = asyncio.create_task(runtime.serve())
    await runtime.wait_until_ready(timeout=10)

    client = ServiceClient()

    try:
        result = await client.call("ping-test", "ping", {"message": "hello"})
        assert result == {"reply": "reply:hello"}
    finally:
        await client.close()
        await runtime.shutdown()
        with suppress(asyncio.CancelledError):
            worker_task.cancel()
            await worker_task


@pytest.mark.asyncio
async def test_task_can_start_child_workflow() -> None:
    config = QueueRuntimeConfig()
    if not _temporal_available(config.address):
        pytest.skip(f"Temporal dev server is not reachable on {config.address}.")

    service = CloudService("child-example")

    @service.task("child")
    async def child(payload: dict, ctx: ServiceContext) -> dict:
        return {"child_reply": payload["message"].upper()}

    @service.task("parent")
    async def parent(payload: dict, ctx: ServiceContext) -> dict:
        child_result = await ctx.call("child", payload)
        handle = await ctx.start_child_task("child", payload)
        second_result = await handle
        return {
            "first": child_result,
            "second": second_result,
            "handle_id": handle.id,
        }

    runtime = TaskQueueRuntime(config)
    service.attach_runtime(runtime)

    worker_task = asyncio.create_task(runtime.serve())
    await runtime.wait_until_ready(timeout=10)

    client = ServiceClient()

    try:
        result = await client.call(
            "child-example",
            "parent",
            {"message": "hi"},
        )
        assert result["first"] == {"child_reply": "HI"}
        assert result["second"] == {"child_reply": "HI"}
        assert result["handle_id"].startswith(
            f"{WORKFLOW_ID_PREFIX}-child-example-child-"
        )
    finally:
        await client.close()
        await runtime.shutdown()
        with suppress(asyncio.CancelledError):
            worker_task.cancel()
            await worker_task


@pytest.mark.asyncio
async def test_task_can_call_other_service_task() -> None:
    config = QueueRuntimeConfig()
    if not _temporal_available(config.address):
        pytest.skip(f"Temporal dev server is not reachable on {config.address}.")

    service_a = CloudService("alpha-service")
    service_b = CloudService("beta-service")

    @service_b.task("echo")
    async def echo(payload: dict, ctx: ServiceContext) -> dict:
        return {"echo": payload["value"]}

    @service_a.task("caller")
    async def caller(payload: dict, ctx: ServiceContext) -> dict:
        response = await ctx.call("beta-service.echo", payload)
        handle = await ctx.start_child_task("beta-service.echo", payload)
        awaited = await handle
        return {
            "via_call": response,
            "via_handle": awaited,
            "handle_id": handle.id,
        }

    runtime_a = TaskQueueRuntime(QueueRuntimeConfig())
    runtime_b = TaskQueueRuntime(QueueRuntimeConfig())
    service_a.attach_runtime(runtime_a)
    service_b.attach_runtime(runtime_b)

    worker_a = asyncio.create_task(runtime_a.serve())
    worker_b = asyncio.create_task(runtime_b.serve())
    await asyncio.gather(
        runtime_a.wait_until_ready(timeout=10),
        runtime_b.wait_until_ready(timeout=10),
    )

    client = ServiceClient()

    try:
        result = await client.call(
            "alpha-service",
            "caller",
            {"value": "from-parent"},
        )
        expected = {"echo": "from-parent"}
        assert result["via_call"] == expected
        assert result["via_handle"] == expected
        assert result["handle_id"].startswith(
            f"{WORKFLOW_ID_PREFIX}-beta-service-echo-"
        )
    finally:
        await client.close()
        await asyncio.gather(runtime_a.shutdown(), runtime_b.shutdown())
        for task in (worker_a, worker_b):
            with suppress(asyncio.CancelledError):
                task.cancel()
                await task
