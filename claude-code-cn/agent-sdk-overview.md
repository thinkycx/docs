---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Agent SDK - 概览
description: Claude Agent SDK 概览，介绍如何将 Claude Code 作为库来构建生产级 AI Agent，涵盖内置工具、Hooks、子代理、MCP、权限和会话管理等核心能力。
category: translation
tags: [claude-code, agent-sdk, translation]
refs:
  - https://code.claude.com/docs/en/agent-sdk/overview.md
  - en-source/agent-sdk/overview.md
---

# Agent SDK 概览

> 将 Claude Code 作为库来构建生产级 AI Agent

**用 Python 和 TypeScript 构建能自主读取文件、执行命令、搜索网络、编辑代码等操作的 AI Agent。** Agent SDK 提供与 Claude Code 相同的工具、Agent 循环和上下文管理能力，以编程方式供你调用。

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    async for message in query(
        prompt="Find and fix the bug in auth.py",
        options=ClaudeAgentOptions(allowed_tools=["Read", "Edit", "Bash"]),
    ):
        print(message)  # Claude reads the file, finds the bug, edits it


asyncio.run(main())
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Find and fix the bug in auth.ts",
  options: { allowedTools: ["Read", "Edit", "Bash"] }
})) {
  console.log(message); // Claude reads the file, finds the bug, edits it
}
```

Agent SDK 包含读取文件、执行命令和编辑代码的内置工具，Agent 无需你实现工具执行逻辑即可立即开始工作。可以前往快速开始，或浏览基于 SDK 构建的示例 Agent：

- [快速开始](https://code.claude.com/docs/en/agent-sdk/quickstart) - 几分钟内构建一个修 Bug 的 Agent
- [示例 Agent](https://github.com/anthropics/claude-agent-sdk-demos) - 邮件助手、调研 Agent 等

## 快速上手

### 1. 安装 SDK

**TypeScript:**

```bash
npm install @anthropic-ai/claude-agent-sdk
```

**Python:**

```bash
pip install claude-agent-sdk
```

Python 包需要 Python 3.10 或更高版本。如果 pip 报错 `No matching distribution found for claude-agent-sdk`，说明解释器版本低于 3.10。在 macOS/Linux 执行 `python3 --version`，Windows 执行 `py --version` 检查。

> TypeScript SDK 会捆绑当前平台的原生 Claude Code 二进制文件作为可选依赖，无需单独安装 Claude Code。

### 2. 设置 API Key

从 [Console](https://platform.claude.com/) 获取 API Key，然后设为环境变量：

```bash
export ANTHROPIC_API_KEY=your-api-key
```

**SDK 还支持通过第三方 API 提供商认证：**

| 提供商 | 配置方式 |
|:---|:---|
| Amazon Bedrock | 设置 `CLAUDE_CODE_USE_BEDROCK=1` 并配置 AWS 凭证 |
| Claude Platform on AWS | 设置 `CLAUDE_CODE_USE_ANTHROPIC_AWS=1` 和 `ANTHROPIC_AWS_WORKSPACE_ID`，配置 AWS 凭证 |
| Google Cloud Agent Platform | 设置 `CLAUDE_CODE_USE_VERTEX=1` 并配置 Google Cloud 凭证 |
| Microsoft Azure | 设置 `CLAUDE_CODE_USE_FOUNDRY=1` 并配置 Azure 凭证 |

详见 [Amazon Bedrock](https://code.claude.com/docs/en/amazon-bedrock)、[Claude Platform on AWS](https://code.claude.com/docs/en/claude-platform-on-aws)、[Google Cloud Agent Platform](https://code.claude.com/docs/en/google-vertex-ai) 或 [Microsoft Foundry](https://code.claude.com/docs/en/microsoft-foundry) 的设置指南。

> 除非事先获得批准，Anthropic 不允许第三方开发者在其产品中使用 claude.ai 登录或速率限额，包括基于 Claude Agent SDK 构建的 Agent。请使用本文档中描述的 API Key 认证方式。

### 3. 运行你的第一个 Agent

**下面的示例创建一个使用内置工具列出当前目录文件的 Agent。**

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    async for message in query(
        prompt="What files are in this directory?",
        options=ClaudeAgentOptions(allowed_tools=["Bash", "Glob"]),
    ):
        if hasattr(message, "result"):
            print(message.result)


asyncio.run(main())
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "What files are in this directory?",
  options: { allowedTools: ["Bash", "Glob"] }
})) {
  if ("result" in message) console.log(message.result);
}
```

