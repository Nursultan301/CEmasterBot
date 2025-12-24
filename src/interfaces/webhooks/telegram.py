import logging
import uuid

from aiogram import Bot, types
from fastapi import APIRouter, Request, status

from dispatcher import dp
from infrastructures.http.client import OrganizationAPIClient
from schemas.base import SuccessResponse


router = APIRouter(
    tags=["Webhook Telegram"],
)


@router.post(
    "/{organization_id}/",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
)
async def telegram_webhook(
    organization_id: uuid.UUID,
    request: Request,
) -> SuccessResponse:
    try:
        http = OrganizationAPIClient()
        telegram_token = await http.get_token(organization_id=organization_id)

        bot = Bot(token=telegram_token)
        request_data = await request.json()
        await dp.feed_update(bot, types.Update(**request_data))

    except Exception as e:
        logging.error(e)
    return SuccessResponse(
        detail="Success send message!",
    )
