"""Tests for the KV client module."""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from cloudtools.kv import (
    KVClient,
    KVError,
    KVNotFoundError,
    ensure_kv_client,
    get_kv_client,
    stop_kv_client,
    kv,
)

pytestmark = pytest.mark.asyncio


class TestKVClient:
    async def test_init_default_url(self):
        client = KVClient()
        assert client._kv_url == "http://127.0.0.1:8000"

    async def test_init_custom_url(self):
        client = KVClient("http://custom:9000")
        assert client._kv_url == "http://custom:9000"

    async def test_init_from_env(self, monkeypatch):
        monkeypatch.setenv("KV_URL", "http://env-kv:8000")
        client = KVClient()
        assert client._kv_url == "http://env-kv:8000"

    async def test_build_path(self):
        client = KVClient("http://test-kv:8000")
        path = client._build_path("my-service/users/123")
        assert path == "/v1/kv/my-service/users/123"

    async def test_build_path_strips_leading_slash(self):
        client = KVClient("http://test-kv:8000")
        path = client._build_path("/my-service/users/123")
        assert path == "/v1/kv/my-service/users/123"

    async def test_set_success(self):
        client = KVClient("http://test-kv:8000")
        
        mock_httpx = MagicMock()
        mock_httpx.aclose = AsyncMock()
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_httpx.put = AsyncMock(return_value=mock_response)
        
        with patch("httpx.AsyncClient", return_value=mock_httpx):
            await client.set("my-service/test-key", {"data": "value"})
        
        mock_httpx.put.assert_called_once()
        call_args = mock_httpx.put.call_args
        assert call_args[0][0] == "/v1/kv/my-service/test-key"
        assert call_args[1]["json"] == {"data": "value"}

    async def test_get_success(self):
        client = KVClient("http://test-kv:8000")
        
        mock_httpx = MagicMock()
        mock_httpx.aclose = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = MagicMock(return_value={"data": "value"})
        mock_httpx.get = AsyncMock(return_value=mock_response)
        
        with patch("httpx.AsyncClient", return_value=mock_httpx):
            result = await client.get("my-service/test-key")
        
        assert result == {"data": "value"}
        mock_httpx.get.assert_called_once_with("/v1/kv/my-service/test-key")

    async def test_get_not_found(self):
        client = KVClient("http://test-kv:8000")
        
        mock_httpx = MagicMock()
        mock_httpx.aclose = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_httpx.get = AsyncMock(return_value=mock_response)
        
        with patch("httpx.AsyncClient", return_value=mock_httpx):
            with pytest.raises(KVNotFoundError) as exc_info:
                await client.get("my-service/missing-key")
        
        assert "Key not found" in str(exc_info.value)

    async def test_delete_success(self):
        client = KVClient("http://test-kv:8000")
        
        mock_httpx = MagicMock()
        mock_httpx.aclose = AsyncMock()
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_httpx.delete = AsyncMock(return_value=mock_response)
        
        with patch("httpx.AsyncClient", return_value=mock_httpx):
            await client.delete("my-service/test-key")
        
        mock_httpx.delete.assert_called_once_with("/v1/kv/my-service/test-key")

    async def test_update_url(self):
        client = KVClient("http://test-kv:8000")
        assert client._kv_url == "http://test-kv:8000"
        
        client.update_url("http://new-kv:9000")
        
        assert client._kv_url == "http://new-kv:9000"

    async def test_global_config_access(self):
        client = KVClient("http://test-kv:8000")
        
        mock_httpx = MagicMock()
        mock_httpx.aclose = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = MagicMock(return_value={"setting": "value"})
        mock_httpx.get = AsyncMock(return_value=mock_response)
        
        with patch("httpx.AsyncClient", return_value=mock_httpx):
            result = await client.get("global/config")
        
        assert result == {"setting": "value"}
        mock_httpx.get.assert_called_once_with("/v1/kv/global/config")


class TestModuleLevelFunctions:
    async def test_ensure_kv_client_creates_singleton(self):
        await stop_kv_client()
        
        client1 = await ensure_kv_client()
        client2 = await ensure_kv_client()
        
        assert client1 is client2
        
        await stop_kv_client()

    async def test_get_kv_client_before_ensure_raises(self):
        await stop_kv_client()
        
        with pytest.raises(KVError) as exc_info:
            get_kv_client()
        
        assert "not initialized" in str(exc_info.value)

    async def test_get_kv_client_after_ensure(self):
        await ensure_kv_client()
        client = get_kv_client()
        assert client is not None
        
        await stop_kv_client()


class TestKVProxy:
    async def test_kv_proxy_operations(self):
        mock_httpx = MagicMock()
        mock_httpx.aclose = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = MagicMock(return_value={"data": "value"})
        mock_httpx.get = AsyncMock(return_value=mock_response)
        mock_httpx.put = AsyncMock(return_value=mock_response)
        mock_httpx.delete = AsyncMock(return_value=mock_response)
        
        with patch("httpx.AsyncClient", return_value=mock_httpx):
            result = await kv.get("my-service/test-key")
            assert result == {"data": "value"}
            
            await kv.set("my-service/test-key", {"data": "new"})
            mock_httpx.put.assert_called_once()
            
            await kv.delete("my-service/test-key")
            mock_httpx.delete.assert_called_once()
        
        await stop_kv_client()

    async def test_kv_proxy_global_keys(self):
        mock_httpx = MagicMock()
        mock_httpx.aclose = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = MagicMock(return_value={"config": "shared"})
        mock_httpx.get = AsyncMock(return_value=mock_response)
        mock_httpx.put = AsyncMock(return_value=mock_response)
        
        with patch("httpx.AsyncClient", return_value=mock_httpx):
            await kv.set("global/config", {"config": "shared"})
            mock_httpx.put.assert_called_once()
            call_args = mock_httpx.put.call_args
            assert call_args[0][0] == "/v1/kv/global/config"
            
            result = await kv.get("global/config")
            assert result == {"config": "shared"}
        
        await stop_kv_client()