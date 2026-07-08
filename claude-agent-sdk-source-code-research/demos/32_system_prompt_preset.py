"""
create: 2026-07-08
update: 2026-07-08
description:
    演示使用预设 system_prompt (preset) 和 append 追加指令的功能。
    示例1: 使用 claude_code 预设(Claude Code 默认系统提示);
    示例2: 预设 + append 追加 "始终使用中文回答" 指令。
    核心 API: ClaudeAgentOptions(system_prompt={"type":"preset","preset":"claude_code","append":"..."})
expect_output:
    - 示例1: Claude 以 Claude Code 默认风格回复, 输出费用
    - 示例2: Claude 用中文回答 "2 + 2" (输出 "4" 或中文数字), 输出费用
usage:
    cd demos && uv run python 32_system_prompt_preset.py
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
    # 示例 1: 纯预设模式 (使用 Claude Code 默认系统提示)
    print("=== 示例 1: preset 系统提示 ===")
    options1 = ClaudeAgentOptions(
        system_prompt={"type": "preset", "preset": "claude_code"},
        max_turns=1,
    )

    async for msg in query(prompt="Say hello in one sentence.", options=options1):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"Claude (preset): {block.text}")
        elif isinstance(msg, ResultMessage):
            print(f"--- 完成 (cost: ${msg.total_cost_usd or 0:.6f}) ---\n")

    # 示例 2: 预设 + append 追加指令 (总是用中文回答)
    print("=== 示例 2: preset + append 系统提示 ===")
    options2 = ClaudeAgentOptions(
        system_prompt={
            "type": "preset",
            "preset": "claude_code",
            "append": "Always respond in Chinese. 始终使用中文回答。",
        },
        max_turns=1,
    )

    async for msg in query(prompt="What is 2 + 2?", options=options2):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"Claude (中文): {block.text}")
        elif isinstance(msg, ResultMessage):
            print(f"--- 完成 (cost: ${msg.total_cost_usd or 0:.6f}) ---")


if __name__ == "__main__":
    anyio.run(main)
