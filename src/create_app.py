from contextlib import asynccontextmanager

from redis.asyncio import Redis
import httpx
import structlog
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from core.config import settings
from core.structlog import Logger
from infrastructures.http.server_api import ServerAPI
from infrastructures.redis.base import redis_storage

logger: Logger = structlog.get_logger(__name__)


class FastAPIApp(FastAPI):
    @staticmethod
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.http_client = httpx.AsyncClient(
            base_url=f"{settings.server_site_url}/api/v1",
            timeout=httpx.Timeout(connect=3.0, read=10.0, write=10.0, pool=5.0),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
        )
        app.state.server = ServerAPI(http=app.state.http_client)

        # Redis
        await redis_storage.connect()

        app.state.bot_cache = {}

        try:
            yield
        finally:
            # закрываем ботов
            for bot in app.state.bot_cache.values():
                await bot.session.close()

            await app.state.http_client.aclose()
            await redis_storage.close()

    app = FastAPI(lifespan=lifespan)

    def create(
        self,
        title: str,
        description: str,
        custom_docs_url: str | None = None,
    ) -> FastAPI:
        return FastAPI(
            title=title,
            description=description,
            default_response_class=ORJSONResponse,
            lifespan=self.lifespan,
            docs_url=custom_docs_url if custom_docs_url else "/docs/",
            redoc_url=None,
            version="0.1.0",
            openapi_url="/rest/v1/openapi.json",
        )
