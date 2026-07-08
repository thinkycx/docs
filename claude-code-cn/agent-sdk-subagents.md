---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Agent SDK - 子代理
description: 介绍如何在 Claude Agent SDK 中定义和调用子代理（Subagents），实现上下文隔离、并行执行、专用指令和工具限制，以及子代理的恢复与嵌套机制。
category: translation
tags: [claude-code, agent-sdk, translation]
refs:
  - https://code.claude.com/docs/en/agent-sdk/subagents
  - en-source/agent-sdk/subagents.md
---

# SDK 中的子代理

> 在 Claude Agent SDK 应用中定义和调用子代理，实现上下文隔离、并行任务和专用指令。

**子代理是主 Agent 可以生成的独立实例，用于处理聚焦的子任务。** 可用于隔离上下文、并行运行多个分析、应用专用指令而不污染主 Agent 的 prompt。

本指南介绍如何通过 `agents` 参数在 SDK 中定义和使用子代理。

## 概览

**创建子代理有三种方式：**

| 方式 | 说明 |
|:---|:---|
| 编程定义 | 通过 `query()` options 中的 `agents` 参数。见 [TypeScript](https://code.claude.com/docs/en/agent-sdk/typescript#agentdefinition) 和 [Python](https://code.claude.com/docs/en/agent-sdk/python#agentdefinition) 参考 |
| 文件系统定义 | 在 `.claude/agents/` 目录中以 Markdown 文件定义。见 [文件定义子代理](https://code.claude.com/docs/en/sub-agents) |
| 内置通用型 | Claude 可随时通过 Agent 工具调用内置的 `general-purpose` 子代理，无需你做任何定义 |

本指南聚焦编程方式，这是 SDK 应用的推荐做法。

**当你定义了子代理，Claude 会根据每个子代理的 `description` 字段自动判断是否调用。** 编写清晰的描述说明何时使用该子代理，Claude 就会自动委派合适的任务。你也可以在 prompt 中通过名称显式请求某个子代理，例如 "Use the code-reviewer agent to..."。

## 使用子代理的优势

### 上下文隔离

**每个子代理在独立的全新对话中运行。** 中间的工具调用和结果留在子代理内部，只有最终消息返回给父 Agent。详见 [子代理继承内容](#子代理继承的内容)。

举例：一个 `research-assistant` 子代理可以浏览数十个文件，但这些内容不会累积到主对话中。父 Agent 收到的是简洁摘要，而非子代理读过的每个文件。

### 并行化

**多个子代理可以并发运行，独立子任务的总耗时等于最慢的那个，而非全部之和。**

举例：代码审查时，可以同时运行 `style-checker`、`security-scanner` 和 `test-coverage` 三个子代理，而非串行执行。

### 专用指令与知识

**每个子代理可以有定制化的系统 prompt，包含特定专业知识、最佳实践和约束。**

举例：一个 `database-migration` 子代理可以内含 SQL 最佳实践、回滚策略和数据完整性检查的详细知识，这些对主 Agent 来说是不必要的噪声。

### 工具限制

**子代理可以被限制为只能使用特定工具，降低意外操作的风险。**

举例：一个 `doc-reviewer` 子代理可能只能访问 Read 和 Grep 工具，确保它能分析但永远不会意外修改你的文档文件。

## 创建子代理

### 编程定义（推荐）

**直接在代码中通过 `agents` 参数定义子代理。** Claude 通过 Agent 工具调用子代理，因此在 `allowedTools` 中包含 `Agent` 可以自动批准子代理调用而无需权限提示。

本页大多数示例只打印最终结果。要确认 Claude 确实委派给了子代理而非直接回答，见 [检测子代理调用](#检测子代理调用)。

以下示例创建两个子代理：一个具有只读访问权限的代码审查器和一个可执行命令的测试运行器。

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition


async def main():
    async for message in query(
        prompt="Review the authentication module for security issues",
        options=ClaudeAgentOptions(
            # 自动批准这些工具，包括用于子代理调用的 Agent
            allowed_tools=["Read", "Grep", "Glob", "Agent"],
            agents={
                "code-reviewer": AgentDefinition(
                    # description 告诉 Claude 何时使用此子代理
                    description="Expert code review specialist. Use for quality, security, and maintainability reviews.",
                    # prompt 定义子代理的行为和专长
                    prompt="""You are a code review specialist with expertise in security, performance, and best practices.

When reviewing code:
- Identify security vulnerabilities
- Check for performance issues
- Verify adherence to coding standards
- Suggest specific improvements

Be thorough but concise in your feedback.""",
                    # tools 限制子代理能做什么（此处为只读）
                    tools=["Read", "Grep", "Glob"],
                    # model 覆盖此子代理的默认模型
                    model="sonnet",
                ),
                "test-runner": AgentDefinition(
                    description="Runs and analyzes test suites. Use for test execution and coverage analysis.",
                    prompt="""You are a test execution specialist. Run tests and provide clear analysis of results.

Focus on:
- Running test commands
- Analyzing test output
- Identifying failing tests
- Suggesting fixes for failures""",
                    # Bash 访问让此子代理能运行测试命令
                    tools=["Bash", "Read", "Grep"],
                ),
            },
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)


asyncio.run(main())
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Review the authentication module for security issues",
  options: {
    // 自动批准这些工具，包括用于子代理调用的 Agent
    allowedTools: ["Read", "Grep", "Glob", "Agent"],
    agents: {
      "code-reviewer": {
        // description 告诉 Claude 何时使用此子代理
        description:
          "Expert code review specialist. Use for quality, security, and maintainability reviews.",
        // prompt 定义子代理的行为和专长
        prompt: `You are a code review specialist with expertise in security, performance, and best practices.

When reviewing code:
- Identify security vulnerabilities
- Check for performance issues
- Verify adherence to coding standards
- Suggest specific improvements

Be thorough but concise in your feedback.`,
        // tools 限制子代理能做什么（此处为只读）
        tools: ["Read", "Grep", "Glob"],
        // model 覆盖此子代理的默认模型
        model: "sonnet"
      },
      "test-runner": {
        description:
          "Runs and analyzes test suites. Use for test execution and coverage analysis.",
        prompt: `You are a test execution specialist. Run tests and provide clear analysis of results.

Focus on:
- Running test commands
- Analyzing test output
- Identifying failing tests
- Suggesting fixes for failures`,
        // Bash 访问让此子代理能运行测试命令
        tools: ["Bash", "Read", "Grep"]
      }
    }
  }
})) {
  if ("result" in message) console.log(message.result);
}
```

### AgentDefinition 配置

| 字段 | 类型 | 必填 | 说明 |
|:---|:---|:---|:---|
| `description` | <code>string</code> | 是 | 自然语言描述，说明何时使用此代理 |
| `prompt` | <code>string</code> | 是 | 代理的系统 prompt，定义其角色和行为 |
| `tools` | <code>string[]</code> | 否 | 允许的工具名列表。省略时继承所有工具 |
| `disallowedTools` | <code>string[]</code> | 否 | 要从代理工具集中移除的工具名。支持 MCP 服务器级别模式：`mcp__server` 或 `mcp__server__*` 移除该服务器的所有工具，`mcp__*` 移除所有 MCP 工具 |
| `model` | <code>string</code> | 否 | 此代理的模型覆盖。接受别名如 `'fable'`、`'opus'`、`'sonnet'`、`'haiku'`、`'inherit'`，或完整模型 ID。省略时使用主模型 |
| `skills` | <code>string[]</code> | 否 | 启动时预加载到代理上下文的 skill 名称列表。未列出的 skill 仍可通过 Skill 工具调用 |
| `memory` | <code>'user' \| 'project' \| 'local'</code> | 否 | 此代理的记忆来源 |
| `mcpServers` | <code>(string \| object)[]</code> | 否 | 此代理可用的 MCP 服务器，按名称或内联配置 |
| `initialPrompt` | <code>string</code> | 否 | 当此代理作为主线程代理运行时，自动作为第一个用户 turn 提交。作为子代理调用时忽略 |
| `maxTurns` | <code>number</code> | 否 | 代理停止前的最大 agentic turn 数 |
| `background` | <code>boolean</code> | 否 | 调用时作为非阻塞后台任务运行 |
| `effort` | <code>'low' \| 'medium' \| 'high' \| 'xhigh' \| 'max' \| number</code> | 否 | 此代理的推理深度级别 |
| `permissionMode` | <code>PermissionMode</code> | 否 | 此代理内的工具执行权限模式 |

**Python SDK 注意：** 多词字段名如 `disallowedTools` 和 `mcpServers` 保持 camelCase 拼写以匹配线上格式，而非遵循 Python 的 snake_case 惯例。详见 [`AgentDefinition` 参考](https://code.claude.com/docs/en/agent-sdk/python#agentdefinition)。

**Claude Code v2.1.198 中两个子代理行为变更：**

- 子代理默认在后台运行。省略 [`run_in_background`](https://code.claude.com/docs/en/agent-sdk/typescript) 输入的 Agent 工具调用会启动后台子代理，Claude 在需要结果才能继续时设置 `run_in_background: false`。v2.1.198 之前，省略 `run_in_background` 会同步运行子代理。将 `background` 字段设为 `true` 可强制特定代理后台执行，无论 Claude 请求什么。
- 子代理继承主会话的 extended thinking 配置。在更早版本中，无论主会话设置如何，子代理内部都禁用 extended thinking。

> 自 Claude Code v2.1.172 起，子代理可以生成自己的子代理。位于主 Agent 之下第五层的子代理无法再生成子代理，无论是前台还是后台运行。要阻止子代理生成其他子代理，从其 `tools` 数组中省略 `Agent` 或将其加入 `disallowedTools`。详见 [嵌套子代理](https://code.claude.com/docs/en/sub-agents#spawn-nested-subagents) 的完整深度规则。

### 文件系统定义（备选方案）

你也可以在 `.claude/agents/` 目录中以 Markdown 文件定义子代理。详见 [Claude Code 子代理文档](https://code.claude.com/docs/en/sub-agents)。编程定义的代理优先于同名的文件系统代理。

> 即使不定义自定义子代理，Claude 也可以生成内置的 `general-purpose` 子代理。这对于委派研究或探索任务很有用，无需创建专门的代理。在 `allowedTools` 中包含 `Agent` 以便这些调用自动批准而无需权限提示。

## 子代理继承的内容

**子代理的上下文窗口从零开始，没有父对话内容，但也不是完全空白。** 从父到子代理的唯一通道是 Agent 工具的 prompt 字符串，因此需要在该 prompt 中直接包含子代理所需的文件路径、错误消息或决策。

| 子代理接收的内容 | 子代理不接收的内容 |
|:---|:---|
| 自身的系统 prompt（`AgentDefinition.prompt`）和 Agent 工具的 prompt | 父对话的历史记录或工具结果 |
| 项目 CLAUDE.md（通过 [`settingSources`](https://code.claude.com/docs/en/agent-sdk/claude-code-features#control-filesystem-settings-with-settingsources) 加载） | 预加载的 skill 内容，除非在 `AgentDefinition.skills` 中列出 |
| 工具定义（从父继承，或 `tools` 中指定的子集） | 父的系统 prompt |

> 父 Agent 将子代理的最终消息原样作为 Agent 工具结果接收，但可能在自己的响应中对其进行摘要。要在面向用户的响应中保留子代理输出原文，在传给主 `query()` 调用的 prompt 或 `systemPrompt` 选项中加入相应指令。

**API 错误处理：** 过早结束子代理的 API 错误（如限流）不会作为其结果传递。如果限流、过载或服务器错误中断了已产出文本的前台子代理，Agent 工具返回该部分输出并附注子代理未完成。没有产出任何内容或仅产出工具调用的子代理会以错误消息 `Agent terminated early due to an API error` 加错误详情失败。详见 [子代理中的 API 错误](https://code.claude.com/docs/en/sub-agents#api-errors-in-subagents)。

此部分输出处理需要 Claude Code v2.1.199 或更高版本。

## 调用子代理

### 自动调用

**Claude 根据任务和每个子代理的 `description` 自动决定何时调用子代理。** 例如，如果你定义了一个 `performance-optimizer` 子代理并描述为 "Performance optimization specialist for query tuning"，当 prompt 提到优化查询时 Claude 就会调用它。

编写清晰、具体的描述，让 Claude 能将任务匹配到正确的子代理。

### 显式调用

**要保证 Claude 使用特定子代理，在 prompt 中提及其名称：**

```text
"Use the code-reviewer agent to check the authentication module"
```

这会绕过自动匹配，直接调用指定的子代理。

### 动态代理配置

**可以根据运行时条件动态创建代理定义。** 以下示例创建具有不同严格程度的安全审查器，对严格审查使用更强大的模型。

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition


# 工厂函数返回 AgentDefinition
# 此模式让你根据运行时条件自定义代理
def create_security_agent(security_level: str) -> AgentDefinition:
    is_strict = security_level == "strict"
    return AgentDefinition(
        description="Security code reviewer",
        # 根据严格程度自定义 prompt
        prompt=f"You are a {'strict' if is_strict else 'balanced'} security reviewer...",
        tools=["Read", "Grep", "Glob"],
        # 关键点：高风险审查使用更强的模型
        model="opus" if is_strict else "sonnet",
    )


async def main():
    # 代理在 query 时创建，因此每次请求可用不同设置
    async for message in query(
        prompt="Review this PR for security issues",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Grep", "Glob", "Agent"],
            agents={
                # 用期望的配置调用工厂函数
                "security-reviewer": create_security_agent("strict")
            },
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)


asyncio.run(main())
```

```typescript
import { query, type AgentDefinition } from "@anthropic-ai/claude-agent-sdk";

// 工厂函数返回 AgentDefinition
// 此模式让你根据运行时条件自定义代理
function createSecurityAgent(securityLevel: "basic" | "strict"): AgentDefinition {
  const isStrict = securityLevel === "strict";
  return {
    description: "Security code reviewer",
    // 根据严格程度自定义 prompt
    prompt: `You are a ${isStrict ? "strict" : "balanced"} security reviewer...`,
    tools: ["Read", "Grep", "Glob"],
    // 关键点：高风险审查使用更强的模型
    model: isStrict ? "opus" : "sonnet"
  };
}

// 代理在 query 时创建，因此每次请求可用不同设置
for await (const message of query({
  prompt: "Review this PR for security issues",
  options: {
    allowedTools: ["Read", "Grep", "Glob", "Agent"],
    agents: {
      // 用期望的配置调用工厂函数
      "security-reviewer": createSecurityAgent("strict")
    }
  }
})) {
  if ("result" in message) console.log(message.result);
}
```

## 检测子代理调用

**Claude 通过 Agent 工具调用子代理。要检测子代理调用，检查 `name` 为 `"Agent"` 的 `tool_use` 块。** 子代理上下文内的消息包含 `parent_tool_use_id` 字段。

> 工具名在 Claude Code v2.1.63 中从 `"Task"` 重命名为 `"Agent"`。当前 SDK 版本在 `tool_use` 块中发出 `"Agent"`，但在 `system:init` 工具列表和 `result.permission_denials[].tool_name` 中仍使用 `"Task"`。在 `block.name` 中同时检查两个值可确保跨 SDK 版本兼容性。

消息结构在两个 SDK 间有差异。Python 中通过 `message.content` 直接访问内容块；TypeScript 中 `SDKAssistantMessage` 包装了 Claude API 消息，通过 `message.message.content` 访问。

以下示例遍历流式消息，记录子代理调用和子代理执行上下文内的后续消息。

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition, ToolUseBlock


async def main():
    async for message in query(
        prompt="Use the code-reviewer agent to review this codebase",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Glob", "Grep", "Agent"],
            agents={
                "code-reviewer": AgentDefinition(
                    description="Expert code reviewer.",
                    prompt="Analyze code quality and suggest improvements.",
                    tools=["Read", "Glob", "Grep"],
                )
            },
        ),
    ):
        # 检查子代理调用。同时匹配两个名称：旧 SDK 版本发出 "Task"，当前版本发出 "Agent"
        if hasattr(message, "content") and message.content:
            for block in message.content:
                if isinstance(block, ToolUseBlock) and block.name in (
                    "Task",
                    "Agent",
                ):
                    print(f"Subagent invoked: {block.input.get('subagent_type')}")

        # 检查此消息是否来自子代理上下文内部
        if hasattr(message, "parent_tool_use_id") and message.parent_tool_use_id:
            print("  (running inside subagent)")

        if hasattr(message, "result"):
            print(message.result)


asyncio.run(main())
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Use the code-reviewer agent to review this codebase",
  options: {
    allowedTools: ["Read", "Glob", "Grep", "Agent"],
    agents: {
      "code-reviewer": {
        description: "Expert code reviewer.",
        prompt: "Analyze code quality and suggest improvements.",
        tools: ["Read", "Glob", "Grep"]
      }
    }
  }
})) {
  const msg = message as any;

  // 检查子代理调用。同时匹配两个名称：旧 SDK 版本发出 "Task"，当前版本发出 "Agent"
  for (const block of msg.message?.content ?? []) {
    if (block.type === "tool_use" && (block.name === "Task" || block.name === "Agent")) {
      console.log(`Subagent invoked: ${block.input.subagent_type}`);
    }
  }

  // 检查此消息是否来自子代理上下文内部
  if (msg.parent_tool_use_id) {
    console.log("  (running inside subagent)");
  }

  if ("result" in message) {
    console.log(message.result);
  }
}
```

## 恢复子代理

**可以恢复子代理以从上次中断处继续，而非重新开始。** 恢复的子代理保留其完整对话历史，包括所有先前的工具调用、结果和推理。

子代理完成时，Agent 工具结果包含 `agentId: <id>` 的文本块。内置的 [`Explore` 和 `Plan` 代理](https://code.claude.com/docs/en/sub-agents#built-in-subagents) 是一次性的，不返回 `agentId`，需要恢复时使用自定义代理或 `general-purpose`。编程方式恢复子代理的步骤：

1. **捕获会话 ID**：从第一次 query 的消息中提取 `session_id`
2. **提取代理 ID**：从 Agent 工具结果文本中解析 `agentId`
3. **恢复会话**：在第二次 query 的 options 中传入 `resume: sessionId`，并在 prompt 中包含代理 ID

> 必须恢复同一会话才能访问子代理的 transcript。每次 `query()` 调用默认创建新会话，因此传入 `resume: sessionId` 以在同一会话中继续。使用自定义代理时，两次 query 的 `agents` 参数中都要传入相同的代理定义。

以下示例定义自定义 `endpoint-finder` 代理。第一次 query 运行它并从 Agent 工具结果中捕获会话 ID 和代理 ID，然后第二次 query 恢复会话来提问需要第一次分析上下文的后续问题。

```python
import asyncio
import re
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition, ToolResultBlock

