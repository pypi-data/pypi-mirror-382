"""Exception classes for the Distru SDK."""

from typing import Any, Dict, Optional


class DistruAPIError(Exception):
    """Base exception for all Distru API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize API error.

        Args:
            message: Error message
            status_code: HTTP status code
            response_data: Full response data from the API
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}

    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message

    def __repr__(self) -> str:
        """Return detailed representation of the error."""
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"status_code={self.status_code}, "
            f"response_data={self.response_data!r})"
        )


class AuthenticationError(DistruAPIError):
    """Raised when authentication fails (401)."""

    def __init__(
        self,
        message: str = "Authentication failed. Check your API token.",
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize authentication error."""
        super().__init__(message, status_code=401, response_data=response_data)


class AuthorizationError(DistruAPIError):
    """Raised when authorization fails (403)."""

    def __init__(
        self,
        message: str = "Not authorized to perform this action.",
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize authorization error."""
        super().__init__(message, status_code=403, response_data=response_data)


class NotFoundError(DistruAPIError):
    """Raised when a resource is not found (404)."""

    def __init__(
        self,
        message: str = "Resource not found.",
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize not found error."""
        super().__init__(message, status_code=404, response_data=response_data)


class ValidationError(DistruAPIError):
    """Raised when request validation fails (422)."""

    def __init__(
        self,
        message: str = "Validation error.",
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize validation error."""
        super().__init__(message, status_code=422, response_data=response_data)
        self.details = response_data.get("details", {}) if response_data else {}

    def __str__(self) -> str:
        """Return string representation with validation details."""
        base = super().__str__()
        if self.details:
            return f"{base} - Details: {self.details}"
        return base


class RateLimitError(DistruAPIError):
    """Raised when rate limit is exceeded (429)."""

    def __init__(
        self,
        message: str = "Rate limit exceeded.",
        retry_after: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize rate limit error.

        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
            response_data: Full response data from the API
        """
        super().__init__(message, status_code=429, response_data=response_data)
        self.retry_after = retry_after

    def __str__(self) -> str:
        """Return string representation with retry information."""
        base = super().__str__()
        if self.retry_after:
            return f"{base} - Retry after {self.retry_after} seconds."
        return base


class ServerError(DistruAPIError):
    """Raised when server returns 5xx error."""

    def __init__(
        self,
        message: str = "Internal server error.",
        status_code: int = 500,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize server error."""
        super().__init__(message, status_code=status_code, response_data=response_data)


class NetworkError(DistruAPIError):
    """Raised when network connection fails."""

    def __init__(
        self,
        message: str = "Network connection failed.",
        original_error: Optional[Exception] = None,
    ) -> None:
        """Initialize network error.

        Args:
            message: Error message
            original_error: The original exception that caused this error
        """
        super().__init__(message, status_code=None, response_data=None)
        self.original_error = original_error

    def __str__(self) -> str:
        """Return string representation with original error."""
        base = super().__str__()
        if self.original_error:
            return f"{base} - {type(self.original_error).__name__}: {self.original_error}"
        return base


class TimeoutError(DistruAPIError):
    """Raised when request times out."""

    def __init__(
        self,
        message: str = "Request timed out.",
        timeout: Optional[float] = None,
    ) -> None:
        """Initialize timeout error.

        Args:
            message: Error message
            timeout: The timeout value in seconds
        """
        super().__init__(message, status_code=None, response_data=None)
        self.timeout = timeout

    def __str__(self) -> str:
        """Return string representation with timeout value."""
        base = super().__str__()
        if self.timeout:
            return f"{base} - Timeout was {self.timeout} seconds."
        return base
