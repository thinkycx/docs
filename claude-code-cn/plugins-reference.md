---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】插件参考
description: Claude Code 插件系统完整技术参考，包含组件 schema（skills、agents、hooks、MCP、LSP、monitors、themes）、CLI 命令、安装作用域、目录结构和环境变量。
category: translation
tags: [claude-code, plugins-reference, translation]
refs:
  - https://code.claude.com/docs/en/plugins-reference.md
  - en-source/plugins-reference.md
---

# 插件参考

**Claude Code 插件系统的完整技术规范，包含组件 schema、CLI 命令和开发工具。**

> 安装插件见 [Discover and install plugins](https://code.claude.com/docs/en/discover-plugins)。创建插件见 [Plugins](https://code.claude.com/docs/en/plugins)。分发插件见 [Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)。

**插件**是一个自包含目录，用自定义功能扩展 Claude Code。组件包括 skills、agents、hooks、MCP 服务器、LSP 服务器和 monitors。

## 插件组件参考

### Skills

**位置：** `skills/` 或 `commands/` 目录，或插件根目录的单个 `SKILL.md`

Skills 是含 `SKILL.md` 的目录；commands 是简单 markdown 文件。安装后自动发现，Claude 可根据任务上下文自动调用。

### Agents

**位置：** `agents/` 目录

Markdown 文件描述 agent 能力。支持 `name`、`description`、`model`、`effort`、`maxTurns`、`tools`、`disallowedTools`、`skills`、`memory`、`background`、`isolation` frontmatter 字段。安全原因不支持 `hooks`、`mcpServers`、`permissionMode`。

### Hooks

**位置：** `hooks/hooks.json` 或内联在 plugin.json

响应 Claude Code 生命周期事件。支持的事件：

| 事件 | 触发时机 |
|------|---------|
| `SessionStart` | 会话开始或恢复 |
| `UserPromptSubmit` | 提交 prompt 前 |
| `PreToolUse` | 工具调用执行前（可阻止） |
| `PostToolUse` | 工具调用成功后 |
| `Stop` | Claude 完成响应 |
| `SubagentStart`/`SubagentStop` | subagent 生命周期 |
| `FileChanged` | 监视的文件磁盘变更 |
| `ConfigChange` | 会话中配置文件变更 |
| `PreCompact`/`PostCompact` | 上下文压缩前后 |

Hook 类型：`command`、`http`、`mcp_tool`、`prompt`、`agent`

### MCP 服务器

**位置：** `.mcp.json` 或内联在 plugin.json

插件启用时自动启动。用 `${CLAUDE_PLUGIN_ROOT}` 引用插件安装目录中的文件。

### LSP 服务器

**位置：** `.lsp.json` 或内联在 plugin.json

提供实时代码智能：即时诊断、代码导航、类型信息。

必填字段：`command`、`extensionToLanguage`

可用 LSP 插件：

| 插件 | 语言服务器 | 安装命令 |
|------|-----------|---------|
| `pyright-lsp` | Pyright (Python) | `pip install pyright` |
| `typescript-lsp` | TypeScript LS | `npm install -g typescript-language-server typescript` |
| `rust-analyzer-lsp` | rust-analyzer | 见官方安装文档 |

### Monitors

**位置：** `monitors/monitors.json` 或内联在 plugin.json

后台监视器，Claude Code 在插件活跃时自动启动。每个 stdout 行作为通知传递给 Claude。需 v2.1.105+。

| 字段 | 描述 |
|------|------|
| `name` | 插件内唯一标识符 |
| `command` | 作为持久后台进程运行的 shell 命令 |
| `description` | 监视内容的短摘要 |
| `when` | 可选。`"always"`（默认）或 `"on-skill-invoke:<skill-name>"` |

### Themes

**位置：** `themes/` 目录

颜色主题，出现在 `/theme` 中。含 `base` 预设和 `overrides` 颜色 token 映射。

## 安装作用域

| 作用域 | 设置文件 | 用例 |
|--------|---------|------|
| `user` | `~/.claude/settings.json` | 跨所有项目的个人插件（默认） |
| `project` | `.claude/settings.json` | 通过版本控制共享的团队插件 |
| `local` | `.claude/settings.local.json` | 项目特定、gitignored |
| `managed` | 管理设置 | 只读，仅更新 |

## Skills 目录插件

`~/.claude/skills/` 或 `<cwd>/.claude/skills/` 下含 `.claude-plugin/plugin.json` 的文件夹自动作为 `<name>@skills-dir` 加载，无需市场和安装步骤。

用 `claude plugin init <name>` 脚手架。

## plugin.json Schema

### 必填字段

仅 `name`（kebab-case）。

### 元数据字段

| 字段 | 描述 |
|------|------|
| `name` | 唯一标识符 |
| `displayName` | UI 显示名（v2.1.143+） |
| `version` | 语义版本。设置则锁定；省略则用 git SHA |
| `description` | 简述 |
| `author` | 作者信息 |
| `defaultEnabled` | 安装后是否默认启用（v2.1.154+） |
| `dependencies` | 依赖的其他插件 |

### 组件路径字段

| 字段 | 替换还是扩展默认 |
|------|----------------|
| `skills` | 扩展（添加到默认 `skills/` 扫描） |
| `commands` | 替换 |
| `agents` | 替换 |
| `hooks` | 自有合并规则 |
| `mcpServers` | 自有合并规则 |
| `lspServers` | 自有合并规则 |
| `outputStyles` | 替换 |

### 环境变量

| 变量 | 描述 |
|------|------|
| `${CLAUDE_PLUGIN_ROOT}` | 插件安装目录绝对路径。更新时变化 |
| `${CLAUDE_PLUGIN_DATA}` | 持久数据目录，跨更新存活 |
| `${CLAUDE_PROJECT_DIR}` | 项目根目录 |

### User Configuration

```json
{
  "userConfig": {
    "api_endpoint": {
      "type": "string",
      "title": "API endpoint",
      "description": "Your team's API endpoint"
    },
    "api_token": {
      "type": "string",
      "title": "API token",
      "sensitive": true
    }
  }
}
```

值可用 `${user_config.KEY}` 在 MCP/LSP 配置、hook 命令和 monitor 命令中替换。

## 插件目录结构

```text
enterprise-plugin/
├── .claude-plugin/plugin.json   # 清单（可选）
├── skills/                      # Skills
├── commands/                    # 扁平 .md 技能
├── agents/                      # Subagent 定义
├── output-styles/               # 输出样式
├── themes/                      # 颜色主题
├── monitors/monitors.json       # 后台监视器
├── hooks/hooks.json             # Hook 配置
├── bin/                         # 添加到 PATH 的可执行文件
├── settings.json                # 插件默认设置
├── .mcp.json                    # MCP 服务器
├── .lsp.json                    # LSP 服务器
└── scripts/                     # Hook 和工具脚本
```

## CLI 命令参考

### plugin init

```bash
claude plugin init <name> [--with skills,agents,hooks,mcp,lsp,output-style,channel]
```

脚手架新插件到 `~/.claude/skills/<name>/`。

### plugin install

```bash
claude plugin install <plugin> [-s user|project|local]
```

### plugin uninstall

```bash
claude plugin uninstall <plugin> [--prune] [--keep-data]
```

### plugin enable / disable

```bash
claude plugin enable <plugin> [--scope <scope>]
claude plugin disable <plugin> [--scope <scope>]
```

### plugin list

```bash
claude plugin list [--json]
```

### plugin update

```bash
claude plugin update [plugin]
```

### plugin validate

```bash
claude plugin validate <path> [--strict]
```

### plugin tag

```bash
claude plugin tag [--push] [--dry-run]
```

### plugin prune

```bash
claude plugin prune [--scope <scope>] [--dry-run] [-y]
```

## 缓存和文件解析

插件安装后复制到 `~/.claude/plugins/cache`。每个版本独立目录。更新后旧版本 7 天后自动清理。

**路径遍历限制：** 安装的插件不能引用目录外的文件。需要跨插件共享文件时使用符号链接。

## 另见

- [Plugins](https://code.claude.com/docs/en/plugins) — 创建插件
- [Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces) — 分发插件
- [Plugin dependencies](https://code.claude.com/docs/en/plugin-dependencies) — 版本约束
- [Discover plugins](https://code.claude.com/docs/en/discover-plugins) — 安装插件
- [Skills](https://code.claude.com/docs/en/skills) — 技能详解
- [Sub-agents](https://code.claude.com/docs/en/sub-agents) — subagent 详解
