---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
category: translation
tags: [claude-code, agent-sdk, translation]
description: Claude Agent SDK 的 Hooks 机制详解，涵盖如何在工具调用前后拦截操作、阻止危险命令、修改输入输出，以及转发通知到外部服务。
refs:
  - https://code.claude.com/docs/en/agent-sdk/hooks
  - en-source/agent-sdk/hooks.md
title: 【译】Agent SDK - Hooks
---

# 【译】SDK Hooks

> 通过 Hooks 在关键执行节点拦截和自定义 Agent 行为

**Hooks 是在 Agent 事件发生时执行自定义代码的回调函数。** 比如工具被调用、会话开始、执行停止时都会触发。通过 Hooks，你可以：

* **阻止危险操作** — 在执行之前拦截破坏性 shell 命令或未授权的文件访问
* **记录和审计** — 对每次工具调用进行合规、调试或分析日志记录
* **转换输入和输出** — 清洗数据、注入凭证或重定向文件路径
* **要求人工审批** — 对数据库写入或 API 调用等敏感操作进行把关
* **跟踪会话生命周期** — 管理状态、清理资源或发送通知

本文介绍 Hooks 的工作原理和配置方式，并提供阻止工具、修改输入和转发通知等常见模式的示例。

## Hooks 工作原理

**Hooks 的执行分为五个步骤：**

