import httpx
from laydata_core.errors import LayDataError
from laydata_core.types import BaseData


class Base:
    def __init__(self, client: httpx.AsyncClient, data: BaseData):
        self._client = client
        self._data = data

    @property
    def id(self) -> str:
        return self._data["id"]

    @property
    def name(self) -> str:
        return self._data["name"]

    @property
    def space_id(self) -> str:
        return self._data["spaceId"]

    async def tables(self) -> list["Table"]:
        from laydata.table import TableClient
        table_client = TableClient(self._client, self.id)
        return await table_client.list()

    async def table(self, name: str, icon: str | None = None, description: str | None = None) -> "Table":
        from laydata.table import TableClient
        table_client = TableClient(self._client, self.id)
        return await table_client.create_or_get(name, icon=icon, description=description)

    async def delete(self) -> None:
        from laydata_core.errors import map_teable_error
        try:
            response = await self._client.delete(f"/base/{self.id}")
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                raise map_teable_error(
                    e.response.status_code,
                    error_data.get("detail", str(e)),
                    error_data.get("code")
                )
            except Exception:
                raise map_teable_error(e.response.status_code, str(e), None)

    def __repr__(self) -> str:
        return f"Base(id={self.id}, name={self.name}, space_id={self.space_id})"


class BaseClient:
    def __init__(self, client: httpx.AsyncClient, space_id: str):
        self._client = client
        self._space_id = space_id

    async def list(self) -> list[Base]:
        try:
            response = await self._client.get(f"/base?space_id={self._space_id}")
            response.raise_for_status()
            bases_data = response.json()
            return [Base(self._client, base) for base in bases_data]
        except httpx.HTTPStatusError as e:
            from laydata_core.errors import map_teable_error
            try:
                error_data = e.response.json()
                raise map_teable_error(
                    e.response.status_code,
                    error_data.get("detail", str(e)),
                    error_data.get("code")
                )
            except Exception:
                raise map_teable_error(e.response.status_code, str(e), None)

    async def create_or_get(self, name: str) -> Base:
        try:
            response = await self._client.post(
                f"/base?space_id={self._space_id}",
                json={"name": name}
            )
            response.raise_for_status()
            base_data = response.json()
            return Base(self._client, base_data)
        except httpx.HTTPStatusError as e:
            from laydata_core.errors import map_teable_error
            try:
                error_data = e.response.json()
                raise map_teable_error(
                    e.response.status_code,
                    error_data.get("detail", str(e)),
                    error_data.get("code")
                )
            except Exception:
                raise map_teable_error(e.response.status_code, str(e), None)

