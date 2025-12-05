from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from core.structlog import Logger

logger: Logger = structlog.get_logger(__name__)


class FastAPIApp(FastAPI):
    @staticmethod
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncGenerator[None, Any]:
        yield

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
