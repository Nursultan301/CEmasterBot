from typing import Annotated

import structlog
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
)
from sqlalchemy.ext.asyncio import AsyncSession

from core.s3_storage import storage
from core.structlog import Logger
from domain.services.user import UserService
from infrastructure.database.config import db_helper
from interfaces.rest.dependencies.files import image_file_dep
from interfaces.rest.dependencies.user import UserDependence
from schemas.base import DataDetailResponse
from schemas.user import UserPhotoUrl, UserProfile, UserRead, UserUpdate

router = APIRouter()

logger: Logger = structlog.getLogger(__name__)


@router.get("/me/", response_model=DataDetailResponse[UserProfile])
async def get_me_user(
    user: Annotated[
        UserRead,
        Depends(UserDependence.get_user_from_access_token),
    ],
    session: Annotated[
        AsyncSession,
        Depends(
            db_helper.session_getter,
        ),
    ],
) -> DataDetailResponse[UserProfile]:
    user_service = UserService(session=session)
    user_profile = await user_service.get_profile(email=user.email)
    return DataDetailResponse(
        object="me",
        data=user_profile,
    )


@router.put("/me/photo", response_model=UserPhotoUrl)
async def user_photo_update(
    uploaded_file: Annotated[
        UploadFile,
        Depends(image_file_dep),
    ],
    user: Annotated[
        UserRead,
        Depends(UserDependence.get_user_from_access_token),
    ],
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
) -> UserPhotoUrl:
    unique_filename = f"{user.id}_{uploaded_file.filename}"
    url = await storage.upload_file(
        file_name=unique_filename,
        file_obj=uploaded_file.file,
    )
    logger.info(
        "User photo uploaded",
        user_id=user.id,
        filename=unique_filename,
    )
    service = UserService(session)
    await service.update_partial_by_filter(
        update_data={"photo_url": url},
        id=user.id,
    )
    return UserPhotoUrl(
        photo_url=url,
    )


@router.patch("/me/", response_model=UserRead)
async def update_me_user(
    update_data: UserUpdate,
    user: Annotated[
        UserRead,
        Depends(UserDependence.get_user_from_access_token),
    ],
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
) -> UserRead:
    logger.info("User self-update", user_id=user.id, update=update_data)
    service = UserService(session)
    updated_user_data = await service.update_partial_by_filter(
        update_data=update_data.model_dump(exclude_unset=True),
        id=user.id,
    )
    return UserRead(**updated_user_data.model_dump())
