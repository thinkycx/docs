"""
create: 2026-07-08
update: 2026-07-08
description:
    演示三种 thinking 配置模式：adaptive（模型自行决定）、enabled（固定 budget_tokens）、disabled（禁用）。
    通过 ThinkingBlock 检测是否收到扩展思考内容。
    核心 API: query(), ClaudeAgentOptions.thinking, ThinkingBlock。
expect_output:
    - adaptive 模式: 收到 ThinkingBlock (内容较短如 "Simple arithmetic question.")
    - enabled 模式 (budget_tokens=2000): 收到 ThinkingBlock
    - disabled 模式: 未收到 ThinkingBlock，打印提示
    - 三种配置均返回正确答案 255 (15*17)
    - 每次打印 cost 和 turns 统计
usage:
    cd demos && uv run python 35_thinking_config.py
"""

import anyio
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ThinkingBlock,
    query,
)


async def run_with_thinking(name: str, thinking_config, prompt: str):
    """使用指定 thinking 配置运行查询"""
    options = ClaudeAgentOptions(
        thinking=thinking_config,
        max_turns=1,
    )

    print(f"\n{'='*50}")
    print(f"配置: {name}")
    print(f"thinking = {thinking_config}")
    print(f"提问: {prompt}")
    print("-" * 50)

    has_thinking = False
    async for msg in query(prompt=prompt, options=options):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, ThinkingBlock):
                    has_thinking = True
                    # 截断显示 thinking 内容
                    preview = block.thinking[:200] + "..." if len(block.thinking) > 200 else block.thinking
                    print(f"[Thinking]: {preview}")
                elif isinstance(block, TextBlock):
                    print(f"[回答]: {block.text[:200]}")

        elif isinstance(msg, ResultMessage):
            print(f"[结果]: cost=${msg.total_cost_usd or 0:.6f}, turns={msg.num_turns}")

    if not has_thinking:
        print("[注意]: 未收到 ThinkingBlock (可能被模型跳过或配置为 disabled)")


async def main():
    print("=== Thinking 配置演示 ===")

    prompt = "What is 15 * 17? Show your reasoning briefly."

    # 1. Adaptive thinking (模型自行决定是否/多少思考)
    await run_with_thinking(
        "Adaptive (模型自行决定)",
        {"type": "adaptive"},
        prompt,
    )

    # 2. Enabled with budget (固定思考 token 预算)
    await run_with_thinking(
        "Enabled (budget_tokens=2000)",
        {"type": "enabled", "budget_tokens": 2000},
        prompt,
    )

    # 3. Disabled (不进行扩展思考)
    await run_with_thinking(
        "Disabled (无扩展思考)",
        {"type": "disabled"},
        prompt,
    )


if __name__ == "__main__":
    anyio.run(main)
