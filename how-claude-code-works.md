---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】Claude Code 工作原理
description: 解析 Claude Code 的 Agent 循环（收集上下文→执行→验证）、内置五类工具、访问范围、执行环境差异、会话管理与上下文窗口机制、以及 Checkpoint/权限两道安全保障。
category: translation
tags: [claude-code, architecture, translation]
refs:
  - https://code.claude.com/docs/en/how-claude-code-works.md
---

# Claude Code 工作原理

> 理解 Agent 循环、内置工具，以及 Claude Code 如何与你的项目交互。

**Claude Code 是一个运行在终端里的 Agent 助手。** 它不只写代码——凡是命令行能做的事它都能帮你做：写文档、跑构建、搜文件、查资料等等。

本文涵盖核心架构、内置能力，以及[高效使用技巧](#高效使用-claude-code)。操作指南见 [Common workflows](https://code.claude.com/docs/en/common-workflows)；扩展机制（Skills、MCP、Hooks）见 [Extend Claude Code](https://code.claude.com/docs/en/features-overview)。

## Agent 循环

**Claude 处理任务分三个阶段：收集上下文 → 执行操作 → 验证结果。** 三个阶段相互交织，Claude 在整个过程中持续使用工具——搜索文件理解代码、编辑文件做修改、运行测试检查结果。

![Agent 循环：Prompt → 收集上下文 → 执行操作 → 验证结果 → 循环直到完成，你可以随时打断](assets/agentic-loop.svg)

循环会根据任务自适应调整：

- 问一个关于代码库的问题？可能只需要收集上下文。
- 修一个 Bug？三个阶段反复循环。
- 做一次重构？可能涉及大量验证。

Claude 根据上一步的结果决定下一步做什么，能连续串联几十个操作并随时修正方向。

**你也是循环的一部分。** 你可以随时打断，提供额外上下文，或让 Claude 换个思路。Claude 自主工作但始终对你的输入保持响应。

Agent 循环由两个核心组件驱动：[模型](#模型)负责推理，[工具](#工具)负责行动。Claude Code 作为**Agent 框架（harness）**，为 Claude 提供工具、上下文管理和执行环境，将语言模型变成一个真正有行动力的编程 Agent。

### 模型

**模型负责理解代码和推理任务。** Claude 能读任何语言的代码，理解组件之间的关联，找出完成目标需要改什么。复杂任务会被拆分成多个步骤，逐步执行，并根据执行结果动态调整。

[多种模型可选](https://code.claude.com/docs/en/model-config)，各有取舍。Sonnet 能处理大多数编码任务。Opus 在复杂架构决策上推理更强。会话中用 `/model` 切换，或启动时用 `claude --model <name>` 指定。

本文中说"Claude 选择"或"Claude 决定"时，指的是模型在做推理。

### 工具

**工具是 Claude Code 具备 Agent 能力的关键。** 没有工具，Claude 只能输出文本；有了工具，Claude 可以读代码、改文件、跑命令、搜索网络、调用外部服务。每次工具调用的返回结果都会反馈到循环中，驱动下一步决策。

内置工具分五大类：

| 类别 | Claude 的能力 |
|------|------|
| **文件操作** | 读文件、编辑代码、新建文件、重命名和重组 |
| **搜索** | 按模式查找文件、正则搜索内容、探索代码库 |
| **执行** | 运行 Shell 命令、启动服务器、跑测试、使用 git |
| **网络** | 搜索网页、获取文档、查错误信息 |
| **代码智能** | 编辑后查看类型错误和警告、跳转到定义、查找引用（需要 [code intelligence plugins](https://code.claude.com/docs/en/discover-plugins#code-intelligence)） |

此外还有生成子 Agent、向你提问等编排工具。完整列表见 [Tools available to Claude](https://code.claude.com/docs/en/tools-reference)。

Claude 根据你的 prompt 和过程中学到的信息自主选择工具。比如当你说 "fix the failing tests"，Claude 可能会：

1. 运行测试套件，看哪些失败了
2. 阅读错误输出
3. 搜索相关源文件
4. 读取这些文件理解代码
5. 编辑文件修复问题
6. 再次运行测试验证修复

每次工具调用给 Claude 新的信息，驱动下一步决策。这就是 Agent 循环的运作方式。

**扩展基础能力：** 内置工具是基座。你可以用 [Skills](https://code.claude.com/docs/en/skills) 扩展 Claude 的知识，用 [MCP](https://code.claude.com/docs/en/mcp) 连接外部服务，用 [Hooks](https://code.claude.com/docs/en/hooks) 自动化工作流，用 [子 Agent](https://code.claude.com/docs/en/sub-agents) 分派任务。这些扩展构建在核心 Agent 循环之上。如何选择合适的扩展方式见 [Extend Claude Code](https://code.claude.com/docs/en/features-overview)。

## Claude 能访问什么

**本节聚焦终端环境。** Claude Code 同样支持 [VS Code](https://code.claude.com/docs/en/vs-code)、[JetBrains IDEs](https://code.claude.com/docs/en/jetbrains) 等环境。

当你在某个目录运行 `claude` 时，Claude Code 能访问：

- **你的项目。** 当前目录及子目录下的所有文件；经你授权后也可访问其他位置的文件。
- **你的终端。** 你能跑的任何命令：构建工具、git、包管理器、系统工具、脚本。你能在命令行做的，Claude 也能做。
- **你的 git 状态。** 当前分支、未提交的更改、最近的 commit 历史。
- **你的 [CLAUDE.md](https://code.claude.com/docs/en/memory)。** 存放项目特定的指令、惯例和上下文的 markdown 文件，每次会话都会加载。
- **[自动记忆](https://code.claude.com/docs/en/memory#auto-memory)。** Claude 在工作中自动保存的经验，如项目模式和你的偏好。每次会话开始时加载 MEMORY.md 前 200 行或 25KB（取较先到达者）。
- **你配置的扩展。** [MCP 服务器](https://code.claude.com/docs/en/mcp) 连外部服务、[Skills](https://code.claude.com/docs/en/skills) 封装工作流、[子 Agent](https://code.claude.com/docs/en/sub-agents) 委派任务、[Claude in Chrome](https://code.claude.com/docs/en/chrome) 做浏览器交互。

**因为 Claude 能看到整个项目，所以它可以跨文件协作。** 当你说 "fix the authentication bug"，它会搜索相关文件、读多个文件理解上下文、协调修改多处代码、运行测试验证修复、按你要求提交更改。这和只看当前文件的行内代码助手本质不同。

## 环境与界面

**核心的 Agent 循环、工具和能力在所有地方一致。** 变化的只是代码执行的位置和交互方式。

### 执行环境

Claude Code 运行在三种环境中，各有不同的代码执行位置和权衡：

| 环境 | 代码执行位置 | 适用场景 |
|------|------|------|
| **本地** | 你的机器 | 默认方式。完全访问你的文件、工具和环境 |
| **云端** | Anthropic 托管的虚拟机 | 卸载任务、处理本地没有的仓库 |
| **远程控制** | 你的机器，通过浏览器操控 | 使用 Web UI 但代码仍在本地执行 |

### 界面

你可以通过终端、[桌面应用](https://code.claude.com/docs/en/desktop)、[IDE 扩展](https://code.claude.com/docs/en/vs-code)、[claude.ai/code](https://claude.ai/code)、[远程控制](https://code.claude.com/docs/en/remote-control)、[Slack](https://code.claude.com/docs/en/slack) 和 [CI/CD 流水线](https://code.claude.com/docs/en/github-actions) 使用 Claude Code。界面只决定你看到什么和如何交互，底层 Agent 循环完全相同。完整列表见 [Use Claude Code everywhere](https://code.claude.com/docs/en/overview#use-claude-code-everywhere)。

## 会话管理

**Claude Code 会将对话保存在本地。** 每条消息、工具调用和返回结果都以 JSONL 明文写入 `~/.claude/projects/`。这使得[回退](#通过-checkpoint-撤销更改)、[恢复和分叉](#恢复或分叉会话)成为可能。Claude 在修改代码前还会快照受影响的文件，方便你随时回滚。路径、保留策略和清除方式见 [application data in `~/.claude`](https://code.claude.com/docs/en/claude-directory#application-data)。

**会话之间相互独立。** 每个新会话从空白上下文窗口开始，不带之前的对话历史。Claude 可以通过[自动记忆](https://code.claude.com/docs/en/memory#auto-memory)跨会话保留经验，你也可以在 [CLAUDE.md](https://code.claude.com/docs/en/memory) 中写入持久指令。

### 跨分支工作

每个 Claude Code 会话绑定到当前目录。`/resume` 选择器默认显示当前 worktree 的会话，也可以用快捷键扩展到其他 worktree 或项目。详见 [Manage sessions](https://code.claude.com/docs/en/sessions#use-the-session-picker)。

Claude 看到的是当前分支的文件。切换分支后，Claude 看到新分支的文件，但对话历史保持不变——它记得之前讨论过什么。

由于会话绑定到目录，你可以用 [git worktrees](https://code.claude.com/docs/en/worktrees) 创建独立目录来并行运行多个 Claude 会话。

### 恢复或分叉会话

- **恢复（Resume）：** 用 `claude --continue` 或 `claude --resume` 重新打开已有会话，新消息追加到同一个 session ID。
- **分叉（Fork）：** 用 `--fork-session` 或 `/branch` 将历史复制到新 session ID，原会话不变。

![会话连续性：Resume 继续同一会话，Fork 创建新分支新 ID](assets/session-continuity.svg)

恢复的标志、`/resume` 选择器、命名规则，以及同一会话在两个终端打开会怎样，详见 [Manage sessions](https://code.claude.com/docs/en/sessions)。

### 上下文窗口

**上下文窗口装着你的对话历史、文件内容、命令输出、CLAUDE.md、自动记忆、已加载的 Skills 和系统指令。** 随着工作推进，上下文会逐渐填满。Claude 会自动压缩（compact），但早期对话中的指令可能丢失。把持久性规则放到 CLAUDE.md 中，用 `/context` 查看空间占用情况。

交互式了解上下文加载时机和内容，见 [Explore the context window](https://code.claude.com/docs/en/context-window)。

#### 上下文满了怎么办

**Claude Code 会自动管理上下文。** 接近上限时，先清理旧的工具输出，必要时再总结对话。你的请求和关键代码片段会保留；早期对话中的详细指令可能丢失。所以——**把持久规则放在 CLAUDE.md，别依赖对话历史。**

控制压缩时保留什么的方法：在 CLAUDE.md 中添加 "Compact Instructions" 章节，或带焦点运行 `/compact`（如 `/compact focus on the API changes`）。

如果单个文件或工具输出过大，导致每次总结后上下文立刻再次填满，Claude Code 会在几次尝试后停止自动压缩并报错，而不是无限循环。恢复方法见 [Auto-compaction stops with a thrashing error](https://code.claude.com/docs/en/troubleshooting#auto-compaction-stops-with-a-thrashing-error)。

用 `/context` 查看空间占用。MCP 工具定义默认延迟加载——只有工具名占上下文，具体定义在 Claude 使用该工具时才加载（通过 [tool search](https://code.claude.com/docs/en/mcp#scale-with-mcp-tool-search)）。用 `/mcp` 查看每个 server 的上下文开销。

#### 用 Skills 和子 Agent 管理上下文

除了压缩，还有其他方式控制上下文内容。

**[Skills](https://code.claude.com/docs/en/skills) 按需加载。** Claude 在会话开始时只看到 Skill 描述，完整内容在使用时才加载。对于手动触发的 Skill，设置 `disable-model-invocation: true` 可以让描述也不进入上下文，直到你主动使用。对别人写的 Skill，可以用 [`skillOverrides`](https://code.claude.com/docs/en/skills#override-skill-visibility-from-settings) 从设置中实现同样效果。

**[子 Agent](https://code.claude.com/docs/en/sub-agents) 拥有独立的上下文窗口**，完全不占用主对话空间。完成后只返回一个摘要。这种隔离性正是子 Agent 在长会话中有价值的原因。

各功能的上下文开销见 [context costs](https://code.claude.com/docs/en/features-overview#understand-context-costs)；减少 token 用量的技巧见 [reduce token usage](https://code.claude.com/docs/en/costs#reduce-token-usage)。

## 安全保障：Checkpoint 和权限

**Claude 有两道安全机制：Checkpoint 让你撤销文件更改，权限控制 Claude 能不经询问做什么。**

### 通过 Checkpoint 撤销更改

**每次文件编辑都可逆。** 在修改任何文件之前，Claude 会快照当前内容。出了问题，按两次 `Esc` 回退到之前的状态，或直接让 Claude 撤销。

Checkpoint 是会话本地的，和 git 独立。它只覆盖文件更改。影响远程系统的操作（数据库、API、部署）无法通过 Checkpoint 回退——这正是 Claude 在运行有外部副作用的命令前会先询问你的原因。

### 控制 Claude 的行为权限

按 `Shift+Tab` 在权限模式之间切换：

| 模式 | 行为 |
|------|------|
| **Default** | 文件编辑和 Shell 命令都需要确认 |
| **Auto-accept edits** | 文件编辑和 `mkdir`、`mv` 等常见文件系统命令自动通过，其他命令仍需确认 |
| **Plan mode** | Claude 探索代码并提出方案，但不修改源文件；权限提示和 Default 相同 |
| **Auto mode** | Claude 通过后台安全检查评估所有操作。目前为 Research Preview |

你还可以在 `.claude/settings.json` 中允许特定命令（如 `npm test`、`git status`），这样 Claude 就不用每次都问。设置可以从组织级策略到个人偏好分层覆盖。详见 [Permissions](https://code.claude.com/docs/en/permissions)。

---

## 高效使用 Claude Code

**以下技巧帮你从 Claude Code 获得更好的结果。**

### 向 Claude Code 求助

**Claude Code 可以教你怎么用它。** 问它 "how do I set up hooks?" 或 "what's the best way to structure my CLAUDE.md?"，它会直接解释。

内置命令也能引导你完成配置：

- `/init` 引导你为项目创建 CLAUDE.md
- `/agents` 帮你配置自定义子 Agent
- `/doctor` 诊断安装的常见问题

### 这是一场对话

**Claude Code 是对话式的。你不需要完美的 prompt。** 先说你想要什么，然后迭代：

```text theme={null}
Fix the login bug
```

[Claude 调查，尝试一个方案]

```text theme={null}
That's not quite right. The issue is in the session handling.
```

[Claude 调整方向]

第一次不对不需要从头来过，直接迭代就好。

#### 随时打断和引导

你可以在任何时候重定向 Claude，无需等它完成或重来：

- **按 `Esc`**：立即停止 Claude。正在运行的工具调用被取消，Claude 等待你的下一条指令。
- **输入修正后按 `Enter`**：不停止当前运行的工具直接发送。当前操作完成后 Claude 立即读取你的修正，在决定下一步前先做调整。

### 开头就说具体

**初始 prompt 越精确，后续修正越少。** 引用具体文件、提到约束条件、指出参考模式。

```text theme={null}
The checkout flow is broken for users with expired cards.
Check src/payments/ for the issue, especially token refresh.
Write a failing test first, then fix it.
```

模糊的 prompt 也能工作，但你要花更多时间引导。像上面这样具体的 prompt 经常一次就成功。

### 给 Claude 验证手段

**Claude 能自我验证时表现更好。** 提供测试用例、贴预期 UI 的截图、或定义期望输出。

```text theme={null}
Implement validateEmail. Test cases: 'user@example.com' → true,
'invalid' → false, 'user@.com' → false. Run the tests after.
```

做视觉类工作时，贴一张设计稿截图，让 Claude 把它的实现和设计稿对比。

### 先探索再实现

**对复杂问题，把研究和编码分开。** 用 Plan mode（按两次 `Shift+Tab`）先分析代码库：

```text theme={null}
Read src/auth/ and understand how we handle sessions.
Then create a plan for adding OAuth support.
```

审查方案，通过对话细化，然后让 Claude 实现。这种两阶段方法比直接写代码效果更好。

### 委托而非指令

**把 Claude 当一个能力强的同事来委托，而不是逐行下指令。** 给上下文和方向，相信它能搞定细节：

```text theme={null}
The checkout flow is broken for users with expired cards.
The relevant code is in src/payments/. Can you investigate and fix it?
```

你不需要指定读哪些文件或跑什么命令。Claude 自己会搞清楚。

## 后续阅读

- [Extend Claude Code](https://code.claude.com/docs/en/features-overview) — 添加 Skills、MCP 连接和自定义命令
- [Common workflows](https://code.claude.com/docs/en/common-workflows) — 常见任务的逐步指南
