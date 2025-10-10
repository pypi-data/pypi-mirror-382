from __future__ import annotations

import logging  # For debug and status logging
from typing import TYPE_CHECKING
from typing import Any
from typing import Dict

if TYPE_CHECKING:
    from ragger_sdk.client import RaggerClient

from ..constants import ProjectConstants
from ..exceptions import RaggerAPIError

# Set up logging for this module
# This helps with debugging and monitoring chat history operations
logger = logging.getLogger(__name__)


class ChatHistoryAPI:
    def __init__(self, client: "RaggerClient") -> None:
        # Store the client reference for making authenticated API requests
        self.client = client
        # Define the endpoint for all chat history operations
        self.endpoint = "/history/"

    def sessions(
        self,
        organization: str,
        project: str,
        user: str,
    ) -> Dict[str, Any]:
        # Validate project name length
        if len(project) > ProjectConstants.PROJECT_NAME_MAX_LENGTH:
            raise RaggerAPIError(
                f"Project name exceeds maximum length of {ProjectConstants.PROJECT_NAME_MAX_LENGTH} "
                f"characters (current: {len(project)}). Please use a shorter name.",
                code="INVALID_PARAMETERS",
            )

        # Prepare query parameters
        params = {
            "organization": organization.strip(),
            "project": project.strip(),
            "user": user.strip(),
        }

        logger.debug(f"Retrieving all chat sessions for {organization}/{project} (user: {user})")

        # Make API request to get all sessions
        response = self.client.request(
            method="GET",
            endpoint=self.endpoint,
            params=params,
        )

        logger.debug(
            f"Retrieved {len(response)} chat sessions for {organization}/{project} (user: {user})"
        )

        if isinstance(response, dict):
            return response
        else:
            # This shouldn't happen if API is working correctly, but handle gracefully
            logger.warning("Unexpected response format when retrieving sessions")
            return {}

    def session(
        self,
        organization: str,
        project: str,
        user: str,
        session_id: str,
    ) -> Dict[str, Any]:
        # Validate project name length
        if len(project) > ProjectConstants.PROJECT_NAME_MAX_LENGTH:
            raise RaggerAPIError(
                f"Project name exceeds maximum length of {ProjectConstants.PROJECT_NAME_MAX_LENGTH} "
                f"characters (current: {len(project)}). Please use a shorter name.",
                code="INVALID_PARAMETERS",
            )

        params = {
            "organization": organization.strip(),
            "project": project.strip(),
            "user": user.strip(),
            "session": session_id.strip(),
        }

        logger.debug(
            f"Retrieving chat session {session_id} for {organization}/{project} (user: {user})"
        )

        # Make API request to get specific session
        response = self.client.request(
            method="GET",
            endpoint=self.endpoint,
            params=params,
        )

        # Handle different response formats
        if isinstance(response, dict):
            # If response is a dict, check if it has 'data'
            if (
                "data" in response
                and isinstance(response["data"], list)
                and len(response["data"]) > 0
            ):
                session_data: Dict[str, Any] = response["data"][0]
                logger.debug(
                    f"Retrieved chat session {session_id} "
                    f"with {len(session_data.get('messages', []))} messages"
                )
                return session_data
            else:
                # Handle case where API returns session dict directly
                logger.debug(
                    f"Retrieved chat session {session_id} "
                    f"with {len(response.get('messages', []))} messages"
                )
                return response
        elif isinstance(response, list) and len(response) > 0:
            # Handle legacy case where API returns array directly
            first_session: Dict[str, Any] = response[0]
            logger.debug(
                f"Retrieved chat session {session_id} with "
                f"{len(first_session.get('messages', []))} messages"
            )
            return first_session
        else:
            # This shouldn't happen if API is working correctly, but handle gracefully
            logger.warning(f"Unexpected response format for session {session_id}")
            # Return empty session dict
            return {
                "session_id": session_id,
                "messages": [],
                "error": "Unexpected response format",
            }

    def user_sessions(
        self,
        organization: str,
        project: str,
        user: str,
    ) -> Dict[str, Any]:

        # Get all sessions for the user
        sessions_response = self.sessions(organization, project, user)

        # Extract sessions list from response
        if isinstance(sessions_response, dict) and "data" in sessions_response:
            sessions = sessions_response["data"]
        else:
            # Fallback: assume the response is the sessions directly
            sessions = sessions_response if isinstance(sessions_response, list) else []

        total_sessions = len(sessions)
        total_messages = 0
        session_summaries = []

        for session in sessions:
            if isinstance(session, dict):  # Type guard to ensure session is a dict
                messages = session.get("messages", [])
                message_count = len(messages)
                total_messages += message_count

                # Find last activity (most recent message timestamp)
                last_activity = session.get("created_at")
                if messages:
                    # Get the timestamp of the last message
                    last_message = max(messages, key=lambda m: m.get("timestamp", 0))
                    last_activity = last_message.get("timestamp", session.get("created_at"))

                session_summaries.append({
                    "session_id": session.get("session_id"),
                    "message_count": message_count,
                    "created_at": session.get("created_at"),
                    "last_activity": last_activity,
                })

        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "sessions": session_summaries,
        }
