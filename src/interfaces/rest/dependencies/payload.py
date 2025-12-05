from typing import Annotated, Any

from fastapi import Depends, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from jwt import InvalidTokenError

from core.exceptions import ClientException
from interfaces.rest.dependencies.base import http_bearer
from schemas.auth import AccessPayload, RefreshPayload
from utils import decode_jwt


class ExtractPayload:
    async def refresh(self, request: Request) -> RefreshPayload:
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise ClientException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                error_code="invalid_token",
                detail="Refresh token has not been provided!",
            )
        jwt_payload = await self.extract_jwt_payload(refresh_token)
        payload: RefreshPayload = RefreshPayload(**jwt_payload)
        if payload.type != "refresh":
            raise ClientException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                error_code="invalid_token",
                detail="Invalid refresh token!",
            )
        return payload

    async def access(
        self,
        access_token: Annotated[
            HTTPAuthorizationCredentials,
            Depends(http_bearer),
        ],
    ) -> AccessPayload:
        try:
            jwt_payload = await self.extract_jwt_payload(access_token.credentials)
            payload = AccessPayload(**jwt_payload)
            if payload.type != "access":
                raise ClientException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    error_code="invalid_token",
                    detail="Invalid access token!",
                )
            return payload
        except AttributeError as err:
            raise ClientException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                error_code="invalid_token",
                detail="Authentication data has not been provided!",
            ) from err

    @staticmethod
    async def extract_jwt_payload(token: str) -> Any:
        """
        Извлекает и проверяет полезную нагрузку из JWT токена.
        Args:
            token: JWT токен для расшифровки
        Returns:
            dict[str, str]: Расшифрованная полезная нагрузка токена
        Raises:
            ClientException: Если токен недействителен или его невозможно расшифровать
        """
        try:
            payload = decode_jwt(token)
        except InvalidTokenError as err:
            raise ClientException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                error_code="invalid_token",
                detail="Невозможно расшифровать токен: "
                "токен недействителен или истек срок его действия",
            ) from err
        return payload


extract_payload = ExtractPayload()
