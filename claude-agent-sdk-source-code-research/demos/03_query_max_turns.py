"""
create: 2026-07-08
update: 2026-07-08
description:
    限制对话轮次。演示核心 API: query(), ClaudeAgentOptions.max_turns,
    ResultMessage.num_turns, ResultMessage.stop_reason。
    第一部分: max_turns=1 限制为一轮，Claude 直接输出结果后停止 (stop_reason=end_turn)。
    第二部分: max_turns=2 允许工具调用后继续，Claude 先调 Bash 再总结 (num_turns=2)。
expect_output:
    - 第一部分: num_turns=1, stop_reason=end_turn, 输出 1-10 数字
    - 第二部分: num_turns=2, stop_reason=end_turn
    - is_error=False
usage:
    cd demos && uv run python 03_query_max_turns.py
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
    # max_turns=1 意味着只允许一轮对话（一个用户消息 + 一个助手回复）
    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        max_turns=1,
    )

    print("=== max_turns=1: 只允许一轮对话 ===\n")

    async for message in query(
        prompt="Count from 1 to 10, one number per line.",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            print("[AssistantMessage]")
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"  {block.text[:300]}")

        elif isinstance(message, ResultMessage):
            print(f"\n[ResultMessage]")
            print(f"  实际轮次 (num_turns): {message.num_turns}")
            print(f"  停止原因 (stop_reason): {message.stop_reason}")
            print(f"  是否错误: {message.is_error}")
            print(f"  耗时: {message.duration_ms}ms")

    print("\n=== 对比: max_turns=2 允许工具使用后继续 ===\n")

    options_2 = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        allowed_tools=["Bash"],
        max_turns=2,
    )

    async for message in query(
        prompt="Run 'echo hello' then tell me what you see.",
        options=options_2,
    ):
        if isinstance(message, ResultMessage):
            print(f"[ResultMessage] num_turns={message.num_turns}, stop_reason={message.stop_reason}")


if __name__ == "__main__":
    anyio.run(main)
