---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】Claude Code 概览
description: Claude Code 是一个 AI 编程助手，能读取代码库、编辑文件、执行命令并与开发工具集成。本文介绍了它在终端、IDE、桌面应用和浏览器等多种环境中的安装方式和核心能力。
category: translation
tags: [claude-code, overview, translation]
refs:
  - https://code.claude.com/docs/en/overview.md
---

# Claude Code 概览

> Claude Code 是一个代理式编程工具，能读取你的代码库、编辑文件、执行命令，并与开发工具深度集成。支持终端、IDE、桌面应用和浏览器多种使用方式。

**Claude Code 是一个 AI 编程助手，帮你构建功能、修复 Bug、自动化开发任务。** 它能理解整个代码库，跨文件、跨工具协作完成任务。

## 快速开始

选择你的使用环境即可上手。大多数环境需要 [Claude 订阅](https://claude.com/pricing?utm_source=claude_code&utm_medium=docs&utm_content=overview_pricing) 或 [Anthropic Console](https://console.anthropic.com/) 账号。终端 CLI 和 VS Code 还支持[第三方服务商](https://code.claude.com/docs/en/third-party-integrations)。

### 终端 CLI

**功能最完整的命令行界面，直接在终端中与 Claude Code 交互。** 可编辑文件、执行命令、管理整个项目。

安装方式（推荐原生安装）：

**macOS / Linux / WSL：**

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows PowerShell：**

```powershell
irm https://claude.ai/install.ps1 | iex
```

**Windows CMD：**

```batch
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

> 如果遇到 `The token '&&' is not a valid statement separator` 说明你在 PowerShell 而非 CMD 中；如果遇到 `'irm' is not recognized` 说明你在 CMD 而非 PowerShell 中。PowerShell 提示符为 `PS C:\`，CMD 提示符为 `C:\`（无 PS 前缀）。

也可通过 Homebrew 安装：

```bash
brew install --cask claude-code
```

或 WinGet：

```powershell
winget install Anthropic.ClaudeCode
```

还支持 [apt、dnf、apk](https://code.claude.com/docs/en/setup) 等 Linux 包管理器。

安装后，进入项目目录启动即可：

```bash
cd your-project
claude
```

首次使用会提示登录。详见[快速入门](https://code.claude.com/docs/en/quickstart)。

> 原生安装会自动后台更新；Homebrew 和 WinGet 需手动执行升级命令。

### VS Code

**VS Code 扩展提供行内 diff、@-mentions、计划审查和对话历史功能，直接在编辑器中使用。**

- [安装 VS Code 扩展](vscode:extension/anthropic.claude-code)
- [安装 Cursor 扩展](cursor:extension/anthropic.claude-code)

或在扩展视图中搜索 "Claude Code"（Mac: `Cmd+Shift+X`，Windows/Linux: `Ctrl+Shift+X`）。安装后打开命令面板，搜索 "Claude Code" 并选择 **Open in New Tab**。

详见 [VS Code 指南](https://code.claude.com/docs/en/vs-code)。

### 桌面应用

**独立桌面应用，适合在 IDE 和终端之外使用。** 可视化审查 diff、并行运行多个会话、设置定时任务、启动云端会话。

下载：
- [macOS](https://claude.ai/api/desktop/darwin/universal/dmg/latest/redirect?utm_source=claude_code&utm_medium=docs)（Intel 和 Apple Silicon）
- [Windows x64](https://claude.ai/api/desktop/win32/x64/setup/latest/redirect?utm_source=claude_code&utm_medium=docs)
- [Windows ARM64](https://claude.ai/api/desktop/win32/arm64/setup/latest/redirect?utm_source=claude_code&utm_medium=docs)

安装后登录，点击 **Code** 标签页即可开始。需要[付费订阅](https://claude.com/pricing?utm_source=claude_code&utm_medium=docs&utm_content=overview_desktop_pricing)。

详见[桌面应用指南](https://code.claude.com/docs/en/desktop-quickstart)。

### Web 端

**在浏览器中运行 Claude Code，无需本地安装。** 适合启动长时间任务后稍后查看结果、操作本地没有的仓库、并行执行多个任务。支持桌面浏览器和 Claude iOS App。

访问 [claude.ai/code](https://claude.ai/code) 开始。

详见 [Web 端指南](https://code.claude.com/docs/en/web-quickstart)。

### JetBrains

**支持 IntelliJ IDEA、PyCharm、WebStorm 等 JetBrains 系列 IDE 的插件，** 提供交互式 diff 查看和选区上下文共享。

从 [JetBrains Marketplace](https://plugins.jetbrains.com/plugin/27310-claude-code-beta-) 安装 Claude Code 插件并重启 IDE。插件依赖单独安装的 Claude Code CLI。

详见 [JetBrains 指南](https://code.claude.com/docs/en/jetbrains)。

## 核心能力

**Claude Code 覆盖从日常杂务到复杂开发的完整工作流。**

### 自动化那些你一直拖着没做的事

处理那些消耗大量时间的繁琐任务：为未覆盖的代码写测试、批量修复 lint 错误、解决合并冲突、更新依赖、撰写 release notes。

```bash
claude "write tests for the auth module, run them, and fix any failures"
```

### 构建功能和修复 Bug

用自然语言描述需求，Claude Code 会规划方案、跨多文件编写代码并验证其正确性。

对于 Bug，粘贴错误信息或描述症状即可。Claude Code 会在代码库中追踪问题根因并实现修复。详见[常用工作流](https://code.claude.com/docs/en/common-workflows)。

### 创建 Commit 和 Pull Request

直接操作 git：暂存变更、编写 commit message、创建分支、打开 PR。

```bash
claude "commit my changes with a descriptive message"
```

在 CI 中，可通过 [GitHub Actions](https://code.claude.com/docs/en/github-actions) 或 [GitLab CI/CD](https://code.claude.com/docs/en/gitlab-ci-cd) 自动化代码审查和 issue 分类。

### 通过 MCP 连接外部工具

[Model Context Protocol (MCP)](https://code.claude.com/docs/en/mcp) 是一个连接 AI 工具与外部数据源的开放标准。通过 MCP，Claude Code 可以读取 Google Drive 中的设计文档、更新 Jira ticket、从 Slack 拉取数据，或使用你自定义的工具。详见 [MCP 快速入门](https://code.claude.com/docs/en/mcp-quickstart)。

### 通过指令、技能和 Hook 定制行为

[`CLAUDE.md`](https://code.claude.com/docs/en/memory) 是放在项目根目录的 Markdown 文件，Claude Code 在每次会话开始时读取。用它来设定编码规范、架构决策、偏好的库和审查清单。Claude 还会在工作中构建[自动记忆](https://code.claude.com/docs/en/memory#auto-memory)，将构建命令、调试经验等知识跨会话保存。

[技能（Skills）](https://code.claude.com/docs/en/skills)可以将可复用的工作流打包为团队共享的命令，如 `/review-pr` 或 `/deploy-staging`。

[Hook](https://code.claude.com/docs/en/hooks) 允许在 Claude Code 操作前后执行 shell 命令，如每次编辑文件后自动格式化，或 commit 前运行 lint。

### 运行多 Agent 团队和构建自定义 Agent

可以派生[多个 Claude Code Agent](https://code.claude.com/docs/en/sub-agents) 同时处理不同子任务，由主 Agent 协调、分配任务并合并结果。

如果需要并行运行多个完整会话并在同一界面监控，可使用[后台 Agent](https://code.claude.com/docs/en/agent-view)。对于完全自定义的工作流，[Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) 可以构建由 Claude Code 工具和能力驱动的自定义 Agent，完全控制编排、工具访问和权限。

### 管道、脚本和自动化

Claude Code 可组合使用，遵循 Unix 哲学。可以将日志管道输入、在 CI 中运行、或与其他工具串联：

```bash
# 分析最近的日志输出
tail -200 app.log | claude -p "Slack me if you see any anomalies"

# 在 CI 中自动化翻译
claude -p "translate new strings into French and raise a PR for review"

# 跨文件批量操作
git diff main --name-only | claude -p "review these changed files for security issues"
```

详见 [CLI 参考](https://code.claude.com/docs/en/cli-reference)。

### 定时执行重复任务

按计划运行 Claude 来自动化重复性工作：晨间 PR 审查、overnight CI 失败分析、每周依赖审计、PR 合并后同步文档。

- [Routines](https://code.claude.com/docs/en/routines)：在 Anthropic 托管的基础设施上运行，电脑关机也能执行，还可通过 API 调用或 GitHub 事件触发
- [桌面定时任务](https://code.claude.com/docs/en/desktop-scheduled-tasks)：在本地机器上运行，可直接访问本地文件和工具
- [`/loop`](https://code.claude.com/docs/en/scheduled-tasks)：在 CLI 会话中重复执行 prompt，适合快速轮询

### 随时随地工作

会话不绑定单一环境，可以在不同环境间无缝切换：

- 用 [Remote Control](https://code.claude.com/docs/en/remote-control) 从手机或任何浏览器继续工作
- 从手机向 [Dispatch](https://code.claude.com/docs/en/desktop#sessions-from-dispatch) 发送任务，在桌面应用中打开创建的会话
- 在 [Web 端](https://code.claude.com/docs/en/claude-code-on-the-web) 或 iOS App 启动长任务，然后用 `claude --teleport` 拉到终端继续
- 用 `/desktop` 将终端会话移交给[桌面应用](https://code.claude.com/docs/en/desktop)做可视化 diff 审查
- 在 [Slack](https://code.claude.com/docs/en/slack) 中 @Claude 提交 Bug 报告，拿回一个 PR

## 全平台使用

**各个平台连接到同一个 Claude Code 引擎，CLAUDE.md 文件、设置和 MCP 服务器在所有环境中通用。**

除了上面提到的[终端](https://code.claude.com/docs/en/quickstart)、[VS Code](https://code.claude.com/docs/en/vs-code)、[JetBrains](https://code.claude.com/docs/en/jetbrains)、[桌面应用](https://code.claude.com/docs/en/desktop)和 [Web 端](https://code.claude.com/docs/en/claude-code-on-the-web)，Claude Code 还集成了 CI/CD、聊天和浏览器工作流：

| 使用场景 | 推荐方案 |
|---------|---------|
| 从手机或其他设备继续本地会话 | [Remote Control](https://code.claude.com/docs/en/remote-control) |
| 从 Telegram、Discord、iMessage 或自定义 Webhook 推送事件到会话 | [Channels](https://code.claude.com/docs/en/channels) |
| 本地启动任务，移动端继续 | [Web 端](https://code.claude.com/docs/en/claude-code-on-the-web) 或 Claude iOS App |
| 按计划定时运行 | [Routines](https://code.claude.com/docs/en/routines) 或[桌面定时任务](https://code.claude.com/docs/en/desktop-scheduled-tasks) |
| 自动化 PR 审查和 Issue 分类 | [GitHub Actions](https://code.claude.com/docs/en/github-actions) 或 [GitLab CI/CD](https://code.claude.com/docs/en/gitlab-ci-cd) |
| 每个 PR 自动代码审查 | [GitHub Code Review](https://code.claude.com/docs/en/code-review) |
| 从 Slack 中的 Bug 报告自动生成 PR | [Slack](https://code.claude.com/docs/en/slack) |
| 调试线上 Web 应用 | [Chrome](https://code.claude.com/docs/en/chrome) |
| 为自定义工作流构建 Agent | [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) |

## 下一步

安装完成后，以下指南帮你进一步深入：

- [快速入门](https://code.claude.com/docs/en/quickstart)：从探索代码库到提交修复的完整演练
- [指令和记忆](https://code.claude.com/docs/en/memory)：通过 CLAUDE.md 和自动记忆给 Claude 持久化指令
- [常用工作流](https://code.claude.com/docs/en/common-workflows) 和 [最佳实践](https://code.claude.com/docs/en/best-practices)：充分发挥 Claude Code 的使用模式
- [设置](https://code.claude.com/docs/en/settings)：按你的工作流定制 Claude Code
- [故障排除](https://code.claude.com/docs/en/troubleshooting)：常见问题解决方案
- [code.claude.com](https://code.claude.com/)：演示、定价和产品详情
