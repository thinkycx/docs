---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】Worktrees 并行会话
description: Claude Code 支持通过 git worktree 实现多会话并行隔离，每个会话在独立工作目录中运行，互不干扰。本文介绍 --worktree 标志、子代理隔离、.worktreeinclude 配置、清理机制及非 git 版本控制的 hook 扩展。
category: translation
tags: [claude-code, worktrees, translation]
refs: [https://code.claude.com/docs/en/worktrees.md]
---

# 用 Worktree 运行并行会话

> **核心概念：** 将多个 Claude Code 会话隔离在独立的 git worktree 中，避免文件变更冲突。涵盖 `--worktree` 标志、子代理隔离、`.worktreeinclude`、清理机制以及非 git 版本控制的 hook 支持。

**Worktree 是什么？** [Git worktree](https://git-scm.com/docs/git-worktree) 是一个独立的工作目录，拥有自己的文件和分支，但与主 checkout 共享相同的仓库历史和远端。每个 Claude Code 会话运行在独立的 worktree 中，意味着一个会话的编辑不会影响另一个会话的文件。你可以在一个终端让 Claude 开发新功能，同时在另一个终端修复 bug。

本文介绍 CLI 中的 worktree 隔离功能。以下内容均假设使用 git 仓库。如果使用其他版本控制系统，请参考 [非 git 版本控制](#非-git-版本控制)。[桌面应用](https://code.claude.com/docs/en/desktop)会为每个新会话自动创建 worktree。

**Worktree 在并行方案中的定位：** Worktree 是多种并行运行 Claude 的方式之一。它负责隔离文件编辑，而[子代理](https://code.claude.com/docs/en/sub-agents)和[代理团队](https://code.claude.com/docs/en/agent-teams)负责协调工作本身。可以参考[并行运行代理](https://code.claude.com/docs/en/agents)来对比各种方案，或直接跳到[用 Worktree 隔离子代理](#用-worktree-隔离子代理)了解两者结合使用的方法。

## 在 Worktree 中启动 Claude

**使用 `--worktree` 或 `-w` 创建隔离的 worktree 并启动 Claude。** 默认情况下，worktree 创建在仓库根目录的 `.claude/worktrees/<value>/` 下，所在分支命名为 `worktree-<value>`：

```bash theme={null}
claude --worktree feature-auth
```

如果需要将 worktree 放在其他位置，可以配置 [`WorktreeCreate` hook](#非-git-版本控制)。在另一个终端用不同名称再次运行命令，即可启动第二个隔离会话：

```bash theme={null}
claude --worktree bugfix-123
```

如果省略名称，Claude 会自动生成一个，例如 `bright-running-fox`：

```bash theme={null}
claude --worktree
```

你也可以在会话中要求 Claude "work in a worktree"，它会通过 [`EnterWorktree`](https://code.claude.com/docs/en/tools-reference) 工具创建一个 worktree。进入 worktree 后，Claude 可以通过调用 `EnterWorktree` 并指定目标路径，直接切换到 `.claude/worktrees/` 下的另一个 worktree。之前的 worktree 保留在磁盘上不受影响。

**首次使用前需要信任确认：** 在某个目录下首次交互式使用 `--worktree` 之前，需要先运行一次 `claude` 来接受工作区信任对话框。如果尚未接受信任，`--worktree` 会报错退出并提示你先在该目录运行 `claude`。使用 `-p` 的非交互式运行会跳过[信任检查](https://code.claude.com/docs/en/security)，因此 `claude -p --worktree` 可以直接执行。

> **提示：** 将 `.claude/worktrees/` 添加到 `.gitignore`，这样 worktree 的内容不会在主 checkout 中显示为未跟踪文件。

### 选择基础分支

**Worktree 默认从仓库的默认分支（`origin/HEAD`）创建新分支，** 确保起始状态与远端一致。如果没有配置远端或 fetch 失败，则回退到当前本地 `HEAD`。如果希望始终从本地 `HEAD` 创建分支，可以在[设置](https://code.claude.com/docs/en/settings)中将 `worktree.baseRef` 设为 `"head"`。设为 `"head"` 后，新 worktree 会携带你未推送的 commit 和特性分支状态，适用于需要子代理在进行中的工作上操作的场景。该设置只接受 `"fresh"` 或 `"head"`，不支持任意 git ref：

```json theme={null}
{
  "worktree": {
    "baseRef": "head"
  }
}
```

**从特定 PR 创建 worktree：** 传入以 `#` 开头的 PR 编号或完整的 GitHub PR URL。Claude Code 会从 `origin` 获取 `pull/<number>/head` 并在 `.claude/worktrees/pr-<number>` 创建 worktree：

```bash theme={null}
claude --worktree "#1234"
```

如果需要完全控制 worktree 的创建方式，可以配置 [`WorktreeCreate` hook](https://code.claude.com/docs/en/hooks)，它会完全替代默认的 `git worktree` 逻辑。

## 将 gitignore 文件复制到 Worktree

**Worktree 是全新的 checkout，不包含主仓库中的未跟踪文件，** 如 `.env` 或 `.env.local`。要在 Claude 创建 worktree 时自动复制这些文件，可以在项目根目录添加 `.worktreeinclude` 文件。

该文件使用 `.gitignore` 语法。只有匹配模式且同时被 gitignore 的文件才会被复制，已跟踪的文件不会被重复复制。

以下 `.worktreeinclude` 会将两个 env 文件和一个 secrets 配置复制到每个新 worktree 中：

```text .worktreeinclude theme={null}
.env
.env.local
config/secrets.json
```

这适用于通过 `--worktree` 创建的 worktree、[子代理 worktree](#用-worktree-隔离子代理) 以及[桌面应用](https://code.claude.com/docs/en/desktop)中的并行会话。

## 用 Worktree 隔离子代理

**子代理可以运行在独立的 worktree 中，避免并行编辑产生冲突。** 你可以要求 Claude "use worktrees for your agents"，或者在[自定义子代理](https://code.claude.com/docs/en/sub-agents)的 frontmatter 中添加 `isolation: worktree` 来永久启用。每个子代理获得一个临时 worktree，当子代理完成且没有变更时会自动删除。

子代理 worktree 使用与 `--worktree` 相同的[基础分支](#选择基础分支)，即默认从仓库默认分支创建，除非 `worktree.baseRef` 设为 `"head"`。

## 清理 Worktree

**退出 worktree 会话时，清理行为取决于是否有变更：**

| 场景 | 行为 |
|------|------|
| 无未提交变更、无未跟踪文件、无新 commit | worktree 和分支自动删除。如果会话有[名称](https://code.claude.com/docs/en/sessions)，Claude 会提示是否保留 |
| 存在未提交变更、未跟踪文件或新 commit | Claude 提示你选择保留或删除。保留会保留目录和分支以便后续返回；删除会移除 worktree 目录及其分支，丢弃所有未提交变更、未跟踪文件和 commit |
| 非交互式运行（`-p`） | 通过 `--worktree` 配合 `-p` 创建的 worktree 不会自动清理（因为没有退出提示）。需要手动用 `git worktree remove` 删除 |

**自动清理机制：** Claude 为子代理和[后台会话](https://code.claude.com/docs/en/agent-view)创建的 worktree，在超过 [`cleanupPeriodDays`](https://code.claude.com/docs/en/settings) 设置的天数后会自动删除，前提是没有未提交变更、未跟踪文件和未推送的 commit。通过 `--worktree` 手动创建的 worktree 不受此自动清理影响。

**运行中的锁保护：** 代理运行时，Claude 会对其 worktree 执行 `git worktree lock`，防止并发清理删除它。代理完成后释放锁。如果需要清理被跳过的 worktree，运行 `git worktree remove`，如有未提交变更或未跟踪文件需加 `--force`。

## 手动管理 Worktree

**如果需要完全控制 worktree 的位置和分支配置，可以直接使用 Git 命令创建。** 这在需要检出特定已有分支或将 worktree 放在仓库外时很有用。

在新分支上创建 worktree：

```bash theme={null}
git worktree add ../project-feature-a -b feature-a
```

从已有分支创建 worktree：

```bash theme={null}
git worktree add ../project-bugfix bugfix-123
```

在 worktree 中启动 Claude：

```bash theme={null}
cd ../project-feature-a && claude
```

列出所有 worktree：

```bash theme={null}
git worktree list
```

完成后删除 worktree：

```bash theme={null}
git worktree remove ../project-feature-a
```

完整命令参考见 [Git worktree 文档](https://git-scm.com/docs/git-worktree)。注意每个新 worktree 都需要初始化开发环境：安装依赖、设置虚拟环境，或运行项目所需的任何设置步骤。

## 非 git 版本控制

**Worktree 隔离默认基于 git。** 对于 SVN、Perforce、Mercurial 或其他系统，可以配置 [`WorktreeCreate` 和 `WorktreeRemove` hook](https://code.claude.com/docs/en/hooks) 来提供自定义的创建和清理逻辑。由于 hook 替代了默认的 git 行为，使用 `--worktree` 时不会处理 [`.worktreeinclude`](#将-gitignore-文件复制到-worktree)。请在 hook 脚本中自行复制所需的本地配置文件。

以下 `WorktreeCreate` hook 从 stdin 读取 worktree 名称，检出一份新的 SVN 工作副本，并输出目录路径供 Claude Code 用作会话的工作目录：

```json theme={null}
{
  "hooks": {
    "WorktreeCreate": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'NAME=$(jq -r .name); DIR=\"$HOME/.claude/worktrees/$NAME\"; svn checkout https://svn.example.com/repo/trunk \"$DIR\" >&2 && echo \"$DIR\"'"
          }
        ]
      }
    ]
  }
}
```

配合 `WorktreeRemove` hook 在会话结束时进行清理。输入 schema 和删除示例见 [hooks 参考文档](https://code.claude.com/docs/en/hooks)。

## 相关页面

Worktree 负责文件隔离。以下相关页面介绍如何将工作委派到这些隔离的 checkout 中，以及如何在会话间切换：

| 页面 | 说明 |
|------|------|
| [子代理](https://code.claude.com/docs/en/sub-agents) | 在会话内将工作委派给隔离的代理 |
| [代理团队](https://code.claude.com/docs/en/agent-teams) | 自动协调多个 Claude 会话 |
| [会话管理](https://code.claude.com/docs/en/sessions) | 命名、恢复和切换对话 |
| [桌面并行会话](https://code.claude.com/docs/en/desktop) | 桌面应用中基于 worktree 的并行会话 |
