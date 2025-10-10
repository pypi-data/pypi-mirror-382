from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Dict

if TYPE_CHECKING:
    from ragger_sdk.client import RaggerClient

from ragger_sdk.constants import ErrorCodes
from ragger_sdk.exceptions import RaggerAPIError


class StatusMixin:
    def __init__(
        self,
        client: "RaggerClient",
    ) -> None:
        # Store the client reference for making API requests
        # This client handles authentication, URL building, and HTTP communication
        self._client = client

    def status(self, task_id: str, organization: str) -> Dict[str, Any]:
        if not task_id or not task_id.strip():
            raise RaggerAPIError(
                "task_id cannot be empty",
                ErrorCodes.MISSING_REQUIRED_PARAMETERS,
            )

        response = self._client.get(
            endpoint="/task-status/",
            params={
                "task_id": task_id.strip(),
                "organization": organization.strip(),
            },
        )

        return response
