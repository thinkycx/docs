"""
create: 2026-07-08
update: 2026-07-08
description:
    使用内置工具的 query()。演示核心 API: query(), allowed_tools, ToolUseBlock,
    ToolResultBlock。配置 allowed_tools=["Bash", "Read"] 让 Claude 具备文件系统操作能力，
    请求列出当前目录文件，观察 ToolUseBlock（工具调用请求）和 ToolResultBlock（工具执行结果）的结构。
expect_output:
    - AssistantMessage 中包含 ToolUseBlock，工具名为 "Bash"
    - ToolUseBlock.input 包含 ls 命令
    - 最终 AssistantMessage 包含目录文件列表的文本摘要
    - ResultMessage 显示 num_turns=2（一轮工具调用+一轮总结）
usage:
    cd demos && uv run python 02_query_with_tools.py
"""

import anyio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    query,
)


async def main():
    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        allowed_tools=["Bash", "Read"],
        max_turns=3,
    )

    print("=== 请求 Claude 列出当前目录文件 ===\n")

    async for message in query(
        prompt="List files in the current directory using ls -la. Be brief.",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            print("[AssistantMessage]")
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"  文本: {block.text[:200]}")
                elif isinstance(block, ToolUseBlock):
                    print(f"  [ToolUseBlock] 工具: {block.name}")
                    print(f"    ID: {block.id}")
                    print(f"    输入: {block.input}")
                elif isinstance(block, ToolResultBlock):
                    print(f"  [ToolResultBlock] tool_use_id: {block.tool_use_id}")
                    content_preview = str(block.content)[:200] if block.content else "None"
                    print(f"    结果: {content_preview}")
                    print(f"    是否错误: {block.is_error}")
            print()

        elif isinstance(message, ResultMessage):
            print(f"[ResultMessage] 轮次={message.num_turns}, 费用=${message.total_cost_usd:.6f}" if message.total_cost_usd else f"[ResultMessage] 轮次={message.num_turns}")


if __name__ == "__main__":
    anyio.run(main)
