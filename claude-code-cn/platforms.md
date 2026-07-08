---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】平台总览
description: 选择在哪里运行 Claude Code 以及连接哪些工具。对比 CLI、Desktop、VS Code、JetBrains、Web、移动端和 Chrome/Slack/CI 等集成方式。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/platforms.md
  - en-source/platforms.md
---

# 平台与集成

> 选择在哪里运行 Claude Code，以及连接哪些工具。对比 CLI、Desktop、VS Code、JetBrains、Web、Mobile 和集成。

**Claude Code 在所有地方运行相同的底层引擎，但每个界面针对不同的工作方式进行了调整。** 本页帮你选择适合工作流的平台并连接你已有的工具。

## 在哪里运行 Claude Code

**根据你的工作习惯和项目所在位置选择平台：**

| 平台 | 最适合 | 你将获得 |
| :--- | :--- | :--- |
| [CLI](https://code.claude.com/docs/en/quickstart) | 终端工作流、脚本、远程服务器 | 完整功能集、[Agent SDK](https://code.claude.com/docs/en/headless)、macOS 上的 [computer use](https://code.claude.com/docs/en/computer-use)（Pro/Max）、第三方提供商 |
| [Desktop](https://code.claude.com/docs/en/desktop) | 可视化审查、并行会话、托管安装 | Diff 查看器、应用预览、Pro/Max 上的 [computer use](https://code.claude.com/docs/en/desktop#let-claude-use-your-computer) 和 [Dispatch](https://code.claude.com/docs/en/desktop#sessions-from-dispatch) |
| [VS Code](https://code.claude.com/docs/en/vs-code) | 在 VS Code 内工作无需切换到终端 | 内联 diff、集成终端、文件上下文 |
| [JetBrains](https://code.claude.com/docs/en/jetbrains) | 在 IntelliJ、PyCharm、WebStorm 等 JetBrains IDE 内工作 | Diff 查看器、选中内容共享、终端会话 |
| [Web](https://code.claude.com/docs/en/claude-code-on-the-web) | 不需要太多引导的长时间任务，或断开连接后应继续的工作 | Anthropic 托管的云环境，断开后继续运行 |
| Mobile | 离开电脑时启动和监控任务 | Claude iOS/Android 应用的云会话、本地会话的 [Remote Control](https://code.claude.com/docs/en/remote-control)、Pro/Max 上的 [Dispatch](https://code.claude.com/docs/en/desktop#sessions-from-dispatch) 到 Desktop |

CLI 是终端原生工作中最完整的界面：脚本和 Agent SDK 仅限 CLI。第三方提供商也在 [VS Code](https://code.claude.com/docs/en/vs-code#use-third-party-providers) 中工作。Desktop 和 IDE 扩展用一些 CLI 独有功能换取可视化审查和更紧密的编辑器集成。Web 在 Anthropic 云中运行，断开后任务继续。Mobile 是进入云会话或通过 Remote Control 进入本地会话的轻客户端，可通过 Dispatch 向 Desktop 发送任务。

你可以在同一项目上混合使用多个界面。配置、项目 memory 和 MCP 服务器在本地界面间共享。

## 连接你的工具

**集成让 Claude 能与代码库之外的服务协作：**

| 集成 | 功能 | 适用场景 |
| :--- | :--- | :--- |
| [Chrome](https://code.claude.com/docs/en/chrome) | 使用你的登录态控制浏览器 | 测试 Web 应用、填表、自动化没有 API 的网站 |
| [GitHub Actions](https://code.claude.com/docs/en/github-actions) | 在 CI 流水线中运行 Claude | 自动 PR 审查、issue 分类、定期维护 |
| [GitLab CI/CD](https://code.claude.com/docs/en/gitlab-ci-cd) | GitLab 版 GitHub Actions | GitLab 上的 CI 驱动自动化 |
| [Code Review](https://code.claude.com/docs/en/code-review) | 自动审查每个 PR | 在人工审查前发现 bug |
| [Slack](https://code.claude.com/docs/en/slack) | 响应频道中的 `@Claude` 提及 | 从团队聊天中将 bug 报告转为 PR |

未列出的集成可通过 [MCP 服务器](https://code.claude.com/docs/en/mcp)和[连接器](https://code.claude.com/docs/en/desktop#connect-external-tools)连接几乎任何东西：Linear、Notion、Google Drive 或你的内部 API。

## 离开终端时工作

**Claude Code 提供多种不在终端前时工作的方式。** 它们在什么触发工作、Claude 在哪里运行以及需要多少设置上有所不同：

| 方式 | 触发 | Claude 运行在 | 设置 | 最适合 |
| :--- | :--- | :--- | :--- | :--- |
| [Dispatch](https://code.claude.com/docs/en/desktop#sessions-from-dispatch) | 从 Claude 移动应用发送任务 | 你的机器（Desktop） | [配对移动应用与 Desktop](https://support.claude.com/en/articles/13947068) | 离开时委派工作，最少设置 |
| [Remote Control](https://code.claude.com/docs/en/remote-control) | 从 [claude.ai/code](https://claude.ai/code) 或 Claude 移动应用驱动 | 你的机器（CLI 或 VS Code） | 运行 `claude remote-control` | 从其他设备引导进行中的工作 |
| [Channels](https://code.claude.com/docs/en/channels) | 来自 Telegram/Discord 等聊天应用或你自己的服务器的推送事件 | 你的机器（CLI） | [安装 channel 插件](https://code.claude.com/docs/en/channels#quickstart) | 响应外部事件如 CI 失败或聊天消息 |
| [Slack](https://code.claude.com/docs/en/slack) | 在团队频道中提及 `@Claude` | Anthropic 云 | [安装 Slack 应用](https://code.claude.com/docs/en/slack#setting-up-claude-code-in-slack) | 从团队聊天发起 PR 和审查 |
| [Scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks) | 设置时间表 | [CLI](https://code.claude.com/docs/en/scheduled-tasks)、[Desktop](https://code.claude.com/docs/en/desktop-scheduled-tasks) 或[云](https://code.claude.com/docs/en/routines) | 选择频率 | 每日审查等周期性自动化 |

如果不确定从哪开始，[安装 CLI](https://code.claude.com/docs/en/quickstart) 并在项目目录中运行。如果不想用终端，[Desktop](https://code.claude.com/docs/en/desktop-quickstart) 提供相同引擎的图形界面。

## 相关资源

### 平台

- [CLI 快速开始](https://code.claude.com/docs/en/quickstart)：在终端安装并运行第一个命令
- [Desktop](https://code.claude.com/docs/en/desktop)：可视化 diff 审查、并行会话、computer use 和 Dispatch
- [VS Code](https://code.claude.com/docs/en/vs-code)：编辑器内的 Claude Code 扩展
- [JetBrains](https://code.claude.com/docs/en/jetbrains)：IntelliJ、PyCharm 等 JetBrains IDE 的扩展
- [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web)：断开后继续运行的云会话
- Mobile：Claude [iOS](https://apps.apple.com/us/app/claude-by-anthropic/id6473753684) 和 [Android](https://play.google.com/store/apps/details?id=com.anthropic.claude) 应用

### 集成

- [Chrome](https://code.claude.com/docs/en/chrome)：使用登录态自动化浏览器任务
- [Computer use](https://code.claude.com/docs/en/computer-use)：让 Claude 在 macOS 上打开应用和控制屏幕
- [GitHub Actions](https://code.claude.com/docs/en/github-actions)：在 CI 流水线中运行 Claude
- [GitLab CI/CD](https://code.claude.com/docs/en/gitlab-ci-cd)：GitLab 版
- [Code Review](https://code.claude.com/docs/en/code-review)：每个 PR 的自动审查
- [Slack](https://code.claude.com/docs/en/slack)：从团队聊天发送任务，获得 PR

### 远程访问

- [Dispatch](https://code.claude.com/docs/en/desktop#sessions-from-dispatch)：从手机发消息即可生成 Desktop 会话
- [Remote Control](https://code.claude.com/docs/en/remote-control)：从手机或浏览器驱动运行中的会话
- [Channels](https://code.claude.com/docs/en/channels)：从聊天应用或你的服务器推送事件到会话
- [Scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks)：按周期运行 prompt
