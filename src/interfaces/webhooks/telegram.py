import logging
import uuid

from aiogram import Bot, types
from aiogram.types import Update
from fastapi import APIRouter, Request, status

from dispatcher import dp
from infrastructures.cache.bot_cache import get_bot_cached
from infrastructures.cache.token_cache import get_token_cached
from infrastructures.http.client_api import ClientAPI
from infrastructures.http.exceptions import ClientNotFoundException
from infrastructures.http.organization_api import OrganizationAPI
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

        token = await get_token_cached(request, organization_id)
        bot = get_bot_cached(request, organization_id, token)
        request_data = await request.json()
        update = types.Update.model_validate(request_data, context={"bot": bot})
        try:
            client = await server_api.client.get_me(
                chat_id=extract_chat_id(
                    update=update,
                ),
            )
        except ClientNotFoundException:
            client = None

        await dp.feed_update(
            bot=bot,
            update=update,
            organization_id=organization_id,
            client=client,
            server_api=server_api,
        )

    except Exception as e:
        raise e

    return SuccessResponse(detail="OK")
