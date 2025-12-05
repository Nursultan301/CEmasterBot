from typing import Annotated

from fastapi import Depends, status
from fastapi.security import SecurityScopes
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import ClientException, ValidationException
from domain.services.user import UserService
from domain.services.user_activate_code import UserActivateCodeService
from enums.constants import TypeActivateCode
from infrastructure.database.config import db_helper
from infrastructure.repositories_impl.user import UserRepository
from interfaces.rest.dependencies.payload import extract_payload
from schemas.auth import AccessPayload, AuthLogin, RefreshPayload
from schemas.user import (
    UserActivate,
    UserRead,
    UserResetPassword,
)
from schemas.user_activate_code import UserActivateCodeRead
from utils import validate_password


class UserDependence:
    @staticmethod
    async def login(
        auth_data: AuthLogin,
        session: Annotated[
            AsyncSession,
            Depends(db_helper.session_getter),
        ],
    ) -> UserRead:
        repo = UserRepository(session)
        user = await repo.find_one_by(email=auth_data.email)
        validate_error = ValidationException(detail="Wrong email or password!")
        if not user:
            raise validate_error
        if not validate_password(auth_data.password, str(user.password)):
            raise validate_error
        if not user.is_active:
            raise ClientException(
                error_code="value_error",
                detail="User is not activated!",
            )
        return UserRead.model_validate(user)

    @staticmethod
    async def get_user_on_refresh_token(
        payload: Annotated[
            RefreshPayload,
            Depends(extract_payload.refresh),
        ],
        session: Annotated[
            AsyncSession,
            Depends(db_helper.session_getter),
        ],
    ) -> UserRead:
        repo = UserRepository(session)
        user = await repo.find_one_by(email=payload.sub)
        if not user:
            raise ValidationException(
                error_code="value_error",
                detail="The user with this email was not found!",
                attr="email",
            )
        return UserRead.model_validate(user)

    @staticmethod
    async def get_user_from_access_token(
        payload: Annotated[
            AccessPayload,
            Depends(extract_payload.access),
        ],
        session: Annotated[
            AsyncSession,
            Depends(db_helper.session_getter),
        ],
    ) -> UserRead:
        repo = UserRepository(session)
        user = await repo.find_one_by(email=payload.email)
        if not user:
            raise ValidationException(
                error_code="value_error",
                detail="The user with this email was not found!",
                attr="email",
            )
        return UserRead.model_validate(user)

    @staticmethod
    async def get_user_from_access_token_with_scopes(
        security_scopes: SecurityScopes,
        payload: Annotated[
            AccessPayload,
            Depends(extract_payload.access),
        ],
        session: Annotated[
            AsyncSession,
            Depends(db_helper.session_getter),
        ],
    ) -> UserRead:
        if payload.role not in security_scopes.scopes:
            raise ClientException(
                status_code=status.HTTP_403_FORBIDDEN,
                error_code="not_permissions",
                detail=f"Not enough permissions. Missing scope: {payload.role}",
            )
        repo = UserRepository(session)
        user = await repo.find_one_by(email=payload.email)
        if not user:
            raise ValidationException(
                error_code="value_error",
                detail="The user with this email was not found!",
                attr="email",
            )
        return UserRead.model_validate(user)

    @staticmethod
    async def reset_password(
        data: UserResetPassword,
        session: Annotated[
            AsyncSession,
            Depends(db_helper.session_getter),
        ],
    ) -> UserActivateCodeRead:
        user_service = UserService(session)
        return await user_service.reset_password(
            email=data.email,
            type_code=TypeActivateCode.RESET_PASSWD,
            code=data.code,
            password=data.password,
        )

    @staticmethod
    async def activate_user(
        data: UserActivate,
        session: Annotated[
            AsyncSession,
            Depends(db_helper.session_getter),
        ],
    ) -> UserRead:
        activate_code_service = UserActivateCodeService(session)
        await activate_code_service.get_by_code(
            email=data.email,
            type_code=TypeActivateCode.REGISTRATION,
            code=data.code,
        )
        user_repo = UserRepository(session)
        user = await user_repo.update_partial_by_filter(
            update_data={
                "is_active": True,
            },
            email=data.email,
        )
        if not user:
            raise ValidationException(
                error_code="value_error",
                detail="The user with this email was not found!",
                attr="email",
            )
        await activate_code_service.set_is_verify(
            email=data.email,
            type_code=TypeActivateCode.REGISTRATION,
            code=data.code,
        )
        return UserRead.model_validate(user)
