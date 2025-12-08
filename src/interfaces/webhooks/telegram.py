import logging

from aiogram import Bot, types
from fastapi import APIRouter, Request, status

from dispatcher import dp
from schemas.base import SuccessResponse

from interfaces.tmp_data import api_service


router = APIRouter(
    tags=["Webhook Telegram"],
)


@router.post(
    "/{telegram_id}/",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
)
async def telegram_webhook(
    telegram_id: str,
    request: Request,
) -> SuccessResponse:
    try:
        bot = Bot(token=api_service.get("token"))
        request_data = await request.json()
        await dp.feed_update(bot, types.Update(**request_data))

    except Exception as e:
        logging.error(e)
    return SuccessResponse(
        detail="Success send message!",
    )
