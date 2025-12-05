from fastapi import APIRouter

from core.config import settings

from .telegram import router as telegram_router

router = APIRouter(
    prefix=settings.webhook.prefix,
)


router.include_router(
    telegram_router,
    prefix=settings.webhook.telegram,
)
