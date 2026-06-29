---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】扩展 Claude Code
description: Claude Code 提供了多层扩展机制（CLAUDE.md、Skills、MCP、子代理、Hooks、插件），本文对比各种扩展方式的适用场景、上下文开销和组合策略，帮助你按需构建最适合项目的工作流。
category: translation
tags: [claude-code, features, extensions, translation]
refs:
  - https://code.claude.com/docs/en/features-overview.md
---

# 扩展 Claude Code

> 了解何时使用 CLAUDE.md、Skills、子代理、Hooks、MCP 和插件。

**Claude Code 的内置工具覆盖了绝大多数编码任务，扩展层让你按需叠加自定义能力。** Claude Code 将一个能推理代码的模型与[内置工具](https://code.claude.com/docs/en/how-claude-code-works#tools)（文件操作、搜索、执行、网络访问）组合在一起。本文聚焦于扩展层：你可以添加哪些功能来定制 Claude 的知识、接入外部服务、自动化工作流。

> 核心代理循环的工作原理见 [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works)。

**刚接触 Claude Code？** 先从 [CLAUDE.md](https://code.claude.com/docs/en/memory) 写起，记录项目约定；后续遇到具体需求时再逐步添加其他扩展。

## 总览

**各扩展点嵌入代理循环的不同阶段，各司其职。**

- **[CLAUDE.md](https://code.claude.com/docs/en/memory)** — 每次会话都加载的持久上下文
- **[Skills](https://code.claude.com/docs/en/skills)** — 可复用的知识与可调用的工作流
- **[代码智能](https://code.claude.com/docs/en/tools-reference#lsp-tool-behavior)** — 连接语言服务器，提供符号级导航和实时类型错误
- **[MCP](https://code.claude.com/docs/en/mcp)** — 连接外部服务与工具
- **[子代理](https://code.claude.com/docs/en/sub-agents)** — 在隔离上下文中运行独立循环，返回摘要
- **[Agent Teams](https://code.claude.com/docs/en/agent-teams)** — 协调多个独立会话，通过共享任务和点对点消息协作
- **[Hooks](https://code.claude.com/docs/en/hooks-guide)** — 在生命周期事件上触发脚本、HTTP 请求、Prompt 或子代理
- **[插件](https://code.claude.com/docs/en/plugins)** 和 **[市场](https://code.claude.com/docs/en/plugin-marketplaces)** — 打包和分发以上功能

[Skills](https://code.claude.com/docs/en/skills) 是最灵活的扩展。Skill 是一个包含知识、工作流或指令的 Markdown 文件，可以通过 `/deploy` 这样的命令调用，也可以让 Claude 在相关场景自动加载。Skill 既可以在当前会话中运行，也可以通过子代理在隔离上下文中执行。

## 选择合适的扩展方式

**扩展方式从"常驻上下文"到"按需能力"再到"后台自动化"逐层递进。** 下表展示了各功能的定位和适用场景：

| 功能 | 做什么 | 何时使用 | 示例 |
| --- | --- | --- | --- |
| **CLAUDE.md** | 每次会话自动加载的持久上下文 | 项目约定、"总是做 X"规则 | "用 pnpm 不用 npm，提交前跑测试" |
| **Skill** | Claude 可使用的指令、知识和工作流 | 可复用内容、参考文档、可重复任务 | `/deploy` 执行部署检查清单；API 文档 Skill 描述接口模式 |
| **子代理** | 隔离执行环境，返回汇总结果 | 上下文隔离、并行任务、专业工人 | 研究任务读取大量文件但只返回关键发现 |
| **[Agent Teams](https://code.claude.com/docs/en/agent-teams)** | 协调多个独立 Claude Code 会话 | 并行研究、新功能开发、多假设调试 | 同时派出安全、性能、测试三个 Reviewer |
| **[代码智能](https://code.claude.com/docs/en/tools-reference#lsp-tool-behavior)** | 语言服务器导航与诊断 | 类型语言、大型代码库（grep 太慢或不精确） | 跳转到符号定义，而不是读整个文件 |
| **MCP** | 连接外部服务 | 需要外部数据或操作 | 查询数据库、发 Slack、控制浏览器 |
| **Hook** | 事件触发的脚本/HTTP/Prompt/子代理 | 每次匹配事件都必须执行的自动化 | 每次文件编辑后跑 ESLint |
| **[Artifact](https://code.claude.com/docs/en/artifacts)** | 将会话输出发布为私有交互式网页 | 需要可视化展示或分享的输出 | 事故时间线在调查过程中实时更新 |

**[插件](https://code.claude.com/docs/en/plugins)** 是打包层，将 Skills、Hooks、子代理和 MCP 服务器捆绑为一个可安装单元。插件 Skill 带命名空间（如 `/my-plugin:review`），多个插件可以共存。当你想在多个仓库复用同一套配置或分发给他人时，用插件加 **[市场](https://code.claude.com/docs/en/plugin-marketplaces)**。

### 渐进式构建

**不需要一开始就配齐所有扩展，识别"触发信号"再按需添加。** 大多数团队按如下顺序演进：

| 触发信号 | 应该添加什么 |
| :--- | :--- |
| Claude 犯了两次相同的约定错误 | 写进 [CLAUDE.md](https://code.claude.com/docs/en/memory) |
| 你每次都输入同一段 Prompt 来启动任务 | 保存为用户可调用的 [Skill](https://code.claude.com/docs/en/skills) |
| 第三次把同一份 Playbook 粘贴到聊天里 | 封装为 [Skill](https://code.claude.com/docs/en/skills) |
| 你反复从浏览器标签复制 Claude 看不到的数据 | 接入 [MCP 服务器](https://code.claude.com/docs/en/mcp) |
| Claude 读了很多文件才能找到符号定义 | 安装对应语言的[代码智能插件](https://code.claude.com/docs/en/discover-plugins#code-intelligence) |
| 子任务产生大量输出但你之后不会再引用 | 通过[子代理](https://code.claude.com/docs/en/sub-agents)路由 |
| 想让某些事每次自动发生、无需手动要求 | 写一个 [Hook](https://code.claude.com/docs/en/hooks-guide) |
| 第二个仓库也需要同样的配置 | 打包为[插件](https://code.claude.com/docs/en/plugins) |

同样的信号也告诉你何时更新已有配置：反复犯错 → 改 CLAUDE.md，反复手动微调的工作流 → 改 Skill。

### 区分相似功能

**一些功能看起来相似，实际上解决不同层面的问题。**

#### Skill vs 子代理

| 维度 | Skill | 子代理 |
| --- | --- | --- |
| **本质** | 可复用的指令、知识或工作流 | 拥有独立上下文的隔离工人 |
| **核心价值** | 跨上下文共享内容 | 上下文隔离，工作在别处进行，只返回摘要 |
| **[上下文窗口](https://code.claude.com/docs/en/context-window)影响** | 加入主窗口 | 使用独立窗口，有自己的输入/输出 token |
| **适合** | 参考资料、可调用的工作流 | 需要读取大量文件的任务、并行工作、专业工人 |

Skill 分两种：**参考型**提供 Claude 在整个会话中使用的知识（如 API 风格指南）；**动作型**告诉 Claude 做某件具体的事（如 `/deploy`）。

子代理可能会读几十个文件做大量搜索，但主会话只收到摘要——省上下文。

二者可以组合：子代理可以预加载指定 Skill（`skills:` 字段），Skill 可以通过 `context: fork` 在隔离上下文中运行。

#### CLAUDE.md vs Skill

| 维度 | CLAUDE.md | Skill |
| --- | --- | --- |
| **加载** | 每次会话自动加载 | 按需加载 |
| **可包含文件** | 支持 `@path` 导入 | 支持 `@path` 导入 |
| **可触发工作流** | 不支持 | 支持，`/<name>` |
| **适合** | "总是做 X"规则 | 参考资料、可调用的工作流 |

经验法则：CLAUDE.md 控制在 200 行以内。超了就把参考内容移到 Skill，或拆到 [`.claude/rules/`](https://code.claude.com/docs/en/memory#organize-rules-with-claude/rules/) 文件。

#### CLAUDE.md vs Rules vs Skills

| 维度 | CLAUDE.md | `.claude/rules/` | Skill |
| --- | --- | --- | --- |
| **加载** | 每次会话 | 每次会话，或匹配文件被打开时 | 按需，被调用或匹配时 |
| **作用域** | 整个项目 | 可按文件路径限定 | 任务级 |
| **适合** | 核心约定和构建命令 | 语言/目录级指南 | 参考资料、可重复工作流 |

Rules 配合 [`paths` frontmatter](https://code.claude.com/docs/en/memory#path-specific-rules) 可以只在 Claude 处理匹配文件时加载，节省上下文。

#### 子代理 vs Agent Teams

| 维度 | 子代理 | Agent Teams |
| --- | --- | --- |
| **上下文** | 自有窗口，结果返回调用方 | 自有窗口，完全独立 |
| **通信** | 只向主代理汇报 | 队友之间直接通信 |
| **协调** | 主代理管理所有工作 | 共享任务列表+自我协调 |
| **适合** | 只需结果的聚焦任务 | 需要讨论和协作的复杂工作 |
| **Token 开销** | 较低：结果摘要回主上下文 | 较高：每个队友是独立实例 |

过渡信号：并行子代理碰到上下文上限，或者子代理之间需要互相通信时，切换到 Agent Teams。

> Agent Teams 目前为实验功能，默认关闭。详见 [Agent Teams](https://code.claude.com/docs/en/agent-teams)。

#### MCP vs Skill

| 维度 | MCP | Skill |
| --- | --- | --- |
| **本质** | 连接外部服务的协议 | 知识、工作流和参考资料 |
| **提供** | 工具和数据访问 | 知识、工作流、参考资料 |
| **示例** | Slack 集成、数据库查询、浏览器控制 | 代码评审检查清单、部署工作流、API 风格指南 |

二者解决不同问题且配合良好：MCP 提供工具连接，Skill 教 Claude 如何高效使用这些工具。例如 MCP 连上数据库，Skill 描述数据模型、常用查询模式和各任务对应的表。

#### Hook vs Skill

| 维度 | Hook | Skill |
| --- | --- | --- |
| **执行内容** | Shell 命令/HTTP 请求/LLM Prompt/子代理 | Claude 阅读并遵循的指令 |
| **触发方式** | [生命周期事件](https://code.claude.com/docs/en/hooks#hook-events)如 `PostToolUse`、`SessionStart` | 你输入 `/<name>`，或 Claude 根据描述自动匹配 |
| **确定性** | 事件触发即必定执行 | Claude 自行解读指令，结果可能有变 |
| **上下文开销** | 零（除非 Hook 返回输出） | 描述每次会话加载，完整内容使用时加载 |
| **适合** | 格式化、拦截危险命令、日志、通知 | 需要推理的工作流、参考资料、多步任务 |

关键区别：**把护栏放在 Hook 里**。CLAUDE.md 里写"不要编辑 `.env`"只是请求不是保证；`PreToolUse` Hook 拦截编辑才是强制执行。

### 功能分层规则

**同一功能在多个层级定义时，遵循"合并或覆盖"规则。**

- **CLAUDE.md** — 累加：所有层级的内容同时生效。工作目录及以上的文件启动时加载，子目录的文件在你进入时加载。冲突时更具体的优先。详见 [CLAUDE.md 加载机制](https://code.claude.com/docs/en/memory#how-claude-md-files-load)。
- **Skills 和子代理** — 同名覆盖：managed > user > project（Skills）；managed > CLI flag > project > user > plugin（子代理）。插件 Skill 有[命名空间](https://code.claude.com/docs/en/plugins#add-skills-to-your-plugin)避免冲突。
- **MCP 服务器** — 同名覆盖：local > project > user。详见 [MCP 作用域](https://code.claude.com/docs/en/mcp#scope-hierarchy-and-precedence)。
- **Hooks** — 合并：所有来源的 Hook 只要匹配事件就会触发。详见 [Hooks](https://code.claude.com/docs/en/hooks)。

### 组合使用

**真实配置是多种扩展的组合，让每种功能做它最擅长的事。**

| 模式 | 组合方式 | 示例 |
| --- | --- | --- |
| **Skill + MCP** | MCP 提供连接，Skill 教 Claude 怎么用 | MCP 连数据库，Skill 描述 schema 和查询模式 |
| **Skill + 子代理** | Skill 派出子代理做并行工作 | `/audit` Skill 启动安全、性能、风格三个子代理 |
| **CLAUDE.md + Skills** | CLAUDE.md 放常驻规则，Skill 放按需参考 | CLAUDE.md 说"遵循 API 约定"，Skill 包含完整风格指南 |
| **Hook + MCP** | Hook 通过 MCP 触发外部操作 | 编辑关键文件后 Hook 自动发 Slack 通知 |

## 理解上下文开销

**每个扩展都消耗上下文窗口，过多不仅撑满窗口还会引入噪声。** 噪声会让 Skill 匹配不准确或让 Claude 忘记约定。下表帮你权衡取舍。交互式上下文视图见 [Explore the context window](https://code.claude.com/docs/en/context-window)。

### 各功能的上下文开销

| 功能 | 何时加载 | 加载什么 | 上下文开销 |
| --- | --- | --- | --- |
| **CLAUDE.md** | 会话开始 | 全部内容 | 每个请求 |
| **Skills** | 会话开始 + 使用时 | 开始时加载描述，使用时加载全部 | 低（描述每请求加载）* |
| **MCP 服务器** | 会话开始 | 工具名称；完整 schema 按需 | 低，直到工具被使用 |
| **代码智能** | 文件编辑后 + 按需 | 编辑后的诊断信息；查找时的符号位置 | 低；减少了其他地方的文件读取 |
| **子代理** | 被启动时 | 带指定 Skills 的全新上下文 | 与主会话隔离 |
| **Hooks** | 触发时 | 无（外部执行） | 零（除非 Hook 返回额外上下文） |

*默认行为：Skill 描述在会话开始时加载，让 Claude 判断何时使用。设置 `disable-model-invocation: true` 可让 Skill 完全不对 Claude 可见（直到你手动调用），上下文开销降为零。对于你没有写的 Skill，可在 settings 中设置 [`skillOverrides`](https://code.claude.com/docs/en/skills#override-skill-visibility-from-settings) 达到同样效果。

### 各功能的加载时机

**不同功能在会话的不同阶段加载。**

![Context loading](assets/context-loading.svg)

#### CLAUDE.md

- **何时：** 会话开始
- **加载什么：** 所有层级（managed、user、project）的 CLAUDE.md 全部内容
- **继承关系：** Claude 从工作目录向上读取 CLAUDE.md，进入子目录时发现嵌套的文件。详见 [CLAUDE.md 加载机制](https://code.claude.com/docs/en/memory#how-claude-md-files-load)

> 建议：CLAUDE.md 控制在 200 行以内，参考资料移到按需加载的 Skill。

#### Skills

- **何时：** 取决于配置。默认描述在会话开始时加载，完整内容在使用时加载。设置了 `disable-model-invocation: true` 的 Skill 在你调用前不会加载任何内容。
- **加载什么：** 对于模型可调用的 Skill，Claude 每次请求都能看到名称和描述；调用后加载完整内容。
- **Claude 如何选择 Skill：** 将你的任务与 Skill 描述匹配。描述模糊或重叠时可能加载错误。要指定 Skill，用 `/<name>` 手动调用。
- **在子代理中：** Skills 不是按需加载，而是在子代理启动时通过 `skills` 字段完整预加载。子代理仍可通过 Skill tool 发现并调用未列出的 Skill。

> 建议：有副作用的 Skill 设置 `disable-model-invocation: true`，省上下文且确保只有你能触发。

#### MCP 服务器

- **何时：** 会话开始
- **加载什么：** 已连接服务器的工具名称；完整 JSON schema 延迟到 Claude 需要时加载
- **上下文开销：** 默认开启 [Tool Search](https://code.claude.com/docs/en/mcp#scale-with-mcp-tool-search)，闲置 MCP 工具消耗极少上下文

> 建议：运行 `/mcp` 查看连接状态和每个服务器的 token 开销。Claude Code 会[自动重连远程服务器](https://code.claude.com/docs/en/mcp#automatic-reconnection)，也可以断开当前不用的。

#### 代码智能

- **何时：** 文件编辑后 + Claude 导航代码时按需
- **加载什么：** 编辑后的类型错误和警告；查找符号时的定义、引用和类型信息
- **上下文开销：** 低。符号查找经常替代大范围文件读取，净上下文消耗可能反而下降

> 建议：安装对应语言的[代码智能插件](https://code.claude.com/docs/en/discover-plugins#code-intelligence)后 LSP 工具才会激活。

#### 子代理

- **何时：** 按需，当你或 Claude 为任务启动一个子代理时
- **加载什么：** 全新隔离上下文，包含：
  - 代理自身的系统提示（不是完整的 Claude Code 系统提示）
  - `skills:` 字段中列出的 Skill 完整内容
  - CLAUDE.md 和 git 状态（内置的 Explore 和 Plan 代理[省略这两项](https://code.claude.com/docs/en/sub-agents#what-loads-at-startup)）
  - 主代理在 prompt 中传入的上下文
- **上下文开销：** 与主会话隔离，不继承会话历史或已调用的 Skill

> 建议：不需要完整会话上下文的工作用子代理处理，隔离性防止撑大主会话。

#### Hooks

- **何时：** 触发时。在工具执行、会话边界、Prompt 提交、权限请求、压缩等生命周期事件触发。完整事件列表见 [Hooks](https://code.claude.com/docs/en/hooks)。
- **加载什么：** 默认不加载任何内容，Hooks 在主会话外执行
- **上下文开销：** 零（除非 Hook 返回输出作为消息加入会话）

> 建议：Hooks 适合不影响 Claude 上下文的副作用（lint、日志）。

## 延伸阅读

各功能均有独立指南，包含配置说明、示例和选项：

- [CLAUDE.md](https://code.claude.com/docs/en/memory) — 存储项目上下文、约定和指令
- [Skills](https://code.claude.com/docs/en/skills) — 赋予 Claude 领域知识和可复用工作流
- [子代理](https://code.claude.com/docs/en/sub-agents) — 将工作卸载到隔离上下文
- [Agent Teams](https://code.claude.com/docs/en/agent-teams) — 协调多个并行会话
- [MCP](https://code.claude.com/docs/en/mcp) — 连接外部服务
- [Hooks](https://code.claude.com/docs/en/hooks-guide) — 用 Hooks 自动化操作
- [插件](https://code.claude.com/docs/en/plugins) — 打包和分享功能集
- [市场](https://code.claude.com/docs/en/plugin-marketplaces) — 托管和分发插件集合
