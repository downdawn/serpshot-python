"""Base client with shared logic for sync and async clients."""

import os
from typing import Any

from ._auth import AuthHandler
from .models import SearchRequest, SearchResponse
from .types import LocationType, QueryParams, SearchType

__all__ = ["BaseClient"]

# Environment variable name for API key
ENV_API_KEY = "SERPSHOT_API_KEY"


class BaseClient:
    """Base client containing shared logic."""

    DEFAULT_BASE_URL = "https://api.serpshot.com"

    @staticmethod
    def _get_api_key(api_key: str | None = None) -> str:
        """Get API key from parameter or environment variable.

        Args:
            api_key: API key provided directly, or None to read from environment

        Returns:
            API key string

        Raises:
            ValueError: If API key is not provided and not found in environment
        """
        if api_key:
            return api_key

        env_key = os.getenv(ENV_API_KEY)
        if env_key:
            return env_key

        raise ValueError(
            f"API key is required. Either provide it as 'api_key' parameter "
            f"or set the {ENV_API_KEY} environment variable."
        )

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        """Initialize base client.

        Args:
            api_key: SerpShot API key. If not provided, will try to read from
                SERPSHOT_API_KEY environment variable.
            base_url: API base URL (optional)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        resolved_api_key = self._get_api_key(api_key)
        self.auth = AuthHandler(resolved_api_key)
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

    @staticmethod
    def _build_search_params(
            query: str,
        search_type: SearchType = SearchType.SEARCH,
        num: int = 10,
        page: int = 1,
        gl: str = "us",
        hl: str = "en",
        lr: str = "en",
        location: LocationType | None = None,
        **extra_params: Any,
    ) -> QueryParams:
        """Build search request parameters.

        Args:
            query: Search query
            search_type: Type of search (search or image)
            num: Number of results per page (1-100, default: 10)
            page: Page number for pagination (starts from 1, default: 1)
            gl: Country code
            hl: Interface language code
            lr: Content language restriction
            location: Location type for local search
            **extra_params: Additional parameters

        Returns:
            Dictionary of query parameters
        """
        # Validate using Pydantic model
        request = SearchRequest(
            queries=[query],  # Convert single query to list
            type=search_type,
            num=num,
            page=page,
            gl=gl,
            hl=hl,
            lr=lr,
            location=location,
        )

        # Convert to dict and filter None values
        params = request.model_dump(exclude_none=True)

        # Convert enum values to strings
        if "type" in params:
            params["type"] = params["type"].value

        # Add any extra parameters
        params.update(extra_params)

        return params

    @staticmethod
    def _parse_search_response(data: dict[str, Any] | list[dict[str, Any]]) -> SearchResponse:
        """Parse API response into SearchResponse model.

        Args:
            data: Raw API response data (can be dict or list of dicts)

        Returns:
            Parsed SearchResponse model
        """
        # If backend returns a list (for batch queries), take the first result
        if isinstance(data, list):
            if not data:
                raise ValueError("Empty response from API")
            data = data[0]

        # Backend response structure mapping
        search_info = data.get("search_info", {})

        # Transform image results to match client schema
        results = data.get("results", [])
        search_type = data.get("search_params", {}).get("type", "search")

        if search_type == "image":
            # Map backend image fields to client schema
            results = [
                {
                    "title": r.get("title", ""),
                    "link": r.get("imageUrl", ""),  # Backend imageUrl -> client link
                    "thumbnail": r.get("thumbnailUrl"),
                    "source": r.get("source"),
                    "source_link": r.get("link"),  # Backend link -> client source_link
                    "width": r.get("imageWidth"),
                    "height": r.get("imageHeight"),
                    "position": r.get("position"),
                }
                for r in results
            ]

        response_data = {
            "success": True,
            "query": data.get("search_params", {}).get("q", ""),
            "total_results": search_info.get("total_results", "0"),
            "search_time": search_info.get("search_time", "0"),
            "results": results,
            "credits_used": data.get("credits", 1),
        }

        return SearchResponse.model_validate(response_data)

    @staticmethod
    def _build_search_request_params(
        query: str | list[str],
        search_type: SearchType,
        num: int = 10,
        page: int = 1,
        gl: str = "us",
        hl: str = "en",
        lr: str = "en",
        location: LocationType | None = None,
    ) -> dict[str, Any]:
        """Build search request parameters - shared logic for search and image_search.

        Args:
            query: Search query string or list of query strings
            search_type: Type of search (SEARCH or IMAGE)
            num: Number of results to return per page (1-100, default: 10)
            page: Page number for pagination (starts from 1, default: 1)
            gl: Country code
            hl: Interface language code
            lr: Content language restriction
            location: Location type for local search

        Returns:
            Dictionary of request parameters
        """
        # Normalize to list
        queries = [query] if isinstance(query, str) else query

        # Build request with queries list
        request = SearchRequest(
            queries=queries,
            type=search_type,
            num=num,
            page=page,
            gl=gl,
            hl=hl,
            lr=lr,
            location=location,
        )

        params = request.model_dump(exclude_none=True)
        # Convert enum values to strings
        if "type" in params:
            params["type"] = params["type"].value
        if "location" in params:
            params["location"] = params["location"].value

        return params

    @staticmethod
    def _process_search_response(
        data: Any,
        query: str | list[str],
    ) -> SearchResponse | list[SearchResponse]:
        """Process search response - shared logic for search and image_search.

        Args:
            data: Raw API response data
            query: Original query (str or list) to determine return type

        Returns:
            SearchResponse for single query, list[SearchResponse] for batch queries
        """
        # Backend returns list of results, parse each one
        if not isinstance(data, list):
            data = [data]

        responses = [BaseClient._parse_search_response(item) for item in data]

        # Return single response for single query, list for batch
        return responses[0] if isinstance(query, str) else responses

    @staticmethod
    def _calculate_credits(
            search_type: SearchType,
        num: int,
        gl: str | None = None,
    ) -> int:
        """Calculate credit cost for a search request.

        Args:
            search_type: Type of search
            num: Number of results
            gl: Country code

        Returns:
            Estimated credit cost
        """
        # Base cost
        base_cost = 1

        # Image search typically costs more
        if search_type == SearchType.IMAGE:
            base_cost = 2

        # Higher result counts may cost more
        if num > 10:
            base_cost += (num - 10) // 10

        # Some regions may have different costs
        premium_regions = {"us", "uk", "ca", "au"}
        if gl and gl.lower() in premium_regions:
            base_cost = int(base_cost * 1.2)

        return max(1, base_cost)
