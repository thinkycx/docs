"""
create: 2026-07-08
update: 2026-07-08
description:
    演示 Notification Hook: 捕获 Agent 发出的通知事件。
    核心 API: HookMatcher, NotificationHookInput, NotificationHookSpecificOutput。
    注册一个通知 Hook 来捕获 Agent 的通知(如长任务完成、需要用户关注等)。
    使用 query() 函数式 API 运行。注意：简单查询通常不会触发通知。
expect_output:
    - Claude 回复简单计算结果(如 "4")
    - 打印捕获到的通知数量(简单查询通常为 0)
    - 打印 NotificationHookInput 结构说明
usage:
    cd demos && uv run python 17_hook_notification.py
"""

import anyio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    HookContext,
    HookInput,
    HookJSONOutput,
    HookMatcher,
    ResultMessage,
    TextBlock,
    query,
)


# 收集通知的列表
captured_notifications: list[dict] = []


async def notification_hook(
    input_data: HookInput, tool_use_id: str | None, context: HookContext
) -> HookJSONOutput:
    """Notification hook: 捕获并记录 Agent 的通知。"""
    # NotificationHookInput 包含以下字段:
    # - hook_event_name: "Notification"
    # - session_id: 会话ID
    # - message: 通知消息内容
    # - title: 通知标题 (可选)
    # - notification_type: 通知类型
    # - transcript_path: 转录文件路径
    # - cwd: 工作目录

    notification_info = {
        "message": input_data.get("message", ""),
        "title": input_data.get("title", ""),
        "notification_type": input_data.get("notification_type", ""),
        "session_id": input_data.get("session_id", ""),
    }

    captured_notifications.append(notification_info)

    print(f"  [Notification Hook 触发]")
    print(f"    message: {notification_info['message']}")
    print(f"    title: {notification_info['title']}")
    print(f"    type: {notification_info['notification_type']}")

    # 返回基本确认, 不做任何修改
    return {
        "continue_": True,
        "hookSpecificOutput": {
            "hookEventName": "Notification",
            "additionalContext": "Notification captured by SDK hook",
        },
    }


async def main():
    print("=== Demo: Notification Hook (通知捕获) ===\n")

    options = ClaudeAgentOptions(
        max_turns=2,
        permission_mode="bypassPermissions",
        hooks={
            "Notification": [
                HookMatcher(
                    matcher=None,  # 匹配所有通知
                    hooks=[notification_hook],
                )
            ]
        },
    )

    # 注意: 通知通常在特定场景下触发(如长任务完成)
    # 这里使用一个简单的 prompt, 通知可能不一定触发
    prompt = "What is 2 + 2? Answer briefly."
    print(f"发送 prompt: '{prompt}'\n")

    async for msg in query(prompt=prompt, options=options):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"  [Assistant] {block.text[:100]}")
        elif isinstance(msg, ResultMessage):
            print(f"\n  [Result] session_id={msg.session_id}")

    print(f"\n--- 捕获到的通知数量: {len(captured_notifications)} ---")
    for i, notif in enumerate(captured_notifications):
        print(f"  通知 {i+1}: {notif}")

    print("\n说明: NotificationHookInput 结构:")
    print("  - hook_event_name: 'Notification'")
    print("  - message: str         # 通知消息内容")
    print("  - title: str           # 通知标题 (可选)")
    print("  - notification_type: str  # 通知类型")
    print("  - session_id: str      # 会话ID")
    print("  - transcript_path: str # 转录路径")
    print("  - cwd: str             # 工作目录")

    print("\n=== Demo 完成 ===")


if __name__ == "__main__":
    anyio.run(main)
