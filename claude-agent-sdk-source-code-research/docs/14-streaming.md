# 流式输出与部分消息

流式输出允许实时接收 Agent 的生成内容，无需等待完整响应。适用于需要实时展示 Agent 思考过程和输出的 UI 场景。

## 启用部分消息

通过 `include_partial_messages=True` 启用流式部分消息：

```python
from claude_agent_sdk import ClaudeAgentOptions

options = ClaudeAgentOptions(
    include_partial_messages=True,  # 启用部分消息流
)
```

## StreamEvent 消息类型

启用后，`receive_messages()` 会产出 `StreamEvent` 类型的消息：

```python
@dataclass
class StreamEvent:
    uuid: str                    # 消息唯一 ID
    session_id: str              # Session ID
    event: dict                  # 原始 Anthropic API 流式事件
    parent_tool_use_id: str | None  # 父工具调用 ID（子 Agent 场景）
```

## Event 字典结构

`StreamEvent.event` 字典镜像了 Anthropic API 的原始流式事件格式：

### content_block_start

标记一个新的内容块开始：

```python
{
    "type": "content_block_start",
    "index": 0,
    "content_block": {
        "type": "text",
        "text": ""
    }
}
```

### content_block_delta

增量内容更新：

```python
# 文本增量
{
    "type": "content_block_delta",
    "index": 0,
    "delta": {
        "type": "text_delta",
        "text": "这是新增的文本片段"
    }
}

# 工具输入增量
{
    "type": "content_block_delta",
    "index": 1,
    "delta": {
        "type": "input_json_delta",
        "partial_json": "{\"command\": \"ls"
    }
}
```

### content_block_stop

标记内容块结束：

```python
{
    "type": "content_block_stop",
    "index": 0
}
```

## receive_messages() vs receive_response()

SDK 提供两种接收消息的方法：

### receive_response() — 完整消息

返回处理后的完整消息对象（AssistantMessage、ToolUseBlock、ResultMessage 等），每条消息在完全生成后才产出：

```python
async with ClaudeSDKClient(options) as client:
    await client.query("写一篇文章")

    async for msg in client.receive_response():
        # msg 是完整的消息对象
        if isinstance(msg, AssistantMessage):
            print(msg.content[0].text)  # 完整文本
```

### receive_messages() — 包含流式事件

返回所有消息，包括流式的部分消息（StreamEvent）。需要 `include_partial_messages=True`：

```python
async with ClaudeSDKClient(options) as client:
    await client.query("写一篇文章")

    async for msg in client.receive_messages():
        if isinstance(msg, StreamEvent):
            # 实时增量内容
            event = msg.event
            if event.get("type") == "content_block_delta":
                delta = event.get("delta", {})
                if delta.get("type") == "text_delta":
                    print(delta["text"], end="", flush=True)
        elif isinstance(msg, AssistantMessage):
            # 完整消息（流式结束后也会收到）
            pass
```

## 实时 UI 集成模式

### 基础文本流

```python
import anyio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    StreamEvent,
    AssistantMessage,
    ResultMessage,
)

async def streaming_chat():
    options = ClaudeAgentOptions(
        include_partial_messages=True,
        allowed_tools=["Read", "Bash"],
        permission_mode="bypassPermissions",
    )

    async with ClaudeSDKClient(options) as client:
        await client.query("解释 Python 的 GIL 是什么")

        async for msg in client.receive_messages():
            if isinstance(msg, StreamEvent):
                event = msg.event
                event_type = event.get("type")

                if event_type == "content_block_start":
                    block = event.get("content_block", {})
                    if block.get("type") == "text":
                        pass  # 文本块开始

                elif event_type == "content_block_delta":
                    delta = event.get("delta", {})
                    if delta.get("type") == "text_delta":
                        # 实时输出文本
                        print(delta["text"], end="", flush=True)

                elif event_type == "content_block_stop":
                    print()  # 块结束，换行

            elif isinstance(msg, ResultMessage):
                print("\n--- 对话结束 ---")

anyio.run(streaming_chat)
```

### 带状态追踪的完整实现

