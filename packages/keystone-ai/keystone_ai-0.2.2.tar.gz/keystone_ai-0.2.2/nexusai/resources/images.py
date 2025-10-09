"""Image generation resource module."""

from typing import Optional
from nexusai.models import Image, Task
from nexusai._internal._poller import TaskPoller
from nexusai.constants import TASK_TYPE_IMAGE_GENERATION


class ImagesResource:
    """
    Image generation resource.

    Provides methods for generating images using AI models.
    """

    def __init__(self, client):
        """
        Initialize images resource.

        Args:
            client: InternalClient instance
        """
        self._client = client
        self._poller = TaskPoller(client)

    def generate(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        size: str = "1024x1024",
        quality: str = "standard",
        **kwargs,
    ) -> Image:
        """
        Generate an image (blocking mode).

        This method creates an image generation task and polls until completion.
        Image generation is always asynchronous on the server side.

        Args:
            prompt: Text description of the image to generate
            provider: AI service provider (e.g., "openai", "dmxapi", "anthropic").
                     If not specified, uses default provider.
            model: Model name (e.g., "dall-e-3", "gemini-2.5-flash-image").
                  If not specified, uses default model for the provider.
            size: Image size (e.g., "512x512", "1024x1024", "1920x1080").
                 Default: "1024x1024"
            quality: Image quality ("standard" or "hd"). Default: "standard"
            **kwargs: Additional model configuration parameters

        Returns:
            Image object containing the generated image URL and metadata

        Raises:
            InvalidRequestError: If request parameters are invalid
            APITimeoutError: If image generation times out
            APIError: If generation fails

        Example:
            ```python
            from nexusai import NexusAIClient

            client = NexusAIClient()

            # Simple mode (省心模式) - uses defaults
            image = client.images.generate("A beautiful sunset over mountains")

            # Expert mode (专家模式) - specify provider and model
            image = client.images.generate(
                prompt="A futuristic city with flying cars",
                provider="dmxapi",
                model="gemini-2.5-flash-image",
                size="1920x1080",
                quality="hd"
            )

            print(f"Image URL: {image.image_url}")
            print(f"Dimensions: {image.width}x{image.height}")
            ```
        """
        # Build request body
        request_body = {
            "task_type": TASK_TYPE_IMAGE_GENERATION,
            "input": {"prompt": prompt},
        }

        # Add optional provider and model
        if provider:
            request_body["provider"] = provider
        if model:
            request_body["model"] = model

        # Merge configuration parameters
        config_params = {"size": size, "quality": quality, **kwargs}
        request_body["config"] = config_params

        # Submit async task with Prefer header
        response = self._client.request(
            "POST",
            "/invoke",
            json_data=request_body,
            headers={"Prefer": "respond-async"},
        )

        # Parse task response
        task = Task(**response)

        # Poll task until completion
        result = self._poller.poll(task.task_id)

        # Extract image information from output
        output = result.get("output", {})

        return Image(
            image_url=output.get("image_url", ""),
            width=output.get("width", 0),
            height=output.get("height", 0),
            revised_prompt=output.get("revised_prompt"),
        )
