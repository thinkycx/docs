---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】常见工作流
description: Claude Code 日常开发中的工作流指南：探索代码库、修复 Bug、重构、测试、PR、文档等 Prompt 模式，以及恢复会话、Worktree 并行、计划模式、子 Agent 委托、脚本管道等进阶用法。
category: translation
tags: [claude-code, workflows, translation]
refs:
  - https://code.claude.com/docs/en/common-workflows.md
---

# 常见工作流

> 日常开发中使用 Claude Code 的分步指南：探索代码库、修复 Bug、重构、测试等常见场景。

本页收集了日常开发中的短小配方。关于更高层次的 Prompt 技巧和上下文管理指导，参见 [Best practices](https://code.claude.com/docs/en/best-practices)（[中文](best-practices.md)）。

本页涵盖：

- [Prompt 模式](#prompt-模式)——探索代码、修 Bug、重构、测试、PR、文档
- [恢复历史会话](#恢复历史会话)——跨多次坐下来继续同一任务
- [Worktree 并行会话](#worktree-并行会话)——并发编辑互不冲突
- [先规划再动手](#先规划再动手)——在落盘前审查变更方案
- [委托研究给子 Agent](#委托研究给子-agent)——保持主上下文干净
- [管道式脚本调用](#管道式脚本调用)——CI 和批处理场景

---

## Prompt 模式

**针对探索代码、调试、重构、测试、PR、文档等日常任务的 Prompt 范式。** 每种模式都可在任何 Claude Code 界面使用，根据项目实际调整措辞即可。

### 理解新代码库

关于在 Monorepo 或大型代码库中配置 Claude Code，参见 [Monorepos and large repos](https://code.claude.com/docs/en/large-codebases)。

#### 快速获取代码库概览

**场景：刚加入一个新项目，需要快速理解整体结构。**

| 步骤 | 操作 |
| --- | --- |
| 1. 进入项目根目录 | `cd /path/to/project` |
| 2. 启动 Claude Code | `claude` |
| 3. 请求高层概览 | `give me an overview of this codebase` |
| 4. 深入特定组件 | `explain the main architecture patterns used here` / `what are the key data models?` / `how is authentication handled?` |

> Tips:
> - 先问宽泛问题，再逐步缩小范围
> - 询问项目使用的编码规范和设计模式
> - 让 Claude 给出项目特有术语的词汇表

#### 定位相关代码

**场景：需要找到与某个功能相关的代码文件。**

| 步骤 | 操作 |
| --- | --- |
| 1. 让 Claude 查找相关文件 | `find the files that handle user authentication` |
| 2. 了解组件间交互 | `how do these authentication files work together?` |
| 3. 理解执行流程 | `trace the login process from front-end to database` |

> Tips:
> - 描述要找的东西时尽量具体
> - 使用项目本身的领域语言
> - 安装 [code intelligence plugin](https://code.claude.com/docs/en/discover-plugins#code-intelligence) 让 Claude 获得精确的"跳转到定义"和"查找引用"能力

---

### 高效修复 Bug

**场景：遇到错误信息，需要定位并修复其来源。**

| 步骤 | 操作 |
| --- | --- |
| 1. 把错误分享给 Claude | `I'm seeing an error when I run npm test` |
| 2. 请求修复建议 | `suggest a few ways to fix the @ts-ignore in user.ts` |
| 3. 应用修复 | `update user.ts to add the null check you suggested` |

> Tips:
> - 告诉 Claude 复现问题的命令以获取完整堆栈
> - 说明复现步骤
> - 告知是偶发还是必现

---

### 重构代码

**场景：需要将旧代码更新为现代模式和实践。**

| 步骤 | 操作 |
| --- | --- |
| 1. 识别需要重构的遗留代码 | `find deprecated API usage in our codebase` |
| 2. 获取重构建议 | `suggest how to refactor utils.js to use modern JavaScript features` |
| 3. 安全地应用变更 | `refactor utils.js to use ES2024 features while maintaining the same behavior` |
| 4. 验证重构结果 | `run tests for the refactored code` |

> Tips:
> - 让 Claude 解释现代方式的优势
> - 必要时要求保持向后兼容
> - 以小的、可测试的增量进行重构

---

### 编写测试

**场景：需要为未覆盖的代码添加测试。**

| 步骤 | 操作 |
| --- | --- |
| 1. 识别未测试的代码 | `find functions in NotificationsService.swift that are not covered by tests` |
| 2. 生成测试脚手架 | `add tests for the notification service` |
| 3. 添加有意义的测试用例 | `add test cases for edge conditions in the notification service` |
| 4. 运行并验证 | `run the new tests and fix any failures` |

**Claude 会遵循项目已有的模式和约定来生成测试。** 在请求测试时，明确说明要验证什么行为。Claude 会检查已有测试文件，匹配其风格、框架和断言模式。

要获得全面覆盖，让 Claude 识别你可能遗漏的边界情况。Claude 能分析代码路径，建议针对错误条件、边界值和意外输入的测试。

---

### 创建 Pull Request

**你可以直接让 Claude 创建 PR（"create a pr for my changes"），也可以分步引导：**

| 步骤 | 操作 |
| --- | --- |
| 1. 总结变更 | `summarize the changes I've made to the authentication module` |
| 2. 生成 PR | `create a pr` |
| 3. 审查与完善 | `enhance the PR description with more context about the security improvements` |

当你通过 `gh pr create` 创建 PR 后，会话会自动关联到该 PR。之后可通过 `claude --from-pr <number>` 返回，或在 [`/resume` picker](https://code.claude.com/docs/en/sessions#use-the-session-picker) 搜索中粘贴 PR URL。

> Tip: 提交前审查 Claude 生成的 PR，让 Claude 标注潜在风险或需注意的事项。

---

### 处理文档

**场景：需要为代码添加或更新文档。**

| 步骤 | 操作 |
| --- | --- |
| 1. 识别未文档化的代码 | `find functions without proper JSDoc comments in the auth module` |
| 2. 生成文档 | `add JSDoc comments to the undocumented functions in auth.js` |
| 3. 审查与增强 | `improve the generated documentation with more context and examples` |
| 4. 验证文档 | `check if the documentation follows our project standards` |

> Tips:
> - 指定你想要的文档风格（JSDoc、docstrings 等）
> - 要求在文档中包含示例
> - 重点为公共 API、接口和复杂逻辑添加文档

---

### 在笔记和非代码目录中工作

**Claude Code 可在任意目录中运行。** 在笔记库、文档文件夹或任何 Markdown 文件集合中启动它，就能像处理代码一样搜索、编辑和重组内容。

`.claude/` 目录和 `CLAUDE.md` 与其他工具的配置目录共存不冲突。Claude 每次工具调用时重新读取文件，因此下次读取时能看到你在其他应用中做的编辑。

---

### 处理图片

**场景：需要 Claude 帮助分析代码库中的图片内容。**

| 步骤 | 操作 |
| --- | --- |
| 1. 将图片加入对话 | 拖拽到窗口 / `ctrl+v` 粘贴 / 提供路径（如 `Analyze this image: /path/to/image.png`） |
| 2. 让 Claude 分析 | `What does this image show?` / `Describe the UI elements in this screenshot` / `Are there any problematic elements in this diagram?` |
| 3. 以图片作为上下文 | `Here's a screenshot of the error. What's causing it?` / `This is our current database schema. How should we modify it for the new feature?` |
| 4. 从视觉内容获取代码建议 | `Generate CSS to match this design mockup` / `What HTML structure would recreate this component?` |

> Tips:
> - 当文字描述太累赘或不够清晰时使用图片
> - 可用于错误截图、UI 设计稿、架构图
> - 一次对话中可使用多张图片
> - 当 Claude 引用图片时（如 `[Image #1]`），`Cmd+Click`（Mac）或 `Ctrl+Click`（Windows/Linux）链接可在默认查看器中打开

---

### 用 @ 引用文件和目录

**使用 `@` 快速包含文件或目录，无需等待 Claude 自己去读取。**

| 用法 | 示例 | 效果 |
| --- | --- | --- |
| 引用单个文件 | `Explain the logic in @src/utils/auth.js` | 整个文件内容进入对话 |
| 引用目录 | `What's the structure of @src/components?` | 提供目录列表 |
| 引用 MCP 资源 | `Show me the data from @github:repos/owner/repo/issues` | 从已连接的 MCP 服务器获取数据，格式为 `@server:resource`。详见 [MCP resources](https://code.claude.com/docs/en/mcp#use-mcp-resources) |

> Tips:
> - 文件路径可以是相对或绝对路径
> - `@` 文件引用会自动把该文件所在目录及父目录中的 `CLAUDE.md` 加入上下文
> - 目录引用展示文件列表而非内容
> - 可在单条消息中引用多个文件（如 `@file1.js and @file2.js`）

---

### 定时运行 Claude

**场景：让 Claude 定期自动处理任务，如每天早上审查 PR、每周审计依赖、夜间检查 CI 失败。**

根据任务运行位置选择方案：

| 方案 | 运行位置 | 适用场景 |
| --- | --- | --- |
| [Routines](https://code.claude.com/docs/en/routines) | Anthropic 托管基础设施 | 即使电脑关机也要运行的任务。除定时触发外还支持 API 调用和 GitHub 事件触发。在 [claude.ai/code/routines](https://claude.ai/code/routines) 配置。 |
| [Desktop scheduled tasks](https://code.claude.com/docs/en/desktop-scheduled-tasks) | 你的本机（桌面 App） | 需要直接访问本地文件、工具或未提交变更的任务 |
| [GitHub Actions](https://code.claude.com/docs/en/github-actions) | CI 管道 | 与 repo 事件（如 PR 打开）绑定的任务，或需要写在 workflow 配置中的 cron 调度 |
| [`/loop`](https://code.claude.com/docs/en/scheduled-tasks) | 当前 CLI 会话 | 会话打开期间的快速轮询。新建对话时停止；`--resume` 和 `--continue` 可恢复未过期的任务 |

> Tip: 为定时任务写 Prompt 时，明确定义成功标准和结果处理方式。任务自主运行，无法追问你。例如："Review open PRs labeled `needs-review`, leave inline comments on any issues, and post a summary in the `#eng-reviews` Slack channel."

---

### 询问 Claude 自身的能力

**Claude 内置了对自身文档的访问，可以回答关于自身功能和限制的问题。**

示例问题：

```text
can Claude Code create pull requests?
```

```text
how does Claude Code handle permissions?
```

```text
what skills are available?
```

```text
how do I use MCP with Claude Code?
```

```text
how do I configure Claude Code for Amazon Bedrock?
```

```text
what are the limitations of Claude Code?
```

> Note: Claude 基于文档回答这些问题。如需实操演示，运行 `/powerup` 获取带动画 Demo 的互动课程，或参考上面的具体工作流章节。

> Tips:
> - 无论你使用哪个版本，Claude 始终能访问最新的 Claude Code 文档
> - 问具体问题能获得详细回答
> - Claude 能解释 MCP 集成、企业配置、高级工作流等复杂功能

---

## 恢复历史会话

**当一个任务跨越多次坐下来工作时，接着上次继续而不是重新解释上下文。** Claude Code 在本地保存所有对话。

```bash
claude --continue
```

这会恢复当前目录中最近的会话；如果没有则输出 `No conversation found to continue` 并退出。使用 `claude --resume` 从列表中选择，或在运行中的会话里输入 `/resume`。详见 [Manage sessions](https://code.claude.com/docs/en/sessions)。

---

## Worktree 并行会话

**在一个终端做 Feature 的同时让 Claude 在另一个终端修 Bug，编辑互不冲突。** 每个 Worktree 是一个独立的 checkout，有自己的分支。

```bash
claude --worktree feature-auth
```

在第二个终端用不同名称运行同样的命令，即可启动隔离的并行会话。详见 [Worktrees](https://code.claude.com/docs/en/worktrees) 了解清理、`.worktreeinclude` 和非 git VCS 支持。若要从一个屏幕监控并行会话而非切换终端，参见 [background agents](https://code.claude.com/docs/en/agent-view)。

---

## 先规划再动手

**对于你想在落盘前审查的变更，切换到 Plan 模式。** Claude 读取文件并提出方案，但在你批准前不会做任何编辑。

```bash
claude --permission-mode plan
```

也可以在会话中按 `Shift+Tab` 切换到 Plan 模式。详见 [Plan mode](https://code.claude.com/docs/en/permission-modes#analyze-before-you-edit-with-plan-mode) 了解审批流程和在编辑器中修改方案。

---

## 委托研究给子 Agent

**探索大型代码库会填满上下文窗口。委托给子 Agent 执行探索，只把结论带回来。**

```text
use a subagent to investigate how our auth system handles token refresh
```

子 Agent 在自己的上下文窗口中读取文件并汇报总结。详见 [Subagents](https://code.claude.com/docs/en/sub-agents) 了解如何定义自带工具和 Prompt 的自定义 Agent。

---

## 管道式脚本调用

**以非交互方式运行 Claude，用于 CI、pre-commit hooks 或批处理。** Stdin 和 stdout 与任何 Unix 工具一样工作。

```bash
git log --oneline -20 | claude -p "summarize these recent commits"
```

详见 [Non-interactive mode](https://code.claude.com/docs/en/headless) 了解输出格式、权限标志和 fan-out 模式。

---

## 接下来

| 主题 | 说明 |
| --- | --- |
| [Best practices](https://code.claude.com/docs/en/best-practices)（[中文](best-practices.md)） | 让 Claude Code 发挥最大价值的模式 |
| [Manage sessions](https://code.claude.com/docs/en/sessions) | 恢复、命名和分支对话 |
| [Worktrees](https://code.claude.com/docs/en/worktrees) | 运行隔离的并行会话 |
| [Extend Claude Code](https://code.claude.com/docs/en/features-overview)（[中文](features-overview.md)） | 添加 Skills、Hooks、MCP、子 Agent 和 Plugins |
