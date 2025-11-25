"""Authentication handler for SerpShot API."""

from .exceptions import AuthenticationError
from .types import Headers

__all__ = ["AuthHandler"]


class AuthHandler:
    """Handles API authentication."""

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize authentication handler.

        Args:
            api_key: SerpShot API key
        """
        if not api_key or not api_key.strip():
            raise AuthenticationError("API key is required")
        self.api_key = api_key.strip()

    def get_headers(self) -> Headers:
        """Get authentication headers.

        Returns:
            Dictionary of headers with API key
        """
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def validate(self) -> None:
        """Validate API key format.

        Raises:
            AuthenticationError: If API key is invalid
        """
        if not self.api_key or len(self.api_key) < 10:
            raise AuthenticationError("API key appears to be invalid")
