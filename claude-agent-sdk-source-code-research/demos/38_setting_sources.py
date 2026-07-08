"""
create: 2026-07-08
update: 2026-07-08
description:
    演示 setting_sources 控制加载哪些文件系统设置。
    对比隔离模式 (setting_sources=[]) 和加载用户+项目设置 (["user", "project"]) 的差异。
    通过 SystemMessage init 中的 slash_commands 数量验证设置加载效果。
    核心 API: query(), ClaudeAgentOptions.setting_sources, SystemMessage。
expect_output:
    - 隔离模式: slash_commands 数量较少 (约29个内置命令)
    - user+project模式: slash_commands 数量较多 (包含用户自定义 skills)
    - 两次都打印收到的 SystemMessage 数量和各自的 subtype
    - SystemMessage data keys 包含 type, subtype, cwd, session_id, tools
usage:
    cd demos && uv run python 38_setting_sources.py
"""

import anyio
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    SystemMessage,
    TextBlock,
    query,
)


async def run_with_settings(name: str, setting_sources):
    """使用指定 setting_sources 运行查询"""
    options = ClaudeAgentOptions(
        setting_sources=setting_sources,
        max_turns=1,
    )

    print(f"\n{'='*50}")
    print(f"配置: {name}")
    print(f"setting_sources = {setting_sources}")
    print("-" * 50)

    system_messages = []
    async for msg in query(prompt="Say 'ok' and nothing else.", options=options):
        if isinstance(msg, SystemMessage):
            system_messages.append(msg)
            # 检查 init 消息中的可用信息
            if msg.subtype == "init":
                data = msg.data
                slash_commands = data.get("slash_commands", data.get("slashCommands", []))
                print(f"  [SystemMessage init] 可用 slash_commands 数量: {len(slash_commands) if slash_commands else 0}")
                if slash_commands:
                    # 显示前几个 slash commands
                    cmds = slash_commands[:5] if isinstance(slash_commands, list) else list(slash_commands.keys())[:5]
                    print(f"  前 5 个 commands: {cmds}")

        elif isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"  回答: {block.text}")

        elif isinstance(msg, ResultMessage):
            print(f"  cost: ${msg.total_cost_usd or 0:.6f}")

    print(f"  收到 SystemMessage 数量: {len(system_messages)}")
    for sm in system_messages:
        print(f"    - subtype: {sm.subtype}, data keys: {list(sm.data.keys())[:5]}")


async def main():
    print("=== Setting Sources 演示 ===")
    print("setting_sources 控制加载哪些文件系统配置:")
    print("  - 'user': ~/.claude/settings.json")
    print("  - 'project': .claude/settings.json")
    print("  - 'local': .claude/settings.local.json")
    print("  - []: 禁用所有文件系统设置 (SDK 隔离模式)")
    print("  - None: 加载所有 (CLI 默认行为)")

    # 禁用所有文件系统设置 (SDK 隔离模式)
    await run_with_settings(
        "隔离模式 (无文件系统设置)",
        setting_sources=[],
    )

    # 加载 user + project 设置
    await run_with_settings(
        "加载 user + project 设置",
        setting_sources=["user", "project"],
    )


if __name__ == "__main__":
    anyio.run(main)