AGENTS = {
    "endpoint-finder": AgentDefinition(
        description="Locates and catalogs API endpoints in a codebase.",
        prompt="You find and document API endpoints. Report each endpoint's path, method, and handler.",
        tools=["Read", "Grep", "Glob"],
    )
}


def extract_agent_id(block: ToolResultBlock) -> str | None:
    """从 Agent 工具结果的文本内容中提取 agentId。"""
    parts = block.content if isinstance(block.content, list) else [{"text": block.content}]
    for part in parts:
        if match := re.search(r"agentId:\s*([\w-]+)", part.get("text") or ""):
            return match.group(1)
    return None


async def main():
    agent_id = None
    session_id = None

    # 第一次调用 - 运行 endpoint-finder 子代理
    try:
        async for message in query(
            prompt="Use the endpoint-finder agent to find all API endpoints in this codebase",
            options=ClaudeAgentOptions(allowed_tools=["Read", "Grep", "Glob", "Agent"], agents=AGENTS),
        ):
            # 从 ResultMessage 捕获 session_id（恢复此会话时需要）
            if hasattr(message, "session_id"):
                session_id = message.session_id
            # 在工具结果中搜索 agentId 尾部
            for block in getattr(message, "content", None) or []:
                if isinstance(block, ToolResultBlock):
                    agent_id = extract_agent_id(block) or agent_id
            # 打印最终结果
            if hasattr(message, "result"):
                print(message.result)
    except Exception as error:
        print(f"Session ended with an error: {error}")

    # 第二次调用 - 恢复并提问后续问题
    if agent_id and session_id:
        async for message in query(
            prompt=f"Resume agent {agent_id} and list the top 3 most complex endpoints",
            options=ClaudeAgentOptions(
                allowed_tools=["Read", "Grep", "Glob", "Agent"], agents=AGENTS, resume=session_id
            ),
        ):
            if hasattr(message, "result"):
                print(message.result)
    else:
        print("No agentId found in the first query, so there is no subagent to resume.")


