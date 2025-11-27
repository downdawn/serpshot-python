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

## API 端点

SDK 使用以下 SerpShot API 端点：

- **主搜索**: `/api/search/google` - 用于常规搜索和图片搜索

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

### 同步使用

```python
from serpshot import SerpShot

# 初始化客户端（API 密钥可以显式提供或从 SERPSHOT_API_KEY 环境变量读取）
client = SerpShot(api_key="your-api-key")

# 执行搜索
response = client.search("Python 编程")

# 处理结果
for result in response.results:
    print(f"{result.title}: {result.link}")

# 清理资源
client.close()
```

### 使用上下文管理器（推荐）

```python
from serpshot import SerpShot

with SerpShot(api_key="your-api-key") as client:
    response = client.search("Python 编程")
    print(f"找到 {len(response.results)} 条结果")
```

### 异步使用

```python
import asyncio
from serpshot import AsyncSerpShot

async def main():
    async with AsyncSerpShot(api_key="your-api-key") as client:
        response = await client.search("Python 编程")
        print(f"找到 {len(response.results)} 条结果")

asyncio.run(main())
```

### 使用环境变量

您可以通过 `SERPSHOT_API_KEY` 环境变量设置 API 密钥，这样就无需在代码中显式传递：

```bash
export SERPSHOT_API_KEY="your-api-key"
```

```python
from serpshot import SerpShot

# API 密钥会自动从环境变量读取
with SerpShot() as client:
    response = client.search("Python 编程")
```

## API 参考

### SerpShot 客户端

#### 初始化

```python
from serpshot import SerpShot

client = SerpShot(
    api_key="your-api-key",      # 可选：您的 SerpShot API 密钥（或设置 SERPSHOT_API_KEY 环境变量）
    base_url=None,                # 可选：自定义 API 端点
    timeout=30.0,                 # 可选：请求超时时间（秒）
    max_retries=3,                # 可选：最大重试次数
)
```

#### search()

执行 Google 搜索。支持单个查询和批量查询（每次请求最多 100 个查询）。

```python
from serpshot import SerpShot

# 单个搜索
response = client.search(
    query="搜索查询",              # 必需：搜索查询字符串或查询列表（最多 100 个）
    num=10,                       # 可选：每页结果数量 (1-100)
    page=1,                       # 可选：页码（从 1 开始）
    gl="us",                      # 可选：国家代码（如 'us', 'uk', 'cn'）
    hl="en",                      # 可选：语言代码（如 'en', 'zh-CN'）
    lr="en",                      # 可选：内容语言限制（如 'en', 'zh-CN'）
    location="US",                # 可选：本地搜索位置（如 'US', 'GB', 'CN'）
)

# 批量搜索（推荐用于多个查询）
responses = client.search(
    query=["Python", "JavaScript", "Rust"],  # 查询列表（1-100 个）
    num=10,
    gl="us",
    location="US",               # 支持字符串形式的位置参数
)
# 当 query 是列表时，返回 list[SearchResponse]
```

**提示**：`location` 参数支持字符串（推荐）或 `LocationType` 枚举两种方式。

#### image_search()

执行 Google 图片搜索。支持单个查询和批量查询（每次请求最多 100 个查询）。

```python
# 单个图片搜索
response = client.image_search(
    query="可爱的小狗",            # 必需：图片搜索查询字符串或列表（最多 100 个）
    num=10,                       # 可选：每页结果数量 (1-100)
    page=1,                       # 可选：页码（从 1 开始）
    gl="us",                      # 可选：国家代码
    hl="en",                      # 可选：语言代码
    lr="en",                      # 可选：内容语言限制
)

# 批量图片搜索
responses = client.image_search(
    query=["猫", "狗", "鸟"],      # 查询列表（1-100 个）
    num=10,
)
```

### 响应模型

`SearchResponse` 对象包含：

```python
class SearchResponse:
    success: bool                 # 请求成功状态
    query: str                    # 原始搜索查询
    total_results: str            # 总结果数估计（如 "About 12,300,000 results"）
    search_time: str              # 搜索执行时间（秒，字符串格式）
    results: list[SearchResult] | list[ImageResult]  # 搜索结果列表
    credits_used: int             # 消耗的积分
```

