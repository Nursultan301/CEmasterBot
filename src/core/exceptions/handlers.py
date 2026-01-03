from typing import TYPE_CHECKING, Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from gunicorn.glogging import Logger
from starlette.responses import JSONResponse
import structlog

from core.exceptions import (
    ClientException,
    ErrorDetail,
    ServerException,
    ValidationException,
)

if TYPE_CHECKING:
    from collections.abc import Callable

logger: Logger = structlog.get_logger("uvicorn.error")


def handle_request_validation_error(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "exception_type": "validation_error",
            "errors": [
                ErrorDetail(
                    error_code=error.get("enums"),
                    detail=error.get("msg"),
                    attr=error.get("loc")[-1],
                ).model_dump()
                for error in exc.errors()
            ],
        },
    )


def extractor(
    exc: ServerException | ValidationException | ClientException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "exception_type": exc.exception_type,
            "errors": [
                ErrorDetail(
                    error_code=error.error_code,
                    detail=error.detail,
                    attr=error.attr,
                ).model_dump()
                for error in exc.errors
            ],
        },
    )


def handle_client_exception(
    _request: Request,
    exc: ClientException,
) -> JSONResponse:
    return extractor(exc)


def handle_validation_exception(
    _request: Request,
    exc: ValidationException,
) -> JSONResponse:
    return extractor(exc)


def handle_server_exception(
    _request: Request,
    exc: ServerException,
) -> JSONResponse:
    return extractor(exc)


# <<<<<< Новый обработчик для неожиданных ошибок >>>>>>
def handle_unexpected_exception(
    _request: Request,
    _exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "exception_type": "internal_server_error",
            "errors": [
                ErrorDetail(
                    error_code="internal_error",
                    detail="An unexpected error occurred.",
                    attr=None,
                ).model_dump()
            ],
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    exception_handlers: dict[
        type[Exception], Callable[[Request, Any], JSONResponse]
    ] = {
        RequestValidationError: handle_request_validation_error,
        ClientException: handle_client_exception,
        ServerException: handle_server_exception,
        ValidationException: handle_validation_exception,
        Exception: handle_unexpected_exception,  # <<< добавляем общий хендлер
    }

    for exc, handler in exception_handlers.items():
        app.add_exception_handler(exc, handler)
