---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Ultrareview
description: Ultrareview 是 Claude Code 的深度代码审查功能，通过在云端启动多个审查 Agent 并行分析你的分支或 PR，独立复现并验证每个问题，帮助你在合并前发现真正的 Bug。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/ultrareview.md
  - en-source/ultrareview.md
---

# 用 Ultrareview 发现 Bug

> 在云端运行深度多 Agent 代码审查，使用 `/code-review ultra` 在合并前发现并验证 Bug。

> [!NOTE]
> Ultrareview 是研究预览功能，需要 Claude Code v2.1.86 及以上版本。功能、定价和可用性可能根据反馈调整。现在通过 `/code-review ultra` 调用，`/ultrareview` 仍作为别名保留。

**Ultrareview 是一种深度代码审查，运行在 Claude Code on the web 基础设施上。** 当你执行 `/code-review ultra` 时，Claude Code 在远程沙箱中启动一组审查 Agent，对你的分支或 PR 进行 Bug 检测。

与本地 `/code-review` 或 `/review` 相比，ultrareview 的优势：

| 特性 | 说明 |
|------|------|
| **更高信噪比** | 每个报告的发现都会被独立复现和验证，结果聚焦于真正的 Bug 而非风格建议 |
| **更广覆盖** | 更大规模的审查 Agent 集群并行探索变更，能发现本地审查容易遗漏的问题 |
| **不占用本地资源** | 审查完全在远程沙箱中运行，你的终端可以继续做其他事情 |

**认证要求：** Ultrareview 需要使用 Claude.ai 账号认证，因为它运行在 Claude Code on the web 基础设施上。如果你仅使用 API Key 登录，请先运行 `/login` 并通过 Claude.ai 认证。使用 Amazon Bedrock、Google Cloud Agent Platform 或 Microsoft Foundry 时不可用，启用了 Zero Data Retention 的组织也不可用。

## 从 CLI 运行 Ultrareview

在任何 git 仓库中的 Claude Code CLI 中启动审查：

```text
/code-review ultra
```

**不带参数时，ultrareview 审查当前分支与默认分支之间的 diff**，包括工作目录中未提交和已暂存的变更。Claude Code 会打包仓库状态并上传到远程沙箱进行审查。

如果要审查 GitHub PR，传入 PR 编号：

```text
/code-review ultra 1234
```

