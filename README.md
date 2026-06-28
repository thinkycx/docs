---
create: 2026-06-28
update: 2026-06-29
author: thinkycx
title: Claude Code 文档中文翻译项目
description: Claude Code 官方文档中文意译，覆盖核心概念、配置、扩展功能、工作流等文档。追求可读性同时保留完整信息量。
category: translation
tags: [claude-code, translation, docs]
refs:
  - https://code.claude.com/docs/en/overview.md
  - https://code.claude.com/docs/llms.txt
---

# Claude Code 文档中文翻译

原文：https://code.claude.com/docs/
在线阅读：https://thinkycx.me/files/claude-code-docs-cn-pub/README.html
进度：**58/58**

## 翻译规范

- 意译不直译，短句不删减
- 段首加粗一句话总结
- 对比/列举信息表格化
- Prompt/代码保留英文
- 链接用远程完整 URL；已翻译页面括号追加本地相对链接
- 图片下载到 `assets/`，相对路径引用
- description 2-3 句话概括核心内容

---

### 入门与概念

| # | 原文 | 翻译 | 标签 | 描述 |
|---|------|------|------|------|
| 1 | [overview](https://code.claude.com/docs/en/overview) | [✅ overview.md](overview.md) | claude-code,overview,translation | Claude Code 是一个 AI 编程助手，能读取代码库、编辑文件、执行命令并与开发工具集成。本文介绍了它在终端、IDE、桌面应用和浏览器等多种环境中的安装方式和核心能力。 |
| 2 | [quickstart](https://code.claude.com/docs/en/quickstart) | [✅ quickstart.md](quickstart.md) | claude-code,quickstart,translation | Claude Code 快速上手指南，涵盖安装、登录、首次对话、代码修改、Git 操作等核心工作流，帮助开发者在几分钟内掌握 AI 辅助编码的基本用法。 |
| 3 | [how-claude-code-works](https://code.claude.com/docs/en/how-claude-code-works) | [✅ how-claude-code-works.md](how-claude-code-works.md) | claude-code,architecture,translation | 解析 Claude Code 的 Agent 循环（收集上下文→执行→验证）、内置五类工具、访问范围、执行环境差异、会话管理与上下文窗口机制、以及 Checkpoint/权限两道安全保障。 |
| 4 | [best-practices](https://code.claude.com/docs/en/best-practices) | [✅ best-practices.md](best-practices.md) | claude-code,best-practices,translation | Anthropic 内部验证的 Claude Code 高效模式：管理上下文窗口、提供验证手段、探索→规划→编码流程、精确 Prompt 技巧、CLAUDE.md/权限/MCP/Hooks/Sk... |
| 5 | [features-overview](https://code.claude.com/docs/en/features-overview) | [✅ features-overview.md](features-overview.md) | claude-code,features,extensions,translation | Claude Code 提供了多层扩展机制（CLAUDE.md、Skills、MCP、子代理、Hooks、插件），本文对比各种扩展方式的适用场景、上下文开销和组合策略，帮助你按需构建最适合项目的... |

_5/5_

### 配置与记忆

| # | 原文 | 翻译 | 标签 | 描述 |
|---|------|------|------|------|
| 1 | [memory](https://code.claude.com/docs/en/memory) | [✅ memory.md](memory.md) | claude-code,memory,claude-md,translation | Claude Code 通过 CLAUDE.md 文件和自动记忆两套机制实现跨会话的持久化上下文。本文详解如何编写、组织 CLAUDE.md 文件，配置自动记忆，以及排查指令未生效的问题。 |
| 2 | [settings](https://code.claude.com/docs/en/settings) | [✅ settings.md](settings.md) | claude-code,settings,configuration,translation | Claude Code 的完整配置体系，包括多层级作用域（managed/user/project/local）、settings.json 所有可用配置项、权限规则、托管设置部署方式，以及环境... |
| 3 | [env-vars](https://code.claude.com/docs/en/env-vars) | [✅ env-vars.md](env-vars.md) | claude-code,env-vars,configuration,translation | Claude Code 通过环境变量控制模型选择、认证、请求路由和功能开关等行为。本文介绍如何设置环境变量、优先级规则，以及完整的变量参考表。 |
| 4 | [permissions](https://code.claude.com/docs/en/permissions) | [✅ permissions.md](permissions.md) | claude-code,permissions,security,translation | Claude Code 的权限系统详解：分级权限机制、权限模式（default/auto/plan/bypassPermissions 等）、规则语法（Bash/Read/Edit/WebFet... |
| 5 | [permission-modes](https://code.claude.com/docs/en/permission-modes) | [✅ permission-modes.md](permission-modes.md) | claude-code,permission-modes,translation | Claude Code 提供多种权限模式来控制操作审批流程，从逐一审批到完全自动化，适配不同安全需求和使用场景。本文详解各模式的行为差异、切换方式及受保护路径机制。 |
| 6 | [model-config](https://code.claude.com/docs/en/model-config) | [✅ model-config.md](model-config.md) | claude-code,model-config,translation | Claude Code 的模型配置详解，涵盖模型别名、模型选择限制、特殊模型行为（opusplan/fallback/effort level/extended thinking/extende... |

_6/6_

### 扩展功能（Skills / MCP / Hooks / Plugins）

| # | 原文 | 翻译 | 标签 | 描述 |
|---|------|------|------|------|
| 1 | [skills](https://code.claude.com/docs/en/skills) | [✅ skills.md](skills.md) | claude-code,skills,translation | Skills 是 Claude Code 的可复用能力扩展机制。通过编写 SKILL.md 文件定义指令，Claude 会在相关场景自动加载或由用户手动触发，支持动态上下文注入、子 Agent ... |
| 2 | [hooks-guide](https://code.claude.com/docs/en/hooks-guide) | [✅ hooks-guide.md](hooks-guide.md) | claude-code,hooks,automation,translation | Claude Code 的 Hooks 机制允许你在文件编辑、任务完成、需要输入等关键生命周期节点自动执行 shell 命令。本文覆盖了通知、格式化、权限控制、上下文注入等常见场景，以及 pro... |
| 3 | [hooks](https://code.claude.com/docs/en/hooks) | [✅ hooks.md](hooks.md) | claude-code,hooks,reference,translation | Claude Code Hooks 的完整参考文档，涵盖生命周期、配置格式、输入输出协议、所有事件类型（20+）的详细规格、Prompt/Agent 钩子、后台执行和安全注意事项。 |
| 4 | [mcp](https://code.claude.com/docs/en/mcp) | [✅ mcp.md](mcp.md) | claude-code,mcp,translation | Claude Code 通过 MCP（Model Context Protocol）连接外部工具和数据源的完整指南，涵盖安装配置、认证授权、工具搜索、资源引用等核心功能。 |
| 5 | [mcp-quickstart](https://code.claude.com/docs/en/mcp-quickstart) | [✅ mcp-quickstart.md](mcp-quickstart.md) | claude-code,mcp,quickstart,translation | 手把手教你为 Claude Code 接入第一个 MCP server，涵盖添加、验证连接、使用工具以及常见错误排查的完整流程。 |
| 6 | [sub-agents](https://code.claude.com/docs/en/sub-agents) | [✅ sub-agents.md](sub-agents.md) | claude-code,sub-agents,translation | Claude Code 子代理系统详解：内置子代理（Explore/Plan/General-purpose）、自定义创建与配置（/agents 命令和文件方式）、作用域优先级、工具权限控制、模... |
| 7 | [plugins](https://code.claude.com/docs/en/plugins) | [✅ plugins.md](plugins.md) | claude-code,plugins,translation | Claude Code 插件系统完整开发指南。涵盖从零创建插件、添加 Skill/Agent/Hook/MCP/LSP、本地测试调试、发布到社区市场的全流程，以及将现有 .claude/ 配置迁... |
| 8 | [discover-plugins](https://code.claude.com/docs/en/discover-plugins) | [✅ discover-plugins.md](discover-plugins.md) | claude-code,plugins,marketplace,translation | 介绍如何通过插件市场发现和安装预构建的 Claude Code 插件，涵盖官方市场、社区市场的使用方法，以及插件管理的完整操作流程。 |
| 9 | [channels](https://code.claude.com/docs/en/channels) | [✅ channels.md](channels.md) | claude-code,channels,translation | Channels 是 Claude Code 的事件推送机制，允许 MCP 服务器将消息、告警和 Webhook 推送到正在运行的会话中。支持 Telegram、Discord、iMessage... |

_9/9_

### 工作流与自动化

| # | 原文 | 翻译 | 标签 | 描述 |
|---|------|------|------|------|
| 1 | [common-workflows](https://code.claude.com/docs/en/common-workflows) | [✅ common-workflows.md](common-workflows.md) | claude-code,workflows,translation | Claude Code 日常开发中的工作流指南：探索代码库、修复 Bug、重构、测试、PR、文档等 Prompt 模式，以及恢复会话、Worktree 并行、计划模式、子 Agent 委托、脚本... |
| 2 | [cli-reference](https://code.claude.com/docs/en/cli-reference) | [✅ cli-reference.md](cli-reference.md) | claude-code,cli,reference,translation | Claude Code 命令行界面的完整参考手册，涵盖所有可用命令、标志参数及系统提示词定制方式。 |
| 3 | [commands](https://code.claude.com/docs/en/commands) | [✅ commands.md](commands.md) | claude-code,commands,translation | Claude Code 中所有可用命令的完整参考，包括内置命令和内置 Skill。覆盖从项目初始化、模型切换、权限管理到代码审查、并行任务编排等各阶段常用命令。 |
| 4 | [headless](https://code.claude.com/docs/en/headless) | [✅ headless.md](headless.md) | claude-code,headless,automation,translation | 介绍如何通过 Agent SDK 以编程方式运行 Claude Code，包括 CLI 非交互模式、管道数据、结构化输出、流式响应、工具自动授权等常见用法。 |
| 5 | [goal](https://code.claude.com/docs/en/goal) | [✅ goal.md](goal.md) | claude-code,goal,translation | Claude Code 的 /goal 命令允许你设定一个完成条件，Claude 会持续工作直到条件满足。适合有明确终态的大型任务，比如迁移模块、实现设计文档、拆分大文件等场景。 |
| 6 | [worktrees](https://code.claude.com/docs/en/worktrees) | [✅ worktrees.md](worktrees.md) | claude-code,worktrees,translation | Claude Code 支持通过 git worktree 实现多会话并行隔离，每个会话在独立工作目录中运行，互不干扰。本文介绍 --worktree 标志、子代理隔离、.worktreeinc... |
| 7 | [workflows](https://code.claude.com/docs/en/workflows) | [✅ workflows.md](workflows.md) | claude-code,workflows,orchestration,translation | Claude Code 的动态工作流功能允许通过 JavaScript 脚本大规模编排子代理，适用于代码库审计、大规模迁移和交叉验证研究等场景。本文介绍了工作流的使用时机、运行方式、保存复用以及... |
| 8 | [agents](https://code.claude.com/docs/en/agents) | [✅ agents.md](agents.md) | claude-code,agents,parallel,translation | Claude Code 支持多种并行执行任务的方式，包括子代理、代理视图、代理团队和动态工作流。本文对比了各种方式的适用场景，帮助你选择最合适的并行策略。 |
| 9 | [agent-view](https://code.claude.com/docs/en/agent-view) | [✅ agent-view.md](agent-view.md) | claude-code,agent-view,translation | Agent View 是 Claude Code 的多会话管理界面，让你在一个屏幕上派发、监控和操作多个后台代理会话，无需逐个切换终端窗口。本文涵盖快速上手、会话监控、派发方式、Shell 管理... |

_9/9_

### 高级功能

| # | 原文 | 翻译 | 标签 | 描述 |
|---|------|------|------|------|
| 1 | [artifacts](https://code.claude.com/docs/en/artifacts) | [✅ artifacts.md](artifacts.md) | claude-code,artifacts,translation | Artifacts 将 Claude Code 终端输出一键发布为组织内可分享的实时交互网页。涵盖创建/更新/分享流程、五类构建模式（走读变更/对比方案/交互调参/进度追踪/决策回流）、页面约束... |
| 2 | [fast-mode](https://code.claude.com/docs/en/fast-mode) | [✅ fast-mode.md](fast-mode.md) | claude-code,fast-mode,translation | Fast Mode 用更高 token 单价换取 Opus 2.5 倍响应速度。涵盖开关方式、定价对比、成本权衡、适用场景、速率限制回退机制，以及组织管理员启用配置。 |
| 3 | [routines](https://code.claude.com/docs/en/routines) | [✅ routines.md](routines.md) | claude-code,routines,automation,translation | Routines 是 Claude Code 的云端自动化能力，支持定时调度、API 触发和 GitHub 事件驱动三种方式，让 Claude 在无人值守的环境中自动执行代码审查、告警分流、文档... |
| 4 | [scheduled-tasks](https://code.claude.com/docs/en/scheduled-tasks) | [✅ scheduled-tasks.md](scheduled-tasks.md) | claude-code,scheduled-tasks,translation | Claude Code 的定时任务机制，包括 /loop 轮询、一次性提醒和 cron 调度工具，用于在会话中自动执行重复性检查或提醒。 |
| 5 | [checkpointing](https://code.claude.com/docs/en/checkpointing) | [✅ checkpointing.md](checkpointing.md) | claude-code,checkpointing,translation | Claude Code 的检查点机制会自动追踪代码编辑状态，支持回退到任意历史节点、恢复代码或对话、以及压缩对话释放上下文空间。本文介绍检查点的工作原理、常见用法和局限性。 |
| 6 | [code-review](https://code.claude.com/docs/en/code-review) | [✅ code-review.md](code-review.md) | claude-code,code-review,translation | Claude Code Review 是一项自动化 PR 审查服务，通过多智能体并行分析代码变更，捕获逻辑错误、安全漏洞和隐性回归。本文介绍其工作原理、配置方式、触发方法和定价模型。 |

_6/6_

### 平台集成

| # | 原文 | 翻译 | 标签 | 描述 |
|---|------|------|------|------|
| 1 | [vs-code](https://code.claude.com/docs/en/vs-code) | [✅ vs-code.md](vs-code.md) | claude-code,vs-code,ide,translation | Claude Code 的 VS Code 扩展安装与配置指南，涵盖内联 diff 审查、@-mentions 引用文件、权限模式、快捷键、MCP 服务器集成等核心功能。 |
| 2 | [jetbrains](https://code.claude.com/docs/en/jetbrains) | [✅ jetbrains.md](jetbrains.md) | claude-code,jetbrains,ide,translation | Claude Code 通过专用插件与 JetBrains IDE 集成，支持 IntelliJ、PyCharm、WebStorm 等主流 IDE，提供交互式 diff 查看、选中代码上下文共享... |
| 3 | [desktop](https://code.claude.com/docs/en/desktop) | [✅ desktop.md](desktop.md) | claude-code,desktop,translation | Claude Code 桌面应用完整指南，涵盖会话管理、代码编写、工作区布局、Computer Use、扩展功能（MCP/Skills/Plugins）、环境配置、企业部署，以及从 CLI 迁移... |
| 4 | [claude-code-on-the-web](https://code.claude.com/docs/en/claude-code-on-the-web) | [✅ claude-code-on-the-web.md](claude-code-on-the-web.md) | claude-code,web,translation | 本文介绍如何在 Web 端使用 Claude Code，包括云环境配置、Setup 脚本、网络访问控制、Docker 使用，以及通过 --remote 和 --teleport 在 Web 和终... |
| 5 | [github-actions](https://code.claude.com/docs/en/github-actions) | [✅ github-actions.md](github-actions.md) | claude-code,github-actions,ci-cd,translation | Claude Code GitHub Actions 将 AI 驱动的自动化能力引入 GitHub 工作流。通过在 PR 或 Issue 评论中 @claude，Claude 即可分析代码、创建... |
| 6 | [gitlab-ci-cd](https://code.claude.com/docs/en/gitlab-ci-cd) | [✅ gitlab-ci-cd.md](gitlab-ci-cd.md) | claude-code,gitlab,ci-cd,translation | Claude Code 与 GitLab CI/CD 的集成指南。通过在 CI/CD 流水线中运行 Claude，实现从 Issue 自动创建 MR、代码审查、Bug 修复等 AI 驱动的开发工... |
| 7 | [slack](https://code.claude.com/docs/en/slack) | [✅ slack.md](slack.md) | claude-code,slack,translation | Claude Code 与 Slack 的集成指南。在 Slack 中 @Claude 即可发起编码任务，Claude 会自动路由到 Claude Code on the web 创建会话，完成... |
| 8 | [chrome](https://code.claude.com/docs/en/chrome) | [✅ chrome.md](chrome.md) | claude-code,chrome,translation | Claude Code 与 Chrome 浏览器的集成指南（beta）。通过 Claude in Chrome 扩展将浏览器自动化能力引入 CLI，实现实时调试、设计验证、Web 应用测试、表单... |
| 9 | [remote-control](https://code.claude.com/docs/en/remote-control) | [✅ remote-control.md](remote-control.md) | claude-code,remote-control,translation | Claude Code Remote Control 功能指南。让你从手机、平板或任何浏览器继续本地 Claude Code 会话，Claude 始终在本地机器上运行，web 和移动端只是本地会... |

_9/9_

### 安全与权限

| # | 原文 | 翻译 | 标签 | 描述 |
|---|------|------|------|------|
| 1 | [security](https://code.claude.com/docs/en/security) | [✅ security.md](security.md) | claude-code,security,translation | Claude Code 的安全架构与最佳实践：基于权限的分层防护、防范 Prompt 注入、MCP 安全、IDE 安全、云端执行安全，以及面向团队的安全建议。 |
| 2 | [sandboxing](https://code.claude.com/docs/en/sandboxing) | [✅ sandboxing.md](sandboxing.md) | tags: | 介绍 Claude Code 沙箱化 Bash 工具的工作原理，包括文件系统隔离、网络隔离、OS 级别强制执行机制，以及如何为组织配置和强制沙箱策略。 |
| 3 | [auto-mode-config](https://code.claude.com/docs/en/auto-mode-config) | [✅ auto-mode-config.md](auto-mode-config.md) | tags: | 介绍如何配置 Claude Code 的 auto mode 分类器，包括定义可信基础设施、覆盖默认的阻止和允许规则、检查生效配置以及审查拒绝记录。 |

_3/3_

### 上下文与会话

| # | 原文 | 翻译 | 标签 | 描述 |
|---|------|------|------|------|
| 1 | [context-window](https://code.claude.com/docs/en/context-window) | [✅ context-window.md](context-window.md) | claude-code,context-window,translation | Claude Code 上下文窗口的交互式模拟与深度解析。了解会话启动时自动加载了什么、每次文件读取的 token 开销、以及 Rules 和 Hooks 何时触发。 |
| 2 | [prompt-caching](https://code.claude.com/docs/en/prompt-caching) | [✅ prompt-caching.md](prompt-caching.md) | tags: | 解释 Claude Code 如何自动管理 prompt caching，包括缓存组织方式、哪些操作会使缓存失效、哪些操作保持缓存、缓存生命周期和性能检查方法。 |
| 3 | [large-codebases](https://code.claude.com/docs/en/large-codebases) | [✅ large-codebases.md](large-codebases.md) | tags: | 介绍如何在 monorepo 或大型代码库中配置 Claude Code，通过分层 CLAUDE.md、稀疏 worktree、代码智能插件等手段，让 Claude 聚焦于当前任务涉及的代码，降... |
| 4 | [sessions](https://code.claude.com/docs/en/sessions) | [✅ sessions.md](sessions.md) | tags: | 介绍 Claude Code 会话的命名、恢复、分支和切换机制，涵盖 --continue、--resume、--from-pr、/resume 选择器、会话命名、导出会话记录以及本地存储位置。 |

_4/4_

### 企业管理

| # | 原文 | 翻译 | 标签 | 描述 |
|---|------|------|------|------|
| 1 | [admin-setup](https://code.claude.com/docs/en/admin-setup) | [✅ admin-setup.md](admin-setup.md) | tags: | 面向管理员的 Claude Code 部署决策指南，涵盖 API 提供商选择、托管设置分发、策略执行、使用监控和数据处理等方面。 |
| 2 | [costs](https://code.claude.com/docs/en/costs) | [✅ costs.md](costs.md) | tags: | 介绍如何追踪 Claude Code 的 token 使用、为团队设置花费限制，以及通过上下文管理、模型选择、思考配置和预处理 hook 等手段降低成本。 |
| 3 | [analytics](https://code.claude.com/docs/en/analytics) | [✅ analytics.md](analytics.md) | claude-code,analytics,translation | Claude Code 提供分析仪表盘帮助团队追踪使用指标、开发者采纳率和工程效率。本文介绍了 Team/Enterprise 和 API 两种方案的仪表盘功能、GitHub 贡献指标集成以及 ... |
| 4 | [third-party-integrations](https://code.claude.com/docs/en/third-party-integrations) | [✅ third-party-integrations.md](third-party-integrations.md) | tags: | 介绍 Claude Code 的企业部署选项，对比 Claude for Teams/Enterprise、Anthropic Console 和各云提供商的差异，并提供代理/网关配置和组织最佳实践。 |
| 5 | [amazon-bedrock](https://code.claude.com/docs/en/amazon-bedrock) | [✅ amazon-bedrock.md](amazon-bedrock.md) | claude-code,bedrock,aws,translation | 介绍如何通过 Amazon Bedrock 配置和使用 Claude Code，涵盖登录向导、手动配置、IAM 权限、模型版本固定、Mantle 端点以及常见问题排查。 |
| 6 | [google-vertex-ai](https://code.claude.com/docs/en/google-vertex-ai) | [✅ google-vertex-ai.md](google-vertex-ai.md) | claude-code,vertex-ai,gcp,translation | 介绍如何通过 Google Vertex AI 配置和使用 Claude Code，涵盖登录向导、手动配置、区域设置、IAM 权限、模型版本固定以及常见问题排查。 |
| 7 | [tools-reference](https://code.claude.com/docs/en/tools-reference) | [✅ tools-reference.md](tools-reference.md) | tags: | Claude Code 内置工具的完整参考手册，包括每个工具的权限要求、行为细节和配置方式。 |

_7/7_

