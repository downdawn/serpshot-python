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

```python
from serpshot import SerpShot

with SerpShot(api_key="your-api-key") as client:
    response = client.search("Python programming")
    for result in response.results:
        print(f"{result.title}: {result.link}")
```

Set `SERPSHOT_API_KEY` env var to skip passing the key explicitly:

```python
with SerpShot() as client:
    response = client.search("Python programming")
```

Async:

```python
import asyncio
from serpshot import AsyncSerpShot

async def main():
    async with AsyncSerpShot() as client:
        response = await client.search("Python programming")

asyncio.run(main())
```

## MCP Integration

SerpShot includes a built-in [MCP](https://modelcontextprotocol.io) server, letting AI assistants (Claude, Cursor, Windsurf, etc.) call Google Search directly as a tool.

### Install MCP extra

```bash
pip install 'serpshot[mcp]'
# or
uv add 'serpshot[mcp]'
```

### Configuration

Add the following to your MCP client's config (Claude Code, Cursor, Windsurf, etc.):

```json
{
  "mcpServers": {
    "serpshot": {
      "command": "python",
      "args": ["-m", "serpshot.mcp"],
      "env": { "SERPSHOT_API_KEY": "your_key_here" }
    }
  }
}
```

Or with **uvx** (no install required):

```json
{
  "mcpServers": {
    "serpshot": {
      "command": "uvx",
      "args": ["--from", "serpshot[mcp]", "serpshot-mcp"],
      "env": { "SERPSHOT_API_KEY": "your_key_here" }
    }
  }
}
```

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `google_search` | Search Google — returns organic results, supports `query`, `num`, `gl`, `hl` |
| `google_image_search` | Search Google Images — returns image results with thumbnails and source URLs |

## API Reference

### SerpShot(api_key, base_url, timeout, max_retries)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `api_key` | env var | SerpShot API key, falls back to `SERPSHOT_API_KEY` |
| `base_url` | `None` | Custom API endpoint |
| `timeout` | `30.0` | Request timeout in seconds |
| `max_retries` | `3` | Maximum retry attempts |

Use `AsyncSerpShot` for async usage — same interface, all methods are awaitable.

### search(query, ...)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `query` | required | Search string or list of strings (max 100) |
| `num` | `10` | Results per page (1–100) |
| `page` | `1` | Page number |
| `gl` | `"us"` | Country code |
| `hl` | `"en"` | Interface language |
| `lr` | — | Content language restriction |
| `location` | — | Location for local search |

Returns `SearchResponse`, or `list[SearchResponse]` when `query` is a list.

### image_search(query, ...)

Same parameters as `search()` except `lr` and `location` are not supported.

### get_available_credits()

```python
with SerpShot() as client:
    print(client.get_available_credits())
```

### Response Models

**SearchResponse**

| Field | Type | Description |
|-------|------|-------------|
| `query` | `str` | Original query |
| `total_results` | `str` | Estimated total (e.g. `"About 12,300,000 results"`) |
| `search_time` | `str` | Execution time in seconds |
| `results` | `list` | `list[SearchResult]` or `list[ImageResult]` |
| `credits_used` | `int` | Credits consumed |

**SearchResult**: `title`, `link`, `snippet`, `position`

**ImageResult**: `title`, `link`, `thumbnail`, `source`, `source_link`, `width`, `height`, `position`

## Examples

### Batch Search

```python
with SerpShot() as client:
    responses = client.search(["Python", "JavaScript", "Rust"], num=10)
    for r in responses:
        print(f"{r.query}: {r.results[0].title}")
```

### Error Handling

```python
from serpshot import SerpShot, AuthenticationError, RateLimitError, InsufficientCreditsError, APIError, NetworkError

try:
    with SerpShot() as client:
        response = client.search("test query")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited, retry after {e.retry_after}s")
except InsufficientCreditsError as e:
    print(f"Need {e.credits_required} credits")
except (APIError, NetworkError) as e:
    print(f"Error: {e}")
```

The SDK handles rate limiting automatically with exponential backoff. Track credit usage via `response.credits_used`.

## Development

```bash
git clone https://github.com/downdawn/serpshot-python.git
cd serpshot-python
uv sync --dev
pytest
```

## License

MIT — see [LICENSE](LICENSE).

## Support

- 📧 support@serpshot.com
- 📖 [Documentation](https://www.serpshot.com/docs)
- 🐛 [Issues](https://github.com/downdawn/serpshot-python/issues)
- 🔑 [Get API Key](https://www.serpshot.com/dashboard/api-keys)
