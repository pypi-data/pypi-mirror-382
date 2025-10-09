"""Constants used throughout the SDK."""

# API endpoints
DEFAULT_BASE_URL = "https://nexus-ai.juncai-ai.com/api/v1"  # Production
DEVELOPMENT_BASE_URL = "http://localhost:8000/api/v1"        # Local development

# Timeout settings (seconds)
DEFAULT_TIMEOUT = 30.0
DEFAULT_POLL_INTERVAL = 2.0
DEFAULT_POLL_TIMEOUT = 300.0

# Retry settings
DEFAULT_MAX_RETRIES = 3

# Task status
TASK_STATUS_PENDING = "pending"
TASK_STATUS_QUEUED = "queued"
TASK_STATUS_RUNNING = "running"
TASK_STATUS_COMPLETED = "completed"
TASK_STATUS_FAILED = "failed"

# Task types
TASK_TYPE_TEXT_GENERATION = "text_generation"
TASK_TYPE_IMAGE_GENERATION = "image_generation"
TASK_TYPE_SPEECH_TO_TEXT = "speech_to_text"
TASK_TYPE_DOCUMENT_PROCESSING = "document_processing"

# Stream markers
STREAM_END_MARKER = "[DONE]"
