"""
create: 2026-07-08
update: 2026-07-08
description:
    演示使用自定义字符串 system_prompt 改变 Claude 回复风格。
    设置海盗风格系统提示, 让 Claude 用海盗口吻回答 "What is Python?"。
    核心 API: ClaudeAgentOptions(system_prompt="自定义字符串")
expect_output:
    - 输出包含 "Arrr" 或海盗风格用语
    - 回答内容涉及 Python 编程语言
    - 输出费用信息 cost: $X.XXXXXX
usage:
    cd demos && uv run python 31_system_prompt_string.py
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
        system_prompt="You are a pirate captain. Always respond in pirate speak with 'Arrr!' and nautical metaphors. Keep responses brief.",
        max_turns=1,
    )

    print("=== 自定义字符串 system_prompt 演示 ===")
    print("系统提示: 以海盗风格回应")
    print(f"提问: What is Python?\n")

    async for msg in query(prompt="What is Python?", options=options):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"海盗 Claude: {block.text}")
        elif isinstance(msg, ResultMessage):
            print(f"\n--- 完成 (cost: ${msg.total_cost_usd or 0:.6f}) ---")


if __name__ == "__main__":
    anyio.run(main)
