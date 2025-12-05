from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from domain.services.agent import AgentService
from infrastructure.database.config import db_helper
from schemas.sw_live_chat import SWLiveChatCreate, SWLiveChatRead

router = APIRouter()


@router.get("/{agent_id}/sw_live_chat/", response_model=SWLiveChatRead)
async def get_sw_live_chat_service(
    agent_id: str,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
) -> SWLiveChatRead:
    service = AgentService(session)
    sw_live_chat = await service.get_sw_live_chat_service(
        id=agent_id,
    )
    return SWLiveChatRead(**sw_live_chat.model_dump())


@router.post("/{agent_id}/sw_live_chat/", status_code=status.HTTP_201_CREATED)
async def create_telegram_service(
    agent_id: str,
    data: SWLiveChatCreate,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
) -> SWLiveChatRead:
    service = AgentService(session)
    sw_live_chat = await service.create_sw_live_chat_service(
        data=data,
        id=agent_id,
    )
    return SWLiveChatRead(**sw_live_chat.model_dump())
