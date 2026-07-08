"""
create: 2026-07-08
update: 2026-07-08
description:
    演示 PreToolUse Hook: 在工具执行前拦截并判断是否允许。
    核心 API: HookMatcher, HookCallback, PreToolUseHookInput, permissionDecision("allow"/"deny")。
    实现了一个安全 Hook，拦截 Bash 工具调用并阻止包含 rm -rf/sudo 等危险模式的命令。
    使用 ClaudeSDKClient streaming 模式运行。
expect_output:
    - 打印 Hook 拦截信息: 允许 echo hello 命令
    - 打印 Hook 阻止信息: 阻止 rm -rf /tmp/test 命令
    - Claude 报告第一个命令成功、第二个命令被阻止
    - 输出 ResultMessage 显示轮次数
usage:
    cd demos && uv run python 13_hook_pre_tool_use.py
"""

import anyio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    HookContext,
    HookInput,
    HookJSONOutput,
    HookMatcher,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
)


# 定义 PreToolUse Hook 回调
async def block_dangerous_commands(
    input: HookInput, tool_use_id: str | None, context: HookContext
) -> HookJSONOutput:
    """
    拦截 Bash 工具调用，阻止危险命令。

    检查 Bash 命令是否包含危险操作（rm -rf, sudo, etc），
    如果是则返回 deny 阻止执行。
    """
    # input 的类型根据 hook_event_name 确定
    tool_name = input.get("tool_name", "")
    tool_input = input.get("tool_input", {})

    print(f"  [Hook] 拦截工具: {tool_name}, tool_use_id={tool_use_id}")

    if tool_name == "Bash":
        command = tool_input.get("command", "")
        # 定义危险命令模式
        dangerous_patterns = ["rm -rf", "sudo", "chmod 777", "dd if="]

        for pattern in dangerous_patterns:
            if pattern in command:
                print(f"  [Hook] 阻止危险命令: {command}")
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"Blocked dangerous command containing '{pattern}'",
                    }
                }

        print(f"  [Hook] 允许命令: {command}")

    # 允许其他工具正常执行
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
        }
    }


async def main():
    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        allowed_tools=["Bash"],
        max_turns=4,
        # 配置 hooks
        hooks={
            "PreToolUse": [
                HookMatcher(
                    matcher="Bash",  # 只匹配 Bash 工具
                    hooks=[block_dangerous_commands],
                ),
            ],
        },
    )

    print("=== PreToolUse Hook 演示: 阻止危险命令 ===\n")

    async with ClaudeSDKClient(options) as client:
        # 请求执行包含安全和危险命令的任务
        await client.query(
            "Run these commands one by one: 'echo hello', then 'rm -rf /tmp/test'. "
            "Report what happened with each."
        )

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"  Claude: {block.text}")
                    elif isinstance(block, ToolUseBlock):
                        print(f"  [工具调用] {block.name}: {block.input}")
                print()

            elif isinstance(message, ResultMessage):
                print(f"[ResultMessage] 轮次={message.num_turns}")

    print("\n=== Hook 成功阻止了危险命令 ===")


if __name__ == "__main__":
    anyio.run(main)
