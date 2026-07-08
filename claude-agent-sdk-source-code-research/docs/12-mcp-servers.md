# MCP 服务器集成

MCP（Model Context Protocol）是扩展 Agent 工具能力的标准协议。SDK 支持连接多种类型的 MCP 服务器，使 Agent 能够调用外部系统的工具。

## MCP 服务器类型

SDK 支持 4 种 MCP 服务器配置：

| 类型 | 类名 | 传输方式 | 适用场景 |
|------|------|---------|---------|
| SDK | `McpSdkServerConfig` | 进程内 | Python 实现的 MCP 服务器 |
| Stdio | `McpStdioServerConfig` | 标准输入/输出 | 命令行工具 |
| SSE | `McpSSEServerConfig` | Server-Sent Events | 远程 HTTP 服务 |
| HTTP | `McpHttpServerConfig` | HTTP Streamable | 远程 HTTP 服务（新协议） |

## McpSdkServerConfig — 进程内 SDK 服务器

通过 `create_sdk_mcp_server()` 创建的 Python 进程内 MCP 服务器，零网络开销：

```python
from claude_agent_sdk import ClaudeAgentOptions, create_sdk_mcp_server

# 定义工具处理函数
async def get_weather(city: str) -> str:
    """获取城市天气"""
    return f"{city} 今天晴，25°C"

async def search_database(query: str, limit: int = 10) -> list[dict]:
    """搜索数据库"""
    # 实际实现...
    return [{"id": 1, "name": "result"}]

# 创建 SDK MCP 服务器
weather_server = create_sdk_mcp_server(
    name="weather",
    tools={
        "get_weather": {
            "description": "获取指定城市的天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称"}
                },
                "required": ["city"],
            },
            "handler": get_weather,
        },
        "search_database": {
            "description": "搜索数据库",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "default": 10},
                },
                "required": ["query"],
            },
            "handler": search_database,
        },
    },
)

options = ClaudeAgentOptions(
    mcp_servers={
        "weather": weather_server,  # type="sdk"
    },
)
```

## McpStdioServerConfig — 标准输入/输出

通过子进程的 stdin/stdout 与 MCP 服务器通信：

```python
from claude_agent_sdk import ClaudeAgentOptions, McpStdioServerConfig

options = ClaudeAgentOptions(
    mcp_servers={
        "filesystem": McpStdioServerConfig(
            type="stdio",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp/workspace"],
            env={"NODE_ENV": "production"},  # 可选：环境变量
            cwd="/tmp/workspace",            # 可选：工作目录
        ),
        "github": McpStdioServerConfig(
            type="stdio",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-github"],
            env={"GITHUB_TOKEN": "ghp_xxx"},
        ),
        "sqlite": McpStdioServerConfig(
            type="stdio",
            command="uvx",
            args=["mcp-server-sqlite", "--db-path", "/tmp/test.db"],
        ),
    },
)
```

## McpSSEServerConfig — Server-Sent Events

通过 SSE（Server-Sent Events）连接远程 MCP 服务器：

```python
from claude_agent_sdk import ClaudeAgentOptions, McpSSEServerConfig

options = ClaudeAgentOptions(
    mcp_servers={
        "remote_api": McpSSEServerConfig(
            type="sse",
            url="https://mcp.example.com/sse",
            headers={                        # 可选：请求头
                "Authorization": "Bearer token_xxx",
                "X-Custom-Header": "value",
            },
        ),
    },
)
```

## McpHttpServerConfig — HTTP Streamable

通过 HTTP Streamable Transport 连接远程 MCP 服务器（MCP 协议的新版传输方式）：

```python
from claude_agent_sdk import ClaudeAgentOptions, McpHttpServerConfig

options = ClaudeAgentOptions(
    mcp_servers={
        "modern_api": McpHttpServerConfig(
            type="http",
            url="https://mcp.example.com/mcp",
            headers={
                "Authorization": "Bearer token_xxx",
            },
        ),
    },
)
```

## 通过 .mcp.json 文件配置

可以指定 `.mcp.json` 配置文件路径，复用已有的 MCP 配置：

```python
options = ClaudeAgentOptions(
    mcp_servers="/path/to/.mcp.json",  # 字符串路径
)
```

`.mcp.json` 文件格式：

```json
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
    },
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_xxx"
      }
    }
  }
}
```

## strict_mcp_config — 严格模式

默认情况下，SDK 会加载项目目录中的 `.mcp.json` 和 Claude 设置中的 MCP 配置。设置 `strict_mcp_config=True` 可以忽略所有外部 MCP 源，仅使用代码中明确配置的服务器：

```python
options = ClaudeAgentOptions(
    mcp_servers={
        "my_server": McpStdioServerConfig(...),
    },
    strict_mcp_config=True,  # 忽略 .mcp.json 和 Claude 设置中的 MCP 配置
)
```

## 工具命名规则

MCP 服务器提供的工具在 Agent 中以固定格式命名：

```
mcp__<server_name>__<tool_name>
```

例如：
- `mcp__github__create_issue` — github 服务器的 create_issue 工具
- `mcp__filesystem__read_file` — filesystem 服务器的 read_file 工具
- `mcp__weather__get_weather` — weather 服务器的 get_weather 工具

在 `allowed_tools` 和 `disallowed_tools` 中使用此命名：

