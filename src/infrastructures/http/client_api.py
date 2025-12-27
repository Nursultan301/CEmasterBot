from __future__ import annotations

from typing import TypeVar

import httpx
import structlog

from core.structlog import Logger
from enums.commons import ClientCodeTypeEnum
from schemas.base import ResponsePayload, ErrorResponse
from schemas.client import ClientInfoSchema, ClientCreateSchema

logger: Logger = structlog.get_logger(__name__)

T = TypeVar("T")


class ClientAPI:
    http: httpx.AsyncClient

    def __init__(self, http: httpx.AsyncClient) -> None:
        self.http = http

    async def get_me(self, chat_id: int) -> ClientInfoSchema | None:
        try:
            response = await self.http.get(
                "/clients/me/",
                headers={"x-data-chat-id": str(chat_id)},
            )
            response.raise_for_status()
            payload = ResponsePayload[ClientInfoSchema](**response.json())
            return payload.result

        except httpx.HTTPStatusError as exc:
            errors = ErrorResponse(**exc.response.json())
            logger.error(
                "Client API request failed",
                status_code=exc.response.status_code,
                exception_type=errors.exception_type,
                errors=errors.errors,
            )

        except httpx.RequestError as exc:
            logger.warning("Client API is unavailable", error=str(exc))

    async def create(self, client_data: ClientCreateSchema) -> ClientInfoSchema | None:
        try:
            response = await self.http.post(
                "/clients/registration/",
                content=client_data.model_dump_json(),
            )
            response.raise_for_status()
            payload = ResponsePayload[ClientInfoSchema](**response.json())
            return payload.result

        except httpx.HTTPStatusError as exc:
            errors = ErrorResponse(**exc.response.json())
            logger.error(
                "Client API request failed",
                status_code=exc.response.status_code,
                exception_type=errors.exception_type,
                errors=errors.errors,
            )

        except httpx.RequestError as exc:
            logger.warning("Client API is unavailable", error=str(exc))

    async def generate_code(
        self,
        chat_id: int,
        type_client_code: ClientCodeTypeEnum,
    ) -> ClientInfoSchema | None:
        try:
            response = await self.http.post(
                "/clients/generate/client-code/",
                headers={"x-data-chat-id": str(chat_id)},
                json={
                    "type_client_code": type_client_code,
                },
            )
            response.raise_for_status()
            payload = ResponsePayload[ClientInfoSchema](**response.json())
            return payload.result
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Client API request failed",
                status_code=exc.response.status_code,
                errors=exc.response.json(),
            )
        except httpx.RequestError as exc:
            logger.warning("Client API is unavailable", error=str(exc))
