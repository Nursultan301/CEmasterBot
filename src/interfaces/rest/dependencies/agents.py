from typing import Annotated

from fastapi import Header

from core.exceptions import ValidationException


def get_header_agent_id(
    agent_id: Annotated[str | None, Header(alias="XSai-Agent-Id")] = None,
) -> str:
    if not agent_id:
        raise ValidationException(
            error_code="value_error",
            detail="The agent id field was not passed!",
        )
    return agent_id
