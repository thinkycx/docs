---
title: 【译】会话管理
tags:
  - claude-code
  - sessions
  - translation
create: 2026-06-28
update: 2026-06-28
author: thinkycx
category: translation
description: 介绍 Claude Code 会话的命名、恢复、分支和切换机制，涵盖 --continue、--resume、--from-pr、/resume 选择器、会话命名、导出会话记录以及本地存储位置。
refs: https://code.claude.com/docs/en/sessions.md
---

# 管理会话

> 命名、恢复、分支和切换 Claude Code 对话。涵盖 `--continue`、`--resume`、`--from-pr`、`/resume` 选择器、会话命名、导出记录，以及记录存储位置。

**会话是绑定到项目目录的已保存对话。** Claude Code 在你工作时将其存储在本地，因此你可以恢复中断的工作、分支尝试不同方案，或在任务间切换。

[桌面应用](https://code.claude.com/docs/en/desktop#work-in-parallel-with-sessions)、[Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web) 和 [VS Code 扩展](https://code.claude.com/docs/en/vs-code#resume-past-conversations) 各自维护自己的会话历史。本页涵盖 CLI。

## 恢复会话

**会话在你工作时持续保存到 [本地记录文件](#导出和定位会话数据)，因此你可以在退出或运行 `/clear` 后返回。** 使用以下入口：

| 命令 | 作用 |
| :--- | :--- |
| `claude --continue` | 恢复当前目录中最近的会话 |
| `claude --resume` | 打开 [会话选择器](#使用会话选择器) |
| `claude --resume <name>` | 直接恢复指定名称的会话 |
| `claude --from-pr <number>` | 恢复关联到该 pull request 的会话 |
| `/resume` | 在活动会话内切换到不同对话 |

用 [`claude -p`](https://code.claude.com/docs/en/headless) 或 [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) 创建的会话不会出现在会话选择器中，但你仍可通过将会话 ID 传递给 `claude --resume <session-id>` 来恢复。需要从会话启动时所在的目录运行：会话 ID 查找限定在当前项目目录及其 git worktrees 范围内。

### 会话选择器的搜索范围

**会话按项目目录存储。** 默认情况下，会话选择器显示当前 worktree 的交互式会话，以及通过 `/add-dir` 添加了当前目录的其他会话。从 v2.1.169 起，用 [`/cd`](https://code.claude.com/docs/en/commands) 移动会话会将其迁移到新目录的项目存储，之后它会出现在该目录的选择器中。使用 `Ctrl+W` 扩展到仓库的所有 worktrees，或 `Ctrl+A` 扩展到本机上的所有项目。

从同一仓库的另一个 worktree 选择会话会就地恢复。从不相关项目选择会话会将 cd 和 resume 命令复制到剪贴板。

**按名称恢复时会跨当前仓库及其 worktrees 解析：**

| 命令 | 精确匹配 | 名称模糊 |
| :--- | :--- | :--- |
| `claude --resume <name>` | 直接恢复 | 打开会话选择器，名称作为预填搜索词 |
| `/resume <name>` | 直接恢复 | 报错；运行不带参数的 `/resume` 打开选择器 |

## 命名会话

**给会话起描述性名称，使其在选择器中可查找并可按名称恢复。** 这在你并行处理多个任务时尤其重要。

| 时机 | 设置方式 |
| :--- | :--- |
| 启动时 | `claude -n auth-refactor` |
| 会话中 | `/rename auth-refactor`。名称也会显示在提示栏 |
| 从会话选择器 | 高亮会话并按 `Ctrl+R` |
| 接受计划时 | 在 [plan mode](https://code.claude.com/docs/en/permission-modes#analyze-before-you-edit-with-plan-mode) 中接受计划会从计划内容命名会话（除非你已设置名称） |

命名后，用 `claude --resume <name>` 或 `/resume <name>` 返回。

## 使用会话选择器

**在会话中运行 `/resume`，或不带参数运行 `claude --resume`，打开交互式会话选择器。** 使用以下快捷键导航、搜索和扩展列表：

| 快捷键 | 操作 |
| :--- | :--- |
| `↑` / `↓` | 在会话间导航 |
| `→` / `←` | 展开或折叠分组会话 |
| `Enter` | 恢复高亮的会话 |
| `Space` | 预览会话内容（`Ctrl+V` 在不捕获粘贴的终端中也有效） |
| `Ctrl+R` | 重命名高亮的会话 |
| `/` 或除 `Space` 外的可打印字符 | 进入搜索模式并过滤会话。粘贴 GitHub/GitLab/Bitbucket PR 或 MR URL 可查找创建它的会话 |
| `Ctrl+A` | 显示本机所有项目的会话。再按一次返回当前仓库 |
| `Ctrl+W` | 显示当前仓库所有 worktrees 的会话。再按一次返回当前 worktree。仅在多 worktree 仓库中显示 |
| `Ctrl+B` | 过滤到当前 git 分支的会话。再按一次显示所有分支 |
| `Esc` | 退出会话选择器或搜索模式 |

每行显示会话名称（如果已设置），否则显示对话摘要或首个提示，以及上次活动时间、消息数和 git 分支。用 `Ctrl+A` 扩展到所有项目后会显示项目路径。

通过 `/branch`、`/rewind` 或 `--fork-session` 创建的分叉会话分组在其根会话下。按 `→` 展开分组。

## 分支会话

**分支创建当前对话的副本并切换到其中，原始会话保持不变。** 用它尝试不同方案而不丢失当前路径。

从会话内运行 `/branch`，可带可选名称：

```text
/branch try-streaming-approach
```

从命令行，将 `--continue` 或 `--resume` 与 `--fork-session` 组合：

```bash
claude --continue --fork-session
```

原始会话不变，仍可在会话选择器中使用。`/branch` 确认信息会打印两个会话 ID：你现在所在的新分支和原始会话。要返回原始会话，将其 ID 传递给 `/resume`，使用选择器，或运行 `/resume <original-name>`。

**你用 "allow for this session" 批准的权限不会传递到新分支。** 如果你在不 fork 的情况下在两个终端中恢复同一会话，两者的消息会交错到一个记录中。

对于单个会话内基于检查点的回退，参见 [Checkpointing](https://code.claude.com/docs/en/checkpointing)。

## 管理会话内的上下文

**这些命令控制上下文窗口中的内容而不离开会话：**

- **`/clear`**：以空上下文重新开始。之前的对话已保存且可恢复
- **`/compact [instructions]`**：用摘要替换历史，可选地聚焦于你指定的内容
- **`/context`**：显示当前消耗上下文的内容

关于压缩如何与 CLAUDE.md、skills 和规则交互，参见 [Context window 指南](https://code.claude.com/docs/en/context-window)。关于何时 clear 与何时 compact 的策略，参见 [Best practices](https://code.claude.com/docs/en/best-practices#manage-your-session)。

## 导出和定位会话数据

**运行 `/export` 将当前对话复制到剪贴板或保存为纯文本文件**，消息和工具输出渲染为可读文本。传入文件名可直接写入该文件。

### 从脚本访问对话

`/export` 生成供人阅读的渲染记录。以下接口生成供脚本解析的结构化数据：

- **运行 Claude 一次并捕获结果**：调用 `claude -p` 配合 [`--output-format json` 或 `stream-json`](https://code.claude.com/docs/en/headless#get-structured-output) 捕获非交互式运行的结果、会话 ID、用量和成本（JSON 格式）。
- **向现有会话提问**：将会话 ID 传递给 [`claude -p --resume`](https://code.claude.com/docs/en/headless#continue-conversations) 发送后续提示并捕获结构化响应。
- **响应会话事件**：读取 [hooks](https://code.claude.com/docs/en/hooks#common-input-fields) 和 [status line commands](https://code.claude.com/docs/en/statusline#available-data) 作为输入接收的 `transcript_path` 字段。`SessionEnd` hook 可在会话结束时归档记录。
- **在 TypeScript 或 Python 应用中嵌入 Claude**：使用 [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) 以编程方式接收每条消息。

以下示例使用第二个接口，向现有会话发送后续提示并用 `jq` 读取答案：

```bash
claude -p --resume <session-id> --output-format json "summarize what we changed" | jq -r '.result'
```

### 记录存储位置

**默认情况下，记录以 JSONL 格式存储在 `~/.claude/projects/<project>/<session-id>.jsonl`**，其中 `<project>` 是你的工作目录路径（非字母数字字符替换为 `-`）。每行是消息、工具使用或元数据条目的 JSON 对象。条目格式是 Claude Code 内部的，版本间会变化，因此直接解析这些文件的脚本可能在任何版本中断。要基于会话数据构建，使用 `/export` 或 [脚本接口](#从脚本访问对话)。

**存储位置、保留期和写入行为可配置：**

| 目的 | 设置 | 位置 |
| :--- | :--- | :--- |
| 将存储移出 `~/.claude` | [`CLAUDE_CONFIG_DIR`](https://code.claude.com/docs/en/env-vars) | 环境变量 |
| 更改 30 天保留期 | [`cleanupPeriodDays`](https://code.claude.com/docs/en/settings#available-settings) | `settings.json` |
| 在所有模式下抑制记录写入 | [`CLAUDE_CODE_SKIP_PROMPT_HISTORY`](https://code.claude.com/docs/en/env-vars) | 环境变量 |
| 为单次非交互式运行抑制写入 | [`--no-session-persistence`](https://code.claude.com/docs/en/cli-reference) | CLI 标志（配合 `claude -p`） |

## 另请参阅

以下页面涵盖相关的会话和并行机制：

- [Worktrees](https://code.claude.com/docs/en/worktrees)：在独立分支上运行隔离的并行会话
- [Checkpointing](https://code.claude.com/docs/en/checkpointing)：将代码和对话回退到更早的点
- [Context window](https://code.claude.com/docs/en/context-window)：什么填充上下文以及什么在压缩后留存
- [Non-interactive mode](https://code.claude.com/docs/en/headless)：`claude -p` 下的会话行为
