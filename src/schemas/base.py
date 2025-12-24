from dataclasses import dataclass
from typing import Literal

from fastapi import Query
from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    detail: str


class ErrorResponse(BaseModel):
    exception_type: Literal[
        "server_error",
        "validation_error",
        "client_error",
    ]
    errors: list["ErrorDetail"]


class ErrorDetail(BaseModel):
    error_code: str | None = None
    detail: str | None = None
    attr: str | None = None


class BaseResponse(BaseModel):
    object: Literal[
        "list",
        "object",
    ]


class ResponsePayload[T](BaseResponse):
    object: Literal["object"] = "object"
    result: T


class ResponseListPayload[T](BaseResponse):
    object: Literal["list"] = "list"
    results: list[T]


@dataclass
class PaginatedParams:
    page: int = Query(
        default=1,
        ge=1,
        description="The page number",
    )
    per_page: int = Query(
        default=100,
        ge=10,
        le=200,
        description="The number of items per page",
    )


class PaginatedResponse[T](BaseModel):
    count: int = Field(
        description="Number of items returned in the response",
    )
    number_of_pages: int = Field(
        description="Number of pages in the response",
    )
    results: list[T] = Field(
        description="List of items returned in the response following given criteria"
    )
