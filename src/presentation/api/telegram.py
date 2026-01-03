from aiogram import Bot
from fastapi import APIRouter, status
import structlog

from core.config import settings
from core.exceptions import ClientException
from core.structlog import Logger
from infrastructures.aiogram import dispatcher
from presentation.api_prefix import api_prefix
from schemas.base import SuccessResponse
from schemas.telegram import TelegramSchema

router = APIRouter(
    prefix=api_prefix.v1.telegram,
    tags=["Telegram"],
)


logger: Logger = structlog.get_logger(__name__)


@router.post(
    "/set_webhook/",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
)
async def get_telegram_service(data: TelegramSchema) -> SuccessResponse:
    url = (
        f"{settings.current_site_url}{api_prefix.webhook.prefix}"
        f"{api_prefix.webhook.telegram}/{data.organization_id}/"
    )
    logger.info("Setting up Telegram service...", url=url)
    try:
        bot = Bot(token=data.token)
        response = await bot.set_webhook(
            url=url,
            allowed_updates=dispatcher.resolve_used_update_types(),
        )
        if response:
            return SuccessResponse(
                detail="Telegram service has been successfully set up!",
            )
        logger.error("Telegram service has not been set up!", tg_response=response)
        raise ClientException(detail="Telegram service has not been set up!")

    except Exception as e:
        logger.exception("Telegram service has not been set up")
        raise ClientException(
            detail="Telegram service has not been set up!",
        ) from e