asyncio.run(main())
```

```typescript
import { query, type SDKMessage } from "@anthropic-ai/claude-agent-sdk";

const agents = {
  "endpoint-finder": {
    description: "Locates and catalogs API endpoints in a codebase.",
    prompt: "You find and document API endpoints. Report each endpoint's path, method, and handler.",
    tools: ["Read", "Grep", "Glob"]
  }
};

// 字符串化内容以搜索 agentId，无需遍历嵌套块类型
function extractAgentId(message: SDKMessage): string | undefined {
  if (message.type !== "assistant" && message.type !== "user") return undefined;
  const content = JSON.stringify(message.message.content);
  const match = content.match(/agentId:\s*([\w-]+)/);
  return match?.[1];
}

let agentId: string | undefined;
let sessionId: string | undefined;

// 第一次调用 - 运行 endpoint-finder 子代理
try {
  for await (const message of query({
    prompt: "Use the endpoint-finder agent to find all API endpoints in this codebase",
    options: { allowedTools: ["Read", "Grep", "Glob", "Agent"], agents }
  })) {
    // 从 ResultMessage 捕获 session_id（恢复此会话时需要）
    if ("session_id" in message) sessionId = message.session_id;
    // 在消息内容中搜索 agentId（出现在 Agent 工具结果中）
    const extractedId = extractAgentId(message);
    if (extractedId) agentId = extractedId;
    // 打印最终结果
    if ("result" in message) console.log(message.result);
  }
} catch (error) {
  console.error(`Session ended with an error: ${error}`);
}

