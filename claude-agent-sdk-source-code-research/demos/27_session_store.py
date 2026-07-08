"""
create: 2026-07-08
update: 2026-07-08
description:
    演示 InMemorySessionStore 会话存储镜像功能。
    创建 InMemorySessionStore 实例, 运行查询后检查存储内容(条目数、类型分布、预览),
    然后演示 store.load() 恢复会话和 store.list_sessions() 列出会话。
    展示 SessionStore 协议的完整接口规范。
    核心 API: InMemorySessionStore, ClaudeAgentOptions(session_store=..., session_store_flush=...)
expect_output:
    - 初始存储条目数为 0
    - 查询后存储 key 数量为 1, 条目数 >= 5
    - 条目类型包含 user, assistant, queue-operation 等
    - store.load() 成功加载记录
    - store.list_sessions() 返回会话列表含 session_id 和 mtime
usage:
    cd demos && uv run python 27_session_store.py
"""

import anyio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    InMemorySessionStore,
    ResultMessage,
    TextBlock,
    query,
)


async def main():
    print("=== Demo: InMemorySessionStore (会话存储) ===\n")

    # 创建 InMemorySessionStore 实例
    store = InMemorySessionStore()

    print("已创建 InMemorySessionStore")
    print(f"  初始存储条目数: {len(store._store)}")
    print()

    # --- 第一轮: 使用 session_store 运行查询 ---
    print("--- 运行查询 (session_store 会自动镜像转录) ---")

    options = ClaudeAgentOptions(
        session_store=store,
        # session_store_flush 控制刷新策略:
        # - "batched" (默认): 每轮结束时刷新
        # - "eager": 每帧都刷新 (近实时)
        session_store_flush="batched",
        max_turns=1,
        permission_mode="bypassPermissions",
    )

    session_id = None
    async for msg in query(
        prompt="Tell me a fun fact about the number 7. Keep it to one sentence.",
        options=options,
    ):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"  [Assistant] {block.text[:100]}")
        elif isinstance(msg, ResultMessage):
            session_id = msg.session_id
            print(f"  [Result] session_id={session_id}")

    # --- 检查存储内容 ---
    print(f"\n--- 存储状态 ---")
    print(f"  存储的 key 数量: {len(store._store)}")

    for key, entries in store._store.items():
        print(f"\n  Key: {key}")
        print(f"  条目数: {len(entries)}")
        print(f"  条目类型分布:")

        # 统计不同类型的条目
        type_counts: dict[str, int] = {}
        for entry in entries:
            entry_type = entry.get("type", "unknown")
            type_counts[entry_type] = type_counts.get(entry_type, 0) + 1

        for t, count in sorted(type_counts.items()):
            print(f"    {t}: {count}")

        # 展示前几个条目的摘要
        print(f"  前 3 条内容预览:")
        for i, entry in enumerate(entries[:3]):
            entry_type = entry.get("type", "?")
            uuid = entry.get("uuid", "?")[:8]
            print(f"    [{i}] type={entry_type}, uuid={uuid}...")

    # --- 使用 store.load() 恢复 ---
    if session_id:
        print(f"\n--- 从 store 加载会话 ---")
        # 构造 SessionKey
        # 注意: project_key 通常由 SDK 自动生成 (基于 cwd)
        for key_str in store._store:
            loaded = await store.load(
                {"project_key": key_str.rsplit("/", 1)[0], "session_id": session_id}
            )
            if loaded:
                print(f"  成功加载 {len(loaded)} 条记录")
                break
        else:
            print("  未找到匹配的会话 (key 可能不同)")

    # --- 列出会话 ---
    print(f"\n--- store.list_sessions() ---")
    for key_str in store._store:
        project_key = key_str.rsplit("/", 1)[0]
        sessions = await store.list_sessions(project_key)
        for s in sessions:
            print(f"  session_id={s['session_id'][:8]}..., mtime={s['mtime']}")
        break

    print("\n--- SessionStore 协议说明 ---")
    print("""
SessionStore 需要实现的方法:
  必需:
    append(key, entries) -> None   # 镜像转录条目
    load(key) -> list | None       # 加载完整会话

  可选 (提供更多功能):
    list_sessions(project_key)     # 列出会话
    list_session_summaries(...)    # 列出会话摘要
    delete(key)                    # 删除会话
    list_subkeys(key)              # 列出子 Agent 转录

SessionKey 结构:
  {"project_key": str, "session_id": str, "subpath"?: str}
""")

    print("=== Demo 完成 ===")


if __name__ == "__main__":
    anyio.run(main)
