# 消息类型体系

SDK 返回的消息流由多种类型的消息组成。所有消息类型的联合定义为 `Message`。

## Message 联合类型

```python
Message = (
    UserMessage | AssistantMessage | SystemMessage | ResultMessage |
    StreamEvent | RateLimitEvent |
    TaskStartedMessage | TaskProgressMessage |
    TaskNotificationMessage | TaskUpdatedMessage |
    MirrorErrorMessage | HookEventMessage
)
```

## 核心消息类型

### AssistantMessage

Claude 的回复消息，最常用的消息类型。

```python
@dataclass
class AssistantMessage:
    content: list[ContentBlock]     # 内容块列表
    model: str                      # 使用的模型 ID
    message_id: str | None          # 消息 ID
    stop_reason: str | None         # 停止原因
    usage: dict | None              # token 使用情况
    session_id: str | None          # Session ID
    uuid: str | None                # 消息 UUID
    parent_tool_use_id: str | None  # 父工具调用 ID（子 Agent 中）
    error: str | None               # 错误信息
```

处理模式：
```python
if isinstance(msg, AssistantMessage):
    for block in msg.content:
        if isinstance(block, TextBlock):
            print(block.text)
        elif isinstance(block, ThinkingBlock):
            print(f"[思考] {block.thinking[:100]}...")
        elif isinstance(block, ToolUseBlock):
            print(f"[调用工具] {block.name}({block.input})")
```

### ResultMessage

最终结果消息，总是消息流的最后一条。

```python
@dataclass
class ResultMessage:
    subtype: str                    # 结果类型
    duration_ms: int | None         # 总耗时(ms)
    duration_api_ms: int | None     # API 调用耗时(ms)
    is_error: bool                  # 是否为错误
    num_turns: int | None           # 对话轮数
    session_id: str | None          # Session ID
    total_cost_usd: float | None    # 总费用(USD)
    usage: dict | None              # token 使用统计
    result: str | None              # 文本结果
    structured_output: Any | None   # 结构化输出
    model_usage: dict | None        # 按模型分的 token 统计
    permission_denials: list | None  # 被拒绝的权限请求
    deferred_tool_use: list[DeferredToolUse] | None  # 被延迟的工具调用
    errors: list[dict] | None       # 错误列表
    api_error_status: int | None    # API HTTP 错误码
    stop_reason: str | None         # 停止原因
    uuid: str | None
```

**subtype 取值**：
| 值 | 含义 |
|---|------|
| `"success"` | 正常完成 |
| `"error_max_turns"` | 超出最大轮数 |
| `"error_max_budget_usd"` | 超出预算 |
| `"error_during_execution"` | 执行过程中出错 |
| `"error_max_structured_output_retries"` | 结构化输出校验重试耗尽 |

### UserMessage

用户消息（通常是工具执行结果，由 CLI 自动生成）。

```python
@dataclass
class UserMessage:
    content: str | list[ContentBlock]
    uuid: str | None
    parent_tool_use_id: str | None
    tool_use_result: dict | None
```

### SystemMessage

系统事件消息。

```python
@dataclass
class SystemMessage:
    subtype: str        # 事件子类型
    data: dict          # 事件数据
```

常见 subtype：
| subtype | 含义 | data 内容 |
|---------|------|----------|
| `"init"` | 初始化完成 | tools, slash_commands, mcp_servers |
| `"task_started"` | 后台任务启动 | task_id, description |
| `"task_notification"` | 任务完成通知 | task_id, status, output_file |

### StreamEvent

流式部分消息（需 `include_partial_messages=True`）。

```python
@dataclass
class StreamEvent:
    uuid: str | None
    session_id: str | None
    event: dict                     # 原始 API 事件
    parent_tool_use_id: str | None
```

`event` 字典包含 API 流式事件，如：
- `{"type": "content_block_delta", "delta": {"type": "text_delta", "text": "..."}}`
- `{"type": "content_block_start", ...}`

### RateLimitEvent

速率限制事件。

```python
@dataclass
class RateLimitEvent:
    rate_limit_info: RateLimitInfo
    uuid: str | None
    session_id: str | None

@dataclass
class RateLimitInfo:
    status: RateLimitStatus          # "allowed" | "allowed_warning" | "rejected"
    type: RateLimitType              # "five_hour" | "seven_day" | ...
    seconds_until_allowed: float | None
```

## 内容块类型 (ContentBlock)

```python
ContentBlock = (
    TextBlock | ThinkingBlock | ToolUseBlock | ToolResultBlock |
    ServerToolUseBlock | ServerToolResultBlock
)
```

### TextBlock
```python
@dataclass
class TextBlock:
    text: str
```

### ThinkingBlock
```python
@dataclass
class ThinkingBlock:
    thinking: str       # 思考内容
    signature: str      # 签名
```

### ToolUseBlock
```python
@dataclass
class ToolUseBlock:
    id: str             # 工具调用 ID
    name: str           # 工具名称
    input: dict         # 工具输入参数
```

### ToolResultBlock
```python
@dataclass
class ToolResultBlock:
    tool_use_id: str                    # 对应的 ToolUseBlock.id
    content: str | list | None          # 工具执行结果
    is_error: bool | None               # 是否执行出错
```

### ServerToolUseBlock
```python
@dataclass
class ServerToolUseBlock:
    id: str
    name: ServerToolName    # API 端工具名（web_search 等）
    input: dict
```

### ServerToolResultBlock
```python
@dataclass
class ServerToolResultBlock:
    tool_use_id: str
    content: dict
```

## 任务相关消息

### TaskStartedMessage
```python
@dataclass
class TaskStartedMessage(SystemMessage):
    task_id: str
    description: str | None
    uuid: str | None
    session_id: str | None
    tool_use_id: str | None
    task_type: str | None
```

### TaskProgressMessage
```python
@dataclass
class TaskProgressMessage(SystemMessage):
    task_id: str
    description: str | None
    usage: TaskUsage | None
    uuid: str | None
    session_id: str | None
    tool_use_id: str | None
    last_tool_name: str | None
```

### TaskNotificationMessage
```python
@dataclass
class TaskNotificationMessage(SystemMessage):
    task_id: str
    status: TaskNotificationStatus    # "completed" | "failed" | "stopped"
    output_file: str | None
    summary: str | None
    uuid: str | None
    session_id: str | None
```

## 消息处理最佳实践

```python
from claude_agent_sdk import (
    AssistantMessage, ResultMessage, SystemMessage,
    StreamEvent, RateLimitEvent, TextBlock, ToolUseBlock
)

async for msg in query(prompt="..."):
    if isinstance(msg, AssistantMessage):
        for block in msg.content:
            if isinstance(block, TextBlock):
                print(block.text, end="")
            elif isinstance(block, ToolUseBlock):
                print(f"\n→ 调用 {block.name}")

    elif isinstance(msg, ResultMessage):
        if msg.is_error:
            print(f"错误: {msg.subtype}")
        else:
            print(f"\n✓ 完成 | 费用: ${msg.total_cost_usd:.4f} | 耗时: {msg.duration_ms}ms")

    elif isinstance(msg, RateLimitEvent):
        if msg.rate_limit_info.status == "rejected":
            print(f"被限流，等待 {msg.rate_limit_info.seconds_until_allowed}s")

    elif isinstance(msg, SystemMessage):
        if msg.subtype == "init":
            print(f"已初始化，可用工具: {len(msg.data.get('tools', []))}")
```