**PR 模式下，远程沙箱直接从 GitHub 克隆 PR**，而不是打包本地工作目录。PR 模式支持 `github.com` 上的仓库以及 Owner 已连接到 Claude Code 的 [GitHub Enterprise Server](https://code.claude.com/docs/en/github-enterprise-server) 实例。

> [!TIP]
> 如果仓库太大无法打包，Claude Code 会提示使用 PR 模式。推送你的分支并创建一个 draft PR，然后运行 `/code-review ultra <PR-number>`。
>
> 如果 PR 的 diff 太大，Claude Code 会在审查开始前拒绝并给出范围提示。

**启动前，Claude Code 会显示确认对话框**，包含审查范围（分支审查时包含文件和行数）、剩余免费次数和预估费用。确认后审查在后台继续，你可以继续使用会话。该命令只在你手动调用 `/code-review ultra` 时运行，Claude 不会自行启动 ultrareview。

## 定价和免费次数

**Ultrareview 是高级功能，按 usage credits 计费。**

| 计划 | 包含免费次数 | 免费次数用完后 |
|------|-------------|---------------|
| Pro | 3 次免费 | 按 [usage credits](https://support.claude.com/en/articles/12429409-extra-usage-for-paid-claude-plans) 计费 |
| Max | 3 次免费 | 按 [usage credits](https://support.claude.com/en/articles/12429409-extra-usage-for-paid-claude-plans) 计费 |
| Team 和 Enterprise | 无 | 按 [usage credits](https://support.claude.com/en/articles/12429409-extra-usage-for-paid-claude-plans) 计费 |

Pro 和 Max 订阅者有 3 次免费 ultrareview 体验机会。这 3 次是每个账号的一次性额度，不会刷新。用完后或免费期结束后，每次审查按 usage credits 计费，通常在 $5 到 $20 之间，取决于变更规模。一旦云端会话启动即计为一次使用，因此提前停止或未完成的审查仍会消耗一次免费次数。付费审查则只对已运行部分计费。

**由于免费次数之外的 ultrareview 始终按 usage credits 计费**，你的账号或组织必须先开启 usage credits 才能启动付费审查。如果未开启，Claude Code 会阻止启动并引导你到计费设置页面。你也可以运行 `/usage-credits` 检查或更改当前设置。

## 追踪运行中的审查

**审查通常需要 5 到 10 分钟。** 审查作为后台任务运行，你可以继续工作、启动其他命令，或关闭终端。

使用 `/tasks` 查看运行中和已完成的审查、打开审查详情，或停止进行中的审查。停止审查会归档云端会话，部分发现不会返回。审查完成后，验证过的发现会以通知形式出现在你的会话中。每个发现包含文件位置和问题说明，你可以直接让 Claude 修复。

## 非交互式运行 Ultrareview

使用 `claude ultrareview` 子命令从 CI 或脚本启动 ultrareview，无需交互式会话。该子命令启动与 `/code-review ultra` 相同的审查，阻塞直到远程审查完成，将发现打印到 stdout，成功退出码为 0，失败为 1。

```bash
claude ultrareview
claude ultrareview 1234
claude ultrareview origin/main
```

**不带参数时审查当前分支与默认分支之间的 diff。** 传入 PR 编号审查 PR，传入基准分支审查与该分支的 diff。调用子命令即视为同意交互命令所显示的计费和条款提示。

进度消息和实时会话 URL 输出到 stderr，stdout 保持可解析。使用以下标志控制输出和超时：

| 标志 | 说明 |
|------|------|
| `--json` | 打印原始 `bugs.json` payload 而非格式化的发现 |
| `--timeout <minutes>` | 等待审查完成的最大分钟数，默认 30 |

**退出码说明：**
- `0`：审查完成（无论是否有发现）
- `1`：审查启动失败、云端会话出错或超时
- `130`：被 Ctrl-C 中断

如果你中断了子命令，远程审查会继续运行；通过 stderr 打印的会话 URL 在浏览器中查看。

如需在 GitHub PR 上自动审查，[Code Review](https://code.claude.com/docs/en/code-review) 可直接集成到仓库，以 PR 内联评论形式发布发现，无需 CLI 步骤。

## Ultrareview 与 /code-review 和 /review 的对比

三个命令都审查代码，但面向工作流的不同阶段：

| | `/code-review` | `/review <pr>` | `/code-review ultra` |
|---|---|---|---|
| **目标** | 工作目录 diff | GitHub PR | 工作目录 diff 或 PR |
| **运行位置** | 本地会话 | 本地会话 | 远程云端沙箱 |
| **深度** | 随 effort 参数缩放 | 单次审查 | 多 Agent 集群 + 独立验证 |
| **耗时** | 几秒到几分钟 | 几秒到几分钟 | 约 5 到 10 分钟 |
| **成本** | 计入正常使用量 | 计入正常使用量 | 免费次数，之后约 $5-$20/次（usage credits） |
| **适用场景** | 迭代中快速获取反馈 | 审核前查看队友的 PR | 对重大变更在合并前获得深度信心 |

**使用建议：** 用 `/code-review` 在开发中获取快速反馈。用 `/review <pr>` 在审批前查看 PR。用 `/code-review ultra` 在合并重大变更前做深度审查，捕获本地审查可能遗漏的问题。

## 相关资源

- [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web)：了解云端会话和沙箱的工作原理
- [用 ultraplan 规划复杂变更](https://code.claude.com/docs/en/ultraplan)：ultrareview 的规划对应功能，用于前期设计工作
- [有效管理成本](https://code.claude.com/docs/en/costs)：跟踪使用量和设置支出限额
