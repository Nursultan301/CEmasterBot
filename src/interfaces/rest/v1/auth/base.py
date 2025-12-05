from typing import Annotated

import structlog
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Response,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.structlog import Logger
from domain.services.auth import AuthJWTService
from domain.services.user import UserService
from domain.services.user_activate_code import UserActivateCodeService
from enums import TypeActivateCode
from infrastructure.database.config import db_helper
from interfaces.rest.dependencies.user import UserDependence
from interfaces.rest.dependencies.user_activate_code import UserActivateCodeDependence
from schemas.auth import TokenInfo
from schemas.base import SuccessResponse
from schemas.user import UserCreate, UserRead
from schemas.user_activate_code import UserActivateCodeRead

router = APIRouter()

logger: Logger = structlog.getLogger(__name__)


@router.post("/login/", response_model=TokenInfo)
async def login(
    response: Response,
    user: Annotated[
        UserRead,
        Depends(UserDependence.login),
    ],
) -> TokenInfo:
    auth_jwt = AuthJWTService(user)
    access_token = await auth_jwt.create_access_token()
    refresh_token = await auth_jwt.create_refresh_token()
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.jwt.refresh_token_expire_minutes,
        httponly=True,
        secure=settings.jwt.refresh_token_secure,
        domain=settings.domain,
        path="/",
    )
    return TokenInfo(
        access_token=access_token,
    )


@router.post("/logout/", response_model=SuccessResponse)
async def logout(response: Response) -> SuccessResponse:
    response.delete_cookie(
        key="refresh_token",
        secure=settings.jwt.refresh_token_secure,
        httponly=True,
        domain=settings.domain,
        path="/",
    )
    return SuccessResponse(
        detail="The user has been successfully logged out!",
    )


@router.post(
    "/refresh/",
    response_model=TokenInfo,
    response_model_exclude_none=True,
)
async def get_access_token_from_refresh_token(
    user: Annotated[
        UserRead,
        Depends(UserDependence.get_user_on_refresh_token),
    ],
) -> TokenInfo:
    auth_jwt = AuthJWTService(user)
    access_token = await auth_jwt.create_access_token()
    return TokenInfo(
        access_token=access_token,
    )


@router.post(
    "/registration/",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
)
async def registration(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
) -> SuccessResponse:
    service = UserService(session)
    user = await service.registration(
        user_data=user_data,
    )
    active_code_service = UserActivateCodeService(session)
    await active_code_service.create(
        email=user.email,
        type_code=TypeActivateCode.REGISTRATION,
        background_tasks=background_tasks,
    )
    logger.info("Success registration", **user.model_dump())
    return SuccessResponse(
        detail="Success registration!",
    )


@router.post("/reset-password/", status_code=status.HTTP_200_OK)
async def reset_password(
    _: Annotated[
        UserActivateCodeRead,
        Depends(UserDependence.reset_password),
    ],
) -> SuccessResponse:
    return SuccessResponse(
        detail="Success send reset password code!",
    )


@router.post("/send-activate-code/", status_code=status.HTTP_201_CREATED)
async def send_activate_code(
    _: Annotated[
        UserActivateCodeRead,
        Depends(UserActivateCodeDependence.create),
    ],
) -> SuccessResponse:
    return SuccessResponse(
        detail="Success send active code!",
    )


@router.post("/check-activate-code/", status_code=status.HTTP_200_OK)
async def check_activate_code(
    active_code: Annotated[
        UserActivateCodeRead,
        Depends(UserActivateCodeDependence.check),
    ],
) -> UserActivateCodeRead:
    return active_code


@router.post("/activate-user/", response_model=SuccessResponse)
async def user_activate(
    _: Annotated[
        UserRead,
        Depends(UserDependence.activate_user),
    ],
) -> SuccessResponse:
    return SuccessResponse(
        detail="The user has been successfully activated!",
    )
