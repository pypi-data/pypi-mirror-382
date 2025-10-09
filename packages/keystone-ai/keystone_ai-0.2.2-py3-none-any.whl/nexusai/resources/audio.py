"""Audio processing resource module (ASR/TTS)."""

from typing import Optional
from nexusai.models import TranscriptionResponse, TTSResponse, Task
from nexusai._internal._poller import TaskPoller
from nexusai.constants import TASK_TYPE_SPEECH_TO_TEXT


class AudioResource:
    """
    Audio processing resource.

    Provides speech-to-text (ASR) and text-to-speech (TTS) capabilities.
    """

    def __init__(self, client):
        """
        Initialize audio resource.

        Args:
            client: InternalClient instance
        """
        self._client = client
        self._poller = TaskPoller(client)

    def transcribe(
        self,
        file_id: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        language: Optional[str] = None,
        **kwargs,
    ) -> TranscriptionResponse:
        """
        Transcribe audio to text (Speech-to-Text / ASR).

        Uses the unified file architecture: upload file first to get file_id,
        then use that file_id for transcription.

        Args:
            file_id: File ID from prior file upload (client.files.upload)
            provider: AI service provider (e.g., "dmxapi", "openai").
                     If not specified, uses default provider.
            model: Model name (e.g., "whisper-1").
                  If not specified, uses default model.
            language: Language code (e.g., "zh", "en"). If not specified,
                     auto-detects language.
            **kwargs: Additional model configuration parameters

        Returns:
            TranscriptionResponse with transcribed text

        Raises:
            InvalidRequestError: If file_id is invalid
            NotFoundError: If file doesn't exist
            APITimeoutError: If transcription times out
            APIError: If transcription fails

        Example:
            ```python
            from nexusai import NexusAIClient

            client = NexusAIClient()

            # Step 1: Upload audio file
            file_meta = client.files.upload("meeting.mp3")

            # Step 2: Transcribe using file_id (省心模式)
            transcription = client.audio.transcribe(file_id=file_meta.file_id)
            print(transcription.text)

            # Expert mode (专家模式) - specify provider and language
            transcription = client.audio.transcribe(
                file_id=file_meta.file_id,
                provider="dmxapi",
                language="zh"
            )
            print(f"Language: {transcription.language}")
            print(f"Duration: {transcription.duration}s")
            ```
        """
        # Build request body
        request_body = {
            "task_type": TASK_TYPE_SPEECH_TO_TEXT,
            "input": {"file_id": file_id},
        }

        # Add optional provider and model
        if provider:
            request_body["provider"] = provider
        if model:
            request_body["model"] = model

        # Build configuration
        config_params = {**kwargs}
        if language:
            config_params["language"] = language
        if config_params:
            request_body["config"] = config_params

        # Submit async task (ASR is typically async)
        response = self._client.request(
            "POST",
            "/invoke",
            json_data=request_body,
            headers={"Prefer": "respond-async"},
        )

        # Parse task and poll
        task = Task(**response)
        result = self._poller.poll(task.task_id)

        # Parse result
        output = result.get("output", {})

        return TranscriptionResponse(
            text=output.get("text", ""),
            language=output.get("language"),
            duration=output.get("duration"),
            segments=output.get("segments"),
        )

    def synthesize(
        self,
        text: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        voice: Optional[str] = None,
        **kwargs,
    ) -> TTSResponse:
        """
        Synthesize speech from text (Text-to-Speech / TTS).

        Args:
            text: Text to synthesize
            provider: AI service provider (e.g., "dmxapi", "openai")
            model: Model name
            voice: Voice name/ID (provider-specific)
            **kwargs: Additional model configuration parameters

        Returns:
            TTSResponse with audio URL

        Raises:
            InvalidRequestError: If text is invalid
            APITimeoutError: If synthesis times out
            APIError: If synthesis fails

        Example:
            ```python
            # Simple TTS
            audio = client.audio.synthesize("Hello, how are you?")
            print(f"Audio URL: {audio.audio_url}")

            # With voice selection
            audio = client.audio.synthesize(
                text="你好,很高兴见到你",
                provider="dmxapi",
                voice="zh-CN-XiaoxiaoNeural"
            )
            ```
        """
        # Build request body
        request_body = {
            "task_type": "text_to_speech",
            "input": {"text": text},
        }

        if provider:
            request_body["provider"] = provider
        if model:
            request_body["model"] = model

        # Build configuration
        config_params = {**kwargs}
        if voice:
            config_params["voice"] = voice
        if config_params:
            request_body["config"] = config_params

        # Submit async task
        response = self._client.request(
            "POST",
            "/invoke",
            json_data=request_body,
            headers={"Prefer": "respond-async"},
        )

        # Parse task and poll
        task = Task(**response)
        result = self._poller.poll(task.task_id)

        # Parse result
        output = result.get("output", {})

        return TTSResponse(
            audio_url=output.get("audio_url", ""),
            duration=output.get("duration"),
        )
