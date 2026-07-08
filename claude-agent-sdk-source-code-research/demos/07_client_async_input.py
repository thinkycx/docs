"""
create: 2026-07-08
update: 2026-07-08
description:
    异步可迭代输入（流式输入模式）。演示核心 API: query() with AsyncIterable prompt。
    使用异步生成器函数作为 prompt 参数，按顺序 yield 多条用户消息。
    每条消息是 {"type": "user", "message": {...}, "parent_tool_use_id": None, "session_id": "default"} 格式。
    展示 SDK 如何支持流式/渐进式输入，适用于需要动态生成用户消息的场景。
expect_output:
    - 第一条消息后 Claude 确认记住颜色 blue
    - 第二条消息后 Claude 回复 "Blue"
    - 每段交互后各有一个 ResultMessage（num_turns=1）
    - 两次 ResultMessage 共享同一个 session_id
usage:
    cd demos && uv run python 07_client_async_input.py
"""

import anyio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)


async def streaming_prompts():
    """异步生成器，按顺序产生多条用户消息。

    每条消息的格式必须是:
    {
        "type": "user",
        "message": {"role": "user", "content": "..."},
        "parent_tool_use_id": None,
        "session_id": "default"
    }
    """
    # 第一条消息
    yield {
        "type": "user",
        "message": {"role": "user", "content": "Remember: my favorite color is blue."},
        "parent_tool_use_id": None,
        "session_id": "default",
    }

    # 模拟延迟后发送第二条消息
    await anyio.sleep(0.5)

    yield {
        "type": "user",
        "message": {"role": "user", "content": "What is my favorite color? Reply with just the color."},
        "parent_tool_use_id": None,
        "session_id": "default",
    }


async def main():
    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        max_turns=2,
    )

    print("=== 流式输入模式演示 ===\n")
    print("通过异步生成器发送多条消息...\n")

    async for message in query(prompt=streaming_prompts(), options=options):
        if isinstance(message, AssistantMessage):
            print("[AssistantMessage]")
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"  Claude: {block.text}")

        elif isinstance(message, ResultMessage):
            print(f"\n[ResultMessage] 轮次={message.num_turns}, 会话={message.session_id}")

    print("\n=== 流式输入完成 ===")


if __name__ == "__main__":
    anyio.run(main)
