---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Agent SDK - 快速开始
description: Agent SDK 快速上手指南，从零开始构建一个能自动发现并修复代码 Bug 的 AI Agent，涵盖环境配置、SDK 安装、Agent 编写和运行全流程。
category: translation
tags: [claude-code, agent-sdk, translation]
refs:
  - https://code.claude.com/docs/en/agent-sdk/quickstart.md
  - en-source/agent-sdk/quickstart.md
---

# Agent SDK 快速开始

> 使用 Python 或 TypeScript Agent SDK 构建自主工作的 AI Agent

**用 Agent SDK 构建一个能读取代码、发现 Bug 并自动修复的 AI Agent，全程无需人工干预。**

**你将完成：**

1. 搭建一个使用 Agent SDK 的项目
2. 创建一个包含故意 Bug 的文件
3. 运行 Agent 自动发现并修复 Bug

## 前置要求

- **Node.js 18+** 或 **Python 3.10+**
- **Anthropic 账号**（[注册地址](https://platform.claude.com/)）

## 环境搭建

### 1. 创建项目目录

```bash
mkdir my-agent
cd my-agent
```

实际项目中，你可以从任意目录运行 SDK；默认情况下 Agent 可以访问该目录及其子目录中的文件。

### 2. 安装 SDK

**TypeScript（新项目）：**

```bash
npm init -y
npm pkg set type=module
npm install @anthropic-ai/claude-agent-sdk
npm install --save-dev tsx
```

设置 `"type": "module"` 让 Agent 脚本可以使用顶层 `await`，[tsx](https://tsx.is) 可以直接运行 TypeScript 文件。

**TypeScript（已有项目）：**

```bash
npm install @anthropic-ai/claude-agent-sdk
npm install --save-dev tsx
```

[tsx](https://tsx.is) 直接运行 TypeScript 文件。如果项目使用 CommonJS，将 Agent 脚本命名为 `agent.mts` 而非 `agent.ts`。`.mts` 扩展名让 tsx 将文件视为 ES module，顶层 `await` 无需转换整个项目为 ES modules 即可工作。

**Python（uv）：**

[uv](https://docs.astral.sh/uv/) 是一个快速的 Python 包管理器，自动处理虚拟环境：

```bash
uv init
uv add claude-agent-sdk
```

**Python（pip）：**

创建并激活虚拟环境，然后安装：

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install claude-agent-sdk
```

Windows：

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install claude-agent-sdk
```

如果 PowerShell 因执行策略阻止 `Activate.ps1`，先运行 `Set-ExecutionPolicy -Scope Process RemoteSigned`。

> TypeScript SDK 会捆绑当前平台的原生 Claude Code 二进制文件作为可选依赖，无需单独安装 Claude Code。

### 3. 设置 API Key

从 [Claude Console](https://platform.claude.com/) 获取 API Key，然后在运行 Agent 的 shell 中设为环境变量：

**macOS / Linux：**

```bash
export ANTHROPIC_API_KEY=your-api-key
```

**Windows (PowerShell)：**

```powershell
$env:ANTHROPIC_API_KEY = "your-api-key"
```

SDK 从运行 Agent 的进程环境中读取 Key；不会自动加载 `.env` 文件。如果把 Key 存在 `.env` 文件中，需要自行加载（例如使用 `dotenv` 包）再调用 SDK。

**SDK 还支持通过第三方 API 提供商认证：**

| 提供商 | 配置方式 |
|:---|:---|
| Amazon Bedrock | 设置 `CLAUDE_CODE_USE_BEDROCK=1` 并配置 AWS 凭证 |
| Claude Platform on AWS | 设置 `CLAUDE_CODE_USE_ANTHROPIC_AWS=1` 和 `ANTHROPIC_AWS_WORKSPACE_ID`，配置 AWS 凭证 |
| Google Cloud Agent Platform | 设置 `CLAUDE_CODE_USE_VERTEX=1` 并配置 Google Cloud 凭证 |
| Microsoft Azure | 设置 `CLAUDE_CODE_USE_FOUNDRY=1` 并配置 Azure 凭证 |

详见 [Amazon Bedrock](https://code.claude.com/docs/en/amazon-bedrock)、[Claude Platform on AWS](https://code.claude.com/docs/en/claude-platform-on-aws)、[Google Cloud Agent Platform](https://code.claude.com/docs/en/google-vertex-ai) 或 [Microsoft Foundry](https://code.claude.com/docs/en/microsoft-foundry) 的设置指南。

> 除非事先获得批准，Anthropic 不允许第三方开发者在其产品中使用 claude.ai 登录或速率限额，包括基于 Claude Agent SDK 构建的 Agent。请使用本文档中描述的 API Key 认证方式。

## 创建包含 Bug 的文件

**本快速开始引导你构建一个能找到并修复代码 Bug 的 Agent。** 首先需要一个有故意 Bug 的文件供 Agent 修复。在 `my-agent` 目录创建 `utils.py` 并粘贴以下代码：

```python
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)


def get_user_name(user):
    return user["name"].upper()
```

这段代码有两个 Bug：

1. `calculate_average([])` 会因除零而崩溃
2. `get_user_name(None)` 会因 TypeError 崩溃

## 构建修复 Bug 的 Agent

创建 `agent.py`（Python SDK）或 `agent.ts`（TypeScript）。如果已有项目使用 CommonJS 则用 `agent.mts`：

**Python：**

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage


async def main():
    # Agent 循环：Claude 工作时流式输出消息
    async for message in query(
        prompt="Review utils.py for bugs that would cause crashes. Fix any issues you find.",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Edit", "Glob"],  # 自动批准这些工具
            permission_mode="acceptEdits",  # 自动批准文件编辑
        ),
    ):
        # 输出可读内容
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)  # Claude 的推理过程
                elif hasattr(block, "name"):
                    print(f"Tool: {block.name}")  # 正在调用的工具
        elif isinstance(message, ResultMessage):
            print(f"Done: {message.subtype}")  # 最终结果


asyncio.run(main())
```

**TypeScript：**

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

// Agent 循环：Claude 工作时流式输出消息
for await (const message of query({
  prompt: "Review utils.py for bugs that would cause crashes. Fix any issues you find.",
  options: {
    allowedTools: ["Read", "Edit", "Glob"], // 自动批准这些工具
    permissionMode: "acceptEdits" // 自动批准文件编辑
  }
})) {
  // 输出可读内容
  if (message.type === "assistant" && message.message?.content) {
    for (const block of message.message.content) {
      if ("text" in block) {
        console.log(block.text); // Claude 的推理过程
      } else if ("name" in block) {
        console.log(`Tool: ${block.name}`); // 正在调用的工具
      }
    }
  } else if (message.type === "result") {
    console.log(`Done: ${message.subtype}`); // 最终结果
  }
}
```

**代码的三个主要部分：**

1. **`query`**：创建 Agent 循环的主入口。返回异步迭代器，用 `async for` 在 Claude 工作时流式获取消息。完整 API 参见 [Python](https://code.claude.com/docs/en/agent-sdk/python#query) 或 [TypeScript](https://code.claude.com/docs/en/agent-sdk/typescript#query) SDK 参考。

2. **`prompt`**：你想让 Claude 做什么。Claude 根据任务自行决定使用哪些工具。

3. **`options`**：Agent 配置。本例使用 `allowedTools` 预批准 `Read`、`Edit` 和 `Glob`，用 `permissionMode: "acceptEdits"` 自动批准文件修改。其他选项包括 `systemPrompt`、`mcpServers` 等。全部选项参见 [Python](https://code.claude.com/docs/en/agent-sdk/python#claudeagentoptions) 或 [TypeScript](https://code.claude.com/docs/en/agent-sdk/typescript#options)。

`async for` 循环在 Claude 思考、调用工具、观察结果并决定下一步时持续运行。每次迭代产出一条消息：Claude 的推理、工具调用、工具结果或最终输出。SDK 处理编排（工具执行、上下文管理、重试），你只需消费流。循环在 Claude 完成任务或遇到错误时结束。

循环内的消息处理过滤出可读输出。不过滤的话会看到原始消息对象（包括系统初始化和内部状态），对调试有用但通常太嘈杂。

> 本例使用流式输出以实时显示进度。如果不需要实时输出（例如后台任务或 CI 流水线），可以一次性收集所有消息。详见 [流式 vs 单次模式](https://code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode)。

### 运行 Agent

Agent 已就绪，使用以下命令运行：

**TypeScript：**

```bash
npx tsx agent.ts
```

如果脚本命名为 `agent.mts`，运行 `npx tsx agent.mts`。

**Python（uv）：**

```bash
uv run agent.py
```

**Python（pip）：**

虚拟环境激活后：

```bash
python agent.py
```

**Agent 运行时会输出推理过程和调用的每个工具，最后输出 `Done: success`。** 运行后查看 `utils.py`，你会看到处理空列表和 null 用户的防御性代码。Agent 自主完成了：

1. **读取** `utils.py` 理解代码
2. **分析** 逻辑，识别会导致崩溃的边界情况
3. **编辑** 文件添加适当的错误处理

这就是 Agent SDK 的不同之处：Claude 直接执行工具，而不是让你来实现。

> 如果看到 "API key not found"，确保在运行 Agent 的 shell 中设置了 `ANTHROPIC_API_KEY` 环境变量。SDK 不会自动加载 `.env` 文件。更多帮助参见 [完整排障指南](https://code.claude.com/docs/en/troubleshooting)。

### 尝试其他 Prompt

Agent 已搭建好，试试不同的 Prompt：

- `"Add docstrings to all functions in utils.py"`
- `"Add type hints to all functions in utils.py"`
- `"Create a README.md documenting the functions in utils.py"`

### 自定义 Agent

可以通过修改 options 来改变 Agent 行为，几个例子：

**添加网络搜索能力：**

```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Edit", "Glob", "WebSearch"], permission_mode="acceptEdits"
)
```

**自定义系统提示词：**

```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Edit", "Glob"],
    permission_mode="acceptEdits",
    system_prompt="You are a senior Python developer. Always follow PEP 8 style guidelines.",
)
```

**执行终端命令：**

```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Edit", "Glob", "Bash"], permission_mode="acceptEdits"
)
```

启用 `Bash` 后可尝试：`"Write unit tests for utils.py, run them, and fix any failures"`

## 核心概念

**工具（Tools）** 控制 Agent 能做什么：

| 工具组合 | Agent 能力 |
|:---|:---|
| `Read`, `Glob`, `Grep` | 只读分析 |
| `Read`, `Edit`, `Glob` | 分析并修改代码 |
| `Read`, `Edit`, `Bash`, `Glob`, `Grep` | 全自动化 |

**权限模式（Permission modes）** 控制人工监督程度：

| 模式 | 行为 | 适用场景 |
|:---|:---|:---|
| `acceptEdits` | 自动批准文件编辑和常见文件系统命令，其他操作需确认 | 受信开发工作流 |
| `plan` | 运行只读工具；文件编辑不自动批准，触发 `canUseTool` 回调 | 执行前先确认范围 |
| `dontAsk` | 拒绝不在 `allowedTools` 中的所有操作 | 锁定的无头 Agent |
| `auto` | 模型分类器批准或拒绝每个工具调用 | 带安全护栏的自主 Agent |
| `bypassPermissions` | 运行所有工具无需提示，除非匹配明确的 [`ask` 规则](https://code.claude.com/docs/en/agent-sdk/permissions#how-permissions-are-evaluated) | 沙箱 CI、完全受信环境 |
| `default` | 需要 `canUseTool` 回调处理审批 | 自定义审批流程 |

本例使用 `acceptEdits` 模式，自动批准文件操作使 Agent 无需交互提示即可运行。如果想提示用户审批，使用 `default` 模式并提供收集用户输入的 [`canUseTool` 回调](https://code.claude.com/docs/en/agent-sdk/user-input)。更多控制参见 [权限](https://code.claude.com/docs/en/agent-sdk/permissions)。

## 下一步

创建了第一个 Agent 后，学习如何扩展能力并适配你的场景：

- [权限](https://code.claude.com/docs/en/agent-sdk/permissions)：控制 Agent 能做什么以及何时需要审批
- [Hooks](https://code.claude.com/docs/en/agent-sdk/hooks)：在工具调用前后运行自定义代码
- [会话](https://code.claude.com/docs/en/agent-sdk/sessions)：构建保持上下文的多轮 Agent
- [MCP 服务器](https://code.claude.com/docs/en/agent-sdk/mcp)：连接数据库、浏览器、API 等外部系统
- [部署](https://code.claude.com/docs/en/agent-sdk/hosting)：将 Agent 部署到 Docker、云和 CI/CD
- [示例 Agent](https://github.com/anthropics/claude-agent-sdk-demos)：完整示例，邮件助手、调研 Agent 等
