from fastapi import APIRouter, Depends

from interfaces.rest.dependencies.base import http_bearer

from interfaces.rest.v1.telegram import router as telegram_router
from interfaces.api_prefix import api_prefix

router = APIRouter(
    prefix=api_prefix.v1.prefix,
    dependencies=[
        Depends(http_bearer),
    ],
)

router.include_router(
    router=telegram_router,
    prefix=api_prefix.v1.telegram,
    tags=["Telegram"],
)

__all__ = ["router"]
