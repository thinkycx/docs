# 完整类型速查表

本文档列出 `claude-agent-sdk` v0.2.111 的所有导出符号（`__all__`），按功能分类组织。

## 核心入口

| 符号 | 类型 | 说明 |
|------|------|------|
| `query` | `async generator function` | 一次性查询入口，返回消息的异步生成器 |
| `ClaudeSDKClient` | `class` | 持久客户端，支持多轮对话和流式控制 |
| `Transport` | `abstract class` | 传输层抽象基类，可自定义实现 |
| `__version__` | `str` | SDK 版本号 |

## 工具系统

| 符号 | 类型 | 说明 |
|------|------|------|
| `tool` | `decorator` | 将 Python 函数注册为 SDK 自定义工具 |
| `create_sdk_mcp_server` | `function` | 创建内嵌的 MCP 服务器实例 |
| `SdkMcpTool` | `class` | MCP 工具定义 |
| `ToolAnnotations` | `TypedDict` | 工具元数据注解（只读、幂等等） |

## 配置

| 符号 | 类型 | 说明 |
|------|------|------|
| `ClaudeAgentOptions` | `dataclass` | 所有配置参数的容器（约 50 个字段） |

## 消息类型

| 符号 | 类型 | 说明 |
|------|------|------|
| `UserMessage` | `TypedDict` | 用户输入消息 |
| `AssistantMessage` | `TypedDict` | 模型回复消息，含 content 和 usage |
| `SystemMessage` | `TypedDict` | 系统消息 |
| `ResultMessage` | `TypedDict` | 查询结束消息，含成本、错误、统计信息 |
| `StreamEvent` | `TypedDict` | 流式事件（增量文本、工具调用进度等） |
| `RateLimitEvent` | `TypedDict` | 限流事件通知 |
| `TaskStartedMessage` | `TypedDict` | 子任务开始通知 |
| `TaskProgressMessage` | `TypedDict` | 子任务进度更新 |
| `TaskNotificationMessage` | `TypedDict` | 子任务通知 |
| `TaskUpdatedMessage` | `TypedDict` | 子任务状态变更 |
| `MirrorErrorMessage` | `TypedDict` | Session Store 镜像错误 |
| `HookEventMessage` | `TypedDict` | Hook 事件通知消息 |
| `Message` | `Union` | 所有消息类型的联合类型 |

## 内容块（Content Blocks）

| 符号 | 类型 | 说明 |
|------|------|------|
| `TextBlock` | `TypedDict` | 文本内容块 |
| `ThinkingBlock` | `TypedDict` | 思考内容块（含 thinking 文本和 signature） |
| `ToolUseBlock` | `TypedDict` | 工具调用块（含 tool_name 和 input） |
| `ToolResultBlock` | `TypedDict` | 工具返回结果块 |
| `ServerToolUseBlock` | `TypedDict` | 服务端工具调用块（内置工具） |
| `ServerToolResultBlock` | `TypedDict` | 服务端工具结果块 |
| `ContentBlock` | `Union` | 所有内容块类型的联合类型 |

## 权限系统

| 符号 | 类型 | 说明 |
|------|------|------|
| `PermissionMode` | `Literal` | 权限模式（"default"/"acceptall"/"bypassaliases"） |
| `CanUseTool` | `TypedDict` | 工具可用性查询结果 |
| `CanUseToolShadowedWarning` | `TypedDict` | 工具被遮蔽警告 |
| `ToolPermissionContext` | `TypedDict` | 工具权限上下文信息 |
| `PermissionResult` | `Union` | 权限判定结果（允许或拒绝） |
| `PermissionResultAllow` | `TypedDict` | 允许结果 |
| `PermissionResultDeny` | `TypedDict` | 拒绝结果（含 reason） |
| `PermissionUpdate` | `TypedDict` | 权限动态更新 |

## Hook 系统