1. **事件触发** — Agent 执行过程中发生某件事，SDK 触发事件：工具即将被调用（`PreToolUse`）、工具返回结果（`PostToolUse`）、子 Agent 启动或停止、Agent 空闲、或执行结束。完整事件列表见[可用 Hooks](#可用-hooks)。

2. **SDK 收集已注册的 Hooks** — SDK 检查为该事件类型注册的 Hooks，包括你在 `options.hooks` 中传入的回调 Hooks，以及当相应的 [`settingSources`](https://code.claude.com/docs/en/agent-sdk/typescript#settingsource) 或 [`setting_sources`](https://code.claude.com/docs/en/agent-sdk/python#settingsource) 条目启用时从设置文件加载的 shell 命令 Hooks（默认 `query()` 选项中已启用）。

3. **Matcher 过滤哪些 Hooks 运行** — 如果 Hook 配置了 [`matcher`](#matcher-匹配器) 模式（如 `"Write|Edit"`），SDK 会将其与事件目标（例如工具名称）进行匹配。没有 matcher 的 Hook 会对该类型的每个事件运行。

4. **回调函数执行** — 每个匹配的 Hook 的[回调函数](#回调函数)接收当前发生的信息：工具名称、参数、会话 ID 和其他事件特定的详情。

5. **回调返回决策** — 执行任何操作（日志记录、API 调用、校验）后，回调返回一个[输出对象](#输出)，告诉 Agent 下一步该怎么做：允许操作、阻止操作、修改输入或向对话注入上下文。

以下示例将这些步骤组合在一起。它注册了一个 `PreToolUse` Hook（步骤 1），配置了 `"Write|Edit"` matcher（步骤 3），使回调仅对文件写入工具触发。当被触发时，回调接收工具的输入（步骤 4），检查文件路径是否指向 `.env` 文件，如果是则返回 `permissionDecision: "deny"` 来阻止操作（步骤 5）：

```python
import asyncio
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeSDKClient,
    ClaudeAgentOptions,
    HookMatcher,
    ResultMessage,
)


# 定义一个 Hook 回调，接收工具调用详情
async def protect_env_files(input_data, tool_use_id, context):
    # 从工具输入参数中提取文件路径
    file_path = input_data["tool_input"].get("file_path", "")
    file_name = file_path.split("/")[-1]

    # 如果目标是 .env 文件则阻止操作
    if file_name == ".env":
        return {
            "hookSpecificOutput": {
                "hookEventName": input_data["hook_event_name"],
                "permissionDecision": "deny",
                "permissionDecisionReason": "Cannot modify .env files",
            }
        }

    # 返回空对象表示允许操作
    return {}


async def main():
    options = ClaudeAgentOptions(
        hooks={
            # 为 PreToolUse 事件注册 Hook
            # matcher 过滤为只匹配 Write 和 Edit 工具调用
            "PreToolUse": [HookMatcher(matcher="Write|Edit", hooks=[protect_env_files])]
        }
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("Update the database configuration")
        async for message in client.receive_response():
            # 过滤助手消息和结果消息
            if isinstance(message, (AssistantMessage, ResultMessage)):
                print(message)


asyncio.run(main())
```

```typescript
import { query, HookCallback, PreToolUseHookInput } from "@anthropic-ai/claude-agent-sdk";

// 定义一个 Hook 回调，使用 HookCallback 类型
const protectEnvFiles: HookCallback = async (input, toolUseID, { signal }) => {
  // 转为特定 Hook 类型以获得类型安全
  const preInput = input as PreToolUseHookInput;

  // 转换 tool_input 以访问其属性（SDK 中类型为 unknown）
  const toolInput = preInput.tool_input as Record<string, unknown>;
  const filePath = toolInput?.file_path as string;
  const fileName = filePath?.split("/").pop();

  // 如果目标是 .env 文件则阻止操作
  if (fileName === ".env") {
    return {
      hookSpecificOutput: {
        hookEventName: preInput.hook_event_name,
        permissionDecision: "deny",
        permissionDecisionReason: "Cannot modify .env files"
      }
    };
  }

  // 返回空对象表示允许操作
  return {};
};

for await (const message of query({
  prompt: "Update the database configuration",
  options: {
    hooks: {
      // 为 PreToolUse 事件注册 Hook
      // matcher 过滤为只匹配 Write 和 Edit 工具调用
      PreToolUse: [{ matcher: "Write|Edit", hooks: [protectEnvFiles] }]
    }
  }
})) {
  // 过滤助手消息和结果消息
  if (message.type === "assistant" || message.type === "result") {
    console.log(message);
  }
}
```

## 可用 Hooks

**SDK 为 Agent 执行的不同阶段提供了 Hooks。** 部分 Hooks 在两个 SDK 中都可用，其他仅限 TypeScript。

| Hook 事件 | Python SDK | TypeScript SDK | 触发条件 | 使用场景示例 |
| :--- | :--- | :--- | :--- | :--- |
| `PreToolUse` | 支持 | 支持 | 工具调用请求（可阻止或修改） | 阻止危险的 shell 命令 |
| `PostToolUse` | 支持 | 支持 | 工具执行结果 | 将所有文件变更记录到审计轨迹 |
| `PostToolUseFailure` | 支持 | 支持 | 工具执行失败 | 处理或记录工具错误 |
| `PostToolBatch` | 不支持 | 支持 | 一批工具调用全部完成，在下一次模型调用前触发一次 | 为整个批次注入一次约定 |
| `UserPromptSubmit` | 支持 | 支持 | 用户提示提交 | 向提示注入额外上下文 |
| `MessageDisplay` | 不支持 | 支持 | 带文本的助手消息完成，每条消息触发一次 | 对显示文本进行脱敏或重新格式化 |
| `Stop` | 支持 | 支持 | Agent 执行停止 | 退出前保存会话状态 |
| `SubagentStart` | 支持 | 支持 | 子 Agent 初始化 | 跟踪并行任务的生成 |
| `SubagentStop` | 支持 | 支持 | 子 Agent 完成 | 汇总并行任务的结果 |
| `PreCompact` | 支持 | 支持 | 对话压缩请求 | 在摘要前归档完整记录 |
| `PermissionRequest` | 支持 | 支持 | 权限对话框将显示 | 自定义权限处理 |
| `SessionStart` | 不支持 | 支持 | 会话初始化 | 初始化日志和遥测 |
| `SessionEnd` | 不支持 | 支持 | 会话终止 | 清理临时资源 |
| `Notification` | 支持 | 支持 | Agent 状态消息 | 发送状态更新到 Slack 或 PagerDuty |
| `Setup` | 不支持 | 支持 | 会话设置/维护 | 运行初始化任务 |
| `TeammateIdle` | 不支持 | 支持 | 队友变为空闲 | 重新分配工作或通知 |
| `TaskCompleted` | 不支持 | 支持 | 后台任务完成 | 汇总并行任务的结果 |
| `ConfigChange` | 不支持 | 支持 | 配置文件变更 | 动态重新加载设置 |
| `WorktreeCreate` | 不支持 | 支持 | Git worktree 创建 | 跟踪隔离工作空间 |
| `WorktreeRemove` | 不支持 | 支持 | Git worktree 删除 | 清理工作空间资源 |

## 配置 Hooks

**在 agent options 的 `hooks` 字段中传入配置即可注册 Hook。** Python 使用 `ClaudeAgentOptions`，TypeScript 使用 `options` 对象：

```python
options = ClaudeAgentOptions(
    hooks={"PreToolUse": [HookMatcher(matcher="Bash", hooks=[my_callback])]}
)

async with ClaudeSDKClient(options=options) as client:
    await client.query("Your prompt")
    async for message in client.receive_response():
        print(message)
```

```typescript
for await (const message of query({
  prompt: "Your prompt",
  options: {
    hooks: {
      PreToolUse: [{ matcher: "Bash", hooks: [myCallback] }]
    }
  }
})) {
  console.log(message);
}
```

`hooks` 选项是一个字典（Python）或对象（TypeScript），其中：

* **键**：[Hook 事件名称](#可用-hooks)，如 `'PreToolUse'`、`'PostToolUse'`、`'Stop'`
* **值**：[matcher](#matcher-匹配器) 数组，每个包含一个可选的过滤模式和你的[回调函数](#回调函数)

### Matcher 匹配器

**使用 matcher 来过滤回调的触发时机。** `matcher` 字段根据 Hook 事件类型匹配不同的值。例如，基于工具的 Hooks 匹配工具名称，而 `Notification` Hooks 匹配通知类型。完整的 matcher 值列表见 [Claude Code hooks 参考](https://code.claude.com/docs/en/hooks#matcher-patterns)。

SDK 的 matcher 遵循与[设置文件中 matcher 相同的规则](https://code.claude.com/docs/en/hooks#matcher-patterns)。仅包含字母、数字、`_`、`-`、空格、`,` 和 `|` 的 matcher 会作为精确字符串比较，备选项用 `|` 或 `,` 分隔（可选前后空格），因此 `Write|Edit` 和 `Write, Edit` 各匹配这两个工具，`code-reviewer` 只匹配该 agent 类型。matcher 为 `*`、空字符串或省略 matcher 则匹配该事件的所有出现。

包含其他字符的 matcher 会作为非锚定正则表达式求值，因此 `^mcp__` 匹配所有 MCP 工具，`Edit.*` 同时匹配 `Edit` 和 `NotebookEdit`。需要完整字符串匹配时用 `^` 和 `$` 包裹。

像 `mcp__memory` 或 `mcp__brave-search` 这样的 matcher 只包含精确匹配字符，会作为精确字符串比较，不匹配任何工具；使用 `mcp__memory__.*` 来匹配该服务器的所有工具。

精确匹配集中的连字符要求 Claude Code 运行时版本 v2.1.195 或更高。在更早版本上，像 `code-reviewer` 这样带连字符的名称会被当作非锚定正则表达式求值，必须锚定为 `^code-reviewer$` 才能精确匹配。

| 选项 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `matcher` | <code>string</code> | `undefined` | 匹配事件过滤字段的模式，遵循上述比较规则。对于工具 Hooks，这是工具名称。内置工具包括 `Bash`、`Read`、`Write`、`Edit`、`Glob`、`Grep`、`WebFetch`、`Agent` 等（完整列表见 [Tool Input Types](https://code.claude.com/docs/en/agent-sdk/typescript#tool-input-types)）。MCP 工具使用 `mcp__<server>__<action>` 模式。 |
| `hooks` | <code>HookCallback[]</code> | - | 必需。模式匹配时执行的回调函数数组 |
| `timeout` | <code>number</code> | `60` | 超时时间（秒） |

尽可能使用 `matcher` 模式来针对特定工具。`'Bash'` 的 matcher 只对 Bash 命令运行，而省略模式则对该事件的所有出现运行回调。

对于基于工具的 Hooks，matcher 只按工具名称过滤，不按文件路径或其他参数过滤。要按文件路径过滤，在回调内检查 `tool_input.file_path`。

> **发现工具名称：** 完整的内置工具名称列表见 [Tool Input Types](https://code.claude.com/docs/en/agent-sdk/typescript#tool-input-types)，或者添加一个不带 matcher 的 Hook 来记录会话中所有工具调用。
>
> **MCP 工具命名：** MCP 工具始终以 `mcp__` 开头，后接服务器名称和操作：`mcp__<server>__<action>`。例如配置名为 `playwright` 的服务器，其工具命名为 `mcp__playwright__browser_screenshot`、`mcp__playwright__browser_click` 等。服务器名称来自 `mcpServers` 配置中使用的键名。

### 回调函数

#### 输入

**每个 Hook 回调接收三个参数：**

| 参数 | 说明 |
| :--- | :--- |
| **Input data** | 包含事件详情的类型化对象。每种 Hook 类型有自己的输入结构。例如 `PreToolUseHookInput` 包含 `tool_name` 和 `tool_input`，`NotificationHookInput` 包含 `message`。完整类型定义见 [TypeScript](https://code.claude.com/docs/en/agent-sdk/typescript#hookinput) 和 [Python](https://code.claude.com/docs/en/agent-sdk/python#hookinput) SDK 参考。所有 Hook 输入共享 `session_id`、`cwd` 和 `hook_event_name`。`agent_id` 和 `agent_type` 在 Hook 在子 Agent 内触发时填充。 |
| **Tool use ID** | <code>str \| None</code> / <code>string \| undefined</code>：关联同一工具调用的 `PreToolUse` 和 `PostToolUse` 事件。 |
| **Context** | TypeScript 中包含 `signal` 属性（`AbortSignal`）用于取消。Python 中此参数保留供将来使用。 |

#### 输出

**回调返回一个包含两类字段的对象：**

* **顶层字段** 在所有事件上行为一致：`systemMessage` 向用户显示消息，`continue`（Python 中为 `continue_`）决定 Hook 之后 Agent 是否继续运行。
* **`hookSpecificOutput`** 控制当前操作。内部字段取决于 Hook 事件类型。对于 `PreToolUse` Hooks，在这里设置 `permissionDecision`（`"allow"`、`"deny"`、`"ask"` 或 `"defer"`）、`permissionDecisionReason` 和 `updatedInput`。返回 `"defer"` 会结束查询，以便你稍后[恢复它](https://code.claude.com/docs/en/hooks#defer-a-tool-call-for-later)。对于 `PostToolUse` Hooks，可以设置 `additionalContext` 将信息附加到工具结果。要在 Claude 看到之前替换工具的输出，设置 `updatedToolOutput`，该字段适用于两个 SDK 中的任何工具。旧的 `updatedMCPToolOutput` 字段仅替换 MCP 工具输出且已弃用。

返回 `{}` 表示允许操作不做更改。SDK 回调 Hooks 使用与 [Claude Code shell 命令 Hooks](https://code.claude.com/docs/en/hooks#json-output) 相同的 JSON 输出格式，其中记录了每个字段和事件特定选项。SDK 类型定义见 [TypeScript](https://code.claude.com/docs/en/agent-sdk/typescript#synchookjsonoutput) 和 [Python](https://code.claude.com/docs/en/agent-sdk/python#synchookjsonoutput) SDK 参考。

> **多个 Hooks 的优先级：** 当多个 Hooks 或权限规则适用时，`deny` 优先于 `defer`，`defer` 优先于 `ask`，`ask` 优先于 `allow`。任何一个 Hook 返回 `deny`，操作就会被阻止，无论其他 Hooks 返回什么。

#### 异步输出

**默认情况下，Agent 会等待 Hook 返回后再继续。** 如果你的 Hook 执行的是副作用（如日志记录或发送 webhook），不需要影响 Agent 行为，可以返回异步输出。这告诉 Agent 立即继续，不等待 Hook 完成：

```python
async def async_hook(input_data, tool_use_id, context):
    # 启动后台任务，然后立即返回
    asyncio.create_task(send_to_logging_service(input_data))
    return {"async_": True, "asyncTimeout": 30000}
```

```typescript
const asyncHook: HookCallback = async (input, toolUseID, { signal }) => {
  // 启动后台任务，然后立即返回
  sendToLoggingService(input).catch(console.error);
  return { async: true, asyncTimeout: 30000 };
};
```

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `async` | <code>true</code> | 标识异步模式。Agent 继续而不等待。Python 中使用 `async_` 避免关键字冲突。 |
| `asyncTimeout` | <code>number</code> | 后台操作的可选超时时间（毫秒） |

> 异步输出无法阻止、修改或向操作注入上下文，因为 Agent 已经继续前进了。仅用于日志记录、指标收集或通知等副作用。

## 示例

### 修改工具输入

**此示例拦截 Write 工具调用，将 `file_path` 参数重写为添加 `/sandbox` 前缀，** 将所有文件写入重定向到沙盒目录。回调返回 `updatedInput`（包含修改后的路径）和 `permissionDecision: 'allow'` 来自动批准重写后的操作：

```python
async def redirect_to_sandbox(input_data, tool_use_id, context):
    if input_data["hook_event_name"] != "PreToolUse":
        return {}

    if input_data["tool_name"] == "Write":
        original_path = input_data["tool_input"].get("file_path", "")
        return {
            "hookSpecificOutput": {
                "hookEventName": input_data["hook_event_name"],
                "permissionDecision": "allow",
                "updatedInput": {
                    **input_data["tool_input"],
                    "file_path": f"/sandbox{original_path}",
                },
            }
        }
    return {}
```

```typescript
const redirectToSandbox: HookCallback = async (input, toolUseID, { signal }) => {
  if (input.hook_event_name !== "PreToolUse") return {};

  const preInput = input as PreToolUseHookInput;
  const toolInput = preInput.tool_input as Record<string, unknown>;
  if (preInput.tool_name === "Write") {
    const originalPath = toolInput.file_path as string;
    return {
      hookSpecificOutput: {
        hookEventName: preInput.hook_event_name,
        permissionDecision: "allow",
        updatedInput: {
          ...toolInput,
          file_path: `/sandbox${originalPath}`
        }
      }
    };
  }
  return {};
};
```

> 使用 `updatedInput` 时，必须同时包含 `permissionDecision: 'allow'` 来自动批准修改后的输入，或 `permissionDecision: 'ask'` 来让用户确认。使用 `'defer'` 时 `updatedInput` 会被忽略。始终返回新对象而不是修改原始 `tool_input`。

### 添加上下文并阻止工具

**此示例阻止向 `/etc` 目录写入，并向模型和用户解释原因：**

* `permissionDecision: 'deny'` — 停止工具调用
* `permissionDecisionReason` — 告诉模型原因，使其避免重试
* `systemMessage` — 向用户展示发生了什么

```python
async def block_etc_writes(input_data, tool_use_id, context):
    file_path = input_data["tool_input"].get("file_path", "")

    if file_path.startswith("/etc"):
        return {
            # 顶层字段：向用户显示的消息
            "systemMessage": "Remember: system directories like /etc are protected.",
            # hookSpecificOutput：阻止操作
            "hookSpecificOutput": {
                "hookEventName": input_data["hook_event_name"],
                "permissionDecision": "deny",
                "permissionDecisionReason": "Writing to /etc is not allowed",
            },
        }
    return {}
```

```typescript
const blockEtcWrites: HookCallback = async (input, toolUseID, { signal }) => {
  const preInput = input as PreToolUseHookInput;
  const toolInput = preInput.tool_input as Record<string, unknown>;
  const filePath = toolInput?.file_path as string;

  if (filePath?.startsWith("/etc")) {
    return {
      // 顶层字段：向用户显示的消息
      systemMessage: "Remember: system directories like /etc are protected.",
      // hookSpecificOutput：阻止操作
      hookSpecificOutput: {
        hookEventName: preInput.hook_event_name,
        permissionDecision: "deny",
        permissionDecisionReason: "Writing to /etc is not allowed"
      }
    };
  }
  return {};
};
```

### 自动批准特定工具

**默认情况下，Agent 在使用某些工具前可能会提示权限确认。** 此示例通过返回 `permissionDecision: 'allow'` 来自动批准只读文件系统工具（Read、Glob、Grep），让它们无需用户确认即可运行，而其他所有工具仍遵循正常权限检查：

```python
async def auto_approve_read_only(input_data, tool_use_id, context):
    if input_data["hook_event_name"] != "PreToolUse":
        return {}

    read_only_tools = ["Read", "Glob", "Grep"]
    if input_data["tool_name"] in read_only_tools:
        return {
            "hookSpecificOutput": {
                "hookEventName": input_data["hook_event_name"],
                "permissionDecision": "allow",
                "permissionDecisionReason": "Read-only tool auto-approved",
            }
        }
    return {}
```

```typescript
const autoApproveReadOnly: HookCallback = async (input, toolUseID, { signal }) => {
  if (input.hook_event_name !== "PreToolUse") return {};

  const preInput = input as PreToolUseHookInput;
  const readOnlyTools = ["Read", "Glob", "Grep"];
  if (readOnlyTools.includes(preInput.tool_name)) {
    return {
      hookSpecificOutput: {
        hookEventName: preInput.hook_event_name,
        permissionDecision: "allow",
        permissionDecisionReason: "Read-only tool auto-approved"
      }
    };
  }
  return {};
};
```

### 注册多个 Hooks

**当事件触发时，所有匹配的 Hooks 并行运行。** 对于权限决策，最严格的结果生效：单个 `deny` 会阻止工具调用，无论其他 Hooks 返回什么。因为完成顺序是非确定性的，编写每个 Hook 时应独立运作，不依赖另一个 Hook 是否已经运行。

以下示例为每次工具调用注册了三个独立的检查：

```python
options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(hooks=[authorization_check]),
            HookMatcher(hooks=[input_validator]),
            HookMatcher(hooks=[audit_logger]),
        ]
    }
)
```

```typescript
const options = {
  hooks: {
    PreToolUse: [
      { hooks: [authorizationCheck] },
      { hooks: [inputValidator] },
      { hooks: [auditLogger] }
    ]
  }
};
```

### 使用多工具 Matcher 过滤

**使用多工具 matcher 将一个回调共享给相关工具。** 此示例注册了三个不同作用域的 matcher：

* 管道分隔的精确列表（`Write|Edit|Delete`）— 仅对文件修改工具触发 `file_security_hook`
* 正则表达式（`^mcp__`）— 对任何名称以 `mcp__` 开头的 MCP 工具触发 `mcp_audit_hook`
* 省略 matcher — 对所有工具调用触发 `global_logger`

```python
options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            # 匹配文件修改工具
            HookMatcher(matcher="Write|Edit|Delete", hooks=[file_security_hook]),
            # 匹配所有 MCP 工具
            HookMatcher(matcher="^mcp__", hooks=[mcp_audit_hook]),
            # 匹配所有（无 matcher）
            HookMatcher(hooks=[global_logger]),
        ]
    }
)
```

```typescript
const options = {
  hooks: {
    PreToolUse: [
      // 匹配文件修改工具
      { matcher: "Write|Edit|Delete", hooks: [fileSecurityHook] },

      // 匹配所有 MCP 工具
      { matcher: "^mcp__", hooks: [mcpAuditHook] },

      // 匹配所有（无 matcher）
      { hooks: [globalLogger] }
    ]
  }
};
```

### 跟踪子 Agent 活动

**使用 `SubagentStop` Hooks 来监控子 Agent 何时完成工作。** 完整输入类型见 [TypeScript](https://code.claude.com/docs/en/agent-sdk/typescript#hookinput) 和 [Python](https://code.claude.com/docs/en/agent-sdk/python#hookinput) SDK 参考。此示例在每次子 Agent 完成时记录摘要：

```python
async def subagent_tracker(input_data, tool_use_id, context):
    # 子 Agent 完成时记录详情
    print(f"[SUBAGENT] Completed: {input_data['agent_id']}")
    print(f"  Transcript: {input_data['agent_transcript_path']}")
    print(f"  Tool use ID: {tool_use_id}")
    print(f"  Stop hook active: {input_data.get('stop_hook_active')}")
    return {}


options = ClaudeAgentOptions(
    hooks={"SubagentStop": [HookMatcher(hooks=[subagent_tracker])]}
)
```

```typescript
import { HookCallback, SubagentStopHookInput } from "@anthropic-ai/claude-agent-sdk";

const subagentTracker: HookCallback = async (input, toolUseID, { signal }) => {
  // 转为 SubagentStopHookInput 以访问子 Agent 特定字段
  const subInput = input as SubagentStopHookInput;

  // 子 Agent 完成时记录详情
  console.log(`[SUBAGENT] Completed: ${subInput.agent_id}`);
  console.log(`  Transcript: ${subInput.agent_transcript_path}`);
  console.log(`  Tool use ID: ${toolUseID}`);
  console.log(`  Stop hook active: ${subInput.stop_hook_active}`);
  return {};
};

const options = {
  hooks: {
    SubagentStop: [{ hooks: [subagentTracker] }]
  }
};
```

### 从 Hooks 发起 HTTP 请求

**Hooks 可以执行异步操作如 HTTP 请求。** 在 Hook 内部捕获错误而不是让其传播，因为未处理的异常可能中断 Agent。

此示例在每个工具完成后发送 webhook，记录哪个工具运行了以及时间。Hook 捕获错误以确保失败的 webhook 不会中断 Agent：

```python
import asyncio
import json
import urllib.request
from datetime import datetime


def _send_webhook(tool_name):
    """同步辅助函数，将工具使用数据 POST 到外部 webhook。"""
    data = json.dumps(
        {
            "tool": tool_name,
            "timestamp": datetime.now().isoformat(),
        }
    ).encode()
    req = urllib.request.Request(
        "https://api.example.com/webhook",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    urllib.request.urlopen(req)


async def webhook_notifier(input_data, tool_use_id, context):
    # 仅在工具完成后（PostToolUse）触发，不在之前
    if input_data["hook_event_name"] != "PostToolUse":
        return {}

    try:
        # 在线程中运行阻塞 HTTP 调用以避免阻塞事件循环
        await asyncio.to_thread(_send_webhook, input_data["tool_name"])
    except Exception as e:
        # 记录错误但不抛出。失败的 webhook 不应停止 Agent
        print(f"Webhook request failed: {e}")

    return {}
```

```typescript
import { query, HookCallback, PostToolUseHookInput } from "@anthropic-ai/claude-agent-sdk";

const webhookNotifier: HookCallback = async (input, toolUseID, { signal }) => {
  // 仅在工具完成后（PostToolUse）触发，不在之前
  if (input.hook_event_name !== "PostToolUse") return {};

  try {
    await fetch("https://api.example.com/webhook", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tool: (input as PostToolUseHookInput).tool_name,
        timestamp: new Date().toISOString()
      }),
      // 传递 signal 以便 Hook 超时时请求被取消
      signal
    });
  } catch (error) {
    // 单独处理取消错误
    if (error instanceof Error && error.name === "AbortError") {
      console.log("Webhook request cancelled");
    }
    // 不重新抛出。失败的 webhook 不应停止 Agent
  }

  return {};
};

// 注册为 PostToolUse Hook
for await (const message of query({
  prompt: "Refactor the auth module",
  options: {
    hooks: {
      PostToolUse: [{ hooks: [webhookNotifier] }]
    }
  }
})) {
  console.log(message);
}
```

### 转发通知到 Slack

**使用 `Notification` Hooks 接收 Agent 的系统通知并转发到外部服务。** 通知会针对以下事件类型触发：

* `permission_prompt` — Claude 需要权限时
* `idle_prompt` — Claude 等待输入时
* `auth_success` — 认证完成时
* `elicitation_dialog`、`elicitation_complete` 和 `elicitation_response` — 用户提示问询流程

每个通知包含一个 `message` 字段（人类可读描述）和可选的 `title`。

此示例将每个通知转发到 Slack 频道。需要一个 [Slack incoming webhook URL](https://api.slack.com/messaging/webhooks)：

```python
import asyncio
import json
import urllib.request

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, HookMatcher


def _send_slack_notification(message):
    """同步辅助函数，通过 incoming webhook 发送消息到 Slack。"""
    data = json.dumps({"text": f"Agent status: {message}"}).encode()
    req = urllib.request.Request(
        "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    urllib.request.urlopen(req)


async def notification_handler(input_data, tool_use_id, context):
    try:
        # 在线程中运行阻塞 HTTP 调用以避免阻塞事件循环
        await asyncio.to_thread(_send_slack_notification, input_data.get("message", ""))
    except Exception as e:
        print(f"Failed to send notification: {e}")

    # 返回空对象。Notification Hooks 不修改 Agent 行为
    return {}


async def main():
    options = ClaudeAgentOptions(
        hooks={
            # 为 Notification 事件注册 Hook（不需要 matcher）
            "Notification": [HookMatcher(hooks=[notification_handler])],
        },
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("Analyze this codebase")
        async for message in client.receive_response():
            print(message)


asyncio.run(main())
```

```typescript
import { query, HookCallback, NotificationHookInput } from "@anthropic-ai/claude-agent-sdk";

// 定义一个将通知发送到 Slack 的 Hook 回调
const notificationHandler: HookCallback = async (input, toolUseID, { signal }) => {
  // 转为 NotificationHookInput 以访问 message 字段
  const notification = input as NotificationHookInput;

  try {
    // 将通知消息 POST 到 Slack incoming webhook
    await fetch("https://hooks.slack.com/services/YOUR/WEBHOOK/URL", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: `Agent status: ${notification.message}`
      }),
      // 传递 signal 以便 Hook 超时时请求被取消
      signal
    });
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") {
      console.log("Notification cancelled");
    } else {
      console.error("Failed to send notification:", error);
    }
  }

  // 返回空对象。Notification Hooks 不修改 Agent 行为
  return {};
};

// 为 Notification 事件注册 Hook（不需要 matcher）
for await (const message of query({
  prompt: "Analyze this codebase",
  options: {
    hooks: {
      Notification: [{ hooks: [notificationHandler] }]
    }
  }
})) {
  console.log(message);
}
```

## 常见问题排查

### Hook 未触发

* 确认 Hook 事件名称正确且区分大小写（`PreToolUse`，不是 `preToolUse`）
* 检查 matcher 模式是否精确匹配工具名称
* 确保 Hook 在 `options.hooks` 中的正确事件类型下
* 对于支持 matcher 的非工具 Hooks（如 `Notification` 和 `SubagentStop`），matcher 匹配不同的字段，`Stop` 完全忽略 matcher（见 [matcher patterns](https://code.claude.com/docs/en/hooks#matcher-patterns)）
* 当 Agent 达到 [`max_turns`](https://code.claude.com/docs/en/agent-sdk/python#claudeagentoptions) 限制时，Hooks 可能不会触发，因为会话在 Hooks 执行之前就结束了

### Matcher 过滤不符合预期

**Matcher 只匹配工具名称，不匹配文件路径或其他参数。** 要按文件路径过滤，在 Hook 内部检查 `tool_input.file_path`：

```typescript
const myHook: HookCallback = async (input, toolUseID, { signal }) => {
  const preInput = input as PreToolUseHookInput;
  const toolInput = preInput.tool_input as Record<string, unknown>;
  const filePath = toolInput?.file_path as string;
  if (!filePath?.endsWith(".md")) return {}; // 跳过非 markdown 文件
  // 处理 markdown 文件...
  return {};
};
```

### Hook 超时

* 增加 `HookMatcher` 配置中的 `timeout` 值
* 在 TypeScript 中使用第三个回调参数的 `AbortSignal` 来优雅地处理取消

### 工具被意外阻止

* 检查所有 `PreToolUse` Hooks 中是否有 `permissionDecision: 'deny'` 的返回
* 在 Hooks 中添加日志以查看返回的 `permissionDecisionReason`
* 验证 matcher 模式不会过于宽泛：空 matcher 匹配所有工具

### 修改的输入未生效

* 确保 `updatedInput` 在 `hookSpecificOutput` 内部，不是在顶层：

```typescript
return {
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    permissionDecision: "allow",
    updatedInput: { command: "new command" }
  }
};
```

* 返回 `permissionDecision: 'allow'` 来自动批准修改后的输入，或 `'ask'` 来让用户确认
* 在 `hookSpecificOutput` 中包含 `hookEventName` 以标识输出对应的 Hook 类型

### Python 中不可用的会话 Hooks

**`SessionStart` 和 `SessionEnd` 在 TypeScript 中可以注册为 SDK 回调 Hooks，但在 Python SDK 中不可用**，因为其 `HookEvent` 类型不包含它们。在 Python 中，它们仅作为设置文件（如 `.claude/settings.json`）中定义的 [shell 命令 Hooks](https://code.claude.com/docs/en/hooks#hook-events) 可用。要从 SDK 应用加载 shell 命令 Hooks，在 [`setting_sources`](https://code.claude.com/docs/en/agent-sdk/python#settingsource) 或 [`settingSources`](https://code.claude.com/docs/en/agent-sdk/typescript#settingsource) 中包含适当的设置源：

```python
options = ClaudeAgentOptions(
    setting_sources=["project"],  # 加载 .claude/settings.json 包括 Hooks
)
```

```typescript
const options = {
  settingSources: ["project"] // 加载 .claude/settings.json 包括 Hooks
};
```

要在 Python SDK 中用回调运行初始化逻辑，使用 `client.receive_response()` 的第一条消息作为触发器。

### 子 Agent 权限提示倍增

**当生成多个子 Agent 时，每个子 Agent 可能分别请求权限。** 子 Agent 不会自动继承父 Agent 的权限。要避免重复提示，使用 `PreToolUse` Hooks 自动批准特定工具，或配置适用于子 Agent 会话的权限规则。

### 子 Agent 的递归 Hook 循环

**生成子 Agent 的 `UserPromptSubmit` Hook 可能会创建无限循环**，如果那些子 Agent 触发同一个 Hook。要防止这种情况：

* 在生成前检查 Hook 输入中的子 Agent 标识
* 使用共享变量或会话状态跟踪是否已在子 Agent 内部
* 将 Hooks 的作用域限定为仅在顶层 Agent 会话中运行

### systemMessage 未出现在输出中

**`systemMessage` 字段向用户显示消息，不是向模型。** 默认情况下 SDK 不在消息流中展示 Hook 输出，所以除非设置 `includeHookEvents`（Python 中为 `include_hook_events`），消息可能不会出现。要向模型传递上下文，请返回 [`additionalContext`](https://code.claude.com/docs/en/hooks#add-context-for-claude)。

如果需要可靠地向应用展示 Hook 决策，单独记录它们或使用专用输出通道。

## 相关资源

* [Claude Code hooks 参考](https://code.claude.com/docs/en/hooks)：完整的 JSON 输入/输出 schema、事件文档和 matcher 模式
* [Claude Code hooks 指南](https://code.claude.com/docs/en/hooks-guide)：shell 命令 Hook 示例和教程
* [TypeScript SDK 参考](https://code.claude.com/docs/en/agent-sdk/typescript)：Hook 类型、输入/输出定义和配置选项
* [Python SDK 参考](https://code.claude.com/docs/en/agent-sdk/python)：Hook 类型、输入/输出定义和配置选项
* [权限配置](https://code.claude.com/docs/en/agent-sdk/permissions)：控制 Agent 能做什么
* [自定义工具](https://code.claude.com/docs/en/agent-sdk/custom-tools)：构建工具来扩展 Agent 能力
