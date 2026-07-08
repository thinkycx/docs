---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】.claude 目录
description: 详解 Claude Code 在项目 .claude/ 目录和用户 ~/.claude/ 目录中读取的所有文件：CLAUDE.md、settings.json、hooks、skills、commands、subagents、workflows、rules 和自动记忆。
category: translation
tags: [claude-code, claude-directory, translation]
refs:
  - https://code.claude.com/docs/en/claude-directory.md
  - en-source/claude-directory.md
---

# 探索 .claude 目录

**Claude Code 从项目 `.claude/` 和用户 `~/.claude/` 目录中读取配置、规则和扩展。** 本页完整列出每个文件的作用、加载时机和示例。

> 注：原文是一个交互式 React 组件（文件树浏览器）。本译文以结构化表格呈现同等信息。

## 项目级文件

### 项目根目录

| 文件 | 标记 | 用途 | 加载时机 |
|------|------|------|---------|
| `CLAUDE.md` | committed | 项目指令，Claude 每个会话读取 | 每个会话开始时加载 |
| `.mcp.json` | committed | 项目级 MCP 服务器配置 | 会话开始时连接 |
| `.worktreeinclude` | committed | 列出 gitignored 文件以复制到新 worktree | 创建 worktree 时读取 |

**CLAUDE.md 提示：**
- 目标 200 行以内
- 列出最常用命令（build、test、format）
- 也可放在 `.claude/CLAUDE.md`
- 用 `/memory` 在会话中编辑

### .claude/ 目录

| 文件/目录 | 标记 | 用途 | 加载时机 |
|-----------|------|------|---------|
| `settings.json` | committed | 权限、hooks、配置 | 覆盖全局设置 |
| `settings.local.json` | gitignored | 个人设置覆盖 | 最高优先级的用户可编辑设置 |
| `rules/` | committed | 按主题拆分的指令文件 | 无 `paths:` 的在启动时加载；有 `paths:` 的按需加载 |
| `skills/` | committed | 可复用 prompt，按名称调用 | 用 `/skill-name` 调用或 Claude 自动匹配 |
| `commands/` | committed | 单文件 prompt（现推荐用 skills） | 用 `/command-name` 调用 |
| `output-styles/` | committed | 项目级输出样式 | 通过 `outputStyle` 设置选择时应用 |
| `agents/` | committed | 专用 subagent，有自己的上下文窗口 | 你或 Claude 调用时运行 |
| `workflows/` | committed | 动态工作流脚本 | 启动时加载，成为 `/<name>` 命令 |
| `agent-memory/` | committed | Subagent 持久记忆 | subagent 启动时加载 MEMORY.md |

### settings.json 示例

```json
{
  "permissions": {
    "allow": ["Bash(npm test *)", "Bash(npm run *)"],
    "deny": ["Bash(rm -rf *)"]
  },
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write"
      }]
    }]
  }
}
```

### rules/ 示例

```markdown
---
paths:
  - "**/*.test.ts"
  - "**/*.test.tsx"
---

# Testing Rules

- Use descriptive test names: "should [expected] when [condition]"
- Mock external dependencies, not internal modules
- Clean up side effects in afterEach
```

### skills/ 示例

```markdown
---
description: Reviews code changes for security vulnerabilities
disable-model-invocation: true
argument-hint: <branch-or-path>
---

## Diff to review

!`git diff $ARGUMENTS`

Audit the changes above for:
1. Injection vulnerabilities (SQL, XSS, command)
2. Authentication and authorization gaps
3. Hardcoded secrets or credentials

Use checklist.md in this skill directory for the full review checklist.
```

### agents/ 示例

```markdown
---
name: code-reviewer
description: Reviews code for correctness, security, and maintainability
tools: Read, Grep, Glob
---

You are a senior code reviewer. Review for:
1. Correctness: logic errors, edge cases, null handling
2. Security: injection, auth bypass, data exposure
3. Maintainability: naming, complexity, duplication

Every finding must include a concrete fix.
```

## 用户级文件（~/）

### ~/.claude.json

**应用状态和 UI 偏好。** 持有主题、OAuth 会话、项目信任决策、个人 MCP 服务器。主要通过 `/config` 管理。

### ~/.claude/ 目录

| 文件/目录 | 用途 | 加载时机 |
|-----------|------|---------|
| `CLAUDE.md` | 跨所有项目的个人偏好 | 每个会话开始时加载 |
| `settings.json` | 所有项目的默认设置 | 作为默认值；项目设置覆盖 |
| `keybindings.json` | 自定义键盘快捷键 | 启动时读取，编辑后热重载 |
| `themes/` | 自定义颜色主题 | 启动时读取，文件变更时热重载 |
| `rules/` | 适用于每个项目的用户级规则 | 同项目 rules |
| `skills/` | 每个项目可用的个人技能 | 在任何项目中用 `/skill-name` 调用 |
| `commands/` | 每个项目可用的个人命令 | 在任何项目中用 `/command-name` 调用 |
| `output-styles/` | 自定义系统 prompt 部分 | 通过 `outputStyle` 设置选择 |
| `agents/` | 每个项目可用的个人 subagent | Claude 委派或你 @-mention |
| `workflows/` | 每个项目可用的动态工作流 | 启动时加载 |
| `agent-memory/` | `memory: user` 的 subagent 跨项目记忆 | subagent 启动时加载 |
| `projects/` | 自动记忆——Claude 按项目的自我笔记 | MEMORY.md 每会话加载；话题文件按需读取 |

### 全局 CLAUDE.md 示例

```markdown
# Global preferences

- Keep explanations concise
- Use conventional commit format
- Show the terminal command to verify changes
- Prefer composition over inheritance
```

### output-styles/ 示例

```markdown
---
description: Explains reasoning and asks you to implement small pieces
keep-coding-instructions: true
---

After completing each task, add a brief "Why this approach" note
explaining the key design decision.

When a change is under 10 lines, ask the user to implement it
themselves by leaving a TODO(human) marker instead of writing it.
```

### 自动记忆（projects/）

Claude 跨会话积累知识。每个项目获得独立记忆目录。

- **MEMORY.md**：索引文件，每会话前 200 行（或 25KB）加载
- **话题文件**（如 `debugging.md`）：按需读取，不在启动时加载
- 默认开启，用 `/memory` 或 `autoMemoryEnabled` 设置切换

## 文件标记说明

| 标记 | 含义 |
|------|------|
| committed | 提交到版本控制，与团队共享 |
| gitignored | 不提交，个人覆盖 |
| local only | 仅在你机器上，从不提交 |
| Claude writes | Claude 自动写入和维护 |

## 相关链接

- [Memory](https://code.claude.com/docs/en/memory) — CLAUDE.md 和项目记忆详解
- [Settings](https://code.claude.com/docs/en/settings) — 所有设置键
- [Skills](https://code.claude.com/docs/en/skills) — 技能和命令
- [Sub-agents](https://code.claude.com/docs/en/sub-agents) — subagent 定义和记忆
- [Hooks](https://code.claude.com/docs/en/hooks) — hook 配置
- [Output styles](https://code.claude.com/docs/en/output-styles) — 自定义输出样式
