"""HTTP client wrapper with retry logic."""

import asyncio
import logging
from typing import Any

import httpx

from .exceptions import APIError, NetworkError, RateLimitError
from .types import Headers

__all__ = ["HTTPClient", "AsyncHTTPClient", "_parse_response"]

logger = logging.getLogger(__name__)


def _parse_response(response: httpx.Response) -> Any:
    """Parse HTTP response and unwrap API wrapper.

    Args:
        response: HTTP response object

    Returns:
        Parsed JSON data (unwrapped from {code, msg, data} structure)

    Raises:
        RateLimitError: When rate limit is exceeded
        APIError: When API returns an error
    """
    # Handle rate limiting
    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 60))
        raise RateLimitError(
            f"Rate limit exceeded. Retry after {retry_after} seconds",
            retry_after=retry_after,
        )

    # Handle other HTTP errors
    if response.status_code >= 400:
        error_data = response.json() if response.content else {}
        raise APIError(
            error_data.get("error", f"HTTP {response.status_code}"),
            status_code=response.status_code,
            response_data=error_data,
        )

    # Parse response and unwrap API wrapper
    json_data = response.json()

    # Backend wraps response in {code, msg, data} structure
    if isinstance(json_data, dict) and "data" in json_data:
        if json_data.get("code") != 200:
            raise APIError(
                json_data.get("msg", "API returned error"),
                status_code=json_data.get("code", 500),
                response_data=json_data,
            )
        return json_data["data"]

    return json_data


class HTTPClient:
    """Synchronous HTTP client with automatic retry."""

    def __init__(
        self,
        base_url: str,
        headers: Headers,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        """Initialize HTTP client.

        Args:
            base_url: Base API URL
            headers: Default headers
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        self.base_url = base_url.rstrip("/")
        self.default_headers = headers
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: httpx.Client | None = None

    def __enter__(self) -> "HTTPClient":
        """Enter context manager."""
        self._client = httpx.Client(
            base_url=self.base_url,
            headers=self.default_headers,
            timeout=self.timeout,
        )
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit context manager."""
        if self._client:
            self._client.close()
            self._client = None

    def _get_client(self) -> httpx.Client:
        """Get or create client instance."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                headers=self.default_headers,
                timeout=self.timeout,
            )
        return self._client

    def request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make HTTP request with retry logic.

        Args:
            method: HTTP method
            path: API endpoint path
            **kwargs: Additional request parameters

        Returns:
            Response JSON data

        Raises:
            RateLimitError: When rate limit is exceeded
            APIError: When API returns an error
            NetworkError: When network error occurs
        """
        client = self._get_client()
        last_error: Exception | None = None

        for attempt in range(self.max_retries):
            try:
                response = client.request(method, path, **kwargs)
                return _parse_response(response)

            except httpx.TimeoutException as e:
                last_error = NetworkError(f"Request timeout after {self.timeout}s", e)
                logger.warning(f"Attempt {attempt + 1}/{self.max_retries} failed: timeout")

            except httpx.NetworkError as e:
                last_error = NetworkError(f"Network error: {str(e)}", e)
                logger.warning(f"Attempt {attempt + 1}/{self.max_retries} failed: {e}")

            except (RateLimitError, APIError):
                raise

            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error: {e}")
                break

            # Exponential backoff
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time}s...")
                import time
                time.sleep(wait_time)

        # All retries failed
        if isinstance(last_error, NetworkError):
            raise last_error
        raise NetworkError(f"Request failed after {self.max_retries} attempts", last_error)

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None


class AsyncHTTPClient:
    """Asynchronous HTTP client with automatic retry."""

    def __init__(
        self,
        base_url: str,
        headers: Headers,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        """Initialize async HTTP client.

        Args:
            base_url: Base API URL
            headers: Default headers
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        self.base_url = base_url.rstrip("/")
        self.default_headers = headers
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "AsyncHTTPClient":
        """Enter async context manager."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.default_headers,
            timeout=self.timeout,
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit async context manager."""
        if self._client:
            await self._client.aclose()
            self._client = None

    def _get_client(self) -> httpx.AsyncClient:
        """Get or create client instance."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.default_headers,
                timeout=self.timeout,
            )
        return self._client

    async def request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make async HTTP request with retry logic.

        Args:
            method: HTTP method
            path: API endpoint path
            **kwargs: Additional request parameters

        Returns:
            Response JSON data

        Raises:
            RateLimitError: When rate limit is exceeded
            APIError: When API returns an error
            NetworkError: When network error occurs
        """
        client = self._get_client()
        last_error: Exception | None = None

        for attempt in range(self.max_retries):
            try:
                response = await client.request(method, path, **kwargs)
                return _parse_response(response)

            except httpx.TimeoutException as e:
                last_error = NetworkError(f"Request timeout after {self.timeout}s", e)
                logger.warning(f"Attempt {attempt + 1}/{self.max_retries} failed: timeout")

            except httpx.NetworkError as e:
                last_error = NetworkError(f"Network error: {str(e)}", e)
                logger.warning(f"Attempt {attempt + 1}/{self.max_retries} failed: {e}")

            except (RateLimitError, APIError):
                raise

            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error: {e}")
                break

            # Exponential backoff
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

        # All retries failed
        if isinstance(last_error, NetworkError):
            raise last_error
        raise NetworkError(f"Request failed after {self.max_retries} attempts", last_error)

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
