"""
create: 2026-07-08
update: 2026-07-08
description:
    演示 PostToolUse Hook: 在工具执行后拦截结果，记录日志并检测错误。
    核心 API: HookMatcher, PostToolUseHookInput, additionalContext, systemMessage。
    实现了一个监控 Hook，记录每次工具调用的输入输出，
    并在检测到 error/permission denied 等错误模式时通过 additionalContext 向 Claude 提供额外上下文。
    使用 ClaudeSDKClient streaming 模式运行。
expect_output:
    - 打印 PostHook 记录工具调用 (echo hello world)
    - Claude 报告 echo 成功、cat 非存在文件失败
    - 最后打印收集的工具调用日志(至少1条)
usage:
    cd demos && uv run python 14_hook_post_tool_use.py
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

# 模拟日志记录
tool_usage_log: list[dict] = []


async def log_and_check_tool_output(
    input: HookInput, tool_use_id: str | None, context: HookContext
) -> HookJSONOutput:
    """
    PostToolUse Hook: 记录工具输出并检测错误。

    功能:
    1. 记录每次工具调用的输入和输出到日志
    2. 检测输出中是否包含错误信号
    3. 如果检测到错误，通过 additionalContext 向 Claude 提供额外上下文
    """
    tool_name = input.get("tool_name", "")
    tool_input = input.get("tool_input", {})
    tool_response = input.get("tool_response", "")

    # 记录到日志
    log_entry = {
        "tool": tool_name,
        "input": tool_input,
        "output_preview": str(tool_response)[:100],
    }
    tool_usage_log.append(log_entry)
    print(f"  [PostHook] 记录工具调用 #{len(tool_usage_log)}: {tool_name}")

    # 检测错误模式
    response_str = str(tool_response).lower()
    error_patterns = ["error", "permission denied", "no such file", "command not found"]

    detected_errors = [p for p in error_patterns if p in response_str]

    if detected_errors:
        print(f"  [PostHook] 检测到错误信号: {detected_errors}")
        # 通过 additionalContext 向 Claude 提供额外上下文
        # 通过 systemMessage 向用户显示警告
        return {
            "systemMessage": f"[Monitor] Tool '{tool_name}' produced error output.",
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": (
                    f"NOTE: The command produced an error. "
                    f"Detected patterns: {detected_errors}. "
                    f"Consider trying an alternative approach."
                ),
            },
        }

    # 正常情况，不做额外处理
    return {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
        }
    }


async def main():
    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        allowed_tools=["Bash"],
        max_turns=4,
        hooks={
            "PostToolUse": [
                HookMatcher(
                    matcher=None,  # None 匹配所有工具
                    hooks=[log_and_check_tool_output],
                ),
            ],
        },
    )

    print("=== PostToolUse Hook 演示: 日志记录与错误检测 ===\n")

    async with ClaudeSDKClient(options) as client:
        await client.query(
            "Run 'echo hello world', then try 'cat /nonexistent_file_xyz'. Be brief about results."
        )

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"  Claude: {block.text[:200]}")
                    elif isinstance(block, ToolUseBlock):
                        print(f"  [工具调用] {block.name}: {block.input}")
                print()

            elif isinstance(message, ResultMessage):
                print(f"[ResultMessage] 轮次={message.num_turns}")

    # 打印收集的日志
    print(f"\n=== 工具调用日志 ({len(tool_usage_log)} 条) ===")
    for i, entry in enumerate(tool_usage_log, 1):
        print(f"  {i}. [{entry['tool']}] input={entry['input']}")
        print(f"     output: {entry['output_preview']}")


if __name__ == "__main__":
    anyio.run(main)
