"""Exception classes for Nexus AI SDK."""

from typing import Optional, Dict, Any


class APIError(Exception):
    """
    Base exception for all SDK errors.

    All Nexus AI SDK exceptions inherit from this class.
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        response_body: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize an API error.

        Args:
            message: Human-readable error message
            status_code: HTTP status code (if applicable)
            error_code: Error code from API response
            response_body: Full response body from the API
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.response_body = response_body

    def __str__(self) -> str:
        """Return a string representation of the error."""
        # Ensure message is a string
        message_str = str(self.message) if not isinstance(self.message, str) else self.message
        parts = [message_str]
        if self.status_code:
            parts.append(f"(HTTP {self.status_code})")
        if self.error_code:
            parts.append(f"[{self.error_code}]")
        return " ".join(parts)

    def __repr__(self) -> str:
        """Return a detailed string representation of the error."""
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"status_code={self.status_code}, "
            f"error_code={self.error_code!r})"
        )


class AuthenticationError(APIError):
    """
    Authentication failed (HTTP 401).

    Raised when the API key is missing, invalid, or expired.
    """

    pass


class PermissionError(APIError):
    """
    Permission denied (HTTP 403).

    Raised when the API key doesn't have permission to perform the requested action.
    """

    pass


class NotFoundError(APIError):
    """
    Resource not found (HTTP 404).

    Raised when the requested resource doesn't exist.
    """

    pass


class RateLimitError(APIError):
    """
    Rate limit exceeded (HTTP 429).

    Raised when too many requests have been made in a given time period.
    """

    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        **kwargs,
    ):
        """
        Initialize a rate limit error.

        Args:
            message: Human-readable error message
            retry_after: Number of seconds to wait before retrying
            **kwargs: Additional arguments passed to APIError
        """
        super().__init__(message, **kwargs)
        self.retry_after = retry_after

    def __str__(self) -> str:
        """Return a string representation of the error."""
        base = super().__str__()
        if self.retry_after:
            return f"{base} (retry after {self.retry_after}s)"
        return base


class APITimeoutError(APIError):
    """
    Request or polling timed out.

    Raised when a request takes longer than the configured timeout,
    or when task polling exceeds the maximum wait time.
    """

    pass


class InvalidRequestError(APIError):
    """
    Invalid request parameters (HTTP 400).

    Raised when the request is malformed or contains invalid parameters.
    """

    pass


class ServerError(APIError):
    """
    Server-side error (HTTP 5xx).

    Raised when the server encounters an internal error.
    """

    pass


class ValidationError(APIError):
    """
    Data validation error (HTTP 422).

    Raised when request data fails server-side validation (Pydantic errors).
    Contains detailed field-level validation errors.
    """

    def __init__(
        self,
        message: str,
        validation_errors: Optional[list] = None,
        **kwargs,
    ):
        """
        Initialize a validation error.

        Args:
            message: Human-readable error message
            validation_errors: List of field-level validation errors from Pydantic
            **kwargs: Additional arguments passed to APIError
        """
        super().__init__(message, **kwargs)
        self.validation_errors = validation_errors or []

    def __str__(self) -> str:
        """Return a string representation of the error."""
        base = super().__str__()
        if self.validation_errors:
            # Format validation errors nicely
            errors = []
            for err in self.validation_errors[:3]:  # Show first 3 errors
                if isinstance(err, dict):
                    field = ".".join(str(loc) for loc in err.get("loc", []))
                    msg = err.get("msg", "")
                    errors.append(f"{field}: {msg}")
            if errors:
                error_str = "; ".join(errors)
                if len(self.validation_errors) > 3:
                    error_str += f" (and {len(self.validation_errors) - 3} more)"
                return f"{base} - {error_str}"
        return base


class NetworkError(APIError):
    """
    Network communication error.

    Raised when a network error occurs during the request.
    Examples: connection refused, DNS resolution failure, etc.
    """

    def __init__(
        self,
        message: str,
        is_retryable: bool = True,
        **kwargs,
    ):
        """
        Initialize a network error.

        Args:
            message: Human-readable error message
            is_retryable: Whether this error can be retried
            **kwargs: Additional arguments passed to APIError
        """
        super().__init__(message, **kwargs)
        self.is_retryable = is_retryable


class FileUploadError(APIError):
    """
    File upload error.

    Raised when file upload fails due to format, size, or other issues.
    """

    def __init__(
        self,
        message: str,
        file_name: Optional[str] = None,
        file_size: Optional[int] = None,
        **kwargs,
    ):
        """
        Initialize a file upload error.

        Args:
            message: Human-readable error message
            file_name: Name of the file that failed
            file_size: Size of the file in bytes
            **kwargs: Additional arguments passed to APIError
        """
        super().__init__(message, **kwargs)
        self.file_name = file_name
        self.file_size = file_size

    def __str__(self) -> str:
        """Return a string representation of the error."""
        base = super().__str__()
        if self.file_name:
            return f"{base} (file: {self.file_name})"
        return base


class StreamError(APIError):
    """
    Streaming error.

    Raised when SSE stream encounters an error.
    """

    pass
