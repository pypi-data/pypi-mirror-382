"""Abstract base classes for service runtimes."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:  # pragma: no cover - only for static analysis
    from ..service import CloudService


class RuntimeNotAttachedError(RuntimeError):
    """Raised when accessing runtime state before a service is attached."""


class ServiceRuntime(ABC):
    """Abstract base class for service execution backends."""

    def __init__(self) -> None:
        self._service: Optional["CloudService"] = None

    def attach(self, service: "CloudService") -> None:
        """Bind the runtime to a specific service instance."""
        self._service = service
        self.on_attach(service)

    def on_attach(self, service: "CloudService") -> None:
        """Hook for subclasses to perform initialization when attached."""
        # Default implementation does nothing.
        return None

    @property
    def service(self) -> "CloudService":
        """Return the bound service or raise if not attached."""
        if self._service is None:
            raise RuntimeNotAttachedError("Runtime is not attached to any service.")
        return self._service

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> None:
        """Start the runtime. Subclasses decide how to block or schedule."""

    async def shutdown(self) -> None:
        """Optional async shutdown hook for graceful teardown."""
        return None
