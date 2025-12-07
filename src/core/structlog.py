import json
import logging.config
import uuid
from typing import Any, TypeVar

import structlog
from structlog import configure_once
from structlog.stdlib import BoundLogger
from structlog.typing import EventDict

from core.config import settings

RendererType = TypeVar("RendererType")

Logger = BoundLogger


def get_level() -> str:
    return str(settings.logging.log_level)


def drop_color_message_key(_: Any, __: Any, event_dict: EventDict) -> EventDict:
    """Удаляем лишний цветной лог от Uvicorn"""
    event_dict.pop("color_message", None)
    return event_dict


def custom_json_renderer(event_dict: dict[str, str], **kwargs: Any) -> str:
    """Рендер JSON без Unicode escape (обрабатывает доп. аргументы)"""
    return json.dumps(event_dict, ensure_ascii=False, **kwargs)


class Logging[RendererType]:
    _structlog_configured = False
    timestamper = structlog.processors.TimeStamper(fmt="iso")
    shared_processors: list[Any] = [  # noqa: RUF012
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        drop_color_message_key,
        timestamper,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.StackInfoRenderer(),
    ]

    @classmethod
    def get_processors(cls) -> list[Any]:
        if not settings.debug:
            cls.shared_processors.append(structlog.processors.format_exc_info)

        return [
            *cls.shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ]

    @classmethod
    def get_renderer(cls) -> RendererType:
        raise NotImplementedError()

    @classmethod
    def configure_stdlib(cls) -> None:
        level = get_level()

        log_handlers = {
            "console": {
                "level": level,
                "class": "logging.StreamHandler",
                "formatter": "myLogger",
            },
        }

        if not settings.debug:
            log_handlers["file"] = {
                "level": level,
                "class": "logging.FileHandler",
                "filename": settings.logging.log_filename,
                "formatter": "myLogger",
                "encoding": "utf-8",
            }

        logging.config.dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": True,
                "formatters": {
                    "myLogger": {
                        "()": structlog.stdlib.ProcessorFormatter,
                        "processors": [
                            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                            cls.get_renderer(),
                        ],
                        "foreign_pre_chain": cls.shared_processors,
                    },
                },
                "handlers": log_handlers,
                "loggers": {
                    "": {
                        "handlers": list(log_handlers.keys()),
                        "level": level,
                        "propagate": False,
                    },
                    **{
                        logger: {
                            "handlers": [],
                            "propagate": True,
                        }
                        for logger in ["uvicorn", "sqlalchemy", "arq"]
                    },
                },
            }
        )

    @classmethod
    def configure_structlog(cls) -> None:
        if cls._structlog_configured:
            return
        configure_once(
            processors=cls.get_processors(),
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=BoundLogger,
            cache_logger_on_first_use=True,
        )
        cls._structlog_configured = True

    @classmethod
    def configure(cls) -> None:
        cls.configure_stdlib()
        cls.configure_structlog()


class Development(Logging[structlog.dev.ConsoleRenderer]):
    @classmethod
    def get_renderer(cls) -> structlog.dev.ConsoleRenderer:
        return structlog.dev.ConsoleRenderer(colors=True)


class Production(Logging[structlog.processors.JSONRenderer]):
    @classmethod
    def get_renderer(cls) -> structlog.processors.JSONRenderer:
        return structlog.processors.JSONRenderer(serializer=custom_json_renderer)


def configure() -> None:
    if settings.debug:
        Development.configure()
    else:
        Production.configure()


def generate_correlation_id() -> str:
    return str(uuid.uuid4())
