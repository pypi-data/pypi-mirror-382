"""
Nexus AI Python SDK

A Python client library for the Nexus AI platform.
"""

from nexusai.__version__ import __version__
from nexusai.client import NexusAIClient
from nexusai.config import config
from nexusai import error

# Export commonly used error classes for convenience
from nexusai.error import (
    APIError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    NetworkError,
    ServerError,
    APITimeoutError,
    NotFoundError,
    InvalidRequestError,
    PermissionError,
    StreamError,
    FileUploadError,
)

__all__ = [
    "__version__",
    "NexusAIClient",
    "config",
    "error",
    # Error classes
    "APIError",
    "AuthenticationError",
    "ValidationError",
    "RateLimitError",
    "NetworkError",
    "ServerError",
    "APITimeoutError",
    "NotFoundError",
    "InvalidRequestError",
    "PermissionError",
    "StreamError",
    "FileUploadError",
]
