---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】Claude Code 快速开始
description: Claude Code 快速上手指南，涵盖安装、登录、首次对话、代码修改、Git 操作等核心工作流，帮助开发者在几分钟内掌握 AI 辅助编码的基本用法。
category: translation
tags: [claude-code, quickstart, translation]
refs:
  - https://code.claude.com/docs/en/quickstart.md
---

# Claude Code 快速开始

> 欢迎使用 Claude Code！

**这篇指南带你在几分钟内跑通 Claude Code 的核心工作流。** 读完后你会掌握如何用 Claude Code 完成日常开发中的常见任务。

## 前置条件

**开始之前，确认你已具备以下环境。**

| 条件 | 说明 |
|------|------|
| 终端 / 命令行 | 如果从未用过终端，参考 [终端入门指南](https://code.claude.com/docs/en/terminal-guide) |
| 一个代码项目 | 任何现有项目目录即可 |
| Claude 账号 | [Claude 订阅](https://claude.com/pricing?utm_source=claude_code&utm_medium=docs&utm_content=quickstart_prereq)（Pro / Max / Team / Enterprise）、[Claude Console](https://console.anthropic.com/) 账号，或通过[支持的云厂商](https://code.claude.com/docs/en/third-party-integrations)接入 |

> **注意：** 本指南针对终端 CLI。Claude Code 同样可以在 [Web](https://claude.ai/code)、[桌面客户端](https://code.claude.com/docs/en/desktop)、[VS Code](https://code.claude.com/docs/en/vs-code)、[JetBrains IDE](https://code.claude.com/docs/en/jetbrains)、[Slack](https://code.claude.com/docs/en/slack) 以及 CI/CD 环境（[GitHub Actions](https://code.claude.com/docs/en/github-actions)、[GitLab CI/CD](https://code.claude.com/docs/en/gitlab-ci-cd)）中使用。完整列表见 [所有接入方式](https://code.claude.com/docs/en/overview#use-claude-code-everywhere)。

## 第一步：安装 Claude Code

**根据你的系统选择安装方式。**

### 原生安装（推荐）

macOS / Linux / WSL：

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Windows PowerShell：

```powershell
irm https://claude.ai/install.ps1 | iex
```

Windows CMD：

```batch
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

常见报错排查：
- 看到 `The token '&&' is not a valid statement separator` — 说明你在 PowerShell 里执行了 CMD 命令。PowerShell 提示符以 `PS C:\` 开头，CMD 提示符只有 `C:\`。
- 看到 `'irm' is not recognized` — 说明你在 CMD 里执行了 PowerShell 命令。
- 如果安装脚本报 `syntax error near unexpected token '<'`、`403` 或其他 curl 错误，参考 [安装排错指南](https://code.claude.com/docs/en/troubleshoot-install#find-your-error)。

Windows 原生环境建议安装 [Git for Windows](https://git-scm.com/downloads/win)，Claude Code 可以使用其提供的 Bash 工具。未安装时会回退到 PowerShell。WSL 环境不需要额外安装。

> 原生安装会在后台自动更新，始终保持最新版本。

### Homebrew

```bash
brew install --cask claude-code
```

Homebrew 提供两个 cask：`claude-code` 跟踪稳定通道（通常落后约一周，跳过有严重回退的版本），`claude-code@latest` 跟踪最新通道。

> Homebrew 安装不会自动更新。运行 `brew upgrade claude-code` 或 `brew upgrade claude-code@latest` 手动升级。

### WinGet

```powershell
winget install Anthropic.ClaudeCode
```

> WinGet 安装不会自动更新。定期运行 `winget upgrade Anthropic.ClaudeCode` 获取最新版。

此外也支持通过 [apt / dnf / apk](https://code.claude.com/docs/en/setup#install-with-linux-package-managers) 在 Debian、Fedora、RHEL、Alpine 上安装。

## 第二步：登录账号

**首次启动时需要登录，之后凭据会被保存。**

在终端中运行：

```bash
claude
```

首次启动会提示在浏览器中完成认证。如果后续需要切换账号或重新登录，在会话内输入：

```text
/login
```

支持的账号类型：

| 账号类型 | 说明 |
|----------|------|
| [Claude Pro / Max / Team / Enterprise](https://claude.com/pricing?utm_source=claude_code&utm_medium=docs&utm_content=quickstart_login) | 推荐方式 |
| [Claude Console](https://console.anthropic.com/) | API 访问（预充值额度）。首次登录会自动在 Console 中创建 "Claude Code" workspace 用于集中追踪费用 |
| [Amazon Bedrock / Google Vertex AI / Microsoft Foundry](https://code.claude.com/docs/en/third-party-integrations) | 企业级云厂商接入 |

登录完成后凭据会存储在本地，无需再次登录。

## 第三步：启动第一个会话

**进入项目目录，输入 `claude` 即可开始。**

```bash
cd /path/to/your/project
claude
```

启动后会看到 Claude Code 提示符，上方显示版本号、当前模型和工作目录。输入 `/help` 查看可用命令，输入 `/resume` 继续上一次对话。

> **提示：** 登录后凭据会保存在系统中，详情参考 [凭据管理](https://code.claude.com/docs/en/authentication#credential-management)。

## 第四步：问出第一个问题

**从了解代码库入手是最好的起点。**

```text
what does this project do?
```

Claude 会分析项目文件并给出概要。也可以问更具体的问题：

```text
what technologies does this project use?
```

```text
where is the main entry point?
```

```text
explain the folder structure
```

你还可以询问 Claude Code 自身的能力：

```text
what can Claude Code do?
```

```text
how do I create custom skills in Claude Code?
```

```text
can Claude Code work with Docker?
```

> Claude Code 会按需自动读取项目文件，你不需要手动添加上下文。

## 第五步：做出第一次代码修改

**让 Claude 动手改代码，体验完整的编辑流程。**

```text
add a hello world function to the main file
```

Claude Code 会执行以下步骤：

1. 找到合适的文件
2. 展示修改方案
3. 等待你确认
4. 执行修改

> Claude Code 在修改文件前始终会请求你的许可。你可以逐条批准，也可以为当前会话开启 "Accept all" 模式。

## 第六步：用 Claude Code 操作 Git

**把 Git 操作变成自然语言对话。**

```text
what files have I changed?
```

```text
commit my changes with a descriptive message
```

更复杂的 Git 操作也能处理：

```text
create a new branch called feature/quickstart
```

```text
show me the last 5 commits
```

```text
help me resolve merge conflicts
```

## 第七步：修 Bug 或加功能

**用自然语言描述需求，Claude 负责定位代码、理解上下文、实现方案。**

添加功能：

```text
add input validation to the user registration form
```

修复问题：

```text
there's a bug where users can submit empty forms - fix it
```

Claude Code 的执行过程：
- 定位相关代码
- 理解上下文
- 实现修复方案
- 如果有测试则运行测试

## 第八步：更多常见工作流

**Claude Code 能覆盖绝大多数日常开发场景。**

重构代码：

```text
refactor the authentication module to use async/await instead of callbacks
```

编写测试：

```text
write unit tests for the calculator functions
```

更新文档：

```text
update the README with installation instructions
```

代码审查：

```text
review my changes and suggest improvements
```

> 像跟同事说话一样跟 Claude 对话。描述你想达成什么目标，它会帮你实现。

## 核心命令速查

**日常使用最常打交道的命令分两类：终端命令和会话内命令。**

### 终端命令（启动前）

| 命令 | 作用 | 示例 |
|------|------|------|
| `claude` | 启动交互模式 | `claude` |
| `claude "task"` | 执行一次性任务 | `claude "fix the build error"` |
| `claude -p "query"` | 单次查询后退出 | `claude -p "explain this function"` |
| `claude -c` | 继续当前目录最近的对话 | `claude -c` |
| `claude -r` | 恢复之前的对话 | `claude -r` |

### 会话内命令（启动后）

| 命令 | 作用 |
|------|------|
| `/clear` | 清除对话历史 |
| `/help` | 显示可用命令 |
| `/exit` 或 Ctrl+D | 退出 Claude Code |

完整的终端命令列表见 [CLI 参考](https://code.claude.com/docs/en/cli-reference)，会话内命令列表见 [命令参考](https://code.claude.com/docs/en/commands)。

## 新手进阶技巧

**几个小习惯能显著提升 Claude Code 的输出质量。**

### 尽量具体

不要说："fix the bug"

改为："fix the login bug where users see a blank screen after entering wrong credentials"

### 拆解复杂任务

把大需求分步骤描述：

```text
1. create a new database table for user profiles
2. create an API endpoint to get and update user profiles
3. build a webpage that allows users to see and edit their information
```

### 先让 Claude 探索

改代码之前，先让它理解现有结构：

```text
analyze the database schema
```

```text
build a dashboard showing products that are most frequently returned by our UK customers
```

### 善用快捷键

| 快捷键 | 作用 |
|--------|------|
| `/` | 查看所有命令和 skill |
| Tab | 命令补全 |
| ↑ | 历史命令 |
| Shift+Tab | 切换权限模式 |

更多最佳实践见 [最佳实践](https://code.claude.com/docs/en/best-practices) 和 [常见工作流](https://code.claude.com/docs/en/common-workflows)。

## 下一步

**掌握基础后，可以继续探索进阶功能。**

| 主题 | 说明 | 链接 |
|------|------|------|
| Claude Code 工作原理 | 理解 Agent 循环、内置工具及项目交互方式 | [查看](https://code.claude.com/docs/en/how-claude-code-works) |
| 最佳实践 | 通过更有效的 Prompt 和项目配置获得更好的结果 | [查看](https://code.claude.com/docs/en/best-practices) |
| 常见工作流 | 常见任务的分步指南 | [查看](https://code.claude.com/docs/en/common-workflows) |
| 扩展 Claude Code | 通过 CLAUDE.md、skill、hook、MCP 等自定义行为 | [查看](https://code.claude.com/docs/en/features-overview) |

## 获取帮助

- **在 Claude Code 中**：输入 `/help` 或直接问 "how do I..."
- **文档站**：浏览本系列其他指南
- **社区**：加入 [Discord](https://www.anthropic.com/discord) 获取技巧和支持
