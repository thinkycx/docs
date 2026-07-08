---
create: 2026-07-07
update: 2026-07-07
author: thinkycx
title: 【译】Agent SDK - Python 参考
description: Claude Agent SDK Python 版完整参考，涵盖 query() 函数与 ClaudeSDKClient 类的对比选择、所有 API 函数签名与参数、Options/Transport/Hook 等核心类、Type 定义（权限、工具、MCP 配置等），以及 Message 类型体系。
category: translation
tags: [claude-code, agent-sdk, python, reference, translation]
refs:
  - https://code.claude.com/docs/en/agent-sdk/python.md
---

# Agent SDK 参考文档 - Python（完整文档）

## 安装

```bash
pip install claude-agent-sdk
```

## 选择 `query()` 还是 `ClaudeSDKClient`

### 快速对比

**两种接口各有侧重，根据场景选择即可。**

| 特性 | `query()` | `ClaudeSDKClient` |
|:---|:---|:---|
| **会话模式** | 默认每次创建新会话 | 复用同一会话 |
| **对话深度** | 单轮交互 | 同一上下文中多轮交互 |
| **连接管理** | 自动管理 | 手动控制 |
| **流式输入** | ✅ 支持 | ✅ 支持 |
| **中断能力** | ❌ 不支持 | ✅ 支持 |
| **Hooks** | ✅ 支持 | ✅ 支持 |
| **自定义工具** | ✅ 支持 | ✅ 支持 |
| **继续对话** | 需手动通过 `continue_conversation` 或 `resume` | ✅ 自动 |
| **适用场景** | 一次性任务 | 持续性对话 |

### 何时使用 `query()`（一次性任务）

**适合不需要上下文延续的独立任务。**

* 不需要对话历史的一次性提问
* 无需依赖前序交互上下文的独立任务
* 简单的自动化脚本
* 每次都想从零开始的场景

### 何时使用 `ClaudeSDKClient`（持续对话）

**适合需要多轮交互、上下文累积的应用场景。**

* **延续对话** - 需要 Claude 记住先前上下文
* **追问** - 在前序回答基础上追加提问
* **交互式应用** - 聊天界面、REPL 环境
* **响应驱动逻辑** - 下一步操作取决于 Claude 的回答
* **会话控制** - 显式管理对话生命周期

## 函数

### `query()`

**默认为每次交互创建新会话，返回异步迭代器逐条产出消息。**

```python
async def query(
    *,
    prompt: str | AsyncIterable[dict[str, Any]],
    options: ClaudeAgentOptions | None = None,
    transport: Transport | None = None
) -> AsyncIterator[Message]
```

#### 参数

| 参数 | 类型 | 说明 |
|:---|:---|:---|
| `prompt` | <code>str | AsyncIterable[dict]</code> | 输入提示词，可以是字符串或异步可迭代对象（流式模式） |
| `options` | <code>ClaudeAgentOptions | None</code> | 可选配置对象（为 `None` 时使用 `ClaudeAgentOptions()` 默认值） |
| `transport` | <code>Transport | None</code> | 可选的自定义传输层，用于与 CLI 进程通信 |

#### 返回值

返回 `AsyncIterator[Message]`，逐条产出对话中的消息。

#### 示例 - 带配置项

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    options = ClaudeAgentOptions(
        system_prompt="You are an expert Python developer",
        permission_mode="acceptEdits",
        cwd="/home/user/project",
    )

    async for message in query(prompt="Create a Python web server", options=options):
        print(message)


asyncio.run(main())
```

### `tool()`

**用于定义 MCP 工具的装饰器，提供类型安全。**

```python
def tool(
    name: str,
    description: str,
    input_schema: type | dict[str, Any],
    annotations: ToolAnnotations | None = None
) -> Callable[[Callable[[Any], Awaitable[dict[str, Any]]]], SdkMcpTool[Any]]
```

#### 参数

| 参数 | 类型 | 说明 |
|:---|:---|:---|
| `name` | `str` | 工具的唯一标识符 |
| `description` | `str` | 人类可读的工具功能描述 |
| `input_schema` | <code>type | dict[str, Any]</code> | 定义工具输入参数的 Schema（详见下方） |
| `annotations` | <code>ToolAnnotations | None</code> | 可选的 MCP 工具注解，向客户端提供行为提示 |

#### 输入 Schema 的两种写法

**1. 简单类型映射**（推荐）：

```python
{"text": str, "count": int, "enabled": bool}
```

**2. JSON Schema 格式**（适合复杂校验）：

```python
{
    "type": "object",
    "properties": {
        "text": {"type": "string"},
        "count": {"type": "integer", "minimum": 0},
    },
    "required": ["text"],
}
```

#### 返回值

返回一个装饰器函数，将工具实现包装为 `SdkMcpTool` 实例。

#### 示例

```python
from claude_agent_sdk import tool
from typing import Any


