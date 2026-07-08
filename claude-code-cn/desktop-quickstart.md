---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】桌面快速开始
description: Claude Code 桌面应用提供图形化界面，支持并行会话、拖拽布局、集成终端、diff 审查、应用预览、PR 监控等功能。本文介绍安装和首次使用的完整流程。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/desktop-quickstart.md
  - en-source/desktop-quickstart.md
---

# 桌面应用快速开始

> 安装 Claude Code 桌面应用并开始你的第一个编程会话

**桌面应用提供 Claude Code 的图形化界面，专为并行会话设计：** 侧边栏管理并行工作、拖拽布局、集成终端和文件编辑器、可视化 diff 审查、实时应用预览、GitHub PR 监控与自动合并、定时任务。无需终端。

### 下载

| 平台 | 链接 |
|------|------|
| macOS | [下载通用版](https://claude.ai/api/desktop/darwin/universal/dmg/latest/redirect?utm_source=claude_code&utm_medium=docs)（支持 Intel 和 Apple Silicon） |
| Windows | [下载 x64 版](https://claude.ai/api/desktop/win32/x64/setup/latest/redirect?utm_source=claude_code&utm_medium=docs) |
| Linux (beta) | [获取 Linux 版](https://code.claude.com/docs/en/desktop-linux)（apt 或 .deb） |

Windows ARM64 用户下载 [ARM64 安装包](https://claude.ai/api/desktop/win32/arm64/setup/latest/redirect?utm_source=claude_code&utm_medium=docs)。Linux 通过 apt 安装，参见 [Claude Desktop on Linux](https://code.claude.com/docs/en/desktop-linux)。

> [!NOTE]
> Claude Code 需要 [Pro、Max、Team 或 Enterprise 订阅](https://claude.com/pricing?utm_source=claude_code&utm_medium=docs&utm_content=desktop_quickstart_pricing)。

本页介绍安装应用和启动第一个会话。如果已经设置好，参见 [使用 Claude Code Desktop](https://code.claude.com/docs/en/desktop) 获取完整参考。

**桌面应用有三个标签页：**

| 标签 | 说明 |
|------|------|
| **Chat** | 通用对话，无文件访问，类似 claude.ai |
| **Cowork** | 自治后台 Agent，在云端 VM 中独立运行任务 |
| **Code** | 交互式编程助手，直接访问本地文件，实时审查和批准每个更改 |

Chat 和 Cowork 在 [Claude Desktop 帮助文章](https://support.claude.com/en/collections/16163169-claude-desktop)中介绍。本页聚焦 **Code** 标签。

## 安装

1. **安装并登录**：macOS 和 Windows 下载上方安装包运行。Linux 按 [Claude Desktop on Linux](https://code.claude.com/docs/en/desktop-linux) 步骤操作。从应用文件夹（macOS）、开始菜单（Windows）或应用启动器（Linux）启动 Claude，使用 Anthropic 账号登录。
2. **打开 Code 标签**：点击顶部中央的 **Code** 标签。如果提示升级，需要先[订阅付费计划](https://claude.com/pricing?utm_source=claude_code&utm_medium=docs&utm_content=desktop_quickstart_upgrade)。如果提示在线登录，完成登录后重启应用。如果看到 403 错误，参见[认证故障排除](https://code.claude.com/docs/en/desktop#403-or-authentication-errors-in-the-code-tab)。

桌面应用自带 Claude Code，不需要单独安装 Node.js 或 CLI。如果要在终端使用 `claude` 命令，需要单独安装 CLI。参见[CLI 快速开始](https://code.claude.com/docs/en/quickstart)。

## 开始第一个会话

Code 标签打开后，选择项目并给 Claude 任务。

### 步骤 1：选择环境和文件夹

选择 **Local** 在本地机器上运行，使用你的文件。点击 **Select folder** 选择项目目录。

> [!TIP]
> 从一个你熟悉的小项目开始。这是了解 Claude Code 能力的最快方式。Windows 上本地会话需要安装 [Git](https://git-scm.com/downloads/win)。大多数 Mac 默认包含 Git。

你也可以选择：

- **Remote**：在 Anthropic 云基础设施上运行，即使关闭应用也继续运行
- **SSH**：通过 SSH 连接远程机器。首次连接时桌面应用自动在远程机器上安装 Claude Code

### 步骤 2：选择模型

从发送按钮旁的下拉菜单选择模型。参见 [models](https://code.claude.com/docs/en/model-config#available-models) 对比可用模型。

### 步骤 3：告诉 Claude 要做什么

输入你想让 Claude 做的事情：

- `Find a TODO comment and fix it`
- `Add tests for the main function`
- `Create a CLAUDE.md with instructions for this codebase`

每个[会话](https://code.claude.com/docs/en/desktop#work-in-parallel-with-sessions)是一个与 Claude 关于你代码的对话。每个会话跟踪自己的上下文和变更，多个任务互不干扰。

### 步骤 4：审查并接受更改

**默认情况下 Code 标签以 [Ask 权限模式](https://code.claude.com/docs/en/desktop#choose-a-permission-mode) 启动**，Claude 提出更改并等待你批准后再应用：

1. [Diff 视图](https://code.claude.com/docs/en/desktop#review-changes-with-diff-view) 显示每个文件的确切更改
2. Accept/Reject 按钮批准或拒绝每个更改
3. Claude 处理请求时实时更新

如果你拒绝更改，Claude 会询问你想如何换一种方式。你的文件在你接受之前不会被修改。

## 接下来做什么

**你已经完成了第一次编辑。** 以下是一些可以尝试的功能：

**中断和引导。** 随时可以重定向 Claude。点击停止按钮立即中断，或输入修正然后按 Enter 发送而不停止正在运行的操作。

**给 Claude 更多上下文。** 在提示框中输入 `@filename` 引入特定文件，用附件按钮附加图片和 PDF，或直接拖拽文件到提示框中。上下文越多结果越好。

**使用 Skills 执行可重复任务。** 输入 `/` 或点击 **+** → **Slash commands** 浏览[内置命令](https://code.claude.com/docs/en/commands)、[自定义 Skills](https://code.claude.com/docs/en/skills) 和插件 Skills。

**提交前审查变更。** Claude 编辑文件后会出现 `+12 -1` 指示器。点击打开 [diff 视图](https://code.claude.com/docs/en/desktop#review-changes-with-diff-view)，逐文件审查修改，对特定行评论。

**调整控制程度。** [权限模式](https://code.claude.com/docs/en/desktop#choose-a-permission-mode)控制平衡。Ask permissions（默认）每次编辑前需要批准。Auto accept edits 自动接受文件编辑加速迭代。Plan mode 让 Claude 规划方案而不动文件。

**添加插件扩展能力。** 点击提示框旁的 **+** 按钮选择 **Plugins** 浏览和安装[插件](https://code.claude.com/docs/en/desktop#install-plugins)。

**安排工作区。** 将 chat、diff、terminal、file 和 preview 面板拖拽成任何布局。用 **Ctrl+\`** 打开终端。

**预览应用。** 点击 **Preview** 下拉在桌面中运行 dev server。Claude 可以查看运行中的应用、测试端点、检查日志并迭代。

**跟踪 PR。** 打开 PR 后，Claude Code 监控 CI 检查结果，可以自动修复失败或在所有检查通过后合并 PR。

**设置定时任务。** 设置[定时任务](https://code.claude.com/docs/en/desktop-scheduled-tasks)让 Claude 定期自动运行：每天早上代码审查、每周依赖审计等。

**准备好后扩展规模。** 从侧边栏打开[并行会话](https://code.claude.com/docs/en/desktop#work-in-parallel-with-sessions)同时处理多个任务。将[长时间任务发送到云端](https://code.claude.com/docs/en/desktop#run-long-running-tasks-remotely)即使关闭应用也能继续。

## 从 CLI 迁移？

桌面应用运行与 CLI 相同的引擎，配有图形界面。你可以在同一项目上同时运行两者，它们共享配置（CLAUDE.md 文件、MCP servers、hooks、skills 和 settings）。完整功能对比参见 [CLI comparison](https://code.claude.com/docs/en/desktop#coming-from-the-cli)。

## 后续步骤

- [使用 Claude Code Desktop](https://code.claude.com/docs/en/desktop)：权限模式、并行会话、diff 视图、连接器和企业配置
- [故障排除](https://code.claude.com/docs/en/desktop#troubleshooting)：常见错误和设置问题的解决方案
- [最佳实践](https://code.claude.com/docs/en/best-practices)：编写有效 prompt 和充分利用 Claude Code 的技巧
- [常见工作流](https://code.claude.com/docs/en/common-workflows)：调试、重构、测试等教程
