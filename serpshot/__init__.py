"""SerpShot API Python SDK.

Official Python client for the SerpShot API - Google Search Results.

Example:
    Synchronous usage:
        >>> from serpshot import SerpShot
        >>>
        >>> # API key can be provided explicitly or read from SERPSHOT_API_KEY env var
        >>> serpshot_client = SerpShot(api_key="your-api-key")
        >>> with serpshot_client:
        ...     response = serpshot_client.search("Python programming")
        ...     for result in response.results:
        ...         print(result.title)

    Asynchronous usage:
        >>> import asyncio
        >>> from serpshot import AsyncSerpShot
        >>>
        >>> async def main():
        ...     # API key can be provided explicitly or read from SERPSHOT_API_KEY env var
        ...     async_serpshot_client = AsyncSerpShot(api_key="your-api-key")
        ...     async with async_serpshot_client:
        ...         response = await async_serpshot_client.search("Python programming")
        ...         print(f"Found {response.total_results} results")
        >>>
        >>> asyncio.run(main())
"""

__version__ = "0.1.2"

from ._auth import AuthHandler
from .async_client import AsyncSerpShot
from .client import SerpShot
from .exceptions import (
    APIError,
    AuthenticationError,
    InsufficientCreditsError,
    NetworkError,
    RateLimitError,
    SerpShotError,
    ValidationError,
)
from .models import (
    ImageResult,
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from .types import Device, LocationType, SearchType

__all__ = [
    # Version
    "__version__",
    # Clients
    "SerpShot",
    "AsyncSerpShot",
    # Authentication
    "AuthHandler",
    # Exceptions
    "SerpShotError",
    "AuthenticationError",
    "RateLimitError",
    "InsufficientCreditsError",
    "APIError",
    "ValidationError",
    "NetworkError",
    # Models
    "SearchRequest",
    "SearchResponse",
    "SearchResult",
    "ImageResult",
    # Types
    "SearchType",
    "Device",
    "LocationType",
]
