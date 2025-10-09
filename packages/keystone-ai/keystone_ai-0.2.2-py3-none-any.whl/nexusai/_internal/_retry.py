"""Retry mechanism with exponential backoff for API requests."""

import time
import random
from typing import Callable, TypeVar, Optional, Type, Tuple
from nexusai.error import (
    APIError,
    NetworkError,
    ServerError,
    RateLimitError,
    APITimeoutError,
)

T = TypeVar("T")


class RetryConfig:
    """
    Configuration for retry behavior.

    Attributes:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry
        max_delay: Maximum delay in seconds between retries
        exponential_base: Base for exponential backoff (delay *= base ** attempt)
        jitter: Add random jitter to prevent thundering herd (0.0 to 1.0)
    """

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: float = 0.1,
    ):
        """Initialize retry configuration."""
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for the given retry attempt.

        Args:
            attempt: Retry attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        # Exponential backoff: delay = initial_delay * (base ** attempt)
        delay = self.initial_delay * (self.exponential_base**attempt)

        # Cap at max_delay
        delay = min(delay, self.max_delay)

        # Add jitter to prevent thundering herd
        if self.jitter > 0:
            jitter_amount = delay * self.jitter
            delay += random.uniform(-jitter_amount, jitter_amount)

        return max(0, delay)


# Default retry configuration
DEFAULT_RETRY_CONFIG = RetryConfig(
    max_retries=3,
    initial_delay=1.0,
    max_delay=60.0,
    exponential_base=2.0,
    jitter=0.1,
)


def should_retry(error: Exception, attempt: int, max_retries: int) -> bool:
    """
    Determine if an error should be retried.

    Args:
        error: The exception that occurred
        attempt: Current retry attempt (0-indexed)
        max_retries: Maximum number of retries allowed

    Returns:
        True if the error should be retried, False otherwise
    """
    # Check if we've exceeded max retries
    if attempt >= max_retries:
        return False

    # Always retry these error types
    if isinstance(error, (NetworkError, ServerError, APITimeoutError)):
        return True

    # Retry rate limit errors (they often include retry-after header)
    if isinstance(error, RateLimitError):
        return True

    # Don't retry client errors (4xx except 429)
    if isinstance(error, APIError) and error.status_code:
        if 400 <= error.status_code < 500 and error.status_code != 429:
            return False

    return False


def retry_with_backoff(
    func: Callable[..., T],
    retry_config: Optional[RetryConfig] = None,
    retryable_exceptions: Tuple[Type[Exception], ...] = (APIError,),
) -> Callable[..., T]:
    """
    Decorator to retry a function with exponential backoff.

    Args:
        func: Function to retry
        retry_config: Retry configuration (uses default if None)
        retryable_exceptions: Tuple of exception types that can be retried

    Returns:
        Wrapped function with retry logic

    Example:
        ```python
        @retry_with_backoff
        def make_api_call():
            return client.text.generate("Hello")

        # Or with custom config
        config = RetryConfig(max_retries=5, initial_delay=2.0)
        @retry_with_backoff(retry_config=config)
        def make_api_call():
            return client.text.generate("Hello")
        ```
    """
    config = retry_config or DEFAULT_RETRY_CONFIG

    def wrapper(*args, **kwargs) -> T:
        last_error = None

        for attempt in range(config.max_retries + 1):
            try:
                return func(*args, **kwargs)

            except retryable_exceptions as e:
                last_error = e

                # Check if we should retry
                if not should_retry(e, attempt, config.max_retries):
                    raise

                # Calculate delay
                if isinstance(e, RateLimitError) and e.retry_after:
                    # Use retry_after from rate limit response
                    delay = e.retry_after
                else:
                    delay = config.calculate_delay(attempt)

                # Log retry attempt (can be replaced with proper logging)
                error_msg = str(e).split("\n")[0][:100]  # First line, max 100 chars
                print(
                    f"[Retry {attempt + 1}/{config.max_retries}] "
                    f"Retrying after {delay:.2f}s due to: {error_msg}"
                )

                # Wait before retrying
                time.sleep(delay)

        # All retries exhausted
        if last_error:
            raise last_error

    return wrapper


class RetryableRequest:
    """
    Context manager for retryable API requests.

    Example:
        ```python
        with RetryableRequest(max_retries=5) as retry:
            response = retry.execute(lambda: client.text.generate("Hello"))
        ```
    """

    def __init__(self, retry_config: Optional[RetryConfig] = None):
        """Initialize retryable request context."""
        self.config = retry_config or DEFAULT_RETRY_CONFIG
        self.attempt = 0
        self.last_error = None

    def __enter__(self):
        """Enter context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        return False

    def execute(
        self,
        func: Callable[..., T],
        *args,
        **kwargs,
    ) -> T:
        """
        Execute a function with retry logic.

        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result of func

        Raises:
            APIError: If all retries are exhausted
        """
        for attempt in range(self.config.max_retries + 1):
            self.attempt = attempt
            try:
                return func(*args, **kwargs)

            except (APIError, NetworkError) as e:
                self.last_error = e

                # Check if we should retry
                if not should_retry(e, attempt, self.config.max_retries):
                    raise

                # Calculate delay
                if isinstance(e, RateLimitError) and e.retry_after:
                    delay = e.retry_after
                else:
                    delay = self.config.calculate_delay(attempt)

                # Wait before retrying
                time.sleep(delay)

        # All retries exhausted
        if self.last_error:
            raise self.last_error
