import json
import logging
import mimetypes
import tempfile
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

from ..endpoints.status import StatusMixin
from ..exceptions import RaggerAPIError
from ..constants import DocumentConstants
from ..constants import ProjectConstants

logger = logging.getLogger(__name__)


class DocumentsAPI(StatusMixin):
    @staticmethod
    def _validate_name_length(name: str, project: str) -> None:
        """
        Validate document and project name lengths.

        Args:
            name: Document name to validate
            project: Project name to validate

        Raises:
            RaggerAPIError: If names exceed maximum length
        """
        if len(name) > DocumentConstants.DOCUMENT_NAME_MAX_LENGTH:
            raise RaggerAPIError(
                f"Document name exceeds maximum length of {DocumentConstants.DOCUMENT_NAME_MAX_LENGTH} "
                f"characters (current: {len(name)}). Please use a shorter name.",
                code="INVALID_PARAMETERS",
            )

        if len(project) > ProjectConstants.PROJECT_NAME_MAX_LENGTH:
            raise RaggerAPIError(
                f"Project name exceeds maximum length of {ProjectConstants.PROJECT_NAME_MAX_LENGTH} "
                f"characters (current: {len(project)}). Please use a shorter name.",
                code="INVALID_PARAMETERS",
            )

    def upload(
        self,
        name: str,
        organization: str,
        project: str,
        file_path: Optional[Union[str, Path]] = None,
        content: Optional[str] = None,
        content_type: Optional[str] = None,
        system_prompt: Optional[str] = None,
        text_search_config: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        force_overwrite: bool = False,
    ) -> Dict[str, Any]:

        # Validate name lengths early
        self._validate_name_length(name, project)

        if file_path is None and content is None:
            raise RaggerAPIError(
                "Either 'file_path' or 'content' must be provided",
                code="MISSING_REQUIRED_PARAMETERS",
            )

        if file_path is not None and content is not None:
            raise RaggerAPIError(
                "Cannot provide both 'file_path' and 'content'. Choose one.",
                code="INVALID_PARAMETERS",
            )

        # Handle file path upload
        if file_path is not None:
            return self._upload_from_file(
                file_path=file_path,
                name=name,
                organization=organization,
                project=project,
                system_prompt=system_prompt,
                text_search_config=text_search_config,
                metadata=metadata,
                force_overwrite=force_overwrite,
            )

        # Handle content upload (creates temporary file)
        # At this point, content is guaranteed to be not None due to validation above
        if content is None:
            raise RaggerAPIError("Content cannot be None at this point", code="INTERNAL_ERROR")

        return self._upload_from_content(
            content=content,
            name=name,
            organization=organization,
            project=project,
            content_type=content_type or "text/plain",
            system_prompt=system_prompt,
            text_search_config=text_search_config,
            metadata=metadata,
            force_overwrite=force_overwrite,
        )

    def _upload_from_file(
        self,
        file_path: Union[str, Path],
        name: str,
        organization: str,
        project: str,
        system_prompt: Optional[str] = None,
        text_search_config: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        force_overwrite: bool = False,
    ) -> Dict[str, Any]:
        """Upload document from an existing file path."""
        # Convert file path to Path object for robust file handling
        file_path = Path(file_path)

        # Verify file exists and is accessible
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not file_path.is_file():
            raise RaggerAPIError(f"Path is not a file: {file_path}")

        # Detect MIME content type for proper HTTP upload
        content_type, _ = mimetypes.guess_type(str(file_path))
        if not content_type:
            content_type = "application/octet-stream"

        logger.debug(f"Uploading file: {file_path} (type: {content_type})")

        return self._perform_upload(
            file_path=file_path,
            content_type=content_type,
            name=name,
            organization=organization,
            project=project,
            system_prompt=system_prompt,
            text_search_config=text_search_config,
            metadata=metadata,
            force_overwrite=force_overwrite,
        )

    def _upload_from_content(
        self,
        content: str,
        name: str,
        organization: str,
        project: str,
        content_type: str = "text/plain",
        system_prompt: Optional[str] = None,
        text_search_config: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        force_overwrite: bool = False,
    ) -> Dict[str, Any]:
        """Upload document from text content using a temporary file."""

        # Determine file extension from content type
        extension_map = {
            "text/plain": ".txt",
            "text/markdown": ".md",
            "text/html": ".html",
            "application/json": ".json",
            "text/csv": ".csv",
        }
        extension = extension_map.get(content_type, ".txt")

        logger.debug(f"Creating temporary file for content upload (type: {content_type})")

        # Create a temporary file with appropriate extension
        with tempfile.NamedTemporaryFile(
            mode='w', suffix=extension, delete=False, encoding='utf-8'
        ) as temp_file:
            temp_file.write(content)
            temp_file_path = Path(temp_file.name)

        try:
            return self._perform_upload(
                file_path=temp_file_path,
                content_type=content_type,
                name=name,
                organization=organization,
                project=project,
                system_prompt=system_prompt,
                text_search_config=text_search_config,
                metadata=metadata,
                force_overwrite=force_overwrite,
            )
        finally:
            # Clean up temporary file
            try:
                temp_file_path.unlink()
                logger.debug(f"Temporary file cleaned up: {temp_file_path}")
            except OSError as e:
                logger.warning(f"Failed to clean up temporary file {temp_file_path}: {e}")

    def _perform_upload(
        self,
        file_path: Path,
        content_type: str,
        name: str,
        organization: str,
        project: str,
        system_prompt: Optional[str] = None,
        text_search_config: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        force_overwrite: bool = False,
    ) -> Dict[str, Any]:
        """Perform the actual file upload to the API."""

        # Prepare form data for multipart upload
        form_data = {
            "name": name.strip(),
            "organization": organization.strip(),
            "project": project.strip(),
            "system_prompt": system_prompt.strip() if system_prompt else "",
            "text_search_config": text_search_config.strip() if text_search_config else "",
            "metadata": json.dumps(metadata) if metadata else "{}",
            "force_overwrite": str(force_overwrite).lower(),
        }

        # Debug logging
        logger.debug("Form data being sent to server:")
        for key, value in form_data.items():
            if key == "metadata":
                logger.debug(f"   {key} = {value[:100]}{'...' if len(str(value)) > 100 else ''}")
            else:
                logger.debug(f"   {key} = '{value}' (length: {len(str(value))})")

        # Perform the actual file upload
        try:
            with open(file_path, "rb") as f:
                files = {"document": (file_path.name, f, content_type)}

                response = self._client.post(
                    endpoint="/documents/file/",
                    data=form_data,
                    files=files,
                )

                return response

        except IOError as e:
            raise RaggerAPIError(f"Failed to read file {file_path}: {str(e)}") from e

    def delete(
        self,
        organization: str,
        project: str,
        name: Optional[str] = None,
        delete_all: bool = False,
    ) -> Dict[str, Any]:
        """
        Delete a document or all documents in a project.

        Args:
            organization: Organization name
            project: Project name
            name: Document name (required if delete_all is False)
            delete_all: If True, deletes all documents in the project

        Returns:
            API response dictionary

        Raises:
            RaggerAPIError: If parameters are invalid or API request fails
        """
        # Validation: must provide either name or delete_all=True
        if not delete_all and not name:
            raise RaggerAPIError(
                "Must provide either 'name' parameter or set 'delete_all=True'",
                code="MISSING_REQUIRED_PARAMETERS",
            )

        if delete_all and name:
            raise RaggerAPIError(
                "Cannot provide 'name' when 'delete_all=True'. Choose one operation.",
                code="INVALID_PARAMETERS",
            )

        # Validate name lengths if deleting a specific document
        if name:
            self._validate_name_length(name, project)

        # Prepare request data
        data = {
            "organization": organization.strip(),
            "project": project.strip(),
        }

        if delete_all:
            data["delete_all"] = "true"
            logger.debug(f"Deleting all documents in {organization}/{project}")
        else:
            data["name"] = name.strip() if name else ""
            logger.debug(f"Deleting document '{name}' from {organization}/{project}")

        # Make DELETE request
        response = self._client.delete(
            endpoint="/documents/file/",
            data=data,
        )

        logger.debug(f"Document deletion completed for {organization}/{project}")
        return response
