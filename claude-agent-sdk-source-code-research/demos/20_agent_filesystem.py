"""
create: 2026-07-08
update: 2026-07-08
description:
    演示文件系统 Agent: 通过 setting_sources 加载 .claude/agents/*.md 中定义的 Agent。
    核心 API: ClaudeAgentOptions(setting_sources=["project"/"user"/"local"/[]])。
    展示四种加载模式: 全部加载、仅项目、SDK隔离模式、混合使用。
    文件系统 Agent 格式为 .claude/agents/<name>.md 带 YAML frontmatter。
    使用 query() 函数式 API 运行。
expect_output:
    - 打印文件系统 Agent 配置说明和四种模式
    - 实际运行查询，Claude 列出可用的 Agent 类型
    - 打印 setting_sources 值说明
usage:
    cd demos && uv run python 20_agent_filesystem.py
"""

import anyio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)


async def main():
    print("=== Demo: 文件系统 Agent (.claude/agents/*.md) ===\n")

    # --- 说明文件系统 Agent 的配置模式 ---
    print("文件系统 Agent 配置说明:")
    print()
    print("1. 创建文件 .claude/agents/my-reviewer.md:")
    print("   ---")
    print("   description: Reviews code for quality and correctness")
    print("   tools:")
    print("     - Read")
    print("     - Grep")
    print("   model: sonnet")
    print("   maxTurns: 5")
    print("   ---")
    print("   You are a code reviewer. Analyze code for bugs and improvements.")
    print()
    print("2. 在 SDK 中通过 setting_sources 加载:")
    print()

    # 模式 1: 加载所有设置源 (默认行为)
    print("模式 1: 加载所有设置源 (包括 project agents)")
    options_all = ClaudeAgentOptions(
        setting_sources=["user", "project", "local"],  # 默认行为
        max_turns=1,
        permission_mode="bypassPermissions",
    )
    print(f"  setting_sources={options_all.setting_sources}")
    print()

    # 模式 2: 只加载项目设置 (包含 .claude/agents/)
    print("模式 2: 仅加载项目级设置")
    options_project = ClaudeAgentOptions(
        setting_sources=["project"],  # 只加载 .claude/settings.json 和 .claude/agents/
        max_turns=1,
        permission_mode="bypassPermissions",
    )
    print(f"  setting_sources={options_project.setting_sources}")
    print()

    # 模式 3: SDK 隔离模式 (不加载任何文件系统设置)
    print("模式 3: SDK 隔离模式 (不加载文件系统设置)")
    options_isolated = ClaudeAgentOptions(
        setting_sources=[],  # 不加载任何文件系统设置, 也不会加载 CLAUDE.md
        max_turns=1,
        permission_mode="bypassPermissions",
    )
    print(f"  setting_sources={options_isolated.setting_sources}")
    print()

    # 模式 4: 混合使用 - 文件系统 Agent + 编程定义的 Agent
    print("模式 4: 同时使用文件系统 Agent 和编程定义的 Agent")
    print("  setting_sources=['project'] 会加载 .claude/agents/*.md")
    print("  agents={...} 会添加额外的编程定义的 Agent")
    print("  两者合并使用, Agent 名称不能冲突")
    print()

    # --- 实际运行一个简单查询 ---
    print("--- 运行示例 (使用 setting_sources=['project']) ---\n")

    options = ClaudeAgentOptions(
        setting_sources=["project"],
        max_turns=1,
        permission_mode="bypassPermissions",
    )

    async for msg in query(
        prompt="What agents are available to you? List them briefly.",
        options=options,
    ):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"  [Assistant] {block.text[:200]}")
        elif isinstance(msg, ResultMessage):
            print(f"\n  [Result] session_id={msg.session_id}")

    print("\n--- setting_sources 值说明 ---")
    print("  'user'    -> ~/.claude/settings.json")
    print("  'project' -> .claude/settings.json + .claude/agents/*.md + CLAUDE.md")
    print("  'local'   -> .claude/settings.local.json")
    print("  None      -> 加载所有 (等同于 ['user', 'project', 'local'])")
    print("  []        -> 不加载任何文件系统设置 (SDK 隔离模式)")

    print("\n=== Demo 完成 ===")


if __name__ == "__main__":
    anyio.run(main)
