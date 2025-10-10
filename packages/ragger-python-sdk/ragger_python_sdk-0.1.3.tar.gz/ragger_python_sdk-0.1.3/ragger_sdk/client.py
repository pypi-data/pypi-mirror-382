import json
import logging
from importlib.metadata import version
from typing import Any
from typing import Dict
from typing import Optional
from urllib.parse import urljoin
from urllib.parse import urlparse

import requests  # mypy: ignore[import-untyped]

from .constants import Config
from .constants import ErrorCodes
from .endpoints.chat_history import ChatHistoryAPI  # Chat session history retrieval
from .endpoints.documents import DocumentsAPI  # Unified document upload and management
from .endpoints.index import IndexAPI  # Vector index creation and management
from .endpoints.query import QueryAPI  # Natural language querying and RAG
from .exceptions import RaggerAPIError
from .exceptions import create_exception_from_response

logger = logging.getLogger(__name__)


class RaggerClient:
    def __init__(
        self,
        base_url: str = Config.BASE_URL,
        token: str = "",  # nosec
        timeout: int = Config.TIMEOUT,
        verify_ssl: bool = True,
    ) -> None:

        if not isinstance(base_url, str):
            raise RaggerAPIError(
                detail="base_url must be a non-empty string",
                code=ErrorCodes.MISSING_REQUIRED_PARAMETERS,
                status_code=400,
            )

        if not isinstance(token, str) or not token.strip():
            raise RaggerAPIError(
                detail="token must be a non-empty string",
                code=ErrorCodes.MISSING_REQUIRED_PARAMETERS,
                status_code=400,
            )

        # Normalize base URL (remove trailing slash)
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

        # Step 3: Validate that the base URL is actually a valid URL format
        # This catches common mistakes like missing http:// or malformed URLs
        try:
            parsed = urlparse(self.base_url)
            if not parsed.scheme or not parsed.netloc:
                raise RaggerAPIError(
                    detail=f"Invalid base_url format: {base_url}",
                    code=ErrorCodes.INVALID_SETTINGS,
                    status_code=400,
                )
        except Exception as e:
            raise RaggerAPIError(
                detail=f"Invalid base_url: {e}",
                code=ErrorCodes.INVALID_SETTINGS,
                status_code=400,
            ) from e

        # Step 4: Set up HTTP session with authentication and sensible defaults
        # Using a session allows connection pooling and reuse for better performance
        self.session = requests.Session()

        # Configure authentication header that will be sent with every request
        # The Ragger API uses Token-based authentication
        try:
            ragger_sdk_version = version("ragger_sdk")
        except Exception:
            ragger_sdk_version = "unknown"

        self.session.headers.update({
            "Authorization": f"Token {self.token}",  # Format required by Ragger API
            "User-Agent": f"RaggerSDK/{ragger_sdk_version}",  # Identify our SDK to the server
        })

        # Configure SSL verification setting
        self.session.verify = verify_ssl

        # Step 5: Initialize all the endpoint-specific API interfaces
        # These objects handle the actual API operations for different features
        # Each one gets a reference to this client so they can make HTTP requests
        self.documents = DocumentsAPI(self)  # Unified document upload and management
        self.index = IndexAPI(self)  # Vector index creation and management
        self.query = QueryAPI(self)  # Natural language querying and RAG
        self.chat_history = ChatHistoryAPI(self)  # Chat session history retrieval

        # Backward compatibility aliases for existing code
        # These will be deprecated in future versions
        self.documents_from_file = self.documents  # Legacy alias
        self.documents_from_text = self.documents  # Legacy alias

        # Log successful initialization for debugging
        logger.debug(f"Initialized RaggerClient. I will connect to '{self.base_url}'")

    def _build_url(self, endpoint: str) -> str:
        # Ensure endpoint starts with / for consistent URL building
        # This prevents issues like "base.com/v1documents" instead of "base.com/v1/documents"
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint

        # Use urljoin for proper URL combination that handles edge cases
        # The '+ /' ensures there's always a slash before the endpoint path
        return urljoin(self.base_url + "/", endpoint.lstrip("/"))

    def _prepare_request_data(
        self, data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:

        if not data:
            return None

        # Create a copy so we don't modify the original data
        # This is important because the original data is still needed for the actual API call
        sanitized = data.copy()

        # List of field names that might contain sensitive information
        # These will be replaced with a placeholder in the sanitized version
        sensitive_fields = [
            "token",
            "password",
            "secret",  # pragma: allowlist secret
            "api_key",
            "apikey",
            "access_token",
            "auth_token",
        ]

        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = "***REDACTED***"

        return sanitized

    def _handle_response(
        self, response: requests.Response, request_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        # Prepare sanitized request data for error context (removes sensitive info)
        sanitized_request = self._prepare_request_data(request_data)

        # Log the response status for debugging
        # This helps developers understand what's happening with their API calls
        logger.debug(f"API Response: {response.status_code} {response.reason}")

        # Handle successful responses (HTTP status 200-299)
        if 200 <= response.status_code < 300:
            try:
                # Most API responses are JSON, so try to parse them
                json_response = response.json()
                if isinstance(json_response, dict):
                    return json_response
                else:
                    # Handle case where JSON is not a dict (e.g., list or primitive)
                    return {"data": json_response}
            except (json.JSONDecodeError, ValueError):
                # Some endpoints might return non-JSON responses (rare)
                # In this case, return the raw response text for the caller to handle
                logger.warning(f"Non-JSON response: {response.text[:200]}")
                return {
                    "raw_response": response.text,
                    "status_code": response.status_code,
                }

        # Handle error responses (HTTP status 400+)
        # Log the error for debugging - developers often need this information
        logger.error(f"API Error: {response.status_code} {response.reason}")

        # Create and raise an appropriate exception based on the status code
        # The create_exception_from_response function determines the right exception type
        raise create_exception_from_response(response, sanitized_request)

    def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:

        # Step 1: Build the complete URL from base URL + endpoint
        url = self._build_url(endpoint)

        # Step 2: Prepare headers by merging defaults with any custom headers
        request_headers = {}
        if headers:
            request_headers.update(headers)

        # Step 3: Set content type for JSON requests (but not for file uploads)
        # File uploads need multipart/form-data which requests sets automatically
        if data and not files:  # If we have data but no files, it's a JSON request
            request_headers["Content-Type"] = "application/json"

        # Step 4: Log the request for debugging purposes
        # Could be helpful to see what requests are being made
        logger.debug(f"API Request: {method.upper()} {url}")
        if params:
            logger.debug(f"Query params: {params}")
        if data:
            # Log the keys of the data (not the values, for security)
            logger.debug(
                f"Request data keys: {list(data.keys()) if isinstance(data, dict) else 'non-dict'}"
            )

        try:
            # Step 5: Determine request type and prepare data accordingly
            # The requests library handles JSON and multipart uploads differently
            request_kwargs: Dict[str, Any]
            if files:
                # File upload mode: use 'data' parameter for form data + 'files' for files
                # Don't use 'json' parameter as it conflicts with multipart uploads
                request_kwargs = {
                    "data": data,  # Form data (will be form-encoded)
                    "files": files,  # Files (creates multipart/form-data request)
                }
            else:
                # Regular API call mode: use 'json' parameter for JSON data
                # This automatically sets Content-Type and encodes data as JSON
                request_kwargs = {
                    "json": data,  # JSON payload (automatically encoded)
                }

            # Step 6: Make the actual HTTP request
            response = self.session.request(
                method=method.upper(),  # Normalize HTTP method to uppercase
                url=url,  # Complete URL we built earlier
                params=params,  # Query parameters
                headers=request_headers,  # Headers (including authentication)
                timeout=self.timeout,  # Request timeout from client configuration
                **request_kwargs,  # Data/files configuration from above
                **kwargs,  # Any additional arguments from caller
            )

            # Step 7: Process the response and return parsed data
            return self._handle_response(response, data)

        # Step 8: Handle various types of request failures
        # Convert low-level network errors into meaningful SDK exceptions
        except requests.exceptions.Timeout as e:
            raise RaggerAPIError(
                f"Request timed out after {self.timeout} seconds",
                request_data=self._prepare_request_data(data),
            ) from e
        except requests.exceptions.ConnectionError as e:
            raise RaggerAPIError(
                f"Connection error: {str(e)}",
                request_data=self._prepare_request_data(data),
            ) from e
        except requests.exceptions.RequestException as e:
            raise RaggerAPIError(
                f"Request failed: {str(e)}",
                request_data=self._prepare_request_data(data),
            ) from e

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Dict[str, Any]:

        return self.request(
            "GET",
            endpoint,
            params=params,
            **kwargs,
        )

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:

        return self.request("POST", endpoint, data=data, files=files, **kwargs)

    def put(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        # PUT is not used in the current Ragger API.
        return self.request("PUT", endpoint, data=data, **kwargs)

    def delete(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Send a DELETE request to the API.

        Args:
            endpoint: API endpoint path
            data: Request body data (JSON payload)
            **kwargs: Additional arguments to pass to request()

        Returns:
            Parsed API response
        """
        return self.request("DELETE", endpoint, data=data, **kwargs)

    def close(self) -> None:

        if hasattr(self, "session"):
            self.session.close()
            logger.debug("RaggerClient session closed")

    def __enter__(self) -> "RaggerClient":
        return self

    def __exit__(
        self,
        exc_type: Any,
        exc_val: Any,
        exc_tb: Any,
    ) -> None:

        self.close()

    def __repr__(self) -> str:
        return f"RaggerClient(base_url='{self.base_url}', timeout={self.timeout})"
