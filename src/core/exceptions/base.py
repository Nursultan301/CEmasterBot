from typing import Any

from fastapi import HTTPException, status
from pydantic import BaseModel


# Общая модель ошибки
class ErrorDetail(BaseModel):
    error_code: str | None = None
    detail: str | None = None
    attr: str | None = None


# Базовый класс для пользовательских исключений
class BaseCustomException(HTTPException):
    def __init__(
        self,
        error_code: str | None = None,
        detail: str | None = None,
        attr: str | None = None,
        errors: list[ErrorDetail] | None = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        **kwargs: Any,
    ) -> None:
        exception_type_default: str = "custom_error"
        self.exception_type = kwargs.pop("exception_type", exception_type_default)
        if not errors:
            self.errors = [
                ErrorDetail(
                    error_code=error_code,
                    detail=detail,
                    attr=attr,
                ),
            ]
        super().__init__(status_code=status_code, **kwargs)


# Специфические исключения
class ClientException(BaseCustomException):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            exception_type="client_error",
            **kwargs,
        )


class ValidationException(BaseCustomException):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            exception_type="validation_error",
            **kwargs,
        )


class ServerException(BaseCustomException):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            exception_type="server_error",
            **kwargs,
        )
