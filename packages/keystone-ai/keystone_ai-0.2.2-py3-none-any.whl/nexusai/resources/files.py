"""File management resource module."""

from typing import BinaryIO, Union, Dict, Any
from pathlib import Path
from nexusai.models import FileMetadata, FileListResponse


class FilesResource:
    """
    File management resource.

    Provides unified file upload and management capabilities.
    Files uploaded here receive a file_id that can be used across
    all Nexus AI services (ASR, RAG, document processing, etc.)
    """

    def __init__(self, client):
        """
        Initialize files resource.

        Args:
            client: InternalClient instance
        """
        self._client = client

    def upload(
        self,
        file: Union[str, Path, BinaryIO],
        filename: str = None,
    ) -> FileMetadata:
        """
        Upload a file to Nexus AI platform.

        The file receives a unique file_id that can be used for subsequent
        operations like speech-to-text, knowledge base ingestion, etc.

        Args:
            file: File path (str or Path) or file-like object (BinaryIO)
            filename: Optional filename override. If not provided, uses
                     the filename from path or "upload" for file objects

        Returns:
            FileMetadata object containing file_id and metadata

        Raises:
            InvalidRequestError: If file is invalid or too large
            APIError: If upload fails

        Example:
            ```python
            from nexusai import NexusAIClient

            client = NexusAIClient()

            # Upload from file path
            file_meta = client.files.upload("meeting_audio.mp3")
            print(f"File ID: {file_meta.file_id}")

            # Use file_id for ASR
            transcription = client.audio.transcribe(file_id=file_meta.file_id)

            # Upload from file object
            with open("document.pdf", "rb") as f:
                file_meta = client.files.upload(f, filename="document.pdf")
            ```
        """
        # Handle different file input types
        if isinstance(file, (str, Path)):
            # File path
            file_path = Path(file)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file}")

            file_obj = open(file_path, "rb")
            actual_filename = filename or file_path.name
            should_close = True
        else:
            # File-like object
            file_obj = file
            actual_filename = filename or "upload"
            should_close = False

        try:
            # Prepare multipart form data
            files = {"file": (actual_filename, file_obj)}

            # Make request with httpx directly to avoid Content-Type: application/json
            import httpx

            url = f"{self._client.base_url}/files"
            headers = {
                "Authorization": f"Bearer {self._client.api_key}",
                "User-Agent": f"nexus-ai-python/0.1.0",
                # Do NOT set Content-Type - let httpx set it automatically for multipart
            }

            # Use a new httpx client instead of self._client.client to avoid default headers
            with httpx.Client() as upload_client:
                response = upload_client.post(url, files=files, headers=headers, timeout=self._client.timeout)
                self._client._check_response_status(response)
                data = response.json()

            return FileMetadata(**data)

        finally:
            if should_close:
                file_obj.close()

    def get(self, file_id: str) -> FileMetadata:
        """
        Get metadata for an uploaded file.

        Args:
            file_id: Unique file identifier

        Returns:
            FileMetadata object

        Raises:
            NotFoundError: If file doesn't exist
            APIError: If retrieval fails

        Example:
            ```python
            file_meta = client.files.get("file_abc123def456")
            print(f"Filename: {file_meta.filename}")
            print(f"Size: {file_meta.size} bytes")
            print(f"Type: {file_meta.content_type}")
            ```
        """
        response = self._client.request("GET", f"/files/{file_id}")
        return FileMetadata(**response)

    def delete(self, file_id: str) -> Dict[str, Any]:
        """
        Delete an uploaded file.

        Args:
            file_id: Unique file identifier

        Returns:
            Dictionary with deletion confirmation

        Raises:
            NotFoundError: If file doesn't exist
            APIError: If deletion fails

        Example:
            ```python
            result = client.files.delete("file_abc123def456")
            print(result["message"])  # "File deleted successfully"
            ```
        """
        return self._client.request("DELETE", f"/files/{file_id}")

    def list(self, page: int = 1, per_page: int = 20) -> FileListResponse:
        """
        List all files uploaded by current API key.

        Args:
            page: Page number (default: 1)
            per_page: Items per page, max 100 (default: 20)

        Returns:
            FileListResponse with files list and pagination info

        Raises:
            InvalidRequestError: If pagination parameters are invalid
            APIError: If retrieval fails

        Example:
            ```python
            # Get first page
            result = client.files.list(page=1, per_page=10)
            print(f"Total files: {result.total}")
            for file in result.files:
                print(f"- {file.filename} ({file.size} bytes)")

            # Get second page
            result = client.files.list(page=2, per_page=10)
            ```
        """
        response = self._client.request("GET", f"/files?page={page}&per_page={per_page}")
        return FileListResponse(**response)
