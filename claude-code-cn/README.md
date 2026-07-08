# Claude Code 文档中文翻译

Claude Code 官方文档的中文意译版本，覆盖核心概念、配置、扩展功能、工作流等全部文档。追求可读性的同时保留完整信息量，帮助中文开发者快速上手 Claude Code。

更新时间：20260708


- 原文：https://code.claude.com/docs/
- 数据来源：https://code.claude.com/docs/llms.txt
- 英文原文存档：`en-source/`（147 文件，含 MD5 manifest）
- 在线阅读：https://docs.thinkycx.me/claude-code-cn/
- 进度：**146/147**

## 翻译规范

- 意译不直译，短句不删减
- 段首加粗一句话总结
- 对比/列举信息表格化
- Prompt/代码保留英文
- 类型注解用 `<code>` HTML 标签（表格中避免 `|` 冲突）
- 参数名/代码标识符不翻译
- 链接用远程完整 URL；已翻译页面括号追加本地相对链接
- 图片下载到 `assets/`，相对路径引用
- description 2-3 句话概括核心内容

---

### 入门与概念

| # | 原文 | 翻译 | 描述 |
|---|------|------|------|
| 1 | [overview](https://code.claude.com/docs/en/overview) | [✅ overview.md](overview.md) | Claude Code 是一个 AI 编程助手，能读取代码库、编辑文件、执行命令并与开发工具集成。本文介绍了它在终端、IDE、桌面应用和浏览器等多种环境中的安装方式和核心能力。 |
| 2 | [quickstart](https://code.claude.com/docs/en/quickstart) | [✅ quickstart.md](quickstart.md) | Claude Code 快速上手指南，涵盖安装、登录、首次对话、代码修改、Git 操作等核心工作流，帮助开发者在几分钟内掌握 AI 辅助编码的基本用法。 |
| 3 | [how-claude-code-works](https://code.claude.com/docs/en/how-claude-code-works) | [✅ how-claude-code-works.md](how-claude-code-works.md) | 解析 Claude Code 的 Agent 循环（收集上下文→执行→验证）、内置五类工具、访问范围、执行环境差异、会话管理与上下文窗口机制、以及 Checkpoint/权限两道安全保障。 |
| 4 | [best-practices](https://code.claude.com/docs/en/best-practices) | [✅ best-practices.md](best-practices.md) | Anthropic 内部验证的 Claude Code 高效模式：管理上下文窗口、提供验证手段、探索→规划→编码流程、精确 Prompt 技巧、CLAUDE.md/权限/MCP/Hooks/Skills 环境配置、会话管理策略。 |
| 5 | [features-overview](https://code.claude.com/docs/en/features-overview) | [✅ features-overview.md](features-overview.md) | Claude Code 提供了多层扩展机制（CLAUDE.md、Skills、MCP、子代理、Hooks、插件），本文对比各种扩展方式的适用场景、上下文开销和组合策略，帮助你按需构建最适合项目的工作流。 |

### 配置与记忆

| # | 原文 | 翻译 | 描述 |
|---|------|------|------|
| 1 | [memory](https://code.claude.com/docs/en/memory) | [✅ memory.md](memory.md) | Claude Code 通过 CLAUDE.md 文件和自动记忆两套机制实现跨会话的持久化上下文。本文详解如何编写、组织 CLAUDE.md 文件，配置自动记忆，以及排查指令未生效的问题。 |
| 2 | [settings](https://code.claude.com/docs/en/settings) | [✅ settings.md](settings.md) | Claude Code 的完整配置体系，包括多层级作用域（managed/user/project/local）、settings.json 所有可用配置项、权限规则、托管设置部署方式，以及环境变量参考。 |
| 3 | [env-vars](https://code.claude.com/docs/en/env-vars) | [✅ env-vars.md](env-vars.md) | Claude Code 通过环境变量控制模型选择、认证、请求路由和功能开关等行为。本文介绍如何设置环境变量、优先级规则，以及完整的变量参考表。 |
| 4 | [permissions](https://code.claude.com/docs/en/permissions) | [✅ permissions.md](permissions.md) | Claude Code 的权限系统详解：分级权限机制、权限模式（default/auto/plan/bypassPermissions 等）、规则语法（Bash/Read/Edit/WebFetch/MCP 等工具的规则写法）、沙箱联动、托管策略、设置优先级。 |
| 5 | [permission-modes](https://code.claude.com/docs/en/permission-modes) | [✅ permission-modes.md](permission-modes.md) | Claude Code 提供多种权限模式来控制操作审批流程，从逐一审批到完全自动化，适配不同安全需求和使用场景。本文详解各模式的行为差异、切换方式及受保护路径机制。 |
| 6 | [model-config](https://code.claude.com/docs/en/model-config) | [✅ model-config.md](model-config.md) | Claude Code 的模型配置详解，涵盖模型别名、模型选择限制、特殊模型行为（opusplan/fallback/effort level/extended thinking/extended context）以及第三方部署的模型固定方案。 |

### 扩展功能（Skills / MCP / Hooks / Plugins）

| # | 原文 | 翻译 | 描述 |
|---|------|------|------|
| 1 | [skills](https://code.claude.com/docs/en/skills) | [✅ skills.md](skills.md) | Skills 是 Claude Code 的可复用能力扩展机制。通过编写 SKILL.md 文件定义指令，Claude 会在相关场景自动加载或由用户手动触发，支持动态上下文注入、子 Agent 运行、参数传递等高级模式。 |
| 2 | [hooks-guide](https://code.claude.com/docs/en/hooks-guide) | [✅ hooks-guide.md](hooks-guide.md) | Claude Code 的 Hooks 机制允许你在文件编辑、任务完成、需要输入等关键生命周期节点自动执行 shell 命令。本文覆盖了通知、格式化、权限控制、上下文注入等常见场景，以及 prompt/agent/HTTP 类型 hook 的进阶用法。 |
| 3 | [hooks](https://code.claude.com/docs/en/hooks) | [✅ hooks.md](hooks.md) | Claude Code Hooks 的完整参考文档，涵盖生命周期、配置格式、输入输出协议、所有事件类型（20+）的详细规格、Prompt/Agent 钩子、后台执行和安全注意事项。 |
| 4 | [mcp](https://code.claude.com/docs/en/mcp) | [✅ mcp.md](mcp.md) | Claude Code 通过 MCP（Model Context Protocol）连接外部工具和数据源的完整指南，涵盖安装配置、认证授权、工具搜索、资源引用等核心功能。 |
| 5 | [mcp-quickstart](https://code.claude.com/docs/en/mcp-quickstart) | [✅ mcp-quickstart.md](mcp-quickstart.md) | 手把手教你为 Claude Code 接入第一个 MCP server，涵盖添加、验证连接、使用工具以及常见错误排查的完整流程。 |
| 6 | [sub-agents](https://code.claude.com/docs/en/sub-agents) | [✅ sub-agents.md](sub-agents.md) | Claude Code 子代理系统详解：内置子代理（Explore/Plan/General-purpose）、自定义创建与配置（/agents 命令和文件方式）、作用域优先级、工具权限控制、模型选择、持久记忆、前后台执行、以及完整示例集。 |
| 7 | [plugins](https://code.claude.com/docs/en/plugins) | [✅ plugins.md](plugins.md) | Claude Code 插件系统完整开发指南。涵盖从零创建插件、添加 Skill/Agent/Hook/MCP/LSP、本地测试调试、发布到社区市场的全流程，以及将现有 .claude/ 配置迁移为可复用插件的方法。 |
| 8 | [discover-plugins](https://code.claude.com/docs/en/discover-plugins) | [✅ discover-plugins.md](discover-plugins.md) | 介绍如何通过插件市场发现和安装预构建的 Claude Code 插件，涵盖官方市场、社区市场的使用方法，以及插件管理的完整操作流程。 |
| 9 | [channels](https://code.claude.com/docs/en/channels) | [✅ channels.md](channels.md) | Channels 是 Claude Code 的事件推送机制，允许 MCP 服务器将消息、告警和 Webhook 推送到正在运行的会话中。支持 Telegram、Discord、iMessage 等双向通道，让 Claude 在你离开终端时也能响应外部事件。 |

### 工作流与自动化

| # | 原文 | 翻译 | 描述 |
|---|------|------|------|
| 1 | [common-workflows](https://code.claude.com/docs/en/common-workflows) | [✅ common-workflows.md](common-workflows.md) | Claude Code 日常开发中的工作流指南：探索代码库、修复 Bug、重构、测试、PR、文档等 Prompt 模式，以及恢复会话、Worktree 并行、计划模式、子 Agent 委托、脚本管道等进阶用法。 |
| 2 | [cli-reference](https://code.claude.com/docs/en/cli-reference) | [✅ cli-reference.md](cli-reference.md) | Claude Code 命令行界面的完整参考手册，涵盖所有可用命令、标志参数及系统提示词定制方式。 |
| 3 | [commands](https://code.claude.com/docs/en/commands) | [✅ commands.md](commands.md) | Claude Code 中所有可用命令的完整参考，包括内置命令和内置 Skill。覆盖从项目初始化、模型切换、权限管理到代码审查、并行任务编排等各阶段常用命令。 |
| 4 | [headless](https://code.claude.com/docs/en/headless) | [✅ headless.md](headless.md) | 介绍如何通过 Agent SDK 以编程方式运行 Claude Code，包括 CLI 非交互模式、管道数据、结构化输出、流式响应、工具自动授权等常见用法。 |
| 5 | [goal](https://code.claude.com/docs/en/goal) | [✅ goal.md](goal.md) | Claude Code 的 /goal 命令允许你设定一个完成条件，Claude 会持续工作直到条件满足。适合有明确终态的大型任务，比如迁移模块、实现设计文档、拆分大文件等场景。 |
| 6 | [worktrees](https://code.claude.com/docs/en/worktrees) | [✅ worktrees.md](worktrees.md) | Claude Code 支持通过 git worktree 实现多会话并行隔离，每个会话在独立工作目录中运行，互不干扰。本文介绍 --worktree 标志、子代理隔离、.worktreeinclude 配置、清理机制及非 git 版本控制的 hook 扩展。 |
| 7 | [workflows](https://code.claude.com/docs/en/workflows) | [✅ workflows.md](workflows.md) | Claude Code 的动态工作流功能允许通过 JavaScript 脚本大规模编排子代理，适用于代码库审计、大规模迁移和交叉验证研究等场景。本文介绍了工作流的使用时机、运行方式、保存复用以及成本管理。 |
| 8 | [agents](https://code.claude.com/docs/en/agents) | [✅ agents.md](agents.md) | Claude Code 支持多种并行执行任务的方式，包括子代理、代理视图、代理团队和动态工作流。本文对比了各种方式的适用场景，帮助你选择最合适的并行策略。 |
| 9 | [agent-view](https://code.claude.com/docs/en/agent-view) | [✅ agent-view.md](agent-view.md) | Agent View 是 Claude Code 的多会话管理界面，让你在一个屏幕上派发、监控和操作多个后台代理会话，无需逐个切换终端窗口。本文涵盖快速上手、会话监控、派发方式、Shell 管理以及后台进程托管机制。 |

### 高级功能

| # | 原文 | 翻译 | 描述 |
|---|------|------|------|
| 1 | [artifacts](https://code.claude.com/docs/en/artifacts) | [✅ artifacts.md](artifacts.md) | Artifacts 将 Claude Code 终端输出一键发布为组织内可分享的实时交互网页。涵盖创建/更新/分享流程、五类构建模式（走读变更/对比方案/交互调参/进度追踪/决策回流）、页面约束（CSP/无后端/16MiB）、可用条件和组织管理。 |
| 2 | [fast-mode](https://code.claude.com/docs/en/fast-mode) | [✅ fast-mode.md](fast-mode.md) | Fast Mode 用更高 token 单价换取 Opus 2.5 倍响应速度。涵盖开关方式、定价对比、成本权衡、适用场景、速率限制回退机制，以及组织管理员启用配置。 |
| 3 | [routines](https://code.claude.com/docs/en/routines) | [✅ routines.md](routines.md) | Routines 是 Claude Code 的云端自动化能力，支持定时调度、API 触发和 GitHub 事件驱动三种方式，让 Claude 在无人值守的环境中自动执行代码审查、告警分流、文档维护等重复性任务。 |
| 4 | [scheduled-tasks](https://code.claude.com/docs/en/scheduled-tasks) | [✅ scheduled-tasks.md](scheduled-tasks.md) | Claude Code 的定时任务机制，包括 /loop 轮询、一次性提醒和 cron 调度工具，用于在会话中自动执行重复性检查或提醒。 |
| 5 | [checkpointing](https://code.claude.com/docs/en/checkpointing) | [✅ checkpointing.md](checkpointing.md) | Claude Code 的检查点机制会自动追踪代码编辑状态，支持回退到任意历史节点、恢复代码或对话、以及压缩对话释放上下文空间。本文介绍检查点的工作原理、常见用法和局限性。 |
| 6 | [code-review](https://code.claude.com/docs/en/code-review) | [✅ code-review.md](code-review.md) | Claude Code Review 是一项自动化 PR 审查服务，通过多智能体并行分析代码变更，捕获逻辑错误、安全漏洞和隐性回归。本文介绍其工作原理、配置方式、触发方法和定价模型。 |
| 7 | [ultraplan](https://code.claude.com/docs/en/ultraplan) | [✅ ultraplan.md](ultraplan.md) | Ultraplan 将规划任务从本地 CLI 移交到 Claude Code on the web 的 plan mode 会话中。支持浏览器内评审、行内评论和灵活选择执行位置。 |
| 8 | [ultrareview](https://code.claude.com/docs/en/ultrareview) | [✅ ultrareview.md](ultrareview.md) | Ultrareview 是 Claude Code 的深度代码审查功能，通过在云端启动多个审查 Agent 并行分析你的分支或 PR，独立复现并验证每个问题，帮助你在合并前发现真正的 Bug。 |
| 9 | [advisor](https://code.claude.com/docs/en/advisor) | [✅ advisor.md](advisor.md) | Claude Code 的 Advisor 工具让主模型在关键决策点咨询更强的模型获取指导。本文介绍如何启用 advisor、模型配对规则、计费方式和与其他功能的对比。 |
| 10 | [computer-use](https://code.claude.com/docs/en/computer-use) | [✅ computer-use.md](computer-use.md) | Claude Code CLI 中的 Computer Use 功能让 Claude 能打开应用、点击、打字并查看屏幕。支持原生应用测试、可视化问题调试和 GUI 工具自动化。 |
| 11 | [voice-dictation](https://code.claude.com/docs/en/voice-dictation) | [✅ voice-dictation.md](voice-dictation.md) | Claude Code CLI 的语音听写功能，支持按住录音和轻按录音两种模式。语音被实时转写到 prompt 输入中，可以在同一条消息中混合语音和打字。 |
| 12 | [output-styles](https://code.claude.com/docs/en/output-styles) | [✅ output-styles.md](output-styles.md) | 输出风格改变 Claude 的响应方式（角色、语气、格式），通过修改系统 prompt 实现。支持内置预设和自定义 Markdown 文件定义，适用于将 Claude Code 用于软件工程之外的场景。 |
| 13 | [fullscreen](https://code.claude.com/docs/en/fullscreen) | [✅ fullscreen.md](fullscreen.md) | 全屏渲染是 Claude Code CLI 的替代渲染模式，消除闪烁、保持平稳内存使用、支持鼠标操作。在备用屏幕缓冲区绘制界面，只渲染当前可见的消息。 |
| 14 | [prompt-library](https://code.claude.com/docs/en/prompt-library) | [✅ prompt-library.md](prompt-library.md) | Claude Code 的 Prompt 库收录了按任务和角色分类的可复制 prompt，涵盖理解代码、规划、构建、测试、审查、调试、自动化等阶段的实用模板。 |

### 平台集成

| # | 原文 | 翻译 | 描述 |
|---|------|------|------|
| 1 | [vs-code](https://code.claude.com/docs/en/vs-code) | [✅ vs-code.md](vs-code.md) | Claude Code 的 VS Code 扩展安装与配置指南，涵盖内联 diff 审查、@-mentions 引用文件、权限模式、快捷键、MCP 服务器集成等核心功能。 |
| 2 | [jetbrains](https://code.claude.com/docs/en/jetbrains) | [✅ jetbrains.md](jetbrains.md) | Claude Code 通过专用插件与 JetBrains IDE 集成，支持 IntelliJ、PyCharm、WebStorm 等主流 IDE，提供交互式 diff 查看、选中代码上下文共享、快捷键引用文件等功能。 |
| 3 | [desktop](https://code.claude.com/docs/en/desktop) | [✅ desktop.md](desktop.md) | Claude Code 桌面应用完整指南，涵盖会话管理、代码编写、工作区布局、Computer Use、扩展功能（MCP/Skills/Plugins）、环境配置、企业部署，以及从 CLI 迁移的对照说明。 |
| 4 | [desktop-linux](https://code.claude.com/docs/en/desktop-linux) | [✅ desktop-linux.md](desktop-linux.md) | Claude 桌面应用 Linux 版的安装、更新和卸载指南。支持 Ubuntu 22.04+ 和 Debian 12+，通过 apt 仓库获取更新。 |
| 5 | [desktop-quickstart](https://code.claude.com/docs/en/desktop-quickstart) | [✅ desktop-quickstart.md](desktop-quickstart.md) | Claude Code 桌面应用提供图形化界面，支持并行会话、拖拽布局、集成终端、diff 审查、应用预览、PR 监控等功能。本文介绍安装和首次使用的完整流程。 |
| 6 | [claude-code-on-the-web](https://code.claude.com/docs/en/claude-code-on-the-web) | [✅ claude-code-on-the-web.md](claude-code-on-the-web.md) | 本文介绍如何在 Web 端使用 Claude Code，包括云环境配置、Setup 脚本、网络访问控制、Docker 使用，以及通过 --remote 和 --teleport 在 Web 和终端之间切换会话。 |
| 7 | [web-quickstart](https://code.claude.com/docs/en/web-quickstart) | [✅ web-quickstart.md](web-quickstart.md) | Claude Code on the web 允许你在浏览器或手机上运行 Claude Code，连接 GitHub 仓库后提交任务，Claude 在云端 VM 中克隆代码、执行修改并推送分支供你审查。 |
| 8 | [github-actions](https://code.claude.com/docs/en/github-actions) | [✅ github-actions.md](github-actions.md) | Claude Code GitHub Actions 将 AI 驱动的自动化能力引入 GitHub 工作流。通过在 PR 或 Issue 评论中 @claude，Claude 即可分析代码、创建 PR、实现功能并修复 Bug。本文覆盖安装配置、云厂商集成、升级迁移及最佳实践。 |
| 9 | [gitlab-ci-cd](https://code.claude.com/docs/en/gitlab-ci-cd) | [✅ gitlab-ci-cd.md](gitlab-ci-cd.md) | Claude Code 与 GitLab CI/CD 的集成指南。通过在 CI/CD 流水线中运行 Claude，实现从 Issue 自动创建 MR、代码审查、Bug 修复等 AI 驱动的开发工作流。支持 Claude API、Amazon Bedrock 和 Google Vertex AI... |
| 10 | [github-enterprise-server](https://code.claude.com/docs/en/github-enterprise-server) | [✅ github-enterprise-server.md](github-enterprise-server.md) | 将 Claude Code 连接到自托管的 GitHub Enterprise Server 实例，用于 Web 会话、代码审查和插件市场。涵盖管理员设置、开发者工作流和 Teleport。 |
| 11 | [slack](https://code.claude.com/docs/en/slack) | [✅ slack.md](slack.md) | Claude Code 与 Slack 的集成指南。在 Slack 中 @Claude 即可发起编码任务，Claude 会自动路由到 Claude Code on the web 创建会话，完成代码审查、Bug 修复、功能实现等工作，并在完成后通知你创建 PR。 |
| 12 | [chrome](https://code.claude.com/docs/en/chrome) | [✅ chrome.md](chrome.md) | Claude Code 与 Chrome 浏览器的集成指南（beta）。通过 Claude in Chrome 扩展将浏览器自动化能力引入 CLI，实现实时调试、设计验证、Web 应用测试、表单填写、数据提取等工作流，支持在单一工作流中串联编码任务与浏览器操作。 |
| 13 | [remote-control](https://code.claude.com/docs/en/remote-control) | [✅ remote-control.md](remote-control.md) | Claude Code Remote Control 功能指南。让你从手机、平板或任何浏览器继续本地 Claude Code 会话，Claude 始终在本地机器上运行，web 和移动端只是本地会话的一个窗口。支持多设备同步、网络中断自动重连、服务器模式多并发会话。 |
| 14 | [platforms](https://code.claude.com/docs/en/platforms) | [✅ platforms.md](platforms.md) | 选择在哪里运行 Claude Code 以及连接哪些工具。对比 CLI、Desktop、VS Code、JetBrains、Web、移动端和 Chrome/Slack/CI 等集成方式。 |
| 15 | [deep-links](https://code.claude.com/docs/en/deep-links) | [✅ deep-links.md](deep-links.md) | 深度链接是 claude-cli:// URL，用于从链接直接打开 Claude Code 终端会话。可嵌入运维手册、告警面板和文档中，一键打开正确的仓库和预填充 prompt。 |
| 16 | [interactive-mode](https://code.claude.com/docs/en/interactive-mode) | [✅ interactive-mode.md](interactive-mode.md) | Claude Code 交互模式的完整参考，涵盖键盘快捷键、输入模式、Vim 编辑、命令历史、后台任务、Shell 模式、Prompt 建议等交互功能。 |

### 安全与权限

| # | 原文 | 翻译 | 描述 |
|---|------|------|------|
| 1 | [security](https://code.claude.com/docs/en/security) | [✅ security.md](security.md) | Claude Code 的安全架构与最佳实践：基于权限的分层防护、防范 Prompt 注入、MCP 安全、IDE 安全、云端执行安全，以及面向团队的安全建议。 |
| 2 | [sandboxing](https://code.claude.com/docs/en/sandboxing) | [✅ sandboxing.md](sandboxing.md) | 介绍 Claude Code 沙箱化 Bash 工具的工作原理，包括文件系统隔离、网络隔离、OS 级别强制执行机制，以及如何为组织配置和强制沙箱策略。 |
| 3 | [auto-mode-config](https://code.claude.com/docs/en/auto-mode-config) | [✅ auto-mode-config.md](auto-mode-config.md) | 介绍如何配置 Claude Code 的 auto mode 分类器，包括定义可信基础设施、覆盖默认的阻止和允许规则、检查生效配置以及审查拒绝记录。 |
| 4 | [sandbox-environments](https://code.claude.com/docs/en/sandbox-environments) | [✅ sandbox-environments.md](sandbox-environments.md) | 比较 Claude Code 的各种沙箱隔离方案（内置 Bash 沙箱、沙箱运行时、Dev Container、Docker 容器、虚拟机、Web 版），帮助你根据威胁模型选择合适的隔离级别。 |
| 5 | [security-guidance](https://code.claude.com/docs/en/security-guidance) | [✅ security-guidance.md](security-guidance.md) | 介绍 security-guidance 插件的安装和使用，该插件让 Claude 在编写代码时自动审查漏洞并在同一会话中修复，覆盖逐编辑模式匹配、每轮 diff 审查和提交级深度审查三层检测。 |

### 上下文与会话

| # | 原文 | 翻译 | 描述 |
|---|------|------|------|
| 1 | [context-window](https://code.claude.com/docs/en/context-window) | [✅ context-window.md](context-window.md) | Claude Code 上下文窗口的交互式模拟与深度解析。了解会话启动时自动加载了什么、每次文件读取的 token 开销、以及 Rules 和 Hooks 何时触发。 |
| 2 | [prompt-caching](https://code.claude.com/docs/en/prompt-caching) | [✅ prompt-caching.md](prompt-caching.md) | 解释 Claude Code 如何自动管理 prompt caching，包括缓存组织方式、哪些操作会使缓存失效、哪些操作保持缓存、缓存生命周期和性能检查方法。 |
| 3 | [large-codebases](https://code.claude.com/docs/en/large-codebases) | [✅ large-codebases.md](large-codebases.md) | 介绍如何在 monorepo 或大型代码库中配置 Claude Code，通过分层 CLAUDE.md、稀疏 worktree、代码智能插件等手段，让 Claude 聚焦于当前任务涉及的代码，降低 token 消耗并提升输出质量。 |
| 4 | [sessions](https://code.claude.com/docs/en/sessions) | [✅ sessions.md](sessions.md) | 介绍 Claude Code 会话的命名、恢复、分支和切换机制，涵盖 --continue、--resume、--from-pr、/resume 选择器、会话命名、导出会话记录以及本地存储位置。 |

### 网络与网关

| # | 原文 | 翻译 | 描述 |
|---|------|------|------|
| 1 | [gateways](https://code.claude.com/docs/en/gateways) | [✅ gateways.md](gateways.md) | Gateway 是组织在 Claude Code 与模型服务商之间运行的代理。本文介绍 gateway 的工作原理、选择 Claude apps gateway 还是自建 gateway、以及与订阅的关系。 |
| 2 | [llm-gateway](https://code.claude.com/docs/en/llm-gateway) | [✅ llm-gateway.md](llm-gateway.md) | 介绍如何将 Claude Code 路由到组织已运行的第三方 LLM 网关，包括网关的连接方式、组织级推广流程和网关协议。 |
| 3 | [llm-gateway-connect](https://code.claude.com/docs/en/llm-gateway-connect) | [✅ llm-gateway-connect.md](llm-gateway-connect.md) | 如何将 Claude Code 连接到组织的 LLM 网关，包括检查已有配置、设置 Base URL 和凭证、验证连接、各平台配置方式及故障排查。 |
| 4 | [llm-gateway-protocol](https://code.claude.com/docs/en/llm-gateway-protocol) | [✅ llm-gateway-protocol.md](llm-gateway-protocol.md) | Claude Code 与 LLM 网关之间的 API 协议参考，包括端点、请求头和 Body 字段转发、功能降级规则和模型发现。 |
| 5 | [llm-gateway-rollout](https://code.claude.com/docs/en/llm-gateway-rollout) | [✅ llm-gateway-rollout.md](llm-gateway-rollout.md) | 管理员为组织部署 LLM 网关的完整流程：确认路由、签发凭证、测试 Claude Code、分发托管设置、验证推广效果。 |
| 6 | [claude-apps-gateway](https://code.claude.com/docs/en/claude-apps-gateway) | [✅ claude-apps-gateway.md](claude-apps-gateway.md) | Claude Apps Gateway 是内置于 claude 二进制文件的自托管网关服务，支持 SSO 登录、按组模型访问控制和 OTLP 遥测。本文介绍部署理由、快速入门和开发者连接。 |
| 7 | [claude-apps-gateway-config](https://code.claude.com/docs/en/claude-apps-gateway-config) | [✅ claude-apps-gateway-config.md](claude-apps-gateway-config.md) | Claude Apps Gateway 的 gateway.yaml 配置参考。涵盖监听和 TLS、OIDC、会话、Postgres 存储、多种上游服务商、模型路由、托管策略和遥测。 |
| 8 | [claude-apps-gateway-deploy](https://code.claude.com/docs/en/claude-apps-gateway-deploy) | [✅ claude-apps-gateway-deploy.md](claude-apps-gateway-deploy.md) | Claude Apps Gateway 的部署和运维指南。涵盖 IdP 注册、容器镜像构建、Kubernetes/Cloud Run 部署、日志和健康检查、密钥轮换、升级和安全模型。 |
| 9 | [claude-apps-gateway-on-gcp](https://code.claude.com/docs/en/claude-apps-gateway-on-gcp) | [✅ claude-apps-gateway-on-gcp.md](claude-apps-gateway-on-gcp.md) | 在 Google Cloud 上部署 Claude Apps Gateway 的完整示例：Cloud Run 或 GKE、Cloud SQL for PostgreSQL、Secret Manager、以及 Google Cloud Agent Platform 服务账号认证。 |
| 10 | [claude-apps-gateway-spend-limits](https://code.claude.com/docs/en/claude-apps-gateway-spend-limits) | [✅ claude-apps-gateway-spend-limits.md](claude-apps-gateway-spend-limits.md) | Claude Apps Gateway 的消费限额功能，按日/周/月限制每个开发者的使用量。通过 Admin API 设置上限，gateway 实时强制执行。 |
| 11 | [network-config](https://code.claude.com/docs/en/network-config) | [✅ network-config.md](network-config.md) | 为企业环境配置 Claude Code 的代理服务器、自定义 CA 证书和 mTLS 认证，以及网络访问白名单要求。 |

### 企业管理

| # | 原文 | 翻译 | 描述 |
|---|------|------|------|
| 1 | [admin-setup](https://code.claude.com/docs/en/admin-setup) | [✅ admin-setup.md](admin-setup.md) | 面向管理员的 Claude Code 部署决策指南，涵盖 API 提供商选择、托管设置分发、策略执行、使用监控和数据处理等方面。 |
| 2 | [costs](https://code.claude.com/docs/en/costs) | [✅ costs.md](costs.md) | 介绍如何追踪 Claude Code 的 token 使用、为团队设置花费限制，以及通过上下文管理、模型选择、思考配置和预处理 hook 等手段降低成本。 |
| 3 | [analytics](https://code.claude.com/docs/en/analytics) | [✅ analytics.md](analytics.md) | Claude Code 提供分析仪表盘帮助团队追踪使用指标、开发者采纳率和工程效率。本文介绍了 Team/Enterprise 和 API 两种方案的仪表盘功能、GitHub 贡献指标集成以及 PR 归因机制。 |
| 4 | [third-party-integrations](https://code.claude.com/docs/en/third-party-integrations) | [✅ third-party-integrations.md](third-party-integrations.md) | 介绍 Claude Code 的企业部署选项，对比 Claude for Teams/Enterprise、Anthropic Console 和各云提供商的差异，并提供代理/网关配置和组织最佳实践。 |
| 5 | [amazon-bedrock](https://code.claude.com/docs/en/amazon-bedrock) | [✅ amazon-bedrock.md](amazon-bedrock.md) | 介绍如何通过 Amazon Bedrock 配置和使用 Claude Code，涵盖登录向导、手动配置、IAM 权限、模型版本固定、Mantle 端点以及常见问题排查。 |
| 6 | [google-vertex-ai](https://code.claude.com/docs/en/google-vertex-ai) | [✅ google-vertex-ai.md](google-vertex-ai.md) | 介绍如何通过 Google Vertex AI 配置和使用 Claude Code，涵盖登录向导、手动配置、区域设置、IAM 权限、模型版本固定以及常见问题排查。 |
| 7 | [microsoft-foundry](https://code.claude.com/docs/en/microsoft-foundry) | [✅ microsoft-foundry.md](microsoft-foundry.md) | 通过 Microsoft Foundry 配置 Claude Code 的完整指南，包括 Azure 资源创建、认证方式、模型版本固定和故障排查。 |
| 8 | [claude-platform-on-aws](https://code.claude.com/docs/en/claude-platform-on-aws) | [✅ claude-platform-on-aws.md](claude-platform-on-aws.md) | 配置 Claude Code 使用 Claude Platform on AWS，包括 AWS 认证、SigV4 签名、工作区 API 密钥、Agent SDK 集成和代理路由。 |
| 9 | [tools-reference](https://code.claude.com/docs/en/tools-reference) | [✅ tools-reference.md](tools-reference.md) | Claude Code 内置工具的完整参考手册，包括每个工具的权限要求、行为细节和配置方式。 |
| 10 | [server-managed-settings](https://code.claude.com/docs/en/server-managed-settings) | [✅ server-managed-settings.md](server-managed-settings.md) | 通过 claude.ai 控制台集中配置 Claude Code 的服务端托管设置，无需设备管理基础设施。涵盖配置方式、设置下发、安全审批和平台可用性。 |
| 11 | [monitoring-usage](https://code.claude.com/docs/en/monitoring-usage) | [✅ monitoring-usage.md](monitoring-usage.md) | 通过 OpenTelemetry 追踪 Claude Code 的使用量、成本和工具活动。涵盖快速开始、管理员配置、指标/事件/追踪详情以及安全审计。 |
| 12 | [data-usage](https://code.claude.com/docs/en/data-usage) | [✅ data-usage.md](data-usage.md) | Anthropic 的 Claude Code 数据使用政策，涵盖训练政策、数据保留、遥测服务和按提供商的默认行为。 |
| 13 | [feature-availability](https://code.claude.com/docs/en/feature-availability) | [✅ feature-availability.md](feature-availability.md) | 对比 Claude Code 各功能在 Anthropic 订阅计划、Anthropic Console、Amazon Bedrock、Claude Platform on AWS、Google Cloud Agent Platform 和 Microsoft Foundry 上的可用性。 |
| 14 | [legal-and-compliance](https://code.claude.com/docs/en/legal-and-compliance) | [✅ legal-and-compliance.md](legal-and-compliance.md) | Claude Code 的法律协议、合规认证和安全信息，包括许可证、商业协议、BAA 和可接受使用政策。 |
| 15 | [zero-data-retention](https://code.claude.com/docs/en/zero-data-retention) | [✅ zero-data-retention.md](zero-data-retention.md) | Claude Code 的零数据保留 (ZDR) 功能详解，适用于 Claude for Enterprise 的合格账户。涵盖覆盖范围、禁用功能、模型可用性和申请方式。 |

### 安装与排错

| # | 原文 | 翻译 | 描述 |
|---|------|------|------|
| 1 | [setup](https://code.claude.com/docs/en/setup) | [✅ setup.md](setup.md) | Claude Code 的系统要求、平台特定安装、版本管理和卸载的完整参考。涵盖原生安装、Homebrew、WinGet、Linux 包管理器、npm 安装以及二进制完整性验证。 |
| 2 | [authentication](https://code.claude.com/docs/en/authentication) | [✅ authentication.md](authentication.md) | Claude Code 支持多种认证方式：claude.ai 订阅、Console 账号、云服务商凭证和 Claude apps gateway。本文介绍登录流程、团队认证配置和凭证管理。 |
| 3 | [terminal-config](https://code.claude.com/docs/en/terminal-config) | [✅ terminal-config.md](terminal-config.md) | 为 Claude Code 配置终端的指南，涵盖 Shift+Enter 换行、Option 键快捷键、终端铃声通知、tmux 配置、颜色主题、全屏渲染和 Vim 模式等常见问题的解决方案。 |
| 4 | [keybindings](https://code.claude.com/docs/en/keybindings) | [✅ keybindings.md](keybindings.md) | Claude Code 支持自定义快捷键绑定，通过 keybindings.json 配置文件实现个性化的键盘操作。本文详细列出所有可用上下文、动作和按键语法。 |
| 5 | [statusline](https://code.claude.com/docs/en/statusline) | [✅ statusline.md](statusline.md) | 配置自定义状态栏来监控上下文窗口使用、费用和 git 状态。状态栏通过 shell 脚本接收 JSON 会话数据并输出自定义内容。 |
| 6 | [debug-your-config](https://code.claude.com/docs/en/debug-your-config) | [✅ debug-your-config.md](debug-your-config.md) | 当 CLAUDE.md、settings、hooks、MCP 服务器或 skills 未生效时，使用 /context、/doctor、/hooks、/mcp 等命令诊断配置加载问题，找出真正被加载的内容。 |
| 7 | [devcontainer](https://code.claude.com/docs/en/devcontainer) | [✅ devcontainer.md](devcontainer.md) | 在开发容器（Dev Container）中运行 Claude Code，为团队提供一致的隔离环境。涵盖安装、认证持久化、组织策略、网络限制和无提示运行。 |
| 8 | [errors](https://code.claude.com/docs/en/errors) | [✅ errors.md](errors.md) | 查阅 Claude Code 运行时错误消息的含义和修复方法。涵盖服务器错误、使用限额、认证、网络、请求和安装错误的完整参考。 |
| 9 | [troubleshoot-install](https://code.claude.com/docs/en/troubleshoot-install) | [✅ troubleshoot-install.md](troubleshoot-install.md) | 修复安装或登录 Claude Code 时的 command not found、PATH、权限、网络和认证错误。包含各平台的诊断步骤和常见问题解决方案。 |
| 10 | [troubleshooting](https://code.claude.com/docs/en/troubleshooting) | [✅ troubleshooting.md](troubleshooting.md) | 修复 Claude Code 运行时的高 CPU/内存占用、挂起、自动压缩抖动和搜索问题，以及问题分流到正确的排错页面。 |
| 11 | [claude-directory](https://code.claude.com/docs/en/claude-directory) | [✅ claude-directory.md](claude-directory.md) | 详解 Claude Code 在项目 .claude/ 目录和用户 ~/.claude/ 目录中读取的所有文件：CLAUDE.md、settings.json、hooks、skills、commands、subagents、workflows、rules 和自动记忆。 |

### 其他

| # | 原文 | 翻译 | 描述 |
|---|------|------|------|
| 1 | [champion-kit](https://code.claude.com/docs/en/champion-kit) | [✅ champion-kit.md](champion-kit.md) | 面向已在使用 Claude Code 并希望帮助团队采用的工程师的行动指南，包括分享什么、如何回答问题、三十天推广计划以及应对常见顾虑的方法。 |
| 2 | [communications-kit](https://code.claude.com/docs/en/communications-kit) | [✅ communications-kit.md](communications-kit.md) | 面向管理员和工程 lead 的 Claude Code 组织级 rollout 沟通套件，包含发布公告模板、功能激活滴水邮件和高频 FAQ 一行回复。 |
| 3 | [changelog](https://code.claude.com/docs/en/changelog) | [✅ changelog.md](changelog.md) | Claude Code 的版本发布说明，包含各版本的新功能、改进和 bug 修复。本页从 GitHub CHANGELOG.md 生成。 |
| 4 | [channels-reference](https://code.claude.com/docs/en/channels-reference) | [✅ channels-reference.md](channels-reference.md) | Channels MCP 服务器技术参考，覆盖 capability 声明、notification 事件格式、reply tool 暴露、发送者门控和权限转发的完整合约。 |
| 5 | [managed-mcp](https://code.claude.com/docs/en/managed-mcp) | [✅ managed-mcp.md](managed-mcp.md) | 通过 managed-mcp.json、允许列表和拒绝列表控制组织中用户可添加或连接的 MCP 服务器。涵盖完全管控、策略过滤和监控等多种模式。 |
| 6 | [plugin-dependencies](https://code.claude.com/docs/en/plugin-dependencies) | [✅ plugin-dependencies.md](plugin-dependencies.md) | 介绍如何在 plugin.json 中声明依赖版本约束，防止上游插件发布破坏性变更时影响你的插件。覆盖声明语法、版本解析、冲突处理和孤立清理。 |
| 7 | [plugin-hints](https://code.claude.com/docs/en/plugin-hints) | [✅ plugin-hints.md](plugin-hints.md) | 介绍如何从你的 CLI 工具发出标记，让 Claude Code 提示用户安装你在官方市场的插件。覆盖 hint 协议格式、发射时机和用户体验。 |
| 8 | [plugin-marketplaces](https://code.claude.com/docs/en/plugin-marketplaces) | [✅ plugin-marketplaces.md](plugin-marketplaces.md) | 介绍如何创建和分发插件市场（marketplace），覆盖 marketplace.json 结构、插件来源类型、托管方式、版本解析、发布渠道、重命名迁移和组织级限制。 |
| 9 | [plugin-relevance](https://code.claude.com/docs/en/plugin-relevance) | [✅ plugin-relevance.md](plugin-relevance.md) | 介绍如何在 marketplace.json 的插件条目中添加 relevance 块，让 Claude Code 根据用户当前工作上下文推荐安装相关插件。 |
| 10 | [plugins-reference](https://code.claude.com/docs/en/plugins-reference) | [✅ plugins-reference.md](plugins-reference.md) | Claude Code 插件系统完整技术参考，包含组件 schema（skills、agents、hooks、MCP、LSP、monitors、themes）、CLI 命令、安装作用域、目录结构和环境变量。 |
| 11 | [desktop-scheduled-tasks](https://code.claude.com/docs/en/desktop-scheduled-tasks) | [✅ desktop-scheduled-tasks.md](desktop-scheduled-tasks.md) | Claude Code Desktop 的定时任务功能允许你设置定期自动运行的任务，如每日代码审查、依赖审计或晨报。任务在本地机器上运行，可直接访问文件和工具。 |
| 12 | [agent-teams](https://code.claude.com/docs/en/agent-teams) | [✅ agent-teams.md](agent-teams.md) | Agent Teams 让多个 Claude Code 实例协同工作。一个会话做领导协调工作，队友独立工作并互相通信。本文介绍启用、控制和最佳实践。 |
| 13 | [glossary](https://code.claude.com/docs/en/glossary) | [✅ glossary.md](glossary.md) | Claude Code 术语定义汇总。涵盖 agentic loop、compaction、CLAUDE.md、hooks、subagents、MCP 等核心概念的含义和相关链接。 |

---

### Agent SDK

| # | 原文 | 翻译 | 描述 |
|---|------|------|------|
| 1 | [agent-sdk/overview](https://code.claude.com/docs/en/agent-sdk/overview) | [✅ agent-sdk-overview.md](agent-sdk-overview.md) | Claude Agent SDK 概览，介绍如何将 Claude Code 作为库来构建生产级 AI Agent，涵盖内置工具、Hooks、子代理、MCP、权限和会话管理等核心能力。 |
| 2 | [agent-sdk/quickstart](https://code.claude.com/docs/en/agent-sdk/quickstart) | [✅ agent-sdk-quickstart.md](agent-sdk-quickstart.md) | Agent SDK 快速上手指南，从零开始构建一个能自动发现并修复代码 Bug 的 AI Agent，涵盖环境配置、SDK 安装、Agent 编写和运行全流程。 |
| 3 | [agent-sdk/python](https://code.claude.com/docs/en/agent-sdk/python) | [✅ agent-sdk-python.md](agent-sdk-python.md) | Claude Agent SDK Python 版完整参考，涵盖 query() 函数与 ClaudeSDKClient 类的对比选择、所有 API 函数签名与参数、Options/Transport/Hook 等核心类、Type 定义（权限、工具、MCP 配置等），以及 Message 类型体系。 |
| 4 | [agent-sdk/typescript](https://code.claude.com/docs/en/agent-sdk/typescript) | ⬜ 待分段翻译 | TypeScript SDK 完整参考（长文档，待分段翻译） |
| 5 | [agent-sdk/agent-loop](https://code.claude.com/docs/en/agent-sdk/agent-loop) | [✅ agent-sdk-agent-loop.md](agent-sdk-agent-loop.md) | Agent SDK 的核心循环机制详解，涵盖消息生命周期、工具执行流程、上下文窗口管理、自动压缩、Turns 与预算控制、权限模式等架构细节。 |
| 6 | [agent-sdk/claude-code-features](https://code.claude.com/docs/en/agent-sdk/claude-code-features) | [✅ agent-sdk-claude-code-features.md](agent-sdk-claude-code-features.md) | 如何在 Agent SDK 中加载项目指令（CLAUDE.md）、Skills、Hooks 等 Claude Code 文件系统功能，涵盖 settingSources 配置、加载位置和功能选择指南。 |
| 7 | [agent-sdk/custom-tools](https://code.claude.com/docs/en/agent-sdk/custom-tools) | [✅ agent-sdk-custom-tools.md](agent-sdk-custom-tools.md) | 使用 Claude Agent SDK 的进程内 MCP 服务器定义自定义工具，让 Claude 调用你的函数、请求 API 和执行领域特定操作，涵盖工具定义、注册、权限、错误处理和返回图片/资源。 |
| 8 | [agent-sdk/hooks](https://code.claude.com/docs/en/agent-sdk/hooks) | [✅ agent-sdk-hooks.md](agent-sdk-hooks.md) | Claude Agent SDK 的 Hooks 机制详解，涵盖如何在工具调用前后拦截操作、阻止危险命令、修改输入输出，以及转发通知到外部服务。 |
| 9 | [agent-sdk/mcp](https://code.claude.com/docs/en/agent-sdk/mcp) | [✅ agent-sdk-mcp.md](agent-sdk-mcp.md) | Claude Agent SDK 的 MCP 集成指南，介绍如何通过 MCP 协议连接外部工具和数据源，涵盖传输类型、工具搜索、认证和错误处理。 |
| 10 | [agent-sdk/permissions](https://code.claude.com/docs/en/agent-sdk/permissions) | [✅ agent-sdk-permissions.md](agent-sdk-permissions.md) | Claude Agent SDK 的权限配置详解，介绍如何通过权限模式、Hooks 和声明式允许/拒绝规则来控制 Agent 使用工具的方式。 |
| 11 | [agent-sdk/sessions](https://code.claude.com/docs/en/agent-sdk/sessions) | [✅ agent-sdk-sessions.md](agent-sdk-sessions.md) | Claude Agent SDK 的会话管理指南，介绍会话如何持久化对话历史，以及何时使用 continue、resume 和 fork 回到先前的运行。 |
| 12 | [agent-sdk/streaming-output](https://code.claude.com/docs/en/agent-sdk/streaming-output) | [✅ agent-sdk-streaming-output.md](agent-sdk-streaming-output.md) | Claude Agent SDK 流式输出指南，介绍如何实时接收文本和工具调用的增量更新，以及如何构建流式 UI。 |
| 13 | [agent-sdk/structured-outputs](https://code.claude.com/docs/en/agent-sdk/structured-outputs) | [✅ agent-sdk-structured-outputs.md](agent-sdk-structured-outputs.md) | 介绍如何通过 JSON Schema、Zod 或 Pydantic 从 Agent 工作流中获取经过验证的结构化 JSON 数据，实现类型安全的多轮工具调用后结构化返回。 |
| 14 | [agent-sdk/subagents](https://code.claude.com/docs/en/agent-sdk/subagents) | [✅ agent-sdk-subagents.md](agent-sdk-subagents.md) | 介绍如何在 Claude Agent SDK 中定义和调用子代理（Subagents），实现上下文隔离、并行执行、专用指令和工具限制，以及子代理的恢复与嵌套机制。 |
| 15 | [agent-sdk/hosting](https://code.claude.com/docs/en/agent-sdk/hosting) | [✅ agent-sdk-hosting.md](agent-sdk-hosting.md) | Agent SDK 生产环境部署指南，涵盖子进程架构、会话持久化、扩容、可观测性以及 Docker/Kubernetes/沙箱提供商下的多租户隔离方案。 |
| 16 | [agent-sdk/secure-deployment](https://code.claude.com/docs/en/agent-sdk/secure-deployment) | [✅ agent-sdk-secure-deployment.md](agent-sdk-secure-deployment.md) | Claude Code 与 Agent SDK 部署安全指南，涵盖隔离技术（沙箱/容器/gVisor/VM）、凭证管理（代理模式）、网络控制和文件系统配置的纵深防御方案。 |
| 17 | [agent-sdk/observability](https://code.claude.com/docs/en/agent-sdk/observability) | [✅ agent-sdk-observability.md](agent-sdk-observability.md) | 介绍如何通过 OpenTelemetry 从 Agent SDK 导出 traces、metrics 和事件到可观测性后端，涵盖信号启用、trace 阅读、应用关联、标签过滤和敏感数据控制。 |
| 18 | [agent-sdk/cost-tracking](https://code.claude.com/docs/en/agent-sdk/cost-tracking) | [✅ agent-sdk-cost-tracking.md](agent-sdk-cost-tracking.md) | Claude Agent SDK 成本追踪指南，涵盖 token 用量统计、费用估算、按模型拆分、跨调用累计、缓存 token 追踪及 1 小时缓存 TTL 配置。 |
| 19 | [agent-sdk/user-input](https://code.claude.com/docs/en/agent-sdk/user-input) | [✅ agent-sdk-user-input.md](agent-sdk-user-input.md) | Claude Agent SDK 用户输入处理指南，涵盖工具审批回调、澄清问题处理、AskUserQuestion 工具、响应格式与多种审批模式。 |
| 20 | [agent-sdk/file-checkpointing](https://code.claude.com/docs/en/agent-sdk/file-checkpointing) | [✅ agent-sdk-file-checkpointing.md](agent-sdk-file-checkpointing.md) | Claude Agent SDK 文件检查点机制，追踪 Write/Edit/NotebookEdit 工具的文件修改，支持回退到任意历史状态，涵盖启用方式、UUID 捕获、回退操作和常见故障排除。 |
| 21 | [agent-sdk/modifying-system-prompts](https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts) | [✅ agent-sdk-modifying-system-prompts.md](agent-sdk-modifying-system-prompts.md) | Claude Agent SDK 系统提示词定制指南，涵盖 claude_code 预设与自定义提示词的选择决策、CLAUDE.md 项目级指令、输出风格、append 追加模式、跨用户缓存优化及四种方案对比。 |
| 22 | [agent-sdk/session-storage](https://code.claude.com/docs/en/agent-sdk/session-storage) | [✅ agent-sdk-session-storage.md](agent-sdk-session-storage.md) | Claude Agent SDK 会话持久化存储指南，涵盖 SessionStore 接口设计、InMemorySessionStore 快速入门、S3/Redis/Postgres 参考实现、双写架构、子代理支持及适配器验证。 |
| 23 | [agent-sdk/migration-guide](https://code.claude.com/docs/en/agent-sdk/migration-guide) | [✅ agent-sdk-migration-guide.md](agent-sdk-migration-guide.md) | 从 Claude Code SDK 迁移到 Claude Agent SDK 的完整指南，涵盖 TypeScript 和 Python 项目的迁移步骤、破坏性变更（系统提示默认值、设置源配置等），以及改名原因。 |
| 24 | [agent-sdk/plugins](https://code.claude.com/docs/en/agent-sdk/plugins) | [✅ agent-sdk-plugins.md](agent-sdk-plugins.md) | 通过 Agent SDK 加载自定义插件，为 Claude Code 扩展 Skills、Agents、Hooks 和 MCP 服务器。涵盖插件加载、命名空间使用、目录结构和常见问题排查。 |
| 25 | [agent-sdk/skills](https://code.claude.com/docs/en/agent-sdk/skills) | [✅ agent-sdk-skills.md](agent-sdk-skills.md) | 在 Claude Agent SDK 中使用 Agent Skills 扩展 Claude 的专业能力。涵盖 Skills 的工作原理、配置方式、文件位置、工具限制和故障排查。 |
| 26 | [agent-sdk/slash-commands](https://code.claude.com/docs/en/agent-sdk/slash-commands) | [✅ agent-sdk-slash-commands.md](agent-sdk-slash-commands.md) | 在 SDK 中使用斜杠命令控制 Claude Code 会话。涵盖内置命令（/compact、/clear）的使用、自定义命令的创建（参数占位、Bash 执行、文件引用），以及命名空间组织。 |
| 27 | [agent-sdk/streaming-vs-single-mode](https://code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode) | [✅ agent-sdk-streaming-vs-single-mode.md](agent-sdk-streaming-vs-single-mode.md) | Claude Agent SDK 的两种输入模式对比——流式输入模式（持久交互会话，支持图片上传和消息队列）和单消息输入（一次性查询），包括各自的适用场景和实现示例。 |
| 28 | [agent-sdk/todo-tracking](https://code.claude.com/docs/en/agent-sdk/todo-tracking) | [✅ agent-sdk-todo-tracking.md](agent-sdk-todo-tracking.md) | 通过 Claude Agent SDK 追踪和展示 Todo 任务进度。涵盖 Todo 生命周期、TodoWrite 工具监控、实时进度展示，以及迁移到新的 Task 工具的方法。 |
| 29 | [agent-sdk/tool-search](https://code.claude.com/docs/en/agent-sdk/tool-search) | [✅ agent-sdk-tool-search.md](agent-sdk-tool-search.md) | 通过工具搜索让 Agent 扩展到数千个工具——按需动态发现和加载所需工具，而非一次性全部加入上下文窗口。涵盖工作原理、配置方式、优化策略和限制。 |
