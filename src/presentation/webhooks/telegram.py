import uuid

from aiogram import types
from aiogram.types import Update
from fastapi import APIRouter, Request, status

from infrastructures.aiogram import dispatcher
from infrastructures.cache.bot_cache import get_bot_cached
from infrastructures.cache.token_cache import get_token_cached
from infrastructures.http.server_api import ServerAPI
from schemas.base import SuccessResponse


router = APIRouter(
    tags=["Webhook Telegram"],
)


def extract_chat_id(update: Update) -> int | None:
    if update.message:
        return update.message.chat.id
    if update.callback_query and update.callback_query.message:
        return update.callback_query.message.chat.id
    return None


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
        server_api: ServerAPI = request.app.state.server

        token = await get_token_cached(server_api, organization_id)
        bot = get_bot_cached(request, organization_id, token)

        await dispatcher.feed_update(
            bot=bot,
            update=types.Update.model_validate(
                obj=await request.json(),
                context={"bot": bot},
            ),
            organization_id=organization_id,
            server_api=server_api,
        )

    except Exception as e:
        raise e

    return SuccessResponse(detail="OK")