**注意**：使用批量搜索（传入查询列表）时，`search()` 返回 `list[SearchResponse]` 而不是单个 `SearchResponse`。

### 搜索结果模型

`response.results` 中的每个结果包含：

```python
class SearchResult:
    title: str                    # 结果标题
    link: str                     # 结果 URL
    snippet: str                  # 描述片段
    position: int                 # 结果位置（从 1 开始）
```

### 图片结果模型

图片搜索的结果包含：

```python
class ImageResult:
    title: str                    # 图片标题
    link: str                     # 图片源 URL
    thumbnail: str                # 缩略图 URL
    source: str                   # 来源网站
    source_link: str              # 来源页面 URL
    width: int                    # 图片宽度（像素）
    height: int                   # 图片高度（像素）
    position: int                 # 结果位置
```

## 高级示例

### 批量搜索

使用批量搜索可以在一次 API 调用中处理多个查询（最多 100 个），比分别调用更高效：

```python
from serpshot import SerpShot

with SerpShot(api_key="your-api-key") as client:
    queries = ["Python", "JavaScript", "Rust", "Go"]
    responses = client.search(queries, num=10)  # 返回 list[SearchResponse]
    
    for query, response in zip(queries, responses):
        print(f"{query}: {len(response.results)} 条结果")
        if response.results:
            print(f"  最佳结果: {response.results[0].title}\n")
```

### 分页

```python
from serpshot import SerpShot

with SerpShot(api_key="your-api-key") as client:
    page1 = client.search("Python", num=10, page=1)
    page2 = client.search("Python", num=10, page=2)
    page3 = client.search("Python", num=10, page=3)
```

### 异步批量搜索

```python
import asyncio
from serpshot import AsyncSerpShot

async def main():
    async with AsyncSerpShot(api_key="your-api-key") as client:
        queries = ["Python", "JavaScript", "Rust"]
        responses = await client.search(queries, num=10)
        for response in responses:
            print(f"找到 {len(response.results)} 条结果")

asyncio.run(main())
```

### 错误处理

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
        response = client.search("测试查询")
except AuthenticationError as e:
    print(f"无效的 API 密钥: {e}")
except RateLimitError as e:
    print(f"超过速率限制。请在 {e.retry_after} 秒后重试")
except InsufficientCreditsError as e:
    print(f"积分不足。需要: {e.credits_required}")
except APIError as e:
    print(f"API 错误 ({e.status_code}): {e.message}")
except NetworkError as e:
    print(f"网络错误: {e}")
```

### 自定义配置

```python
client = SerpShot(
    api_key="your-api-key",
    timeout=60.0,        # 更长的超时时间，适用于慢速连接
    max_retries=5,       # 更多重试次数，提高可靠性
)
```

## 获取可用积分

```python
from serpshot import SerpShot

with SerpShot(api_key="your-api-key") as client:
    credits = client.get_available_credits()
    print(f"可用积分: {credits}")
```

## 速率限制

请参考您的 SerpShot 账户仪表板了解速率限制信息。SDK 会自动使用指数退避处理速率限制。

## 积分成本

不同的搜索操作消耗不同数量的积分。

使用 `response.credits_used` 字段跟踪每次请求的实际积分消耗。

## 开发

### 设置

```bash
# 克隆仓库
git clone https://github.com/downdawn/serpshot-python.git
cd serpshot-python

# 使用 uv 安装开发依赖
uv sync --dev

# 或使用 pip
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 类型检查

```bash
mypy serpshot
```

### 代码检查

```bash
ruff check serpshot
```

## 示例

查看 [examples](examples/) 目录了解更多使用示例：

- [sync_example.py](examples/sync_example.py) - 同步使用示例
- [async_example.py](examples/async_example.py) - 异步使用示例

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

## 支持

- 📧 邮箱: support@serpshot.com
- 📖 文档: https://www.serpshot.com/docs
- 🐛 问题反馈: https://github.com/downdawn/serpshot-python/issues

## 链接

- [SerpShot 网站](https://www.serpshot.com)
- [API 文档](https://www.serpshot.com/docs)
- [获取 API 密钥](https://www.serpshot.com/dashboard/api-keys)