| 符号 | 类型 | 说明 |
|------|------|------|
| `HookCallback` | `Callable` | Hook 回调函数类型 |
| `HookContext` | `TypedDict` | Hook 执行上下文 |
| `HookInput` | `Union` | 所有 Hook 输入类型的联合 |
| `HookJSONOutput` | `TypedDict` | Hook JSON 输出格式 |
| `HookMatcher` | `TypedDict` | Hook 匹配规则（tool_name 等） |
| `BaseHookInput` | `TypedDict` | Hook 输入基类 |
| `PreToolUseHookInput` | `TypedDict` | 工具调用前 Hook 输入 |
| `PostToolUseHookInput` | `TypedDict` | 工具调用后 Hook 输入 |
| `PostToolUseFailureHookInput` | `TypedDict` | 工具失败后 Hook 输入 |
| `PostToolUseFailureHookSpecificOutput` | `TypedDict` | 工具失败 Hook 特定输出 |
| `UserPromptSubmitHookInput` | `TypedDict` | 用户提交提示词时 Hook 输入 |
| `StopHookInput` | `TypedDict` | 代理停止时 Hook 输入 |
| `SubagentStopHookInput` | `TypedDict` | 子代理停止时 Hook 输入 |
| `SubagentStartHookInput` | `TypedDict` | 子代理启动时 Hook 输入 |
| `SubagentStartHookSpecificOutput` | `TypedDict` | 子代理启动 Hook 特定输出 |
| `PreCompactHookInput` | `TypedDict` | 上下文压缩前 Hook 输入 |
| `NotificationHookInput` | `TypedDict` | 通知 Hook 输入 |
| `NotificationHookSpecificOutput` | `TypedDict` | 通知 Hook 特定输出 |
| `PermissionRequestHookInput` | `TypedDict` | 权限请求 Hook 输入 |
| `PermissionRequestHookSpecificOutput` | `TypedDict` | 权限请求 Hook 特定输出 |
| `HookEventMessage` | `TypedDict` | Hook 事件消息 |

## Agent 系统

| 符号 | 类型 | 说明 |
|------|------|------|
| `AgentDefinition` | `TypedDict` | 子代理定义（名称、模型、工具、提示词等） |
| `SettingSource` | `Literal` | 配置源类型（"user"/"project"/"local"） |

## 插件系统

| 符号 | 类型 | 说明 |
|------|------|------|
| `SdkPluginConfig` | `TypedDict` | 插件配置（type="local", path=...） |

## Session 管理 — 查询

| 符号 | 类型 | 说明 |
|------|------|------|
| `list_sessions` | `async function` | 列出所有 session |
| `get_session_info` | `async function` | 获取指定 session 的元信息 |
| `get_session_messages` | `async function` | 获取 session 的消息历史 |
| `list_subagents` | `async function` | 列出 session 的子代理 |
| `get_subagent_messages` | `async function` | 获取子代理的消息历史 |
| `SDKSessionInfo` | `TypedDict` | Session 元信息结构 |
| `SessionMessage` | `TypedDict` | Session 消息结构 |

## Session 管理 — Store

| 符号 | 类型 | 说明 |
|------|------|------|
| `SessionKey` | `TypedDict` | Session 唯一键 |
| `SessionStore` | `abstract class` | Session 存储抽象基类 |
| `SessionStoreEntry` | `TypedDict` | Session 存储条目 |
| `SessionStoreFlushMode` | `Literal` | 刷新模式（同步/异步） |
| `SessionStoreListEntry` | `TypedDict` | Session 列表条目 |
| `SessionSummaryEntry` | `TypedDict` | Session 摘要条目 |
| `SessionListSubkeysKey` | `TypedDict` | 子键列表键 |
| `InMemorySessionStore` | `class` | 内存实现的 Session Store |
| `fold_session_summary` | `function` | 折叠 Session 摘要 |
| `project_key_for_directory` | `function` | 为目录生成项目键 |
| `import_session_to_store` | `async function` | 导入 Session 到 Store |
| `MirrorErrorMessage` | `TypedDict` | 镜像错误消息 |

