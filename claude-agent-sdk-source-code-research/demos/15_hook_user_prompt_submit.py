"""
create: 2026-07-08
update: 2026-07-08
description:
    演示 UserPromptSubmit Hook: 在每次用户提交消息时自动注入额外上下文。
    核心 API: HookMatcher, UserPromptSubmitHookInput, additionalContext。
    实现了一个上下文注入 Hook，在用户消息提交时自动附加当前时间、语言偏好、安全规则等信息。
    使用 ClaudeSDKClient streaming 模式运行，演示多轮对话中 Hook 的持续作用。
expect_output:
    - 第1条消息: Hook 触发并注入上下文，Claude 用中文回复当前时间
    - 第2条消息: Hook 再次触发并注入上下文，Claude 用中文简短回复
    - 每次 Hook 触发打印用户消息摘要和注入提示
usage:
    cd demos && uv run python 15_hook_user_prompt_submit.py
"""

import datetime

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
)


async def inject_context_on_prompt(
    input: HookInput, tool_use_id: str | None, context: HookContext
) -> HookJSONOutput:
    """
    UserPromptSubmit Hook: 在每个用户消息中注入额外上下文。

    用途:
    - 注入当前时间戳
    - 注入项目规范或安全规则
    - 注入用户偏好设定
    - 注入环境信息
    """
    prompt = input.get("prompt", "")
    session_id = input.get("session_id", "")

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"  [Hook] 用户提交消息: '{prompt[:50]}...' (session={session_id})")
    print(f"  [Hook] 注入额外上下文...")

    # 构建要注入的上下文信息
    additional_context = (
        f"[System Context - Injected by UserPromptSubmit Hook]\n"
        f"- Current time: {now}\n"
        f"- Language preference: Chinese (Simplified)\n"
        f"- Security rule: Never reveal internal paths or credentials\n"
        f"- Response style: Be concise, reply in 1-2 sentences"
    )

    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": additional_context,
        }
    }


async def main():
    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        max_turns=1,
        hooks={
            "UserPromptSubmit": [
                HookMatcher(
                    matcher=None,  # 匹配所有用户消息
                    hooks=[inject_context_on_prompt],
                ),
            ],
        },
    )

    print("=== UserPromptSubmit Hook 演示: 自动注入上下文 ===\n")

    async with ClaudeSDKClient(options) as client:
        # 第一次查询
        print("--- 第1条消息 ---")
        await client.query("What time is it and what language should you respond in?")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"  Claude: {block.text}")
            elif isinstance(message, ResultMessage):
                print(f"  [结束] 轮次={message.num_turns}\n")

        # 第二次查询 - Hook 会再次注入上下文
        print("--- 第2条消息 ---")
        await client.query("Tell me something about yourself.")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"  Claude: {block.text}")
            elif isinstance(message, ResultMessage):
                print(f"  [结束] 轮次={message.num_turns}")

    print("\n=== Hook 在每次用户消息时都注入了上下文 ===")


if __name__ == "__main__":
    anyio.run(main)
