"""
create: 2026-07-08
update: 2026-07-08
description:
    演示使用 resume=session_id 恢复特定会话的功能。
    三步验证: 1) 创建新会话并记住密码; 2) 用 resume 恢复该会话并验证记忆;
    3) 创建全新会话对比(无法回忆密码)。证明 resume 精确恢复指定会话上下文。
    核心 API: ClaudeAgentOptions(resume=session_id), ResultMessage.session_id
expect_output:
    - 第一轮创建会话并输出 session_id
    - 第二轮 resume 后模型能回忆密码 'openSesame2024', 且 session_id 相同
    - 输出 "恢复成功: True"
    - 第三轮新会话模型无法回忆密码, 输出 "新会话: True"
usage:
    cd demos && uv run python 25_session_resume.py
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
    print("=== Demo: 会话恢复 (resume=session_id) ===\n")

    # --- 第一轮: 创建会话并获取 session_id ---
    print("--- 第一轮: 创建新会话 ---")

    options_new = ClaudeAgentOptions(
        max_turns=1,
        permission_mode="bypassPermissions",
    )

    session_id = None
    async for msg in query(
        prompt="I'm setting a secret password: 'openSesame2024'. Please remember it.",
        options=options_new,
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

    # --- 第二轮: 使用 resume 恢复指定会话 ---
    print(f"\n--- 第二轮: resume='{session_id}' ---")

    options_resume = ClaudeAgentOptions(
        resume=session_id,  # 指定要恢复的会话 ID
        max_turns=1,
        permission_mode="bypassPermissions",
    )

    async for msg in query(
        prompt="What was the secret password I told you?",
        options=options_resume,
    ):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"  [Assistant] {block.text[:100]}")
        elif isinstance(msg, ResultMessage):
            print(f"  [Result] session_id={msg.session_id}")
            print(f"  [Result] 恢复成功: {msg.session_id == session_id}")

    # --- 对比: 不恢复的新会话 ---
    print("\n--- 对比: 全新会话 (不恢复) ---")

    options_fresh = ClaudeAgentOptions(
        max_turns=1,
        permission_mode="bypassPermissions",
    )

    async for msg in query(
        prompt="What was the secret password I told you?",
        options=options_fresh,
    ):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"  [Assistant] {block.text[:100]}")
        elif isinstance(msg, ResultMessage):
            print(f"  [Result] session_id={msg.session_id}")
            print(f"  [Result] 新会话: {msg.session_id != session_id}")

    print("\n--- resume 参数说明 ---")
    print("resume: str | None")
    print("  - None (默认): 创建新会话")
    print("  - session_id: 恢复指定的历史会话")
    print()
    print("行为:")
    print("  1. 从本地文件加载完整对话历史 (~/.claude/projects/<cwd>/<session_id>.jsonl)")
    print("  2. 如果配置了 session_store, 也可以从远程存储加载")
    print("  3. 恢复后的新消息会追加到同一会话")
    print()
    print("相关选项:")
    print("  - resume + fork_session=True: 从该会话 fork 一个新分支")
    print("  - session_store: 支持从外部存储恢复")

    print("\n=== Demo 完成 ===")


if __name__ == "__main__":
    anyio.run(main)
