"""
create: 2026-07-08
update: 2026-07-08
description:
    演示多 Agent 协作: 同时注册 reviewer 和 writer 两个子 Agent，让 Claude 协调使用。
    核心 API: AgentDefinition, ClaudeAgentOptions(agents={...}), Agent 工具调用。
    定义 reviewer(代码审查) 和 writer(代码编写) 两个 Agent，
    请求 Claude 先让 reviewer 审查代码，再让 writer 基于审查反馈改进代码。
    使用 query() 函数式 API 运行。
expect_output:
    - 打印两个已注册 Agent 的信息(tools/model)
    - Claude 调用 Agent 工具两次(reviewer 和 writer)
    - Claude 输出审查结果和改进后的代码
    - ResultMessage 显示 session_id、num_turns 和 cost
usage:
    cd demos && uv run python 19_agent_multi_agents.py
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
    print("=== Demo: Multi-Agent 协作 (审查 + 编写) ===\n")

    # 定义代码审查 Agent
    reviewer_agent = AgentDefinition(
        description="Reviews code for bugs, quality issues, and suggests improvements",
        prompt=(
            "You are a code reviewer. Analyze the given code and identify:\n"
            "- Bugs and edge cases\n"
            "- Code quality issues\n"
            "- Suggested improvements\n"
            "Be specific and actionable in your feedback."
        ),
        tools=["Read", "Grep"],
        model="sonnet",
        maxTurns=3,
    )

    # 定义代码编写 Agent
    writer_agent = AgentDefinition(
        description="Writes clean, well-documented code following best practices",
        prompt=(
            "You are an expert code writer. Write clean, efficient, and "
            "well-documented code. Follow these principles:\n"
            "- Clear variable names\n"
            "- Proper error handling\n"
            "- Type hints where appropriate\n"
            "- Concise docstrings\n"
            "When asked to fix code, apply the suggested improvements."
        ),
        tools=["Read", "Write", "Edit"],
        model="sonnet",
        maxTurns=5,
    )

    print("已注册 Agent:")
    print(f"  1. reviewer - tools={reviewer_agent.tools}, model={reviewer_agent.model}")
    print(f"  2. writer   - tools={writer_agent.tools}, model={writer_agent.model}")
    print()

    options = ClaudeAgentOptions(
        max_turns=5,
        permission_mode="bypassPermissions",
        agents={
            "reviewer": reviewer_agent,
            "writer": writer_agent,
        },
    )

    prompt = (
        "I have this Python function that needs improvement:\n\n"
        "```python\n"
        "def process_data(data):\n"
        "    result = []\n"
        "    for i in range(len(data)):\n"
        "        if data[i] != None:\n"
        "            result.append(data[i] * 2)\n"
        "    return result\n"
        "```\n\n"
        "First, ask the reviewer agent to review it, then ask the writer agent "
        "to produce an improved version based on the review feedback. "
        "Don't actually write any files, just show the improved code in your response."
    )

    print(f"发送 prompt: (要求 reviewer 审查后 writer 改进代码)\n")

    async for msg in query(prompt=prompt, options=options):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    # 截取输出以保持简洁
                    text = block.text[:300]
                    print(f"  [Assistant] {text}")
                    if len(block.text) > 300:
                        print(f"  ... (共 {len(block.text)} 字符)")
                elif isinstance(block, ToolUseBlock):
                    print(f"  [ToolUse] {block.name}")
                    if block.name == "Agent":
                        agent_name = block.input.get("agent_name", "?")
                        task = block.input.get("task", "?")[:80]
                        print(f"    -> agent_name: {agent_name}")
                        print(f"    -> task: {task}...")
        elif isinstance(msg, ResultMessage):
            print(f"\n  [Result] session_id={msg.session_id}")
            print(f"  [Result] num_turns={msg.num_turns}")
            if msg.total_cost_usd:
                print(f"  [Result] cost=${msg.total_cost_usd:.4f}")

    print("\n=== Demo 完成 ===")


if __name__ == "__main__":
    anyio.run(main)
