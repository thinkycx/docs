"""
create: 2026-07-08
update: 2026-07-08
description:
    演示 include_partial_messages=True 获取实时流式文本增量的功能。
    开启后除了完整 AssistantMessage 外, 还收到 StreamEvent 消息(content_block_delta 等)。
    实现打字机效果, 统计流式事件数/文本增量片段/事件类型集合。
    核心 API: ClaudeAgentOptions(include_partial_messages=True), StreamEvent
expect_output:
    - 实时逐字输出数字 1-5 及描述(打字机效果)
    - StreamEvent 总数 > 30
    - 文本增量片段数 > 20
    - 事件类型集合包含 message_start, content_block_start, content_block_delta, content_block_stop, message_delta, message_stop
    - 完整 AssistantMessage 文本长度 > 100 字符
    - 输出 stop_reason: end_turn
usage:
    cd demos && uv run python 30_streaming_partial.py
"""

import anyio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    StreamEvent,
    TextBlock,
    query,
)


async def main():
    print("=== Demo: 流式部分消息 (StreamEvent) ===\n")

    options = ClaudeAgentOptions(
        include_partial_messages=True,  # 启用流式部分消息
        max_turns=1,
        permission_mode="bypassPermissions",
    )

    prompt = "Count from 1 to 5, putting each number on a new line with a brief description."
    print(f"Prompt: '{prompt}'\n")
    print("--- 实时流式输出 ---")

    stream_event_count = 0
    delta_texts: list[str] = []
    event_types_seen: set[str] = set()

    async for msg in query(prompt=prompt, options=options):
        if isinstance(msg, StreamEvent):
            stream_event_count += 1
            event = msg.event  # 原始 Anthropic API 事件 dict

            event_type = event.get("type", "unknown")
            event_types_seen.add(event_type)

            # content_block_delta 包含文本增量
            if event_type == "content_block_delta":
                delta = event.get("delta", {})
                delta_type = delta.get("type", "")

                if delta_type == "text_delta":
                    text = delta.get("text", "")
                    delta_texts.append(text)
                    # 实时打印 (不换行, 模拟打字机效果)
                    print(text, end="", flush=True)
                elif delta_type == "thinking_delta":
                    # Thinking 增量 (如果启用了 thinking)
                    pass

            elif event_type == "content_block_start":
                # 新 content block 开始
                content_block = event.get("content_block", {})
                block_type = content_block.get("type", "")
                if block_type == "text":
                    pass  # text block 开始

            elif event_type == "content_block_stop":
                # content block 结束
                pass

            elif event_type == "message_start":
                # 消息开始, 包含 model 信息
                message = event.get("message", {})
                model = message.get("model", "unknown")
                if stream_event_count <= 1:
                    print(f"[model: {model}] ", end="")

            elif event_type == "message_delta":
                # 消息级别更新 (stop_reason 等)
                delta = event.get("delta", {})
                stop_reason = delta.get("stop_reason")
                if stop_reason:
                    print(f"\n[stop_reason: {stop_reason}]")

        elif isinstance(msg, AssistantMessage):
            # 完整的 AssistantMessage (在所有 StreamEvent 之后)
            print(f"\n\n--- 完整 AssistantMessage ---")
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"  完整文本长度: {len(block.text)} 字符")
                    print(f"  预览: {block.text[:80]}...")

        elif isinstance(msg, ResultMessage):
            print(f"\n--- ResultMessage ---")
            print(f"  session_id: {msg.session_id}")
            print(f"  num_turns: {msg.num_turns}")

    # --- 统计 ---
    print(f"\n--- 流式统计 ---")
    print(f"  StreamEvent 总数: {stream_event_count}")
    print(f"  文本增量片段数: {len(delta_texts)}")
    print(f"  拼接后总长度: {sum(len(t) for t in delta_texts)} 字符")
    print(f"  事件类型集合: {sorted(event_types_seen)}")

    # --- StreamEvent 结构说明 ---
    print("\n--- StreamEvent 结构 ---")
    print("""
@dataclass
class StreamEvent:
    uuid: str              # 事件唯一 ID
    session_id: str        # 会话 ID
    event: dict[str, Any]  # 原始 Anthropic API 流式事件
    parent_tool_use_id: str | None  # 如果在工具调用中

常见 event.type 值:
  - message_start:        消息开始, event.message 含 model/id/role
  - content_block_start:  content block 开始
  - content_block_delta:  内容增量
    - delta.type="text_delta":     文本增量, delta.text
    - delta.type="thinking_delta": 思考增量
    - delta.type="input_json_delta": 工具输入增量
  - content_block_stop:   content block 结束
  - message_delta:        消息级更新 (stop_reason, usage)
  - message_stop:         消息结束
""")

    print("=== Demo 完成 ===")


if __name__ == "__main__":
    anyio.run(main)
