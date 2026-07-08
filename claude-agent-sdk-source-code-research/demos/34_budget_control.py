"""
create: 2026-07-08
update: 2026-07-08
description:
    演示预算控制机制。设置极低的 max_budget_usd ($0.001) 触发预算超限。
    当预算耗尽时，SDK 抛出包含 "Reached maximum budget" 的异常。
    核心 API: query(), ClaudeAgentOptions.max_budget_usd, Exception 处理。
expect_output:
    - 打印 max_budget_usd = 0.001
    - 回答被截断显示 (前100字符)
    - 捕获预算超限异常，打印 "Claude Code returned an error result: Reached maximum budget ($0.001)"
    - 说明 SDK 在预算超限时抛出异常而非返回 ResultMessage
usage:
    cd demos && uv run python 34_budget_control.py
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
    # 设置极低预算 $0.001, 尝试触发预算超限
    options = ClaudeAgentOptions(
        max_budget_usd=0.001,
        max_turns=10,  # 允许多轮以增加触发几率
    )

    print("=== 预算控制演示 ===")
    print(f"max_budget_usd = {options.max_budget_usd}")
    print("提问: Write a very long essay about the history of computing.\n")

    result_msg = None
    try:
        async for msg in query(
            prompt="Write a very long and detailed essay about the entire history of computing from ancient times to present day. Include every major figure and invention.",
            options=options,
        ):
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        # 只打印前 100 个字符
                        preview = block.text[:100] + "..." if len(block.text) > 100 else block.text
                        print(f"回答 (截断): {preview}")

            elif isinstance(msg, ResultMessage):
                result_msg = msg

    except Exception as e:
        error_str = str(e)
        if "maximum budget" in error_str.lower() or "budget" in error_str.lower():
            print(f"\n[检测到] 预算超限异常!")
            print(f"  异常信息: {error_str}")
            print(f"  异常类型: {type(e).__name__}")
            print("\n  说明: SDK 在预算超限时抛出异常而非返回 ResultMessage")
            print("  处理模式: 使用 try/except 捕获包含 'budget' 的异常")
        else:
            print(f"\n[异常] {type(e).__name__}: {error_str}")
        return

    if result_msg:
        print("\n--- ResultMessage ---")
        print(f"  subtype:        {result_msg.subtype}")
        print(f"  is_error:       {result_msg.is_error}")
        print(f"  total_cost_usd: ${result_msg.total_cost_usd or 0:.6f}")
        print(f"  num_turns:      {result_msg.num_turns}")

        if result_msg.subtype == "error_max_budget_usd":
            print("\n  [检测到] 预算超限! subtype == 'error_max_budget_usd'")
        elif result_msg.subtype == "success":
            print("\n  [注意] 查询在预算内完成。尝试更复杂的提示以触发预算超限。")
        else:
            print(f"\n  [其他] 结果子类型: {result_msg.subtype}")


if __name__ == "__main__":
    anyio.run(main)
