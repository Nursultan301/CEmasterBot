from typing import Annotated

from fastapi import APIRouter, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession

from domain.services.agent import AgentService
from enums.roles import UserRoleType
from infrastructure.database.config import db_helper
from interfaces.rest.dependencies.user import UserDependence
from schemas.agent import AgentRead
from schemas.user import UserRead

router = APIRouter()


@router.get("/{agent_id}/", response_model=AgentRead)
async def get_agent(
    agent_id: str,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    _: Annotated[
        UserRead,
        Security(
            UserDependence.get_user_from_access_token_with_scopes,
            scopes=[
                UserRoleType.ADMIN,
            ],
        ),
    ],
) -> AgentRead:
    service = AgentService(session)
    return await service.get_agent_and_channels(id=agent_id)
