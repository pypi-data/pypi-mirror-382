"""Tests for WorkflowServiceContext metadata propagation."""

from datetime import timedelta

import pytest

from cloudtools import (
    CloudService,
    QueueRuntimeConfig,
    TaskQueueRuntime,
    WORKFLOW_ID_PREFIX,
)
from cloudtools.runtime import workflow_context
from cloudtools.runtime.workflow_context import WorkflowServiceContext


@pytest.mark.asyncio
async def test_execute_action_applies_retry_policy(monkeypatch):
    """Workflow actions should honour explicit attempt limits."""

    service = CloudService("retry-service")
    runtime = TaskQueueRuntime(QueueRuntimeConfig())
    service.attach_runtime(runtime)

    @service.action(timeout=timedelta(seconds=5), attempts=2)
    async def limited_action(payload: str) -> str:
        return f"{payload}-processed"

    ctx = WorkflowServiceContext(service, runtime)

    captured_call = {}

    async def fake_execute_activity(*args, **kwargs):
        captured_call.update(kwargs)
        return "ok"

    monkeypatch.setattr(
        workflow_context.workflow,
        "execute_activity",
        fake_execute_activity,
    )

    result = await ctx._execute_action("limited_action", "data")

    assert result == "ok"
    policy = captured_call["retry_policy"]
    assert policy is not None
    assert policy.maximum_attempts == 2
    assert captured_call["start_to_close_timeout"] == timedelta(seconds=5)
    assert captured_call["schedule_to_close_timeout"] == timedelta(seconds=10)


@pytest.mark.asyncio
async def test_execute_action_respects_total_timeout(monkeypatch):
    """Explicit total timeout should override automatic scaling."""

    service = CloudService("total-timeout-service")
    runtime = TaskQueueRuntime(QueueRuntimeConfig())
    service.attach_runtime(runtime)

    @service.action(
        timeout=timedelta(seconds=5),
        total_timeout=timedelta(seconds=18),
        attempts=3,
    )
    async def limited_action(payload: str) -> str:
        return f"{payload}-processed"

    ctx = WorkflowServiceContext(service, runtime)

    captured_call = {}

    async def fake_execute_activity(*args, **kwargs):
        captured_call.update(kwargs)
        return "ok"

    monkeypatch.setattr(
        workflow_context.workflow,
        "execute_activity",
        fake_execute_activity,
    )

    await ctx._execute_action("limited_action", "data")

    assert captured_call["start_to_close_timeout"] == timedelta(seconds=5)
    assert captured_call["schedule_to_close_timeout"] == timedelta(seconds=18)


def test_child_workflow_options_include_timeout_and_retry():
    """Child workflow invocations should include timeout and retry metadata."""

    service = CloudService("timeout-service")
    runtime = TaskQueueRuntime(QueueRuntimeConfig())
    service.attach_runtime(runtime)

    @service.task("perform", timeout=timedelta(seconds=7), attempts=3)
    async def perform(payload: dict, ctx):
        return {"ok": True}

    ctx = WorkflowServiceContext(service, runtime)

    options = ctx._compose_child_options("timeout-service", "perform", {})

    assert options["run_timeout"] == timedelta(seconds=7)
    assert options["retry_policy"].maximum_attempts == 3
    assert "task_queue" not in options
    assert options["id"].startswith(
        f"{WORKFLOW_ID_PREFIX}-timeout-service-perform-"
    )


def test_child_workflow_options_fall_back_for_external_service():
    """When calling another service we fall back to runtime defaults."""

    service = CloudService("alpha")
    runtime = TaskQueueRuntime(QueueRuntimeConfig())
    service.attach_runtime(runtime)
    ctx = WorkflowServiceContext(service, runtime)

    options = ctx._compose_child_options("beta", "external-task", {})

    assert options["task_queue"] == "beta-queue"
    assert options["run_timeout"] == runtime.config.workflow_run_timeout
    assert "retry_policy" not in options
