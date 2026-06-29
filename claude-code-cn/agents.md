---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】并行代理
description: Claude Code 支持多种并行执行任务的方式，包括子代理、代理视图、代理团队和动态工作流。本文对比了各种方式的适用场景，帮助你选择最合适的并行策略。
category: translation
tags: [claude-code, agents, parallel, translation]
refs: [https://code.claude.com/docs/en/agents.md]
---

# 并行运行代理

> **核心概念：** Claude Code 有多种方式同时处理多个任务——子代理、代理视图、代理团队和动态工作流。选哪种取决于你想亲自参与每个对话、委派任务后回来查看，还是让 Claude 替你协调一组工作者。

**四种并行方式概览：** [子代理](https://code.claude.com/docs/en/sub-agents)、[代理视图](https://code.claude.com/docs/en/agent-view)、[代理团队](https://code.claude.com/docs/en/agent-teams)和[动态工作流](https://code.claude.com/docs/en/workflows)各自以不同方式实现并行。

| 方式 | 能力 | 适用场景 |
| :--- | :--- | :--- |
| [子代理](https://code.claude.com/docs/en/sub-agents) | 在同一会话内派出工作者，让它们在独立上下文中完成子任务，最后返回摘要 | 子任务会产生大量搜索结果、日志或文件内容，而这些信息之后不再需要引用 |
| [代理视图](https://code.claude.com/docs/en/agent-view) | 通过 `claude agents` 打开一个界面，用于派发和监控后台运行的会话。研究预览阶段 | 你有多个独立任务，想把它们委派出去，一眼看到状态，只在需要时才介入 |
| [代理团队](https://code.claude.com/docs/en/agent-teams) | 多个协作会话共享任务列表并互相发消息，由一个组长管理。实验性功能，默认关闭 | 你想让 Claude 把项目拆成多个部分，分配给各成员，并保持它们同步 |
| [动态工作流](https://code.claude.com/docs/en/workflows) | 用脚本运行多个子代理并交叉验证结果，适合工作量太大、无法逐轮协调或需要多次处理的场景 | 任务已超出几个子代理的承载能力，或者你需要结果互相校验：全代码库审计、500 文件迁移、交叉验证的调研、从多个角度起草方案 |

**所有方式的底层都是 Claude 会话。** 如果需要引入其他工具，把它以 [MCP 服务器](https://code.claude.com/docs/en/mcp)的形式暴露给 Claude 即可。

**两个辅助工具也值得了解，** 它们不是运行代理的方式，但支撑着并行工作：

- **[Worktrees（工作树）](https://code.claude.com/docs/en/worktrees)** 为每个会话提供独立的 git checkout，使并行会话不会编辑同一组文件。适用于你自己运行的会话。代理视图会自动把每个派发的会话放入独立工作树，你生成的子代理也可以各自获得一个。
- **[`/batch`](https://code.claude.com/docs/en/commands)** 是一个 [skill](https://code.claude.com/docs/en/skills)，让 Claude 把一个大改动拆分为 5 到 30 个工作树隔离的子代理，每个子代理各自提交一个 Pull Request。它是子代理和工作树的打包使用，不是独立的协调方式。

**还有几个功能可以在无人驱动的情况下运行 Claude，但它们解决的问题不同于跨代理拆分工作：**

- **[后台 bash 命令](https://code.claude.com/docs/en/interactive-mode#background-bash-commands)** 运行一条 shell 命令而不阻塞对话，不会生成代理。
- **[Fork 子代理](https://code.claude.com/docs/en/sub-agents#fork-the-current-conversation)** 是继承你完整对话上下文的子代理，而非从头开始。本质上它还是一种生成子代理的方式，不是独立的界面。
- **[Routine（例行任务）](https://code.claude.com/docs/en/routines)** 按计划在 Anthropic 云端运行会话，而非在你的机器上并行。

> **注意：** 同时运行多个会话或子代理会成倍增加 token 消耗。详见 [Costs（费用）](https://code.claude.com/docs/en/costs)了解用量和速率限制。

## 如何选择

**选择取决于三个维度：谁协调工作、工作者是否需要通信、是否编辑同一组文件。**

- **谁来协调工作？**
  - Claude 在一个对话内委派并收集结果：[子代理](https://code.claude.com/docs/en/sub-agents)
  - 你把独立任务委派出去，之后回来查看：[代理视图](https://code.claude.com/docs/en/agent-view)
  - Claude 制定计划、分配任务并监督一组工作者：[代理团队](https://code.claude.com/docs/en/agent-teams)，实验性功能，默认关闭
  - 用脚本承载计划，而非依赖 Claude 的逐轮判断：[动态工作流](https://code.claude.com/docs/en/workflows)。参见[工作流与子代理及 skill 的对比](https://code.claude.com/docs/en/workflows#when-to-use-a-workflow)
- **工作者之间需要通信吗？** 子代理把结果汇报给生成它的对话；代理视图的会话只向你汇报。代理团队中的成员共享任务列表并直接互相发消息。
- **任务是否涉及同一组文件？** 用[工作树](https://code.claude.com/docs/en/worktrees)隔离。子代理和你自己运行的会话都可以使用独立工作树。代理团队不会自动为成员隔离工作树，因此需要[划分工作](https://code.claude.com/docs/en/agent-teams#avoid-file-conflicts)，让每个成员负责不同的文件集。

## 查看运行中的工作

**检查进度的命令取决于你使用的并行方式：**

- **后台会话：** `claude agents` 打开[代理视图](https://code.claude.com/docs/en/agent-view)——一个界面展示所有会话的状态以及哪些需要你介入。
- **当前会话中的子代理：** `/agents` 打开一个面板，**Running** 标签列出运行中的子代理，**Library** 标签可以[创建和编辑自定义子代理](https://code.claude.com/docs/en/sub-agents#use-the-%2Fagents-command)。名字虽然类似，但它和 `claude agents` 是分开的。
- **当前会话后台运行的任务：** `/tasks` 列出所有项目，可以查看、附加或停止。
- **动态工作流：** `/workflows` 列出正在运行和已完成的工作流、各阶段进展以及已完成的代理数量。

如果想在桌面端查看所有会话，参见[桌面应用中的并行会话](https://code.claude.com/docs/en/desktop#work-in-parallel-with-sessions)。

## 深入了解

**以下指南分别介绍每种方式的设置和配置：**

- [创建自定义子代理](https://code.claude.com/docs/en/sub-agents)：定义可复用的专家角色，控制它们能使用哪些工具。
- [用代理视图管理代理](https://code.claude.com/docs/en/agent-view)：派发会话、观察状态、在需要时接入。
- [编排代理团队](https://code.claude.com/docs/en/agent-teams)：设置组长和成员、分配任务、审查工作成果。
- [编排动态工作流](https://code.claude.com/docs/en/workflows)：运行内置工作流，或让 Claude 编写自定义工作流来运行多个子代理并交叉验证结果。
- [用工作树运行并行会话](https://code.claude.com/docs/en/worktrees)：在隔离的 checkout 中启动 Claude、控制哪些内容被复制进来、完成后清理。
