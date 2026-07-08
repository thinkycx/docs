---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Agent SDK - Agent 循环机制
description: Agent SDK 的核心循环机制详解，涵盖消息生命周期、工具执行流程、上下文窗口管理、自动压缩、Turns 与预算控制、权限模式等架构细节。
category: translation
tags: [claude-code, agent-sdk, translation]
refs:
  - https://code.claude.com/docs/en/agent-sdk/agent-loop.md
  - en-source/agent-sdk/agent-loop.md
---

# Agent 循环机制

> 理解 SDK Agent 的消息生命周期、工具执行、上下文窗口和架构

**Agent SDK 让你在自己的应用中嵌入 Claude Code 的自主 Agent 循环。** SDK 是一个独立包，提供对工具、权限、成本限制和输出的编程控制。无需安装 Claude Code CLI 即可使用。

启动 Agent 时，SDK 运行与 [Claude Code 相同的执行循环](https://code.claude.com/docs/en/how-claude-code-works#the-agentic-loop)：Claude 评估你的 Prompt、调用工具执行操作、接收结果，然后重复直到任务完成。本页解释循环内部的运作机制，帮助你有效地构建、调试和优化 Agent。

## 循环一览

每个 Agent 会话都遵循相同的周期：

1. **接收 Prompt。** Claude 接收你的 Prompt 以及系统提示词、工具定义和对话历史。SDK 产出一条 subtype 为 `"init"` 的 [`SystemMessage`](#消息类型) 包含会话元数据。
2. **评估并响应。** Claude 评估当前状态并决定如何继续。可能用文本回复、请求一个或多个工具调用，或两者兼有。SDK 产出一条 [`AssistantMessage`](#消息类型) 包含文本和工具调用请求。
3. **执行工具。** SDK 运行每个请求的工具并收集结果。每组工具结果反馈给 Claude 用于下一步决策。你可以使用 [Hooks](https://code.claude.com/docs/en/agent-sdk/hooks) 在工具运行前拦截、修改或阻止调用。
4. **重复。** 步骤 2 和 3 作为循环重复。每个完整循环是一个 Turn。Claude 持续调用工具和处理结果，直到产出不包含工具调用的响应。
5. **返回结果。** SDK 产出最终的 [`AssistantMessage`](#消息类型)（纯文本响应，无工具调用），然后是 [`ResultMessage`](#消息类型) 包含最终文本、token 用量、成本和 session ID。

简单问题（"这里有哪些文件？"）可能只需一两个 Turn 调用 `Glob` 并返回结果。复杂任务（"重构 auth 模块并更新测试"）可能跨多个 Turn 链式调用数十个工具，读取文件、编辑代码、运行测试，Claude 根据每次结果调整方案。

## Turns 和消息

**一个 Turn 是循环内的一次往返：** Claude 产出包含工具调用的输出，SDK 执行这些工具，结果自动反馈给 Claude。这一过程不会将控制权交还你的代码。Turn 持续直到 Claude 产出不包含工具调用的输出，此时循环结束并交付最终结果。

以 Prompt "Fix the failing tests in auth.ts" 为例，一个完整会话可能是这样的：

首先，SDK 将你的 Prompt 发送给 Claude 并产出一条 [`SystemMessage`](#消息类型) 包含会话元数据。然后循环开始：

1. **Turn 1：** Claude 调用 `Bash` 运行 `npm test`。SDK 产出一条 [`AssistantMessage`](#消息类型)（工具调用），执行命令，然后产出一条 [`UserMessage`](#消息类型)（输出：三个失败）。
2. **Turn 2：** Claude 调用 `Read` 读取 `auth.ts` 和 `auth.test.ts`。SDK 返回文件内容并产出一条 `AssistantMessage`。
3. **Turn 3：** Claude 调用 `Edit` 修复 `auth.ts`，然后调用 `Bash` 重新运行 `npm test`。三个测试全部通过。SDK 产出一条 `AssistantMessage`。
4. **最终 Turn：** Claude 产出纯文本响应（无工具调用）："Fixed the auth bug, all three tests pass now." SDK 产出最终的 `AssistantMessage` 包含此文本，然后是 [`ResultMessage`](#消息类型) 包含相同文本加上成本和用量。

共四个 Turn：三个有工具调用，一个最终纯文本响应。

可以用 `max_turns` / `maxTurns` 限制循环，它只计算工具使用的 Turn。例如上例中 `max_turns=2` 会在编辑步骤前停止。也可以用 `max_budget_usd` / `maxBudgetUsd` 按消费阈值限制 Turn。

不设限制时，循环运行直到 Claude 自行完成，对范围明确的任务没问题，但对开放式 Prompt（"改进这个代码库"）可能运行很久。为生产 Agent 设置预算是个好默认。参见下方 [Turns 与预算](#turns-与预算)。

## 消息类型

循环运行时 SDK 产出消息流。每条消息有一个 type 标明它来自循环的哪个阶段。五种核心类型：

- **`SystemMessage`：** 会话生命周期事件。通过 `subtype` 字段区分：
  - `"init"`：第一条消息，包含会话元数据
  - `"compact_boundary"`：[压缩](#自动压缩)后触发
  - `"informational"`：循环的纯文本状态横幅
  - `"worker_shutting_down"`：循环将在当前 Turn 后结束（宿主退出或 Remote Control 断开）

  在 TypeScript 中，`"init"` 以外的每个 subtype 是 [`SDKMessage` 联合类型](https://code.claude.com/docs/en/agent-sdk/typescript#sdkmessage) 中的独立类型，而非 `SDKSystemMessage` 的 subtype。

- **`AssistantMessage`：** 每次 Claude 响应后产出，包括最终纯文本响应。包含该 Turn 的文本内容块和工具调用块。

- **`UserMessage`：** 每次工具执行后产出，包含发回给 Claude 的工具结果内容。你在循环中流式发送的用户输入也会产出此类型。

- **`StreamEvent`：** 仅在启用 partial messages 时产出。包含原始 API 流事件（文本 delta、工具输入片段）。参见 [流式响应](https://code.claude.com/docs/en/agent-sdk/streaming-output)。

- **`ResultMessage`：** 标记 Agent 循环结束。包含最终文本结果、token 用量、成本和 session ID。检查 `subtype` 字段判断任务成功还是触及限制。少量尾部系统事件（如 `prompt_suggestion`）可能在其后到达，因此要迭代流至完成而非在 result 时 break。参见 [处理结果](#处理结果)。

这五种类型涵盖两个 SDK 中完整的 Agent 循环生命周期。TypeScript SDK 还产出额外的可观测事件（hook 事件、工具进度、速率限制、任务通知），提供更多细节但非驱动循环所必需。参见 [Python 消息类型参考](https://code.claude.com/docs/en/agent-sdk/python#message-types) 和 [TypeScript 消息类型参考](https://code.claude.com/docs/en/agent-sdk/typescript#message-types)。

### 处理消息

**处理哪些消息取决于你在构建什么：**

- **仅最终结果：** 处理 `ResultMessage` 获取输出、成本和任务是否成功。
- **进度更新：** 处理 `AssistantMessage` 查看 Claude 每个 Turn 在做什么，包括调用了哪些工具。
- **实时流式：** 启用 partial messages（Python 中 `include_partial_messages`，TypeScript 中 `includePartialMessages`）获取实时 `StreamEvent` 消息。参见 [实时流式响应](https://code.claude.com/docs/en/agent-sdk/streaming-output)。

**类型检查方式因 SDK 而异：**

- **Python：** 使用 `isinstance()` 检查从 `claude_agent_sdk` 导入的类（例如 `isinstance(message, ResultMessage)`）。
- **TypeScript：** 检查 `type` 字符串字段（例如 `message.type === "result"`）。`AssistantMessage` 和 `UserMessage` 将原始 API 消息包裹在 `.message` 字段中，因此内容块在 `message.message.content`，而非 `message.content`。

示例 — 检查消息类型并处理结果：

```python
import asyncio
from claude_agent_sdk import query, AssistantMessage, ResultMessage


async def main():
    try:
        async for message in query(prompt="Summarize this project"):
            if isinstance(message, AssistantMessage):
                print(f"Turn completed: {len(message.content)} content blocks")
            if isinstance(message, ResultMessage):
                if message.subtype == "success":
                    print(message.result)
                else:
                    print(f"Stopped: {message.subtype}")
    except Exception as error:
        # 单次 query() 在产出错误结果后会抛异常。如果失败是错误结果，
        # 上面的 subtype 分支已执行；连接或进程失败则不产出 result 消息。
        print(f"Session ended with an error: {error}")


asyncio.run(main())
```

## 工具执行

**工具赋予 Agent 执行操作的能力。** 没有工具，Claude 只能用文本回复。有工具，Claude 可以读文件、运行命令、搜索代码、与外部服务交互。

### 内置工具

SDK 包含驱动 Claude Code 的相同工具：

| 分类 | 工具 | 功能 |
|:---|:---|:---|
| **文件操作** | `Read`, `Edit`, `Write` | 读取、修改和创建文件 |
| **搜索** | `Glob`, `Grep` | 按模式查找文件，用正则搜索内容 |
| **执行** | `Bash` | 运行 shell 命令、脚本、git 操作 |
| **网络** | `WebSearch`, `WebFetch` | 搜索网络，抓取并解析页面 |
| **发现** | `ToolSearch` | 动态按需查找和加载工具，而非预加载全部 |
| **编排** | `Agent`, `Skill`, `AskUserQuestion`, `TaskCreate`, `TaskUpdate` | 派生子代理、调用 Skills、询问用户、跟踪任务 |

除内置工具外，还可以：

- 用 [MCP 服务器](https://code.claude.com/docs/en/agent-sdk/mcp) **连接外部服务**（数据库、浏览器、API）
- 用 [自定义工具处理器](https://code.claude.com/docs/en/agent-sdk/custom-tools) **定义自定义工具**
- 通过 [setting sources](https://code.claude.com/docs/en/agent-sdk/claude-code-features) **加载项目 Skills** 实现可复用工作流

### 工具权限

**Claude 根据任务决定调用哪些工具，但你控制这些调用是否被允许执行。** 你可以自动批准特定工具、完全阻止其他工具，或要求所有工具都需审批。三个选项协同确定什么能运行：

- **`allowed_tools` / `allowedTools`** 自动批准列出的工具。只读 Agent 在 allowed tools 列表中放 `["Read", "Glob", "Grep"]` 则这些工具无需提示即可运行。未列出的工具仍可用但需要权限。
- **`disallowed_tools` / `disallowedTools`** 阻止列出的工具，无视其他设置。参见 [权限](https://code.claude.com/docs/en/agent-sdk/permissions) 了解工具运行前的检查顺序。
- **`permission_mode` / `permissionMode`** 控制未被 allow 或 deny 规则覆盖的工具如何处理。参见 [权限模式](#权限模式)。

还可以用规则如 `"Bash(npm *)"` 限定特定命令。参见 [权限](https://code.claude.com/docs/en/agent-sdk/permissions) 的完整规则语法。

当工具被拒绝时，Claude 收到拒绝消息作为工具结果，通常会尝试其他方法或报告无法继续。

### 并行工具执行

**当 Claude 在单个 Turn 中请求多个工具调用时，两个 SDK 可以根据工具类型并发或顺序运行。** 只读工具（如 `Read`、`Glob`、`Grep` 和标记为只读的 MCP 工具）可以并发运行。修改状态的工具（如 `Edit`、`Write`、`Bash`）顺序运行以避免冲突。

自定义工具默认顺序执行。要启用并行执行，在工具的 annotations 中设置 `readOnlyHint`。TypeScript 和 Python SDK 都使用来自 MCP SDK 的此字段名。

## 控制循环运行

可以限制循环的 Turn 数、成本、Claude 的推理深度以及工具是否需要运行前审批。所有这些都是 [`ClaudeAgentOptions`](https://code.claude.com/docs/en/agent-sdk/python#claudeagentoptions)（Python）/ [`Options`](https://code.claude.com/docs/en/agent-sdk/typescript#options)（TypeScript）上的字段。

### Turns 与预算

| 选项 | 控制内容 | 默认值 |
|:---|:---|:---|
| Max turns (`max_turns` / `maxTurns`) | 最大工具使用往返次数 | 无限制 |
| Max budget (`max_budget_usd` / `maxBudgetUsd`) | 停止前的最大成本 | 无限制 |

触及任一限制时，SDK 返回带对应错误 subtype（`error_max_turns` 或 `error_max_budget_usd`）的 `ResultMessage`。参见 [处理结果](#处理结果) 了解如何检查这些 subtype。

### 推理努力级别（Effort）

**`effort` 选项控制 Claude 投入多少推理。** 较低级别每个 Turn 使用更少 token 并降低成本。并非所有模型支持 effort 参数。参见 [Effort](https://platform.claude.com/docs/en/build-with-claude/effort) 了解支持的模型。

| 级别 | 行为 | 适用场景 |
|:---|:---|:---|
| `"low"` | 最少推理，快速响应 | 文件查找、目录列出 |
| `"medium"` | 平衡推理 | 常规编辑、标准任务 |
| `"high"` | 深入分析 | 重构、调试 |
| `"xhigh"` | 扩展推理深度 | 编码和 Agent 任务；推荐用于 Fable 5、Opus 4.7+ 和 Sonnet 5 |
| `"max"` | 最大推理深度 | 需要深入分析的多步骤问题 |

不设置 `effort` 时，两个 SDK 都不传此参数，使用模型默认行为。

> `effort` 在每次响应内以延迟和 token 成本换取推理深度。[Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking) 是另一个功能，在输出中产出可见的思维链块。两者独立：可以设 `effort: "low"` 同时启用 extended thinking，或设 `effort: "max"` 而不启用。

对执行简单、范围明确的任务（如列文件或运行单次 grep）的 Agent，使用较低 effort 以减少成本和延迟。在顶层 `query()` options 中设置 `effort` 应用于整个会话，或在 [`AgentDefinition`](https://code.claude.com/docs/en/agent-sdk/subagents#agentdefinition-configuration) 的 `effort` 字段中为子代理覆盖会话级别。

### 权限模式

**`permission_mode`（Python）/ `permissionMode`（TypeScript）选项控制 Agent 使用工具前是否需要审批：**

| 模式 | 行为 |
|:---|:---|
| `"default"` | 未被 allow 规则覆盖的工具触发审批回调；无回调则拒绝 |
| `"acceptEdits"` | 自动批准文件编辑和常见文件系统命令（`mkdir`、`touch`、`mv`、`cp` 等）；其他 Bash 命令遵循 default 规则 |
| `"plan"` | Claude 探索和规划但不编辑源文件；文件编辑不自动批准，通过 `canUseTool` 回调提示 |
| `"dontAsk"` | 从不提示。由 [权限规则](https://code.claude.com/docs/en/settings#permission-settings) 预批准的工具运行，其余全部拒绝 |
| `"auto"` | 使用模型分类器批准或拒绝每个工具调用。参见 [Auto 模式](https://code.claude.com/docs/en/permission-modes#eliminate-prompts-with-auto-mode) |
| `"bypassPermissions"` | 运行所有 allowed 工具无需询问，除非匹配明确的 [`ask` 规则](https://code.claude.com/docs/en/settings#permission-settings)。在 Unix 上不能以 root 运行。仅在隔离环境中使用 |

对交互式应用使用 `"default"` 加工具审批回调。对开发机上的自主 Agent，`"acceptEdits"` 自动批准文件编辑和常见文件系统命令同时仍对其他 `Bash` 命令有门控。`"bypassPermissions"` 保留给 CI、容器或其他隔离环境。参见 [权限](https://code.claude.com/docs/en/agent-sdk/permissions)。

### 模型

不设置 `model` 时，SDK 使用 Claude Code 的默认模型（取决于认证方式和订阅）。显式设置（例如 `model="claude-sonnet-5"`）来锁定特定模型，或使用更小模型以获得更快、更便宜的 Agent。参见 [models](https://platform.claude.com/docs/en/about-claude/models) 获取可用 ID。

## 上下文窗口

**上下文窗口是会话期间 Claude 可用的全部信息总量。** 在同一会话的 Turn 之间不会重置，所有内容累积：系统提示词、工具定义、对话历史、工具输入和工具输出。Turn 间不变的内容（系统提示词、工具定义、CLAUDE.md）会自动 [prompt cached](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)，减少重复前缀的成本和延迟。

### 什么消耗上下文

| 来源 | 何时加载 | 影响 |
|:---|:---|:---|
| **系统提示词** | 每次请求 | 固定小成本，始终存在 |
| **CLAUDE.md 文件** | 会话开始时，通过 [`settingSources`](https://code.claude.com/docs/en/agent-sdk/claude-code-features) | 每次请求完整内容（但 prompt-cached，仅首次请求付全价） |
| **工具定义** | 每次请求；MCP schema 默认延迟 | 内置工具 schema 每次请求加载。[Tool search](https://code.claude.com/docs/en/agent-sdk/mcp#mcp-tool-search) 默认延迟 MCP 工具 schema |
| **对话历史** | 逐 Turn 累积 | 随每个 Turn 增长：prompt、响应、工具输入、工具输出 |
| **Skill 描述** | 会话开始时，通过 setting sources | 短摘要；完整内容仅在调用时加载 |

大的工具输出消耗大量上下文。读取大文件或运行输出详细的命令可以在单个 Turn 使用数千 token。上下文跨 Turn 累积，因此有很多工具调用的长会话比短会话积累的上下文显著更多。

### 自动压缩

**当上下文窗口接近限制时，SDK 自动压缩对话：** 总结较早的历史以释放空间，保持最近的交互和关键决策完整。压缩发生时 SDK 在流中产出一条 `type: "system"` 且 `subtype: "compact_boundary"` 的消息（Python 中是 `SystemMessage`；TypeScript 中是独立的 `SDKCompactBoundaryMessage` 类型）。

压缩将旧消息替换为摘要，因此对话早期的特定指令可能不会保留。持久规则应放在 CLAUDE.md（通过 [`settingSources`](https://code.claude.com/docs/en/agent-sdk/claude-code-features) 加载）而非初始 Prompt 中，因为 CLAUDE.md 内容每次请求都重新注入。

自定义压缩行为的几种方式：

- **CLAUDE.md 中的摘要指令：** 压缩器像读取其他上下文一样读取你的 CLAUDE.md，因此可以包含一个章节告诉它摘要时保留什么。标题格式自由（非魔法字符串）；压缩器按意图匹配。
- **`PreCompact` Hook：** 压缩前运行自定义逻辑，例如归档完整转录。Hook 接收 `trigger` 字段（`manual` 或 `auto`）。参见 [Hooks](https://code.claude.com/docs/en/agent-sdk/hooks)。
- **手动压缩：** 发送 `/compact` 作为 prompt 字符串按需触发压缩。这样发送的命令是 SDK 输入，不是 CLI 专有快捷方式。参见 [SDK 中的命令](https://code.claude.com/docs/en/agent-sdk/slash-commands)。

CLAUDE.md 中摘要指令示例：

```markdown
# Summary instructions

When summarizing this conversation, always preserve:
- The current task objective and acceptance criteria
- File paths that have been read or modified
- Test results and error messages
- Decisions made and the reasoning behind them
```

### 保持上下文高效

**长时间运行 Agent 的几个策略：**

- **用子代理处理子任务。** 每个子代理以全新对话开始（无先前消息历史，但会加载自己的系统提示词和项目级上下文如 CLAUDE.md）。它看不到父级的 Turn，只有最终响应作为工具结果返回给父级。主 Agent 的上下文只增长该摘要，而非完整子任务转录。参见 [子代理继承什么](https://code.claude.com/docs/en/agent-sdk/subagents#what-subagents-inherit)。
- **精选工具。** 每个工具定义占上下文空间。用 [`AgentDefinition`](https://code.claude.com/docs/en/agent-sdk/subagents#agentdefinition-configuration) 上的 `tools` 字段将子代理限制在最小所需集。
- **注意 MCP 服务器成本。** [MCP tool search](https://code.claude.com/docs/en/agent-sdk/mcp#mcp-tool-search) 默认延迟 MCP 工具 schema 按需加载。当 tool search 关闭时，每个 MCP 服务器的所有工具 schema 都加入每次请求，几个工具多的服务器可能在 Agent 开始工作前就消耗大量上下文。
- **常规任务用低 effort。** 对只需读文件或列目录的 Agent 设置 [effort](#推理努力级别effort) 为 `"low"`，减少 token 用量和成本。

每个功能的上下文成本详细分解，参见 [理解上下文成本](https://code.claude.com/docs/en/features-overview#understand-context-costs)。

## 会话与连续性

**每次与 SDK 的交互都创建或继续一个会话。** 从 `ResultMessage.session_id`（两个 SDK 都有）捕获 session ID 以便稍后恢复。TypeScript SDK 还在 init `SystemMessage` 上直接暴露它；Python 中嵌套在 `SystemMessage.data` 中。

恢复时，之前 Turn 的完整上下文被还原：读取过的文件、执行过的分析和采取过的操作。还可以 fork 会话以分叉到不同方案而不修改原始会话。

参见 [会话管理](https://code.claude.com/docs/en/agent-sdk/sessions) 了解 resume、continue 和 fork 模式的完整指南。

> Python 中，`ClaudeSDKClient` 跨多次调用自动处理 session ID。参见 [Python SDK 参考](https://code.claude.com/docs/en/agent-sdk/python#choosing-between-query-and-claudesdkclient)。

## 处理结果

**循环结束时，`ResultMessage` 告诉你发生了什么并给出输出。** `subtype` 字段（两个 SDK 都有）是检查终止状态的主要方式。

| Result subtype | 发生了什么 | `result` 字段可用？ |
|:---|:---|:---:|
| `success` | Claude 正常完成任务 | 是 |
| `error_max_turns` | 在完成前触及 `maxTurns` 限制 | 否 |
| `error_max_budget_usd` | 在完成前触及 `maxBudgetUsd` 限制 | 否 |
| `error_during_execution` | 错误中断了循环（例如 API 故障或请求取消） | 否 |
| `error_max_structured_output_retries` | 在配置的重试次数内未产出有效的结构化输出 | 否 |

`result` 字段（最终文本输出）仅在 `success` 变体上存在，因此读取前一定要先检查 subtype。所有结果 subtype 都带 `total_cost_usd`、`usage`、`num_turns` 和 `session_id`，即使错误后也能追踪成本并恢复。Python 中 `total_cost_usd` 和 `usage` 类型为 optional，某些错误路径可能为 `None`，格式化前需要判断。参见 [成本和用量追踪](https://code.claude.com/docs/en/agent-sdk/cost-tracking)。

> 当查询以错误结果结束时：
> - 单次 `query()` 调用产出最终 result 消息后抛出错误（包含失败文本如 `Reached maximum number of turns`）。抛出是有意为之 — 如果代码需要继续执行，将循环包裹在 try 块中。底层 Claude Code 进程也以非零码退出。
> - 流式输入会话保持存活，可以继续发送消息。

结果还包含 `stop_reason` 字段（TypeScript 中 `string | null`，Python 中 `str | None`），表示模型在最后一个 Turn 为何停止生成。常见值为 `end_turn`（模型正常结束）、`max_tokens`（达到输出 token 限制）和 `refusal`（模型拒绝请求）。错误结果 subtype 上，`stop_reason` 携带循环结束前最后一次 assistant 响应的值。检测拒绝用 `stop_reason === "refusal"`（TypeScript）或 `stop_reason == "refusal"`（Python）。

## Hooks

**[Hooks](https://code.claude.com/docs/en/agent-sdk/hooks) 是在循环特定节点触发的回调：** 工具运行前、返回后、Agent 完成时等。常用 Hooks：

| Hook | 触发时机 | 常见用途 |
|:---|:---|:---|
| `PreToolUse` | 工具执行前 | 验证输入，阻止危险命令 |
| `PostToolUse` | 工具返回后 | 审计输出，触发副作用 |
| `UserPromptSubmit` | 发送 Prompt 时 | 向 Prompt 注入额外上下文 |
| `Stop` | Agent 完成时 | 验证结果，保存会话状态 |
| `SubagentStart` / `SubagentStop` | 子代理启动或完成时 | 追踪和聚合并行任务结果 |
| `PreCompact` | 上下文压缩前 | 摘要前归档完整转录 |

Hooks 在你的应用进程中运行，不在 Agent 的上下文窗口内，因此不消耗上下文。Hooks 还可以短路循环：`PreToolUse` Hook 拒绝工具调用会阻止其执行，Claude 收到拒绝消息代替。

两个 SDK 都支持上述所有事件。TypeScript SDK 包含 Python 尚不支持的额外事件。参见 [Hooks 控制执行](https://code.claude.com/docs/en/agent-sdk/hooks) 了解完整事件列表、SDK 可用性和完整回调 API。

## 综合示例

**下面的示例将本页关键概念组合到一个修复失败测试的 Agent 中。** 它配置 allowed tools（自动批准使 Agent 自主运行）、项目设置和 Turn/推理 effort 的安全限制。循环运行时捕获 session ID 以备恢复，处理最终结果并输出总成本。

因为单次 `query()` 在错误结果后会抛异常，循环包裹在 try 块中以便触及限制时干净退出。

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


async def run_agent():
    session_id = None

    try:
        async for message in query(
            prompt="Find and fix the bug causing test failures in the auth module",
            options=ClaudeAgentOptions(
                allowed_tools=[
                    "Read",
                    "Edit",
                    "Bash",
                    "Glob",
                    "Grep",
                ],  # 列在这里自动批准（无提示）
                setting_sources=[
                    "project"
                ],  # 从当前目录加载 CLAUDE.md、skills、hooks
                max_turns=30,  # 防止失控会话
                effort="high",  # 复杂调试需要深入推理
            ),
        ):
            # 处理最终结果
            if isinstance(message, ResultMessage):
                session_id = message.session_id  # 保存以备恢复

                if message.subtype == "success":
                    print(f"Done: {message.result}")
                elif message.subtype == "error_max_turns":
                    # Agent Turn 用尽。用更高限制恢复。
                    print(f"Hit turn limit. Resume session {session_id} to continue.")
                elif message.subtype == "error_max_budget_usd":
                    print("Hit budget limit.")
                else:
                    print(f"Stopped: {message.subtype}")
                if message.total_cost_usd is not None:
                    print(f"Cost: ${message.total_cost_usd:.4f}")
    except Exception as error:
        # 单次 query() 在产出错误结果后抛异常。如果失败是错误结果，
        # 上面的 subtype 分支已执行；连接或进程失败则不产出 result 消息。
        print(f"Session ended with an error: {error}")


asyncio.run(run_agent())
```

## 下一步

理解循环后，根据你在构建什么选择下一步：

- **还没运行过 Agent？** 从 [快速开始](https://code.claude.com/docs/en/agent-sdk/quickstart) 开始，安装 SDK 并看到完整示例运行。
- **准备接入项目？** [加载 CLAUDE.md、Skills 和文件系统 Hooks](https://code.claude.com/docs/en/agent-sdk/claude-code-features) 让 Agent 自动遵循项目约定。
- **构建交互式 UI？** 启用 [流式输出](https://code.claude.com/docs/en/agent-sdk/streaming-output) 在循环运行时实时显示文本和工具调用。
- **需要更严格控制 Agent 能做什么？** 用 [权限](https://code.claude.com/docs/en/agent-sdk/permissions) 锁定工具访问，用 [Hooks](https://code.claude.com/docs/en/agent-sdk/hooks) 在工具执行前审计、阻止或转换调用。
- **运行长时间或高成本任务？** 将隔离工作卸载到 [子代理](https://code.claude.com/docs/en/agent-sdk/subagents) 以保持主上下文精简。

更广泛的 Agent 循环概念（非 SDK 特定），参见 [Claude Code 工作原理](https://code.claude.com/docs/en/how-claude-code-works)。
