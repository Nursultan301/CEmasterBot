from typing import Annotated

from fastapi import BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from domain.services.user_activate_code import UserActivateCodeService
from infrastructure.database.config import db_helper
from schemas.user_activate_code import (
    UserActivateCodeCheck,
    UserActivateCodeCreate,
    UserActivateCodeRead,
)


class UserActivateCodeDependence:
    @staticmethod
    async def create(
        data: UserActivateCodeCreate,
        background_tasks: BackgroundTasks,
        session: Annotated[
            AsyncSession,
            Depends(db_helper.session_getter),
        ],
    ) -> UserActivateCodeRead:
        activate_code_service = UserActivateCodeService(session)
        activate_code: UserActivateCodeRead = await activate_code_service.create(
            email=data.email,
            type_code=data.type_code,
            background_tasks=background_tasks,
        )
        return activate_code

    @staticmethod
    async def check(
        data: UserActivateCodeCheck,
        session: Annotated[
            AsyncSession,
            Depends(db_helper.session_getter),
        ],
    ) -> UserActivateCodeRead:
        active_code_service = UserActivateCodeService(session)
        active_code: UserActivateCodeRead = await active_code_service.get_by_code(
            email=data.email,
            type_code=data.type_code,
            code=data.code,
        )
        return active_code
