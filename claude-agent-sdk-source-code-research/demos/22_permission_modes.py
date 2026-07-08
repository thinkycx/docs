"""
create: 2026-07-08
update: 2026-07-08
description:
    演示 Permission Modes: 展示 SDK 支持的所有权限模式及其效果。
    核心 API: ClaudeAgentOptions(permission_mode=...), PermissionMode。
    详细说明 6 种模式: default/acceptEdits/plan/bypassPermissions/dontAsk/auto，
    并使用 bypassPermissions 模式实际运行一个简单查询作为示例。
    使用 query() 函数式 API 运行。
expect_output:
    - 打印 6 种 PermissionMode 的说明(效果/适用场景/SDK行为)
    - 使用 bypassPermissions 模式运行查询，Claude 回复 "Two"
    - 打印配置示例代码
usage:
    cd demos && uv run python 22_permission_modes.py
"""

import anyio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)

# PermissionMode 类型定义:
# Literal["default", "acceptEdits", "plan", "bypassPermissions", "dontAsk", "auto"]


async def run_with_mode(mode: str, description: str):
    """使用指定权限模式运行一个简单查询。"""
    print(f"\n--- 模式: '{mode}' ---")
    print(f"    说明: {description}")

    options = ClaudeAgentOptions(
        permission_mode=mode,  # type: ignore
        max_turns=1,
    )

    async for msg in query(prompt="What is 1+1? Answer in one word.", options=options):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"    回复: {block.text[:80]}")
        elif isinstance(msg, ResultMessage):
            print(f"    结果: turns={msg.num_turns}, error={msg.is_error}")


async def main():
    print("=== Demo: Permission Modes (权限模式) ===")
    print()
    print("PermissionMode 可选值及效果:")
    print()

    # --- "default" 模式 ---
    # 标准权限行为: 对危险操作会触发权限提示
    # 在 SDK 中如果没有 can_use_tool 回调, 危险操作会被拒绝
    print('1. "default" - 标准模式')
    print("   效果: 对危险操作触发权限提示")
    print("   适用: 交互式场景, 需要用户确认")
    print("   SDK中: 如有 can_use_tool 回调则调用它; 否则危险操作被拒绝")

    # --- "acceptEdits" 模式 ---
    # 自动接受文件编辑操作, 其他危险操作仍需确认
    print()
    print('2. "acceptEdits" - 自动接受编辑')
    print("   效果: Write/Edit 等文件编辑操作自动通过")
    print("   适用: 代码生成场景, 信任 AI 的文件修改")
    print("   SDK中: 文件操作不触发 can_use_tool, Bash 等仍可能触发")

    # --- "plan" 模式 ---
    # 计划模式: 不执行任何工具, 只生成计划
    print()
    print('3. "plan" - 计划模式')
    print("   效果: 不执行任何工具调用, 只输出计划")
    print("   适用: 预览 AI 计划执行的步骤, 安全审查")
    print("   SDK中: 所有工具调用被跳过")

    # --- "bypassPermissions" 模式 ---
    # 绕过所有权限检查, 允许所有工具
    print()
    print('4. "bypassPermissions" - 绕过权限')
    print("   效果: 允许所有工具调用, 不进行任何权限检查")
    print("   适用: 受信任环境中的全自动化流程")
    print("   SDK中: can_use_tool 回调永远不会被调用")
    print("   警告: 有安全风险, 仅在受控环境中使用!")

    # --- "dontAsk" 模式 ---
    # 不提示权限: 未被 allow rules 预先批准的操作直接拒绝
    print()
    print('5. "dontAsk" - 不询问模式')
    print("   效果: 不提示权限; 未在 allowed_tools 中的操作直接拒绝")
    print("   适用: CI/CD 管道, 仅执行预定义安全操作")
    print("   SDK中: can_use_tool 不会被调用, 未允许的工具被拒绝")

    # --- "auto" 模式 ---
    # 模型分类器自动判断是否允许
    print()
    print('6. "auto" - 自动判断模式')
    print("   效果: 使用模型分类器自动判断每个工具调用是否安全")
    print("   适用: 半自动化场景, 平衡安全与效率")
    print("   SDK中: 由 CLI 内部分类器处理, 无需回调")

    # --- 实际运行示例 ---
    print("\n" + "=" * 50)
    print("实际运行 (使用 bypassPermissions 模式, 最安全的简单查询):")

    await run_with_mode(
        "bypassPermissions",
        "所有操作自动通过, 适合受信任环境",
    )

    print("\n--- 配置示例 ---")
    print("""
# 生产环境推荐: dontAsk + 明确的 allowed_tools
options = ClaudeAgentOptions(
    permission_mode="dontAsk",
    allowed_tools=["Read", "Grep", "Bash(git status:*)"],
)

# 开发环境: acceptEdits + can_use_tool 回调
options = ClaudeAgentOptions(
    permission_mode="acceptEdits",
    can_use_tool=my_permission_handler,
)

# 完全自动化 (慎用):
options = ClaudeAgentOptions(
    permission_mode="bypassPermissions",
)
""")

    print("=== Demo 完成 ===")


if __name__ == "__main__":
    anyio.run(main)
