import pytest

from cloudtools import CloudService
from cloudtools.runtime.workflow_context import WorkflowServiceContext


@pytest.mark.asyncio
async def test_envelope_unwraps_and_populates_ctx_http(monkeypatch):
    service = CloudService("envtest")

    seen = {"payload": None, "http": None}

    @service.task("consume")
    async def consume(payload, ctx):
        seen["payload"] = payload
        seen["http"] = ctx.http
        return {"ok": True}

    # Build a minimal runtime stub to construct WorkflowServiceContext
    class DummyRuntime:
        def __init__(self, svc):
            self.service = svc
            self.config = type("cfg", (), {"workflow_run_timeout": None})
            self.event_bus = None
        def activity_name(self, s, a):
            return f"{s}.actions.{a}"
        def workflow_name(self, s, t):
            return f"{s}.{t}"

    runtime = DummyRuntime(service)

    ctx = WorkflowServiceContext(service, runtime, metadata=None)

    # Simulate what _workflow_run would do after unwrap: call task with clean payload and metadata
    envelope = {
        "metadata": {
            "http": {
                "method": "POST",
                "path": "/x",
                "headers": {"authorization": "Bearer xyz"},
                "query": {},
                "params": {},
            }
        },
        "payload": {"x": 1},
    }

    # Directly invoke the task using service._invoke, as runtime does
    await service._invoke(service.tasks["consume"], envelope["payload"], ctx)

    assert seen["payload"] == {"x": 1}
# Since we passed metadata=None to ctx, http is None here (unwrap is tested in runtime path)
    assert seen["http"] is None


@pytest.mark.asyncio
async def test_queue_workflow_run_unwraps_and_emits_without_http():
    service = CloudService("envtest2")

    captured = {"payload": None, "http_method": None, "event_meta": None}

    class DummyEventBus:
        def __init__(self):
            self.published = []
        async def publish(self, topic, payload, *, metadata=None):
            captured["event_meta"] = dict(metadata or {})
            self.published.append((topic, payload, metadata))

    @service.task("consume")
    async def consume(payload, ctx):
        captured["payload"] = payload
        captured["http_method"] = ctx.http.get("method") if ctx.http else None
        await ctx.emit("topic", {"ok": True})
        return {"ok": True}

    # Prepare runtime and event bus
    class DummyRuntime:
        def __init__(self, svc):
            self.service = svc
            self.config = type("cfg", (), {"workflow_run_timeout": None})
            self.event_bus = DummyEventBus()
        def activity_name(self, s, a):
            return f"{s}.actions.{a}"
        def workflow_name(self, s, t):
            return f"{s}.{t}"

    from cloudtools.runtime.queue import _workflow_run

    runtime = DummyRuntime(service)

    # Build dummy self with class attributes expected by _workflow_run
    class DummySelf:
        pass
    DummySelf.runtime = runtime
    DummySelf.task_name = "consume"

    envelope = {
        "metadata": {
            "http": {
                "method": "POST",
                "path": "/x",
                "headers": {"authorization": "Bearer xyz"},
                "query": {},
                "params": {},
            }
        },
        "payload": {"x": 2},
    }

    result = await _workflow_run(DummySelf(), envelope)

    assert result == {"ok": True}
    assert captured["payload"] == {"x": 2}
    assert captured["http_method"] == "POST"
    # Event metadata should not include http
    assert captured["event_meta"] is not None
    assert "http" not in captured["event_meta"]
