"""
create: 2026-07-08
update: 2026-07-08
description:
    中断正在进行的任务。演示核心 API: ClaudeSDKClient.interrupt(), 任务中断后发送新查询。
    发送一个需要多轮工具调用的长任务，收到第一条 AssistantMessage 后立即调用 interrupt()
    中断执行，然后验证中断后仍可发送新查询，证明 interrupt 不会破坏会话状态。
expect_output:
    - 收到第一条助手消息后打印 "发送中断信号"
    - ResultMessage 显示被中断，num_turns >= 1
    - 中断后新查询正常返回 "Ready for new tasks!"
    - 最后打印 "中断不影响后续交互"
usage:
    cd demos && uv run python 06_client_interrupt.py
"""

import anyio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
)


async def main():
    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        allowed_tools=["Bash"],
        max_turns=5,
    )

    print("=== 中断演示 ===\n")

    async with ClaudeSDKClient(options) as client:
        # 发送一个可能需要多轮的任务
        print("--- 发送长任务: 列出多个目录 ---")
        await client.query(
            "List files in /tmp, /var, and /etc one by one using separate ls commands."
        )

        # 接收几条消息后中断
        msg_count = 0
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                msg_count += 1
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"  [{msg_count}] 文本: {block.text[:100]}...")
                    elif isinstance(block, ToolUseBlock):
                        print(f"  [{msg_count}] 工具调用: {block.name}")

                # 收到第一条助手消息后立即中断
                if msg_count >= 1:
                    print("\n  >>> 发送中断信号 <<<\n")
                    await client.interrupt()

            elif isinstance(message, ResultMessage):
                print(f"  [ResultMessage] 被中断, num_turns={message.num_turns}")
                break

        # 中断后发送新查询
        print("\n--- 中断后发送新查询 ---")
        await client.query("Just say 'Ready for new tasks!' Nothing else.")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"  Claude: {block.text}")
            elif isinstance(message, ResultMessage):
                print(f"  [ResultMessage] num_turns={message.num_turns}")

    print("\n=== 中断不影响后续交互 ===")


if __name__ == "__main__":
    anyio.run(main)
