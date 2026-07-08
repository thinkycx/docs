---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Ultraplan
description: Ultraplan 将规划任务从本地 CLI 移交到 Claude Code on the web 的 plan mode 会话中。支持浏览器内评审、行内评论和灵活选择执行位置。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/ultraplan.md
  - en-source/ultraplan.md
---

# 云端规划：Ultraplan

> 从 CLI 发起规划，在 Claude Code on the web 中起草方案，然后选择在云端或本地终端执行

**Ultraplan 处于研究预览阶段，需要 Claude Code v2.1.91 或更高版本。** 行为和能力可能根据反馈变化。

**Ultraplan 将规划任务从本地 CLI 移交到 [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web) 的 [plan mode](https://code.claude.com/docs/en/permission-modes#analyze-before-you-edit-with-plan-mode) 会话。** Claude 在云端起草方案，你可以继续在终端工作。方案就绪后，在浏览器中评审、评论、请求修改，并选择执行位置。

适用场景：

- **精确反馈**：对方案的各个部分分别评论，而非回复整体
- **后台起草**：方案在远程生成，终端保持空闲
- **灵活执行**：可在网页端执行并创建 PR，也可发回终端

**前提条件：** 需要 [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web) 账号和 GitHub 仓库。由于在 Anthropic 云基础设施上运行，不支持 Amazon Bedrock、Google Cloud Agent Platform 或 Microsoft Foundry。云会话在你账号的默认[云环境](https://code.claude.com/docs/en/claude-code-on-the-web#the-cloud-environment)中运行。如果还没有云环境，ultraplan 首次启动时会自动创建。

## 从 CLI 启动 ultraplan

三种启动方式：

| 方式 | 说明 |
| --- | --- |
| 命令 | 运行 `/ultraplan` 加上你的提示 |
| 关键词 | 在普通提示中包含 `ultraplan` 一词 |
| 从本地 plan | Claude 完成本地规划并显示批准对话框时，选择 **No, refine with Ultraplan on Claude Code on the web** 将草案发送到云端进一步迭代 |

示例：

```
/ultraplan migrate the auth service from sessions to JWTs
```

**命令和关键词方式会在启动前显示确认对话框。** 本地 plan 方式跳过确认，因为你的选择本身就是确认。如果 [Remote Control](https://code.claude.com/docs/en/remote-control) 处于活跃状态，ultraplan 启动时会断开连接，因为两者共用 claude.ai/code 界面。

云会话启动后，CLI 提示输入区显示状态指示器：

| 状态 | 含义 |
| --- | --- |
| `◇ ultraplan` | Claude 正在研究代码库并起草方案 |
| `◇ ultraplan needs your input` | Claude 有澄清问题；打开会话链接回应 |
| `◆ ultraplan ready` | 方案已就绪，可在浏览器中评审 |

运行 `/tasks` 并选择 ultraplan 条目可打开详细视图，包含会话链接、agent 活动和 **Stop ultraplan** 操作。停止会归档云会话并清除指示器，不会向终端保存任何内容。

## 在浏览器中评审和修改方案

**当状态变为 `◆ ultraplan ready` 时，打开会话链接在 claude.ai 中查看方案。** 方案展示在专用评审视图中：

- **行内评论**：选中任何段落，针对性地留下评论供 Claude 处理
- **Emoji 反应**：对某个部分做出反应，无需撰写完整评论即可表达认可或关注
- **大纲侧边栏**：在方案各部分间快速跳转

要求 Claude 处理你的评论后，它会修订方案并呈现更新版本。可以迭代任意多次。

## 选择执行位置

方案满意后，在浏览器中选择执行方式。

### 在网页端执行

选择 **Approve Claude's plan and start coding** 让 Claude 在同一云会话中实现。终端显示确认，状态指示器清除，工作在云端继续。实现完成后，[审查 diff](https://code.claude.com/docs/en/claude-code-on-the-web#review-changes) 并从网页界面创建 pull request。

### 将方案发回终端

选择 **Approve plan and teleport back to terminal** 在本地实现，完整访问你的环境。此选项在会话从 CLI 启动且终端仍在轮询时才显示。网页会话会被归档，不会并行继续。

终端显示标题为 **Ultraplan approved** 的方案对话框，提供三个选项：

| 选项 | 说明 |
| --- | --- |
| Implement here | 将方案注入当前对话，从中断处继续 |
| Start new session | 清除当前对话，仅以方案作为上下文重新开始 |
| Cancel | 将方案保存为文件，不执行；Claude 打印文件路径供后续使用 |

如果选择 Start new session，Claude 会在顶部打印 `claude --resume` 命令，方便你稍后回到之前的对话。

## 相关资源

- [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web)：ultraplan 运行的云基础设施
- [Plan mode](https://code.claude.com/docs/en/permission-modes#analyze-before-you-edit-with-plan-mode)：本地会话中的规划方式
- [用 ultrareview 发现 bug](https://code.claude.com/docs/en/ultrareview)：ultraplan 的代码审查对应物
- [Remote Control](https://code.claude.com/docs/en/remote-control)：在 claude.ai/code 界面使用本机运行的会话
