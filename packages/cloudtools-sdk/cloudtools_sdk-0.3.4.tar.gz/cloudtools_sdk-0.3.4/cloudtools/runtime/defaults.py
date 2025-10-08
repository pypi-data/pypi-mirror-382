"""Default runtime factory for CloudService."""
from __future__ import annotations

from typing import TYPE_CHECKING

from .queue import QueueRuntimeConfig, TaskQueueRuntime

if TYPE_CHECKING:  # pragma: no cover - for type checking only
    from ..service import CloudService
    from .base import ServiceRuntime


def default_runtime_factory(service: "CloudService") -> "ServiceRuntime":
    """Return the default runtime instance for the given service."""
    config = QueueRuntimeConfig()
    if service.default_activity_timeout is not None:
        config.activity_timeout = service.default_activity_timeout
    if service.default_workflow_run_timeout is not None:
        config.workflow_run_timeout = service.default_workflow_run_timeout
    return TaskQueueRuntime(config)
