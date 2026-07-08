"""
create: 2026-07-08
update: 2026-07-08
description:
    演示 continue_conversation=True 自动恢复当前工作目录最近会话的功能。
    先创建一个新会话建立上下文(记住数字和名字), 然后用 continue_conversation=True
    继续对话验证上下文是否保留。注意 continue_conversation 恢复的是目录下最近的会话,
    不一定是刚创建的那个(如果有更新的会话存在)。
    核心 API: ClaudeAgentOptions(continue_conversation=True), ResultMessage.session_id
expect_output:
    - 第一轮输出 session_id
    - 第二轮使用 continue_conversation=True 获取新/相同的 session_id
    - 输出 "同一会话: True/False" 标识是否恢复到同一会话
    - 最后打印 continue_conversation 与 resume 的区别说明
usage:
    cd demos && uv run python 24_session_continue.py
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
    print("=== Demo: 会话延续 (continue_conversation) ===\n")

    # --- 第一轮对话: 建立上下文 ---
    print("--- 第一轮: 建立对话上下文 ---")

    options_first = ClaudeAgentOptions(
        max_turns=1,
        permission_mode="bypassPermissions",
    )

    session_id = None
    async for msg in query(
        prompt="Remember this number: 42. My name is Alice. Just acknowledge.",
        options=options_first,
    ):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"  [Assistant] {block.text[:100]}")
        elif isinstance(msg, ResultMessage):
            session_id = msg.session_id
            print(f"  [Result] session_id={session_id}")

    if not session_id:
        print("  错误: 未获取到 session_id")
        return

    print(f"\n  已保存 session_id: {session_id}")

    # --- 第二轮对话: 使用 continue_conversation 继续 ---
    print("\n--- 第二轮: 使用 continue_conversation=True 继续 ---")

    options_continue = ClaudeAgentOptions(
        continue_conversation=True,  # 自动恢复当前目录的最近会话
        max_turns=1,
        permission_mode="bypassPermissions",
    )

    async for msg in query(
        prompt="What number did I ask you to remember? What is my name?",
        options=options_continue,
    ):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"  [Assistant] {block.text[:150]}")
        elif isinstance(msg, ResultMessage):
            print(f"  [Result] session_id={msg.session_id}")
            # 验证是否是同一个会话
            same_session = msg.session_id == session_id
            print(f"  [Result] 同一会话: {same_session}")

    print("\n--- 说明 ---")
    print("continue_conversation=True 的行为:")
    print("  1. 自动查找当前工作目录的最近会话")
    print("  2. 恢复该会话的完整对话历史")
    print("  3. 新消息追加到同一会话中")
    print()
    print("与 resume 的区别:")
    print("  - continue_conversation: 自动找最近会话, 不需要知道 session_id")
    print("  - resume: 需要指定具体的 session_id")
    print()
    print("注意事项:")
    print("  - continue_conversation 与 resume 互斥, 不能同时使用")
    print("  - 会话恢复基于工作目录(cwd), 不同目录的会话是隔离的")

    print("\n=== Demo 完成 ===")


if __name__ == "__main__":
    anyio.run(main)
