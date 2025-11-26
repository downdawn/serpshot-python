# SerpShot Python SDK

Official Python client for the [SerpShot API](https://www.serpshot.com) - Get Google Search Results programmatically.

[![Python Version](https://img.shields.io/pypi/pyversions/serpshot)](https://pypi.org/project/serpshot/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[中文文档](README.zh.md) | [English](README.md)

## Features

- ✅ **Synchronous & Asynchronous** - Support for both sync and async operations
- ✅ **Type Safe** - Full type hints with Pydantic models
- ✅ **Automatic Retries** - Built-in exponential backoff for failed requests
- ✅ **Error Handling** - Comprehensive exception hierarchy
- ✅ **Easy to Use** - Simple, intuitive API
- ✅ **Google Search** - Regular search and image search
- ✅ **Customizable** - Flexible configuration options

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

Before you can use the SDK, you need to get your API key from the [SerpShot Dashboard](https://www.serpshot.com/dashboard/api-keys).

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

with SerpShot(api_key="your-api-key") as client:  # Or use SerpShot() if env var is set
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
from serpshot import SerpShot, LocationType

# Single search
response = client.search(
    query="search query",         # Required: Search query string or list of queries (max 100)
    num=10,                       # Optional: Number of results per page (1-100)
    page=1,                       # Optional: Page number for pagination (starts from 1)
    gl="us",                      # Optional: Country code (e.g., 'us', 'uk', 'cn')
    hl="en",                      # Optional: Language code (e.g., 'en', 'zh-CN')
    lr="en",                      # Optional: Content language restriction (e.g., 'en', 'zh-CN')
    location=LocationType.US,    # Optional: Location type for local search
)

# Batch search (recommended for multiple queries)
responses = client.search(
    query=["Python", "JavaScript", "Rust"],  # List of queries (1-100)
    num=10,
)
# Returns list[SearchResponse] when query is a list
```

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

### Batch Search (Recommended)

The most efficient way to search multiple queries is using batch search, which makes a single API call:

```python
from serpshot import SerpShot

with SerpShot(api_key="your-api-key") as client:  # Or use SerpShot() if env var is set
    # Batch search - single API call for multiple queries
    queries = ["Python", "JavaScript", "Rust", "Go"]
    responses = client.search(queries, num=10)  # Returns list[SearchResponse]
    
    for query, response in zip(queries, responses):
        print(f"{query}: {len(response.results)} results")
        if response.results:
            print(f"  Top result: {response.results[0].title}\n")
```

**Note**: Batch search supports up to 100 queries per request and is more efficient than making separate API calls.

### Pagination

```python
from serpshot import SerpShot

with SerpShot(api_key="your-api-key") as client:  # Or use SerpShot() if env var is set
    # Get first page (results 1-10)
    page1 = client.search("Python", num=10, page=1)
    
    # Get second page (results 11-20)
    page2 = client.search("Python", num=10, page=2)
    
    # Get third page (results 21-30)
    page3 = client.search("Python", num=10, page=3)
```

### Asynchronous Usage

For async applications, you can use `AsyncSerpShot`:

```python
import asyncio
from serpshot import AsyncSerpShot

async def main():
    async with AsyncSerpShot(api_key="your-api-key") as client:
        # Single async search
        response = await client.search("Python programming")
        print(f"Found {len(response.results)} results")
        
        # Batch async search
        queries = ["Python", "JavaScript"]
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
    with SerpShot(api_key="your-api-key") as client:  # Or use SerpShot() if env var is set
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

## Environment Variables

You can set your API key via environment variable. The SDK will automatically read from the `SERPSHOT_API_KEY` environment variable if the `api_key` parameter is not provided:

```bash
export SERPSHOT_API_KEY="your-api-key"
```

Then use in code without passing `api_key`:

```python
from serpshot import SerpShot

# API key will be automatically read from SERPSHOT_API_KEY environment variable
client = SerpShot()
```

You can also still provide the API key explicitly, which takes precedence over the environment variable:

```python
from serpshot import SerpShot

# Explicit API key takes precedence
client = SerpShot(api_key="your-api-key")
```

## Rate Limits

Please refer to your SerpShot account dashboard for rate limit information. The SDK automatically handles rate limiting with exponential backoff.

## Credit Costs

Different search operations consume different amounts of credits:

- **Regular Search**: 1 credit per request (base)
- **Image Search**: ~2 credits per request
- **Higher result counts**: Additional credits for num > 10

Use `response.credits_used` to track consumption.

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
