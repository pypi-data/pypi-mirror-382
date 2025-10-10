from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional

import httpx

from .config import get_config_value

LOGGER = logging.getLogger(__name__)

_table_client: Optional["TableClient"] = None
_table_lock = asyncio.Lock()


class TableError(RuntimeError):
    pass


class TableNotFoundError(TableError):
    pass


class LazyTableHandle:
    def __init__(self, space_name: str, base_name: str, table_name: str):
        self._space_name = space_name
        self._base_name = base_name
        self._table_name = table_name
        self._resolved_handle: Optional["TableHandle"] = None
        self._resolution_error: Optional[Exception] = None

    async def _ensure_resolved(self) -> "TableHandle":
        if self._resolution_error:
            raise self._resolution_error
        
        if self._resolved_handle is None:
            try:
                client = await ensure_table_client()
                self._resolved_handle = await client.get_table_handle_by_name(
                    self._space_name,
                    self._base_name,
                    self._table_name
                )
            except Exception as e:
                self._resolution_error = e
                raise
        
        return self._resolved_handle

    @property
    def space_name(self) -> str:
        return self._space_name

    @property
    def base_name(self) -> str:
        return self._base_name

    @property
    def table_name(self) -> str:
        return self._table_name

    @property
    def base_id(self) -> Optional[str]:
        return self._resolved_handle.base_id if self._resolved_handle else None

    @property
    def table_id(self) -> Optional[str]:
        return self._resolved_handle.table_id if self._resolved_handle else None

    async def validate(self) -> None:
        await self._ensure_resolved()

    async def create_record(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        handle = await self._ensure_resolved()
        return await handle.create_record(fields)

    async def batch_create_records(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        handle = await self._ensure_resolved()
        return await handle.batch_create_records(records)

    async def get_records(
        self,
        filter: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        handle = await self._ensure_resolved()
        filter = await _normalize_filter(handle, filter)
        print(f">>> LazyTableHandle.get_records: table={self._table_name}, filter={filter}, limit={limit}, skip={skip}")
        result = await handle.get_records(filter, limit, skip)
        print(f">>> LazyTableHandle.get_records: table={self._table_name}, result={result}")
        return result

    async def update_record(self, record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        handle = await self._ensure_resolved()
        return await handle.update_record(record_id, fields)

    async def batch_update_records(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        handle = await self._ensure_resolved()
        return await handle.batch_update_records(updates)

    async def delete_record(self, record_id: str) -> None:
        handle = await self._ensure_resolved()
        await handle.delete_record(record_id)

    async def batch_delete_records(self, record_ids: List[str]) -> Dict[str, Any]:
        handle = await self._ensure_resolved()
        return await handle.batch_delete_records(record_ids)

    async def get_info(self) -> Dict[str, Any]:
        handle = await self._ensure_resolved()
        return await handle.get_info()

    async def add_field(
        self,
        name: str,
        field_type: str,
        required: bool = False,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        handle = await self._ensure_resolved()
        return await handle.add_field(name, field_type, required, options)

    async def delete_field(self, field_id: str) -> None:
        handle = await self._ensure_resolved()
        await handle.delete_field(handle.table_id, field_id)

    async def delete(self) -> None:
        handle = await self._ensure_resolved()
        await handle.delete()


class TableHandle:
    def __init__(self, client: "TableClient", base_id: str, table_id: str, table_name: Optional[str] = None):
        self._client = client
        self.base_id = base_id
        self.table_id = table_id
        self.name = table_name

    async def create_record(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        return await self._client.create_record(self.base_id, self.table_id, fields)

    async def batch_create_records(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        return await self._client.batch_create_records(self.base_id, self.table_id, records)

    async def get_records(
        self,
        filter: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        filter = await _normalize_filter(self, filter)
        print(f">>> TableHandle.get_records: base={self.base_id}, table={self.table_id}, filter={filter}, limit={limit}, skip={skip}")
        result = await self._client.get_records(self.base_id, self.table_id, filter, limit, skip)
        print(f">>> TableHandle.get_records: base={self.base_id}, table={self.table_id}, filter={filter}, limit={limit}, skip={skip}, result={result}")
        return result

    async def update_record(self, record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        return await self._client.update_record(self.base_id, self.table_id, record_id, fields)

    async def batch_update_records(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        return await self._client.batch_update_records(self.base_id, self.table_id, updates)

    async def delete_record(self, record_id: str) -> None:
        await self._client.delete_record(self.base_id, self.table_id, record_id)

    async def batch_delete_records(self, record_ids: List[str]) -> Dict[str, Any]:
        return await self._client.batch_delete_records(self.base_id, self.table_id, record_ids)

    async def get_info(self) -> Dict[str, Any]:
        return await self._client.get_table(self.base_id, self.table_id)

    async def add_field(
        self,
        name: str,
        field_type: str,
        required: bool = False,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return await self._client.add_field(self.base_id, self.table_id, name, field_type, required, options)

    async def delete_field(self, table_id: str, field_id: str) -> None:
        await self._client.delete_field(table_id, field_id)

    async def delete(self) -> None:
        await self._client.delete_table(self.base_id, self.table_id)


class TableClient:
    def __init__(self, table_url: Optional[str] = None) -> None:
        self._table_url = get_config_value(
            "TABLE_URL", "TABLE_SERVICE_ADDRESS",
            default="http://127.0.0.1:8001",
            explicit=table_url,
            strip_slash=True
        )
        self._client: Optional[httpx.AsyncClient] = None
        self._client_lock = asyncio.Lock()
        print(f"TableClient initialized with URL: {self._table_url}")
        LOGGER.debug(f"TableClient initialized with URL: {self._table_url}")

    async def _get_http(self) -> httpx.AsyncClient:
        if self._client is None:
            async with self._client_lock:
                if self._client is None:
                    self._client = httpx.AsyncClient(
                        base_url=self._table_url,
                        timeout=30.0,
                        follow_redirects=True
                    )
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def update_url(self, table_url: str) -> None:
        new_url = table_url.rstrip("/")
        if new_url != self._table_url:
            self._table_url = new_url
            LOGGER.info(f"Table URL updated to: {self._table_url}")

    async def create_space(self, name: str) -> str:
        http = await self._get_http()
        try:
            response = await http.post("/v1/spaces", json={"name": name})
            response.raise_for_status()
            result = response.json()
            return result["space_id"]
        except Exception as e:
            raise TableError(f"Failed to create space '{name}': {e}") from e

    async def create_base(self, space_id: str, name: str) -> str:
        http = await self._get_http()
        try:
            response = await http.post(
                "/v1/bases",
                json={"space_id": space_id, "name": name}
            )
            response.raise_for_status()
            result = response.json()
            return result["base_id"]
        except Exception as e:
            raise TableError(f"Failed to create base '{name}': {e}") from e

    async def create_table(
        self,
        base_id: str,
        name: str,
        fields: List[Dict[str, Any]],
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        http = await self._get_http()
        try:
            response = await http.post(
                "/v1/tables",
                json={
                    "base_id": base_id,
                    "name": name,
                    "fields": fields,
                    "description": description
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise TableError(f"Failed to create table '{name}': {e}") from e

    async def get_table(self, base_id: str, table_id: str) -> Dict[str, Any]:
        http = await self._get_http()
        try:
            response = await http.get(f"/v1/tables/{base_id}/{table_id}")
            if response.status_code == 404:
                raise TableNotFoundError(f"Table not found: {table_id}")
            response.raise_for_status()
            return response.json()
        except TableNotFoundError:
            raise
        except Exception as e:
            raise TableError(f"Failed to get table '{table_id}': {e}") from e

    async def delete_table(self, base_id: str, table_id: str) -> None:
        http = await self._get_http()
        try:
            response = await http.delete(f"/v1/tables/{base_id}/{table_id}")
            response.raise_for_status()
        except Exception as e:
            raise TableError(f"Failed to delete table '{table_id}': {e}") from e

    async def add_field(
        self,
        base_id: str,
        table_id: str,
        name: str,
        field_type: str,
        required: bool = False,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        http = await self._get_http()
        try:
            response = await http.post(
                "/v1/fields",
                json={
                    "base_id": base_id,
                    "table_id": table_id,
                    "name": name,
                    "field_type": field_type,
                    "required": required,
                    "options": options
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise TableError(f"Failed to add field '{name}': {e}") from e

    async def delete_field(self, table_id: str, field_id: str) -> None:
        http = await self._get_http()
        try:
            response = await http.delete(f"/v1/fields/{table_id}/{field_id}")
            response.raise_for_status()
        except Exception as e:
            raise TableError(f"Failed to delete field '{field_id}': {e}") from e

    async def list_spaces(self) -> List[Dict[str, Any]]:
        http = await self._get_http()
        try:
            response = await http.get("/v1/spaces")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise TableError(f"Failed to list spaces: {e}") from e

    async def list_bases(self, space_id: str) -> List[Dict[str, Any]]:
        http = await self._get_http()
        try:
            response = await http.get(f"/v1/spaces/{space_id}/bases")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise TableError(f"Failed to list bases: {e}") from e

    async def list_tables(self, base_id: str) -> List[Dict[str, Any]]:
        http = await self._get_http()
        try:
            response = await http.get(f"/v1/bases/{base_id}/tables")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise TableError(f"Failed to list tables: {e}") from e

    async def get_table_handle(
        self,
        base_id: str,
        table_id: str
    ) -> TableHandle:
        table_info = await self.get_table(base_id, table_id)
        return TableHandle(self, base_id, table_id, table_info.get("name"))

    async def get_table_handle_by_name(
        self,
        space_name: str,
        base_name: str,
        table_name: str
    ) -> TableHandle:
        spaces = await self.list_spaces()
        space = next((s for s in spaces if s["name"] == space_name), None)
        if not space:
            raise TableNotFoundError(f"Space '{space_name}' not found")
        
        bases = await self.list_bases(space["space_id"])
        base = next((b for b in bases if b["name"] == base_name), None)
        if not base:
            raise TableNotFoundError(f"Base '{base_name}' not found in space '{space_name}'")
        
        tables = await self.list_tables(base["base_id"])
        table = next((t for t in tables if t["name"] == table_name), None)
        if not table:
            raise TableNotFoundError(f"Table '{table_name}' not found in base '{base_name}'")
        
        return TableHandle(self, base["base_id"], table["table_id"], table_name)

    async def create_record(
        self,
        base_id: str,
        table_id: str,
        fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        http = await self._get_http()
        try:
            response = await http.post(
                "/v1/records",
                json={
                    "base_id": base_id,
                    "table_id": table_id,
                    "fields": fields
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise TableError(f"Failed to create record: {e}") from e

    async def batch_create_records(
        self,
        base_id: str,
        table_id: str,
        records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        http = await self._get_http()
        try:
            response = await http.post(
                "/v1/records/batch",
                json={
                    "base_id": base_id,
                    "table_id": table_id,
                    "records": records
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise TableError(f"Failed to batch create records: {e}") from e

    async def get_records(
        self,
        base_id: str,
        table_id: str,
        filter: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        http = await self._get_http()
        try:
            print(">>> TableClient.get_records REQUEST:", {
                "base_id": base_id,
                "table_id": table_id,
                "filter": filter,
                "limit": limit,
                "skip": skip
            })
            response = await http.post(
                "/v1/records/query",
                json={
                    "base_id": base_id,
                    "table_id": table_id,
                    "filter": filter,
                    "limit": limit,
                    "skip": skip
                }
            )
            print("<<< TableClient.get_records RESPONSE:", response.status_code, response.text[:500])
            response.raise_for_status()
            result = response.json()
            return result["records"]
        except Exception as e:
            raise TableError(f"Failed to get records: {e}") from e

    async def update_record(
        self,
        base_id: str,
        table_id: str,
        record_id: str,
        fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        http = await self._get_http()
        try:
            response = await http.put(
                "/v1/records",
                json={
                    "base_id": base_id,
                    "table_id": table_id,
                    "record_id": record_id,
                    "fields": fields
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise TableError(f"Failed to update record '{record_id}': {e}") from e

    async def batch_update_records(
        self,
        base_id: str,
        table_id: str,
        updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        http = await self._get_http()
        try:
            response = await http.put(
                "/v1/records/batch",
                json={
                    "base_id": base_id,
                    "table_id": table_id,
                    "updates": updates
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise TableError(f"Failed to batch update records: {e}") from e

    async def delete_record(
        self,
        base_id: str,
        table_id: str,
        record_id: str
    ) -> None:
        http = await self._get_http()
        try:
            response = await http.request(
                "DELETE",
                "/v1/records",
                json={
                    "base_id": base_id,
                    "table_id": table_id,
                    "record_id": record_id
                }
            )
            response.raise_for_status()
        except Exception as e:
            raise TableError(f"Failed to delete record of'{record_id}': {e}") from e

    async def batch_delete_records(
        self,
        base_id: str,
        table_id: str,
        record_ids: List[str]
    ) -> Dict[str, Any]:
        http = await self._get_http()
        try:
            response = await http.request(
                "DELETE",
                "/v1/records/batch",
                json={
                    "base_id": base_id,
                    "table_id": table_id,
                    "record_ids": record_ids
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise TableError(f"Failed to batch delete records: {e}") from e


async def ensure_table_client(table_url: Optional[str] = None) -> TableClient:
    global _table_client
    
    async with _table_lock:
        if _table_client is None:
            _table_client = TableClient(table_url)
            LOGGER.debug("Global table client created")
        elif table_url is not None:
            _table_client.update_url(table_url)
    
    return _table_client


def get_table_client() -> TableClient:
    if _table_client is None:
        raise TableError("Table client not initialized. Call 'await ensure_table_client()' first or use module-level functions.")
    return _table_client


async def stop_table_client() -> None:
    global _table_client
    
    async with _table_lock:
        if _table_client is not None:
            await _table_client.close()
            _table_client = None
            LOGGER.debug("Global table client stopped")


async def create_space(name: str) -> str:
    client = await ensure_table_client()
    return await client.create_space(name)


async def create_base(space_id: str, name: str) -> str:
    client = await ensure_table_client()
    return await client.create_base(space_id, name)


async def create_table(
    base_id: str,
    name: str,
    fields: List[Dict[str, Any]],
    description: Optional[str] = None
) -> Dict[str, Any]:
    client = await ensure_table_client()
    return await client.create_table(base_id, name, fields, description)


async def get_table(base_id: str, table_id: str) -> Dict[str, Any]:
    client = await ensure_table_client()
    return await client.get_table(base_id, table_id)


async def delete_table(base_id: str, table_id: str) -> None:
    client = await ensure_table_client()
    await client.delete_table(base_id, table_id)


async def create_record(
    base_id: str,
    table_id: str,
    fields: Dict[str, Any]
) -> Dict[str, Any]:
    client = await ensure_table_client()
    return await client.create_record(base_id, table_id, fields)


async def batch_create_records(
    base_id: str,
    table_id: str,
    records: List[Dict[str, Any]]
) -> Dict[str, Any]:
    client = await ensure_table_client()
    return await client.batch_create_records(base_id, table_id, records)


async def get_records(
    base_id: str,
    table_id: str,
    filter: Optional[Dict[str, Any]] = None,
    limit: int = 100,
    skip: int = 0
) -> List[Dict[str, Any]]:
    client = await ensure_table_client()
    return await client.get_records(base_id, table_id, filter, limit, skip)


async def update_record(
    base_id: str,
    table_id: str,
    record_id: str,
    fields: Dict[str, Any]
) -> Dict[str, Any]:
    client = await ensure_table_client()
    return await client.update_record(base_id, table_id, record_id, fields)


async def batch_update_records(
    base_id: str,
    table_id: str,
    updates: List[Dict[str, Any]]
) -> Dict[str, Any]:
    client = await ensure_table_client()
    return await client.batch_update_records(base_id, table_id, updates)


async def delete_record(
    base_id: str,
    table_id: str,
    record_id: str
) -> None:
    client = await ensure_table_client()
    await client.delete_record(base_id, table_id, record_id)


async def batch_delete_records(
    base_id: str,
    table_id: str,
    record_ids: List[str]
) -> Dict[str, Any]:
    client = await ensure_table_client()
    return await client.batch_delete_records(base_id, table_id, record_ids)


async def add_field(
    base_id: str,
    table_id: str,
    name: str,
    field_type: str,
    required: bool = False,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    client = await ensure_table_client()
    return await client.add_field(base_id, table_id, name, field_type, required, options)


async def delete_field(table_id: str, field_id: str) -> None:
    client = await ensure_table_client()
    await client.delete_field(table_id, field_id)


async def list_spaces() -> List[Dict[str, Any]]:
    client = await ensure_table_client()
    return await client.list_spaces()


async def list_bases(space_id: str) -> List[Dict[str, Any]]:
    client = await ensure_table_client()
    return await client.list_bases(space_id)


async def list_tables(base_id: str) -> List[Dict[str, Any]]:
    client = await ensure_table_client()
    return await client.list_tables(base_id)


async def get_table_handle(base_id: str, table_id: str) -> TableHandle:
    client = await ensure_table_client()
    return await client.get_table_handle(base_id, table_id)


async def get_table_handle_by_name(
    space_name: str,
    base_name: str,
    table_name: str
) -> TableHandle:
    client = await ensure_table_client()
    return await client.get_table_handle_by_name(space_name, base_name, table_name)


def table(space_name: str, base_name: str, table_name: str) -> LazyTableHandle:
    return LazyTableHandle(space_name, base_name, table_name)


def table_sync(space_name: str, base_name: str, table_name: str) -> LazyTableHandle:
    handle = LazyTableHandle(space_name, base_name, table_name)
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            raise RuntimeError(
                "table_sync() cannot be called from an already running event loop. "
                "Use table() instead and call await handle.validate() in your async code."
            )
    except RuntimeError:
        pass
    
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(handle.validate())
        return handle
    finally:
        loop.close()
        try:
            asyncio.set_event_loop(asyncio.new_event_loop())
        except Exception:
            pass

async def _normalize_filter(table_handle, simple_filter: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not simple_filter:
        return None

    # Получаем схему таблицы
    info = await table_handle.get_info()
    fields = info.get("fields", [])
    field_map = {f["name"]: f.get("field_id") for f in fields if "field_id" in f}

    def normalize_filterset(filterset: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized = []
        for f in filterset:
            # рекурсивно обрабатываем вложенные filterSet
            if "filterSet" in f:
                f["filterSet"] = normalize_filterset(f["filterSet"])
                normalized.append(f)
                continue

            if "fieldId" in f:
                # уже нормализованная запись
                normalized.append(f)
                continue

            field_name = f.get("fieldName")
            if not field_name:
                raise TableError("Filter entry missing fieldName/fieldId")

            if field_name not in field_map:
                table_name = getattr(table_handle, "name", None)
                raise TableError(f"Field '{field_name}' not found in table {table_name or '?'}")

            normalized.append({
                "fieldId": field_map[field_name],
                "operator": f.get("operator", "is"),
                "value": f.get("value")
            })
        return normalized

    # Если это уже filterSet — прогоняем рекурсивно
    if "filterSet" in simple_filter:
        return {
            "filterSet": normalize_filterset(simple_filter["filterSet"]),
            "conjunction": simple_filter.get("conjunction", "and")
        }

    # Старый формат { "fieldName": "value" }
    filter_set = []
    for key, value in simple_filter.items():
        if key not in field_map:
            table_name = getattr(table_handle, "name", None)
            raise TableError(f"Field '{key}' not found in table {table_name or '?'}")
        filter_set.append({
            "fieldId": field_map[key],
            "operator": "is",
            "value": value
        })

    return {"filterSet": filter_set, "conjunction": "and"}


class _TableProxy:
    def __call__(self, space_name: str, base_name: str, table_name: str) -> LazyTableHandle:
        return LazyTableHandle(space_name, base_name, table_name)
    
    async def get(self, space_name: str, base_name: str, table_name: str) -> TableHandle:
        return await get_table_handle_by_name(space_name, base_name, table_name)
    
    async def create_space(self, name: str) -> str:
        return await create_space(name)
    
    async def list_spaces(self) -> List[Dict[str, Any]]:
        return await list_spaces()
    
    async def list_bases(self, space_id: str) -> List[Dict[str, Any]]:
        return await list_bases(space_id)
    
    async def list_tables(self, base_id: str) -> List[Dict[str, Any]]:
        return await list_tables(base_id)
    
    async def create_base(self, space_id: str, name: str) -> str:
        return await create_base(space_id, name)
    
    async def create_table(
        self,
        base_id: str,
        name: str,
        fields: List[Dict[str, Any]],
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        return await create_table(base_id, name, fields, description)
    
    async def get_table(self, base_id: str, table_id: str) -> Dict[str, Any]:
        return await get_table(base_id, table_id)
    
    async def delete_table(self, base_id: str, table_id: str) -> None:
        await delete_table(base_id, table_id)
    
    async def create_record(
        self,
        base_id: str,
        table_id: str,
        fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await create_record(base_id, table_id, fields)
    
    async def batch_create_records(
        self,
        base_id: str,
        table_id: str,
        records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        return await batch_create_records(base_id, table_id, records)
    
    async def get_records(
        self,
        base_id: str,
        table_id: str,
        filter: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        return await get_records(base_id, table_id, filter, limit, skip)
    
    async def update_record(
        self,
        base_id: str,
        table_id: str,
        record_id: str,
        fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await update_record(base_id, table_id, record_id, fields)
    
    async def batch_update_records(
        self,
        base_id: str,
        table_id: str,
        updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        return await batch_update_records(base_id, table_id, updates)
    
    async def delete_record(
        self,
        base_id: str,
        table_id: str,
        record_id: str
    ) -> None:
        await delete_record(base_id, table_id, record_id)
    
    async def batch_delete_records(
        self,
        base_id: str,
        table_id: str,
        record_ids: List[str]
    ) -> Dict[str, Any]:
        return await batch_delete_records(base_id, table_id, record_ids)


table = _TableProxy()

