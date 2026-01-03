from starlette.types import ASGIApp, Receive, Scope, Send
import structlog

from core.structlog import generate_correlation_id


class LogCorrelationIdMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        structlog.contextvars.bind_contextvars(
            correlation_id=generate_correlation_id(),
        )

        await self.app(scope, receive, send)

        structlog.contextvars.unbind_contextvars(
            "correlation_id",
        )
        return None
