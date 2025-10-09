"""Main client class for Nexus AI SDK."""

from typing import Optional
from nexusai._internal._client import InternalClient


class NexusAIClient:
    """
    Main client for interacting with Nexus AI Platform.

    This is the primary entry point for the SDK. It provides access to
    all resource modules (images, text, sessions, knowledge_bases, etc.)

    Example:
        ```python
        from nexusai import NexusAIClient

        client = NexusAIClient(api_key="nxs_your_api_key")

        # Generate an image
        image = client.images.generate("A beautiful sunset")
        print(image.image_url)

        # Create a session
        session = client.sessions.create()
        response = session.invoke("Hello!")
        print(response.response.content)
        ```
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
    ):
        """
        Initialize the Nexus AI client.

        Args:
            api_key: API key for authentication. If not provided, reads from
                    NEXUS_API_KEY environment variable.
            base_url: Base URL for API. Defaults to http://localhost:8000/api/v1
                     (development mode). Set NEXUS_BASE_URL environment variable
                     to switch to production.
            timeout: Request timeout in seconds. Defaults to 30.
            max_retries: Maximum number of retries for failed requests. Defaults to 3.

        Raises:
            AuthenticationError: If API key is not provided

        Example:
            ```python
            # Using environment variables (recommended)
            client = NexusAIClient()

            # Explicit configuration
            client = NexusAIClient(
                api_key="nxs_your_api_key",
                base_url="https://nexus-ai.juncai-ai.com/api/v1",
                timeout=60
            )
            ```
        """
        self._internal_client = InternalClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Lazy-load resource modules to avoid circular imports
        self._images_resource = None
        self._text_resource = None
        self._sessions_resource = None
        self._audio_resource = None
        self._files_resource = None
        self._knowledge_bases_resource = None

    @property
    def images(self):
        """Access image generation resources."""
        if self._images_resource is None:
            from nexusai.resources.images import ImagesResource

            self._images_resource = ImagesResource(self._internal_client)
        return self._images_resource

    @property
    def text(self):
        """Access text generation resources."""
        if self._text_resource is None:
            from nexusai.resources.text import TextResource

            self._text_resource = TextResource(self._internal_client)
        return self._text_resource

    @property
    def sessions(self):
        """Access session management resources."""
        if self._sessions_resource is None:
            from nexusai.resources.sessions import SessionsResource

            self._sessions_resource = SessionsResource(self._internal_client)
        return self._sessions_resource

    @property
    def audio(self):
        """Access audio processing resources (ASR/TTS)."""
        if self._audio_resource is None:
            from nexusai.resources.audio import AudioResource

            self._audio_resource = AudioResource(self._internal_client)
        return self._audio_resource

    @property
    def files(self):
        """Access file management resources."""
        if self._files_resource is None:
            from nexusai.resources.files import FilesResource

            self._files_resource = FilesResource(self._internal_client)
        return self._files_resource

    @property
    def knowledge_bases(self):
        """Access knowledge base resources."""
        if self._knowledge_bases_resource is None:
            from nexusai.resources.knowledge_bases import KnowledgeBasesResource

            self._knowledge_bases_resource = KnowledgeBasesResource(self._internal_client)
        return self._knowledge_bases_resource

    def close(self) -> None:
        """
        Close the client and release resources.

        This should be called when you're done using the client to properly
        close HTTP connections.

        Example:
            ```python
            client = NexusAIClient()
            try:
                # Use client
                pass
            finally:
                client.close()
            ```
        """
        self._internal_client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, *args):
        """Context manager exit - close client."""
        self.close()


# Global client instance for convenience
_default_client: Optional[NexusAIClient] = None


def get_default_client() -> NexusAIClient:
    """
    Get or create the default global client instance.

    This is used by module-level convenience functions.

    Returns:
        Global NexusAIClient instance
    """
    global _default_client
    if _default_client is None:
        _default_client = NexusAIClient()
    return _default_client
