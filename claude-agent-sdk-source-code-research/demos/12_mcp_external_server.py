"""
create: 2026-07-08
update: 2026-07-08
description:
    演示外部 MCP 服务器的三种传输配置方式(stdio/SSE/HTTP)。
    核心 API: ClaudeAgentOptions.mcp_servers, stdio/sse/http config dict。
    展示如何将 MCP 服务器配置传入 query() 或 ClaudeSDKClient。
    配置演示，需要外部 MCP 服务器才能实际运行。
expect_output:
    - 打印三种 MCP 传输方式的配置信息(command/url/headers)
    - 检测 npx 是否可用，若不可用则打印使用方式代码结构后退出
    - 若 npx 可用则尝试启动 filesystem MCP 服务器并执行 list_directory
usage:
    cd demos && uv run python 12_mcp_external_server.py
"""

import os

import anyio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)


def show_mcp_configs():
    """展示三种 MCP 服务器配置方式"""

    # 1. stdio 方式: 通过子进程启动 MCP 服务器
    stdio_config = {
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
        "env": {"NODE_ENV": "production"},
    }

    # 2. SSE 方式: 连接 SSE 端点
    sse_config = {
        "type": "sse",
        "url": "http://localhost:3001/sse",
        "headers": {"Authorization": "Bearer token123"},
    }

    # 3. HTTP 方式: 连接 HTTP 端点（streamable HTTP transport）
    http_config = {
        "type": "http",
        "url": "http://localhost:3002/mcp",
        "headers": {"X-API-Key": "key123"},
    }

    print("=== MCP 外部服务器配置方式 ===\n")

    print("1. Stdio 传输（子进程）:")
    print(f"   command: {stdio_config['command']}")
    print(f"   args: {stdio_config['args']}")
    print(f"   env: {stdio_config['env']}")
    print()

    print("2. SSE 传输（Server-Sent Events）:")
    print(f"   url: {sse_config['url']}")
    print(f"   headers: {sse_config['headers']}")
    print()

    print("3. HTTP 传输（Streamable HTTP）:")
    print(f"   url: {http_config['url']}")
    print(f"   headers: {http_config['headers']}")
    print()

    return stdio_config, sse_config, http_config


async def main():
    stdio_config, sse_config, http_config = show_mcp_configs()

    # 实际使用时，将配置传入 ClaudeAgentOptions
    # 这里使用 filesystem MCP 服务器作为示例
    # 如果 npx 不可用或服务器路径不存在，跳过实际执行

    # 检查是否有 npx 可用来运行 filesystem 服务器
    has_npx = os.system("which npx > /dev/null 2>&1") == 0

    if not has_npx:
        print("--- npx 不可用，跳过实际 MCP 服务器调用 ---")
        print("--- 以下展示使用方式的代码结构 ---\n")
        print("""
# 使用方式:
options = ClaudeAgentOptions(
    permission_mode="bypassPermissions",
    mcp_servers={
        "filesystem": stdio_config,   # stdio 方式
        "remote_sse": sse_config,     # SSE 方式
        "remote_http": http_config,   # HTTP 方式
    },
    allowed_tools=["read_file", "list_directory"],
    max_turns=3,
)

async for message in query(prompt="List files in /tmp", options=options):
    ...
""")
        return

    # 如果 npx 可用，尝试运行 filesystem 服务器
    print("--- 尝试使用 filesystem MCP 服务器 ---\n")

    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        mcp_servers={
            "filesystem": {
                "type": "stdio",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
            },
        },
        allowed_tools=["list_directory"],
        max_turns=2,
    )

    try:
        async for message in query(
            prompt="List files in the /tmp directory.",
            options=options,
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"  Claude: {block.text[:200]}")
            elif isinstance(message, ResultMessage):
                print(f"\n[完成] 轮次={message.num_turns}")
    except Exception as e:
        print(f"  MCP 服务器连接失败 (预期行为): {e}")
        print("  提示: 确保 @modelcontextprotocol/server-filesystem 已安装")


if __name__ == "__main__":
    anyio.run(main)
