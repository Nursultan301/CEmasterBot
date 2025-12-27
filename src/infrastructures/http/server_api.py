from dataclasses import dataclass
from typing import final

import httpx

from infrastructures.http.organization_api import OrganizationAPI


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class ServerAPI:
    http: httpx.AsyncClient

    @property
    def organization(self) -> OrganizationAPI:
        return OrganizationAPI(http=self.http)
