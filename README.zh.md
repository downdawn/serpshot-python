# SerpShot Python SDK

[SerpShot API](https://www.serpshot.com) 的官方 Python 客户端 - 快速获取实时 Google 搜索结果。

[![Python Version](https://img.shields.io/pypi/pyversions/serpshot)](https://pypi.org/project/serpshot/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[English](README.md) | [中文文档](README.zh.md)

## 核心特性

- ⚡ **极速响应** - 1-2 秒内获取实时搜索结果
- 🌍 **全球覆盖** - 支持 200+ 国家和地区的本地化搜索
- 🔒 **稳定可靠** - 99.9% 正常运行时间保证，企业级安全
- 🚀 **开发友好** - 同步/异步双模式，完整类型提示，简单易用
- 🔄 **批量查询** - 单次请求支持 100 个查询，效率倍增
- 🛡️ **自动重试** - 内置智能重试机制，无需担心网络波动

## 安装

### 使用 pip

```bash
pip install serpshot
```

### 使用 uv

```bash
uv add serpshot
```

## 获取 API 密钥

免费使用，只需要[注册](https://www.serpshot.com/auth/register)即可获取您的 API 密钥。

## 快速开始

```python
from serpshot import SerpShot

with SerpShot(api_key="your-api-key") as client:
    response = client.search("Python 编程")
    for result in response.results:
        print(f"{result.title}: {result.link}")
```

设置 `SERPSHOT_API_KEY` 环境变量后可省略 `api_key` 参数：

```python
with SerpShot() as client:
    response = client.search("Python 编程")
```

异步：

```python
import asyncio
from serpshot import AsyncSerpShot

async def main():
    async with AsyncSerpShot() as client:
        response = await client.search("Python 编程")

asyncio.run(main())
```

## MCP 集成

SerpShot 内置 [MCP](https://modelcontextprotocol.io) 服务器，让 AI 助手（Claude、Cursor、Windsurf 等）可以直接将 Google 搜索作为工具调用。

### 安装 MCP 扩展

```bash
pip install 'serpshot[mcp]'
# 或
uv add 'serpshot[mcp]'
```

### 配置

在你的 MCP 客户端配置中添加以下内容（Claude Code、Cursor、Windsurf 等均适用）：

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

或使用 **uvx**（无需安装）：

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

### 可用 MCP 工具

| 工具 | 说明 |
|------|------|
| `google_search` | Google 搜索 — 返回自然结果，支持 `query`、`num`、`gl`、`hl` 参数 |
| `google_image_search` | Google 图片搜索 — 返回带缩略图和来源 URL 的图片结果 |

## API 参考

### SerpShot(api_key, base_url, timeout, max_retries)

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `api_key` | 环境变量 | API 密钥，自动读取 `SERPSHOT_API_KEY` |
| `base_url` | `None` | 自定义 API 端点 |
| `timeout` | `30.0` | 请求超时时间（秒） |
| `max_retries` | `3` | 最大重试次数 |

异步版本使用 `AsyncSerpShot`，接口完全相同，所有方法均为 awaitable。

### search(query, ...)

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `query` | 必填 | 查询字符串或字符串列表（最多 100 个） |
| `num` | `10` | 每页结果数（1–100） |
| `page` | `1` | 页码 |
| `gl` | `"us"` | 国家代码 |
| `hl` | `"en"` | 界面语言 |
| `lr` | — | 内容语言限制 |
| `location` | — | 本地搜索位置 |

`query` 为字符串时返回 `SearchResponse`，为列表时返回 `list[SearchResponse]`。

### image_search(query, ...)

参数与 `search()` 相同，不支持 `lr` 和 `location`。

### get_available_credits()

```python
with SerpShot() as client:
    print(client.get_available_credits())
```

### 响应模型

**SearchResponse**

| 字段 | 类型 | 说明 |
|------|------|------|
| `query` | `str` | 原始查询 |
| `total_results` | `str` | 估计总数（如 `"About 12,300,000 results"`） |
| `search_time` | `str` | 执行时间（秒） |
| `results` | `list` | `list[SearchResult]` 或 `list[ImageResult]` |
| `credits_used` | `int` | 消耗积分数 |

**SearchResult**：`title`、`link`、`snippet`、`position`

**ImageResult**：`title`、`link`、`thumbnail`、`source`、`source_link`、`width`、`height`、`position`

## 示例

### 批量搜索

```python
with SerpShot() as client:
    responses = client.search(["Python", "JavaScript", "Rust"], num=10)
    for r in responses:
        print(f"{r.query}: {r.results[0].title}")
```

### 错误处理

```python
from serpshot import SerpShot, AuthenticationError, RateLimitError, InsufficientCreditsError, APIError, NetworkError

try:
    with SerpShot() as client:
        response = client.search("测试查询")
except AuthenticationError:
    print("无效的 API 密钥")
except RateLimitError as e:
    print(f"超过速率限制，{e.retry_after} 秒后重试")
except InsufficientCreditsError as e:
    print(f"积分不足，需要 {e.credits_required}")
except (APIError, NetworkError) as e:
    print(f"错误: {e}")
```

SDK 会自动使用指数退避处理速率限制，通过 `response.credits_used` 跟踪积分消耗。

## 开发

```bash
git clone https://github.com/downdawn/serpshot-python.git
cd serpshot-python
uv sync --dev
pytest
```

## 许可证

MIT — 详见 [LICENSE](LICENSE)。

## 支持

- 📧 support@serpshot.com
- 📖 [文档](https://www.serpshot.com/docs)
- 🐛 [问题反馈](https://github.com/downdawn/serpshot-python/issues)
- 🔑 [获取 API 密钥](https://www.serpshot.com/dashboard/api-keys)
