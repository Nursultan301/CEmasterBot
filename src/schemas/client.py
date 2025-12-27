from datetime import datetime

from pydantic import BaseModel

from enums.commons import ClientCodeTypeEnum


class ClientInfoSchema(BaseModel):
    id: int
    firstName: str
    lastName: str
    phone: str
    chatId: str
    code: str
    createdAt: datetime = None
    updatedAt: datetime = None


class ClientCreateSchema(BaseModel):
    firstName: str | None = None
    lastName: str | None = None
    phone: str
    chat_id: int


class ClientCodeGenerateSchema(BaseModel):
    type_client_code: ClientCodeTypeEnum
