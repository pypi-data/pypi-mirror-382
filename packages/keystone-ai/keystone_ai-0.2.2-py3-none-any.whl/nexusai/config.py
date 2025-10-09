"""Global configuration management for Nexus AI SDK."""

import os
from typing import Optional
from dotenv import load_dotenv
from nexusai.constants import (
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT,
    DEFAULT_MAX_RETRIES,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_POLL_TIMEOUT,
)

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Global configuration manager for Nexus AI SDK.

    Configuration priority (highest to lowest):
    1. Explicitly passed parameters to client
    2. Environment variables
    3. Default values
    """

    def __init__(self):
        self._api_key: Optional[str] = os.getenv("NEXUS_API_KEY")
        self._base_url: str = os.getenv("NEXUS_BASE_URL", DEFAULT_BASE_URL)
        self._timeout: float = float(os.getenv("NEXUS_TIMEOUT", str(DEFAULT_TIMEOUT)))
        self._max_retries: int = int(os.getenv("NEXUS_MAX_RETRIES", str(DEFAULT_MAX_RETRIES)))
        self._poll_interval: float = float(
            os.getenv("NEXUS_POLL_INTERVAL", str(DEFAULT_POLL_INTERVAL))
        )
        self._poll_timeout: float = float(
            os.getenv("NEXUS_POLL_TIMEOUT", str(DEFAULT_POLL_TIMEOUT))
        )

    @property
    def api_key(self) -> Optional[str]:
        """Get the API key."""
        return self._api_key

    @api_key.setter
    def api_key(self, value: str) -> None:
        """Set the API key."""
        self._api_key = value

    @property
    def base_url(self) -> str:
        """Get the base URL (without trailing slash)."""
        return self._base_url.rstrip("/")

    @base_url.setter
    def base_url(self, value: str) -> None:
        """Set the base URL."""
        self._base_url = value.rstrip("/")

    @property
    def timeout(self) -> float:
        """Get the request timeout in seconds."""
        return self._timeout

    @timeout.setter
    def timeout(self, value: float) -> None:
        """Set the request timeout in seconds."""
        self._timeout = value

    @property
    def max_retries(self) -> int:
        """Get the maximum number of retries."""
        return self._max_retries

    @max_retries.setter
    def max_retries(self, value: int) -> None:
        """Set the maximum number of retries."""
        self._max_retries = value

    @property
    def poll_interval(self) -> float:
        """Get the task polling interval in seconds."""
        return self._poll_interval

    @poll_interval.setter
    def poll_interval(self, value: float) -> None:
        """Set the task polling interval in seconds."""
        self._poll_interval = value

    @property
    def poll_timeout(self) -> float:
        """Get the task polling timeout in seconds."""
        return self._poll_timeout

    @poll_timeout.setter
    def poll_timeout(self, value: float) -> None:
        """Set the task polling timeout in seconds."""
        self._poll_timeout = value


# Global configuration instance
config = Config()
