from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: Path = Path(__file__).parent.parent.parent


LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
)


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class GunicornConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    timeout: int = 900


class LoggingConfig(BaseModel):
    log_level: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ] = "INFO"
    log_format: str = LOG_DEFAULT_FORMAT
    log_file: str = "app.log"


class RedisConfig(BaseModel):
    url: str | None = Field(default=None)
    host: str
    port: str
    prefix: str = "app"
    default_ttl_seconds: int = 3600
    decode_responses: bool = False

    @model_validator(mode="after")
    def set_url(self) -> "RedisConfig":
        self.url = f"redis://{self.host}:{self.port}"
        return self


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(f"{BASE_DIR / '.env.template'}", f"{BASE_DIR / '.env'}"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    debug: bool
    allow_origins: list[str]
    current_site_url: str
    server_site_url: str
    redis: RedisConfig

    admin_ids: frozenset[int] = frozenset({42, 3595399})
    run: RunConfig = RunConfig()
    gunicorn: GunicornConfig = GunicornConfig()
    logging: LoggingConfig = LoggingConfig()


# noinspection PyArgumentList
settings = Settings()
