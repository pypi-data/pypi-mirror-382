"""Type definitions and aliases for Nexus AI SDK."""

from typing import Union, Dict, Any, Literal

# Common type aliases
JSON = Dict[str, Any]
Headers = Dict[str, str]
Params = Dict[str, Union[str, int, float, bool]]

# Task status types
TaskStatus = Literal["pending", "queued", "running", "completed", "failed"]

# Message role types
MessageRole = Literal["user", "assistant", "system"]

# Task types
TaskType = Literal[
    "text_generation",
    "image_generation",
    "speech_to_text",
    "text_to_speech",
    "document_processing",
]

# Processing status types
ProcessingStatus = Literal["queued", "processing", "completed", "failed"]
