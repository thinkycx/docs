"""
create: 2026-07-08
update: 2026-07-08
description:
    演示模型选择机制。通过 AssistantMessage.model 字段验证实际使用的模型。
    展示 model 和 fallback_model 参数配置。
    核心 API: query(), ClaudeAgentOptions.model, ClaudeAgentOptions.fallback_model,
    AssistantMessage.model, ResultMessage.model_usage。
expect_output:
    - 第一次查询: model=None (使用环境默认模型)，打印实际使用模型名
    - 第二次查询: model=None + fallback_model="claude-haiku-4"
    - 每次打印 AssistantMessage.model 字段 (如 claude-opus-4-6)
    - 打印 cost 和 model_usage (含 inputTokens, outputTokens, cacheReadInputTokens 等)
usage:
    cd demos && uv run python 37_model_selection.py
"""

import anyio
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)


async def run_with_model(model: str | None = None, fallback_model: str | None = None):
    """使用指定模型运行查询"""
    options = ClaudeAgentOptions(
        model=model,
        fallback_model=fallback_model,
        max_turns=1,
    )

    print(f"\n{'='*50}")
    print(f"model = \"{model}\"")
    print(f"fallback_model = {repr(fallback_model)}")
    print("-" * 50)

    async for msg in query(prompt="Say 'hello' and nothing else.", options=options):
        if isinstance(msg, AssistantMessage):
            # AssistantMessage.model 显示实际使用的模型
            print(f"  实际使用模型: {msg.model}")
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"  回答: {block.text}")

        elif isinstance(msg, ResultMessage):
            print(f"  cost: ${msg.total_cost_usd or 0:.6f}")
            if msg.model_usage:
                print(f"  model_usage: {msg.model_usage}")


async def main():
    print("=== 模型选择演示 ===")
    print("通过 AssistantMessage.model 字段验证实际响应的模型")
    print("注: model 参数传入后由 CLI 转发给 API，实际可用模型取决于环境配置")

    # 使用默认模型 (model=None 表示由 CLI/环境决定)
    await run_with_model(model=None)

    # 设置 fallback_model (主模型仍为默认)
    await run_with_model(
        model=None,
        fallback_model="claude-haiku-4",
    )


if __name__ == "__main__":
    anyio.run(main)
