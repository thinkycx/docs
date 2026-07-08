"""
create: 2026-07-08
update: 2026-07-08
description:
    演示 AgentDefinition: 以编程方式定义自定义子 Agent 并在 query 中使用。
    核心 API: AgentDefinition(description/prompt/tools/model), ClaudeAgentOptions(agents={...})。
    定义一个代码审查 Agent，注册到 options.agents 中，然后请求 Claude 调用该 Agent 审查代码。
    展示 AgentDefinition 的完整字段说明。使用 query() 函数式 API 运行。
expect_output:
    - 打印 Agent 定义信息(description/tools/model/prompt)
    - 打印 AgentDefinition 完整字段说明
    - Claude 调用 Agent 工具(ToolUse: Agent)
    - Claude 输出代码审查结果(如除零风险)
    - ResultMessage 显示 session_id 和 num_turns
usage:
    cd demos && uv run python 18_agent_definition.py
"""

import anyio

from claude_agent_sdk import (
    AgentDefinition,
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    query,
)


async def main():
    print("=== Demo: AgentDefinition (代码审查 Agent) ===\n")

    # 定义一个代码审查 Agent
    code_reviewer = AgentDefinition(
        description="A code reviewer that analyzes code for quality, bugs, and best practices",
        prompt=(
            "You are an expert code reviewer. When given code or a file to review, "
            "analyze it for:\n"
            "1. Code quality and readability\n"
            "2. Potential bugs or edge cases\n"
            "3. Performance concerns\n"
            "4. Best practice violations\n"
            "Provide concise, actionable feedback."
        ),
        tools=["Read", "Grep"],  # 限制只能使用 Read 和 Grep 工具
        model="sonnet",  # 使用 Sonnet 模型 (也可以是 "opus", "haiku", "inherit")
    )

    print("Agent 定义:")
    print(f"  description: {code_reviewer.description}")
    print(f"  tools: {code_reviewer.tools}")
    print(f"  model: {code_reviewer.model}")
    print(f"  prompt: {code_reviewer.prompt[:80]}...")
    print()

    # AgentDefinition 的其他可选字段:
    print("AgentDefinition 完整字段说明:")
    print("  description: str       # Agent 描述(必需)")
    print("  prompt: str            # Agent 系统提示(必需)")
    print("  tools: list[str]       # 可用工具列表")
    print("  disallowedTools: list  # 禁用工具列表")
    print("  model: str             # 模型 ('sonnet'/'opus'/'haiku'/'inherit'/完整ID)")
    print("  skills: list[str]      # 可用 Skills")
    print("  memory: str            # 记忆范围 ('user'/'project'/'local')")
    print("  mcpServers: list       # MCP 服务器配置")
    print("  initialPrompt: str     # 初始提示")
    print("  maxTurns: int          # 最大对话轮数")
    print("  background: bool       # 是否后台运行")
    print("  effort: str            # 努力等级")
    print("  permissionMode: str    # 权限模式")
    print()

    # 在 query 中使用 agents 参数注册 Agent
    options = ClaudeAgentOptions(
        max_turns=3,
        permission_mode="bypassPermissions",
        agents={
            "code-reviewer": code_reviewer,  # key 就是 Agent 名称
        },
    )

    prompt = (
        "Please use the code-reviewer agent to review this Python code:\n"
        "```python\n"
        "def divide(a, b):\n"
        "    return a / b\n"
        "```"
    )
    print(f"发送 prompt (请求使用 code-reviewer Agent):\n{prompt}\n")

    async for msg in query(prompt=prompt, options=options):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"  [Assistant] {block.text[:200]}")
                elif isinstance(block, ToolUseBlock):
                    print(f"  [ToolUse] {block.name}({list(block.input.keys())})")
        elif isinstance(msg, ResultMessage):
            print(f"\n  [Result] session_id={msg.session_id}")
            print(f"  [Result] num_turns={msg.num_turns}")

    print("\n=== Demo 完成 ===")


if __name__ == "__main__":
    anyio.run(main)
