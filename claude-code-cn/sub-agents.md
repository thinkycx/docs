---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】子代理
description: Claude Code 子代理系统详解：内置子代理（Explore/Plan/General-purpose）、自定义创建与配置（/agents 命令和文件方式）、作用域优先级、工具权限控制、模型选择、持久记忆、前后台执行、以及完整示例集。
category: translation
tags: [claude-code, sub-agents, translation]
refs:
  - https://code.claude.com/docs/en/sub-agents.md
---

# 创建自定义子代理

> 在 Claude Code 中创建和使用专门的 AI 子代理，实现面向特定任务的工作流和更高效的上下文管理。

**子代理是处理特定类型任务的专门 AI 助手。** 当某个附属任务会让主对话充斥大量搜索结果、日志或不再引用的文件内容时，就该使用子代理：子代理在自己的上下文中完成工作，只返回摘要。当你反复以相同指令创建同类工作者时，就该定义一个自定义子代理。

**每个子代理都运行在独立的上下文窗口中**，拥有自定义系统提示词、特定的工具访问权限和独立的权限设置。当 Claude 遇到与某个子代理描述匹配的任务时，会将任务委派给该子代理，子代理独立工作并返回结果。要直观了解上下文节省效果，可参阅[上下文窗口可视化](https://code.claude.com/docs/en/context-window)，其中演示了一个子代理在独立窗口中处理研究任务的会话。

> **注意**
> 子代理在单个会话内工作。如需并行运行多个独立会话并在一处监控，请参阅[后台代理](https://code.claude.com/docs/en/agent-view)。如需会话间相互通信，请参阅[代理团队](https://code.claude.com/docs/en/agent-teams)。

子代理能帮你：

* **保护上下文** — 将探索和实现过程隔离在主对话之外
* **施加约束** — 限制子代理可使用的工具
* **跨项目复用配置** — 通过用户级子代理在所有项目中复用
* **专精行为** — 用聚焦的系统提示词覆盖特定领域
* **控制成本** — 将任务路由到更快、更便宜的模型（如 Haiku）

**Claude 根据每个子代理的描述来决定何时委派任务。** 创建子代理时，请写一段清晰的描述，让 Claude 知道何时该使用它。

Claude Code 内置了多个子代理，如 **Explore**、**Plan** 和 **general-purpose**。你也可以创建自定义子代理来处理特定任务。

## 内置子代理

**Claude Code 包含多个内置子代理，Claude 会在适当时自动使用它们。** 每个子代理继承父对话的权限，并附加额外的工具限制。

Explore 和 Plan 跳过 CLAUDE.md 文件和父会话的 git status，以保持研究的快速和低成本。其他所有内置子代理和[自定义子代理](#configure-subagents)都会加载这两者。完整的启动加载清单详见 [what loads at startup](#what-loads-at-startup)。

### Explore

**快速的只读代理，专为搜索和分析代码库优化。**

| 属性 | 说明 |
| :--- | :--- |
| 模型 | Haiku，快速低延迟 |
| 工具 | 只读工具；禁止 Write 和 Edit |
| 用途 | 文件发现、代码搜索、代码库探索 |

当 Claude 需要搜索或理解代码库但不做修改时，会委派给 Explore。这让探索结果不会占用主对话的上下文。

调用 Explore 时，Claude 会指定一个彻底程度：**quick** 用于定向查找，**medium** 用于均衡探索，**very thorough** 用于全面分析。

### Plan

**研究代理，在[计划模式](https://code.claude.com/docs/en/permission-modes#analyze-before-you-edit-with-plan-mode)中用于在呈现计划前收集上下文。**

| 属性 | 说明 |
| :--- | :--- |
| 模型 | 继承主对话的模型 |
| 工具 | 只读工具；禁止 Write 和 Edit |
| 用途 | 为规划收集代码库信息 |

当你处于计划模式且 Claude 需要理解代码库时，它会将研究委派给 Plan 子代理，这样探索输出保留在独立的上下文窗口中，主对话仍保持只读。

### General-purpose

**通用代理，适用于需要探索和操作的复杂多步任务。**

| 属性 | 说明 |
| :--- | :--- |
| 模型 | 继承主对话的模型 |
| 工具 | 所有工具 |
| 用途 | 复杂研究、多步操作、代码修改 |

当任务同时需要探索和修改、需要复杂推理来解读结果、或有多个相互依赖的步骤时，Claude 会委派给 general-purpose。

### 其他

**Claude Code 还包含用于特定任务的辅助代理。** 它们通常自动调用，无需手动使用。

| 代理 | 模型 | Claude 何时使用 |
| :--- | :--- | :--- |
| statusline-setup | Sonnet | 当你运行 `/statusline` 配置状态栏时 |
| claude-code-guide | Haiku | 当你询问 Claude Code 功能相关问题时 |

### 限制内置子代理

**内置子代理在交互会话中始终注册。** 限制方式如下：

* 要阻止特定内置类型，将其添加到 `permissions.deny`，如[禁用特定子代理](#disable-specific-subagents)所示。
* 要阻止 Claude 委派给任何子代理，使用 [`permissions.deny`](https://code.claude.com/docs/en/permissions#tool-specific-permission-rules) 禁止 `Agent` 工具本身。
* 在[非交互模式](https://code.claude.com/docs/en/headless)和 [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) 中，设置 [`CLAUDE_AGENT_SDK_DISABLE_BUILTIN_AGENTS=1`](https://code.claude.com/docs/en/env-vars) 可移除所有内置类型，仅保留你自己定义的子代理。

除了这些内置子代理，你还可以创建带有自定义提示词、工具限制、权限模式、钩子和技能的自定义子代理。以下章节介绍如何开始配置子代理。

## 快速开始：创建你的第一个子代理

**子代理用带有 YAML frontmatter 的 Markdown 文件定义。** 你可以[手动创建](#write-subagent-files)或使用 `/agents` 命令。

本教程指导你使用 `/agents` 命令创建一个用户级子代理。该子代理会审查代码并为代码库提出改进建议。

### 步骤 1：打开子代理界面

在 Claude Code 中运行：

```text theme={null}
/agents
```

### 步骤 2：选择位置

切换到 **Library** 标签页，选择 **Create new agent**，然后选择 **Personal**。这会将子代理保存到 `~/.claude/agents/`，使其在所有项目中可用。

### 步骤 3：用 Claude 生成

选择 **Generate with Claude**。当提示输入时，描述子代理：

```text theme={null}
A code improvement agent that scans files and suggests improvements
for readability, performance, and best practices. It should explain
each issue, show the current code, and provide an improved version.
```

Claude 会为你生成标识符、描述和系统提示词。

### 步骤 4：选择工具

对于只读审查者，取消勾选所有选项，只保留 **Read-only tools**。如果保留所有工具选中，子代理将继承主对话中所有可用工具。

### 步骤 5：选择模型

选择子代理使用的模型。对于此示例代理，选择 **Sonnet**，它在分析代码模式时兼顾能力和速度。

### 步骤 6：选择颜色

为子代理选择一个背景颜色。这有助于你在 UI 中识别正在运行的子代理。

### 步骤 7：配置记忆

选择 **User scope** 为子代理提供一个位于 `~/.claude/agent-memory/` 的[持久记忆目录](#enable-persistent-memory)。子代理利用它来跨对话积累洞察，例如代码库模式和重复出现的问题。如果不希望子代理持久化学习成果，请选择 **None**。

### 步骤 8：保存并试用

检查配置摘要。按 `s` 或 `Enter` 保存，或按 `e` 保存并在编辑器中打开文件。子代理立即可用。试试看：

```text theme={null}
Use the code-improver agent to suggest improvements in this project
```

Claude 会委派给你的新子代理，子代理扫描代码库并返回改进建议。

**至此你拥有了一个可在任何项目中使用的子代理**，用于分析代码库和提出改进建议。

你也可以手动创建 Markdown 文件形式的子代理、通过 CLI 标志定义，或通过插件分发。以下章节涵盖所有配置选项。

## 配置子代理

### 使用 /agents 命令

**`/agents` 命令打开一个标签式界面来管理子代理。** **Running** 标签页列出活跃和最近完成的子代理，允许你打开或停止它们。**Library** 标签页允许你：

* 查看所有可用子代理（内置、用户、项目和插件）
* 通过引导设置或 Claude 生成来创建新子代理
* 编辑现有子代理的配置和工具访问权限
* 删除自定义子代理
* 查看存在重名时哪个子代理处于活跃状态

这是创建和管理子代理的推荐方式。如需手动创建或自动化，也可以直接添加子代理文件。

### 选择子代理的作用域

**子代理是带有 YAML frontmatter 的 Markdown 文件。** 根据作用域将它们存放在不同位置。当多个子代理同名时，Claude Code 使用更高优先级位置的那个。

| 位置 | 作用域 | 优先级 | 创建方式 |
| :--- | :--- | :--- | :--- |
| 托管设置 | 组织范围 | 1（最高） | 通过[托管设置](https://code.claude.com/docs/en/settings)部署 |
| `--agents` CLI 标志 | 当前会话 | 2 | 启动 Claude Code 时传入 JSON |
| `.claude/agents/` | 当前项目 | 3 | 交互式或手动 |
| `~/.claude/agents/` | 所有项目 | 4 | 交互式或手动 |
| 插件的 `agents/` 目录 | 启用插件的地方 | 5（最低） | 随[插件](https://code.claude.com/docs/en/plugins)安装 |

**项目子代理**（`.claude/agents/`）适用于特定代码库的子代理。将它们提交到版本控制，让团队协作使用和改进。

项目子代理通过从当前工作目录向上遍历来发现，因此当前目录到仓库根之间的每个 `.claude/agents/` 都会被扫描。自 v2.1.178 起，当多个嵌套目录定义了相同的 `name` 时，Claude Code 使用最靠近工作目录的定义。

通过 `--add-dir` 添加的目录也会被扫描：附加目录中的 `.claude/agents/` 文件夹与项目子代理一起加载。关于 `--add-dir` 加载哪些其他配置类型，请参阅 [Additional directories](https://code.claude.com/docs/en/permissions#additional-directories-grant-file-access-not-configuration)。要在不使用 `--add-dir` 的情况下跨项目共享子代理，请使用 `~/.claude/agents/` 或[插件](https://code.claude.com/docs/en/plugins)。

**用户子代理**（`~/.claude/agents/`）是在所有项目中可用的个人子代理。

Claude Code 会递归扫描 `.claude/agents/` 和 `~/.claude/agents/`，因此你可以将定义组织到子文件夹中，如 `agents/review/` 或 `agents/research/`。子目录路径不影响子代理的标识或调用方式，因为身份仅来自 `name` frontmatter 字段。在同一作用域内保持 `name` 值唯一：如果同一作用域内两个文件声明了相同的名称，Claude Code 会保留一个并丢弃另一个，且不会发出警告。

插件 `agents/` 目录也会被递归扫描。与项目和用户作用域不同，插件 `agents/` 目录内的子文件夹会成为[作用域标识符](#invoke-subagents-explicitly)的一部分：插件 `my-plugin` 中 `agents/review/security.md` 文件注册为 `my-plugin:review:security`。

**CLI 定义的子代理**在启动 Claude Code 时通过 JSON 传入。它们仅存在于当前会话，不会保存到磁盘，适合快速测试或自动化脚本。你可以在单个 `--agents` 调用中定义多个子代理：

macOS、Linux、WSL：

```bash theme={null}
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer. Use proactively after code changes.",
    "prompt": "You are a senior code reviewer. Focus on code quality, security, and best practices.",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  },
  "debugger": {
    "description": "Debugging specialist for errors and test failures.",
    "prompt": "You are an expert debugger. Analyze errors, identify root causes, and provide fixes."
  }
}'
```

Windows PowerShell：

```powershell theme={null}
claude --agents @'
{
  "code-reviewer": {
    "description": "Expert code reviewer. Use proactively after code changes.",
    "prompt": "You are a senior code reviewer. Focus on code quality, security, and best practices.",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  },
  "debugger": {
    "description": "Debugging specialist for errors and test failures.",
    "prompt": "You are an expert debugger. Analyze errors, identify root causes, and provide fixes."
  }
}
'@
```

`--agents` 标志接受的 JSON 与文件形式子代理使用相同的 [frontmatter](#supported-frontmatter-fields) 字段：`description`、`prompt`、`tools`、`disallowedTools`、`model`、`permissionMode`、`mcpServers`、`hooks`、`maxTurns`、`skills`、`initialPrompt`、`memory`、`effort`、`background`、`isolation` 和 `color`。其中 `prompt` 对应文件形式中 markdown 正文部分的系统提示词。

**托管子代理**由组织管理员部署。将 Markdown 文件放在[托管设置目录](https://code.claude.com/docs/en/settings#settings-files)中的 `.claude/agents/` 下，使用与项目和用户子代理相同的 frontmatter 格式。托管定义优先于同名的项目和用户子代理。

**插件子代理**来自你安装的[插件](https://code.claude.com/docs/en/plugins)。它们与你的自定义子代理一起显示在 `/agents` 中。关于创建插件子代理的详情，请参阅[插件组件参考](https://code.claude.com/docs/en/plugins-reference#agents)。

> **注意**
> 出于安全考虑，插件子代理不支持 `hooks`、`mcpServers` 或 `permissionMode` frontmatter 字段。从插件加载代理时这些字段会被忽略。如果需要它们，请将代理文件复制到 `.claude/agents/` 或 `~/.claude/agents/`。你也可以在 `settings.json` 或 `settings.local.json` 的 [`permissions.allow`](https://code.claude.com/docs/en/settings#permission-settings) 中添加规则，但这些规则适用于整个会话，而不仅是该插件子代理。

任何作用域的子代理定义也可用于[代理团队](https://code.claude.com/docs/en/agent-teams#use-subagent-definitions-for-teammates)：生成队友时，你可以引用子代理类型，队友会使用其 `tools` 和 `model`，定义的正文作为附加指令追加到队友的系统提示词中。关于哪些 frontmatter 字段适用，请参阅[代理团队](https://code.claude.com/docs/en/agent-teams#use-subagent-definitions-for-teammates)。

### 编写子代理文件

**子代理文件使用 YAML frontmatter 进行配置，后跟 Markdown 格式的系统提示词：**

> **注意**
> 子代理在会话启动时加载。如果你直接在磁盘上添加或编辑了子代理文件，需要重启会话才能加载。通过 `/agents` 界面创建的子代理则无需重启即可立即生效。

```markdown theme={null}
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Glob, Grep
model: sonnet
---

You are a code reviewer. When invoked, analyze the code and provide
specific, actionable feedback on quality, security, and best practices.
```

frontmatter 定义子代理的元数据和配置。正文成为引导子代理行为的系统提示词。子代理只接收这个系统提示词加上基本环境信息（如工作目录），而非完整的 Claude Code 系统提示词。

子代理启动时位于主对话的当前工作目录。在子代理内，`cd` 命令不会在 Bash 或 PowerShell 工具调用之间持久化，也不会影响主对话的工作目录。如需让子代理拥有仓库的隔离副本，请设置 [`isolation: worktree`](#supported-frontmatter-fields)。

#### 支持的 frontmatter 字段

以下字段可在 YAML frontmatter 中使用。只有 `name` 和 `description` 是必填的。

| 字段 | 必填 | 说明 |
| :--- | :--- | :--- |
| `name` | 是 | 唯一标识符，使用小写字母和连字符。[钩子](https://code.claude.com/docs/en/hooks#subagentstart)接收此值作为 `agent_type`。文件名不必匹配 |
| `description` | 是 | 描述 Claude 何时应委派给此子代理 |
| `tools` | 否 | 子代理可使用的[工具](#available-tools)。省略时继承所有工具。要将 Skill 预加载到上下文中，请使用 `skills` 字段而非在此列出 `Skill` |
| `disallowedTools` | 否 | 要禁止的工具，从继承或指定的列表中移除 |
| `model` | 否 | 使用的[模型](#choose-a-model)：`sonnet`、`opus`、`haiku`、`fable`、完整模型 ID（如 `claude-opus-4-8`）或 `inherit`。默认为 `inherit` |
| `permissionMode` | 否 | [权限模式](#permission-modes)：`default`、`acceptEdits`、`auto`、`dontAsk`、`bypassPermissions` 或 `plan`。[插件子代理](#choose-the-subagent-scope)会忽略此字段 |
| `maxTurns` | 否 | 子代理停止前的最大代理轮数 |
| `skills` | 否 | 在启动时预加载到子代理上下文中的[技能](https://code.claude.com/docs/en/skills)。注入的是完整的技能内容，不仅是描述。子代理仍可通过 Skill 工具调用未列出的项目、用户和插件技能 |
| `mcpServers` | 否 | 此子代理可用的 [MCP 服务器](https://code.claude.com/docs/en/mcp)。每个条目可以是引用已配置服务器的名称（如 `"slack"`），也可以是以服务器名为键、完整 [MCP 服务器配置](https://code.claude.com/docs/en/mcp#installing-mcp-servers)为值的内联定义。[插件子代理](#choose-the-subagent-scope)会忽略此字段 |
| `hooks` | 否 | 作用域限定于此子代理的[生命周期钩子](#define-hooks-for-subagents)。[插件子代理](#choose-the-subagent-scope)会忽略此字段 |
| `memory` | 否 | [持久记忆作用域](#enable-persistent-memory)：`user`、`project` 或 `local`。启用跨会话学习 |
| `background` | 否 | 设为 `true` 时此子代理始终作为[后台任务](#run-subagents-in-foreground-or-background)运行。默认：`false` |
| `effort` | 否 | 此子代理活跃时的推理投入等级。覆盖会话级别设置。默认：从会话继承。选项：`low`、`medium`、`high`、`xhigh`、`max`；可用等级取决于模型 |
| `isolation` | 否 | 设为 `worktree` 时在临时 [git worktree](https://code.claude.com/docs/en/worktrees) 中运行子代理，为其提供默认从[默认分支](https://code.claude.com/docs/en/worktrees#choose-the-base-branch)（而非父会话的 `HEAD`）分出的仓库隔离副本。如果子代理未做任何更改，worktree 会自动清理 |
| `color` | 否 | 子代理在任务列表和记录中的显示颜色。接受 `red`、`blue`、`green`、`yellow`、`purple`、`orange`、`pink` 或 `cyan` |
| `initialPrompt` | 否 | 当此代理作为主会话代理运行时（通过 `--agent` 或 `agent` 设置），作为第一个用户轮次自动提交。支持处理[命令](https://code.claude.com/docs/en/commands)和[技能](https://code.claude.com/docs/en/skills)。会前置到用户提供的提示词之前 |

### 选择模型

**`model` 字段控制子代理使用哪个 [AI 模型](https://code.claude.com/docs/en/model-config)：**

* **模型别名**：使用可用别名之一：`sonnet`、`opus`、`haiku` 或 `fable`
* **完整模型 ID**：使用完整模型 ID，如 `claude-opus-4-8` 或 `claude-sonnet-4-6`。接受与 `--model` 标志相同的值
* **inherit**：使用与主对话相同的模型
* **省略**：默认为 `inherit`，使用与主对话相同的模型

当 Claude 调用子代理时，也可以为该次调用传递 `model` 参数。Claude Code 按以下顺序解析子代理的模型：

1. [`CLAUDE_CODE_SUBAGENT_MODEL`](https://code.claude.com/docs/en/model-config#environment-variables) 环境变量（如已设置）
2. 每次调用的 `model` 参数
3. 子代理定义的 `model` frontmatter
4. 主对话的模型

环境变量、每次调用参数和 frontmatter 值会根据组织的 [`availableModels`](https://code.claude.com/docs/en/model-config#restrict-model-selection) 白名单进行检查。如果解析出的值对应一个被排除的模型，则不会使用该值，子代理将使用继承的模型。

### 控制子代理能力

你可以通过工具访问、权限模式和条件规则来控制子代理能做什么。

#### 可用工具

**子代理默认继承主对话中的[内置工具](https://code.claude.com/docs/en/tools-reference)和 MCP 工具。** 以下工具依赖主对话的 UI 或会话状态，即使在 `tools` 字段中列出也不可用于子代理：

* `AskUserQuestion`
* `EnterPlanMode`
* `ExitPlanMode`（除非子代理的 [`permissionMode`](#permission-modes) 为 `plan`）
* `ScheduleWakeup`
* `WaitForMcpServers`

要限制工具，使用 `tools` 字段（白名单）或 `disallowedTools` 字段（黑名单）。以下示例使用 `tools` 仅允许 Read、Grep、Glob 和 Bash。子代理无法编辑文件、写入文件或使用任何 MCP 工具：

```yaml theme={null}
---
name: safe-researcher
description: Research agent with restricted capabilities
tools: Read, Grep, Glob, Bash
---
```

以下示例使用 `disallowedTools` 继承主对话的所有工具，但排除 Write 和 Edit。子代理保留 Bash、MCP 工具和其他一切：

```yaml theme={null}
---
name: no-writes
description: Inherits every tool except file writes
disallowedTools: Write, Edit
---
```

如果同时设置了两者，先应用 `disallowedTools`，然后在剩余工具池中解析 `tools`。同时出现在两个列表中的工具会被移除。

两个字段都接受 MCP 服务器级别的模式，而不仅是精确的工具名称：`mcp__<server>` 或 `mcp__<server>__*` 授予或移除指定服务器的所有工具。在 `disallowedTools` 中，`mcp__*` 可移除任何服务器的所有 MCP 工具。以下示例移除 `github` MCP 服务器的所有工具，同时保留其他服务器的工具和所有内置工具：

```yaml theme={null}
---
name: local-only
description: Inherits every tool except those from the github MCP server
disallowedTools: mcp__github
---
```

#### 限制可生成的子代理

**当代理通过 `claude --agent` 作为主线程运行时，可以使用 Agent 工具生成子代理。** 要限制它可以生成的子代理类型，在 `tools` 字段中使用 `Agent(agent_type)` 语法。

> **注意** 在 v2.1.63 中，Task 工具已重命名为 Agent。设置和代理定义中现有的 `Task(...)` 引用仍作为别名有效。

```yaml theme={null}
---
name: coordinator
description: Coordinates work across specialized agents
tools: Agent(worker, researcher), Read, Bash
---
```

这是一个白名单：只有 `worker` 和 `researcher` 子代理可以被生成。如果代理尝试生成其他类型，请求会失败，代理在提示词中只能看到允许的类型。要阻止特定代理同时允许其他所有代理，请改用 [`permissions.deny`](#disable-specific-subagents)。

要允许生成任何子代理而不受限制，使用不带括号的 `Agent`：

```yaml theme={null}
tools: Agent, Read, Bash
```

如果 `tools` 列表中完全省略 `Agent`，则代理无法生成任何子代理。

`Agent(agent_type)` 白名单语法仅适用于通过 `claude --agent` 作为主线程运行的代理。在子代理定义中，在 `tools` 中列出 `Agent` 可以让该子代理[生成嵌套子代理](#spawn-nested-subagents)，但括号内的任何类型列表会被忽略。

#### 为子代理限定 MCP 服务器

**使用 `mcpServers` 字段让子代理访问主对话中不可用的 [MCP](https://code.claude.com/docs/en/mcp) 服务器。** 此处定义的内联服务器在子代理启动时连接，完成时断开。字符串引用则共享父会话的连接。

> **注意**
> `mcpServers` 字段在代理文件可以运行的两种场景中都适用：
>
> * 作为子代理，通过 Agent 工具或 @-mention 生成
> * 作为主会话，通过 [`--agent`](#invoke-subagents-explicitly) 或 `agent` 设置启动
>
> 当代理作为主会话时，内联服务器定义在启动时与 [`.mcp.json`](https://code.claude.com/docs/en/mcp) 和设置文件中的服务器一起连接。

列表中每个条目要么是内联服务器定义，要么是引用会话中已配置 MCP 服务器的字符串：

```yaml theme={null}
---
name: browser-tester
description: Tests features in a real browser using Playwright
mcpServers:
  # 内联定义：仅限此子代理使用
  - playwright:
      type: stdio
      command: npx
      args: ["-y", "@playwright/mcp@latest"]
  # 按名称引用：复用已配置的服务器
  - github
---

Use the Playwright tools to navigate, screenshot, and interact with pages.
```

内联定义使用与 `.mcp.json` 服务器条目相同的 schema（`stdio`、`http`、`sse`、`ws`），以服务器名称为键。

要让 MCP 服务器完全不出现在主对话中（避免其工具描述占用上下文），在此处内联定义即可。子代理获得这些工具，父对话则不受影响。

自 v2.1.153 起，适用于主会话的 MCP 限制也覆盖子代理 frontmatter 中声明的服务器：

* [`--strict-mcp-config`](https://code.claude.com/docs/en/cli-reference) 和 [`--bare`](https://code.claude.com/docs/en/cli-reference)
* [企业托管 MCP 配置](https://code.claude.com/docs/en/managed-mcp)
* [`allowedMcpServers` 和 `deniedMcpServers` 策略](https://code.claude.com/docs/en/managed-mcp#policy-based-control-with-allowlists-and-denylists)

当其中之一阻止了某个服务器时，Claude Code 会跳过它并显示警告，指出被阻止的服务器名称。

托管设置的限制适用于所有子代理，无论其如何定义。`--strict-mcp-config` 不会过滤通过 `--agents` 或 SDK `agents` 选项内联传入的服务器，因为这些是调用者的显式输入。

#### 权限模式

**`permissionMode` 字段控制子代理如何处理权限提示。** 子代理继承主对话的权限上下文，并可覆盖模式，但以下描述的情况除外（父模式优先时）。

| 模式 | 行为 |
| :--- | :--- |
| `default` | 标准权限检查，带提示 |
| `acceptEdits` | 自动接受工作目录或 `additionalDirectories` 中的文件编辑和常见文件系统命令 |
| `auto` | [自动模式](https://code.claude.com/docs/en/permission-modes#eliminate-prompts-with-auto-mode)：后台分类器审查命令和受保护目录的写入 |
| `dontAsk` | 自动拒绝权限提示（已显式允许的工具仍可使用） |
| `bypassPermissions` | 跳过权限提示 |
| `plan` | 计划模式（只读探索） |

> **警告**
> 谨慎使用 `bypassPermissions`。它跳过权限提示，允许子代理在无需批准的情况下执行操作，包括写入 `.git`、`.config/git`、`.claude`、`.vscode`、`.idea`、`.husky`、`.cargo`、`.devcontainer`、`.yarn` 和 `.mvn`。显式的 [`ask` 规则](https://code.claude.com/docs/en/permissions#manage-permissions)以及根目录和 home 目录的删除操作（如 `rm -rf /`）仍会提示。详见[权限模式](https://code.claude.com/docs/en/permission-modes#skip-all-checks-with-bypasspermissions-mode)。

如果父会话使用 `bypassPermissions` 或 `acceptEdits`，则父模式优先，不可被覆盖。如果父会话使用[自动模式](https://code.claude.com/docs/en/permission-modes#eliminate-prompts-with-auto-mode)，子代理继承自动模式，其 frontmatter 中的任何 `permissionMode` 会被忽略：分类器使用与父会话相同的阻止和允许规则来评估子代理的工具调用。

#### 向子代理预加载技能

**使用 `skills` 字段在启动时将技能内容注入子代理的上下文。** 这让子代理无需在执行过程中发现和加载技能即可获得领域知识。

```yaml theme={null}
---
name: api-developer
description: Implement API endpoints following team conventions
skills:
  - api-conventions
  - error-handling-patterns
---

Implement API endpoints. Follow the conventions and patterns from the preloaded skills.
```

每个列出的技能的完整内容在启动时注入子代理的上下文。此字段控制哪些技能被预加载，而非子代理可以访问哪些技能：即使不设置此字段，子代理仍可在执行过程中通过 Skill 工具发现和调用项目、用户和插件技能。要完全阻止子代理调用技能，从 [`tools`](#available-tools) 列表中省略 `Skill` 或将其添加到 `disallowedTools`。

你无法预加载设置了 [`disable-model-invocation: true`](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill) 的技能，因为预加载与 Claude 可调用的技能来自同一集合。如果列出的技能缺失或被禁用，Claude Code 会跳过它并在调试日志中记录警告。

> **注意**
> 这与[在子代理中运行技能](https://code.claude.com/docs/en/skills#run-skills-in-a-subagent)相反。在子代理中使用 `skills` 时，子代理控制系统提示词并加载技能内容。在技能中使用 `context: fork` 时，技能内容被注入你指定的代理。两者使用相同的底层系统。

#### 启用持久记忆

**`memory` 字段为子代理提供一个跨对话持久化的目录。** 子代理利用此目录随时间积累知识，如代码库模式、调试洞察和架构决策。

```yaml theme={null}
---
name: code-reviewer
description: Reviews code for quality and best practices
memory: user
---

You are a code reviewer. As you review code, update your agent memory with
patterns, conventions, and recurring issues you discover.
```

根据记忆应用的广度选择作用域：

| 作用域 | 位置 | 适用场景 |
| :--- | :--- | :--- |
| `user` | `~/.claude/agent-memory/<name-of-agent>/` | 子代理应在所有项目中记住学习成果 |
| `project` | `.claude/agent-memory/<name-of-agent>/` | 子代理的知识是项目特定的且可通过版本控制共享 |
| `local` | `.claude/agent-memory-local/<name-of-agent>/` | 子代理的知识是项目特定的但不应提交到版本控制 |

启用记忆后：

* 子代理的系统提示词包含读写记忆目录的指令。
* 子代理的系统提示词还包含记忆目录中 `MEMORY.md` 的前 200 行或 25KB（取较小者），以及在超出该限制时整理 `MEMORY.md` 的指令。
* Read、Write 和 Edit 工具自动启用，以便子代理管理其记忆文件。

##### 持久记忆技巧

* `project` 是推荐的默认作用域。它使子代理知识可通过版本控制共享。当子代理的知识广泛适用于多个项目时使用 `user`，当知识不应提交到版本控制时使用 `local`。
* 要求子代理在开始工作前查阅记忆："Review this PR, and check your memory for patterns you've seen before."
* 要求子代理在完成任务后更新记忆："Now that you're done, save what you learned to your memory." 随时间推移，这将构建一个知识库，使子代理越来越高效。
* 直接在子代理的 markdown 文件中包含记忆指令，让它主动维护自己的知识库：

  ```markdown theme={null}
  Update your agent memory as you discover codepaths, patterns, library
  locations, and key architectural decisions. This builds up institutional
  knowledge across conversations. Write concise notes about what you found
  and where.
  ```

#### 使用钩子实现条件规则

**对于更动态的工具使用控制，使用 `PreToolUse` 钩子在操作执行前进行验证。** 当你需要允许某工具的部分操作同时阻止其他操作时，这很有用。

以下示例创建一个仅允许只读数据库查询的子代理。`PreToolUse` 钩子在每个 Bash 命令执行前运行 `command` 中指定的脚本：

```yaml theme={null}
---
name: db-reader
description: Execute read-only database queries
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---
```

Claude Code 通过 stdin 向钩子命令[传递 JSON 格式的钩子输入](https://code.claude.com/docs/en/hooks#pretooluse-input)。验证脚本读取此 JSON，提取 Bash 命令，并[以退出码 2](https://code.claude.com/docs/en/hooks#exit-code-2-behavior-per-event) 阻止写操作：

```bash theme={null}
#!/bin/bash
# ./scripts/validate-readonly-query.sh

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Block SQL write operations (case-insensitive)
if echo "$COMMAND" | grep -iE '\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE)\b' > /dev/null; then
  echo "Blocked: Only SELECT queries are allowed" >&2
  exit 2
fi

exit 0
```

完整输入 schema 详见 [Hook input](https://code.claude.com/docs/en/hooks#pretooluse-input)，退出码对行为的影响详见 [exit codes](https://code.claude.com/docs/en/hooks#exit-code-output)。在 Windows 上，用 PowerShell 编写钩子脚本并在钩子条目中添加 `shell: powershell`，如[在 PowerShell 中运行钩子](https://code.claude.com/docs/en/hooks#windows-powershell-tool)所示。

#### 禁用特定子代理

**你可以通过将子代理添加到[设置](https://code.claude.com/docs/en/settings#permission-settings)中的 `deny` 数组来阻止 Claude 使用它们。** 使用格式 `Agent(subagent-name)`，其中 `subagent-name` 匹配子代理的 name 字段。

```json theme={null}
{
  "permissions": {
    "deny": ["Agent(Explore)", "Agent(my-custom-agent)"]
  }
}
```

这对内置和自定义子代理都有效。你也可以使用 `--disallowedTools` CLI 标志：

```bash theme={null}
claude --disallowedTools "Agent(Explore)"
```

更多权限规则详情请参阅[权限文档](https://code.claude.com/docs/en/permissions#tool-specific-permission-rules)。

### 为子代理定义钩子

**子代理可以定义在其生命周期内运行的[钩子](https://code.claude.com/docs/en/hooks)。** 配置钩子有两种方式：

* **在子代理的 frontmatter 中**：定义仅在该子代理活跃时运行的钩子
* **在 `settings.json` 中**：定义在主会话中子代理启动或停止时运行的钩子

#### frontmatter 中的钩子

直接在子代理的 Markdown 文件中定义钩子。这些钩子仅在该特定子代理活跃时运行，子代理完成时被清理。

> **注意**
> frontmatter 钩子在代理通过 Agent 工具或 @-mention 作为子代理生成时触发，也在代理通过 [`--agent`](#invoke-subagents-explicitly) 或 `agent` 设置作为主会话运行时触发。在主会话场景中，它们与 [`settings.json`](https://code.claude.com/docs/en/hooks) 中定义的钩子一同运行。

支持所有[钩子事件](https://code.claude.com/docs/en/hooks#hook-events)。子代理最常用的事件为：

| 事件 | 匹配器输入 | 触发时机 |
| :--- | :--- | :--- |
| `PreToolUse` | 工具名称 | 子代理使用工具之前 |
| `PostToolUse` | 工具名称 | 子代理使用工具之后 |
| `Stop` | （无） | 子代理完成时（运行时转换为 `SubagentStop`） |

以下示例用 `PreToolUse` 钩子验证 Bash 命令，用 `PostToolUse` 在文件编辑后运行 linter：

```yaml theme={null}
---
name: code-reviewer
description: Review code changes with automatic linting
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-command.sh $TOOL_INPUT"
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "./scripts/run-linter.sh"
---
```

当代理作为子代理被调用时，frontmatter 中的 `Stop` 钩子会自动转换为 `SubagentStop` 事件。

#### 项目级子代理事件钩子

在 `settings.json` 中配置钩子来响应主会话中的子代理生命周期事件。

| 事件 | 匹配器输入 | 触发时机 |
| :--- | :--- | :--- |
| `SubagentStart` | 代理类型名称 | 子代理开始执行时 |
| `SubagentStop` | 代理类型名称 | 子代理完成时 |

两个事件都支持匹配器来按名称定位特定代理类型。以下示例仅在 `db-agent` 子代理启动时运行设置脚本，在任何子代理停止时运行清理脚本：

```json theme={null}
{
  "hooks": {
    "SubagentStart": [
      {
        "matcher": "db-agent",
        "hooks": [
          { "type": "command", "command": "./scripts/setup-db-connection.sh" }
        ]
      }
    ],
    "SubagentStop": [
      {
        "hooks": [
          { "type": "command", "command": "./scripts/cleanup-db-connection.sh" }
        ]
      }
    ]
  }
}
```

完整的钩子配置格式请参阅 [Hooks](https://code.claude.com/docs/en/hooks)。
## 使用子代理

### 理解自动委派机制

**Claude 会根据任务描述和上下文自动选择合适的子代理。** Claude 依据你请求中的任务描述、子代理配置中的 `description` 字段以及当前上下文来自动委派任务。如果希望 Claude 更积极地使用某个子代理，可以在其 description 字段中加入"use proactively"之类的描述。

### 显式调用子代理

**当自动委派不够精确时，你可以手动指定子代理。** 以下三种模式从一次性建议逐步升级为会话级默认：

| 模式 | 说明 |
| :--- | :--- |
| 自然语言 | 在提示词中提到子代理名称，Claude 自行决定是否委派 |
| @-提及 | 保证对单个任务运行指定的子代理 |
| 会话级 | 整个会话使用该子代理的系统提示、工具限制和模型，通过 `--agent` 标志或 `agent` 设置启用 |

对于自然语言方式，不需要特殊语法。直接提到子代理名称，Claude 通常就会委派：

```text theme={null}
Use the test-runner subagent to fix failing tests
Have the code-reviewer subagent look at my recent changes
```

**使用 @-提及子代理。** 输入 `@` 并从提示列表中选择子代理，操作方式与 @-提及文件相同。这能确保指定的子代理一定被调用，而不是交由 Claude 自行决定：

```text theme={null}
@"code-reviewer (agent)" look at the auth changes
```

你的完整消息仍然发送给 Claude，Claude 会根据你的请求为子代理编写任务提示。@-提及控制的是 Claude 调用哪个子代理，而非子代理收到什么提示。

由已启用的[插件](https://code.claude.com/docs/en/plugins)提供的子代理会以作用域名称显示在提示列表中，例如 `my-plugin:code-reviewer` 或 `my-plugin:review:security`（当插件[将代理组织到子文件夹中](#选择子代理作用域)时）。当前会话中正在运行的命名后台子代理也会出现在提示列表中，名称旁显示其状态。

你也可以手动输入提及而不使用选择器：本地子代理用 `@agent-<name>`，插件子代理用 `@agent-` 加上作用域名称，例如 `@agent-my-plugin:code-reviewer`。

**将整个会话作为子代理运行。** 传入 [`--agent <name>`](https://code.claude.com/docs/en/cli-reference) 来启动一个会话，主线程会采用该子代理的系统提示、工具限制和模型：

```bash theme={null}
claude --agent code-reviewer
```

子代理的系统提示会完全替换默认的 Claude Code 系统提示，与 [`--system-prompt`](https://code.claude.com/docs/en/cli-reference) 的效果相同。`CLAUDE.md` 文件和项目记忆仍通过正常的消息流加载。代理名称以 `@<name>` 显示在启动头部，方便你确认其已激活。

这对内置和自定义子代理都有效，且选择在恢复会话时会持续保留。

对于插件提供的子代理，只需传入代理名称，Claude Code 会自动查找：

```bash theme={null}
claude --agent security-reviewer
```

如果多个插件提供了同名代理，传入作用域名称以消除歧义：

```bash theme={null}
claude --agent my-plugin:security-reviewer
```

如果插件将代理放在 `agents/` 目录的子文件夹中，作用域名称中需包含子文件夹路径，例如 `claude --agent my-plugin:review:security`。

要将其设为项目中每个会话的默认值，在 `.claude/settings.json` 中设置 `agent`：

```json theme={null}
{
  "agent": "code-reviewer"
}
```

CLI 标志在两者同时存在时会覆盖设置文件。

### 前台或后台运行子代理

**子代理可以在前台或后台运行，各有不同的交互方式。**

| 模式 | 行为 |
| :--- | :--- |
| 前台子代理 | 阻塞主对话直到完成。权限提示会实时传递给你。 |
| 后台子代理 | 并发运行，你可以继续工作。从 v2.1.186 起，当后台子代理遇到需要权限的工具调用时，提示会出现在你的主会话中并标注是哪个子代理在请求。批准即可让子代理继续，按 Esc 则拒绝该单次工具调用而不停止子代理。v2.1.186 之前，后台子代理会自动拒绝任何需要提示的工具调用。 |

Claude 会根据任务自行决定在前台还是后台运行子代理。你也可以：

* 要求 Claude "run this in the background"
* 按 **Ctrl+B** 将正在运行的任务转入后台

要完全禁用后台任务功能，将 `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` 环境变量设为 `1`。参见[环境变量](https://code.claude.com/docs/en/env-vars)。

当 [`CLAUDE_CODE_FORK_SUBAGENT`](#分叉当前对话) 设为 `1` 时，每次子代理生成都在后台运行，不受 `background` 字段影响。这些后台子代理的权限提示会如上所述出现在你的主会话中。

### 常见模式

#### 隔离高产出操作

**子代理最有效的用途之一是隔离大量输出的操作。** 运行测试、获取文档或处理日志文件都会消耗大量上下文。将这些委派给子代理后，冗长的输出留在子代理的上下文中，只有相关摘要返回到你的主对话。

```text theme={null}
Use a subagent to run the test suite and report only the failing tests with their error messages
```

#### 并行研究

**对于相互独立的调查任务，可以同时启动多个子代理：**

```text theme={null}
Research the authentication, database, and API modules in parallel using separate subagents
```

每个子代理独立探索各自的领域，然后 Claude 综合所有发现。这在研究路径互不依赖时效果最好。

> **注意：** 子代理完成时，其结果会返回到主对话。运行大量子代理且每个都返回详细结果会消耗大量上下文。

对于需要持续并行或超出上下文窗口的任务，[代理团队](https://code.claude.com/docs/en/agent-teams)为每个工作者提供独立的上下文。

#### 串联子代理

**对于多步骤工作流，让 Claude 按顺序使用子代理。** 每个子代理完成任务并将结果返回给 Claude，Claude 再将相关上下文传递给下一个子代理。

```text theme={null}
Use the code-reviewer subagent to find performance issues, then use the optimizer subagent to fix them
```

### 选择子代理还是主对话

**使用主对话**的场景：

* 任务需要频繁的往返交互或迭代优化
* 多个阶段共享大量上下文，如规划、实现和测试
* 你在做快速、精准的小改动
* 延迟敏感的场景。子代理从零开始，可能需要时间收集上下文

**使用子代理**的场景：

* 任务产生大量你不需要保留在主上下文中的输出
* 你希望强制执行特定的工具限制或权限
* 工作是自包含的，可以返回一份摘要

如果你需要在主对话上下文中运行可复用的提示或工作流（而非隔离的子代理上下文），可以考虑使用 [Skills](https://code.claude.com/docs/en/skills)。

对于关于对话中已有内容的快速提问，使用 [`/btw`](https://code.claude.com/docs/en/interactive-mode#side-questions-with-%2Fbtw) 而不是子代理。它能看到你的完整上下文但无法使用工具，且回答不会被添加到历史记录中。

### 生成嵌套子代理

**从 Claude Code v2.1.172 起，子代理可以生成自己的子代理。** 当被委派的任务本身可以拆分为并行子任务时使用此功能，例如一个审查子代理为每个发现分派一个验证器，这样中间输出永远不会进入你的主对话。只有顶层子代理的摘要会返回给你。

嵌套子代理的配置方式与顶层子代理相同，从相同的[作用域](#选择子代理作用域)解析。提示输入下方的子代理面板显示完整的树结构：每行显示后代数量的 `(+N)` 计数，展开某行会显示该子代理的直接子代理以及返回 `main` 的路径。[`/agents`](#使用-agents-命令) 中的 Running 标签页以扁平列表显示正在运行的子代理。

深度计算为主对话之下的子代理层级数，无论每一层是在[前台还是后台](#前台或后台运行子代理)运行。位于第五层深度的子代理不会获得 Agent 工具，因此无法继续生成子代理。此限制是固定的，不可配置。

从 Claude Code v2.1.187 起，后台子代理的深度在首次生成时确定，之后[恢复](#恢复子代理)不会改变该深度。例如，如果你的主对话生成了子代理 A，A 在第二层生成了后台子代理 B，那么即使你后来直接从主对话恢复 B，B 仍然在第二层。从较浅的上下文恢复子代理不会让它获得深度限制已经阻止的额外生成层级。

要阻止特定子代理生成其他子代理，从其 [`tools`](#可用工具) 列表中移除 `Agent`，或将其添加到 `disallowedTools`。

[分叉](#分叉当前对话)仍然不能生成另一个分叉。它可以生成其他类型的子代理，这些会计入深度限制。

### 管理子代理上下文

#### 启动时加载的内容

**每个子代理启动时拥有全新的、隔离的上下文窗口。** 它看不到你的对话历史、你已调用的 skills 或 Claude 已读取的文件。Claude 会编写一条委派消息来概括任务，子代理从该消息开始工作。例外是[分叉](#分叉当前对话)，它继承父对话而非从零开始。

非分叉子代理的初始上下文包含：

| 内容 | 说明 |
| :--- | :--- |
| 系统提示 | 代理自身的提示加上 Claude Code 附加的环境详情，而非完整的 Claude Code 系统提示。自定义子代理在 [markdown 正文](#编写子代理文件)或 `prompt` 字段中定义。内置代理有预定义的提示。 |
| 任务消息 | Claude 在交接工作时编写的委派提示。 |
| CLAUDE.md 和记忆 | 主对话加载的[记忆层级](https://code.claude.com/docs/en/memory#how-claude-md-files-load)的每一层，包括 `~/.claude/CLAUDE.md`、项目规则、`CLAUDE.local.md` 和托管策略文件。内置的 Explore 和 Plan 代理跳过此项。 |
| Git 状态 | 父会话启动时的快照。当工作目录不是 Git 仓库或 [`includeGitInstructions`](https://code.claude.com/docs/en/settings#available-settings) 为 `false` 时不包含。Explore 和 Plan 无论如何都跳过此项。 |
| 预加载的 skills | 代理 [`skills` 字段](#将-skills-预加载到子代理中)中指定的任何 skill 的完整内容。内置代理不预加载 skills。 |

Explore 和 Plan 是唯一省略 CLAUDE.md 和 git 状态的子代理。没有 frontmatter 字段或针对单个代理的设置可以改变哪些代理跳过它们。

主对话在拥有完整 CLAUDE.md 上下文的情况下读取 Explore 和 Plan 的结果，因此大多数规则不需要传递到子代理本身。如果某条规则必须传递（例如"忽略 `vendor/` 目录"），在委派时的提示中重新声明即可。

#### 恢复子代理

**每次子代理调用都会创建一个新实例。要继续现有子代理的工作而非重新开始，请让 Claude 恢复它。**

恢复的子代理保留其完整的对话历史，包括所有先前的工具调用、结果和推理过程。子代理会从停止的地方精确继续，而不是重新开始。

当子代理完成时，Claude 会收到其代理 ID。内置的 Explore 和 Plan 代理是一次性的，不返回代理 ID，因此无法恢复；当你需要继续工作时，使用 `general-purpose` 或自定义子代理。

Claude 使用 `SendMessage` 工具并将代理 ID 作为 `to` 字段来恢复子代理。`SendMessage` 工具始终可用于通过代理 ID 或名称恢复子代理。结构化的团队协议消息（如 `shutdown_request` 和 `plan_approval_response`）需要启用[代理团队](https://code.claude.com/docs/en/agent-teams)。

要恢复子代理，让 Claude 继续之前的工作：

```text theme={null}
Use the code-reviewer subagent to review the authentication module
[Agent completes]

Continue that code review and now analyze the authorization logic
[Claude resumes the subagent with full context from previous conversation]
```

如果一个已停止的子代理收到 `SendMessage`，它会在后台自动恢复，无需新的 `Agent` 调用。

你也可以向 Claude 请求代理 ID 以便显式引用，或在 `~/.claude/projects/{project}/{sessionId}/subagents/` 的转录文件中查找 ID。每个转录以 `agent-{agentId}.jsonl` 格式存储。

子代理转录独立于主对话持久化：

| 场景 | 行为 |
| :--- | :--- |
| 主对话压缩 | 子代理转录不受影响。它们存储在独立文件中。 |
| 会话持久化 | 子代理转录在会话内持久保存。你可以在重启 Claude Code 后通过恢复同一会话来[恢复子代理](#恢复子代理)。 |
| 自动清理 | 转录根据 `cleanupPeriodDays` 设置清理，默认为 30 天。 |

#### 自动压缩

**子代理支持与主对话相同逻辑的自动压缩。** 压缩在相同条件下触发，`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` 也适用于子代理。参见[环境变量](https://code.claude.com/docs/en/env-vars)了解该覆盖何时生效。

压缩事件记录在子代理转录文件中：

```json theme={null}
{
  "type": "system",
  "subtype": "compact_boundary",
  "compactMetadata": {
    "trigger": "auto",
    "preTokens": 167189
  }
}
```

`preTokens` 值表示压缩发生前使用了多少 token。

## 分叉当前对话

> **注意：** 分叉子代理需要 Claude Code v2.1.117 或更高版本。从 v2.1.161 起 `/fork` 命令默认启用；在更早版本中需要将 [`CLAUDE_CODE_FORK_SUBAGENT`](https://code.claude.com/docs/en/env-vars) 环境变量设为 `1`。让 Claude 自行生成分叉是实验性的，可能在未来版本中变更。此功能也可能作为分阶段推出的一部分在交互式会话中启用。

**分叉是继承整个对话历史的子代理，而非从零开始。** 这打破了子代理通常提供的输入隔离：分叉看到的系统提示、工具、模型和消息历史与主会话完全相同，因此你可以将旁支任务交给它而无需重新解释情况。分叉自身的工具调用仍然不会进入你的对话，只有最终结果返回，从而保持主上下文窗口的整洁。当命名子代理需要太多背景信息才能有用时，或者当你想从同一起点并行尝试多种方案时，使用分叉。

要不受分阶段推出的影响地控制分叉模式，将 [`CLAUDE_CODE_FORK_SUBAGENT`](https://code.claude.com/docs/en/env-vars) 设为 `1` 显式启用或设为 `0` 显式禁用。该变量在交互模式以及通过 SDK 或 `claude -p` 使用时均有效。

启用分叉模式后 Claude Code 有两个变化：

* Claude 可以通过在 Agent 工具中显式请求 `fork` 子代理类型来生成分叉。未指定子代理类型的生成仍使用[通用](#内置子代理)子代理，命名子代理如 Explore 仍按原方式生成。
* 每次子代理生成都在[后台](#前台或后台运行子代理)运行，无论是分叉还是命名子代理。将 `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` 设为 `1` 可保持同步生成。

你可以使用 `/fork` 加上指令自行启动分叉，无论该变量是否设置。Claude Code 会从指令的开头几个词为分叉命名。以下示例在你继续在主会话中进行实现的同时，分叉对话来起草测试用例：

```text theme={null}
/fork draft unit tests for the parser changes so far
```

分叉出现在提示下方的面板中，在后台运行的同时你可以继续工作。完成时，其结果以消息形式出现在你的主对话中。下一节介绍在分叉运行时监控和操作它们的面板控制。

### 观察和操作运行中的分叉

**运行中的分叉显示在提示输入下方的面板中。** 面板中主会话和每个分叉各占一行。使用以下按键与面板交互：

| 按键 | 操作 |
| :--- | :--- |
| `上` / `下` | 在行之间移动 |
| `Enter` | 打开所选分叉的转录并发送后续消息 |
| `x` | 关闭已完成的分叉或停止正在运行的分叉 |
| `Esc` | 将焦点返回到提示输入 |

### 分叉与命名子代理的区别

**分叉继承主会话生成时的所有内容。命名子代理从自身定义开始。**

|  | 分叉 | 命名子代理 |
| :--- | :--- | :--- |
| 上下文 | 完整的对话历史 | 全新上下文，包含你传入的提示 |
| 系统提示和工具 | 与主会话相同 | 来自子代理的[定义文件](#编写子代理文件) |
| 模型 | 与主会话相同 | 来自子代理的 `model` 字段 |
| 权限 | 提示出现在你的终端中 | 后台运行时[提示出现在你的主会话中](#前台或后台运行子代理) |
| 提示缓存 | 与主会话共享 | 独立缓存 |

由于分叉的系统提示和工具定义与父级完全相同，其第一个请求会复用父级的[提示缓存](https://code.claude.com/docs/en/prompt-caching#subagents-and-the-cache)。这使得对于需要相同上下文的任务，分叉比生成全新子代理成本更低。

当 Claude 通过 Agent 工具生成分叉时，可以传入 `isolation: "worktree"` 使分叉的文件编辑写入单独的 git worktree 而非你的检出目录。

### 限制

将 `CLAUDE_CODE_FORK_SUBAGENT=1` 设置后会在交互式会话、[非交互模式](https://code.claude.com/docs/en/headless)和 Agent SDK 中启用分叉模式；设为 `0` 则在所有地方禁用分叉模式，包括任何服务端推出。分叉不能再生成新的分叉。

## 子代理示例

**这些示例展示了构建子代理的有效模式。** 可以将它们作为起点使用，或者让 Claude 生成定制版本。

> **最佳实践：**
>
> * **设计专注的子代理：** 每个子代理应专注做好一件具体的事
> * **编写详细的描述：** Claude 根据描述来决定何时委派
> * **限制工具访问：** 仅授予必要的权限，兼顾安全性和专注度
> * **纳入版本控制：** 与团队共享项目级子代理

### 代码审查器

**一个只读子代理，审查代码但不修改代码。** 此示例展示了如何设计一个工具访问受限（无 Edit 或 Write）的专注子代理，以及如何编写详细提示来指定检查内容和输出格式。

```markdown theme={null}
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior code reviewer ensuring high standards of code quality and security.

When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code is clear and readable
- Functions and variables are well-named
- No duplicated code
- Proper error handling
- No exposed secrets or API keys
- Input validation implemented
- Good test coverage
- Performance considerations addressed

Provide feedback organized by priority:
- Critical issues (must fix)
- Warnings (should fix)
- Suggestions (consider improving)

Include specific examples of how to fix issues.
```

### 调试器

**一个既能分析也能修复问题的子代理。** 与代码审查器不同，此子代理包含 Edit 工具，因为修复 bug 需要修改代码。提示提供了从诊断到验证的清晰工作流。

```markdown theme={null}
---
name: debugger
description: Debugging specialist for errors, test failures, and unexpected behavior. Use proactively when encountering any issues.
tools: Read, Edit, Bash, Grep, Glob
---

You are an expert debugger specializing in root cause analysis.

When invoked:
1. Capture error message and stack trace
2. Identify reproduction steps
3. Isolate the failure location
4. Implement minimal fix
5. Verify solution works

Debugging process:
- Analyze error messages and logs
- Check recent code changes
- Form and test hypotheses
- Add strategic debug logging
- Inspect variable states

For each issue, provide:
- Root cause explanation
- Evidence supporting the diagnosis
- Specific code fix
- Testing approach
- Prevention recommendations

Focus on fixing the underlying issue, not the symptoms.
```

### 数据科学家

**一个面向数据分析工作的领域专用子代理。** 此示例展示了如何为典型编码任务之外的专业工作流创建子代理。它显式设置 `model: sonnet` 以获得更强的分析能力。

```markdown theme={null}
---
name: data-scientist
description: Data analysis expert for SQL queries, BigQuery operations, and data insights. Use proactively for data analysis tasks and queries.
tools: Bash, Read, Write
model: sonnet
---

You are a data scientist specializing in SQL and BigQuery analysis.

When invoked:
1. Understand the data analysis requirement
2. Write efficient SQL queries
3. Use BigQuery command line tools (bq) when appropriate
4. Analyze and summarize results
5. Present findings clearly

Key practices:
- Write optimized SQL queries with proper filters
- Use appropriate aggregations and joins
- Include comments explaining complex logic
- Format results for readability
- Provide data-driven recommendations

For each analysis:
- Explain the query approach
- Document any assumptions
- Highlight key findings
- Suggest next steps based on data

Always ensure queries are efficient and cost-effective.
```

### 数据库查询验证器

**一个允许 Bash 访问但通过验证确保只执行只读 SQL 查询的子代理。** 此示例展示了当需要比 `tools` 字段更精细的控制时，如何使用 `PreToolUse` 钩子进行条件验证。

```markdown theme={null}
---
name: db-reader
description: Execute read-only database queries. Use when analyzing data or generating reports.
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---

You are a database analyst with read-only access. Execute SELECT queries to answer questions about the data.

When asked to analyze data:
1. Identify which tables contain the relevant data
2. Write efficient SELECT queries with appropriate filters
3. Present results clearly with context

You cannot modify data. If asked to INSERT, UPDATE, DELETE, or modify schema, explain that you only have read access.
```

Claude Code [通过 stdin 将钩子输入以 JSON 形式传递](https://code.claude.com/docs/en/hooks#pretooluse-input)给钩子命令。验证脚本读取此 JSON，提取正在执行的命令，并对照 SQL 写操作列表进行检查。如果检测到写操作，脚本[以退出码 2 退出](https://code.claude.com/docs/en/hooks#exit-code-2-behavior-per-event)来阻止执行，并通过 stderr 向 Claude 返回错误信息。

在项目中的任意位置创建验证脚本。路径必须与钩子配置中的 `command` 字段匹配：

```bash theme={null}
#!/bin/bash
# Blocks SQL write operations, allows SELECT queries

# Read JSON input from stdin
INPUT=$(cat)

# Extract the command field from tool_input using jq
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [ -z "$COMMAND" ]; then
  exit 0
fi

# Block write operations (case-insensitive)
if echo "$COMMAND" | grep -iE '\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|REPLACE|MERGE)\b' > /dev/null; then
  echo "Blocked: Write operations not allowed. Use SELECT queries only." >&2
  exit 2
fi

exit 0
```

在 macOS 和 Linux 上，将脚本设为可执行：

```bash theme={null}
chmod +x ./scripts/validate-readonly-query.sh
```

在 Windows 上，用 PowerShell 编写验证脚本并在钩子条目中添加 `shell: powershell`。参见[在 PowerShell 中运行钩子](https://code.claude.com/docs/en/hooks#windows-powershell-tool)。

钩子通过 stdin 接收 JSON，Bash 命令位于 `tool_input.command` 中。退出码 2 阻止操作并将错误信息反馈给 Claude。参见 [Hooks](https://code.claude.com/docs/en/hooks#exit-code-output) 了解退出码详情，参见[钩子输入](https://code.claude.com/docs/en/hooks#pretooluse-input)了解完整的输入 schema。

## 后续步骤

**理解子代理之后，可以探索以下相关功能：**

* [通过插件分发子代理](https://code.claude.com/docs/en/plugins) -- 跨团队或项目共享子代理
* [以编程方式运行 Claude Code](https://code.claude.com/docs/en/headless) -- 通过 Agent SDK 用于 CI/CD 和自动化
* [使用 MCP 服务器](https://code.claude.com/docs/en/mcp) -- 让子代理访问外部工具和数据
