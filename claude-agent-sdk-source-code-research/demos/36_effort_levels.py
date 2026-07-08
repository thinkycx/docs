"""
create: 2026-07-08
update: 2026-07-08
description:
    演示不同 effort 级别对回答深度的影响，比较 "low" vs "high"。
    展示 EffortLevel 可选值：low, medium, high, xhigh, max。
    核心 API: query(), ClaudeAgentOptions.effort。
expect_output:
    - low effort: 回答 hash table 概念，包含长度统计、cost、duration
    - high effort: 回答同一问题，可能深度不同
    - 两次都打印回答长度(字符)、cost(USD)、duration(ms)、api_duration(ms)
usage:
    cd demos && uv run python 36_effort_levels.py
"""

import anyio
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)


async def run_with_effort(effort_level: str, prompt: str):
    """使用指定 effort 级别运行查询"""
    options = ClaudeAgentOptions(
        effort=effort_level,
        max_turns=1,
    )

    print(f"\n{'='*50}")
    print(f"effort = \"{effort_level}\"")
    print(f"提问: {prompt}")
    print("-" * 50)

    response_text = ""
    result = None

    async for msg in query(prompt=prompt, options=options):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    response_text += block.text
        elif isinstance(msg, ResultMessage):
            result = msg

    print(f"回答: {response_text}")
    print(f"[统计] 回答长度: {len(response_text)} 字符")
    if result:
        print(f"[统计] cost: ${result.total_cost_usd or 0:.6f}, "
              f"duration: {result.duration_ms}ms, "
              f"api_duration: {result.duration_api_ms}ms")


async def main():
    print("=== Effort 级别演示 ===")
    print("可选级别: low, medium, high, xhigh, max")
    print("比较 'low' vs 'high' 对相同问题的回答深度")

    prompt = "Explain what a hash table is."

    # Low effort - 最少思考,最快响应
    await run_with_effort("low", prompt)

    # High effort - 深度推理
    await run_with_effort("high", prompt)


if __name__ == "__main__":
    anyio.run(main)
