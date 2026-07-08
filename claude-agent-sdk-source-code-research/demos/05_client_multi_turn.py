"""
create: 2026-07-08
update: 2026-07-08
description:
    多轮对话。演示核心 API: ClaudeSDKClient.query() 多次调用, receive_response(),
    上下文保持。在同一个 ClaudeSDKClient 会话中发送三轮消息:
    第1轮告诉名字 -> 第2轮验证记忆 -> 第3轮基于上下文生成问候。
    证明同一 client 会话中 Claude 能保持完整对话上下文。
expect_output:
    - 第1轮: Claude 回复包含 "Alice" 的确认
    - 第2轮: Claude 回复 "Alice"
    - 第3轮: Claude 回复 "Hello Alice!"
    - 每轮 num_turns=1
usage:
    cd demos && uv run python 05_client_multi_turn.py
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

    print("=== 多轮对话演示 ===\n")

    async with ClaudeSDKClient(options) as client:
        # 第一轮: 告诉 Claude 一个信息
        print("--- 第1轮: 告诉 Claude 我的名字 ---")
        await client.query("My name is Alice. Remember it. Just say 'Got it, Alice!'")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"  Claude: {block.text}")
            elif isinstance(message, ResultMessage):
                print(f"  [轮次: {message.num_turns}]")

        # 第二轮: 验证 Claude 记住了上下文
        print("\n--- 第2轮: 询问 Claude 是否记住 ---")
        await client.query("What is my name? Reply with just the name.")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"  Claude: {block.text}")
            elif isinstance(message, ResultMessage):
                print(f"  [轮次: {message.num_turns}]")

        # 第三轮: 进一步验证上下文
        print("\n--- 第3轮: 基于上下文提问 ---")
        await client.query("Say 'Hello' followed by my name with an exclamation mark.")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"  Claude: {block.text}")
            elif isinstance(message, ResultMessage):
                print(f"  [轮次: {message.num_turns}]")

    print("\n=== 会话结束，上下文在同一会话中保持 ===")


if __name__ == "__main__":
    anyio.run(main)