```python
import anyio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    StreamEvent,
    AssistantMessage,
    ToolUseBlock,
    ToolResultBlock,
    ResultMessage,
    TextBlock,
)

class StreamingUI:
    """实时流式 UI 管理器"""

    def __init__(self):
        self.current_text = ""
        self.current_block_index = -1
        self.is_thinking = False
        self.tool_calls = []

    def handle_stream_event(self, event: dict):
        event_type = event.get("type")

        if event_type == "content_block_start":
            self.current_block_index = event.get("index", 0)
            block = event.get("content_block", {})
            block_type = block.get("type")

            if block_type == "thinking":
                self.is_thinking = True
                self._display_thinking_start()
            elif block_type == "text":
                self.is_thinking = False
                self._display_text_start()
            elif block_type == "tool_use":
                self._display_tool_start(block.get("name", ""))

        elif event_type == "content_block_delta":
            delta = event.get("delta", {})
            delta_type = delta.get("type")

            if delta_type == "text_delta":
                text = delta.get("text", "")
                self.current_text += text
                self._display_text_delta(text)
            elif delta_type == "thinking_delta":
                # Agent 的思考过程（如果启用了 extended thinking）
                self._display_thinking_delta(delta.get("thinking", ""))
            elif delta_type == "input_json_delta":
                # 工具输入的增量 JSON
                self._display_tool_input_delta(delta.get("partial_json", ""))

        elif event_type == "content_block_stop":
            if self.is_thinking:
                self._display_thinking_end()
            else:
                self._display_text_end()
            self.current_text = ""

    def _display_thinking_start(self):
        print("\n[思考中...]", flush=True)

    def _display_thinking_delta(self, text: str):
        print(f"  {text}", end="", flush=True)

    def _display_thinking_end(self):
        print("\n[思考结束]", flush=True)

    def _display_text_start(self):
        pass  # 文本块开始，可显示光标

    def _display_text_delta(self, text: str):
        print(text, end="", flush=True)

    def _display_text_end(self):
        print()  # 换行

    def _display_tool_start(self, tool_name: str):
        print(f"\n📎 调用工具: {tool_name}", flush=True)

    def _display_tool_input_delta(self, partial_json: str):
        pass  # 可选：显示工具输入的构建过程


async def main():
    options = ClaudeAgentOptions(
        include_partial_messages=True,
        allowed_tools=["Read", "Write", "Bash"],
        permission_mode="bypassPermissions",
    )

    ui = StreamingUI()

    async with ClaudeSDKClient(options) as client:
        await client.query("读取 README.md 并总结项目的主要功能")

        async for msg in client.receive_messages():
            if isinstance(msg, StreamEvent):
                ui.handle_stream_event(msg.event)

            elif isinstance(msg, AssistantMessage):
                # 完整消息确认（可用于验证）
                pass

            elif isinstance(msg, ResultMessage):
                print("\n\n=== 对话完成 ===")
                if msg.cost:
                    print(f"Token 用量: {msg.cost}")

anyio.run(main)
```

## 文本增量累积示例

演示如何从流式事件中逐步构建完整文本：

```python
import anyio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    StreamEvent,
    ResultMessage,
)

async def accumulate_text():
    """累积文本增量，最终得到完整响应"""

    options = ClaudeAgentOptions(
        include_partial_messages=True,
    )

    full_text = []       # 按块存储完整文本
    current_block = ""   # 当前块的累积文本

    async with ClaudeSDKClient(options) as client:
        await client.query("用三段话介绍 Python 的优势")

        async for msg in client.receive_messages():
            if isinstance(msg, StreamEvent):
                event = msg.event
                event_type = event.get("type")

                if event_type == "content_block_start":
                    current_block = ""

                elif event_type == "content_block_delta":
                    delta = event.get("delta", {})
                    if delta.get("type") == "text_delta":
                        text = delta["text"]
                        current_block += text
                        # 实时展示
                        print(text, end="", flush=True)

                elif event_type == "content_block_stop":
                    if current_block:
                        full_text.append(current_block)
                    print()  # 块之间换行

            elif isinstance(msg, ResultMessage):
                break

    # 完整文本
    complete_response = "\n".join(full_text)
    print(f"\n--- 完整响应长度: {len(complete_response)} 字符 ---")

anyio.run(accumulate_text)
```

## 子 Agent 的流式事件

当子 Agent 产生输出时，`StreamEvent.parent_tool_use_id` 标识其父工具调用：

```python
async for msg in client.receive_messages():
    if isinstance(msg, StreamEvent):
        if msg.parent_tool_use_id:
            # 这是子 Agent 的流式输出
            print(f"[子Agent {msg.parent_tool_use_id}] ", end="")

        event = msg.event
        if event.get("type") == "content_block_delta":
            delta = event.get("delta", {})
            if delta.get("type") == "text_delta":
                print(delta["text"], end="", flush=True)
```

## 与 receive_response() 混合使用

不建议在同一个会话中混合使用 `receive_messages()` 和 `receive_response()`。如果只需要完整消息而不需要实时流，使用 `receive_response()` 更简洁：

```python
# 推荐：简单场景用 receive_response()
async for msg in client.receive_response():
    if isinstance(msg, AssistantMessage):
        for block in msg.content:
            if isinstance(block, TextBlock):
                print(block.text)

# 推荐：需要实时展示时用 receive_messages()
async for msg in client.receive_messages():
    if isinstance(msg, StreamEvent):
        # 处理流式事件
        ...
```

## 注意事项

- `include_partial_messages=True` 会增加消息量，仅在需要实时展示时启用
- StreamEvent 的 `event` 字典格式与 Anthropic Messages API 的流式事件一致
- `content_block_delta` 中的 `text_delta` 可能是任意长度的文本片段（从单字符到整句）
- 流式事件和完整消息会同时产出：先收到流式事件，最后收到完整的 AssistantMessage
- 网络中断时流式事件可能不完整，应以最终的完整消息为准
- `parent_tool_use_id` 为 None 时表示是主 Agent 的输出
- 工具调用的输入也会以流式方式产出（`input_json_delta`），但通常不需要实时展示
