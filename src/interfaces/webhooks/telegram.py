import logging

from aiogram import Bot, types
from fastapi import APIRouter, Request, status

from app import dispatcher
from schemas.base import SuccessResponse

router = APIRouter(
    tags=["Webhook Telegram"],
)

api_service = {
    "uuid": "9ye78r7845y784475",
    "name": "CEmasterBot",
    "token": "7787122283:AAHILH2FDJiJROBNURkXIphhI_qDEcc7jcc",
}


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
        await dispatcher.feed_update(bot, types.Update(**request_data))

    except Exception as e:
        logging.error(e)
    return SuccessResponse(
        detail="Success send message!",
    )
