"""KV client for interacting with the CloudTools KV service."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

import httpx

from .config import get_config_value

LOGGER = logging.getLogger(__name__)

_kv_client: Optional["KVClient"] = None
_kv_lock = asyncio.Lock()


class KVError(RuntimeError):
    pass


class KVNotFoundError(KVError):
    pass


class KVClient:
    def __init__(self, kv_url: Optional[str] = None) -> None:
        self._kv_url = get_config_value(
            "KV_URL", "KV_SERVICE_ADDRESS",
            default="http://127.0.0.1:8000",
            explicit=kv_url,
            strip_slash=True
        )
        self._client: Optional[httpx.AsyncClient] = None
        self._client_lock = asyncio.Lock()
        LOGGER.debug(f"KVClient initialized with URL: {self._kv_url}")

    async def _get_http(self) -> httpx.AsyncClient:
        if self._client is None:
            async with self._client_lock:
                if self._client is None:
                    self._client = httpx.AsyncClient(
                        base_url=self._kv_url,
                        timeout=5.0,
                        follow_redirects=True
                    )
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _build_path(self, key: str) -> str:
        key = key.lstrip("/")
        return f"/v1/kv/{key}"

    async def get(self, key: str) -> Any:
        path = self._build_path(key)
        http = await self._get_http()
        
        try:
            response = await http.get(path)
            if response.status_code == 404:
                raise KVNotFoundError(f"Key not found: {key}")
            response.raise_for_status()
            return response.json()
        except KVNotFoundError:
            raise
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise KVNotFoundError(f"Key not found: {key}") from e
            raise KVError(f"Failed to get key '{key}': {e}") from e
        except Exception as e:
            raise KVError(f"Failed to get key '{key}': {e}") from e

    async def set(self, key: str, value: Any) -> None:
        path = self._build_path(key)
        http = await self._get_http()
        
        try:
            response = await http.put(path, json=value)
            response.raise_for_status()
        except Exception as e:
            raise KVError(f"Failed to set key '{key}': {e}") from e

    async def delete(self, key: str) -> None:
        path = self._build_path(key)
        http = await self._get_http()
        
        try:
            response = await http.delete(path)
            response.raise_for_status()
        except Exception as e:
            raise KVError(f"Failed to delete key '{key}': {e}") from e

    def update_url(self, kv_url: str) -> None:
        new_url = kv_url.rstrip("/")
        if new_url != self._kv_url:
            self._kv_url = new_url
            LOGGER.info(f"KV URL updated to: {self._kv_url}")


async def ensure_kv_client(kv_url: Optional[str] = None) -> KVClient:
    global _kv_client
    
    async with _kv_lock:
        if _kv_client is None:
            _kv_client = KVClient(kv_url)
            LOGGER.debug("Global KV client created")
        elif kv_url is not None:
            _kv_client.update_url(kv_url)
    
    return _kv_client


def get_kv_client() -> KVClient:
    if _kv_client is None:
        raise KVError("KV client not initialized. Call 'await ensure_kv_client()' first or use module-level functions.")
    return _kv_client


async def stop_kv_client() -> None:
    global _kv_client
    
    async with _kv_lock:
        if _kv_client is not None:
            await _kv_client.close()
            _kv_client = None
            LOGGER.debug("Global KV client stopped")


async def get(key: str) -> Any:
    client = await ensure_kv_client()
    return await client.get(key)


async def set(key: str, value: Any) -> None:
    client = await ensure_kv_client()
    await client.set(key, value)


async def delete(key: str) -> None:
    client = await ensure_kv_client()
    await client.delete(key)


class _KVProxy:
    async def get(self, key: str) -> Any:
        return await get(key)
    
    async def set(self, key: str, value: Any) -> None:
        await set(key, value)
    
    async def delete(self, key: str) -> None:
        await delete(key)


kv = _KVProxy()