// 第二次调用 - 恢复并提问后续问题
if (agentId && sessionId) {
  for await (const message of query({
    prompt: `Resume agent ${agentId} and list the top 3 most complex endpoints`,
    options: { allowedTools: ["Read", "Grep", "Glob", "Agent"], agents, resume: sessionId }
  })) {
    if ("result" in message) console.log(message.result);
  }
} else {
  console.log("No agentId found in the first query, so there is no subagent to resume.");
}
```

**子代理 transcript 的持久化行为：**

| 行为 | 说明 |
|:---|:---|
| 主对话压缩 | 不影响子代理 transcript，它们存储在独立文件中 |
| 会话持久化 | 子代理 transcript 在会话内持久化。重启 Claude Code 后可通过恢复同一会话来恢复子代理 |
| 自动清理 | transcript 根据 `cleanupPeriodDays` 设置清理，默认 30 天 |

## 工具限制

**子代理可通过 `tools` 字段限制工具访问：**

- **省略字段**：代理继承所有可用工具（默认）
- **指定工具**：代理只能使用列出的工具

以下示例创建一个只读分析代理，可检查代码但不能修改文件或运行命令。

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition


async def main():
    async for message in query(
        prompt="Analyze the architecture of this codebase",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Grep", "Glob", "Agent"],
            agents={
                "code-analyzer": AgentDefinition(
                    description="Static code analysis and architecture review",
                    prompt="""You are a code architecture analyst. Analyze code structure,
identify patterns, and suggest improvements without making changes.""",
                    # 只读工具：无 Edit、Write 或 Bash 访问
                    tools=["Read", "Grep", "Glob"],
                )
            },
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)


asyncio.run(main())
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Analyze the architecture of this codebase",
  options: {
    allowedTools: ["Read", "Grep", "Glob", "Agent"],
    agents: {
      "code-analyzer": {
        description: "Static code analysis and architecture review",
        prompt: `You are a code architecture analyst. Analyze code structure,
