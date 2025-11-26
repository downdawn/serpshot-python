"""Asynchronous SerpShot API client."""

from typing import Any

from ._base import BaseClient
from ._http import AsyncHTTPClient
from .models import SearchResponse
from .types import LocationType, SearchType

__all__ = ["AsyncSerpShot"]


class AsyncSerpShot(BaseClient):
    """Asynchronous SerpShot API client.

    Example:
        >>> import asyncio
        >>> from serpshot import AsyncSerpShot
        >>>
        >>> async def main():
        ...     client = AsyncSerpShot(api_key="your-api-key")
        ...     response = await client.search("Python programming")
        ...     for result in response.results:
        ...         print(result.title, result.link)
        ...     await client.close()
        >>>
        >>> asyncio.run(main())

    Or use as async context manager:
        >>> async def main():
        ...     async with AsyncSerpShot(api_key="your-api-key") as client:
        ...         response = await client.search("Python programming")
        ...         print(response.total_results)
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        """Initialize asynchronous SerpShot client.

        Args:
            api_key: SerpShot API key. If not provided, will try to read from
                SERPSHOT_API_KEY environment variable.
            base_url: API base URL (optional, defaults to production)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for failed requests
        """
        super().__init__(api_key, base_url, timeout, max_retries)
        self._http = AsyncHTTPClient(
            base_url=self.base_url,
            headers=self.auth.get_headers(),
            timeout=timeout,
            max_retries=max_retries,
        )

    async def __aenter__(self) -> "AsyncSerpShot":
        """Enter async context manager."""
        await self._http.__aenter__()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit async context manager."""
        await self._http.__aexit__(*args)

    async def search(
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
        """Perform a Google search asynchronously (single or batch).

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
            >>> async def example():
            ...     client = AsyncSerpShot(api_key="your-api-key")
            ...     # Single search
            ...     response = await client.search("best restaurants", num=20)
            ...     print(f"Found {len(response.results)} results")
            ...     # Batch search
            ...     responses = await client.search(["Python", "JavaScript", "Rust"], num=10)
            ...     for resp in responses:
            ...         print(f"Found {len(resp.results)} results")
            ...     await client.close()
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

        data = await self._http.request("POST", "/api/search/google", json=params)
        return self._process_search_response(data, query)

    async def image_search(
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
        """Perform a Google image search asynchronously (single or batch).

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
            >>> async def example():
            ...     client = AsyncSerpShot(api_key="your-api-key")
            ...     # Single image search
            ...     response = await client.image_search("cute puppies", num=20)
            ...     for img in response.results:
            ...         print(img.title, img.thumbnail)
            ...     # Batch image search
            ...     responses = await client.image_search(["cats", "dogs", "birds"], num=10)
            ...     await client.close()
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

        data = await self._http.request("POST", "/api/search/google", json=params)
        return self._process_search_response(data, query)

    async def close(self) -> None:
        """Close the client and cleanup resources.

        Should be called when done using the client, unless using
        as an async context manager.

        Example:
            >>> async def example():
            ...     client = AsyncSerpShot(api_key="key")
            ...     try:
            ...         response = await client.search("query")
            ...     finally:
            ...         await client.close()
        """
        await self._http.close()
