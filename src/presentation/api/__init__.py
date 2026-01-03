__all__ = ["router"]

from fastapi import APIRouter

from presentation.api_prefix import api_prefix
from presentation.api.telegram import router as telegram_router

router = APIRouter(prefix=api_prefix.prefix)

router.include_router(router=telegram_router)
