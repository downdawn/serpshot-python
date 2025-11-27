# SerpShot Python SDK

Official Python client for the [SerpShot API](https://www.serpshot.com) - Get real-time Google search results programmatically.

[![Python Version](https://img.shields.io/pypi/pyversions/serpshot)](https://pypi.org/project/serpshot/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[中文文档](README.zh.md) | [English](README.md)

## Key Features

- ⚡ **Lightning Fast** - Get results in 1-2 seconds with optimized infrastructure
- 🌍 **Global Coverage** - Support for 200+ countries and regions
- 🔒 **Reliable & Secure** - 99.9% uptime SLA with enterprise-grade security
- 🚀 **Developer Friendly** - Sync/async support, full type hints, intuitive API
- 🔄 **Batch Queries** - Process up to 100 queries in a single request
- 🛡️ **Smart Retries** - Built-in retry logic handles network issues automatically

## API Endpoints

The SDK uses the following SerpShot API endpoints:

- **Main Search**: `/api/search/google` - For regular and image searches

## Installation

### Using pip

```bash
pip install serpshot
```

### Using uv

```bash
uv add serpshot
```

## Get Your API Key

Free to use, just [register](https://www.serpshot.com/auth/register) to get your API key.

## Quick Start

### Synchronous Usage

```python
from serpshot import SerpShot

# Initialize client (API key can be provided or read from SERPSHOT_API_KEY env var)
client = SerpShot(api_key="your-api-key")

# Perform a search
response = client.search("Python programming")

# Process results
for result in response.results:
    print(f"{result.title}: {result.link}")

# Clean up
client.close()
```

### With Context Manager (Recommended)

```python
from serpshot import SerpShot

with SerpShot(api_key="your-api-key") as client:
    response = client.search("Python programming")
    print(f"Found {len(response.results)} results")
```

### Asynchronous Usage

```python
import asyncio
from serpshot import AsyncSerpShot

async def main():
    async with AsyncSerpShot(api_key="your-api-key") as client:
        response = await client.search("Python programming")
        print(f"Found {len(response.results)} results")

asyncio.run(main())
```

### Using Environment Variable

You can set your API key via the `SERPSHOT_API_KEY` environment variable, eliminating the need to pass it explicitly:

```bash
export SERPSHOT_API_KEY="your-api-key"
```

```python
from serpshot import SerpShot

# API key will be automatically read from environment variable
with SerpShot() as client:
    response = client.search("Python programming")
```

## API Reference

### SerpShot Client

#### Initialize

```python
from serpshot import SerpShot

client = SerpShot(
    api_key="your-api-key",      # Optional: Your SerpShot API key (or set SERPSHOT_API_KEY env var)
    base_url=None,                # Optional: Custom API endpoint
    timeout=30.0,                 # Optional: Request timeout in seconds
    max_retries=3,                # Optional: Maximum retry attempts
)
```

#### search()

Perform a Google search. Supports both single query and batch queries (up to 100 queries per request).

```python
from serpshot import SerpShot

# Single search
response = client.search(
    query="search query",         # Required: Search query string or list of queries (max 100)
    num=10,                       # Optional: Number of results per page (1-100)
    page=1,                       # Optional: Page number for pagination (starts from 1)
    gl="us",                      # Optional: Country code (e.g., 'us', 'uk', 'cn')
    hl="en",                      # Optional: Language code (e.g., 'en', 'zh-CN')
    lr="en",                      # Optional: Content language restriction (e.g., 'en', 'zh-CN')
    location="US",                # Optional: Location for local search (e.g., 'US', 'GB', 'CN')
)

# Batch search (recommended for multiple queries)
responses = client.search(
    query=["Python", "JavaScript", "Rust"],  # List of queries (1-100)
    num=10,
    gl="us",
    location="US",               # String location parameter supported
)
# Returns list[SearchResponse] when query is a list
```

**Note**: The `location` parameter accepts strings (recommended) or `LocationType` enum values.

#### image_search()

Perform a Google image search. Supports both single query and batch queries (up to 100 queries per request).

```python
# Single image search
response = client.image_search(
    query="cute puppies",         # Required: Image search query string or list (max 100)
    num=10,                       # Optional: Number of results per page (1-100)
    page=1,                       # Optional: Page number for pagination (starts from 1)
    gl="us",                      # Optional: Country code
    hl="en",                      # Optional: Language code
    lr="en",                      # Optional: Content language restriction
)

# Batch image search
responses = client.image_search(
    query=["cats", "dogs", "birds"],  # List of queries (1-100)
    num=10,
)
```

### Response Model

The `SearchResponse` object contains:

```python
class SearchResponse:
    success: bool                 # Request success status
    query: str                    # Original search query
    total_results: str            # Estimate of total results (e.g., "About 12,300,000 results")
    search_time: str              # Search execution time in seconds (as string)
    results: list[SearchResult] | list[ImageResult]  # List of search results
    credits_used: int             # Credits consumed
```

**Note**: When using batch search (passing a list of queries), `search()` returns `list[SearchResponse]` instead of a single `SearchResponse`.

### Search Result Model

Each result in `response.results` contains:

```python
class SearchResult:
    title: str                    # Result title
    link: str                     # Result URL
    snippet: str                  # Description snippet
    position: int                 # Position in results (1-based)
```

### Image Result Model

For image searches, results contain:

```python
class ImageResult:
    title: str                    # Image title
    link: str                     # Image source URL
    thumbnail: str                # Thumbnail URL
    source: str                   # Source website
    source_link: str              # Source page URL
    width: int                    # Image width in pixels
    height: int                   # Image height in pixels
    position: int                 # Result position
```

## Advanced Examples

### Batch Search

Batch search allows you to process multiple queries (up to 100) in a single API call, which is more efficient than separate calls:

```python
from serpshot import SerpShot

with SerpShot(api_key="your-api-key") as client:
    queries = ["Python", "JavaScript", "Rust", "Go"]
    responses = client.search(queries, num=10)  # Returns list[SearchResponse]
    
    for query, response in zip(queries, responses):
        print(f"{query}: {len(response.results)} results")
        if response.results:
            print(f"  Top result: {response.results[0].title}\n")
```

### Pagination

```python
from serpshot import SerpShot

with SerpShot(api_key="your-api-key") as client:
    page1 = client.search("Python", num=10, page=1)
    page2 = client.search("Python", num=10, page=2)
    page3 = client.search("Python", num=10, page=3)
```

### Asynchronous Batch Search

```python
import asyncio
from serpshot import AsyncSerpShot

async def main():
    async with AsyncSerpShot(api_key="your-api-key") as client:
        queries = ["Python", "JavaScript", "Rust"]
        responses = await client.search(queries, num=10)
        for response in responses:
            print(f"Found {len(response.results)} results")

asyncio.run(main())
```

### Error Handling

```python
from serpshot import (
    SerpShot,
    AuthenticationError,
    RateLimitError,
    InsufficientCreditsError,
    APIError,
    NetworkError,
)

try:
    with SerpShot(api_key="your-api-key") as client:
        response = client.search("test query")
except AuthenticationError as e:
    print(f"Invalid API key: {e}")
except RateLimitError as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after}s")
except InsufficientCreditsError as e:
    print(f"Insufficient credits. Need: {e.credits_required}")
except APIError as e:
    print(f"API error ({e.status_code}): {e.message}")
except NetworkError as e:
    print(f"Network error: {e}")
```

### Custom Configuration

```python
client = SerpShot(
    api_key="your-api-key",
    timeout=60.0,        # Longer timeout for slow connections
    max_retries=5,       # More retries for reliability
)
```

## Get Available Credits

```python
from serpshot import SerpShot

with SerpShot(api_key="your-api-key") as client:
    credits = client.get_available_credits()
    print(f"Available credits: {credits}")
```

## Rate Limits

Please refer to your SerpShot account dashboard for rate limit information. The SDK automatically handles rate limiting with exponential backoff.

## Credit Costs

Different search operations consume different amounts of credits.

Use the `response.credits_used` field to track actual credit consumption for each request.

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/downdawn/serpshot-python.git
cd serpshot-python

# Install with dev dependencies using uv
uv sync --dev

# Or using pip
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Type Checking

```bash
mypy serpshot
```

### Linting

```bash
ruff check serpshot
```

## Examples

Check out the [examples](examples/) directory for more usage examples:

- [sync_example.py](examples/sync_example.py) - Synchronous usage examples
- [async_example.py](examples/async_example.py) - Asynchronous usage examples

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: support@serpshot.com
- 📖 Documentation: https://www.serpshot.com/docs
- 🐛 Issues: https://github.com/downdawn/serpshot-python/issues

## Links

- [SerpShot Website](https://www.serpshot.com)
- [API Documentation](https://www.serpshot.com/docs)
- [Get API Key](https://www.serpshot.com/dashboard/api-keys)