**准备好了？** 跟着 [快速开始](https://code.claude.com/docs/en/agent-sdk/quickstart) 几分钟内创建一个能找到并修复 Bug 的 Agent。

## 核心能力

Claude Code 的全部能力都可以通过 SDK 使用：

### 内置工具

**Agent 开箱即用，能读取文件、执行命令和搜索代码库。** 主要工具包括：

| 工具 | 功能 |
|:---|:---|
| **Read** | 读取工作目录中的任意文件 |
| **Write** | 创建新文件 |
| **Edit** | 对已有文件进行精确编辑 |
| **Bash** | 执行终端命令、脚本、git 操作 |
| **Monitor** | 监控后台脚本，将每行输出作为事件响应 |
| **Glob** | 按模式查找文件（`**/*.ts`、`src/**/*.py`） |
| **Grep** | 使用正则搜索文件内容 |
| **WebSearch** | 搜索网络获取最新信息 |
| **WebFetch** | 抓取并解析网页内容 |
| **[AskUserQuestion](https://code.claude.com/docs/en/agent-sdk/user-input#handle-clarifying-questions)** | 向用户提出澄清性问题，支持多选项 |

示例 — 搜索代码库中所有 TODO 注释：

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    async for message in query(
        prompt="Find all TODO comments and create a summary",
        options=ClaudeAgentOptions(allowed_tools=["Read", "Glob", "Grep"]),
    ):
        if hasattr(message, "result"):
            print(message.result)


asyncio.run(main())
```

### Hooks

**在 Agent 生命周期的关键节点执行自定义代码。** SDK Hooks 使用回调函数来验证、记录、拦截或转换 Agent 行为。

**可用 Hooks：** `PreToolUse`、`PostToolUse`、`Stop`、`SessionStart`、`SessionEnd`、`UserPromptSubmit` 等。

示例 — 将所有文件变更记录到审计日志：

```python
import asyncio
from datetime import datetime
from claude_agent_sdk import query, ClaudeAgentOptions, HookMatcher


async def log_file_change(input_data, tool_use_id, context):
    file_path = input_data.get("tool_input", {}).get("file_path", "unknown")
    with open("./audit.log", "a") as f:
        f.write(f"{datetime.now()}: modified {file_path}\n")
    return {}


async def main():
    async for message in query(
        prompt="Refactor utils.py to improve readability",
        options=ClaudeAgentOptions(
            permission_mode="acceptEdits",
            hooks={
                "PostToolUse": [
                    HookMatcher(matcher="Edit|Write", hooks=[log_file_change])
                ]
            },
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)


asyncio.run(main())
```

[了解更多 Hooks 用法](https://code.claude.com/docs/en/agent-sdk/hooks)

### 子代理（Subagents）

**派生专门的 Agent 处理聚焦的子任务。** 主 Agent 委派工作，子代理完成后汇报结果。

通过专门的指令定义自定义 Agent。子代理通过 Agent 工具调用，因此在 `allowedTools` 中包含 `Agent` 即可自动批准调用：

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition


async def main():
    async for message in query(
        prompt="Use the code-reviewer agent to review this codebase",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Glob", "Grep", "Agent"],
            agents={
                "code-reviewer": AgentDefinition(
                    description="Expert code reviewer for quality and security reviews.",
                    prompt="Analyze code quality and suggest improvements.",
                    tools=["Read", "Glob", "Grep"],
                )
            },
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)


asyncio.run(main())
```

子代理上下文中的消息包含 `parent_tool_use_id` 字段，便于追踪哪些消息属于哪个子代理执行。

[了解更多子代理用法](https://code.claude.com/docs/en/agent-sdk/subagents)

### MCP

**通过 Model Context Protocol 连接外部系统：** 数据库、浏览器、API 以及 [数百种更多服务](https://github.com/modelcontextprotocol/servers)。

示例 — 连接 [Playwright MCP 服务器](https://github.com/microsoft/playwright-mcp) 赋予 Agent 浏览器自动化能力：

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    async for message in query(
        prompt="Open example.com and describe what you see",
        options=ClaudeAgentOptions(
            mcp_servers={
                "playwright": {"command": "npx", "args": ["@playwright/mcp@latest"]}
            }
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)


asyncio.run(main())
```

[了解更多 MCP 用法](https://code.claude.com/docs/en/agent-sdk/mcp)

### 权限控制

**精确控制 Agent 可使用的工具。** 允许安全操作、阻止危险操作，或要求对敏感操作进行审批。

> 交互式审批提示和 `AskUserQuestion` 工具详见 [处理审批和用户输入](https://code.claude.com/docs/en/agent-sdk/user-input)。

示例 — 创建只读 Agent，可分析但不能修改代码。`allowed_tools` 预批准 `Read`、`Glob` 和 `Grep`：

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    async for message in query(
        prompt="Review this code for best practices",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Glob", "Grep"],
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)


asyncio.run(main())
```

[了解更多权限控制](https://code.claude.com/docs/en/agent-sdk/permissions)

### 会话管理

**跨多次交互维护上下文。** Claude 记住已读文件、完成的分析和对话历史。可以稍后恢复会话，或分叉以探索不同方案。

示例 — 从第一次查询中捕获 session ID，然后恢复继续操作：

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, SystemMessage, ResultMessage


async def main():
    session_id = None

    # 第一次查询：捕获 session ID
    async for message in query(
        prompt="Read the authentication module",
        options=ClaudeAgentOptions(allowed_tools=["Read", "Glob"]),
    ):
        if isinstance(message, SystemMessage) and message.subtype == "init":
            session_id = message.data["session_id"]

    # 恢复会话，带上第一次查询的完整上下文
    async for message in query(
        prompt="Now find all places that call it",  # "it" = auth module
        options=ClaudeAgentOptions(resume=session_id),
    ):
        if isinstance(message, ResultMessage):
            print(message.result)


asyncio.run(main())
```

[了解更多会话管理](https://code.claude.com/docs/en/agent-sdk/sessions)

### Claude Code 功能

**SDK 还支持 Claude Code 基于文件系统的配置。** 默认情况下 SDK 从工作目录的 `.claude/` 和 `~/.claude/` 加载。要限制加载来源，在选项中设置 `setting_sources`（Python）或 `settingSources`（TypeScript）。

| 功能 | 说明 | 位置 |
|:---|:---|:---|
| [Skills](https://code.claude.com/docs/en/agent-sdk/skills) | Claude 自动使用或通过 `/name` 调用的专项能力 | `.claude/skills/*/SKILL.md` |
| [Commands](https://code.claude.com/docs/en/agent-sdk/slash-commands) | 旧格式的自定义命令；新命令请用 Skills | `.claude/commands/*.md` |
| [Memory](https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts) | 项目上下文和指令 | `CLAUDE.md` 或 `.claude/CLAUDE.md` |
| [Plugins](https://code.claude.com/docs/en/agent-sdk/plugins) | 通过 skills、agents、hooks 和 MCP 服务器扩展 | 通过 `plugins` 选项编程配置 |

## Agent SDK 与其他 Claude 工具对比

Claude 平台提供多种构建方式，下面是 Agent SDK 的定位：

### Agent SDK vs Client SDK

**[Anthropic Client SDK](https://platform.claude.com/docs/en/api/client-sdks) 提供直接 API 访问：你发送提示词并自行实现工具执行。Agent SDK 则提供带内置工具执行的 Claude。**

使用 Client SDK 你需要实现工具循环；使用 Agent SDK，Claude 自动处理：

```python
# Client SDK: 你自己实现工具循环
response = client.messages.create(...)
while response.stop_reason == "tool_use":
    result = your_tool_executor(response.tool_use)
    response = client.messages.create(tool_result=result, **params)

# Agent SDK: Claude 自主处理工具
async for message in query(prompt="Fix the bug in auth.py"):
    print(message)
```

### Agent SDK vs Claude Code CLI

**相同能力，不同接口：**

| 场景 | 最佳选择 |
|:---|:---|
| 交互式开发 | CLI |
| CI/CD 流水线 | SDK |
| 自定义应用 | SDK |
| 一次性任务 | CLI |
| 生产自动化 | SDK |

很多团队两者并用：日常开发用 CLI，生产环境用 SDK。工作流在两者间可以直接迁移。

### Agent SDK vs Managed Agents

**[Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) 是托管 REST API：Anthropic 运行 Agent 和沙箱，你的应用发送事件并流式接收结果。Agent SDK 则是在你自己的进程中运行 Agent 循环的库。**

| | Agent SDK | Managed Agents |
|:---|:---|:---|
| **运行位置** | 你的进程、你的基础设施 | Anthropic 托管基础设施 |
| **接口** | Python 或 TypeScript 库 | REST API |
| **Agent 工作对象** | 你基础设施上的文件 | 每个会话一个托管沙箱 |
| **会话状态** | 你文件系统上的 JSONL | Anthropic 托管的事件日志 |
| **自定义工具** | 进程内 Python/TypeScript 函数 | Claude 触发工具，你执行并返回结果 |
| **适用场景** | 本地原型开发、直接操作文件系统和服务的 Agent | 无需运维沙箱或会话基础设施的生产 Agent、长时间运行和异步会话 |

常见路径：先用 Agent SDK 本地原型验证，再迁移到 Managed Agents 部署生产。

## Changelog

查看完整更新日志：

- **TypeScript SDK**: [CHANGELOG.md](https://github.com/anthropics/claude-agent-sdk-typescript/blob/main/CHANGELOG.md)
- **Python SDK**: [CHANGELOG.md](https://github.com/anthropics/claude-agent-sdk-python/blob/main/CHANGELOG.md)

## 报告问题

如遇到 Agent SDK 的 Bug 或问题：

- **TypeScript SDK**: [GitHub Issues](https://github.com/anthropics/claude-agent-sdk-typescript/issues)
- **Python SDK**: [GitHub Issues](https://github.com/anthropics/claude-agent-sdk-python/issues)

## 品牌使用指南

对于集成 Claude Agent SDK 的合作伙伴，使用 Claude 品牌是可选的。在产品中引用 Claude 时：

**允许：**

- "Claude Agent"（推荐用于下拉菜单）
- "Claude"（当所在菜单已标注 "Agents"）
- "{YourAgentName} Powered by Claude"（如有已有 Agent 名称）

**不允许：**

- "Claude Code" 或 "Claude Code Agent"
- Claude Code 风格的 ASCII art 或模仿 Claude Code 的视觉元素

你的产品应保持自有品牌，不应看起来像 Claude Code 或任何 Anthropic 产品。品牌合规问题请联系 Anthropic [销售团队](https://www.anthropic.com/contact-sales)。

## 许可证和条款

Claude Agent SDK 的使用受 [Anthropic 商业服务条款](https://www.anthropic.com/legal/commercial-terms) 约束，包括你用它来驱动向客户和最终用户提供的产品和服务时，除非特定组件或依赖在其 LICENSE 文件中标明了不同的许可证。

## 下一步

- [快速开始](https://code.claude.com/docs/en/agent-sdk/quickstart) - 几分钟内构建一个能找到并修复 Bug 的 Agent
- [示例 Agent](https://github.com/anthropics/claude-agent-sdk-demos) - 邮件助手、调研 Agent 等
- [TypeScript SDK](https://code.claude.com/docs/en/agent-sdk/typescript) - 完整 TypeScript API 参考和示例
- [Python SDK](https://code.claude.com/docs/en/agent-sdk/python) - 完整 Python API 参考和示例
