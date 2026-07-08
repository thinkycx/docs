---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】术语表
description: Claude Code 术语定义汇总。涵盖 agentic loop、compaction、CLAUDE.md、hooks、subagents、MCP 等核心概念的含义和相关链接。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/glossary.md
  - en-source/glossary.md
---

# 术语表

> Claude Code 术语定义。每个条目链接到该概念的详细页面。模型层面的概念（如 tokens、temperature、RAG）请参见 [platform 术语表](https://platform.claude.com/docs/en/about-claude/glossary)。

## A

### Agent teams（代理团队）

**多个独立的 Claude Code 会话由一个 team lead 协调，共享任务列表和点对点消息传递。** 与[子代理](#subagent子代理)不同，后者在单个会话内运行且仅向父级报告，团队成员各自有独立的上下文窗口，你可以直接与任何一个交互。Agent teams 为实验性功能，需设置 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 启用。

详见：[Run agent teams](https://code.claude.com/docs/en/agent-teams)

### Agentic coding（代理式编程）

**AI 能自主读取文件、运行命令、进行修改的工作流**，而非仅回复需要你手动应用的文本。Claude Code 是代理式的，因为它有[工具](#tool工具)让它能行动，而不只是建议。

详见：[How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works)

### Agentic harness（代理式基座）

**将语言模型转变为有能力的编程代理的工具、上下文管理和执行环境。** Claude Code 就是基座；Claude 是其中的模型。基座提供文件访问、shell 执行、权限把关、memory 加载以及将动作串联起来的循环。

详见：[How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works)

### Agentic loop（代理循环）

**Claude 处理每个任务所经历的循环：收集上下文、执行动作、验证结果、重复直到完成。** 每次工具使用返回信息供下一步判断。你可以随时中断循环重新引导。大多数扩展点（包括 [hooks](#hookhook)、[skills](#skillskill) 和 [MCP](#mcpmodel-context-protocol)）接入此循环的特定阶段。

详见：[How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works#the-agentic-loop)

### Artifact

**Claude Code 从会话发布到 claude.ai 私有 URL 的实时交互式网页**，让你可视化查看输出或在组织内分享，而非阅读终端文本。会话重新发布时页面原地更新。

详见：[Share session output as artifacts](https://code.claude.com/docs/en/artifacts)

### Auto memory（自动记忆）

**Claude 基于你的纠正和偏好为自己写的笔记**，按 git 仓库存储在 `~/.claude/projects/` 下。同一仓库的所有 worktree 共享一个自动记忆目录。`MEMORY.md` 索引的前 200 行或 25 KB 在每个会话开始时加载。自动记忆是 [CLAUDE.md](#claudemd) 的 Claude 书写版本（后者由你编写）。

详见：[Auto memory](https://code.claude.com/docs/en/memory#auto-memory)

### Auto mode（自动模式）

**一种[权限模式](#permission-mode权限模式)，由独立的分类器模型在后台审查动作**，大多数操作无需审批提示；显式的 ask 规则仍会提示。分类器阻止范围升级、不受信任的基础设施和 [prompt 注入](#prompt-injection)。它从不查看工具结果，因此注入的指令无法影响其决策。Auto mode 为研究预览。

详见：[Eliminate prompts with auto mode](https://code.claude.com/docs/en/permission-modes#eliminate-prompts-with-auto-mode)

## B

### Bare mode

**启动标志 `--bare`，跳过 hooks、skills、plugins、MCP 服务器、auto memory 和 CLAUDE.md 的自动发现。** 仅显式传递的标志生效。推荐用于 CI 和脚本调用，确保跨机器行为一致而不受本地配置影响。

详见：[Start faster with bare mode](https://code.claude.com/docs/en/headless#start-faster-with-bare-mode)

### Bundled skills（内置 skills）

**Claude Code 内置的基于 prompt 的 playbook**，如 `/batch`、`/code-review`、`/debug` 和 `/loop`。与执行固定逻辑的内置命令不同，bundled skills 给 Claude 一个详细 prompt 让它编排工作，因此可以生成代理、读取文件并适应你的代码库。

详见：[Bundled skills](https://code.claude.com/docs/en/skills#bundled-skills)

## C

### Channel（通道）

**将事件推送到运行中会话的 [MCP 服务器](#mcpmodel-context-protocol)**，让 Claude 在你离开终端时对发生的事情做出反应。通道可以双向：Claude 读取入站事件并通过同一通道回复。Telegram、Discord 和 iMessage 包含在研究预览中。

详见：[Channels](https://code.claude.com/docs/en/channels)

### Checkpoint（检查点）

**在你每次发送 prompt 时创建的恢复点。** Claude Code 在每次编辑前快照文件，以便检查点能恢复它们。按 `Esc` 两次或运行 `/rewind` 可恢复代码、对话或两者。检查点是会话本地的，独立于 git，不跟踪通过 Bash 工具所做的更改。

详见：[Checkpointing](https://code.claude.com/docs/en/checkpointing)

### `.claude` 目录

**Claude Code 读取项目级配置的目录**：settings、hooks、skills、子代理、规则和 auto memory。项目在根目录有 `.claude/`；你的用户级默认在 `~/.claude/`。

详见：[The `.claude` directory](https://code.claude.com/docs/en/claude-directory)

### CLAUDE.md

**你为 Claude 编写的持久指令 markdown 文件**，在每个会话开始时作为用户消息加载在系统 prompt 之后。放置项目约定、架构说明和"始终做 X"的规则。项目根目录的 CLAUDE.md 在 [compaction](#compaction压缩) 后保留并从磁盘重新读取。

可以放在项目级 `./CLAUDE.md` 或 `./.claude/CLAUDE.md`，用户级 `~/.claude/CLAUDE.md`，或作为组织的[托管策略](#managed-settings托管设置)。所有发现的文件拼接到上下文中而非互相覆盖，从最宽泛到最具体排序。

详见：[CLAUDE.md files](https://code.claude.com/docs/en/memory#claude-md-files)

### Command（命令）

**通过在 prompt 中输入 `/name` 调用的可复用指令。** 内置命令如 `/clear`、`/model`、`/compact` 控制会话。你可以在 `.claude/commands/` 中定义自己的命令，或从[插件](#plugin插件)安装。[Skills](#skillskill) 是打包多步骤命令的推荐方式。

详见：[Commands](https://code.claude.com/docs/en/commands) · [Skills](https://code.claude.com/docs/en/skills)

### Compaction（压缩）

**当[上下文窗口](#context-window上下文窗口)接近限制时自动总结对话。** 先清除较旧的工具输出，再总结对话。项目根目录的 CLAUDE.md 和 auto memory 在压缩后保留并从磁盘重载；仅在对话中给出的指令可能丢失。运行 `/compact` 手动触发，可带聚焦如 `/compact focus on the API changes`。

详见：[What survives compaction](https://code.claude.com/docs/en/context-window#what-survives-compaction)

### Context window（上下文窗口）

**会话的工作记忆**，容纳对话历史、文件内容、命令输出、CLAUDE.md、auto memory、已加载 skills 和系统指令。随着工作进行上下文填满直到 [compaction](#compaction压缩) 总结它。运行 `/context` 查看占用情况。

详见：[Explore the context window](https://code.claude.com/docs/en/context-window)

## D

### Dispatch

**手机发起的任务路由器**，当你从 Claude 移动应用发送编程任务时在 Desktop 应用中生成一个 Claude Code 会话。你的 prompt 自动路由到正确的工具。Pro 和 Max 计划可用。

详见：[Sessions from Dispatch](https://code.claude.com/docs/en/desktop#sessions-from-dispatch)

## E

### Effort level（推理级别）

**控制 Claude 在每轮使用多少 adaptive-reasoning 思考预算的设置。** 更高的 effort 意味着更多思考 token 和更深推理；更低则更快更便宜。

详见：[Adjust effort level](https://code.claude.com/docs/en/model-config#adjust-effort-level)

### Extended thinking（扩展思考）

**模型在响应前进行的可见逐步推理。** 可通过 [effort level](#effort-level推理级别) 调整，或用 `MAX_THINKING_TOKENS` 限制思考 token。思考以灰色斜体文字显示在终端。

详见：[Use extended thinking](https://code.claude.com/docs/en/model-config#extended-thinking)

## H

### Hook

**在 Claude Code 生命周期特定点自动执行的用户定义处理器**，如工具运行前、文件编辑后或会话开始时。处理器可以是 shell 命令、HTTP 端点、MCP 工具、LLM prompt 或子代理。Hooks 是确定性的：在固定生命周期点触发而非由模型决定。

配置有三个层级：
- **Hook event**：生命周期点
- **Matcher**：过滤哪些事件触发它
- **Hook handler**：运行什么

详见：[Get started with hooks](https://code.claude.com/docs/en/hooks-guide) · [Hooks reference](https://code.claude.com/docs/en/hooks)

## M

### Managed settings（托管设置）

**由 IT 或 DevOps 组织级强制执行的设置**，从 Anthropic 服务器通过管理控制台交付，或部署到 `~/.claude` 之外的操作系统级路径。用户和项目设置无法覆盖托管设置。用于安全策略、合规要求或跨设备群标准化工具。

详见：[Server-managed settings](https://code.claude.com/docs/en/server-managed-settings)

### MCP（Model Context Protocol）

**连接 AI 工具到外部数据源和服务的开放标准。** MCP 服务器赋予 Claude 新的 Slack、Jira、数据库、浏览器等集成工具。通过 `/mcp` 或添加到 `.mcp.json` 连接服务器。

详见：[Model Context Protocol](https://code.claude.com/docs/en/mcp)

### MCP Tool Search

**延迟 MCP 工具 schema 加载直到需要时的上下文节省机制。** 启动时仅加载工具名称；Claude 在决定使用特定工具时按需获取完整 schema。这使空闲的 MCP 服务器不会消耗太多上下文。

详见：[Scale with MCP Tool Search](https://code.claude.com/docs/en/mcp#scale-with-mcp-tool-search)

## N

### Non-interactive mode（非交互模式）

**执行单个 prompt 并退出而不进入对话会话的模式**，通过 `-p` 或 `--print` 调用。用于 CI、脚本和管道。[Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) 是 Python 和 TypeScript 的等效物。以前称为 headless mode。

详见：[Run Claude Code programmatically](https://code.claude.com/docs/en/headless)

## O

### Output style（输出风格）

**修改 Claude 系统 prompt 以改变响应行为、语气或格式的配置。** Output style 关闭默认系统 prompt 中软件工程相关的部分，不同于 [CLAUDE.md](#claudemd)（后者作为系统 prompt 后的用户消息传递）。内置风格包括 Default、Proactive、Explanatory 和 Learning。

详见：[Output styles](https://code.claude.com/docs/en/output-styles)

## P

### Permission mode（权限模式）

**会话的基线审批行为。** 在 CLI 中用 `Shift+Tab` 切换，或在 VS Code、Desktop 和 claude.ai 中使用模式选择器。可用模式：`default`、`acceptEdits`、`plan`、`auto`、`dontAsk`、`bypassPermissions`。

`default` 模式在 CLI 和 VS Code/JetBrains 扩展中标记为 Manual，Claude Code 接受 `manual` 作为别名。

详见：[Choose a permission mode](https://code.claude.com/docs/en/permission-modes)

### Permission rule（权限规则）

**基于工具名和参数模式允许、询问或拒绝工具调用的 settings 条目。** 规则按 deny → ask → allow 求值，首次匹配胜出。权限规则是在更宽泛的[权限模式](#permission-mode权限模式)之上的细粒度控制。

详见：[Configure permissions](https://code.claude.com/docs/en/permissions)

### Plan mode

**Claude 只研究和提出修改方案而不编辑源文件的[权限模式](#permission-mode权限模式)。** 它可以读取、搜索和运行探索命令，然后在修改任何内容前呈现计划等待批准。通过 `/plan` 或 `Shift+Tab` 进入。

详见：[Analyze before you edit with plan mode](https://code.claude.com/docs/en/permission-modes#analyze-before-you-edit-with-plan-mode)

### Plugin（插件）

**将 skills、hooks、子代理和 MCP 服务器打包为单个可安装单元的 bundle。** 插件 skills 命名为 `plugin-name:skill-name` 以便多插件共存。通过[市场](https://code.claude.com/docs/en/plugin-marketplaces)跨团队分发。

详见：[Plugins](https://code.claude.com/docs/en/plugins)

### Project trust（项目信任）

**在 Claude Code 加载目录配置前接受该目录的对话框。** 接受按项目目录保存，除了 home 目录（仅当前会话有效，每次启动重新提示）。信任把关市场插件的自动安装和项目定义 hooks 的执行。

详见：[The `.claude` directory](https://code.claude.com/docs/en/claude-directory)

### Prompt injection

**嵌入在文件、网页或工具结果中的恶意指令，试图将 Claude 重定向到你未要求的操作。** Claude Code 的防御包括权限系统、命令注入检测和信任验证。[Auto mode](#auto-mode自动模式) 添加了扫描工具结果的服务器端探测和从不查看工具结果的分类器。

详见：[Protect against prompt injection](https://code.claude.com/docs/en/security#protect-against-prompt-injection)

## R

### Remote Control

**通过 claude.ai 从手机或浏览器继续本地 Claude Code 会话的方式。** 代码留在你的机器上，只有 UI 是远程的。不同于 Claude Code on the web（运行在云沙箱中）。

详见：[Remote Control](https://code.claude.com/docs/en/remote-control)

### Rules（规则）

**`.claude/rules/` 中的模块化指令文件**，与 CLAUDE.md 一起加载。规则可以通过 YAML `paths:` frontmatter 限定路径范围，仅在 Claude 读取匹配文件时加载，保持上下文精简。

详见：[Organize rules with `.claude/rules/`](https://code.claude.com/docs/en/memory#organize-rules-with-claude/rules/)

## S

### Sandboxing（沙箱）

**Bash 工具的操作系统级文件系统和网络隔离。** 命令在你预先定义的边界内运行，Claude 可在其中自由工作而无需逐命令审批提示。沙箱是独立于[权限规则](#permission-rule权限规则)的层。

详见：[Sandboxing](https://code.claude.com/docs/en/sandboxing)

### Session（会话）

**绑定到当前目录的对话，有自己独立的[上下文窗口](#context-window上下文窗口)。** 可用 `claude -c` 恢复，用 `--fork-session` 分叉，或跨终端并行运行。`/clear` 开始新会话；之前的通过 `/resume` 可用。

详见：[Work with sessions](https://code.claude.com/docs/en/how-claude-code-works#work-with-sessions)

### Settings layers（设置层级）

**Claude Code 读取配置的层级**，优先级从高到低：[托管策略](#managed-settings托管设置)、命令行参数、`.claude/settings.local.json`、`.claude/settings.json`、`~/.claude/settings.json`。数组跨层合并；标量由更高层覆盖更低层。

详见：[Settings files](https://code.claude.com/docs/en/settings#settings-files)

### Skill

**包含指令、知识或工作流的 `SKILL.md` 文件，Claude 添加到其工具箱。** Claude 在相关时自动加载 skill，或你通过 `/skill-name` 直接调用。Skills 是自定义命令的推荐继任者。

详见：[Extend Claude with skills](https://code.claude.com/docs/en/skills)

### Subagent（子代理）

**在自己的上下文窗口中运行的专门 AI 助手**，有自定义系统 prompt、特定工具访问和独立权限。它完成委派任务并向主对话返回摘要。用子代理将大型探索排除在主上下文之外或运行并行研究。

内置子代理包括 Explore、Plan 和通用型。

详见：[Create custom subagents](https://code.claude.com/docs/en/sub-agents)

### Surface（界面）

**访问 Claude Code 的任何地方**：CLI、VS Code、JetBrains、Desktop 或 claude.ai。所有 surface 共享相同引擎，你的 CLAUDE.md、settings 和 skills 在它们之间以相同方式工作。

详见：[Platforms and integrations](https://code.claude.com/docs/en/platforms)

## T

### Teleport

**`/teleport` 命令，将云端 Claude Code 会话拉入本地终端。** Claude 获取分支、加载对话历史，从 web 会话的最后状态恢复。反向操作是 `--cloud`，将本地任务发送到 web 运行。

详见：[From web to terminal](https://code.claude.com/docs/en/claude-code-on-the-web#from-web-to-terminal)

### Tool（工具）

**Claude 能执行的动作：读文件、编辑代码、运行 shell 命令、搜索网页、生成子代理。** 工具是使 Claude Code 具有代理性的关键。没有它们，Claude 只能用文本回复。

详见：[Tools available to Claude](https://code.claude.com/docs/en/tools-reference)

### Turn（轮次）

**[会话](#session会话)中 Claude 的一次完整响应。** 从你发送消息开始到 Claude 完成响应结束，期间可能包含任意数量的[工具](#tool工具)调用。[Stop hooks](#hookhook) 在每轮结束时触发。

详见：[How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works#the-agentic-loop)

## V

### Verification loop（验证循环）

**会话确认工作确实完成而非仅看起来合理的方式。** 你给 Claude 一个可运行的检查（如测试套件、构建或截图对比），Claude 迭代直到检查通过而非单次尝试后停止。验证循环是 [`/goal`](https://code.claude.com/docs/en/goal)、无人值守运行和[动态工作流](https://code.claude.com/docs/en/workflows)的前提。

详见：[Give Claude a way to verify its work](https://code.claude.com/docs/en/best-practices#give-claude-a-way-to-verify-its-work)

## W

### Worktree isolation（Worktree 隔离）

**在 `.claude/worktrees/` 下的独立 git worktree 中运行 Claude 的隔离模式**，通过 `-w` 标志或子代理配置中的 `isolation: worktree` 启用。修改留在独立分支的独立目录中，并行代理不会覆盖彼此的文件。

详见：[Run parallel sessions with git worktrees](https://code.claude.com/docs/en/worktrees)

---

## 已废弃和重命名的术语

这些术语出现在旧文档、博客和社区内容中。在本站搜索时请使用当前名称。

| 旧名 | 现名 | 备注 |
| :--- | :--- | :--- |
| Headless mode | [Non-interactive mode](#non-interactive-mode非交互模式) | 同一个 `-p` 标志，同一行为 |
| Custom commands | [Skills](#skillskill) | `.claude/commands/` 文件仍然有效 |
| Slash commands | Commands | 产品文案中去掉了 "Slash" |
