from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from typing import Any
from typing import Dict
from typing import Optional

if TYPE_CHECKING:
    from ragger_sdk.client import RaggerClient

from ..constants import ProjectConstants
from ..exceptions import RaggerAPIError

logger = logging.getLogger(__name__)


class QueryAPI:
    def __init__(
        self,
        client: "RaggerClient",
    ) -> None:

        # Store the client reference for making authenticated API requests
        self.client = client
        # Define the endpoint for all query operations
        self.endpoint = "/query/"

    def ask(
        self,
        query: str,
        organization: str,
        project: str,
        user: str,
        session_id: Optional[str] = None,
        is_strict: bool = False,
    ) -> Dict[str, Any]:

        # Validate project name length
        if len(project) > ProjectConstants.PROJECT_NAME_MAX_LENGTH:
            raise RaggerAPIError(
                f"Project name exceeds maximum length of {ProjectConstants.PROJECT_NAME_MAX_LENGTH} "
                f"characters (current: {len(project)}). Please use a shorter name.",
                code="INVALID_PARAMETERS",
            )

        # Prepare the API request payload
        # Clean whitespace from all parameters to avoid parsing issues
        data = {
            "query": query.strip(),
            "organization": organization.strip(),
            "project": project.strip(),
            "user": user.strip(),
            "session_id": session_id.strip() if session_id else None,
            "is_strict": is_strict,
        }

        # Log the query operation for debugging and monitoring
        session_info = f"(continuing session {session_id})" if session_id else "(new session)"
        logger.debug(f"Processing query for {organization}/{project} (user: {user}) {session_info}")

        # Make the API request to process the query
        response = self.client.request(
            method="POST",  # POST to submit query data
            endpoint=self.endpoint,  # /query/ endpoint
            data=data,  # Query and context parameters
        )

        # Log successful completion and return the response
        session_id_result = response.get("session_id", "N/A")
        logger.debug(
            f"Query processed successfully for {organization}/{project} "
            f"(session: {session_id_result})"
        )
        return response
