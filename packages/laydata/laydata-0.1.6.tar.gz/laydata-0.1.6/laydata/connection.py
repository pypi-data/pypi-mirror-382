import httpx
from laydata_core.types import VersionResponse, HealthResponse
from laydata_core.logger import get_logger

logger = get_logger("laydata.client.connection")


class Connection:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    async def ping(self) -> bool:
        try:
            logger.debug("Pinging server")
            response = await self.client.get("/ping")
            data = response.json()
            result = data.get("ok", False)
            logger.debug(f"Ping result: {result}")
            return result
        except Exception as e:
            logger.error(f"Ping failed: {e}")
            return False

    async def version(self) -> VersionResponse:
        logger.debug("Fetching server version")
        response = await self.client.get("/version")
        response.raise_for_status()
        version_data = response.json()
        logger.info(f"Server version: {version_data.get('server')}, protocol: {version_data.get('protocol')}")
        return version_data

    async def health(self) -> HealthResponse:
        logger.debug("Checking server health")
        response = await self.client.get("/health")
        response.raise_for_status()
        health_data = response.json()
        logger.info(f"Health: status={health_data.get('status')}, teable={health_data.get('teable')}")
        return health_data

