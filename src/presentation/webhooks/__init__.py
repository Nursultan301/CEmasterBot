from fastapi import APIRouter


from presentation.webhooks.telegram import router as telegram_router
from presentation.api_prefix import api_prefix

router = APIRouter(
    prefix=api_prefix.webhook.prefix,
)


router.include_router(
    telegram_router,
    prefix=api_prefix.webhook.telegram,
)
