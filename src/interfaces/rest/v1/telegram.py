from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from domain.services.agent import AgentService
from infrastructure.database.config import db_helper
from schemas.telegram import TelegramCreate, TelegramRead

router = APIRouter()


@router.get("/{agent_id}/telegram/", response_model=TelegramRead)
async def get_telegram_service(
    agent_id: str,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
) -> TelegramRead:
    service = AgentService(session)
    return await service.get_telegram_service(
        id=agent_id,
    )


@router.post("/{agent_id}/telegram/", status_code=status.HTTP_201_CREATED)
async def create_telegram_service(
    agent_id: str,
    data: TelegramCreate,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
) -> TelegramRead:
    service = AgentService(session)
    return await service.create_telegram_service(
        data=data,
        id=agent_id,
    )
