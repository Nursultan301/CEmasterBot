from fastapi import APIRouter


from interfaces.webhooks.telegram import router as telegram_router
from interfaces.api_prefix import api_prefix

router = APIRouter(
    prefix=api_prefix.webhook.prefix,
)


router.include_router(
    telegram_router,
    prefix=api_prefix.webhook.telegram,
)
