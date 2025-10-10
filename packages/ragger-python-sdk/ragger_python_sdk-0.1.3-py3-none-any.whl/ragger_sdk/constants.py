"""
Ragger SDK - Constants and Configuration
"""
import os

from typing import Final
from typing import List


class Config:

    BASE_URL: str = os.environ.get("RAGGER_BASE_URL", "https://ragger.ai/rag/api/v1")
    API_VERSION: Final[str] = "v1"
    TIMEOUT: int = 30  # seconds


class APIEndpoints:
    """API endpoint paths."""

    DOCUMENTS_FILE: Final[str] = "/documents/file/"
    DOCUMENTS_TEXT: Final[str] = "/documents/text/"
    INDEX: Final[str] = "/index/"
    QUERY: Final[str] = "/query/"
    CHAT_HISTORY: Final[str] = "/history/"


class ErrorCodes:
    """API error codes."""

    INVALID_SETTINGS = "invalid_settings"
    MISSING_REQUIRED_PARAMETERS = "missing_required_parameters"
    RESOURCE_CONFLICT = "resource_conflict"
    RESOURCE_NOT_FOUND = "resource_not_found"
    UNEXPECTED_ERROR = "unexpected_error"


class DocumentConstants:
    """File upload constants."""

    SUPPORTED_EXTENSIONS: Final[List[str]] = [
        ".pdf",
        ".txt",
        ".docx",
        ".doc",
        ".rtf",
        ".md",
        ".html",
        ".csv",
        ".json",
    ]
    MAX_FILE_SIZE: Final[int] = 100 * 1024 * 1024  # 100 MB
    DOCUMENT_NAME_MAX_LENGTH: Final[int] = 50  # Important: keep in sync with backend


class ProjectConstants:
    """Project-related constants."""

    PROJECT_NAME_MAX_LENGTH: Final[int] = 50  # Important: keep in sync with backend


class LoggingConfig:
    """Logging configuration."""

    DEFAULT_LOG_LEVEL: Final[str] = "INFO"
    INDEX_LOGGER_NAME: Final[str] = "ragger_sdk.index"
