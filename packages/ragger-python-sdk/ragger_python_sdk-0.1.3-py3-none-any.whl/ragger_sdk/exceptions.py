"""
Simple exception handling for the Ragger SDK.
"""

# Standard library imports
import json  # For formatting error response data
from typing import Any  # Type hints for better code clarity
from typing import Dict
from typing import Optional

from .constants import ErrorCodes


class RaggerAPIError(Exception):
    """
    Single exception class for all API errors.

    Provides simple boolean methods to check error types.
    """

    def __init__(
        self,
        detail: str,
        code: Optional[str] = None,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        request_data: Optional[Dict[str, Any]] = None,
    ):
        self.detail = detail
        self.code = code or ErrorCodes.UNEXPECTED_ERROR
        self.status_code = status_code
        self.response_data = response_data
        self.request_data = request_data
        super().__init__(self.detail)

    def __str__(self) -> str:
        if self.status_code:
            return f"{self.detail} (code: {self.code}) [HTTP {self.status_code}]"
        return f"{self.detail} (code: {self.code})"

    # Simple boolean methods for error type checking
    def is_validation_error(self) -> bool:
        """Check if this is a validation error."""
        return self.code == ErrorCodes.MISSING_REQUIRED_PARAMETERS

    def is_not_found(self) -> bool:
        """Check if this is a resource not found error."""
        return self.code == ErrorCodes.RESOURCE_NOT_FOUND

    def is_conflict(self) -> bool:
        """Check if this is a resource conflict error."""
        return self.code == ErrorCodes.RESOURCE_CONFLICT

    def is_settings_error(self) -> bool:
        """Check if this is an invalid settings error."""
        return self.code == ErrorCodes.INVALID_SETTINGS

    def is_server_error(self) -> bool:
        """Check if this is a server error."""
        return self.code == ErrorCodes.UNEXPECTED_ERROR or (
            self.status_code is not None and self.status_code >= 500
        )


def create_exception_from_response(
    response: Any,  # Expected to be requests.Response
    request_data: Optional[Dict[str, Any]] = None,
) -> RaggerAPIError:
    """
    Create a RaggerAPIError from an HTTP response.
    """
    # Extract the HTTP status code for determining exception type
    status_code = response.status_code

    try:
        # Most API errors return JSON with structured error data
        response_data = response.json()
        detail = response_data.get("detail", response_data.get("error", "API request failed"))
        code = response_data.get("code", ErrorCodes.UNEXPECTED_ERROR)
    except (json.JSONDecodeError, ValueError):
        # Response is not valid JSON - use the raw text
        response_data = {"raw_response": response.text}
        detail = f"HTTP {status_code}: {response.text[:200]}..."
        code = ErrorCodes.UNEXPECTED_ERROR

    return RaggerAPIError(
        detail=detail,
        code=code,
        status_code=status_code,
        response_data=response_data,
        request_data=request_data,
    )
