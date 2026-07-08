"""
create: 2026-07-08
update: 2026-07-08
description:
    演示从 ResultMessage 获取费用和用量追踪信息的功能。
    发送简单问题 "1+1", 然后展示 ResultMessage 的所有费用/用量字段:
    subtype, total_cost_usd, duration_ms, duration_api_ms, num_turns, is_error,
    session_id, usage (token 详情), model_usage (按模型分列的用量和费用)。
    核心 API: ResultMessage.total_cost_usd/duration_ms/duration_api_ms/usage/model_usage
expect_output:
    - 回答 "Two" 或 "2"
    - subtype: success
    - total_cost_usd > 0
    - duration_ms > 0, duration_api_ms > 0
    - num_turns: 1
    - is_error: False
    - usage 包含 input_tokens, output_tokens, cache 相关字段
    - model_usage 包含模型名和 inputTokens/outputTokens/costUSD
usage:
    cd demos && uv run python 33_cost_tracking.py
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
    options = ClaudeAgentOptions(max_turns=1)

    print("=== 费用与用量追踪演示 ===")
    print("提问: What is 1 + 1? Reply in one word.\n")

    async for msg in query(prompt="What is 1 + 1? Reply in one word.", options=options):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"回答: {block.text}")

        elif isinstance(msg, ResultMessage):
            print("\n--- ResultMessage 费用/用量字段 ---")
            print(f"  subtype:         {msg.subtype}")
            print(f"  total_cost_usd:  ${msg.total_cost_usd or 0:.6f}")
            print(f"  duration_ms:     {msg.duration_ms} ms")
            print(f"  duration_api_ms: {msg.duration_api_ms} ms")
            print(f"  num_turns:       {msg.num_turns}")
            print(f"  is_error:        {msg.is_error}")
            print(f"  session_id:      {msg.session_id}")
            print(f"  usage:           {msg.usage}")
            print(f"  model_usage:     {msg.model_usage}")


if __name__ == "__main__":
    anyio.run(main)