@tool("greet", "Greet a user", {"name": str})
async def greet(args: dict[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Hello, {args['name']}!"}]}
```

#### `ToolAnnotations`

**工具行为注解，所有字段均为可选提示，客户端不应依赖其做安全决策。**

从 `mcp.types` 重新导出（也可通过 `from claude_agent_sdk import ToolAnnotations` 导入）。

| 字段 | 类型 | 默认值 | 说明 |
|:---|:---|:---|:---|
| `title` | <code>str | None</code> | `None` | 工具的人类可读标题 |
| `readOnlyHint` | <code>bool | None</code> | `False` | 若为 `True`，表示该工具不会修改其环境 |
| `destructiveHint` | <code>bool | None</code> | `True` | 若为 `True`，表示该工具可能执行破坏性更新（仅在 `readOnlyHint` 为 `False` 时有意义） |
| `idempotentHint` | <code>bool | None</code> | `False` | 若为 `True`，表示相同参数重复调用不会产生额外影响（仅在 `readOnlyHint` 为 `False` 时有意义） |
| `openWorldHint` | <code>bool | None</code> | `True` | 若为 `True`，表示该工具会与外部实体交互（如网络搜索）。若为 `False`，表示工具的作用域是封闭的（如记忆工具） |

```python
from claude_agent_sdk import tool, ToolAnnotations
from typing import Any


@tool(
    "search",
    "Search the web",
    {"query": str},
    annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
)
async def search(args: dict[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Results for: {args['query']}"}]}
```

### `create_sdk_mcp_server()`

**创建进程内 MCP 服务器，运行在你的 Python 应用内部。**

```python
def create_sdk_mcp_server(
    name: str,
    version: str = "1.0.0",
    tools: list[SdkMcpTool[Any]] | None = None
) -> McpSdkServerConfig
```

#### 参数

| 参数 | 类型 | 默认值 | 说明 |
|:---|:---|:---|:---|
| `name` | `str` | - | 服务器的唯一标识符 |
| `version` | `str` | `"1.0.0"` | 服务器版本号 |
| `tools` | <code>list[SdkMcpTool[Any]] | None</code> | `None` | 通过 `@tool` 装饰器创建的工具函数列表 |

#### 返回值

返回 `McpSdkServerConfig` 对象，可传入 `ClaudeAgentOptions.mcp_servers`。

#### 示例

```python
from claude_agent_sdk import tool, create_sdk_mcp_server


@tool("add", "Add two numbers", {"a": float, "b": float})
async def add(args):
    return {"content": [{"type": "text", "text": f"Sum: {args['a'] + args['b']}"}]}


@tool("multiply", "Multiply two numbers", {"a": float, "b": float})
async def multiply(args):
    return {"content": [{"type": "text", "text": f"Product: {args['a'] * args['b']}"}]}


calculator = create_sdk_mcp_server(
    name="calculator",
    version="2.0.0",
    tools=[add, multiply],  # Pass decorated functions
)

# Use with Claude
options = ClaudeAgentOptions(
    mcp_servers={"calc": calculator},
    allowed_tools=["mcp__calc__add", "mcp__calc__multiply"],
)
```

### `list_sessions()`

**列出历史会话及其元数据，可按项目目录筛选。同步函数，立即返回。**

```python
def list_sessions(
    directory: str | None = None,
    limit: int | None = None,
    include_worktrees: bool = True
) -> list[SDKSessionInfo]
```

#### 参数

| 参数 | 类型 | 默认值 | 说明 |
|:---|:---|:---|:---|
| `directory` | <code>str | None</code> | `None` | 要列出会话的目录。省略时返回所有项目的会话 |
| `limit` | <code>int | None</code> | `None` | 最多返回的会话数量 |
| `include_worktrees` | `bool` | `True` | 当 `directory` 位于 git 仓库内时，是否包含所有 worktree 路径的会话 |

#### 返回类型：`SDKSessionInfo`

| 属性 | 类型 | 说明 |
|:---|:---|:---|
| `session_id` | `str` | 会话唯一标识符 |
| `summary` | `str` | 显示标题：自定义标题、自动生成摘要或首条提示词 |
| `last_modified` | `int` | 最后修改时间（毫秒级 Unix 时间戳） |
| `file_size` | <code>int | None</code> | 会话文件大小（字节）。远程存储后端返回 `None` |
| `custom_title` | <code>str | None</code> | 用户自定义的会话标题 |
| `first_prompt` | <code>str | None</code> | 会话中首条有意义的用户提示词 |
| `git_branch` | <code>str | None</code> | 会话结束时的 Git 分支 |
| `cwd` | <code>str | None</code> | 会话的工作目录 |
| `tag` | <code>str | None</code> | 用户设置的会话标签 |
| `created_at` | <code>int | None</code> | 会话创建时间（毫秒级 Unix 时间戳） |

#### 示例

```python
from claude_agent_sdk import list_sessions

for session in list_sessions(directory="/path/to/project", limit=10):
    print(f"{session.summary} ({session.session_id})")
```

### `get_session_messages()`

**获取历史会话中的消息记录。同步函数，立即返回。**

```python
def get_session_messages(
    session_id: str,
    directory: str | None = None,
    limit: int | None = None,
    offset: int = 0
) -> list[SessionMessage]
```

#### 参数

| 参数 | 类型 | 默认值 | 说明 |
|:---|:---|:---|:---|
| `session_id` | `str` | 必填 | 要获取消息的会话 ID |
| `directory` | <code>str | None</code> | `None` | 要搜索的项目目录。省略时搜索所有项目 |
| `limit` | <code>int | None</code> | `None` | 最多返回的消息数量 |
| `offset` | `int` | `0` | 从开头跳过的消息数量 |

#### 返回类型：`SessionMessage`

| 属性 | 类型 | 说明 |
|:---|:---|:---|
| `type` | `Literal["user", "assistant"]` | 消息角色 |
| `uuid` | `str` | 消息唯一标识符 |
| `session_id` | `str` | 所属会话标识符 |
| `message` | `Any` | 原始消息内容 |
| `parent_tool_use_id` | `None` | 保留字段，供未来使用 |

#### 示例

```python
from claude_agent_sdk import list_sessions, get_session_messages

sessions = list_sessions(limit=1)
if sessions:
    messages = get_session_messages(sessions[0].session_id)
    for msg in messages:
        print(f"[{msg.type}] {msg.uuid}")
```

### `get_session_info()`

**按 ID 读取单个会话的元数据，无需扫描整个项目目录。同步函数，立即返回。**

```python
def get_session_info(
    session_id: str,
    directory: str | None = None,
) -> SDKSessionInfo | None
```

#### 参数

| 参数 | 类型 | 默认值 | 说明 |
|:---|:---|:---|:---|
| `session_id` | `str` | 必填 | 要查找的会话 UUID |
| `directory` | <code>str | None</code> | `None` | 项目目录路径。省略时搜索所有项目目录 |

返回 `SDKSessionInfo`；未找到时返回 `None`。

#### 示例

```python
from claude_agent_sdk import get_session_info

info = get_session_info("550e8400-e29b-41d4-a716-446655440000")
if info:
    print(f"{info.summary} (branch: {info.git_branch}, tag: {info.tag})")
```

### `rename_session()`

**重命名会话，通过追加自定义标题条目实现。可安全重复调用，以最后一次为准。同步函数。**

```python
def rename_session(
    session_id: str,
    title: str,
    directory: str | None = None,
) -> None
```

#### 参数

| 参数 | 类型 | 默认值 | 说明 |
|:---|:---|:---|:---|
| `session_id` | `str` | 必填 | 要重命名的会话 UUID |
| `title` | `str` | 必填 | 新标题。去除首尾空白后不能为空 |
| `directory` | <code>str | None</code> | `None` | 项目目录路径。省略时搜索所有项目目录 |

当 `session_id` 不是有效 UUID 或 `title` 为空时抛出 `ValueError`；找不到会话时抛出 `FileNotFoundError`。

#### 示例

```python
from claude_agent_sdk import list_sessions, rename_session

sessions = list_sessions(directory="/path/to/project", limit=1)
if sessions:
    rename_session(sessions[0].session_id, "Refactor auth module")
```

### `tag_session()`

**为会话添加标签。传入 `None` 可清除标签。可安全重复调用，以最后一次为准。同步函数。**

```python
def tag_session(
    session_id: str,
    tag: str | None,
    directory: str | None = None,
) -> None
```

#### 参数

| 参数 | 类型 | 默认值 | 说明 |
|:---|:---|:---|:---|
| `session_id` | `str` | 必填 | 要添加标签的会话 UUID |
| `tag` | <code>str | None</code> | 必填 | 标签字符串，或 `None` 以清除。存储前会进行 Unicode 清理 |
| `directory` | <code>str | None</code> | `None` | 项目目录路径。省略时搜索所有项目目录 |

当 `session_id` 不是有效 UUID 或 `tag` 在清理后为空时抛出 `ValueError`；找不到会话时抛出 `FileNotFoundError`。

#### 示例

```python
from claude_agent_sdk import list_sessions, tag_session

# Tag a session
tag_session("550e8400-e29b-41d4-a716-446655440000", "needs-review")

# Later: find all sessions with that tag
for session in list_sessions(directory="/path/to/project"):
    if session.tag == "needs-review":
        print(session.summary)
```
## 类（Classes）

### `ClaudeSDKClient`

**维持跨多次交互的会话状态，是 SDK 的核心客户端类。**

#### 核心特性

* **会话连续性**：多次调用 `query()` 时自动维护对话上下文
* **同一对话**：会话保留之前的所有消息
* **中断支持**：可以在任务执行中途停止
* **显式生命周期**：由你控制会话的开始和结束时机
* **响应驱动流程**：可根据响应内容发送后续提问
* **自定义工具与钩子**：支持通过 `@tool` 装饰器创建的自定义工具，以及钩子机制

```python
class ClaudeSDKClient:
    def __init__(self, options: ClaudeAgentOptions | None = None, transport: Transport | None = None)
    async def connect(self, prompt: str | AsyncIterable[dict] | None = None) -> None
    async def query(self, prompt: str | AsyncIterable[dict], session_id: str = "default") -> None
    async def receive_messages(self) -> AsyncIterator[Message]
    async def receive_response(self) -> AsyncIterator[Message]
    async def interrupt(self) -> None
    async def set_permission_mode(self, mode: str) -> None
    async def set_model(self, model: str | None = None) -> None
    async def rewind_files(self, user_message_id: str) -> None
    async def get_mcp_status(self) -> McpStatusResponse
    async def reconnect_mcp_server(self, server_name: str) -> None
    async def toggle_mcp_server(self, server_name: str, enabled: bool) -> None
    async def stop_task(self, task_id: str) -> None
    async def get_server_info(self) -> dict[str, Any] | None
    async def disconnect(self) -> None
```

#### 方法列表

| 方法 | 说明 |
|:---|:---|
| `__init__(options)` | 使用可选配置初始化客户端 |
| `connect(prompt)` | 连接 Claude，可附带初始提示词或消息流 |
| `query(prompt, session_id)` | 以流式模式发送新请求 |
| `receive_messages()` | 以异步迭代器形式接收 Claude 的所有消息 |
| `receive_response()` | 接收消息直到收到 ResultMessage（包含该消息本身） |
| `interrupt()` | 发送中断信号（仅在流式模式下有效） |
| `set_permission_mode(mode)` | 更改当前会话的权限模式 |
| `set_model(model)` | 更改当前会话使用的模型。传 `None` 可重置为默认模型 |
| `rewind_files(user_message_id)` | 将文件恢复到指定用户消息时的状态。需要 `enable_file_checkpointing=True` |
| `get_mcp_status()` | 获取所有已配置 MCP 服务器的状态。返回 `McpStatusResponse` |
| `reconnect_mcp_server(server_name)` | 重新连接已失败或断开的 MCP 服务器 |
| `toggle_mcp_server(server_name, enabled)` | 在会话进行中启用或禁用某个 MCP 服务器。禁用后其工具将被移除 |
| `stop_task(task_id)` | 停止正在运行的后台任务。随后消息流中会出现 status 为 `"stopped"` 的 `TaskNotificationMessage` |
| `get_server_info()` | 获取服务器信息，包括会话 ID 和能力描述 |
| `disconnect()` | 断开与 Claude 的连接 |

#### 上下文管理器支持

```python
async with ClaudeSDKClient() as client:
    await client.query("Hello Claude")
    async for message in client.receive_response():
        print(message)
```

> **注意：** 迭代消息时，请避免使用 `break` 提前退出，否则可能导致 asyncio 清理问题。建议让迭代自然完成，或使用标志变量追踪是否已获取所需内容。

#### 示例 - 多轮对话

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock, ResultMessage


async def main():
    async with ClaudeSDKClient() as client:
        # 第一个问题
        await client.query("What's the capital of France?")

        # 处理响应
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

        # 追问 - 会话保留了之前的上下文
        await client.query("What's the population of that city?")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

        # 继续追问 - 仍在同一对话中
        await client.query("What are some famous landmarks there?")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")


asyncio.run(main())
```

#### 示例 - 使用 ClaudeSDKClient 进行流式输入

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient


async def message_stream():
    """动态生成消息。"""
    yield {
        "type": "user",
        "message": {"role": "user", "content": "Analyze the following data:"},
    }
    await asyncio.sleep(0.5)
    yield {
        "type": "user",
        "message": {"role": "user", "content": "Temperature: 25°C, Humidity: 60%"},
    }
    await asyncio.sleep(0.5)
    yield {
        "type": "user",
        "message": {"role": "user", "content": "What patterns do you see?"},
    }


async def main():
    async with ClaudeSDKClient() as client:
        # 将输入流式发送给 Claude
        await client.query(message_stream())

        # 处理响应
        async for message in client.receive_response():
            print(message)

        # 在同一会话中追问
        await client.query("Should we be concerned about these readings?")

        async for message in client.receive_response():
            print(message)


asyncio.run(main())
```

#### 示例 - 使用中断功能

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, ResultMessage


async def interruptible_task():
    options = ClaudeAgentOptions(allowed_tools=["Bash"], permission_mode="acceptEdits")

    async with ClaudeSDKClient(options=options) as client:
        # 启动一个长时间运行的任务
        await client.query("Count from 1 to 100 slowly, using the bash sleep command")

        # 让它运行一小段时间
        await asyncio.sleep(2)

        # 中断任务
        await client.interrupt()
        print("Task interrupted!")

        # 消费被中断任务的剩余消息（包括其 ResultMessage）
        async for message in client.receive_response():
            if isinstance(message, ResultMessage):
                print(f"Interrupted task finished with subtype={message.subtype!r}")
                # 被中断的任务 subtype 为 "error_during_execution"

        # 发送新命令
        await client.query("Just say hello instead")

        # 接收新响应
        async for message in client.receive_response():
            if isinstance(message, ResultMessage) and message.subtype == "success":
                print(f"New result: {message.result}")


asyncio.run(interruptible_task())
```

> **中断后的缓冲区行为：** `interrupt()` 会发送停止信号，但不会清空消息缓冲区。被中断任务已产生的消息（包括 subtype 为 `"error_during_execution"` 的 `ResultMessage`）仍留在流中。在读取新查询的响应之前，必须先用 `receive_response()` 消费完这些消息。

#### 示例 - 高级权限控制

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from claude_agent_sdk.types import (
    PermissionResultAllow,
    PermissionResultDeny,
    ToolPermissionContext,
)


async def custom_permission_handler(
    tool_name: str, input_data: dict, context: ToolPermissionContext
) -> PermissionResultAllow | PermissionResultDeny:
    """自定义工具权限逻辑。"""

    # 禁止写入系统目录
    if tool_name == "Write" and input_data.get("file_path", "").startswith("/system/"):
        return PermissionResultDeny(
            message="System directory write not allowed", interrupt=True
        )

    # 将敏感文件操作重定向到沙箱路径
    if tool_name in ["Write", "Edit"] and "config" in input_data.get("file_path", ""):
        safe_path = f"./sandbox/{input_data['file_path']}"
        return PermissionResultAllow(
            updated_input={**input_data, "file_path": safe_path}
        )

    # 放行其他所有操作
    return PermissionResultAllow(updated_input=input_data)


async def main():
    # 注意不要把需要权限门控的工具也列入 allowed_tools：allow 规则会在 can_use_tool 之前放行调用
    options = ClaudeAgentOptions(can_use_tool=custom_permission_handler)

    async with ClaudeSDKClient(options=options) as client:
        await client.query("Update the system config file")

        async for message in client.receive_response():
            # 实际会使用沙箱路径
            print(message)


asyncio.run(main())
```

## 类型（Types）

> **`@dataclass` 与 `TypedDict` 的区别：** 本 SDK 使用两种类型定义方式。以 `@dataclass` 装饰的类（如 `ResultMessage`、`AgentDefinition`、`TextBlock`）在运行时是对象实例，支持属性访问：`msg.result`。以 `TypedDict` 定义的类（如 `ThinkingConfigEnabled`、`McpStdioServerConfig`、`SyncHookJSONOutput`）在运行时是**普通字典**，需要用键访问：`config["budget_tokens"]`，而非 `config.budget_tokens`。

### `SdkMcpTool`

**定义一个可供 Claude 调用的自定义 MCP 工具。**

```python
@dataclass
class SdkMcpTool(Generic[T]):
    name: str
    description: str
    input_schema: type[T] | dict[str, Any]
    handler: Callable[[T], Awaitable[dict[str, Any]]]
    annotations: ToolAnnotations | None = None
```

| 属性 | 类型 | 说明 |
|:---|:---|:---|
| `name` | `str` | 工具的唯一标识符 |
| `description` | `str` | 人类可读的描述文本 |
| `input_schema` | <code>type[T] | dict[str, Any]</code> | 用于输入验证的 Schema |
| `handler` | `Callable[[T], Awaitable[dict[str, Any]]]` | 处理工具执行的异步函数 |
| `annotations` | <code>ToolAnnotations | None</code> | 可选的 MCP 工具注解 |

### `Transport`

**自定义传输层的抽象基类，属于低级内部 API。**

> 警告：这是低级内部 API，接口在未来版本中可能发生变化。

```python
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any


class Transport(ABC):
    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def write(self, data: str) -> None: ...

    @abstractmethod
    def read_messages(self) -> AsyncIterator[dict[str, Any]]: ...

    @abstractmethod
    async def close(self) -> None: ...

    @abstractmethod
    def is_ready(self) -> bool: ...

    @abstractmethod
    async def end_input(self) -> None: ...
```

| 方法 | 说明 |
|:---|:---|
| `connect()` | 建立传输连接，准备通信 |
| `write(data)` | 向传输层写入原始数据（JSON + 换行符） |
| `read_messages()` | 异步迭代器，逐条生成解析后的 JSON 消息 |
| `close()` | 关闭连接并清理资源 |
| `is_ready()` | 当传输层可以收发数据时返回 `True` |
| `end_input()` | 关闭输入流（例如关闭子进程传输的 stdin） |

导入方式：`from claude_agent_sdk import Transport`

### `ClaudeAgentOptions`

**Claude Code 查询的配置数据类，控制模型行为、权限、工具、会话等各项参数。**

```python
@dataclass
class ClaudeAgentOptions:
    tools: list[str] | ToolsPreset | None = None
    allowed_tools: list[str] = field(default_factory=list)
    system_prompt: str | SystemPromptPreset | None = None
    mcp_servers: dict[str, McpServerConfig] | str | Path = field(default_factory=dict)
    strict_mcp_config: bool = False
    permission_mode: PermissionMode | None = None
    continue_conversation: bool = False
    resume: str | None = None
    max_turns: int | None = None
    max_budget_usd: float | None = None
    disallowed_tools: list[str] = field(default_factory=list)
    model: str | None = None
    fallback_model: str | None = None
    betas: list[SdkBeta] = field(default_factory=list)
    output_format: dict[str, Any] | None = None
    permission_prompt_tool_name: str | None = None
    cwd: str | Path | None = None
    cli_path: str | Path | None = None
    settings: str | None = None
    add_dirs: list[str | Path] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    extra_args: dict[str, str | None] = field(default_factory=dict)
    max_buffer_size: int | None = None
    debug_stderr: Any = sys.stderr  # Deprecated
    stderr: Callable[[str], None] | None = None
    can_use_tool: CanUseTool | None = None
    hooks: dict[HookEvent, list[HookMatcher]] | None = None
    user: str | None = None
    include_partial_messages: bool = False
    include_hook_events: bool = False
    fork_session: bool = False
    agents: dict[str, AgentDefinition] | None = None
    setting_sources: list[SettingSource] | None = None
    skills: list[str] | Literal["all"] | None = None
    sandbox: SandboxSettings | None = None
    plugins: list[SdkPluginConfig] = field(default_factory=list)
    max_thinking_tokens: int | None = None  # Deprecated: use thinking instead
    thinking: ThinkingConfig | None = None
    effort: EffortLevel | None = None
    enable_file_checkpointing: bool = False
    session_store: SessionStore | None = None
    session_store_flush: SessionStoreFlushMode = "batched"
```

| 属性 | 类型 | 默认值 | 说明 |
|:---|:---|:---|:---|
| `tools` | <code>list[str] | ToolsPreset | None</code> | `None` | 工具配置。使用 `{"type": "preset", "preset": "claude_code"}` 可加载 Claude Code 的默认工具集 |
| `allowed_tools` | `list[str]` | `[]` | 自动放行无需确认的工具列表。这不会限制 Claude 只能使用这些工具；未列出的工具会走 `permission_mode` 和 `can_use_tool` 流程。使用 `disallowed_tools` 来禁止特定工具 |
| `system_prompt` | <code>str | SystemPromptPreset | None</code> | `None` | 系统提示词配置。传字符串表示自定义提示词，或使用 `{"type": "preset", "preset": "claude_code"}` 加载 Claude Code 的系统提示词。添加 `"append"` 字段可在预设基础上追加内容 |
| `mcp_servers` | <code>dict[str, McpServerConfig] | str | Path</code> | `{}` | MCP 服务器配置字典，或指向配置文件的路径 |
| `strict_mcp_config` | `bool` | `False` | 设为 `True` 时，仅使用 `mcp_servers` 中传入的服务器，忽略项目 `.mcp.json`、用户配置、插件提供的 MCP 服务器以及 claude.ai 连接器 |
| `permission_mode` | <code>PermissionMode | None</code> | `None` | 工具使用的权限模式 |
| `continue_conversation` | `bool` | `False` | 继续最近一次对话 |
| `resume` | <code>str | None</code> | `None` | 要恢复的会话 ID |
| `max_turns` | <code>int | None</code> | `None` | 最大智能体轮次（工具调用往返次数） |
| `max_budget_usd` | <code>float | None</code> | `None` | 当客户端估算的费用达到此美元值时停止查询 |
| `disallowed_tools` | `list[str]` | `[]` | 禁用的工具列表。裸名称如 `"Bash"` 会将该工具从 Claude 的上下文中移除。带范围的规则如 `"Bash(rm *)"` 会保留工具可用性，但在所有权限模式（包括 `bypassPermissions`）下拒绝匹配的调用 |
| `enable_file_checkpointing` | `bool` | `False` | 启用文件变更追踪以支持回退 |
| `model` | <code>str | None</code> | `None` | Claude 模型别名或完整模型名称 |
| `fallback_model` | <code>str | None</code> | `None` | 主模型失败时使用的备用模型 |
| `betas` | `list[SdkBeta]` | `[]` | 要启用的 Beta 功能列表 |
| `output_format` | <code>dict[str, Any] | None</code> | `None` | 结构化响应的输出格式（例如 `{"type": "json_schema", "schema": {...}}`） |
| `permission_prompt_tool_name` | <code>str | None</code> | `None` | 用于权限提示的 MCP 工具名称 |
| `cwd` | <code>str | Path | None</code> | `None` | 当前工作目录 |
| `cli_path` | <code>str | Path | None</code> | `None` | Claude Code CLI 可执行文件的自定义路径 |
| `settings` | <code>str | None</code> | `None` | 配置文件路径 |
| `add_dirs` | <code>list[str | Path]</code> | `[]` | Claude 可以访问的额外目录 |
| `env` | `dict[str, str]` | `{}` | 在继承的进程环境基础上合并的环境变量 |
| `extra_args` | <code>dict[str, str | None]</code> | `{}` | 直接传递给 CLI 的额外参数 |
| `max_buffer_size` | <code>int | None</code> | `None` | 缓冲 CLI stdout 时的最大字节数 |
| `debug_stderr` | `Any` | `sys.stderr` | *已弃用* - 调试输出的文件对象。请改用 `stderr` 回调 |
| `stderr` | <code>Callable[[str], None] | None</code> | `None` | 接收 CLI stderr 输出的回调函数 |
| `can_use_tool` | <code>CanUseTool | None</code> | `None` | 工具权限回调，仅在权限评估流程进入提示阶段时被调用 |
| `hooks` | <code>dict[HookEvent, list[HookMatcher]] | None</code> | `None` | 用于拦截事件的钩子配置 |
| `user` | <code>str | None</code> | `None` | 用户标识符 |
| `include_partial_messages` | `bool` | `False` | 包含部分消息的流式事件。启用后会生成 `StreamEvent` 消息 |
| `include_hook_events` | `bool` | `False` | 在消息流中包含钩子生命周期事件，以 `HookEventMessage` 对象形式呈现 |
| `fork_session` | `bool` | `False` | 使用 `resume` 恢复会话时，分叉到新的会话 ID 而非继续原始会话 |
| `agents` | <code>dict[str, AgentDefinition] | None</code> | `None` | 以编程方式定义的子智能体 |
| `plugins` | `list[SdkPluginConfig]` | `[]` | 从本地路径加载自定义插件 |
| `sandbox` | <code>SandboxSettings | None</code> | `None` | 以编程方式配置沙箱行为 |
| `setting_sources` | <code>list[SettingSource] | None</code> | `None`（CLI 默认加载所有来源） | 控制要加载哪些文件系统配置。传 `[]` 可禁用用户、项目和本地配置 |
| `skills` | <code>list[str] | Literal["all"] | None</code> | `None` | 会话可用的 Skill 列表。传 `"all"` 启用所有已发现的 Skill，或传具体名称列表 |
| `max_thinking_tokens` | <code>int | None</code> | `None` | *已弃用* - 思考块的最大 token 数。请改用 `thinking` |
| `thinking` | <code>ThinkingConfig | None</code> | `None` | 控制扩展思考行为。优先级高于 `max_thinking_tokens` |
| `effort` | <code>EffortLevel | None</code> | `None` | 思考深度的努力级别 |
| `session_store` | <code>SessionStore | None</code> | `None` | 将会话记录镜像到外部后端，使任何主机都能恢复这些会话 |
| `session_store_flush` | `Literal["batched", "eager"]` | `"batched"` | 将镜像的记录条目刷新到 `session_store` 的时机 |

#### 处理慢速或卡顿的 API 响应

```python
options = ClaudeAgentOptions(
    env={
        "API_TIMEOUT_MS": "120000",
        "CLAUDE_CODE_MAX_RETRIES": "2",
        "CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS": "120000",
    },
)
```

* `API_TIMEOUT_MS`：Anthropic 客户端的单次请求超时时间（毫秒）。默认 `600000`。
* `CLAUDE_CODE_MAX_RETRIES`：API 最大重试次数。默认 `10`，上限 `15`。
* `CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS`：通过 `run_in_background` 启动的子智能体的卡顿看门狗超时时间。默认 `600000`。
* `CLAUDE_ENABLE_STREAM_WATCHDOG` 搭配 `CLAUDE_STREAM_IDLE_TIMEOUT_MS`：当 HTTP 头已到达但响应体停止传输时中止请求。看门狗默认开启；设置 `CLAUDE_ENABLE_STREAM_WATCHDOG=0` 可禁用。`CLAUDE_STREAM_IDLE_TIMEOUT_MS` 默认为 `300000`，且最小值被限制在该数值。

### `OutputFormat`

**结构化输出验证的配置：**

```python
# output_format 的字典结构

```python
{
    "type": "json_schema",
    "schema": {...},  # 你的 JSON Schema 定义
}
```

| 字段 | 必填 | 说明 |
|:---|:---|:---|
| `type` | 是 | 必须为 `"json_schema"`，用于 JSON Schema 验证 |
| `schema` | 是 | 用于输出验证的 JSON Schema 定义 |

### `SystemPromptPreset`

**预设系统提示词配置。** 使用 Claude Code 内置的系统提示词，并可追加自定义指令。

```python
class SystemPromptPreset(TypedDict):
    type: Literal["preset"]
    preset: Literal["claude_code"]
    append: NotRequired[str]
    exclude_dynamic_sections: NotRequired[bool]
```

| 字段 | 必填 | 说明 |
|:---|:---|:---|
| `type` | 是 | 必须为 `"preset"`，表示使用预设系统提示词 |
| `preset` | 是 | 必须为 `"claude_code"`，表示使用 Claude Code 的系统提示词 |
| `append` | 否 | 追加到预设系统提示词末尾的额外指令 |
| `exclude_dynamic_sections` | 否 | 将每次会话的动态上下文从系统提示词移到首条用户消息中。有助于在不同用户和机器间提升 prompt 缓存复用率 |

### `SettingSource`

**配置来源选项。** 指定从哪些文件加载设置。

```python
SettingSource = Literal["user", "project", "local"]
```

| 值 | 说明 | 文件位置 |
|:---|:---|:---|
| `"user"` | 全局用户设置 | `~/.claude/settings.json` |
| `"project"` | 共享项目设置（纳入版本控制） | `.claude/settings.json` |
| `"local"` | 本地项目设置（不纳入版本控制） | `.claude/settings.local.json` |

#### 默认行为

当 `setting_sources` 省略或为 `None` 时，`query()` 会加载与 Claude Code CLI 相同的文件系统设置：user、project 和 local。

#### 使用场景

**禁用文件系统设置：**

```python
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt="Analyze this code",
    options=ClaudeAgentOptions(
        setting_sources=[]
    ),
):
    print(message)
```

> 在 Python SDK 0.1.59 及更早版本中，传入空列表的效果等同于省略该选项。

**显式加载所有文件系统设置：**

```python
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt="Analyze this code",
    options=ClaudeAgentOptions(
        setting_sources=["user", "project", "local"]
    ),
):
    print(message)
```

**仅加载特定来源的设置：**

```python
# 仅加载项目设置，忽略用户设置和本地设置
async for message in query(
    prompt="Run CI checks",
    options=ClaudeAgentOptions(
        setting_sources=["project"]  # 仅 .claude/settings.json
    ),
):
    print(message)
```

**测试和 CI 环境：**

```python
# 在 CI 中排除本地设置，确保行为一致
async for message in query(
    prompt="Run tests",
    options=ClaudeAgentOptions(
        setting_sources=["project"],  # 仅团队共享的设置
        permission_mode="bypassPermissions",
    ),
):
    print(message)
```

**纯 SDK 应用：**

```python
# 完全通过代码定义所有配置。
# 传入 [] 可以不加载任何文件系统配置。
async for message in query(
    prompt="Review this PR",
    options=ClaudeAgentOptions(
        setting_sources=[],
        agents={...},
        mcp_servers={...},
        allowed_tools=["Read", "Grep", "Glob"],
    ),
):
    print(message)
```

**加载 CLAUDE.md 项目指令：**

```python
# 加载项目设置以包含 CLAUDE.md 文件
async for message in query(
    prompt="Add a new feature following project conventions",
    options=ClaudeAgentOptions(
        system_prompt={
            "type": "preset",
            "preset": "claude_code",  # 使用 Claude Code 的系统提示词
        },
        setting_sources=["project"],  # 从项目中加载 CLAUDE.md
        allowed_tools=["Read", "Write", "Edit"],
    ),
):
    print(message)
```

#### 设置优先级

当加载多个来源时，设置按以下优先级合并（从高到低）：

1. 本地设置（`.claude/settings.local.json`）
2. 项目设置（`.claude/settings.json`）
3. 用户设置（`~/.claude/settings.json`）

代码中的选项会覆盖用户、项目和本地文件系统设置。托管策略设置的优先级高于代码选项。

### `AgentDefinition`

**Agent 定义。** 描述一个 Agent 的行为、能力和约束。

```python
@dataclass
class AgentDefinition:
    description: str
    prompt: str
    tools: list[str] | None = None
    disallowedTools: list[str] | None = None
    model: str | None = None
    skills: list[str] | None = None
    memory: Literal["user", "project", "local"] | None = None
    mcpServers: list[str | dict[str, Any]] | None = None
    initialPrompt: str | None = None
    maxTurns: int | None = None
    background: bool | None = None
    effort: EffortLevel | int | None = None
    permissionMode: PermissionMode | None = None
```

| 字段 | 必填 | 说明 |
|:---|:---|:---|
| `description` | 是 | 自然语言描述，说明何时应使用此 Agent |
| `prompt` | 是 | 该 Agent 的系统提示词 |
| `tools` | 否 | 允许使用的工具名称列表。省略则继承所有工具 |
| `disallowedTools` | 否 | 需从 Agent 工具集中移除的工具名称列表。也支持 MCP 服务器级别的模式匹配 |
| `model` | 否 | 该 Agent 使用的模型。支持别名如 `"sonnet"`、`"opus"`、`"haiku"` 或 `"inherit"`，也支持完整模型 ID |
| `skills` | 否 | 启动时预加载到 Agent 上下文中的技能名称列表 |
| `memory` | 否 | 该 Agent 的记忆来源：`"user"`、`"project"` 或 `"local"` |
| `mcpServers` | 否 | 该 Agent 可用的 MCP 服务器 |
| `initialPrompt` | 否 | 当此 Agent 作为主线程 Agent 运行时，自动提交的首条用户消息 |
| `maxTurns` | 否 | Agent 停止前的最大轮次数 |
| `background` | 否 | 被调用时是否作为非阻塞的后台任务运行 |
| `effort` | 否 | 该 Agent 的推理投入级别 |
| `permissionMode` | 否 | 该 Agent 内工具执行的权限模式 |

> `AgentDefinition` 的字段名使用 camelCase 风格，如 `disallowedTools`、`permissionMode`、`maxTurns`。这些名称与 TypeScript SDK 共享的通信格式保持一致。

### `PermissionMode`

**权限模式。** 控制工具执行时的权限检查策略。

```python
PermissionMode = Literal[
    "default",  # 标准权限行为
    "acceptEdits",  # 自动接受文件编辑
    "plan",  # 规划模式 - 只探索不修改
    "dontAsk",  # 未预先批准的操作直接拒绝，而非弹出提示
    "bypassPermissions",  # 跳过权限检查；显式 ask 规则仍会提示（谨慎使用）
]
```

### `EffortLevel`

**推理投入级别。** 控制模型的思考深度。

```python
EffortLevel = Literal[
    "low",  # 最少思考，最快响应
    "medium",  # 适度思考
    "high",  # 深度推理
    "xhigh",  # 扩展推理；不支持的模型会回退到 "high"
    "max",  # 最大投入
]
```

### `CanUseTool`

**工具权限回调函数类型。** 用于自定义工具调用的权限判断逻辑。

```python
CanUseTool = Callable[
    [str, dict[str, Any], ToolPermissionContext], Awaitable[PermissionResult]
]
```

回调接收以下参数：
* `tool_name`：被调用的工具名称
* `input_data`：工具的输入参数
* `context`：一个 `ToolPermissionContext` 实例，包含附加信息

返回 `PermissionResult`（`PermissionResultAllow` 或 `PermissionResultDeny`）。

### `ToolPermissionContext`

**工具权限上下文。** 提供关于权限请求的额外信息。

```python
@dataclass
class ToolPermissionContext:
    signal: Any | None = None  # 预留：未来的中止信号支持
    suggestions: list[PermissionUpdate] = field(default_factory=list)
    blocked_path: str | None = None
    decision_reason: str | None = None
    title: str | None = None
    display_name: str | None = None
    description: str | None = None
```

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `signal` | <code>Any | None</code> | 预留，用于未来的中止信号支持 |
| `suggestions` | `list[PermissionUpdate]` | CLI 提供的权限更新建议 |
| `blocked_path` | <code>str | None</code> | 触发权限请求的文件路径（如适用） |
| `decision_reason` | <code>str | None</code> | 触发此权限请求的原因 |
| `title` | <code>str | None</code> | 完整的权限提示句 |
| `display_name` | <code>str | None</code> | 工具操作的简短名词短语 |
| `description` | <code>str | None</code> | 权限 UI 中的人类可读副标题 |

### `PermissionResult`

**权限判定结果。** 允许或拒绝工具调用。

```python
PermissionResult = PermissionResultAllow | PermissionResultDeny
```

### `PermissionResultAllow`

**允许工具调用。** 可选地修改输入或更新权限规则。

```python
@dataclass
class PermissionResultAllow:
    behavior: Literal["allow"] = "allow"
    updated_input: dict[str, Any] | None = None
    updated_permissions: list[PermissionUpdate] | None = None
```

| 字段 | 类型 | 默认值 | 说明 |
|:---|:---|:---|:---|
| `behavior` | `Literal["allow"]` | `"allow"` | 必须为 "allow" |
| `updated_input` | <code>dict[str, Any] | None</code> | `None` | 替代原始输入的修改后输入 |
| `updated_permissions` | <code>list[PermissionUpdate] | None</code> | `None` | 需要应用的权限更新 |

### `PermissionResultDeny`

**拒绝工具调用。** 可附带拒绝原因和是否中断执行。

```python
@dataclass
class PermissionResultDeny:
    behavior: Literal["deny"] = "deny"
    message: str = ""
    interrupt: bool = False
```

| 字段 | 类型 | 默认值 | 说明 |
|:---|:---|:---|:---|
| `behavior` | `Literal["deny"]` | `"deny"` | 必须为 "deny" |
| `message` | `str` | `""` | 解释工具被拒绝原因的消息 |
| `interrupt` | `bool` | `False` | 是否中断当前执行 |

### `PermissionUpdate`

**权限更新操作。** 定义对权限规则的增删改操作。

```python
@dataclass
class PermissionUpdate:
    type: Literal[
        "addRules",
        "replaceRules",
        "removeRules",
        "setMode",
        "addDirectories",
        "removeDirectories",
    ]
    rules: list[PermissionRuleValue] | None = None
    behavior: Literal["allow", "deny", "ask"] | None = None
    mode: PermissionMode | None = None
    directories: list[str] | None = None
    destination: (
        Literal["userSettings", "projectSettings", "localSettings", "session"] | None
    ) = None
```

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `type` | `Literal[...]` | 权限更新操作的类型 |
| `rules` | <code>list[PermissionRuleValue] | None</code> | 用于增加/替换/移除操作的规则 |
| `behavior` | <code>Literal["allow", "deny", "ask"] | None</code> | 基于规则的操作行为 |
| `mode` | <code>PermissionMode | None</code> | setMode 操作使用的模式 |
| `directories` | <code>list[str] | None</code> | 增加/移除目录操作使用的目录列表 |
| `destination` | <code>Literal[...] | None</code> | 权限更新的应用位置 |

### `PermissionRuleValue`

**权限规则值。** 表示一条工具权限规则。

```python
@dataclass
class PermissionRuleValue:
    tool_name: str
    rule_content: str | None = None
```

### `ToolsPreset`

**工具预设配置。** 使用 Claude Code 内置的工具集。

```python
class ToolsPreset(TypedDict):
    type: Literal["preset"]
    preset: Literal["claude_code"]
```

### `ThinkingConfig`

**思考模式配置。** 控制模型是否及如何进行"思考"（reasoning）。

```python
ThinkingDisplay = Literal["summarized", "omitted"]


class ThinkingConfigAdaptive(TypedDict):
    type: Literal["adaptive"]
    display: NotRequired[ThinkingDisplay]


class ThinkingConfigEnabled(TypedDict):
    type: Literal["enabled"]
    budget_tokens: int
    display: NotRequired[ThinkingDisplay]


class ThinkingConfigDisabled(TypedDict):
    type: Literal["disabled"]


ThinkingConfig = ThinkingConfigAdaptive | ThinkingConfigEnabled | ThinkingConfigDisabled
```

| 变体 | 字段 | 说明 |
|:---|:---|:---|
| `adaptive` | `type`, `display` | Claude 自适应决定何时进行思考 |
| `enabled` | `type`, `budget_tokens`, `display` | 启用思考并指定 token 预算 |
| `disabled` | `type` | 禁用思考 |

可选的 `display` 字段控制思考文本以 `"summarized"`（摘要）还是 `"omitted"`（省略）形式返回。在 Claude Opus 4.7 及以后版本中，API 默认值为 `"omitted"`，因此如需在 `ThinkingBlock` 输出中接收思考内容，请设置为 `"summarized"`。

```python
from claude_agent_sdk import ClaudeAgentOptions, ThinkingConfigEnabled

# 方式 1：字典字面量（推荐，无需额外导入）
options = ClaudeAgentOptions(thinking={"type": "enabled", "budget_tokens": 20000})

# 方式 2：构造函数风格（返回普通字典）
config = ThinkingConfigEnabled(type="enabled", budget_tokens=20000)
print(config["budget_tokens"])  # 20000
# config.budget_tokens 会抛出 AttributeError
```

### `SdkBeta`

**SDK Beta 标识。** 用于启用实验性功能。

```python
SdkBeta = Literal["context-1m-2025-08-07"]
```

> 注意：`context-1m-2025-08-07` beta 已于 2026 年 4 月 30 日退役。对 Claude Sonnet 4.5 或 Sonnet 4 传入此 header 不再有任何效果。要使用 1M token 上下文窗口，请迁移到 Claude Sonnet 5、Claude Sonnet 4.6、Claude Opus 4.6、Claude Opus 4.7 或 Claude Opus 4.8。

### `McpSdkServerConfig`

**MCP SDK 服务器配置。** 用于直接传入 MCP Server 实例。

```python
class McpSdkServerConfig(TypedDict):
    type: Literal["sdk"]
    name: str
    instance: Any  # MCP Server 实例
```

### `McpServerConfig`

**MCP 服务器配置联合类型。** 支持 stdio、SSE、HTTP 和 SDK 四种连接方式。

```python
McpServerConfig = (
    McpStdioServerConfig | McpSSEServerConfig | McpHttpServerConfig | McpSdkServerConfig
)
```

#### `McpStdioServerConfig`

```python
class McpStdioServerConfig(TypedDict):
    type: NotRequired[Literal["stdio"]]  # 为向后兼容而设为可选
    command: str
    args: NotRequired[list[str]]
    env: NotRequired[dict[str, str]]
```

#### `McpSSEServerConfig`

```python
class McpSSEServerConfig(TypedDict):
    type: Literal["sse"]
    url: str
    headers: NotRequired[dict[str, str]]
```

#### `McpHttpServerConfig`

```python
class McpHttpServerConfig(TypedDict):
    type: Literal["http"]
    url: str
    headers: NotRequired[dict[str, str]]
```

### `McpServerStatusConfig`

**MCP 服务器状态配置。** 包含所有可序列化的服务器配置变体。

```python
McpServerStatusConfig = (
    McpStdioServerConfig
    | McpSSEServerConfig
    | McpHttpServerConfig
    | McpSdkServerConfigStatus
    | McpClaudeAIProxyServerConfig
)
```

`McpSdkServerConfigStatus` 是 `McpSdkServerConfig` 的可序列化形式，仅包含 `type`（`"sdk"`）和 `name`（`str`）字段。`McpClaudeAIProxyServerConfig` 包含 `type`（`"claudeai-proxy"`）、`url`（`str`）和 `id`（`str`）字段。

### `McpStatusResponse`

**MCP 状态响应。** 包含所有 MCP 服务器的状态列表。

```python
class McpStatusResponse(TypedDict):
    mcpServers: list[McpServerStatus]
```

### `McpServerStatus`

**单个 MCP 服务器的状态信息。**

```python
class McpServerStatus(TypedDict):
    name: str
    status: McpServerConnectionStatus  # "connected" | "failed" | "needs-auth" | "pending" | "disabled"
    serverInfo: NotRequired[McpServerInfo]
    error: NotRequired[str]
    config: NotRequired[McpServerStatusConfig]
    scope: NotRequired[str]
    tools: NotRequired[list[McpToolInfo]]
```

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `name` | `str` | 服务器名称 |
| `status` | `str` | 取值为 `"connected"`、`"failed"`、`"needs-auth"`、`"pending"` 或 `"disabled"` |
| `serverInfo` | `dict`（可选） | 服务器名称和版本（`{"name": str, "version": str}`） |
| `error` | `str`（可选） | 服务器连接失败时的错误信息 |
| `config` | `McpServerStatusConfig`（可选） | 服务器配置 |
| `scope` | `str`（可选） | 配置作用域 |
| `tools` | `list`（可选） | 该服务器提供的工具列表，每项包含 `name`、`description` 和 `annotations` 字段 |

### `SdkPluginConfig`

**SDK 插件配置。** 指定本地插件的路径。

```python
class SdkPluginConfig(TypedDict):
    type: Literal["local"]
    path: str
```

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `type` | `Literal["local"]` | 必须为 `"local"`（目前仅支持本地插件） |
| `path` | `str` | 插件目录的绝对路径或相对路径 |

**示例：**

```python
plugins = [
    {"type": "local", "path": "./my-plugin"},
    {"type": "local", "path": "/absolute/path/to/plugin"},
]
```

## 消息类型

### `Message`

**消息联合类型。** SDK 中所有消息类型的总和。

```python
Message = (
    UserMessage
    | AssistantMessage
    | SystemMessage
    | ResultMessage
    | StreamEvent
    | RateLimitEvent
)
```

### `UserMessage`

**用户消息。** 表示用户或工具结果发送的消息。

```python
@dataclass
class UserMessage:
    content: str | list[ContentBlock]
    uuid: str | None = None
    parent_tool_use_id: str | None = None
    tool_use_result: dict[str, Any] | None = None
```

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `content` | <code>str | list[ContentBlock]</code> | 消息内容，可以是文本或内容块列表 |
| `uuid` | <code>str | None</code> | 消息的唯一标识符 |
| `parent_tool_use_id` | <code>str | None</code> | 如果此消息是工具结果响应，对应的工具调用 ID |
| `tool_use_result` | <code>dict[str, Any] | None</code> | 工具结果数据（如适用） |

### `AssistantMessage`

**助手消息。** 模型生成的响应。

```python
@dataclass
class AssistantMessage:
    content: list[ContentBlock]
    model: str
    parent_tool_use_id: str | None = None
    error: AssistantMessageError | None = None
    usage: dict[str, Any] | None = None
    message_id: str | None = None
```

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `content` | `list[ContentBlock]` | 响应中的内容块列表 |
| `model` | `str` | 生成该响应的模型 |
| `parent_tool_use_id` | <code>str | None</code> | 如果是嵌套响应，对应的工具调用 ID |
| `error` | <code>AssistantMessageError | None</code> | 响应遇到错误时的错误类型 |
| `usage` | <code>dict[str, Any] | None</code> | 单条消息的 token 用量（键名与 `ResultMessage.usage` 相同） |
| `message_id` | <code>str | None</code> | API 消息 ID。同一轮次的多条消息共享相同的 ID |

### `AssistantMessageError`

**助手消息错误类型。** 表示响应过程中发生的错误种类。

```python
AssistantMessageError = Literal[
    "authentication_failed",
    "billing_error",
    "rate_limit",
    "invalid_request",
    "server_error",
    "max_output_tokens",
    "unknown",
]
```

### `SystemMessage`

**系统消息。** 由系统产生的内部消息。

```python
@dataclass
class SystemMessage:
    subtype: str
    data: dict[str, Any]
```

### `ResultMessage`

**结果消息。** 会话结束时返回的最终状态汇总。

```python
@dataclass
class ResultMessage:
    subtype: str
    duration_ms: int
    duration_api_ms: int
    is_error: bool
    num_turns: int
    session_id: str
    stop_reason: str | None = None
    total_cost_usd: float | None = None
    usage: dict[str, Any] | None = None
    result: str | None = None
    structured_output: Any = None
    model_usage: dict[str, Any] | None = None
    permission_denials: list[Any] | None = None
    deferred_tool_use: DeferredToolUse | None = None
    errors: list[str] | None = None
    api_error_status: int | None = None
    uuid: str | None = None
```

`subtype` 字段取值为 `"success"`、`"error_during_execution"`、`"error_max_turns"`、`"error_max_budget_usd"` 或 `"error_max_structured_output_retries"`。

诊断字段说明：
* `is_error`：当会话以错误状态结束时为 `True`。
* `api_error_status`：导致终止的 API 错误的 HTTP 状态码。轮次正常结束时为 `None`。
* `result`：当 `subtype="success"` 时为最终助手消息的文本；`error_*` 子类型时为 `None`。
* `errors`：循环级别的错误字符串。仅在 `error_*` 子类型时有值。

`usage` 字典的键：

| 键 | 类型 | 说明 |
|---|---|---|
| `input_tokens` | `int` | 总消耗的输入 token 数。 |
| `output_tokens` | `int` | 总生成的输出 token 数。 |
| `cache_creation_input_tokens` | `int` | 用于创建新缓存条目的 token 数。 |
| `cache_read_input_tokens` | `int` | 从已有缓存条目读取的 token 数。 |

`model_usage` 字典按模型名称映射到每个模型的用量（键名为 camelCase）：

| 键 | 类型 | 说明 |
|---|---|---|
| `inputTokens` | `int` | 该模型的输入 token 数。 |
| `outputTokens` | `int` | 该模型的输出 token 数。 |
| `cacheCreationInputTokens` | `int` | 该模型的缓存创建 token 数。 |
| `cacheReadInputTokens` | `int` | 该模型的缓存读取 token 数。 |

---
