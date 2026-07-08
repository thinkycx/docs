---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
category: translation
tags: [claude-code, agent-sdk, translation]
description: Claude Agent SDK 流式输出指南，介绍如何实时接收文本和工具调用的增量更新，以及如何构建流式 UI。
refs:
  - https://code.claude.com/docs/en/agent-sdk/streaming-output
  - en-source/agent-sdk/streaming-output.md
title: 【译】Agent SDK - 流式输出
---

# 【译】流式输出

> 从 Agent SDK 实时获取响应，在文本和工具调用流入时即时接收

**默认情况下，Agent SDK 在 Claude 完成每个响应后才返回完整的 `AssistantMessage` 对象。** 要在文本和工具调用生成时接收增量更新，通过在选项中设置 `include_partial_messages`（Python）或 `includePartialMessages`（TypeScript）为 `true` 来启用部分消息流。

> 本页涵盖输出流式传输（实时接收 token）。输入模式（如何发送消息）见[向 Agent 发送消息](https://code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode)。你也可以[通过 CLI 使用 Agent SDK 流式响应](https://code.claude.com/docs/en/headless)。

## 启用流式输出

**设置 `include_partial_messages`（Python）或 `includePartialMessages`（TypeScript）为 `true` 即可启用流式传输。** 这会使 SDK 在常规的 `AssistantMessage` 和 `ResultMessage` 之外，额外产出包含原始 API 事件的 `StreamEvent` 消息。

你的代码需要：

1. 检查每条消息的类型，区分 `StreamEvent` 和其他消息类型
2. 对于 `StreamEvent`，提取 `event` 字段并检查其 `type`
3. 查找 `content_block_delta` 事件中 `delta.type` 为 `text_delta` 的，其中包含实际文本块

以下示例启用流式传输并在文本块到达时逐块打印。注意嵌套的类型检查：先检查 `StreamEvent`，再检查 `content_block_delta`，最后检查 `text_delta`：

```python
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import StreamEvent
import asyncio


async def stream_response():
    options = ClaudeAgentOptions(
        include_partial_messages=True,
        allowed_tools=["Bash", "Read"],
    )

    async for message in query(prompt="List the files in my project", options=options):
        if isinstance(message, StreamEvent):
            event = message.event
            if event.get("type") == "content_block_delta":
                delta = event.get("delta", {})
                if delta.get("type") == "text_delta":
                    print(delta.get("text", ""), end="", flush=True)


asyncio.run(stream_response())
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "List the files in my project",
  options: {
    includePartialMessages: true,
    allowedTools: ["Bash", "Read"]
  }
})) {
  if (message.type === "stream_event") {
    const event = message.event;
    if (event.type === "content_block_delta") {
      if (event.delta.type === "text_delta") {
        process.stdout.write(event.delta.text);
      }
    }
  }
}
```

## StreamEvent 参考

**启用部分消息后，你会收到包装在对象中的原始 Claude API 流事件。** 该类型在每个 SDK 中名称不同：

* **Python**: `StreamEvent`（从 `claude_agent_sdk.types` 导入）
* **TypeScript**: `SDKPartialAssistantMessage`，`type: 'stream_event'`

两者都包含原始 Claude API 事件，不是累积的文本。你需要自行提取和累积文本 delta。各类型结构如下：

```python
@dataclass
class StreamEvent:
    uuid: str  # 此事件的唯一标识符
    session_id: str  # 会话标识符
    event: dict[str, Any]  # 原始 Claude API 流事件
    parent_tool_use_id: str | None  # 始终为 None
```

```typescript
type SDKPartialAssistantMessage = {
  type: "stream_event";
  event: BetaRawMessageStreamEvent; // 来自 Anthropic SDK
  parent_tool_use_id: string | null;
  uuid: UUID;
  session_id: string;
  ttft_ms?: number; // 首 token 时间（毫秒），仅在 message_start 事件上出现
};
```

`parent_tool_use_id` 字段在 Python 中始终为 `None`，TypeScript 中始终为 `null`。流事件仅对主会话发出；来自子 Agent 的 token 级 delta 不会被转发。要归属子 Agent 的输出，使用携带 `parent_tool_use_id` 的完整消息。见[检测子 Agent 调用](https://code.claude.com/docs/en/agent-sdk/subagents#detect-subagent-invocation)。

`event` 字段包含来自 [Claude API](https://platform.claude.com/docs/en/build-with-claude/streaming#event-types) 的原始流事件。常见事件类型包括：

| 事件类型 | 说明 |
| :--- | :--- |
| `message_start` | 新消息开始 |
| `content_block_start` | 新内容块开始（文本或工具使用） |
| `content_block_delta` | 内容的增量更新 |
| `content_block_stop` | 内容块结束 |
| `message_delta` | 消息级更新（停止原因、用量） |
| `message_stop` | 消息结束 |

## 消息流

**启用部分消息后，你按以下顺序接收消息：**

```text
StreamEvent (message_start)
StreamEvent (content_block_start) - 文本块
StreamEvent (content_block_delta) - 文本块...
StreamEvent (content_block_stop)
StreamEvent (content_block_start) - tool_use 块
StreamEvent (content_block_delta) - 工具输入块...
StreamEvent (content_block_stop)
StreamEvent (message_delta)
StreamEvent (message_stop)
AssistantMessage - 包含所有内容的完整消息
... 工具执行 ...
... 下一轮更多流事件 ...
ResultMessage - 最终结果
```

未启用部分消息时（Python 中 `include_partial_messages`，TypeScript 中 `includePartialMessages`），你收到除 `StreamEvent` 外的所有消息类型。常见类型包括 `SystemMessage`（会话初始化）、`AssistantMessage`（完整响应）、`ResultMessage`（最终结果），以及表示对话历史被压缩的边界消息（TypeScript 中为 `SDKCompactBoundaryMessage`；Python 中为 subtype 为 `"compact_boundary"` 的 `SystemMessage`）。

## 流式文本响应

**要在文本生成时显示，查找 `content_block_delta` 事件中 `delta.type` 为 `text_delta` 的。** 这些包含增量文本块。以下示例在每个块到达时打印：

```python
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import StreamEvent
import asyncio


async def stream_text():
    options = ClaudeAgentOptions(include_partial_messages=True)

    async for message in query(prompt="Explain how databases work", options=options):
        if isinstance(message, StreamEvent):
            event = message.event
            if event.get("type") == "content_block_delta":
                delta = event.get("delta", {})
                if delta.get("type") == "text_delta":
                    # 在每个文本块到达时打印
                    print(delta.get("text", ""), end="", flush=True)

    print()  # 最后换行


asyncio.run(stream_text())
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Explain how databases work",
  options: { includePartialMessages: true }
})) {
  if (message.type === "stream_event") {
    const event = message.event;
    if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
      process.stdout.write(event.delta.text);
    }
  }
}

console.log(); // 最后换行
```

## 流式工具调用

**工具调用也以增量方式流式传输。** 你可以跟踪工具何时开始、在输入生成时接收其输入、以及在它们完成时看到。以下示例跟踪当前正在调用的工具并在 JSON 输入流入时累积。它使用三种事件类型：

* `content_block_start`：工具开始
* `content_block_delta`（带 `input_json_delta`）：输入块到达
* `content_block_stop`：工具调用完成

```python
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import StreamEvent
import asyncio


async def stream_tool_calls():
    options = ClaudeAgentOptions(
        include_partial_messages=True,
        allowed_tools=["Read", "Bash"],
    )

    # 跟踪当前工具并累积其输入 JSON
    current_tool = None
    tool_input = ""

    async for message in query(prompt="Read the README.md file", options=options):
        if isinstance(message, StreamEvent):
            event = message.event
            event_type = event.get("type")

            if event_type == "content_block_start":
                # 新工具调用开始
                content_block = event.get("content_block", {})
                if content_block.get("type") == "tool_use":
                    current_tool = content_block.get("name")
                    tool_input = ""
                    print(f"Starting tool: {current_tool}")

            elif event_type == "content_block_delta":
                delta = event.get("delta", {})
                if delta.get("type") == "input_json_delta":
                    # 在 JSON 输入流入时累积
                    chunk = delta.get("partial_json", "")
                    tool_input += chunk
                    print(f"  Input chunk: {chunk}")

            elif event_type == "content_block_stop":
                # 工具调用完成 - 显示最终输入
                if current_tool:
                    print(f"Tool {current_tool} called with: {tool_input}")
                    current_tool = None


asyncio.run(stream_tool_calls())
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

// 跟踪当前工具并累积其输入 JSON
let currentTool: string | null = null;
let toolInput = "";

for await (const message of query({
  prompt: "Read the README.md file",
  options: {
    includePartialMessages: true,
    allowedTools: ["Read", "Bash"]
  }
})) {
  if (message.type === "stream_event") {
    const event = message.event;

    if (event.type === "content_block_start") {
      // 新工具调用开始
      if (event.content_block.type === "tool_use") {
        currentTool = event.content_block.name;
        toolInput = "";
        console.log(`Starting tool: ${currentTool}`);
      }
    } else if (event.type === "content_block_delta") {
      if (event.delta.type === "input_json_delta") {
        // 在 JSON 输入流入时累积
        const chunk = event.delta.partial_json;
        toolInput += chunk;
        console.log(`  Input chunk: ${chunk}`);
      }
    } else if (event.type === "content_block_stop") {
      // 工具调用完成 - 显示最终输入
      if (currentTool) {
        console.log(`Tool ${currentTool} called with: ${toolInput}`);
        currentTool = null;
      }
    }
  }
}
```

## 构建流式 UI

**此示例将文本和工具流式传输组合为一个完整的 UI。** 它跟踪 Agent 当前是否正在执行工具（使用 `in_tool` 标志），在工具运行时显示状态指示器（如 `[Using Read...]`）。不在工具中时正常流式文本，工具完成时触发 "done" 消息。此模式适用于需要在多步骤 Agent 任务期间显示进度的聊天界面。

```python
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage
from claude_agent_sdk.types import StreamEvent
import asyncio
import sys


async def streaming_ui():
    options = ClaudeAgentOptions(
        include_partial_messages=True,
        allowed_tools=["Read", "Bash", "Grep"],
    )

    # 跟踪当前是否在工具调用中
    in_tool = False

    async for message in query(
        prompt="Find all TODO comments in the codebase", options=options
    ):
        if isinstance(message, StreamEvent):
            event = message.event
            event_type = event.get("type")

            if event_type == "content_block_start":
                content_block = event.get("content_block", {})
                if content_block.get("type") == "tool_use":
                    # 工具调用开始 - 显示状态指示器
                    tool_name = content_block.get("name")
                    print(f"\n[Using {tool_name}...]", end="", flush=True)
                    in_tool = True

            elif event_type == "content_block_delta":
                delta = event.get("delta", {})
                # 仅在不执行工具时流式文本
                if delta.get("type") == "text_delta" and not in_tool:
                    sys.stdout.write(delta.get("text", ""))
                    sys.stdout.flush()

            elif event_type == "content_block_stop":
                if in_tool:
                    # 工具调用完成
                    print(" done", flush=True)
                    in_tool = False

        elif isinstance(message, ResultMessage):
            # Agent 完成所有工作
            print(f"\n\n--- Complete ---")


asyncio.run(streaming_ui())
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

// 跟踪当前是否在工具调用中
let inTool = false;

for await (const message of query({
  prompt: "Find all TODO comments in the codebase",
  options: {
    includePartialMessages: true,
    allowedTools: ["Read", "Bash", "Grep"]
  }
})) {
  if (message.type === "stream_event") {
    const event = message.event;

    if (event.type === "content_block_start") {
      if (event.content_block.type === "tool_use") {
        // 工具调用开始 - 显示状态指示器
        process.stdout.write(`\n[Using ${event.content_block.name}...]`);
        inTool = true;
      }
    } else if (event.type === "content_block_delta") {
      // 仅在不执行工具时流式文本
      if (event.delta.type === "text_delta" && !inTool) {
        process.stdout.write(event.delta.text);
      }
    } else if (event.type === "content_block_stop") {
      if (inTool) {
        // 工具调用完成
        console.log(" done");
        inTool = false;
      }
    }
  } else if (message.type === "result") {
    // Agent 完成所有工作
    console.log("\n\n--- Complete ---");
  }
}
```

## 已知限制

* **结构化输出**：JSON 结果仅出现在最终的 `ResultMessage.structured_output` 中，不会作为流式 delta 出现。详情见[结构化输出](https://code.claude.com/docs/en/agent-sdk/structured-outputs)。

## 后续步骤

现在你可以实时流式传输文本和工具调用了，可以探索这些相关主题：

* [交互式 vs 一次性查询](https://code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode)：为你的场景选择输入模式
* [结构化输出](https://code.claude.com/docs/en/agent-sdk/structured-outputs)：从 Agent 获取类型化 JSON 响应
* [权限配置](https://code.claude.com/docs/en/agent-sdk/permissions)：控制 Agent 可以使用哪些工具
