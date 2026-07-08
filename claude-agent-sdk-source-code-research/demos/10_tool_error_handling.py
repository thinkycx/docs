"""
create: 2026-07-08
update: 2026-07-08
description:
    工具错误处理。演示核心 API: @tool, is_error 返回值。
    定义 divide 和 sqrt 工具，当输入非法时（除以零、负数开方）返回 {"is_error": True} 格式的错误，
    Claude 收到错误后不会崩溃，而是向用户解释错误原因并继续处理合法计算。
    展示自定义工具的优雅错误处理模式。
expect_output:
    - 调用 divide(10, 0) 返回错误 "Division by zero"
    - 调用 sqrt(-4) 返回错误 "Cannot calculate square root of negative number"
    - 调用 divide(10, 2) 返回正确结果 5
    - 调用 sqrt(16) 返回正确结果 4
    - ResultMessage is_error=False（工具错误不导致整体会话错误）
usage:
    cd demos && uv run python 10_tool_error_handling.py
"""

import anyio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    create_sdk_mcp_server,
    query,
    tool,
)


@tool("divide", "Divide two numbers (a / b)", {"a": float, "b": float})
async def divide_tool(args: dict) -> dict:
    """除法工具 - 除以零时返回错误"""
    a = args["a"]
    b = args["b"]

    if b == 0:
        # 返回 is_error: True 告诉 Claude 这是一个错误
        return {
            "content": [{"type": "text", "text": "Error: Division by zero is not allowed."}],
            "is_error": True,
        }

    result = a / b
    return {"content": [{"type": "text", "text": f"{a} / {b} = {result:.4f}"}]}


@tool("sqrt", "Calculate square root of a number", {"value": float})
async def sqrt_tool(args: dict) -> dict:
    """平方根工具 - 负数时返回错误"""
    value = args["value"]

    if value < 0:
        return {
            "content": [{"type": "text", "text": f"Error: Cannot calculate square root of negative number {value}."}],
            "is_error": True,
        }

    import math
    result = math.sqrt(value)
    return {"content": [{"type": "text", "text": f"sqrt({value}) = {result:.4f}"}]}


async def main():
    server = create_sdk_mcp_server(
        name="math",
        version="1.0.0",
        tools=[divide_tool, sqrt_tool],
    )

    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        mcp_servers={"math": server},
        allowed_tools=["divide", "sqrt"],
        max_turns=5,
    )

    print("=== 工具错误处理演示 ===\n")
    print("请求 Claude 执行: 10/0 和 sqrt(-4)，观察错误如何被处理\n")

    async for message in query(
        prompt="Please calculate: 10 divided by 0, and the square root of -4. Then try 10/2 and sqrt(16).",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            print("[AssistantMessage]")
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"  文本: {block.text}")
                elif isinstance(block, ToolUseBlock):
                    print(f"  [工具调用] {block.name}({block.input})")
                elif isinstance(block, ToolResultBlock):
                    error_flag = " [ERROR]" if block.is_error else ""
                    print(f"  [工具结果{error_flag}] {block.content}")
            print()

        elif isinstance(message, ResultMessage):
            print(f"[ResultMessage] 轮次={message.num_turns}, 是否错误={message.is_error}")


if __name__ == "__main__":
    anyio.run(main)
