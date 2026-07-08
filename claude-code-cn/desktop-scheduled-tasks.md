---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】桌面定时任务
description: Claude Code Desktop 的定时任务功能允许你设置定期自动运行的任务，如每日代码审查、依赖审计或晨报。任务在本地机器上运行，可直接访问文件和工具。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/desktop-scheduled-tasks.md
  - en-source/desktop-scheduled-tasks.md
---

# 在 Claude Code Desktop 中调度定时任务

> 在 Claude Code Desktop 中设置定时任务，让 Claude 定期自动运行每日代码审查、依赖审计或晨报等工作。

**定时任务按你选择的时间和频率自动启动新会话。** 适用于每日代码审查、依赖更新检查、或从日历和收件箱拉取信息的晨报等周期性工作。

桌面应用的 **Routines** 页面可以创建本地定时任务和远程 [routines](https://code.claude.com/docs/en/routines)。本地任务在你的机器上运行，可直接访问文件和工具，但仅在应用打开且电脑唤醒时触发。远程 routine 运行在 Anthropic 管理的云基础设施上，即使电脑关闭也能运行。本页介绍本地定时任务；远程 routines 及其触发选项参见 [Routines](https://code.claude.com/docs/en/routines)。

## 调度方式对比

Claude Code 提供三种调度周期性或一次性工作的方式：

| | [Cloud](https://code.claude.com/docs/en/routines) | [Desktop](https://code.claude.com/docs/en/desktop-scheduled-tasks) | [`/loop`](https://code.claude.com/docs/en/scheduled-tasks) |
|---|---|---|---|
| **运行位置** | Anthropic 云端 | 你的机器 | 你的机器 |
| **需要机器开启** | 否 | 是 | 是 |
| **需要打开会话** | 否 | 否 | 是 |
| **重启后持久化** | 是 | 是 | 用 `--resume` 恢复（如未过期） |
| **访问本地文件** | 否（全新克隆） | 是 | 是 |
| **MCP 服务器** | 每任务配置连接器 | [配置文件](https://code.claude.com/docs/en/mcp)和连接器 | 继承会话 |
| **权限提示** | 否（自治运行） | 按任务配置 | 继承会话 |
| **自定义调度** | 通过 CLI 中的 `/schedule` | 是 | 是 |
| **最小间隔** | 1 小时 | 1 分钟 | 1 分钟 |

> [!TIP]
> 需要可靠运行且不依赖本机时用 **Cloud 任务**。需要访问本地文件和工具时用 **Desktop 任务**。会话中快速轮询用 **`/loop`**。

> [!NOTE]
> 默认情况下，定时任务针对工作目录的当前状态运行，包括未提交的变更。创建任务时启用 worktree 开关可以给每次运行隔离的 Git worktree。

## 创建定时任务

点击侧边栏的 **Routines**，然后点击 **New routine** 选择 **Local**。配置以下字段：

| 字段 | 说明 |
|------|------|
| Name | 任务标识符。转换为小写 kebab-case 作为磁盘文件夹名。需在所有任务中唯一 |
| Description | 任务列表中显示的简短摘要 |
| Instructions | Claude 运行任务时执行的内容。像在提示框中写消息一样。包含权限模式和模型选择器，下方选择工作文件夹和是否使用隔离 worktree |
| Schedule | 任务运行频率。参见[调度选项](#调度选项) |

保存任务前需要选择文件夹。如果尚未信任该文件夹，Desktop 会在保存前提示你信任它。

你也可以在任何会话中描述你想要的来创建任务。例如，"set up a daily code review that runs every morning at 9am" 创建周期任务，"remind me at 3pm tomorrow to check the deploy" 创建触发一次后自动禁用的一次性任务。

## 调度选项

从 Schedule 控件选择预设：

| 选项 | 说明 |
|------|------|
| **Manual** | 无调度，只在点击 **Run now** 时运行。适合保存按需触发的 prompt |
| **Hourly** | 每小时运行 |
| **Daily** | 显示时间选择器，默认本地时间 9:00 AM |
| **Weekdays** | 与 Daily 相同但跳过周六日 |
| **Weekly** | 显示时间选择器和星期选择器 |

选择器未提供的间隔（如每 15 分钟、每月第一天、或特定未来时间的单次运行），可以在任何 Desktop 会话中让 Claude 设置。例如，"schedule a task to run all the tests every 6 hours"。

## 定时任务如何运行

**定时任务在你的机器上运行。** Desktop 在应用打开时每分钟检查调度，任务到期时启动全新会话，独立于任何手动会话。每个任务在计划时间后有几分钟的小延迟以分散 API 流量。延迟是确定性的：同一任务总是在相同偏移量启动。

任务触发时你会收到桌面通知，侧边栏中 **Scheduled** 部分出现新会话。打开它查看 Claude 做了什么、审查变更或响应权限提示。会话与普通会话一样工作：Claude 可以编辑文件、运行命令、创建 commit 和打开 PR。

**任务仅在桌面应用运行且电脑唤醒时运行。** 如果电脑在计划时间睡眠，该次运行会被跳过。要防止空闲睡眠，在 Settings → Desktop app → General 中启用 **Keep computer awake**。合上笔记本盖仍会进入睡眠。对于需要在电脑关闭时运行或响应 API 调用 / GitHub 事件触发的任务，创建远程 [routine](https://code.claude.com/docs/en/routines)。

## 错过的运行

**当应用启动或电脑唤醒时，Desktop 检查每个任务在过去七天内是否错过了运行。** 如果错过了，Desktop 为最近错过的时间启动恰好一次补跑，丢弃更早的。错过六天的每日任务在唤醒时只运行一次。补跑启动时 Desktop 显示通知。

编写 prompt 时需注意这一点。计划在 9am 运行的任务可能在 11pm 运行（如果电脑整天在睡眠）。如果时间重要，在 prompt 中添加防护措施，例如："Only review today's commits. If it's after 5pm, skip the review and just post a summary of what was missed."

## 定时任务的权限

**每个任务有自己的权限模式**，在创建或编辑时设置。`~/.claude/settings.json` 中的 Allow 规则也适用于定时任务会话。如果任务在 Ask 模式运行且需要运行未获权限的工具，运行会暂停直到你批准。会话保持在侧边栏中等你后续回答。

为避免暂停，创建任务后点击 **Run now**，观察权限提示，对每个选择 "always allow"。该任务的后续运行会自动批准相同工具而不提示。可以在任务详情页审查和撤销这些批准。

## 管理定时任务

在 **Routines** 列表中点击任务打开详情页。可以：

| 操作 | 说明 |
|------|------|
| **Run now** | 立即启动任务，不等待下次计划时间 |
| **Status** | 在 Active 和 Paused 之间切换，暂停或恢复计划运行而不删除任务 |
| **Edit** | 修改 instructions、schedule、folder 或其他设置 |
| **Review history** | 查看每次历史运行，包括跳过的运行 |
| **Review allowed permissions** | 从 **Always allowed** 面板查看和撤销已保存的工具批准 |
| **Delete** | 删除任务并归档其创建的所有会话 |

你也可以在任何 Desktop 会话中通过询问 Claude 来列出、创建、编辑和暂停任务。

定时任务还可以在运行中的会话内通过 `update_scheduled_task` MCP 工具修改自己的调度或 prompt。这让任务可以根据发现的内容重新调度自己。

要在磁盘上编辑任务的 prompt，打开 `~/.claude/scheduled-tasks/<task-name>/SKILL.md`（如果设置了 [`CLAUDE_CONFIG_DIR`](https://code.claude.com/docs/en/env-vars) 则在该目录下）。文件使用 YAML frontmatter 存放 `name` 和 `description`，prompt 作为正文。更改在下次运行时生效。

## 相关资源

- [Routines](https://code.claude.com/docs/en/routines)：在 Anthropic 管理的基础设施上按计划、API 调用或 GitHub 事件运行任务
- [按计划运行 Prompt](https://code.claude.com/docs/en/scheduled-tasks)：CLI 中使用 `/loop` 的会话级调度
- [Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions)：在 CI 中按计划运行 Claude
- [使用 Claude Code Desktop](https://code.claude.com/docs/en/desktop)：完整桌面应用指南
