---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
category: translation
tags: [claude-code, agent-sdk, translation]
description: Claude Agent SDK 的权限配置详解，介绍如何通过权限模式、Hooks 和声明式允许/拒绝规则来控制 Agent 使用工具的方式。
refs:
  - https://code.claude.com/docs/en/agent-sdk/permissions
  - en-source/agent-sdk/permissions.md
title: 【译】Agent SDK - 权限配置
---

# 【译】SDK 权限配置

> 通过权限模式、Hooks 和声明式允许/拒绝规则控制 Agent 使用工具的方式

**Claude Agent SDK 提供权限控制来管理 Claude 如何使用工具。** 使用权限模式和规则定义什么是自动允许的，使用 [`canUseTool` 回调](https://code.claude.com/docs/en/agent-sdk/user-input) 在运行时处理其他情况。

> 本页涵盖权限模式和规则。要构建交互式审批流程（用户在运行时批准或拒绝工具请求），请参阅[处理审批和用户输入](https://code.claude.com/docs/en/agent-sdk/user-input)。

## 权限评估流程

**当 Claude 请求使用工具时，SDK 按以下顺序检查权限：**

| 步骤 | 名称 | 行为 |
| :--- | :--- | :--- |
| 1 | **Hooks** | 首先运行 [Hooks](https://code.claude.com/docs/en/agent-sdk/hooks)。Hook 可以直接拒绝调用或放行。Hook 返回 `allow` 不会跳过下面的 deny 和 ask 规则；这些规则无论 Hook 结果如何都会被评估。 |
| 2 | **Deny 规则** | 检查 `deny` 规则（来自 `disallowed_tools` 和 [settings.json](https://code.claude.com/docs/en/settings#permission-settings)）。如果 deny 规则匹配，工具被阻止——即使在 `bypassPermissions` 模式下也是如此。裸名称 deny 规则（如 `Bash`）在此评估开始前就从 Claude 的上下文中移除了工具，所以此步骤只检查带作用域的规则（如 `Bash(rm *)`）。 |
| 3 | **Ask 规则** | 检查来自 [settings.json](https://code.claude.com/docs/en/settings#permission-settings) 的 `ask` 规则。如果 ask 规则匹配，调用会落入你的 [`canUseTool` 回调](https://code.claude.com/docs/en/agent-sdk/user-input)进行确认——即使在 `bypassPermissions` 模式下也是如此。需要用户交互的工具行为相同：`AskUserQuestion` 和服务器设置了 [`_meta["anthropic/requiresUserInteraction"]`](https://code.claude.com/docs/en/mcp#require-approval-for-a-specific-tool) 的 MCP 工具始终落入回调，即使有 allow 规则匹配。在 `dontAsk` 模式下这两种情况都会被拒绝，因为该模式永远不提示。 |
| 4 | **权限模式** | 应用当前的[权限模式](#权限模式)。`bypassPermissions` 批准到达此步骤的所有内容。`acceptEdits` 批准文件操作。`plan` 将文件编辑和 shell 写入工具路由到你的 `canUseTool` 回调，无视 allow 规则，使写操作在规划时无法被自动批准。其他模式继续向下。 |
| 5 | **Allow 规则** | 检查 `allow` 规则（来自 `allowed_tools` 和 settings.json）。如果规则匹配，工具被批准。 |
| 6 | **canUseTool 回调** | 如果以上都未解决，调用你的 [`canUseTool` 回调](https://code.claude.com/docs/en/agent-sdk/user-input)进行决策。在 `dontAsk` 模式下，此步骤被跳过，工具被拒绝。 |

自 v2.1.198 起，如果你传入了此评估顺序永远无法到达的 `canUseTool` 回调，TypeScript SDK 会在构造查询时发出一次 Node.js 进程警告。警告代码为 `CLAUDE_SDK_CAN_USE_TOOL_SHADOWED`。两种配置会触发它：

* `permissionMode: 'bypassPermissions'` — 自动批准到达权限模式步骤的每个调用
* 每个裸 `allowedTools` 条目（如 `"Read"`）— 在回调被咨询之前自动批准整个工具

带限定符的条目（如 `Bash(ls *)`）和 `acceptEdits` 模式不会触发。来自设置文件的 allow 规则对检查不可见。

通过 `process.on('warning', ...)` 监听并匹配代码来记录或抑制。要对每个工具调用都进行检查（无视模式和规则），使用 [`PreToolUse` Hook](https://code.claude.com/docs/en/agent-sdk/hooks)。

本页重点介绍**允许和拒绝规则**以及**权限模式**。其他步骤：

* **Hooks：** 运行自定义代码来允许、拒绝或修改工具请求。见[使用 Hooks 控制执行](https://code.claude.com/docs/en/agent-sdk/hooks)。
* **canUseTool 回调：** 当没有更早的步骤解决调用时提示用户审批。见[处理审批和用户输入](https://code.claude.com/docs/en/agent-sdk/user-input)。

## 允许和拒绝规则

**`allowed_tools` 和 `disallowed_tools`（TypeScript 中为 `allowedTools` / `disallowedTools`）向评估流程中的 allow 和 deny 规则列表添加条目。** Allow 规则只影响审批：未列在 `allowed_tools` 中的工具仍可供 Claude 使用，会落入权限模式。Deny 规则的行为取决于是命名工具还是限定工具内的模式。

| 选项 | 效果 |
| :--- | :--- |
| `allowed_tools=["Read", "Grep"]` | `Read` 和 `Grep` 被自动批准。未列出的工具仍然存在，落入权限模式和 `canUseTool`。 |
| `disallowed_tools=["Bash"]` | `Bash` 工具定义从请求中移除。Claude 看不到该工具，无法尝试使用它。 |
| `disallowed_tools=["Bash(rm *)"]` | `Bash` 保持可用。匹配 `rm *` 的调用在所有权限模式下（包括 `bypassPermissions`）都被拒绝。其他 `Bash` 调用落入权限模式。 |
| `disallowed_tools=["*"]` | 所有工具定义从请求中移除。Deny 规则支持工具名称通配符：`"*"` 匹配所有工具，`"mcp__*"` 匹配所有服务器的所有 MCP 工具。 |

Allow 规则仅在字面 `mcp__<server>__` 前缀后接受工具名称通配符。服务器段必须无通配符，以便规则命名你配置的特定服务器：`mcp__puppeteer__*` 匹配 `puppeteer` 服务器的所有工具，`mcp__github__get_*` 匹配其 `get_` 工具。未锚定的条目（如 `allowed_tools=["*"]` 或 `allowed_tools=["mcp__*"]`）会在启动时产生警告被忽略，不会自动批准任何内容。

> **自动批准的工具永远不会到达 `canUseTool`。** 在任何更早步骤被批准的工具调用（通过 `acceptEdits`、`bypassPermissions` 或 allow 规则）会跳过你的 `canUseTool` 回调，因此你放在那里的权限检查对该工具会被静默绕过。例外是需要用户交互的工具：`AskUserQuestion` 和标记了 [`_meta["anthropic/requiresUserInteraction"]`](https://code.claude.com/docs/en/mcp#require-approval-for-a-specific-tool) 的 MCP 工具，即使有 allow 规则匹配也会到达回调。覆盖范围取决于条目形式：裸名称（如 `Read` 或 `mcp__github__get_issue`）自动批准该工具的每个调用，而带作用域的规则（如 `Bash(ls *)`）仅自动批准匹配的调用，其他 `Bash` 调用仍落入回调。对于必须在每个工具调用上运行的检查，使用 [`PreToolUse` Hook](https://code.claude.com/docs/en/agent-sdk/hooks)：Hooks 在所有其他步骤之前运行，Hook deny 即使在 `bypassPermissions` 模式下也生效。

对于锁定的 Agent，将 `allowedTools` 与 `permissionMode: "dontAsk"` 配对。列出的工具被批准；其他一切直接被拒绝而不提示：

```typescript
const options = {
  allowedTools: ["Read", "Glob", "Grep"],
  permissionMode: "dontAsk"
};
```

> **`allowed_tools` 不限制 `bypassPermissions`。** `allowed_tools` 只预批准你列出的工具。未列出的工具不被任何 allow 规则匹配，落入权限模式，`bypassPermissions` 会批准它们。设置 `allowed_tools=["Read"]` 同时使用 `permission_mode="bypassPermissions"` 仍然批准所有工具，包括 `Bash`、`Write` 和 `Edit`。如果你需要 `bypassPermissions` 但想阻止特定工具，使用 `disallowed_tools`。

你也可以在 `.claude/settings.json` 中声明式配置 allow、deny 和 ask 规则。当 `project` 设置源启用时这些规则会被读取（默认 `query()` 选项中已启用）。如果你显式设置了 `setting_sources`（TypeScript 中为 `settingSources`），需包含 `"project"` 才能应用。规则语法见[权限设置](https://code.claude.com/docs/en/settings#permission-settings)。

## 权限模式

**权限模式提供对 Claude 使用工具方式的全局控制。** 你可以在调用 `query()` 时设置权限模式，也可以在流式会话期间动态更改。

### 可用模式

| 模式 | 说明 | 工具行为 |
| :--- | :--- | :--- |
| `default` | 标准权限行为 | 无自动批准；未匹配的工具触发你的 `canUseTool` 回调 |
| `dontAsk` | 拒绝而非提示 | `allowed_tools` 或规则未预批准的一切都被拒绝；`canUseTool` 永远不会被调用 |
| `acceptEdits` | 自动接受文件编辑 | 文件编辑和[文件系统操作](#accept-edits-模式-acceptedits)（`mkdir`、`rm`、`mv` 等）自动批准 |
| `bypassPermissions` | 绕过权限检查 | 工具运行无需权限提示，除非显式 [`ask` 规则](#权限评估流程)匹配（谨慎使用） |
| `plan` | 规划模式 | Claude 探索和规划但不编辑源文件；文件编辑永远不会被自动批准，通过 `canUseTool` 回调提示 |
| `auto` | 模型分类审批 | 模型分类器批准或拒绝每个工具调用。可用性见 [Auto 模式](https://code.claude.com/docs/en/permission-modes#eliminate-prompts-with-auto-mode) |

> **子 Agent 继承：** 当父级使用 `bypassPermissions`、`acceptEdits` 或 `auto` 时，所有子 Agent 继承该模式且不能按子 Agent 覆盖。子 Agent 可能有不同的系统提示和较少约束的行为，因此继承 `bypassPermissions` 赋予它们完全的自主系统访问权限。显式 [`ask` 规则](#权限评估流程)仍会强制提示。

### 设置权限模式

**你可以在启动查询时设置一次权限模式，也可以在会话活跃时动态更改。**

#### 在查询时设置

创建查询时传入 `permission_mode`（Python）或 `permissionMode`（TypeScript）。此模式在整个会话期间生效，除非动态更改。

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    async for message in query(
        prompt="Help me refactor this code",
        options=ClaudeAgentOptions(
            permission_mode="default",  # 在这里设置模式
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)


asyncio.run(main())
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

async function main() {
  for await (const message of query({
    prompt: "Help me refactor this code",
    options: {
      permissionMode: "default" // 在这里设置模式
    }
  })) {
    if ("result" in message) {
      console.log(message.result);
    }
  }
}

main();
```

#### 在流式过程中动态更改

**调用 `set_permission_mode()`（Python）或 `setPermissionMode()`（TypeScript）来中途更改模式。** 新模式立即对所有后续工具请求生效。这让你可以先限制性地开始，在信任建立后放宽权限——例如在审查 Claude 的初始方案后切换到 `acceptEdits`。

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions


async def main():
    async with ClaudeSDKClient(
        options=ClaudeAgentOptions(
            permission_mode="default",  # 以 default 模式开始
        )
    ) as client:
        await client.query("Help me refactor this code")

        # 在会话中途动态更改模式
        await client.set_permission_mode("acceptEdits")

        # 使用新权限模式处理消息
        async for message in client.receive_response():
            if hasattr(message, "result"):
                print(message.result)


asyncio.run(main())
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

async function main() {
  const q = query({
    prompt: "Help me refactor this code",
    options: {
      permissionMode: "default" // 以 default 模式开始
    }
  });

  // 在会话中途动态更改模式
  await q.setPermissionMode("acceptEdits");

  // 使用新权限模式处理消息
  for await (const message of q) {
    if ("result" in message) {
      console.log(message.result);
    }
  }
}

main();
```

### 模式详解

#### Accept Edits 模式（`acceptEdits`）

**自动批准文件操作，使 Claude 可以无需提示即可编辑代码。** 其他工具（如非文件系统操作的 Bash 命令）仍需正常权限。

自动批准的操作：

* 文件编辑（Edit、Write 工具）
* 文件系统命令：`mkdir`、`touch`、`rm`、`rmdir`、`mv`、`cp`、`sed`

两者都仅适用于工作目录或 `additionalDirectories` 内的路径。作用域外的路径和受保护路径的写入仍会提示。

**适用场景：** 你信任 Claude 的编辑并希望更快迭代，例如原型开发或在隔离目录中工作时。

#### Don't Ask 模式（`dontAsk`）

**将任何权限提示转为拒绝。** 通过 `allowed_tools`、`settings.json` allow 规则或 Hook 预批准的工具正常运行。其他一切被拒绝，不调用 `canUseTool`。

**适用场景：** 你希望为无头 Agent 设定固定、显式的工具面，偏好硬拒绝而非依赖 `canUseTool` 缺失的静默行为。

#### Bypass Permissions 模式（`bypassPermissions`）

**自动批准所有工具使用，无需提示。** Hooks 仍会执行，必要时可以阻止操作。

> 使用时需极度谨慎。在此模式下 Claude 拥有完全的系统访问权限。仅在你信任所有可能操作的受控环境中使用。
>
> `allowed_tools` 不限制此模式。所有工具都被批准，不只是你列出的。Deny 规则（`disallowed_tools`）、显式 `ask` 规则和 Hooks 在模式检查之前评估，仍然可以阻止工具。

#### Plan 模式（`plan`）

**Claude 探索代码库并产出计划，但不编辑源文件。** 只读工具以默认模式运行。文件编辑在 plan 模式下永远不会被自动批准——即使有 allow 规则匹配——它们通过 `canUseTool` 回调提示。Claude 可能使用 `AskUserQuestion` 在最终确定计划前澄清需求。处理这些提示见[处理审批和用户输入](https://code.claude.com/docs/en/agent-sdk/user-input#handle-clarifying-questions)。

**适用场景：** 你希望 Claude 提出更改建议而不执行，例如代码审查或需要在执行前审批更改时。

## 相关资源

权限评估流程中的其他步骤：

* [处理审批和用户输入](https://code.claude.com/docs/en/agent-sdk/user-input)：交互式审批提示和澄清问题
* [Hooks 指南](https://code.claude.com/docs/en/agent-sdk/hooks)：在 Agent 生命周期的关键节点运行自定义代码
* [权限规则](https://code.claude.com/docs/en/settings#permission-settings)：`settings.json` 中的声明式允许/拒绝规则
