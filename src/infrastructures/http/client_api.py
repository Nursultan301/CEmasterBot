from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final, final, TypeVar, Generic

import httpx
import structlog

from core.config import settings
from core.structlog import Logger
from infrastructures.http.exceptions import ClientNotFoundException
from schemas.base import ResponsePayload
from schemas.client import ClientInfoSchema, ClientCreateSchema

logger: Logger = structlog.get_logger(__name__)

T = TypeVar("T")


class ClientAPI:
    http: httpx.AsyncClient

    def __init__(self, http: httpx.AsyncClient) -> None:
        self.http = http

    async def get_me(self, chat_id: int) -> ClientInfoSchema:
        try:
            response = await self.http.get(
                "/clients/me/",
                headers={"x-data-chat-id": str(chat_id)},
            )
            response.raise_for_status()
            payload = ResponsePayload[ClientInfoSchema](**response.json())
            return payload.result

        except httpx.HTTPStatusError as exc:
            logger.warning(
                "Client API request failed",
                status_code=exc.response.status_code,
                response_text=exc.response.text[:500],
            )
            raise ClientNotFoundException(
                f"Client API error: HTTP {exc.response.status_code}"
            ) from exc

        except httpx.RequestError as exc:
            logger.warning("Client API is unavailable", error=str(exc))
            raise RuntimeError("Client API is unavailable") from exc

    async def create(self, client_data: ClientCreateSchema) -> ClientInfoSchema:
        try:
            response = await self.http.post(
                "/clients/registration/",
                json=client_data.model_dump(),
            )
            response.raise_for_status()
            payload = ResponsePayload[ClientInfoSchema](**response.json())
            return payload.result

        except httpx.HTTPStatusError as exc:
            logger.warning(
                "Client API request failed",
                status_code=exc.response.status_code,
                response_text=exc.response.text[:500],
            )
            raise ClientNotFoundException(
                f"Client API error: HTTP {exc.response.status_code}"
            ) from exc

        except httpx.RequestError as exc:
            logger.warning("Client API is unavailable", error=str(exc))
            raise RuntimeError("Client API is unavailable") from exc
