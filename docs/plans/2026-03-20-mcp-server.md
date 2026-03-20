# Serpshot MCP Server Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在 `serpshot-python` SDK 中新增 MCP server 支持，让用户可以通过 `python -m serpshot.mcp` 启动一个 MCP server，供 Claude Desktop、Cursor 等 MCP 客户端直接调用 Serpshot 搜索能力。

**Architecture:** 在现有 `serpshot/` 包内新增 `mcp.py` 模块，依赖已有的 `SerpShot` 同步客户端。通过 `mcp` 可选依赖引入 `mcp` SDK，暴露两个 tool：`google_search` 和 `google_image_search`。`pyproject.toml` 新增 `[mcp]` optional dependency group，版本升至 `0.2.0`。

**Tech Stack:** Python 3.10+, `mcp>=1.0.0` (MCP Python SDK), 现有 `serpshot` SDK

---

## Task 1: 安装 mcp SDK 并验证环境

**Files:**
- 无需修改文件，仅验证环境

**Step 1: 安装 mcp SDK 到开发环境**

```bash
cd e:\personal\serpshot\serpshot-python
uv add --dev mcp
```

**Step 2: 验证安装成功**

```bash
python -c "import mcp; print(mcp.__version__)"
```

Expected: 打印出版本号，无报错

**Step 3: Commit**

```bash
git add uv.lock
git commit -m "chore: add mcp to dev dependencies for testing"
```

---

## Task 2: 新增 `serpshot/mcp.py`

**Files:**
- Create: `serpshot/mcp.py`

**Step 1: 创建 mcp.py**

```python
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
                # Format results as readable text
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

            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except SerpShotError as e:
        return [TextContent(type="text", text=f"Error: {e}")]


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

**Step 2: 验证语法无误**

```bash
cd e:\personal\serpshot\serpshot-python
python -c "import serpshot.mcp"
```

Expected: 无报错（如果 mcp 已安装）

**Step 3: Commit**

```bash
git add serpshot/mcp.py
git commit -m "feat: add MCP server module"
```

---

## Task 3: 新增 `serpshot/__main__.py` 支持 `python -m serpshot.mcp`

**Files:**
- Create: `serpshot/mcp_main.py`（实际上 mcp.py 末尾已有 `__main__` 块，直接验证即可）

**Step 1: 验证 `-m` 方式可以启动**

```bash
cd e:\personal\serpshot\serpshot-python
$env:SERPSHOT_API_KEY="test_key"
# 用 timeout 方式测试启动不报错（会等待 stdin，Ctrl+C 退出）
python -m serpshot.mcp
```

Expected: 进程启动，等待 stdin 输入（说明 server 正常运行），Ctrl+C 退出

---

## Task 4: 更新 `pyproject.toml`

**Files:**
- Modify: `pyproject.toml`

**Step 1: 更新 pyproject.toml**

在 `[project]` 的 `version` 改为 `0.2.0`，在 `[project.optional-dependencies]` 新增：

```toml
[project]
version = "0.2.0"

[project.optional-dependencies]
mcp = [
    "mcp>=1.0.0",
]
dev = [
    "pytest>=9.0.1",
    "pytest-asyncio>=1.3.0",
    "mypy>=1.18.2",
    "ruff>=0.14.6",
    "mcp>=1.0.0",
]
```

**Step 2: 验证安装命令可用**

```bash
pip install -e ".[mcp]"
python -c "from serpshot.mcp import app; print('OK')"
```

Expected: 打印 `OK`

**Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "feat: add mcp optional dependency, bump version to 0.2.0"
```

---

## Task 5: 更新 `__init__.py` 导出说明

**Files:**
- Modify: `serpshot/__init__.py`

**Step 1: 在 `__init__.py` 顶部 docstring 新增 MCP 使用说明**

在现有 docstring 末尾（`asyncio.run(main())` 那行之后）追加：

```python
    MCP server usage (requires pip install 'serpshot[mcp]'):
        Start the MCP server:
        $ python -m serpshot.mcp

        Claude Desktop config:
        {
          "mcpServers": {
            "serpshot": {
              "command": "python",
              "args": ["-m", "serpshot.mcp"],
              "env": { "SERPSHOT_API_KEY": "your_key" }
            }
          }
        }
```

**Step 2: Commit**

```bash
git add serpshot/__init__.py
git commit -m "docs: add MCP server usage to module docstring"
```

---

## Task 6: 发布新版本到 PyPI

**Step 1: 构建**

```bash
cd e:\personal\serpshot\serpshot-python
uv build
```

Expected: `dist/serpshot-0.2.0-py3-none-any.whl` 和 `dist/serpshot-0.2.0.tar.gz` 生成

**Step 2: 发布**

```bash
# 参考项目内的 publish.ps1 脚本
.\publish.ps1
# 或手动
uv publish
```

**Step 3: 验证 PyPI 上版本更新**

访问 https://pypi.org/project/serpshot/ 确认 0.2.0 已发布

---

## Task 7: 前端首页新增 `AISkillSection`

**Files:**
- Create: `e:\personal\serpshot\serpshot-frontend\components\ai-skill-section.tsx`
- Modify: `e:\personal\serpshot\serpshot-frontend\app\page.tsx`

**Step 1: 创建 `ai-skill-section.tsx`**

组件结构：
- 标题：`Integrate with Your AI Agent`
- 副标题：`Works with Cursor, Claude Desktop, and any MCP-compatible client`
- 两列卡片：
  - 左：Cursor Skill（ClawHub 链接 `https://clawhub.ai/downdawn/serpshot`）
  - 右：MCP Server（安装命令 + Claude Desktop 配置片段）
- 代码 Tab 切换：Tab1 ClawHub 安装步骤，Tab2 MCP 配置 JSON

参考现有组件风格（dark slate 背景，blue accent），与 `features-section.tsx` 保持一致。

**Step 2: 在 `page.tsx` 中插入**

在 `<FeaturesSection />` 和 `<UseCasesSection />` 之间插入：

```tsx
import { AISkillSection } from "@/components/ai-skill-section"
// ...
<FeaturesSection />
<AISkillSection />
<UseCasesSection />
```

**Step 3: 本地验证**

```bash
cd e:\personal\serpshot\serpshot-frontend
pnpm dev
```

访问 http://localhost:3000，确认新 section 正常显示

**Step 4: Commit**

```bash
git add components/ai-skill-section.tsx app/page.tsx
git commit -m "feat: add AISkillSection to homepage"
```

---

## Task 8: 更新 ClawHub Skill

**Files:**
- 在 ClawHub 网站上更新 `https://clawhub.ai/downdawn/serpshot` 的 SKILL.md

**改进点：**

1. 扩充触发词：加入 `find/lookup/research/搜索/查询/找一下`
2. 新增 `## Setup` 区块，说明一次性配置 API key
3. 补充完整 try/except 错误处理示例
4. 新增 credits 检查示例
5. 更新版本号

**Step 1: 更新后的 SKILL.md 关键改动**

```markdown
## When to Use
- User says: search / find / google / lookup / research / 查 / 搜 / 找 / 调研 / 查一下 / 搜索
- Need real-time web information
- Need image search results

## Setup (run once)
1. Get API key: https://serpshot.com/dashboard
2. Set env var: `SERPSHOT_API_KEY=your_key`
   Or export in shell: `export SERPSHOT_API_KEY=your_key`
```

**Step 2: 在 ClawHub 发布更新版本**
