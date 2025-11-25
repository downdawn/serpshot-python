"""Synchronous SerpShot API client."""

from typing import Any

from ._base import BaseClient
from ._http import HTTPClient
from .models import SearchResponse
from .types import LocationType, SearchType

__all__ = ["SerpShot"]


class SerpShot(BaseClient):
    """Synchronous SerpShot API client.

    Example:
        >>> from serpshot import SerpShot
        >>>
        >>> client = SerpShot(api_key="your-api-key")
        >>> response = client.search("Python programming")
        >>> for result in response.results:
        ...     print(result.title, result.link)
        >>> client.close()

    Or use as context manager:
        >>> with SerpShot(api_key="your-api-key") as client:
        ...     response = client.search("Python programming")
        ...     print(response.total_results)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        """Initialize synchronous SerpShot client.

        Args:
            api_key: SerpShot API key
            base_url: API base URL (optional, defaults to production)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for failed requests
        """
        super().__init__(api_key, base_url, timeout, max_retries)
        self._http = HTTPClient(
            base_url=self.base_url,
            headers=self.auth.get_headers(),
            timeout=timeout,
            max_retries=max_retries,
        )

    def __enter__(self) -> "SerpShot":
        """Enter context manager."""
        self._http.__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit context manager."""
        self._http.__exit__(*args)

    def search(
        self,
        query: str | list[str],
        *,
        num: int = 10,
        page: int = 1,
        gl: str = "us",
        hl: str = "en",
        lr: str = "en",
        location: LocationType | None = None,
    ) -> SearchResponse | list[SearchResponse]:
        """Perform a Google search (single or batch).

        Args:
            query: Search query string or list of query strings
            num: Number of results to return per page (1-100, default: 10)
            page: Page number for pagination (starts from 1, default: 1)
            gl: Country code for results (e.g., 'us', 'uk', 'cn', default: 'us')
            hl: Interface language code (e.g., 'en', 'zh-CN', default: 'en')
            lr: Content language restriction (e.g., 'en', 'zh-CN', default: 'en')
            location: Location type for local search
                (e.g., LocationType.US, LocationType.GB, default: None)

        Returns:
            SearchResponse for single query, list[SearchResponse] for batch queries

        Raises:
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit is exceeded
            InsufficientCreditsError: If account lacks credits
            ValidationError: If request parameters are invalid
            APIError: If API returns an error
            NetworkError: If network error occurs

        Example:
            >>> client = SerpShot(api_key="your-api-key")
            >>> # Single search
            >>> response = client.search("best restaurants", num=20)
            >>> print(f"Found {len(response.results)} results")
            >>> # Batch search
            >>> responses = client.search(["Python", "JavaScript", "Rust"], num=10)
            >>> for resp in responses:
            ...     print(f"Found {len(resp.results)} results")
            >>> client.close()
        """
        params = self._build_search_request_params(
            query=query,
            search_type=SearchType.SEARCH,
            num=num,
            page=page,
            gl=gl,
            hl=hl,
            lr=lr,
            location=location,
        )

        data = self._http.request("POST", "/api/search/google", json=params)
        return self._process_search_response(data, query)

    def image_search(
        self,
        query: str | list[str],
        *,
        num: int = 10,
        page: int = 1,
        gl: str = "us",
        hl: str = "en",
        lr: str = "en",
        location: LocationType | None = None,
    ) -> SearchResponse | list[SearchResponse]:
        """Perform a Google image search (single or batch).

        Args:
            query: Image search query string or list of query strings
            num: Number of results to return per page (1-100, default: 10)
            page: Page number for pagination (starts from 1, default: 1)
            gl: Country code for results (default: 'us')
            hl: Interface language code (default: 'en')
            lr: Content language restriction (default: 'en')
            location: Location type for local search
                (e.g., LocationType.US, LocationType.GB, default: None)

        Returns:
            SearchResponse for single query, list[SearchResponse] for batch queries

        Raises:
            Same exceptions as search()

        Example:
            >>> client = SerpShot(api_key="your-api-key")
            >>> # Single image search
            >>> response = client.image_search("cute puppies", num=20)
            >>> for img in response.results:
            ...     print(img.title, img.thumbnail)
            >>> # Batch image search
            >>> responses = client.image_search(["cats", "dogs", "birds"], num=10)
            >>> client.close()
        """
        params = self._build_search_request_params(
            query=query,
            search_type=SearchType.IMAGE,
            num=num,
            page=page,
            gl=gl,
            hl=hl,
            lr=lr,
            location=location,
        )

        data = self._http.request("POST", "/api/search/google", json=params)
        return self._process_search_response(data, query)

    def close(self) -> None:
        """Close the client and cleanup resources.

        Should be called when done using the client, unless using
        as a context manager.

        Example:
            >>> client = SerpShot(api_key="key")
            >>> try:
            ...     response = client.search("query")
            ... finally:
            ...     client.close()
        """
        self._http.close()
