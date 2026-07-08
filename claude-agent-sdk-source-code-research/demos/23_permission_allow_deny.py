"""
create: 2026-07-08
update: 2026-07-08
description:
    演示 allowed_tools 与 disallowed_tools 的交互关系。
    通过三个场景展示: 1) 仅设置 allowed_tools 自动允许特定工具;
    2) 仅设置 disallowed_tools 从模型上下文移除工具;
    3) 冲突时 disallowed_tools 优先级高于 allowed_tools。
    还展示了 allowed_tools 的高级语法(带参数匹配的模式)。
    核心 API: ClaudeAgentOptions(allowed_tools=[...], disallowed_tools=[...])
expect_output:
    - 场景1: 模型列出可用工具(包含 Read, Grep)
    - 场景2: 模型列出工具但不包含 Bash/Write/Edit
    - 场景3: 模型确认无法使用 Bash 但可以使用 Read
    - 每个场景输出 [Result] turns=1
    - 最后打印 allowed_tools 高级语法说明
usage:
    cd demos && uv run python 23_permission_allow_deny.py
"""

import anyio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    query,
)


async def demo_allowed_only():
    """演示 allowed_tools: 允许的工具自动通过。"""
    print("--- 场景 1: 仅设置 allowed_tools ---")
    print("  allowed_tools=['Read', 'Grep']")
    print("  效果: Read 和 Grep 自动允许, 其他工具需要权限确认")

    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Grep"],
        max_turns=2,
    )

    async for msg in query(
        prompt="What tools do you have available? Just list them briefly.",
        options=options,
    ):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"  [Assistant] {block.text[:150]}")
        elif isinstance(msg, ResultMessage):
            print(f"  [Result] turns={msg.num_turns}")


async def demo_disallowed_only():
    """演示 disallowed_tools: 禁用的工具从上下文中移除。"""
    print("\n--- 场景 2: 仅设置 disallowed_tools ---")
    print("  disallowed_tools=['Bash', 'Write', 'Edit']")
    print("  效果: Bash/Write/Edit 完全不可用, 模型看不到这些工具")

    options = ClaudeAgentOptions(
        disallowed_tools=["Bash", "Write", "Edit"],
        permission_mode="bypassPermissions",
        max_turns=1,
    )

    async for msg in query(
        prompt="List the tools you can use. Be brief.",
        options=options,
    ):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"  [Assistant] {block.text[:150]}")
        elif isinstance(msg, ResultMessage):
            print(f"  [Result] turns={msg.num_turns}")


async def demo_conflict():
    """演示 disallowed_tools 优先级高于 allowed_tools。"""
    print("\n--- 场景 3: 冲突 - 同一工具同时在 allowed 和 disallowed 中 ---")
    print("  allowed_tools=['Read', 'Bash']")
    print("  disallowed_tools=['Bash']")
    print("  效果: Bash 被禁用(disallowed 优先), Read 自动允许")

    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Bash"],
        disallowed_tools=["Bash"],  # 优先级更高!
        permission_mode="bypassPermissions",
        max_turns=1,
    )

    async for msg in query(
        prompt="Can you use Bash? Can you use Read? Answer briefly.",
        options=options,
    ):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"  [Assistant] {block.text[:150]}")
        elif isinstance(msg, ResultMessage):
            print(f"  [Result] turns={msg.num_turns}")


async def main():
    print("=== Demo: allowed_tools 与 disallowed_tools ===\n")

    print("优先级规则:")
    print("  disallowed_tools > allowed_tools > permission_mode > can_use_tool")
    print()
    print("  1. disallowed_tools: 工具被完全移除, 模型无法看到或使用")
    print("  2. allowed_tools: 自动允许, 不触发权限提示")
    print("  3. permission_mode: 控制未在 allow/deny 中的工具的行为")
    print("  4. can_use_tool: 最后的自定义决策层")
    print()

    await demo_allowed_only()
    await demo_disallowed_only()
    await demo_conflict()

    print("\n--- allowed_tools 高级语法 ---")
    print("""
# 允许整个工具 (所有调用):
allowed_tools=["Read", "Grep"]

# 允许工具的特定调用模式 (带参数匹配):
allowed_tools=[
    "Bash(git status:*)",     # 只允许 git status 相关命令
    "Read(/src/*)",           # 只允许读取 /src/ 下的文件
    "Write(/tmp/*)",          # 只允许写入 /tmp/ 下
]

# 空括号/通配符 = 允许全部:
allowed_tools=["Read()"]      # 等同于 "Read"
allowed_tools=["Read(*)"]     # 等同于 "Read"
""")

    print("=== Demo 完成 ===")


if __name__ == "__main__":
    anyio.run(main)
