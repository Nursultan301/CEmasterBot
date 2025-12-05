from collections.abc import Sequence
from typing import Any

from fastapi import Security

from interfaces.rest.dependencies.user import UserDependence


def permissions(scopes: Sequence[str]) -> Any:
    return Security(
        UserDependence.get_user_from_access_token_with_scopes,
        scopes=scopes,
    )


class PermissionDependence:
    def __init__(self, scopes: Sequence[str] | None) -> None:
        self.scopes = scopes

    async def __call__(self, *_: Any, **__: Any) -> Any:
        return Security(
            UserDependence.get_user_from_access_token_with_scopes,
            scopes=self.scopes,
        )
