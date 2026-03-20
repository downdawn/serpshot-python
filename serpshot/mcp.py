"""MCP server for Serpshot Google Search API.

Usage:
    python -m serpshot.mcp

Environment:
    SERPSHOT_API_KEY: Your Serpshot API key (required)

Claude Desktop config (~/.claude/claude_desktop_config.json):
    {
      "mcpServers": {
        "serpshot": {
          "command": "python",
          "args": ["-m", "serpshot.mcp"],
          "env": { "SERPSHOT_API_KEY": "your_key_here" }
        }
      }
    }
"""

from __future__ import annotations

import asyncio
import os

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent, Tool
except ImportError as e:
    raise ImportError(
        "MCP support requires the 'mcp' package. "
        "Install it with: pip install 'serpshot[mcp]'"
    ) from e

from .client import SerpShot
from .exceptions import SerpShotError

app = Server("serpshot")


def _get_client() -> SerpShot:
    api_key = os.environ.get("SERPSHOT_API_KEY")
    if not api_key:
        raise ValueError(
            "SERPSHOT_API_KEY environment variable is required. "
            "Get your key at https://serpshot.com/dashboard"
        )
    return SerpShot(api_key=api_key)


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="google_search",
            description=(
                "Search Google and return organic results, knowledge graph, and related searches. "
                "Use for real-time web information, research, and fact-checking."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query",
                    },
                    "num": {
                        "type": "integer",
                        "description": "Number of results (1-100, default: 10)",
                        "default": 10,
                    },
                    "gl": {
                        "type": "string",
                        "description": "Country code, e.g. 'us', 'cn', 'gb' (default: 'us')",
                        "default": "us",
                    },
                    "hl": {
                        "type": "string",
                        "description": "Interface language, e.g. 'en', 'zh-CN' (default: 'en')",
                        "default": "en",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="google_image_search",
            description=(
                "Search Google Images and return image results with thumbnails and source URLs."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Image search query",
                    },
                    "num": {
                        "type": "integer",
                        "description": "Number of results (1-100, default: 10)",
                        "default": 10,
                    },
                    "gl": {
                        "type": "string",
                        "description": "Country code (default: 'us')",
                        "default": "us",
                    },
                },
                "required": ["query"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    client = _get_client()
    try:
        with client:
            if name == "google_search":
                response = client.search(
                    query=arguments["query"],
                    num=arguments.get("num", 10),
                    gl=arguments.get("gl", "us"),
                    hl=arguments.get("hl", "en"),
                )
                lines = [f"Search: {response.query}", f"Total: {response.total_results}", ""]
                for r in response.results:
                    lines.append(f"{r.position}. {r.title}")
                    lines.append(f"   {r.link}")
                    lines.append(f"   {r.snippet}")
                    lines.append("")
                return [TextContent(type="text", text="\n".join(lines))]

            elif name == "google_image_search":
                response = client.image_search(
                    query=arguments["query"],
                    num=arguments.get("num", 10),
                    gl=arguments.get("gl", "us"),
                )
                lines = [f"Image Search: {response.query}", ""]
                for r in response.results:
                    lines.append(f"{r.position}. {r.title}")
                    lines.append(f"   Source: {r.source}")
                    lines.append(f"   Link: {r.link}")
                    lines.append(f"   Thumbnail: {r.thumbnail}")
                    lines.append("")
                return [TextContent(type="text", text="\n".join(lines))]

        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except SerpShotError as e:
        return [TextContent(type="text", text=f"Error: {e}")]


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