```python
options = ClaudeAgentOptions(
    mcp_servers={"github": McpStdioServerConfig(...)},
    allowed_tools=[
        "mcp__github__*",            # 允许 github 的所有工具
        "mcp__github__create_issue", # 或精确允许某个工具
    ],
    disallowed_tools=[
        "mcp__github__delete_repo",  # 禁止删除仓库
    ],
)
```

## MCP 状态管理

### 获取 MCP 状态

```python
async with ClaudeSDKClient(options) as client:
    status = client.get_mcp_status()
    # 返回 McpStatusResponse

    for server_name, server_info in status.servers.items():
        print(f"Server: {server_name}")
        print(f"  Status: {server_info.status}")  # "connected" / "disconnected" / "error"
        print(f"  Tools: {[t.name for t in server_info.tools]}")
```

### 重连 MCP 服务器

```python
# 当 MCP 服务器断开时，可以尝试重连
await client.reconnect_mcp_server("github")
```

### 启用/禁用 MCP 服务器

```python
# 临时禁用某个 MCP 服务器
await client.toggle_mcp_server("github", enabled=False)

# 重新启用
await client.toggle_mcp_server("github", enabled=True)
```

## MCP 类型定义

### McpToolInfo

```python
class McpToolInfo(TypedDict):
    name: str              # 工具名称（不含 mcp__ 前缀）
    description: str       # 工具描述
    input_schema: dict     # JSON Schema 格式的参数定义
    annotations: McpToolAnnotations | None  # 工具注解
```

### McpToolAnnotations

```python
class McpToolAnnotations(TypedDict, total=False):
    title: str            # 工具显示标题
    readOnlyHint: bool    # 是否为只读工具
    destructiveHint: bool # 是否为破坏性工具
    idempotentHint: bool  # 是否幂等
    openWorldHint: bool   # 是否访问外部世界
```

### McpServerInfo

```python
class McpServerInfo(TypedDict):
    status: str           # "connected" | "disconnected" | "error"
    tools: list[McpToolInfo]
    error: str | None     # 错误信息（status="error" 时）
```

## Tool Search（工具搜索）

当 MCP 服务器提供大量工具时（如 100+ 个工具），全部加载会消耗大量 token。Tool Search 功能允许 Agent 按需搜索和发现工具：

```python
import os

# 通过环境变量启用 Tool Search
os.environ["ENABLE_TOOL_SEARCH"] = "1"

options = ClaudeAgentOptions(
    mcp_servers={
        "large_api": McpStdioServerConfig(
            type="stdio",
            command="my-large-api-server",
            args=[],
        ),
    },
    env={"ENABLE_TOOL_SEARCH": "1"},  # 或通过 options 传递
)
```

启用 Tool Search 后，Agent 不会在启动时加载所有工具描述，而是获得一个搜索工具，按需查找所需的具体工具。

## 完整示例

```python
import anyio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    McpStdioServerConfig,
    McpSSEServerConfig,
    create_sdk_mcp_server,
    AssistantMessage,
    TextBlock,
)

# 1. 创建进程内 MCP 服务器
async def query_tickets(status: str = "open") -> list[dict]:
    """查询工单"""
    return [
        {"id": "T-001", "title": "登录失败", "status": status},
        {"id": "T-002", "title": "页面崩溃", "status": status},
    ]

ticket_server = create_sdk_mcp_server(
    name="tickets",
    tools={
        "query_tickets": {
            "description": "查询工单列表",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["open", "closed", "all"],
                        "default": "open",
                    }
                },
            },
            "handler": query_tickets,
        },
    },
)

async def main():
    options = ClaudeAgentOptions(
        prompt="你是一个 DevOps 助手，可以管理 GitHub 仓库和查询内部工单系统。",
        mcp_servers={
            # 进程内 SDK 服务器
            "tickets": ticket_server,
            # Stdio 服务器
            "github": McpStdioServerConfig(
                type="stdio",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-github"],
                env={"GITHUB_TOKEN": "ghp_xxx"},
            ),
            # 远程 SSE 服务器
            "monitoring": McpSSEServerConfig(
                type="sse",
                url="https://monitoring.internal.com/mcp/sse",
                headers={"Authorization": "Bearer internal_token"},
            ),
        },
        allowed_tools=[
            "mcp__tickets__*",        # 允许工单系统所有操作
            "mcp__github__*",         # 允许 GitHub 所有操作
            "mcp__monitoring__query", # 只允许监控系统的查询
        ],
        disallowed_tools=[
            "mcp__github__delete_repo",  # 禁止删除仓库
        ],
        strict_mcp_config=True,  # 不加载外部 MCP 配置
        permission_mode="bypassPermissions",
    )

    async with ClaudeSDKClient(options) as client:
        await client.query("查看当前打开的工单，并检查 GitHub 上最近的 PR")

        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

        # 查看 MCP 状态
        status = client.get_mcp_status()
        for name, info in status.servers.items():
            print(f"\n[{name}] Status: {info.status}, Tools: {len(info.tools)}")

anyio.run(main)
```

## 注意事项

- Stdio 类型的 MCP 服务器由 SDK 管理子进程生命周期，客户端关闭时自动清理
- SSE 和 HTTP 类型需要确保远程服务器可达
- SDK 类型（进程内）性能最优，无网络开销，推荐用于 Python 实现的工具
- `strict_mcp_config=True` 在安全敏感场景下推荐使用，避免加载未知的 MCP 配置
- MCP 服务器名称不能包含双下划线 `__`，因为这是工具命名的分隔符
- 单个 MCP 服务器重连失败不会影响其他服务器和 Agent 的正常运行
