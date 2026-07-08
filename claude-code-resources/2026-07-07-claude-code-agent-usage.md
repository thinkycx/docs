---
create: 2026-07-07
update: 2026-07-07
author: thinkycx
title: Claude Code Agent 使用指南
description: 详解 Claude Code 的 --agent 标志和自定义 subagent 系统，包括 agent 文件格式、frontmatter 字段、作用域层级、调用方式和常见模式。
category: translation
tags: [claude-code, agent, subagent, cli]
keywords: [claude --agent, subagent, custom agent, agent file]
refs:
  - https://code.claude.com/docs/en/sub-agents
  - https://code.claude.com/docs/en/cli-reference
---

# Claude Code Agent 使用指南

## 核心概念

**Subagent 是有独立上下文窗口、系统提示词和工具限制的专用 AI 助手。** 它在自己的上下文中工作，只把摘要返回给主会话，避免大量搜索结果、日志等信息污染主对话上下文。

使用 subagent 的好处：

| 价值 | 说明 |
|------|------|
| 保护上下文 | 探索和实现在独立窗口完成 |
| 强制约束 | 限制可用工具 |
| 跨项目复用 | 用户级 agent 全局可用 |
| 专注行为 | 针对特定领域的系统提示词 |
| 控制成本 | 路由到更快更便宜的模型（如 Haiku） |

## `--agent` 基本用法

`--agent` 标志让整个会话使用指定 agent 的系统提示词、工具限制和模型。

```bash
# 启动指定 agent 会话
claude --agent code-reviewer

# 配合非交互模式
claude --agent code-reviewer -p "Review the auth module"

# 后台模式运行 agent
claude --bg --agent code-reviewer "investigate the flaky test"

# 插件 agent（多插件同名时用作用域前缀消歧义）
claude --agent my-plugin:security-reviewer
```

启动后终端标题栏显示 `@<name>` 以确认当前 agent 身份。

**关键行为**：agent 的系统提示词**完全替换**默认 Claude Code 系统提示词（类似 `--system-prompt`），但 `CLAUDE.md` 和项目 memory 仍正常加载。

## 创建 Agent 文件

Agent 文件是**带 YAML frontmatter 的 Markdown 文件**，frontmatter 定义配置，body 作为系统提示词。

### 文件位置与作用域

| 位置 | 作用域 | 优先级 |
|------|--------|--------|
| Managed settings | 组织级 | 1（最高） |
| `--agents` CLI flag | 当前会话 | 2 |
| `.claude/agents/` | 当前项目 | 3 |
| `~/.claude/agents/` | 所有项目 | 4 |
| Plugin `agents/` 目录 | 插件启用处 | 5（最低） |

同名 agent 使用高优先级位置的定义。目录支持递归扫描，可用子文件夹组织。

### 完整示例

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices. Use proactively after code changes.
tools: Read, Glob, Grep, Bash
model: sonnet
maxTurns: 50
permissionMode: acceptEdits
---

You are a senior code reviewer. When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code clarity and readability
- No exposed secrets or API keys
- Proper error handling
- Performance considerations

Provide feedback organized by priority:
- Critical issues (must fix)
- Warnings (should fix)
- Suggestions (consider improving)
```

### 支持的 Frontmatter 字段

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | 是 | 唯一标识符，小写字母+连字符 |
| `description` | 是 | 描述何时使用该 agent（Claude 据此决定自动委派） |
| `tools` | 否 | 可用工具白名单（省略则继承全部）。支持 `Agent(type1, type2)` 限制可调度的子 agent |
| `disallowedTools` | 否 | 工具黑名单，从继承列表中移除 |
| `model` | 否 | `sonnet` / `opus` / `haiku` / `fable` / 完整模型 ID / `inherit`。默认 `inherit` |
| `permissionMode` | 否 | `default` / `acceptEdits` / `auto` / `dontAsk` / `bypassPermissions` / `plan` |
| `maxTurns` | 否 | 最大执行轮次 |
| `skills` | 否 | 启动时预加载的 skill 内容 |
| `mcpServers` | 否 | 关联的 MCP 服务器（内联定义或引用已配置的） |
| `hooks` | 否 | 生命周期钩子（PreToolUse / PostToolUse / Stop） |
| `memory` | 否 | 持久化记忆范围：`user` / `project` / `local` |
| `initialPrompt` | 否 | 作为主会话 agent 时自动提交的第一条消息 |
| `effort` | 否 | 推理努力程度：`low` / `medium` / `high` / `xhigh` / `max` |
| `isolation` | 否 | 设为 `worktree` 在临时 git worktree 中运行 |
| `background` | 否 | `true` 强制后台运行（v2.1.198 起默认后台） |
| `color` | 否 | 任务列表显示颜色 |

## 调用 Agent 的三种方式

### 1. 自然语言（Claude 自动判断是否委派）

```text
Use the test-runner subagent to fix failing tests
Have the code-reviewer subagent look at my recent changes
```

### 2. @-mention（确保指定 agent 运行）

```text
@"code-reviewer (agent)" look at the auth changes
```

### 3. 会话级（--agent 或 settings.json）

```bash
claude --agent code-reviewer
```

或设为项目默认（`.claude/settings.json`）：

```json
{
  "agent": "code-reviewer"
}
```

## CLI 动态定义（--agents）

不创建文件，临时定义会话内有效的 agent：

```bash
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

