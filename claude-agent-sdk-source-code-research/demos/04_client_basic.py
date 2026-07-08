"""
create: 2026-07-08
update: 2026-07-08
description:
    ClaudeSDKClient 基本用法。演示核心 API: ClaudeSDKClient, connect(),
    receive_response(), disconnect(), async context manager。
    使用 async with 上下文管理器自动管理 Claude Code subprocess 的连接/断开生命周期，
    发送单轮查询并通过 receive_response() 异步迭代接收消息流。
expect_output:
    - AssistantMessage 包含关于日本首都东京的回复
    - 打印模型名称 (如 claude-opus-4-6)
    - ResultMessage 包含 session_id, num_turns=1, total_cost_usd
    - 最后打印 "连接已自动断开"
usage:
    cd demos && uv run python 04_client_basic.py
"""

import anyio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
)


async def main():
    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        max_turns=1,
    )

    print("=== ClaudeSDKClient 基本用法（上下文管理器）===\n")

    # 使用 async with 自动管理 connect/disconnect
    async with ClaudeSDKClient(options) as client:
        # 发送查询
        await client.query("What is the capital of Japan? Reply in one sentence.")

        # 接收响应直到 ResultMessage
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                print("[AssistantMessage]")
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"  回复: {block.text}")
                print(f"  模型: {message.model}")

            elif isinstance(message, ResultMessage):
                print(f"\n[ResultMessage]")
                print(f"  会话ID: {message.session_id}")
                print(f"  轮次: {message.num_turns}")
                print(f"  费用: ${message.total_cost_usd:.6f}" if message.total_cost_usd else "  费用: N/A")

    print("\n=== 连接已自动断开 ===")


if __name__ == "__main__":
    anyio.run(main)
