"""
create: 2026-07-08
update: 2026-07-08
description:
    演示 Stop Hook: 在 Claude 完成对话时触发，可添加自定义停止摘要。
    核心 API: HookMatcher, StopHookInput, HookJSONOutput(continue_: False, stopReason)。
    通过返回 continue_=False 和 stopReason，展示如何自定义停止行为。
    使用 query() 函数式 API 运行。
expect_output:
    - Claude 回复简短问候
    - Stop Hook 触发，打印 session_id 和 stop_hook_active 状态
    - ResultMessage 显示 session_id、stop_reason、num_turns、is_error
usage:
    cd demos && uv run python 16_hook_stop.py
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


async def stop_hook(
    input_data: HookInput, tool_use_id: str | None, context: HookContext
) -> HookJSONOutput:
    """Stop hook: 当 Claude 停止时添加自定义摘要。"""
    print(f"  [Stop Hook 触发] session_id={input_data['session_id']}")
    print(f"  [Stop Hook] stop_hook_active={input_data.get('stop_hook_active')}")

    # 返回 continue_: False 表示不继续执行, stopReason 是停止原因
    return {
        "continue_": False,
        "stopReason": "Task completed successfully. Custom summary: The agent finished its work.",
    }


async def main():
    print("=== Demo: Stop Hook (自定义停止摘要) ===\n")

    options = ClaudeAgentOptions(
        max_turns=1,
        permission_mode="bypassPermissions",
        hooks={
            "Stop": [
                HookMatcher(
                    matcher=None,  # None 表示匹配所有
                    hooks=[stop_hook],
                )
            ]
        },
    )

    print("发送 prompt: 'Say hello briefly'\n")

    async for msg in query(prompt="Say hello briefly", options=options):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"  [Assistant] {block.text[:100]}")
        elif isinstance(msg, ResultMessage):
            print(f"\n  [Result] session_id={msg.session_id}")
            print(f"  [Result] stop_reason={msg.stop_reason}")
            print(f"  [Result] num_turns={msg.num_turns}")
            print(f"  [Result] is_error={msg.is_error}")

    print("\n=== Demo 完成 ===")


if __name__ == "__main__":
    anyio.run(main)
