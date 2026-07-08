"""
create: 2026-07-08
update: 2026-07-08
description:
    使用 @tool 装饰器定义简单工具。演示核心 API: @tool, create_sdk_mcp_server, dict schema。
    定义 add 和 multiply 两个计算器工具，input_schema 用 {参数名: 类型} 字典定义，
    通过 create_sdk_mcp_server 创建进程内 MCP 服务器（无 IPC 开销），
    配置到 ClaudeAgentOptions.mcp_servers 后让 Claude 调用自定义工具完成计算任务。
expect_output:
    - Claude 调用 mcp__calc__add({'a': 17.5, 'b': 32.5}) 得到 50
    - Claude 调用 mcp__calc__multiply({'a': 50, 'b': 3}) 得到 150
    - 最终文本包含 "50" 和 "150" 的计算过程
    - ResultMessage 显示 num_turns=3（两轮工具调用+一轮总结）
usage:
    cd demos && uv run python 08_tool_simple.py
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


# 使用 @tool 装饰器定义工具
# input_schema 使用简单的 dict 映射: {参数名: 类型}
@tool("add", "Add two numbers together", {"a": float, "b": float})
async def add_tool(args: dict) -> dict:
    """加法工具"""
    result = args["a"] + args["b"]
    return {"content": [{"type": "text", "text": f"{args['a']} + {args['b']} = {result}"}]}


@tool("multiply", "Multiply two numbers", {"a": float, "b": float})
async def multiply_tool(args: dict) -> dict:
    """乘法工具"""
    result = args["a"] * args["b"]
    return {"content": [{"type": "text", "text": f"{args['a']} * {args['b']} = {result}"}]}


async def main():
    # 创建 SDK MCP 服务器（进程内运行，无 IPC 开销）
    calculator_server = create_sdk_mcp_server(
        name="calculator",
        version="1.0.0",
        tools=[add_tool, multiply_tool],
    )

    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        # mcp_servers 字典: 键是服务器名称，值是配置
        mcp_servers={"calc": calculator_server},
        # allowed_tools 中使用工具名称让 Claude 可以调用
        allowed_tools=["add", "multiply"],
        max_turns=3,
    )

    print("=== 自定义计算器工具演示 ===\n")

    async for message in query(
        prompt="Calculate 17.5 + 32.5, then multiply the result by 3. Show your work.",
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
                    print(f"  [工具结果] {block.content}")
            print()

        elif isinstance(message, ResultMessage):
            print(f"[ResultMessage] 轮次={message.num_turns}")


if __name__ == "__main__":
    anyio.run(main)
