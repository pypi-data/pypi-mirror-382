import httpx
import os
from laydata_core.client import init_laydata_client
from laydata.connection import Connection
from laydata.space import SpaceClient, Space
from laydata_core.types import VersionResponse, HealthResponse


class Data:
    def __init__(self, endpoint: str | None = None, token: str | None = None):
        # If endpoint not provided, honor LAYDATA_BASE_URL (README behavior), fallback to default
        self.endpoint = endpoint or os.getenv("LAYDATA_BASE_URL", "http://127.0.0.1:8077")
        self.token = token
        self._client: httpx.AsyncClient | None = None
        self._connection: Connection | None = None
        self._space_client: SpaceClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = init_laydata_client(self.endpoint, self.token)
        return self._client

    @property
    def connection(self) -> Connection:
        if self._connection is None:
            self._connection = Connection(self.client)
        return self._connection

    @property
    def _spaces(self) -> SpaceClient:
        if self._space_client is None:
            self._space_client = SpaceClient(self.client)
        return self._space_client

    async def ping(self) -> bool:
        return await self.connection.ping()

    async def version(self) -> VersionResponse:
        return await self.connection.version()

    async def health(self) -> HealthResponse:
        return await self.connection.health()

    async def spaces(self) -> list[Space]:
        return await self._spaces.list()

    async def space(self, name: str) -> Space:
        return await self._spaces.create_or_get(name)

    async def close(self):
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            self._connection = None
            self._space_client = None

