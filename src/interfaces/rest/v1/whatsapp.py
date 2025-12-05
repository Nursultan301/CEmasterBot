from typing import Annotated

from fastapi import APIRouter, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from domain.services.agent import AgentService
from enums.roles import UserRoleType
from infrastructure.database.config import db_helper
from interfaces.rest.dependencies.auth import UserDependence
from schemas.user import UserRead
from schemas.whatsapp import WhatsAppCreate, WhatsAppRead

router = APIRouter()


@router.get("/{agent_id}/whatsapp/", response_model=WhatsAppRead, deprecated=True)
async def get_whatsapp_service(
    agent_id: str,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    user: Annotated[
        UserRead,
        Security(
            UserDependence.get_user_from_access_token_with_scopes,
            scopes=[
                UserRoleType.ADMIN,
            ],
        ),
    ],
) -> WhatsAppRead:
    agent_service = AgentService(session)
    agent = await agent_service.get_whatsapp_service(
        id=agent_id,
        user_id=user.id,
    )
    return WhatsAppRead(**agent.model_dump())


@router.post(
    "/{agent_id}/whatsapp/",
    response_model=WhatsAppRead,
    status_code=status.HTTP_201_CREATED,
    deprecated=True,
)
async def create_whatsapp_service(
    agent_id: str,
    data: WhatsAppCreate,
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
) -> WhatsAppRead:
    agent_service = AgentService(session)
    agent = await agent_service.create_whatsapp_service(
        data=data,
        id=agent_id,
    )
    return WhatsAppRead(**agent.model_dump())
