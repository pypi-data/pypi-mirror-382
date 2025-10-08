"""Client for calling service tasks through the runtime queue."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Optional
from uuid import uuid4

from temporalio.client import Client

from .constants import WORKFLOW_ID_PREFIX
from .runtime.queue import DEFAULT_WORKFLOW_TIMEOUT, workflow_name


@dataclass
class ServiceClientConfig:
    address: str = "127.0.0.1:7233"
    namespace: str = "default"
    workflow_run_timeout: timedelta = DEFAULT_WORKFLOW_TIMEOUT

    def resolve_task_queue(self, service_name: str) -> str:
        return f"{service_name}-queue"

    def resolve_workflow_name(self, service_name: str, task_name: str) -> str:
        return workflow_name(service_name, task_name)


class ServiceClient:
    """Helper for calling service tasks via the configured runtime."""

    def __init__(self, config: Optional[ServiceClientConfig] = None) -> None:
        self._config = config or ServiceClientConfig()
        self._client: Optional[Client] = None
        self._client_lock = asyncio.Lock()

    @property
    def config(self) -> ServiceClientConfig:
        return self._config

    async def call(
        self,
        service_name: str,
        task_name: str,
        payload: Any,
        *,
        task_queue: Optional[str] = None,
        id: Optional[str] = None,
    ) -> Any:
        client = await self._ensure_client()
        workflow_id = id or f"{WORKFLOW_ID_PREFIX}-{service_name}-{task_name}-{uuid4()}"
        queue = task_queue or self._config.resolve_task_queue(service_name)
        workflow_id_name = self._config.resolve_workflow_name(service_name, task_name)

        return await client.execute_workflow(
            workflow_id_name,
            args=[payload],
            id=workflow_id,
            task_queue=queue,
            run_timeout=self._config.workflow_run_timeout,
        )

    async def close(self) -> None:
        if self._client is not None:
            close = getattr(self._client, "close", None)
            if callable(close):
                maybe_awaitable = close()
                if hasattr(maybe_awaitable, "__await__"):
                    await maybe_awaitable
            self._client = None

    async def _ensure_client(self) -> Client:
        if self._client is not None:
            return self._client
        async with self._client_lock:
            if self._client is None:
                self._client = await Client.connect(
                    self._config.address,
                    namespace=self._config.namespace,
                )
            return self._client

    async def reconfigure(self, config: ServiceClientConfig) -> None:
        """Update the Temporal connection settings, closing existing client if needed."""
        if self._config == config:
            return
        async with self._client_lock:
            if self._client is not None:
                close = getattr(self._client, "close", None)
                if callable(close):
                    maybe_awaitable = close()
                    if hasattr(maybe_awaitable, "__await__"):
                        await maybe_awaitable
            self._client = None
            self._config = config
