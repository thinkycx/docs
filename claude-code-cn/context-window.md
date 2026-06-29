---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】上下文窗口
description: Claude Code 上下文窗口的交互式模拟与深度解析。了解会话启动时自动加载了什么、每次文件读取的 token 开销、以及 Rules 和 Hooks 何时触发。
category: translation
tags: [claude-code, context-window, translation]
refs: [https://code.claude.com/docs/en/context-window.md]
---

# 探索上下文窗口

> 一个交互式模拟器，展示 Claude Code 的上下文窗口在会话期间是如何被填充的。你可以看到哪些内容自动加载、每次文件读取的 token 成本、以及 Rules 和 Hooks 何时触发。

**Claude Code 的上下文窗口承载着 Claude 对当前会话所知的一切：** 你的指令、它读取的文件、它自己的回复，以及那些从不出现在终端中的内容。原文页面提供了一个交互式时间线，演示从启动到压缩（compaction）的完整会话过程：包括你输入之前加载了什么、Claude 工作时每次文件读取/Rule/Hook 增加了什么、以及子智能体（subagent）如何将大量文件读取隔离在你的上下文之外。下文是时间线的文字版本。

---

## 时间线展示了什么

**这个会话模拟展示了一个典型流程，包含有代表性的 token 数量：**

- **在你输入任何内容之前：** CLAUDE.md、自动记忆（auto memory）、MCP 工具名称和 Skill 描述都已加载到上下文中。你自己的配置可能还会在这里增加更多内容，比如[输出风格](https://code.claude.com/docs/en/output-styles)或通过 [`--append-system-prompt`](https://code.claude.com/docs/en/cli-reference) 添加的文本，它们都以相同的方式进入系统提示。
- **Claude 工作期间：** 每次文件读取都会增加上下文，[路径范围的 Rules](https://code.claude.com/docs/en/memory#path-specific-rules) 会在匹配文件被读取时自动加载，[PostToolUse Hook](https://code.claude.com/docs/en/hooks-guide) 在每次编辑后触发。
- **后续追问：** 一个[子智能体](https://code.claude.com/docs/en/sub-agents)在自己独立的上下文窗口中处理研究任务，因此大量文件读取不会进入你的上下文。只有摘要和少量元数据返回给你。
- **结束阶段：** `/compact` 将对话替换为结构化摘要。大部分启动内容会自动重新加载；下表展示了各种机制的具体行为。

---

## 压缩后哪些内容会保留

**当一个长会话被压缩时，Claude Code 会对对话历史进行摘要以适应上下文窗口。** 你的指令是否保留取决于它们的加载方式：

| 机制 | 压缩后的状态 |
| :--- | :--- |
| 系统提示和输出风格 | 不受影响；不属于消息历史 |
| 项目根目录的 CLAUDE.md 和无范围限制的 Rules | 从磁盘重新注入 |
| 自动记忆（Auto memory） | 从磁盘重新注入 |
| 带 `paths:` 前置声明的 Rules | 丢失，直到再次读取匹配文件时才重新加载 |
| 子目录中的嵌套 CLAUDE.md | 丢失，直到再次读取该子目录中的文件时才重新加载 |
| 已调用的 Skill 正文 | 重新注入，每个 Skill 上限 5,000 token，总计上限 25,000 token；最早调用的 Skill 优先丢弃 |
| Hooks | 不适用；Hooks 作为代码运行，不进入上下文 |

**路径范围 Rules 和嵌套 CLAUDE.md 在触发文件被读取时加载到消息历史中，** 所以压缩会将它们与其他内容一起摘要掉。下次 Claude 读取匹配文件时它们会重新加载。如果某条 Rule 必须在压缩后持续存在，请移除 `paths:` 前置声明，或将其移到项目根目录的 CLAUDE.md 中。

**Skill 正文在压缩后会被重新注入，但大型 Skill 会被截断以适应单个 Skill 的上限，** 最早调用的 Skill 会在总预算超出时被丢弃。截断保留文件开头部分，所以请把最重要的指令放在 `SKILL.md` 的顶部。

---

## 上下文满了会怎样

**Claude Code 在接近上限时会自动压缩，所以上下文满了不会终止会话。** 自动压缩的工作方式与时间线中的 `/compact` 步骤完全相同。详见 [上下文满时的处理](https://code.claude.com/docs/en/how-claude-code-works#when-context-fills-up)。

你也可以在自动压缩运行之前主动采取行动：

- **带焦点压缩：** 在开始长任务前运行带指令的 `/compact`，例如 `/compact focus on the auth bug fix`。摘要会保留你选择的内容，而不是自动压缩猜测的重要内容。
- **任务间清除：** 切换到无关工作时运行 `/clear`。旧对话会挤占你下一步需要的文件空间，并且每条消息都在消耗 token。
- **委托大量读取：** 将研究任务发送给[子智能体](https://code.claude.com/docs/en/sub-agents)，让文件内容留在它的上下文窗口而非你的。

**如果你需要更大的窗口而非更短的对话，** Fable 5、Opus 4.6 及更高版本、Sonnet 4.6 支持 100 万 token 的上下文窗口。详见 [扩展上下文](https://code.claude.com/docs/en/model-config#extended-context) 了解各计划的可用性以及如何选择 `[1m]` 模型变体。压缩在更大上限下的工作方式完全相同。

---

## 查看你自己的会话

**上面的可视化使用的是示意性数字。** 要查看你当前的实际上下文使用情况，运行 `/context` 可获得按类别分类的实时分析和优化建议。运行 `/memory` 可检查启动时加载了哪些 CLAUDE.md 和自动记忆文件。

---

## 相关资源

**时间线中展示的各项功能，可参考以下页面获取更深入的内容：**

- [扩展 Claude Code](https://code.claude.com/docs/en/features-overview)：何时使用 CLAUDE.md vs Skills vs Rules vs Hooks vs MCP
- [存储指令和记忆](https://code.claude.com/docs/en/memory)：CLAUDE.md 层级结构和自动记忆
- [子智能体](https://code.claude.com/docs/en/sub-agents)：将研究任务委托到独立的上下文窗口
- [最佳实践](https://code.claude.com/docs/en/best-practices)：管理上下文作为你的核心约束
- [Prompt 缓存](https://code.claude.com/docs/en/prompt-caching)：哪些操作会使缓存前缀失效
- [降低 token 用量](https://code.claude.com/docs/en/costs#reduce-token-usage)：保持低上下文用量的策略
