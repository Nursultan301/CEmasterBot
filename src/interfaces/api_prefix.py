from pydantic import BaseModel


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    telegram: str = "/telegram"


class WebhookPrefix(BaseModel):
    prefix: str = "/webhook"
    telegram: str = "/telegram"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()
    webhook: WebhookPrefix = WebhookPrefix()


api_prefix: ApiPrefix = ApiPrefix()
