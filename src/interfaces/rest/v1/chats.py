from collections.abc import Sequence
from typing import Annotated

import structlog
from fastapi import APIRouter
from fastapi.params import Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.structlog import Logger
from domain.services.room import RoomService
from enums import RoomType
from infrastructure.database.config import db_helper
from interfaces.rest.dependencies.agents import get_header_agent_id
from schemas.room import RoomOutDB

router = APIRouter()

logger: Logger = structlog.getLogger(__name__)


class ChatScheme(BaseModel):
    pass


def get_channels_dep(
    channels: Annotated[list[RoomType] | None, Query()] = None,
) -> list[RoomType]:
    if not channels:
        return [
            RoomType.Telegram,
            RoomType.WhatsApp,
            RoomType.SWLiveChat,
        ]
    return channels


@router.get("/", response_model=Sequence[ChatScheme])
async def get_agents_chats(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    agent_id: Annotated[str, Depends(get_header_agent_id)],
    channels: Annotated[list[RoomType], Depends(get_channels_dep)],
) -> Sequence[RoomOutDB]:
    room_service = RoomService(session=session)
    logger.info("Get agents chats", agent_id=agent_id, channels=channels)
    return await room_service.filter_by()