identify patterns, and suggest improvements without making changes.`,
        // 只读工具：无 Edit、Write 或 Bash 访问
        tools: ["Read", "Grep", "Glob"]
      }
    }
  }
})) {
  if ("result" in message) console.log(message.result);
}
```

### 常见工具组合

| 用途 | 工具 | 说明 |
|:---|:---|:---|
| 只读分析 | `Read`, `Grep`, `Glob` | 可检查代码但不能修改或执行 |
| 测试执行 | `Bash`, `Read`, `Grep` | 可运行命令并分析输出 |
| 代码修改 | `Read`, `Edit`, `Write`, `Grep`, `Glob` | 完整读写访问，无命令执行 |
| 完全访问 | 所有工具 | 从父继承所有工具（省略 `tools` 字段） |

## 用动态工作流扩展规模

**子代理适合每轮委派少量任务。对于需要协调数十到数百个代理的运行，使用 `Workflow` 工具。** 它将编排移入运行时在对话上下文之外执行的脚本中。详见 [动态工作流](https://code.claude.com/docs/en/workflows)。

`Workflow` 工具在 TypeScript Agent SDK v0.3.149 及之后版本可用。在 `allowedTools` 中包含 `Workflow` 以自动批准工作流运行。工具输入输出 schema 见 [TypeScript 参考](https://code.claude.com/docs/en/agent-sdk/typescript#workflow)。

## 故障排除

### Claude 不委派给子代理

如果 Claude 直接完成任务而不委派给你的子代理：

| 检查项 | 解决方案 |
|:---|:---|
| Agent 调用未被批准 | 在 `allowedTools` 中包含 `Agent`。没有它，Agent 调用会降级到 `canUseTool` 回调，或在 `dontAsk` 模式下被拒绝 |
| prompt 不够明确 | 在 prompt 中提及子代理名称，例如 "Use the code-reviewer agent to..." |
| description 不清晰 | 明确说明何时使用该子代理，让 Claude 能正确匹配任务 |

### 文件系统代理不加载

Claude Code 监视 `~/.claude/agents/` 和 `.claude/agents/`，在几秒内感知新增或编辑的代理文件，无需重启。如果定义始终不出现，排查以下原因：

| 原因 | 说明 |
|:---|:---|
| 新的 `agents` 目录 | 监视器只覆盖会话启动时已存在的目录，新目录中的第一个文件需要重启会话 |
| 无效 frontmatter 或重复 `name` | 检查文件的 YAML 以及是否有已有代理使用了相同的 `name` |
| `--disable-slash-commands` | 使用此标志启动的会话不监视这些目录，总是需要重启才能加载新文件 |
| 同名编程代理 | 传给 `query()` 的 `agents` 会覆盖同名的文件系统代理 |

文件格式详见 [如何编写子代理文件](https://code.claude.com/docs/en/sub-agents#write-subagent-files)。

### Windows 上长 prompt 失败

在 Windows 上，prompt 过长的子代理可能因命令行长度限制（8191 字符）而失败。保持 prompt 简洁，或对复杂指令使用文件系统代理。

## 相关文档

- [Claude Code 子代理](https://code.claude.com/docs/en/sub-agents)：完整的子代理文档，包括文件系统定义
- [动态工作流](https://code.claude.com/docs/en/workflows)：通过脚本编排大量子代理，适用于单个对话无法处理的任务
- [SDK 概览](https://code.claude.com/docs/en/agent-sdk/overview)：Claude Agent SDK 入门指南
