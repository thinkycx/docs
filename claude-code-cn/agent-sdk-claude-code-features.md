---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Agent SDK - Claude Code 功能集成
description: 如何在 Agent SDK 中加载项目指令（CLAUDE.md）、Skills、Hooks 等 Claude Code 文件系统功能，涵盖 settingSources 配置、加载位置和功能选择指南。
category: translation
tags: [claude-code, agent-sdk, translation]
refs:
  - https://code.claude.com/docs/en/agent-sdk/claude-code-features.md
  - en-source/agent-sdk/claude-code-features.md
---

# SDK 中使用 Claude Code 功能

> 将项目指令、Skills、Hooks 及其他 Claude Code 功能加载到 SDK Agent 中

**Agent SDK 构建在与 Claude Code 相同的基础之上，意味着 SDK Agent 可以访问相同的文件系统功能：** 项目指令（`CLAUDE.md` 和 rules）、Skills、Hooks 等。

省略 `settingSources` 时，`query()` 读取与 Claude Code CLI 相同的文件系统设置：user、project 和 local 设置、CLAUDE.md 文件、`.claude/` 中的 skills、agents 和 commands。要不加载这些，传 `settingSources: []` 让 Agent 仅限于你以编程方式配置的内容。Managed policy 设置和全局 `~/.claude.json` 配置无论此选项如何都会被读取。参见 [settingSources 不控制什么](#settingsources-不控制什么)。

功能概览和使用时机参见 [扩展 Claude Code](https://code.claude.com/docs/en/features-overview)。

## 用 settingSources 控制文件系统设置

**setting sources 选项（Python 中 [`setting_sources`](https://code.claude.com/docs/en/agent-sdk/python#claudeagentoptions)，TypeScript 中 [`settingSources`](https://code.claude.com/docs/en/agent-sdk/typescript#settingsource)）控制 SDK 加载哪些文件系统设置。** 传显式列表以选择性加载特定来源，或传空数组禁用 user、project 和 local 设置。

示例 — 同时加载用户级和项目级设置：

```python
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

async for message in query(
    prompt="Help me refactor the auth module",
    options=ClaudeAgentOptions(
        # "user" 从 ~/.claude/ 加载，"project" 从 ./.claude/ 加载（cwd）。
        # 一起提供对两个位置的 CLAUDE.md、skills、hooks 和权限的访问。
        setting_sources=["user", "project"],
        allowed_tools=["Read", "Edit", "Bash"],
    ),
):
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if hasattr(block, "text"):
                print(block.text)
    if isinstance(message, ResultMessage) and message.subtype == "success":
        print(f"\nResult: {message.result}")
```

每个 source 从特定位置加载设置，其中 `<cwd>` 是通过 `cwd` 选项传入的工作目录，未设置则为进程当前目录。完整类型定义参见 [`SettingSource`](https://code.claude.com/docs/en/agent-sdk/typescript#settingsource)（TypeScript）或 [`SettingSource`](https://code.claude.com/docs/en/agent-sdk/python#settingsource)（Python）。

| Source | 加载内容 | 位置 |
|:---|:---|:---|
| `"project"` | 项目 CLAUDE.md、`.claude/rules/*.md`、项目 skills、项目 hooks、项目 `settings.json` | `<cwd>/.claude/`（settings.json 和 hooks）；`<cwd>` 及每个父目录（CLAUDE.md 和 rules）；`<cwd>` 及每个父目录直到仓库根（skills） |
| `"user"` | 用户 CLAUDE.md、`~/.claude/rules/*.md`、用户 skills、用户设置 | `~/.claude/` |
| `"local"` | CLAUDE.local.md、`.claude/settings.local.json` | `<cwd>/.claude/`（settings.local.json）；`<cwd>` 及每个父目录（CLAUDE.local.md） |

省略 `settingSources` 等同于 `["user", "project", "local"]`。

`cwd` 选项决定 SDK 去哪里查找项目级输入。CLAUDE.md 和 rules 从 `<cwd>` 和每个父目录加载。Skills 从 `<cwd>` 和每个父目录直到仓库根加载。项目 `settings.json` 和 hooks 仅从 `<cwd>/.claude/` 加载，无父目录回退。

### settingSources 不控制什么

**`settingSources` 覆盖 user、project 和 local 设置。少数输入无论其值如何都会被读取：**

| 输入 | 行为 | 禁用方式 |
|:---|:---|:---|
| Managed policy 设置 | 端点管理策略（如 MDM plist、注册表策略或 managed settings 文件）从主机加载。[Server-managed settings](https://code.claude.com/docs/en/server-managed-settings) 在 [符合条件的配置](https://code.claude.com/docs/en/server-managed-settings#platform-availability) 上通过组织 OAuth 登录或直接配置的 API key 认证时获取 | 端点策略：从主机移除 managed settings 文件。Server-managed settings：由组织管理员控制；无法从 SDK 禁用 |
| `~/.claude.json` 全局配置 | 始终读取 | 用 `env` 中的 `CLAUDE_CONFIG_DIR` 重定位 |
| `~/.claude/projects/<project>/memory/` 中的自动记忆 | 会话开始时加载到系统提示词。Agent 用标准 `Write` 和 `Edit` 工具写入新记忆，因此这些工具必须启用才能保存记忆 | 在设置中设 `autoMemoryEnabled: false`，或在 `env` 中设 `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` |
| [claude.ai MCP connectors](https://code.claude.com/docs/en/mcp#use-mcp-servers-from-claude-ai) | 当活跃认证方式为 claude.ai 订阅时加载。传 `mcpServers: {}` 不会抑制它们 | 在设置中设 `strictMcpConfig: true`、[`disableClaudeAiConnectors: true`](https://code.claude.com/docs/en/mcp#disable-claude-ai-connectors)，或在 `env` 中设 `ENABLE_CLAUDEAI_MCP_SERVERS=false` |

> **警告：** 不要依赖默认 `query()` 选项做多租户隔离。上述输入无论 `settingSources` 如何都会被读取，SDK 进程可能获取主机级配置和按目录记忆。多租户部署时，每个租户运行在独立文件系统中并设 `settingSources: []` 加 `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`。[Server-managed settings](https://code.claude.com/docs/en/server-managed-settings) 在进程以组织凭证认证时获取；文件系统隔离不能移除它们。参见 [安全部署](https://code.claude.com/docs/en/agent-sdk/secure-deployment)。

## 项目指令（CLAUDE.md 和 rules）

**`CLAUDE.md` 文件和 `.claude/rules/*.md` 文件为 Agent 提供关于项目的持久上下文：** 编码约定、构建命令、架构决策和指令。当 `settingSources` 包含 `"project"` 时，SDK 在会话开始时将这些文件加载到上下文中。Agent 遵循项目约定而无需在每个 Prompt 中重复。

### CLAUDE.md 加载位置

| 层级 | 位置 | 何时加载 |
|:---|:---|:---|
| 项目（根） | `<cwd>/CLAUDE.md` 或 `<cwd>/.claude/CLAUDE.md` | `settingSources` 包含 `"project"` |
| 项目 rules | `<cwd>/.claude/rules/*.md` 及每个父目录的 `.claude/rules/*.md` | `settingSources` 包含 `"project"` |
| 项目（父目录） | `cwd` 上层目录中的 `CLAUDE.md` 文件 | `settingSources` 包含 `"project"`，会话开始时加载 |
| 项目（子目录） | `cwd` 子目录中的 `CLAUDE.md` 文件 | `settingSources` 包含 `"project"`，Agent 读取该子树中的文件时按需加载 |
| Local | `<cwd>/CLAUDE.local.md` 及每个父目录的 `CLAUDE.local.md` | `settingSources` 包含 `"local"` |
| 用户 | `~/.claude/CLAUDE.md` | `settingSources` 包含 `"user"` |
| 用户 rules | `~/.claude/rules/*.md` | `settingSources` 包含 `"user"` |

所有层级叠加：如果项目和用户的 CLAUDE.md 文件都存在，Agent 两者都能看到。层级间没有硬性优先规则；指令冲突时结果取决于 Claude 如何解读。编写不冲突的规则，或在更具体的文件中明确声明优先级（"These project instructions override any conflicting user-level defaults"）。

> **提示：** 也可以直接通过 `systemPrompt` 注入上下文而不使用 CLAUDE.md 文件。参见 [修改系统提示词](https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts)。当你希望交互式 Claude Code 会话和 SDK Agent 共享相同上下文时使用 CLAUDE.md。

关于 CLAUDE.md 内容的组织和结构化，参见 [管理 Claude 的记忆](https://code.claude.com/docs/en/memory)。

## Skills

**Skills 是 markdown 文件，为 Agent 提供专业知识和可调用的工作流。** 与 `CLAUDE.md`（每次会话加载）不同，Skills 按需加载。Agent 在启动时接收 Skill 描述，相关时才加载完整内容。

Skills 通过 `settingSources` 从文件系统发现。`query()` 上的 `skills` 选项省略时，发现的 user 和 project skills 启用且 Skill 工具可用，匹配 CLI 行为。要控制启用哪些 skills，传 `skills` 为 `"all"`、skill 名称列表或 `[]` 禁用全部。设置 `skills` 时，SDK 自动将 Skill 工具添加到 `allowedTools`。如果同时传了显式 `tools` 列表，在该列表中包含 `"Skill"` 以便 Claude 能调用 skills。

```python
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

# .claude/skills/ 中的 skills 在 settingSources 包含 "project" 时自动发现
async for message in query(
    prompt="Review this PR using our code review checklist",
    options=ClaudeAgentOptions(
        setting_sources=["user", "project"],
        skills="all",
        allowed_tools=["Read", "Grep", "Glob"],
    ),
):
    if isinstance(message, ResultMessage) and message.subtype == "success":
        print(message.result)
```

> Skills 必须创建为文件系统产物（`.claude/skills/<name>/SKILL.md`）。SDK 没有编程注册 skills 的 API。参见 [SDK 中的 Agent Skills](https://code.claude.com/docs/en/agent-sdk/skills)。

创建和使用 skills 的更多信息参见 [SDK 中的 Agent Skills](https://code.claude.com/docs/en/agent-sdk/skills)。

## Hooks

**SDK 支持两种方式定义 Hooks，且它们并行运行：**

- **文件系统 Hooks：** 在 `settings.json` 中定义的 shell 命令，当 `settingSources` 包含相关 source 时加载。与 [交互式 Claude Code 会话](https://code.claude.com/docs/en/hooks-guide) 配置的 hooks 相同。
- **编程式 Hooks：** 直接传给 `query()` 的回调函数。在你的应用进程中运行，可以返回结构化决策。参见 [Hooks 控制执行](https://code.claude.com/docs/en/agent-sdk/hooks)。

两种类型在相同的 hook 生命周期中执行。如果项目的 `.claude/settings.json` 中已有 hooks 且设置了 `settingSources: ["project"]`，这些 hooks 在 SDK 中自动运行，无需额外配置。

Hook 回调接收工具输入并返回决策 dict。返回 `{}` 表示允许工具继续。要阻止执行，返回带 `permissionDecision: "deny"` 和 `permissionDecisionReason` 的 `hookSpecificOutput` 对象。reason 作为工具结果发送给 Claude。顶层 `decision` 和 `reason` 字段在 `PreToolUse` 中已弃用。参见 [Hooks 指南](https://code.claude.com/docs/en/agent-sdk/hooks) 了解完整回调签名和返回类型。

```python
from claude_agent_sdk import query, ClaudeAgentOptions, HookMatcher, ResultMessage


# PreToolUse hook 回调。位置参数：
#   input_data: HookInput dict，包含 tool_name, tool_input, hook_event_name
#   tool_use_id: str | None，被拦截的工具调用 ID
#   context: HookContext，携带会话元数据
async def audit_bash(input_data, tool_use_id, context):
    command = input_data.get("tool_input", {}).get("command", "")
    if "rm -rf" in command:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "Destructive command blocked",
            }
        }
    return {}  # 空 dict：允许工具继续


# .claude/settings.json 中的文件系统 hooks 在 settingSources 加载时自动运行。
# 你还可以添加编程式 hooks：
async for message in query(
    prompt="Refactor the auth module",
    options=ClaudeAgentOptions(
        setting_sources=["project"],  # 从 .claude/settings.json 加载 hooks
        hooks={
            "PreToolUse": [
                HookMatcher(matcher="Bash", hooks=[audit_bash]),
            ]
        },
    ),
):
    if isinstance(message, ResultMessage) and message.subtype == "success":
        print(message.result)
```

### 何时使用哪种 Hook 类型

| Hook 类型 | 适用场景 |
|:---|:---|
| **文件系统**（`settings.json`） | CLI 和 SDK 会话共享 hooks。支持 `"command"`（shell 脚本）、`"http"`（POST 到端点）、`"mcp_tool"`（调用已连接的 MCP 服务器工具）、`"prompt"`（LLM 评估提示词）和 `"agent"`（派生验证 Agent）。在主 Agent 和其派生的子代理中都会触发。 |
| **编程式**（`query()` 中的回调） | 应用特定逻辑、结构化决策和进程内集成。也在子代理中触发。回调接收 `agent_id` 和 `agent_type` 以区分。 |

> TypeScript SDK 支持 Python 之外的额外 hook 事件，包括 `SessionStart`、`SessionEnd`、`TeammateIdle` 和 `TaskCompleted`。参见 [Hooks 指南](https://code.claude.com/docs/en/agent-sdk/hooks) 了解完整事件兼容性表。

编程式 hooks 详细信息参见 [Hooks 控制执行](https://code.claude.com/docs/en/agent-sdk/hooks)。文件系统 hook 语法参见 [Hooks](https://code.claude.com/docs/en/hooks)。

## 选择合适的功能

**Agent SDK 提供多种扩展 Agent 行为的方式。** 如果不确定用哪个，下表将常见目标映射到正确的方案。

| 你想... | 使用 | SDK 接口 |
|:---|:---|:---|
| 设置 Agent 始终遵循的项目约定 | [CLAUDE.md](https://code.claude.com/docs/en/memory) | `settingSources: ["project"]` 自动加载 |
| 给 Agent 提供相关时才加载的参考材料 | [Skills](https://code.claude.com/docs/en/agent-sdk/skills) | `settingSources` + `skills` 选项 |
| 运行可复用的工作流（部署、评审、发布） | [用户可调用的 Skills](https://code.claude.com/docs/en/agent-sdk/skills) | `settingSources` + `skills` 选项 |
| 将隔离的子任务委派到全新上下文（调研、评审） | [子代理](https://code.claude.com/docs/en/agent-sdk/subagents) | `agents` 参数 + `allowedTools: ["Agent"]` |
| 多个 Claude Code 实例通过共享任务列表和直接消息协作 | [Agent teams](https://code.claude.com/docs/en/agent-teams) | 非 SDK 选项直接配置。Agent teams 是 CLI 功能，一个会话充当 team lead 协调独立 teammates |
| 对工具调用运行确定性逻辑（审计、阻止、转换） | [Hooks](https://code.claude.com/docs/en/agent-sdk/hooks) | `hooks` 参数配回调，或通过 `settingSources` 加载 shell 脚本 |
| 给 Claude 提供对外部服务的结构化工具访问 | [MCP](https://code.claude.com/docs/en/agent-sdk/mcp) | `mcpServers` 参数 |

> **提示：子代理 vs Agent teams —** 子代理是临时且隔离的：全新对话、一个任务、摘要返回父级。Agent teams 协调多个独立 Claude Code 实例，共享任务列表并直接相互发消息。Agent teams 是 CLI 功能。参见 [子代理继承什么](https://code.claude.com/docs/en/agent-sdk/subagents#what-subagents-inherit) 和 [Agent teams 对比](https://code.claude.com/docs/en/agent-teams#compare-with-subagents)。

你启用的每个功能都增加 Agent 的上下文窗口。每功能成本和功能叠加方式参见 [扩展 Claude Code](https://code.claude.com/docs/en/features-overview#understand-context-costs)。

## 相关资源

- [扩展 Claude Code](https://code.claude.com/docs/en/features-overview)：所有扩展功能的概念概览，含对比表和上下文成本分析
- [SDK 中的 Skills](https://code.claude.com/docs/en/agent-sdk/skills)：以编程方式使用 Skills 的完整指南
- [子代理](https://code.claude.com/docs/en/agent-sdk/subagents)：为隔离子任务定义和调用子代理
- [Hooks](https://code.claude.com/docs/en/agent-sdk/hooks)：在关键执行点拦截和控制 Agent 行为
- [权限](https://code.claude.com/docs/en/agent-sdk/permissions)：用模式、规则和回调控制工具访问
- [系统提示词](https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts)：不用 CLAUDE.md 文件注入上下文
