import httpx
from laydata_core.errors import LayDataError
from laydata_core.types import SpaceData


class Space:
    def __init__(self, client: httpx.AsyncClient, data: SpaceData):
        self._client = client
        self._data = data

    @property
    def id(self) -> str:
        return self._data["id"]

    @property
    def name(self) -> str:
        return self._data["name"]

    @property
    def role(self) -> str | None:
        return self._data.get("role")

    @property
    def organization(self) -> str | None:
        return self._data.get("organization")

    async def bases(self) -> list["Base"]:
        from laydata.base import BaseClient
        base_client = BaseClient(self._client, self.id)
        return await base_client.list()

    async def base(self, name: str) -> "Base":
        from laydata.base import BaseClient
        base_client = BaseClient(self._client, self.id)
        return await base_client.create_or_get(name)

    async def delete(self) -> None:
        from laydata_core.errors import map_teable_error
        try:
            response = await self._client.delete(f"/space/{self.id}")
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
        return f"Space(id={self.id}, name={self.name})"


class SpaceClient:
    def __init__(self, client: httpx.AsyncClient):
        self._client = client

    async def list(self) -> list[Space]:
        try:
            response = await self._client.get("/space")
            response.raise_for_status()
            spaces_data = response.json()
            return [Space(self._client, space) for space in spaces_data]
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

    async def create_or_get(self, name: str) -> Space:
        try:
            response = await self._client.post("/space", json={"name": name})
            response.raise_for_status()
            space_data = response.json()
            return Space(self._client, space_data)
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