## Session 管理 — Store 支持的查询

| 符号 | 类型 | 说明 |
|------|------|------|
| `list_sessions_from_store` | `function` | 从 Store 列出 sessions |
| `get_session_info_from_store` | `function` | 从 Store 获取 session 信息 |
| `get_session_messages_from_store` | `function` | 从 Store 获取消息 |
| `list_subagents_from_store` | `function` | 从 Store 列出子代理 |
| `get_subagent_messages_from_store` | `function` | 从 Store 获取子代理消息 |

## Session 管理 — 变更操作

| 符号 | 类型 | 说明 |
|------|------|------|
| `rename_session` | `async function` | 重命名 session |
| `tag_session` | `async function` | 为 session 添加标签 |
| `delete_session` | `async function` | 删除 session |
| `fork_session` | `async function` | 分叉 session（创建分支） |
| `ForkSessionResult` | `TypedDict` | 分叉操作结果 |
| `rename_session_via_store` | `function` | 通过 Store 重命名 |
| `tag_session_via_store` | `function` | 通过 Store 添加标签 |
| `delete_session_via_store` | `function` | 通过 Store 删除 |
| `fork_session_via_store` | `function` | 通过 Store 分叉 |

## MCP（Model Context Protocol）

| 符号 | 类型 | 说明 |
|------|------|------|
| `McpServerConfig` | `TypedDict` | MCP 服务器配置（command, args, env） |
| `McpSdkServerConfig` | `TypedDict` | SDK 内嵌 MCP 服务器配置 |
| `McpServerStatus` | `TypedDict` | MCP 服务器状态 |
| `McpServerStatusConfig` | `TypedDict` | MCP 服务器状态配置 |
| `McpServerConnectionStatus` | `Literal` | 连接状态（connected/disconnected/error） |
| `McpServerInfo` | `TypedDict` | MCP 服务器信息 |
| `McpStatusResponse` | `TypedDict` | MCP 状态响应 |
| `McpToolAnnotations` | `TypedDict` | MCP 工具注解 |
| `McpToolInfo` | `TypedDict` | MCP 工具信息 |
| `ContextUsageCategory` | `TypedDict` | 上下文使用分类 |
| `ContextUsageResponse` | `TypedDict` | 上下文使用响应 |

## 错误类型

| 符号 | 类型 | 说明 |
|------|------|------|
| `ClaudeSDKError` | `Exception` | 所有 SDK 异常的基类 |
| `CLIConnectionError` | `Exception` | 连接 CLI 失败 |
| `CLINotFoundError` | `Exception` | CLI 二进制文件未找到 |
| `ProcessError` | `Exception` | CLI 进程异常退出（含 exit_code, stderr） |
| `CLIJSONDecodeError` | `Exception` | CLI 返回格式错误的 JSON（含 line, original_error） |

## 配置类型

| 符号 | 类型 | 说明 |
|------|------|------|
| `EffortLevel` | `Literal` | 努力级别（"low"/"medium"/"high"/"xhigh"/"max"） |
| `ThinkingConfig` | `Union` | 思考配置联合类型 |
| `ThinkingConfigAdaptive` | `TypedDict` | 自适应思考配置 `{"type": "adaptive"}` |
| `ThinkingConfigEnabled` | `TypedDict` | 启用思考配置 `{"type": "enabled", "budget_tokens": N}` |
| `ThinkingConfigDisabled` | `TypedDict` | 禁用思考配置 `{"type": "disabled"}` |
| `SdkBeta` | `Literal` | Beta 功能标识符 |
| `SandboxSettings` | `TypedDict` | 沙盒设置 |
| `SandboxNetworkConfig` | `TypedDict` | 沙盒网络配置 |
| `SandboxIgnoreViolations` | `TypedDict` | 沙盒忽略违规配置 |
| `TaskBudget` | `TypedDict` | API 侧令牌预算 |

