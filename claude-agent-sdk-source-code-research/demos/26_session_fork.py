"""
create: 2026-07-08
update: 2026-07-08
description:
    演示使用 fork_session=True 从现有会话创建分支的功能。
    创建原始会话(确定技术栈), 然后从同一会话 fork 两个分支分别讨论不同认证方案(JWT vs Cookies)。
    验证 fork 产生独立 session_id, 且继承原始上下文。
    核心 API: ClaudeAgentOptions(resume=session_id, fork_session=True)
expect_output:
    - 原始会话输出 original_session_id
    - Fork A 输出新 session_id, 讨论 JWT, "新会话 (不同于原始): True"
    - Fork B 输出新 session_id, 讨论 cookies, "新会话 (不同于 Fork A): True"
    - 三个 session_id 互不相同
    - 最后打印会话关系总结和 fork_session 使用模式
usage:
    cd demos && uv run python 26_session_fork.py
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
    print("=== Demo: 会话分叉 (fork_session) ===\n")

    # --- 第一轮: 创建原始会话 ---
    print("--- 第一轮: 创建原始会话 ---")

    options_original = ClaudeAgentOptions(
        max_turns=1,
        permission_mode="bypassPermissions",
    )

    original_session_id = None
    async for msg in query(
        prompt="We are building a web app. The tech stack is: React + FastAPI + PostgreSQL. Acknowledge briefly.",
        options=options_original,
    ):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"  [Assistant] {block.text[:100]}")
        elif isinstance(msg, ResultMessage):
            original_session_id = msg.session_id
            print(f"  [Result] original_session_id={original_session_id}")

    if not original_session_id:
        print("  错误: 未获取到 session_id")
        return

    # --- 第二轮: Fork 会话 - 方案 A ---
    print(f"\n--- Fork A: 从原始会话分叉 (探索方案 A) ---")

    options_fork_a = ClaudeAgentOptions(
        resume=original_session_id,  # 从哪个会话分叉
        fork_session=True,  # 创建新分支, 不修改原始会话
        max_turns=1,
        permission_mode="bypassPermissions",
    )

    fork_a_session_id = None
    async for msg in query(
        prompt="For authentication, should we use JWT tokens? Give a one-sentence recommendation.",
        options=options_fork_a,
    ):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"  [Fork A] {block.text[:150]}")
        elif isinstance(msg, ResultMessage):
            fork_a_session_id = msg.session_id
            print(f"  [Result] fork_a_session_id={fork_a_session_id}")
            print(f"  [Result] 新会话 (不同于原始): {fork_a_session_id != original_session_id}")

    # --- 第三轮: Fork 会话 - 方案 B ---
    print(f"\n--- Fork B: 从同一原始会话再次分叉 (探索方案 B) ---")

    options_fork_b = ClaudeAgentOptions(
        resume=original_session_id,  # 同一个原始会话
        fork_session=True,  # 再次创建新分支
        max_turns=1,
        permission_mode="bypassPermissions",
    )

    fork_b_session_id = None
    async for msg in query(
        prompt="For authentication, should we use session cookies? Give a one-sentence recommendation.",
        options=options_fork_b,
    ):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"  [Fork B] {block.text[:150]}")
        elif isinstance(msg, ResultMessage):
            fork_b_session_id = msg.session_id
            print(f"  [Result] fork_b_session_id={fork_b_session_id}")
            print(f"  [Result] 新会话 (不同于 Fork A): {fork_b_session_id != fork_a_session_id}")

    # --- 总结 ---
    print("\n--- 会话关系 ---")
    print(f"  原始会话:  {original_session_id}")
    print(f"  Fork A:    {fork_a_session_id}")
    print(f"  Fork B:    {fork_b_session_id}")
    print(f"  三个会话互相独立, 但 Fork A/B 都继承了原始会话的上下文")

    print("\n--- fork_session 使用模式 ---")
    print("""
# 基本 Fork: 从指定会话分叉
options = ClaudeAgentOptions(
    resume="original-session-id",
    fork_session=True,
)

# Fork 的特点:
# 1. 新会话获得新的 session_id
# 2. 包含原始会话的完整对话历史
# 3. 后续消息只在新会话中, 不影响原始会话
# 4. 可以从同一会话多次 Fork

# 应用场景:
# - A/B 测试不同对话策略
# - 从同一上下文尝试不同方案
# - 保留原始对话不变, 创建实验分支
# - 多用户从同一模板会话开始
""")

    print("=== Demo 完成 ===")


if __name__ == "__main__":
    anyio.run(main)
