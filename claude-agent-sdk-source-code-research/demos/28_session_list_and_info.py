"""
create: 2026-07-08
update: 2026-07-08
description:
    演示 list_sessions() 和 get_session_messages() 浏览会话历史的功能。
    先创建一个会话确保有数据, 然后: 1) list_sessions() 列出所有会话(含元数据);
    2) list_sessions(directory=cwd) 按目录过滤; 3) 分页查询;
    4) get_session_messages() 获取特定会话的完整消息列表。
    核心 API: list_sessions(directory=..., limit=..., offset=...), get_session_messages(session_id)
expect_output:
    - 创建新会话输出 session_id
    - list_sessions() 返回总会话数 > 0, 含 session_id/summary/last_modified/cwd 等字段
    - list_sessions(directory=cwd) 返回当前目录会话数
    - 分页查询返回指定数量的会话
    - get_session_messages() 返回消息列表, 含 type/uuid/role/content 等字段
usage:
    cd demos && uv run python 28_session_list_and_info.py
"""

import anyio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    SDKSessionInfo,
    TextBlock,
    get_session_messages,
    list_sessions,
    query,
)


async def main():
    print("=== Demo: 浏览会话历史 ===\n")

    # --- 先创建一个会话, 确保有数据 ---
    print("--- 创建一个新会话 (确保有数据) ---")

    options = ClaudeAgentOptions(
        max_turns=1,
        permission_mode="bypassPermissions",
    )

    new_session_id = None
    async for msg in query(
        prompt="The capital of Japan is Tokyo. Confirm this in one word.",
        options=options,
    ):
        if isinstance(msg, ResultMessage):
            new_session_id = msg.session_id
            print(f"  新会话: {new_session_id}")

    # --- list_sessions: 列出所有会话 ---
    print("\n--- list_sessions() - 列出所有会话 ---")

    # 不指定 directory: 返回所有项目的会话
    all_sessions = list_sessions()
    print(f"  总会话数: {len(all_sessions)}")

    # 展示前 5 个会话
    for i, session in enumerate(all_sessions[:5]):
        print(f"\n  会话 {i+1}:")
        print(f"    session_id: {session.session_id}")
        print(f"    summary: {session.summary[:60] if session.summary else 'N/A'}")
        print(f"    last_modified: {session.last_modified}")
        print(f"    custom_title: {session.custom_title}")
        print(f"    first_prompt: {(session.first_prompt or '')[:50]}")
        print(f"    cwd: {session.cwd}")
        print(f"    tag: {session.tag}")

    # --- list_sessions 带 directory 参数 ---
    print("\n--- list_sessions(directory='.') - 当前目录的会话 ---")
    import os

    cwd = os.getcwd()
    local_sessions = list_sessions(directory=cwd)
    print(f"  当前目录 ({cwd}) 的会话数: {len(local_sessions)}")

    # --- list_sessions 带分页参数 ---
    print("\n--- list_sessions(limit=2, offset=0) - 分页 ---")
    page1 = list_sessions(limit=2, offset=0)
    print(f"  第 1 页 (2条): {[s.session_id[:8] + '...' for s in page1]}")

    page2 = list_sessions(limit=2, offset=2)
    print(f"  第 2 页 (2条): {[s.session_id[:8] + '...' for s in page2]}")

    # --- get_session_messages: 获取会话消息 ---
    print("\n--- get_session_messages() - 获取会话消息 ---")

    if new_session_id:
        messages = get_session_messages(new_session_id)
        print(f"  会话 {new_session_id[:8]}... 的消息数: {len(messages)}")

        for i, msg in enumerate(messages):
            print(f"\n  消息 {i+1}:")
            print(f"    type: {msg.type}")
            print(f"    uuid: {msg.uuid[:8]}...")
            # msg.message 是原始 Anthropic API 消息格式
            if isinstance(msg.message, dict):
                role = msg.message.get("role", "?")
                content = msg.message.get("content", "")
                if isinstance(content, str):
                    print(f"    role: {role}")
                    print(f"    content: {content[:80]}")
                elif isinstance(content, list):
                    print(f"    role: {role}")
                    print(f"    content blocks: {len(content)}")
    else:
        print("  跳过 (无可用会话)")

    # --- SDKSessionInfo 字段说明 ---
    print("\n--- SDKSessionInfo 完整字段 ---")
    print("  session_id: str       # 会话 UUID")
    print("  summary: str          # 显示摘要")
    print("  last_modified: int    # 最后修改时间 (ms since epoch)")
    print("  file_size: int | None # 文件大小 (字节)")
    print("  custom_title: str     # 自定义标题")
    print("  first_prompt: str     # 第一条用户消息")
    print("  git_branch: str       # Git 分支")
    print("  cwd: str              # 工作目录")
    print("  tag: str              # 用户标签")
    print("  created_at: int       # 创建时间 (ms since epoch)")

    print("\n=== Demo 完成 ===")


if __name__ == "__main__":
    anyio.run(main)