## 其他类型

| 符号 | 类型 | 说明 |
|------|------|------|
| `DeferredToolUse` | `TypedDict` | Hook 延迟的工具调用 |
| `RateLimitInfo` | `TypedDict` | 限流详细信息 |
| `RateLimitStatus` | `Literal` | 限流状态 |
| `RateLimitType` | `Literal` | 限流类型（令牌/请求/并发） |
| `TaskNotificationStatus` | `Literal` | 任务通知状态 |
| `TaskUpdatedStatus` | `Literal` | 任务更新状态 |
| `TERMINAL_TASK_STATUSES` | `tuple` | 终态任务状态集合 |
| `TaskUsage` | `TypedDict` | 任务令牌使用量 |
| `ServerToolName` | `Literal` | 内置服务端工具名称 |

## 快速导入示例

```python
# 核心入口
from claude_agent_sdk import query, ClaudeSDKClient, ClaudeAgentOptions

# 消息类型
from claude_agent_sdk import (
    AssistantMessage,
    ResultMessage,
    UserMessage,
    StreamEvent,
    Message,
)

# 内容块
from claude_agent_sdk import (
    TextBlock,
    ThinkingBlock,
    ToolUseBlock,
    ToolResultBlock,
    ContentBlock,
)

# 工具系统
from claude_agent_sdk import tool, create_sdk_mcp_server, SdkMcpTool

# 错误类型
from claude_agent_sdk import (
    ClaudeSDKError,
    CLINotFoundError,
    CLIConnectionError,
    ProcessError,
    CLIJSONDecodeError,
)

# Hook 系统
from claude_agent_sdk import (
    HookCallback,
    PreToolUseHookInput,
    PostToolUseHookInput,
    StopHookInput,
)

# 配置类型
from claude_agent_sdk import (
    EffortLevel,
    ThinkingConfig,
    SandboxSettings,
    PermissionMode,
)

# Session 管理
from claude_agent_sdk import (
    list_sessions,
    get_session_info,
    get_session_messages,
    SessionStore,
    InMemorySessionStore,
)

# MCP
from claude_agent_sdk import McpServerConfig, McpStatusResponse

# Transport
from claude_agent_sdk import Transport
```

## 类型使用模式

### 类型守卫模式

```python
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    StreamEvent,
    Message,
)

async for msg in query(prompt="hello", options=ClaudeAgentOptions()):
    if isinstance(msg, AssistantMessage):
        # 处理模型回复
        for block in msg.content:
            if block["type"] == "text":
                print(block["text"])
            elif block["type"] == "thinking":
                print(f"[thinking] {block['thinking'][:100]}")
            elif block["type"] == "tool_use":
                print(f"[tool] {block['name']}({block['input']})")
    elif isinstance(msg, ResultMessage):
        # 处理结束
        if msg.is_error:
            print(f"Error: {msg.subtype}")
        else:
            print(f"Done: ${msg.total_cost_usd}")
    elif isinstance(msg, StreamEvent):
        # 处理流式事件
        pass
```

### Hook 类型模式

```python
from claude_agent_sdk import (
    PreToolUseHookInput,
    PostToolUseHookInput,
    StopHookInput,
)

async def pre_tool_hook(input: PreToolUseHookInput) -> dict:
    tool_name: str = input.tool_name
    tool_input: dict = input.tool_input
    # 返回 allow/deny/modify
    return {"decision": "allow"}

async def post_tool_hook(input: PostToolUseHookInput) -> dict:
    tool_name: str = input.tool_name
    tool_result: str = input.tool_result
    # 返回 proceed/rerun/block
    return {"decision": "proceed"}

async def stop_hook(input: StopHookInput) -> dict:
    result = input.result
    # 返回 stop/continue
    return {"decision": "stop"}
```
