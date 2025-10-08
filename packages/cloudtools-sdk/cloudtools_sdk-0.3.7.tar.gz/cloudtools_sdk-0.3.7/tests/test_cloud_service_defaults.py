"""Tests for CloudService default runtime configuration overrides."""

from datetime import timedelta

from cloudtools import CloudService
from cloudtools.runtime.defaults import default_runtime_factory
from cloudtools.runtime.queue import TaskQueueRuntime


def test_cloud_service_stores_default_timeouts():
    service = CloudService(
        "defaults",
        activity_timeout=30,
        workflow_run_timeout=timedelta(seconds=90),
    )

    assert service.default_activity_timeout == timedelta(seconds=30)
    assert service.default_workflow_run_timeout == timedelta(seconds=90)


def test_default_runtime_factory_applies_service_overrides():
    service = CloudService(
        "defaults",
        activity_timeout=10,
        workflow_run_timeout=60,
    )

    runtime = default_runtime_factory(service)
    assert isinstance(runtime, TaskQueueRuntime)
    assert runtime.config.activity_timeout == timedelta(seconds=10)
    assert runtime.config.workflow_run_timeout == timedelta(seconds=60)
