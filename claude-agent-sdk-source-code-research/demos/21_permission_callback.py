"""
create: 2026-07-08
update: 2026-07-08
description:
    演示 can_use_tool 权限回调: 自定义工具使用权限判断逻辑。
    核心 API: CanUseTool, PermissionResultAllow, PermissionResultDeny, ToolPermissionContext。
    实现了多层权限规则: 自动允许 Read/Grep、拒绝写入 /etc/、重定向写入到安全目录。
    注意: can_use_tool 回调需要 streaming 模式(ClaudeSDKClient)，不能用 query() 直接传 string。
    使用 ClaudeSDKClient streaming 模式运行。
expect_output:
    - 打印权限规则说明
    - Permission Hook 触发并打印 ALLOW(安全的只读工具) 信息
    - Claude 报告文件不存在并解释 can_use_tool 功能
    - 打印 ToolPermissionContext 字段说明
usage:
    cd demos && uv run python 21_permission_callback.py
"""

import anyio
from typing import Any

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    PermissionResultAllow,
    PermissionResultDeny,
    ResultMessage,
    TextBlock,
    ToolPermissionContext,
    ToolUseBlock,
    query,
)


async def permission_callback(
    tool_name: str, tool_input: dict[str, Any], context: ToolPermissionContext
) -> PermissionResultAllow | PermissionResultDeny:
    """
    自定义权限回调:
    - 自动允许 Read 和 Grep
    - 拒绝写入 /etc/
    - 重定向写入到安全目录 (通过 updated_input)
    """
    print(f"  [Permission] tool={tool_name}, context.tool_use_id={context.tool_use_id}")

    # 规则 1: 自动允许 Read 和 Grep
    if tool_name in ("Read", "Grep"):
        print(f"    -> ALLOW (安全的只读工具)")
        return PermissionResultAllow()

    # 规则 2: 拒绝写入 /etc/ 目录
    file_path = tool_input.get("file_path", "") or tool_input.get("path", "")
    if file_path.startswith("/etc/"):
        print(f"    -> DENY (禁止写入 /etc/)")
        return PermissionResultDeny(
            message="Writing to /etc/ is not allowed for security reasons"
        )

    # 规则 3: 重定向写入操作到安全目录
    if tool_name in ("Write", "Edit") and file_path:
        # 通过 updated_input 修改工具输入, 重定向文件路径
        safe_path = f"/tmp/safe_output/{file_path.lstrip('/')}"
        updated_input = {**tool_input, "file_path": safe_path}
        print(f"    -> ALLOW (重定向: {file_path} -> {safe_path})")
        return PermissionResultAllow(updated_input=updated_input)

    # 规则 4: Bash 等其他工具 - 允许
    print(f"    -> ALLOW (默认允许)")
    return PermissionResultAllow()


async def main():
    print("=== Demo: can_use_tool 权限回调 ===\n")

    print("权限规则:")
    print("  1. Read/Grep -> 自动允许")
    print("  2. Write to /etc/* -> 拒绝")
    print("  3. Write to other paths -> 重定向到 /tmp/safe_output/")
    print("  4. 其他工具 -> 允许")
    print()

    # 注意: can_use_tool 只在权限判定为 "ask" 时调用
    # 如果工具已经在 allowed_tools 中, 回调不会被触发
    # 重要: can_use_tool 回调需要 streaming 模式 (ClaudeSDKClient)
    options = ClaudeAgentOptions(
        max_turns=3,
        # 不设置 permission_mode="bypassPermissions", 否则回调不会被调用
        # 也不要把 Write/Edit 加入 allowed_tools
        can_use_tool=permission_callback,
    )

    prompt = "Read the file /tmp/test.txt if it exists. Then briefly explain what can_use_tool does."
    print(f"发送 prompt: '{prompt}'\n")

    # can_use_tool 回调需要 streaming 模式, 必须使用 ClaudeSDKClient
    # 不能使用 query() 直接传 string prompt (会报错)
    async with ClaudeSDKClient(options) as client:
        await client.query(prompt)

        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"  [Assistant] {block.text[:150]}")
                    elif isinstance(block, ToolUseBlock):
                        print(f"  [ToolUse] {block.name}({block.input})")
            elif isinstance(msg, ResultMessage):
                print(f"\n  [Result] session_id={msg.session_id}")
                print(f"  [Result] num_turns={msg.num_turns}")

    print("\n--- ToolPermissionContext 字段说明 ---")
    print("  signal: Any              # 未来的 abort signal 支持")
    print("  suggestions: list        # CLI 的权限建议")
    print("  tool_use_id: str         # 工具调用唯一标识")
    print("  agent_id: str | None     # 子 Agent ID (如果在子 Agent 中)")
    print("  blocked_path: str | None # 触发权限请求的路径")
    print("  decision_reason: str     # 触发原因说明")
    print("  title: str | None        # 权限提示标题")
    print("  display_name: str | None # 工具操作短名称")
    print("  description: str | None  # 人类可读描述")

    print("\n=== Demo 完成 ===")


if __name__ == "__main__":
    anyio.run(main)
