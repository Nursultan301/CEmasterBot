__all__ = ["router"]

from fastapi import APIRouter

from presentation.api.telegram import router as telegram_router
from presentation.api_prefix import api_prefix

router = APIRouter(prefix=api_prefix.prefix)

router.include_router(router=telegram_router)
