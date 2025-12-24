from aiogram import Bot
from fastapi import APIRouter, status

from core.config import settings
from core.exceptions import ClientException, ServerException
from interfaces.api_prefix import api_prefix
from schemas.base import SuccessResponse

from schemas.telegram import TelegramSchema

router = APIRouter()


@router.post(
    "/set_webhook/",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
)
async def get_telegram_service(data: TelegramSchema) -> SuccessResponse:
    url = f"{settings.current_site_url}{api_prefix.webhook.prefix}{api_prefix.webhook.telegram}/{data.organization_id}/"
    try:
        bot = Bot(token=data.token)
        response = await bot.set_webhook(url=url)
        if response:
            return SuccessResponse(
                detail=f"Telegram service has been successfully set up!",
            )
        else:
            raise ClientException(detail="Telegram service has not been set up!")

    except Exception as e:
        raise ServerException(detail=str(e))
