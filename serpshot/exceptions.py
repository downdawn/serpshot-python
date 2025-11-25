"""Custom exceptions for SerpShot SDK."""

from typing import Any

__all__ = [
    "SerpShotError",
    "AuthenticationError",
    "RateLimitError",
    "InsufficientCreditsError",
    "APIError",
    "ValidationError",
    "NetworkError",
]


class SerpShotError(Exception):
    """Base exception for all SerpShot SDK errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        """Initialize error with message and optional status code."""
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthenticationError(SerpShotError):
    """Raised when API key is invalid or missing."""

    def __init__(self, message: str = "Invalid or missing API key") -> None:
        """Initialize authentication error."""
        super().__init__(message, status_code=401)


class RateLimitError(SerpShotError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int | None = None,
    ) -> None:
        """Initialize rate limit error."""
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class InsufficientCreditsError(SerpShotError):
    """Raised when account has insufficient credits."""

    def __init__(
        self,
        message: str = "Insufficient credits",
        credits_required: int | None = None,
        credits_available: int | None = None,
    ) -> None:
        """Initialize insufficient credits error."""
        super().__init__(message, status_code=402)
        self.credits_required = credits_required
        self.credits_available = credits_available


class APIError(SerpShotError):
    """Raised when API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: int,
        response_data: Any = None,
    ) -> None:
        """Initialize API error."""
        super().__init__(message, status_code=status_code)
        self.response_data = response_data


class ValidationError(SerpShotError):
    """Raised when request validation fails."""

    def __init__(self, message: str, errors: dict[str, Any] | None = None) -> None:
        """Initialize validation error."""
        super().__init__(message, status_code=400)
        self.errors = errors


class NetworkError(SerpShotError):
    """Raised when network/connection issues occur."""

    def __init__(self, message: str, original_error: Exception | None = None) -> None:
        """Initialize network error."""
        super().__init__(message, status_code=None)
        self.original_error = original_error
