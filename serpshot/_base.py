"""Base client with shared logic for sync and async clients."""

import os
from typing import Any

from ._auth import AuthHandler
from .models import SearchRequest, SearchResponse
from .types import LocationType, SearchType

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
    def _transform_image_result(result: dict[str, Any]) -> dict[str, Any]:
        """Transform backend image result fields to client schema.

        Backend fields -> Client fields:
        - imageUrl -> link (the actual image URL)
        - link -> source_link (the source page URL)
        - imageWidth -> width
        - imageHeight -> height

        Args:
            result: Raw image result from backend

        Returns:
            Transformed result matching ImageResult schema
        """
        return {
            "title": result.get("title", ""),
            "link": result.get("imageUrl", ""),
            "thumbnail": result.get("thumbnailUrl", ""),
            "source": result.get("source", ""),
            "source_link": result.get("link", ""),
            "width": result.get("imageWidth", 0),
            "height": result.get("imageHeight", 0),
            "position": result.get("position", 0),
        }

    @staticmethod
    def _parse_search_response(
        data: dict[str, Any] | list[dict[str, Any]] | None,
        query: str = "",
    ) -> SearchResponse:
        """Parse API response into SearchResponse model.

        Args:
            data: Raw API response data (can be dict, list of dicts, or None)
            query: Original query string (used as fallback if data is empty)

        Returns:
            Parsed SearchResponse model (with empty results if no data)
        """
        # Handle empty or None data - return empty response instead of raising exception
        if data is None:
            return SearchResponse(
                success=True,
                query=query,
                total_results="0",
                search_time="0",
                results=[],
                credits_used=0,
            )

        # If backend returns a list (for batch queries), take the first result
        if isinstance(data, list):
            if not data:
                # Empty list is a valid response - return empty SearchResponse
                return SearchResponse(
                    success=True,
                    query=query,
                    total_results="0",
                    search_time="0",
                    results=[],
                    credits_used=0,
                )
            data = data[0]

        # Backend response structure mapping
        search_info = data.get("search_info", {}) if isinstance(data, dict) else {}
        results = data.get("results", []) if isinstance(data, dict) else []
        search_type = (
            data.get("search_params", {}).get("type", "search")
            if isinstance(data, dict)
            else "search"
        )

        # Transform image results to match client schema
        if search_type == "image":
            results = [BaseClient._transform_image_result(r) for r in results]

        response_data = {
            "success": True,
            "query": (
                data.get("search_params", {}).get("q", query)
                if isinstance(data, dict)
                else query
            ),
            "total_results": search_info.get("total_results", "0"),
            "search_time": search_info.get("search_time", "0"),
            "results": results,
            "credits_used": data.get("credits", 0) if isinstance(data, dict) else 0,
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
        location: str | LocationType | None = None,
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
            location: Location type for local search (e.g., 'US', 'GB', or LocationType.US)

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
        if "location" in params and isinstance(params["location"], LocationType):
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

        # Handle empty data - return empty response(s) instead of raising exception
        if not data:
            if isinstance(query, str):
                # Single query with no data - return empty SearchResponse
                return BaseClient._parse_search_response(None, query=query)
            else:
                # Batch query with no data - return list of empty SearchResponses
                return [
                    BaseClient._parse_search_response(None, query=q) for q in query
                ]

        # Normalize query to list for easier processing
        queries = [query] if isinstance(query, str) else query

        # Parse each response item
        responses = [
            BaseClient._parse_search_response(item, query=q)
            for item, q in zip(data, queries[: len(data)])
        ]

        # If we have fewer responses than queries, fill with empty responses
        if len(responses) < len(queries):
            responses.extend(
                [
                    BaseClient._parse_search_response(None, query=q)
                    for q in queries[len(responses) :]
                ]
            )

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
