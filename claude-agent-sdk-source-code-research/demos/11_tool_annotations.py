"""
create: 2026-07-08
update: 2026-07-08
description:
    工具注解 (ToolAnnotations)。演示核心 API: @tool with ToolAnnotations,
    readOnlyHint, destructiveHint, openWorldHint。
    定义三个工具分别标注不同的安全属性注解: read_config (只读),
    delete_cache (破坏性), fetch_url (访问外部网络)。
    ToolAnnotations 是 MCP 协议的一部分，向权限系统提供工具行为元信息。
expect_output:
    - 打印三个工具的注解说明
    - Claude 调用 read_config({'key': 'app.name'}) 返回 "MyApp"
    - Claude 调用 read_config({'key': 'app.version'}) 返回 "2.1.0"
    - 最终文本包含 app.name 和 app.version 的值
    - ResultMessage 显示 num_turns=3
usage:
    cd demos && uv run python 11_tool_annotations.py
"""

import anyio
from mcp.types import ToolAnnotations

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    create_sdk_mcp_server,
    query,
    tool,
)


# readOnlyHint=True: 告诉系统此工具只读，不会修改任何状态
@tool(
    "read_config",
    "Read application configuration (read-only operation)",
    {"key": str},
    annotations=ToolAnnotations(
        readOnlyHint=True,       # 只读操作，不修改状态
        destructiveHint=False,   # 非破坏性
        openWorldHint=False,     # 不访问外部世界
    ),
)
async def read_config(args: dict) -> dict:
    """模拟读取配置文件"""
    configs = {
        "app.name": "MyApp",
        "app.version": "2.1.0",
        "app.port": "8080",
        "db.host": "localhost",
    }
    key = args["key"]
    value = configs.get(key, f"<not found: {key}>")
    return {"content": [{"type": "text", "text": f"{key} = {value}"}]}


# destructiveHint=True: 告诉系统此工具有破坏性操作
@tool(
    "delete_cache",
    "Delete application cache entries (destructive operation)",
    {"pattern": str},
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,    # 破坏性操作，会删除数据
        openWorldHint=False,
    ),
)
async def delete_cache(args: dict) -> dict:
    """模拟删除缓存"""
    pattern = args["pattern"]
    return {"content": [{"type": "text", "text": f"Deleted cache entries matching: {pattern} (3 entries removed)"}]}


# openWorldHint=True: 告诉系统此工具会访问外部网络
@tool(
    "fetch_url",
    "Fetch content from a URL (accesses external network)",
    {"url": str},
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        openWorldHint=True,      # 访问外部世界（网络请求）
    ),
)
async def fetch_url(args: dict) -> dict:
    """模拟 URL 请求"""
    url = args["url"]
    return {"content": [{"type": "text", "text": f"Fetched {url}: <html><body>Hello World</body></html>"}]}


async def main():
    server = create_sdk_mcp_server(
        name="annotated_tools",
        version="1.0.0",
        tools=[read_config, delete_cache, fetch_url],
    )

    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        mcp_servers={"tools": server},
        allowed_tools=["read_config", "delete_cache", "fetch_url"],
        max_turns=3,
    )

    print("=== ToolAnnotations 演示 ===\n")
    print("三个工具分别具有不同的注解:")
    print("  - read_config: readOnly=True (只读)")
    print("  - delete_cache: destructive=True (破坏性)")
    print("  - fetch_url: openWorld=True (访问外部网络)")
    print()

    async for message in query(
        prompt="Read the 'app.name' and 'app.version' config values.",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"  Claude: {block.text}")
                elif isinstance(block, ToolUseBlock):
                    print(f"  [调用] {block.name}({block.input})")
            print()

        elif isinstance(message, ResultMessage):
            print(f"[完成] 轮次={message.num_turns}")


if __name__ == "__main__":
    anyio.run(main)
