from typing import TYPE_CHECKING, Annotated

import structlog
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse

from core.config import settings
from core.structlog import Logger
from domain.services.auth import AuthJWTService
from domain.services.user import UserService
from enums import AuthProviderType
from infrastructure.database.config import db_helper
from infrastructure.integrations.authlib import oauth
from schemas.auth import OAuthProvider
from schemas.user import OAuth2UserCreate, UserOutDB, UserRead

if TYPE_CHECKING:
    from authlib.integrations.starlette_client.apps import StarletteAppMixin

router = APIRouter()


logger: Logger = structlog.getLogger(__name__)


@router.get("/providers/", response_model=list[OAuthProvider])
def providers() -> list[OAuthProvider]:
    return [
        OAuthProvider(
            name=AuthProviderType.google,
            connect_uri=f"/api/v1/oauth2/connect/{AuthProviderType.google}/",
            display_name=AuthProviderType.google.value.title(),
        ),
        OAuthProvider(
            name=AuthProviderType.facebook,
            connect_uri=f"/api/v1/oauth2/connect/{AuthProviderType.facebook}/",
            display_name=AuthProviderType.facebook.value.title(),
        ),
    ]


@router.get("/connect/{provider}/")
async def provider_connect(
    provider: AuthProviderType, request: Request
) -> RedirectResponse:
    redirect_url = f"{settings.back_end_url}/api/v1/oauth2/{provider}/callback/"
    logger.info(
        "Redirecting user to provider login",
        provider_name=provider,
        redirect_url=redirect_url,
    )
    provider_oauth: StarletteAppMixin = oauth.create_client(provider)
    response: RedirectResponse = await provider_oauth.authorize_redirect(
        request, redirect_url
    )
    return response


@router.get("/{provider}/callback/", include_in_schema=False)
async def provider_callback_handler(
    provider: AuthProviderType,
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
) -> RedirectResponse:
    logger.info("Authorization callback received")
    response_failure = RedirectResponse(
        url=f"{settings.front_end_url}/login?error="
        f"Не удалось авторизоваться через {provider.value.title()}. "
        f"Пожалуйста, попробуйте снова или выберите другой способ входа."
    )
    try:
        user_data = await get_user_data_from_provider(
            provider=provider,
            request=request,
        )
        if not user_data:
            return response_failure
        user = await get_or_create_user(
            session=session,
            user_data=user_data,
        )
        if user.provider != provider:
            return RedirectResponse(
                url=f"{settings.front_end_url}/login?error="
                f"Аккаунт был зарегистрирован через другим способом"
            )
        user_read = UserRead(**user.model_dump())
        auth_service = AuthJWTService(user_read)
        response = RedirectResponse(
            url=f"{settings.front_end_url}/dashboard?oauth_provider={provider}",
        )
        response.set_cookie(
            key="refresh_token",
            value=await auth_service.create_refresh_token(),
            max_age=settings.jwt.refresh_token_expire_minutes,
            httponly=True,
            secure=settings.jwt.refresh_token_secure,
            domain=settings.domain,
            path="/",
        )
        return response
    except Exception as e:
        logger.error("Failed to get token or user info", error=str(e))
        return response_failure


async def get_user_data_from_provider(
    provider: AuthProviderType, request: Request
) -> OAuth2UserCreate | None:
    provider_oauth = oauth.create_client(provider)
    access_token = await provider_oauth.authorize_access_token(request)
    user_data = None
    if provider == AuthProviderType.google:
        user_info = access_token.get("userinfo")
        user_data = OAuth2UserCreate(
            email=user_info.get("email"),
            first_name=user_info.get("given_name"),
            last_name=user_info.get("family_name"),
            sub=user_info.get("sub"),
            provider=AuthProviderType.google,
            organization_name=user_info.get("name"),
            password=user_info.get("sub"),
        )
    elif provider == AuthProviderType.facebook:
        resp = await provider_oauth.get(
            "me",
            params={"fields": "id,email,first_name,last_name,name"},
            token=access_token,
        )
        resp.raise_for_status()
        user_info = resp.json()
        user_data = OAuth2UserCreate(
            email=user_info.get("email"),
            first_name=user_info.get("first_name"),
            last_name=user_info.get("last_name"),
            sub=user_info.get("id"),
            provider=AuthProviderType.facebook,
            organization_name=user_info.get("name"),
            password=user_info.get("id"),
        )
    logger.info(
        "Получены данные от OAuth провайдера",
        provider=provider,
    )
    return user_data


async def get_or_create_user(
    session: AsyncSession,
    user_data: OAuth2UserCreate,
) -> UserOutDB:
    service = UserService(session)
    try:
        user = await service.get_by(email=user_data.email)
    except Exception:
        user = await service.registration(user_data=user_data)
    return user
