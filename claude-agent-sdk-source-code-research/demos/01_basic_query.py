"""
create: 2026-07-08
update: 2026-07-08
description:
    最基本的 query() 用法。演示核心 API: query(), ClaudeAgentOptions, AssistantMessage,
    ResultMessage, TextBlock。发送简单数学问题 "What is 2+2?"，遍历异步消息流，
    打印助手回复文本、模型名称和 ResultMessage 中的费用/轮次/耗时/会话ID 等元信息。
expect_output:
    - AssistantMessage 包含文本 "4"
    - 打印模型名称 (如 claude-opus-4-6)
    - ResultMessage 显示 num_turns=1
    - ResultMessage 显示 is_error=False
    - ResultMessage 包含 total_cost_usd, duration_ms, session_id
usage:
    cd demos && uv run python 01_basic_query.py
"""

import anyio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)


async def main():
    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        max_turns=1,
    )

    print("=== 发送问题: What is 2+2? ===\n")

    async for message in query(prompt="What is 2+2? Reply with just the number.", options=options):
        if isinstance(message, AssistantMessage):
            print("[AssistantMessage]")
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"  文本: {block.text}")
            print(f"  模型: {message.model}")

        elif isinstance(message, ResultMessage):
            print(f"\n[ResultMessage]")
            print(f"  费用: ${message.total_cost_usd:.6f}" if message.total_cost_usd else "  费用: N/A")
            print(f"  轮次: {message.num_turns}")
            print(f"  耗时: {message.duration_ms}ms")
            print(f"  是否错误: {message.is_error}")
            print(f"  会话ID: {message.session_id}")


if __name__ == "__main__":
    anyio.run(main)