`--agents`（复数）接受 JSON，支持与文件 agent 相同的字段，用 `prompt` 代替 markdown body。

## 前台 vs 后台运行

| 模式 | 行为 |
|------|------|
| 前台 | 阻塞主会话直到完成，权限提示实时传递 |
| 后台（v2.1.198 起默认） | 并发运行，权限提示在主会话弹出 |

操作方式：
- 对话中说 "run in the background / foreground"
- `Ctrl+B` 把运行中的任务转到后台

## 常见模式

### 隔离高产出操作

```text
Use a subagent to run the test suite and report only the failing tests
```

### 并行研究

```text
Research the authentication, database, and API modules in parallel using separate subagents
```

### 链式 agent

```text
Use the code-reviewer to find performance issues, then use the optimizer to fix them
```

### 零输入自动执行（initialPrompt）

```markdown
---
name: daily-report
description: Generates a daily code activity report
initialPrompt: /review HEAD~5..HEAD and generate a summary
---

You are a report generator...
```

```bash
claude --agent daily-report
# 启动后自动执行 initialPrompt
```

## 高级特性

### MCP 服务器作用域

```yaml
---
name: browser-tester
description: Tests features in a real browser using Playwright
mcpServers:
  - playwright:
      type: stdio
      command: npx
      args: ["-y", "@playwright/mcp@latest"]
  - github  # 引用已配置的服务器
---
```

### 持久化记忆

```yaml
---
name: code-reviewer
description: Reviews code for quality
memory: project
---
```

| 范围 | 存储位置 | 用途 |
|------|----------|------|
| `user` | `~/.claude/agent-memory/<name>/` | 跨所有项目的学习 |
| `project` | `.claude/agent-memory/<name>/` | 项目专属，可 git 跟踪 |
| `local` | `.claude/agent-memory-local/<name>/` | 项目专属，不入版本控制 |

### 嵌套 subagent

v2.1.172 起支持。subagent 可调度自己的 subagent（最多 5 层深度）。在 `tools` 中省略 `Agent` 可阻止嵌套。

### 禁用特定 agent

```json
{
  "permissions": {
    "deny": ["Agent(Explore)", "Agent(my-custom-agent)"]
  }
}
```

或 CLI：

```bash
claude --disallowedTools "Agent(Explore)"
```

## 内置 Agent

| Agent | 模型 | 用途 |
|-------|------|------|
| Explore | 继承主会话（API 上限 Opus） | 只读代码搜索和分析 |
| Plan | 继承主会话 | Plan mode 下的代码研究 |
| General-purpose | 继承主会话 | 复杂多步任务 |
| statusline-setup | Sonnet | 配置状态栏 |
| claude-code-guide | Haiku | 回答 Claude Code 使用问题 |

内置 agent 可通过环境变量禁用：
- `CLAUDE_CODE_DISABLE_EXPLORE_PLAN_AGENTS=1`（仅禁用 Explore 和 Plan）
- `CLAUDE_AGENT_SDK_DISABLE_BUILTIN_AGENTS=1`（非交互/SDK 中禁用全部内置）

## Fork（分叉会话）

Fork 是继承完整对话历史的特殊 subagent。用 `/fork` 命令启动：

```text
/fork draft unit tests for the parser changes so far
```

与普通 subagent 的区别：

| 维度 | Fork | 普通 subagent |
|------|------|---------------|
| 上下文 | 完整对话历史 | 全新上下文 |
| 系统提示词 | 与主会话相同 | 来自定义文件 |
| Prompt cache | 共享主会话缓存 | 独立缓存 |

设 `CLAUDE_CODE_FORK_SUBAGENT=1` 启用 Claude 主动 fork 能力。

## 参考链接

- [Custom subagents (官方文档)](https://code.claude.com/docs/en/sub-agents)
- [CLI Reference - --agent flag](https://code.claude.com/docs/en/cli-reference)
- [Permission modes](https://code.claude.com/docs/en/permission-modes)
- [Hooks](https://code.claude.com/docs/en/hooks)
- [Agent teams](https://code.claude.com/docs/en/agent-teams)
- [Background agents](https://code.claude.com/docs/en/agent-view)
