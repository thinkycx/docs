---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】动态工作流编排
description: Claude Code 的动态工作流功能允许通过 JavaScript 脚本大规模编排子代理，适用于代码库审计、大规模迁移和交叉验证研究等场景。本文介绍了工作流的使用时机、运行方式、保存复用以及成本管理。
category: translation
tags: [claude-code, workflows, orchestration, translation]
refs: [https://code.claude.com/docs/en/workflows.md]
---

# 用动态工作流大规模编排子代理

> 动态工作流通过 Claude 编写的脚本来编排大量子代理，你可以反复运行。适用于代码库审计、大规模迁移和交叉验证研究。

> [!NOTE]
> 动态工作流需要 Claude Code v2.1.154 或更高版本，支持所有付费计划、Anthropic API、Amazon Bedrock、Google Cloud Vertex AI 和 Microsoft Foundry。Pro 计划用户可在 `/config` 的 Dynamic workflows 行开启。

**动态工作流是一段 JavaScript 脚本，用于大规模编排[子代理](https://code.claude.com/docs/en/sub-agents)。** Claude 为你描述的任务编写脚本，运行时在后台执行，你的会话始终保持可交互状态。

**适用场景：当一个任务需要的代理数量超出单次对话所能协调的范围，或者你希望把编排逻辑固化为可阅读、可重跑的脚本时，就该使用工作流。** 典型案例包括：全代码库 bug 扫描、500 文件迁移、需要多源交叉验证的研究问题、以及值得从多个角度起草方案再做最终决策的复杂规划。

---

## 何时使用工作流

**[子代理](https://code.claude.com/docs/en/sub-agents)、[技能](https://code.claude.com/docs/en/skills)、[代理团队](https://code.claude.com/docs/en/agent-teams)和工作流都能完成多步骤任务，区别在于"谁持有执行计划"。**

| | 子代理 | 技能 | 代理团队 | 工作流 |
| :--- | :--- | :--- | :--- | :--- |
| 本质 | Claude 生成的执行者 | Claude 遵循的指令 | 主代理监督的对等会话 | 运行时执行的脚本 |
| 谁决定下一步 | Claude，逐轮决定 | Claude，按提示词执行 | 主代理，逐轮决定 | 脚本 |
| 中间结果存放位置 | Claude 的上下文窗口 | Claude 的上下文窗口 | 共享任务列表 | 脚本变量 |
| 可复用的是什么 | 执行者的定义 | 指令本身 | 团队定义 | 编排逻辑本身 |
| 规模 | 每轮少量委派任务 | 与子代理相同 | 少量长时间运行的对等体 | 每次运行数十到数百个代理 |
| 中断后的行为 | 重启该轮 | 重启该轮 | 队友继续运行 | 同一会话内可恢复 |

**工作流将执行计划移入代码。** 在子代理、技能和代理团队中，Claude 是编排者：它逐轮决定下一步生成或分配什么，所有结果都落入上下文窗口。而工作流脚本自身掌控循环、分支和中间结果，Claude 的上下文只保留最终答案。

**将计划代码化还能实现可重复的质量模式，不仅仅是运行更多代理：** 工作流可以让独立代理对彼此的发现进行对抗性审查后再汇报，或从多个角度起草方案并相互权衡，从而获得比单次执行更可信的结果。

---

## 运行内置工作流

**体验工作流最快的方式是运行 `/deep-research`，这是 Claude Code 内置的研究型工作流。**

### 步骤 1：启动工作流

用一个你想调研的问题运行 `/deep-research`。它会从多个角度发起网络搜索、抓取并交叉验证找到的来源，最终综合出一份带引用的报告。

```text
/deep-research What changed in the Node.js permission model between v20 and v22?
```

### 步骤 2：授权工作流

Claude Code 会询问是否允许运行该工作流。选择 **Yes** 继续。具体提示取决于你的权限模式，详见[运行前批准计划](#运行前批准计划)。

### 步骤 3：查看进度

运行在后台启动。执行 `/workflows`，用方向键选中该运行，按 Enter 打开进度视图：

```text
/workflows
```

视图显示每个阶段的代理数量、Token 消耗和耗时。可以钻入任何阶段查看其代理及各自发现。详见[监控运行状态](#监控运行状态)。

你也可以在输入框下方的任务面板查看：运行期间会显示一行进度摘要。按下箭头聚焦，按 Enter 展开。

### 步骤 4：阅读报告

运行完成后，报告直接呈现在你的会话中。报告会标注每项结论的来源，未通过交叉验证的声明已被过滤掉。

---

**如果想为自定义任务运行工作流，请[让 Claude 编写一个](#让-claude-编写工作流)。** 一旦运行结果符合预期，你可以[保存它](#保存工作流以复用)作为自己的命令。

### 内置工作流列表

| 命令 | 功能 |
| :--- | :--- |
| `/deep-research <question>` | 从多个角度对问题发起网络搜索，抓取并交叉验证来源，对每项声明投票，返回带引用的报告，未通过交叉验证的声明会被过滤。需要 [WebSearch 工具](https://code.claude.com/docs/en/tools-reference#websearch-tool-behavior)可用 |

你[自己保存的工作流](#保存工作流以复用)也会以同样方式变成命令，出现在 `/` 自动补全中。

### 监控运行状态

**工作流在后台运行，会话始终可交互。** 随时运行 `/workflows` 查看正在运行和已完成的工作流，选中一个打开进度视图。

```text
/workflows
```

进度视图显示每个阶段的代理数量、Token 消耗和耗时。底部列出可用的快捷键：

| 按键 | 操作 |
| :--- | :--- |
| `↑` / `↓` | 选择阶段或代理 |
| `Enter` 或 `→` | 钻入选中的阶段，再钻入代理可查看其提示词、近期工具调用和结果 |
| `Esc` | 返回上一层 |
| `j` / `k` | 内容溢出时滚动代理详情 |
| `f` | 按状态过滤选中阶段的代理列表，再按循环切换 |
| `p` | 暂停或恢复运行 |
| `x` | 停止选中的代理，或当焦点在运行级别时停止整个工作流 |
| `r` | 重启选中的正在运行的代理 |
| `s` | [保存](#保存工作流以复用)该运行的脚本为命令 |

---

## 让 Claude 编写工作流

**你可以通过两种方式让 Claude 为你的任务编写工作流：**

* **[在提示词中请求工作流](#在提示词中请求工作流)：** 用自然语言描述或包含关键词 `ultracode`，Claude 就会为该任务编写工作流。
* **[用 ultracode 让 Claude 自动决定](#用-ultracode-让-claude-自动决定)：** 设置 `/effort ultracode`，Claude 会为会话中每个实质性任务自动规划工作流。

你也可以运行已有的工作流命令：如[内置工作流](#内置工作流列表) `/deep-research`，或你[已保存的](#保存工作流以复用)工作流。

### 在提示词中请求工作流

**要将单个任务作为工作流运行而不改变会话的 effort 级别，在提示词中包含关键词 `ultracode` 即可。** 用自然语言请求（如"use a workflow"或"run a workflow"）同样有效：Claude 将直接请求视为等效的触发。v2.1.160 之前的字面触发关键词是 `workflow`；自然语言请求在两个版本中都有效。

```text
ultracode: audit every API endpoint under src/routes/ for missing auth checks
```

Claude Code 会高亮输入中的关键词，然后 Claude 为该任务编写工作流脚本，而非逐轮处理。如果你不想启动工作流，按 macOS 上的 `Option+W` 或 Windows/Linux 上的 `Alt+W` 取消本次高亮，或在光标紧跟高亮关键词后面时按退格键。要彻底禁用关键词触发，在 `/config` 中关闭 Ultracode keyword trigger。

**如果运行结果符合预期，可以之后[将其保存为命令](#保存工作流以复用)。**

如果你已有其他形式的编排器（比如一组子代理提示词文件夹，或一个扇出工作的技能），可以将其指给 Claude 并要求生成等效的工作流。

### 用 ultracode 让 Claude 自动决定

**Ultracode 是 Claude Code 的一项设置，结合了 `xhigh` [推理 effort](https://code.claude.com/docs/en/model-config#adjust-effort-level) 和自动工作流编排。** 开启后，Claude 会为每个实质性任务主动规划工作流，无需你逐次要求。

```text
/effort ultracode
```

开启 ultracode 后，Claude 自行判断任务是否需要工作流。一个请求可能产生多个连续工作流：一个用于理解代码，一个用于修改，一个用于验证。这适用于会话中的每个任务，因此每个请求会消耗更多 Token、花费更长时间。

**Ultracode 仅在当前会话有效，新会话时重置。** 回到日常工作时用 `/effort high` 降档。该功能仅在支持 `xhigh` [effort](https://code.claude.com/docs/en/model-config#adjust-effort-level) 的模型上可用；不支持的模型中 `/effort` 菜单不会显示此选项。

### 运行前批准计划

**在 CLI 中，每次运行前的提示会显示规划的阶段和以下选项：**

* **Yes, run it**：开始运行
* **Yes, and don't ask again for `<name>` in `<path>`**：开始运行，并对此项目中此工作流以后不再询问
* **View raw script**：在决定前查看脚本
* **No**：取消

`Ctrl+G` 在编辑器中打开脚本。`Tab` 可在运行前调整提示词。

**是否显示此提示取决于你的[权限模式](https://code.claude.com/docs/en/permission-modes)：**

| 权限模式 | 何时提示 |
| :--- | :--- |
| Default, accept edits | 每次运行都提示，除非你已对该项目中该工作流选过"Yes, and don't ask again" |
| Auto | 仅首次启动时提示。任何"Yes"都会记录到用户设置中，后续启动不再提示。开启 ultracode 时完全跳过 |
| Bypass permissions, `claude -p`, Agent SDK | 从不提示，直接开始运行 |

在桌面应用中，会显示一张审批卡片，包含工作流名称、阶段列表和 Token 消耗提醒，提供 **Once**、**Always** 和 **Deny** 操作。进度视图出现在后台任务侧边栏中。

**你的权限模式仅控制上述启动提示。** 工作流生成的子代理始终以 `acceptEdits` 模式运行，并继承你的[工具白名单](https://code.claude.com/docs/en/settings#permission-settings)，无论你会话的模式如何。文件编辑会自动批准。

不在白名单中的 Shell 命令、网络请求和 MCP 工具仍可能在运行中途提示你。要避免长时间运行被打断，启动前将代理需要的命令加入白名单。

在 `claude -p` 和 Agent SDK 中没有人可以响应提示，因此工具调用按你配置的权限规则执行，无需交互确认。

### 保存工作流以复用

**当 Claude 为你会重复执行的任务编写了工作流时，可以将该运行的脚本保存为命令。** 这样，像每个分支都要跑的代码审查这样的流程就能每次执行相同的编排逻辑。

运行 `/workflows`，选中要保留的运行，按 `s`。在保存对话框中，Tab 切换两个保存位置：

* 项目中的 `.claude/workflows/`：与克隆仓库的所有人共享
* Home 目录下的 `~/.claude/workflows/`：在所有项目中可用，仅你可见

按 Enter 保存。工作流在后续会话中以 `/<name>` 形式运行。

**在含有多个 `.claude/` 目录的 monorepo 中，** 你可以将工作流放在它所适用的包旁边。从 v2.1.178 起，保存到项目位置时会写入工作目录到仓库根之间最近的已存在的 `.claude/workflows/` 目录，如果不存在则写入仓库根。项目工作流也会从该路径上的每个 `.claude/workflows/` 加载，同名时运行离工作目录最近的那个。

如果项目工作流和个人工作流同名，运行项目的那个。

### 向保存的工作流传递输入

**保存的工作流可以通过 `args` 参数接收输入。** 脚本以全局变量 `args` 的形式读取它。用这种方式在调用时提供研究问题、目标路径列表或配置对象，无需每次修改脚本。

以下提示词用一组 issue 编号运行已保存的工作流：

```text
> Run /triage-issues on issues 1024, 1025, and 1030
```

Claude 将列表作为结构化数据传递，脚本可以直接对 `args` 调用数组和对象方法，无需额外解析。如果省略 `args`，脚本中该全局变量为 `undefined`。

---

## 工作流的运行机制

**工作流运行时在隔离环境中执行脚本，独立于你的对话。** 中间结果保留在脚本变量中，而非进入 Claude 的上下文。

每次运行都会将脚本写入 `~/.claude/projects/` 下你会话目录中的文件。Claude 在运行开始时收到文件路径，你可以询问它。你可以打开该文件查看 Claude 编写的编排逻辑，与之前运行的脚本做 diff，或编辑后让 Claude 从修改版重新启动。

运行时会跟踪每个代理的结果，这使得运行可以在同一会话内[恢复](#暂停后恢复)。

### 行为与限制

运行时施加以下约束：

| 约束 | 原因 |
| :--- | :--- |
| 运行中无法接收用户输入 | 只有代理权限提示能暂停运行。如需阶段间签核，将每个阶段作为独立工作流运行 |
| 工作流本身无法直接访问文件系统或 Shell | 代理负责读写和执行命令，脚本负责协调代理 |
| 最多 16 个并发代理（CPU 核心有限的机器上更少） | 限制本地资源消耗 |
| 每次运行最多 1,000 个代理 | 防止失控循环 |

---

## 管理运行

**运行启动后，通过 `/workflows` 视图管理，或展开输入框下方任务面板中的进度行。**

### 暂停后恢复

**如果你停止了一次运行，可以恢复它：** 已完成的代理返回缓存结果，其余代理实时运行。在 `/workflows` 中选中已暂停的运行按 `p` 恢复，或要求 Claude 用相同脚本重新启动。

恢复仅在同一 Claude Code 会话内有效。如果在工作流运行期间退出 Claude Code，下次会话会从头开始。

### 成本

**工作流会生成大量代理，单次运行可能消耗比会话内逐步完成同一任务明显更多的 Token。** 运行计入你计划的用量和速率限制，与其他会话相同。

**在承诺大型任务前，先在小范围试运行来评估开销：** 一个目录而非整个仓库，或一个窄问题而非宽泛问题。`/workflows` 视图在运行过程中显示每个代理的 Token 消耗，你可以随时停止运行而不丢失已完成的工作。运行时的[代理上限](#行为与限制)限制了单次运行能生成的最大代理数，从而约束了失控脚本的成本。

工作流中的每个代理使用你会话的模型，除非脚本将某个阶段路由到不同模型。控制模型成本的方法：

* 在大型运行前检查 `/model`，确认是否在用日常切换的小模型
* 描述任务时要求 Claude 对不需要最强模型的阶段使用较小模型

### 关闭工作流

**工作流在 CLI、桌面应用、IDE 扩展、`claude -p` [非交互模式](https://code.claude.com/docs/en/headless)和 [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) 上都可用。** 相同的禁用设置适用于所有界面。

为自己关闭工作流：

* 在 `/config` 中关闭 Dynamic workflows 开关。跨会话持久化。
* 在 `~/.claude/settings.json` 中设置 `"disableWorkflows": true`。跨会话持久化。
* 设置环境变量 `CLAUDE_CODE_DISABLE_WORKFLOWS=1`。启动时读取，因此在你设置它的任何地方生效。

为整个组织关闭工作流：在[托管设置](https://code.claude.com/docs/en/server-managed-settings)中设置 `"disableWorkflows": true`，或使用 [Claude Code 管理员设置](https://claude.ai/admin-settings/claude-code)页面的开关。

关闭后，内置工作流命令不可用，`ultracode` 关键词不再触发运行，`ultracode` 从 `/effort` 菜单中移除。

---

## 相关资源

* [并行运行代理](https://code.claude.com/docs/en/agents)：比较子代理、代理视图、代理团队和工作流
* [创建自定义子代理](https://code.claude.com/docs/en/sub-agents)：工作流编排的基本执行单元
* [管理成本](https://code.claude.com/docs/en/costs)：多代理运行如何计入用量限制
