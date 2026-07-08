---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Agent 团队编排
description: Agent Teams 让多个 Claude Code 实例协同工作。一个会话做领导协调工作，队友独立工作并互相通信。本文介绍启用、控制和最佳实践。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/agent-teams.md
  - en-source/agent-teams.md
---

# 编排 Claude Code 会话团队

> 协调多个 Claude Code 实例作为团队工作，共享任务、agent 间通信和集中管理。

**Agent Teams 是实验性功能，默认禁用。** 在 [settings.json](https://code.claude.com/docs/en/settings) 或环境变量中添加 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` 启用。未设置时不会建立团队、不写入团队目录、Claude 不会生成或提议队友。Agent teams 有[已知限制](#限制)。

**Agent teams 让你协调多个 Claude Code 实例协同工作。** 一个会话做团队领导（lead），协调工作、分配任务并综合结果。队友独立工作，各有自己的上下文窗口，彼此直接通信。

与 [subagent](https://code.claude.com/docs/en/sub-agents) 不同——subagent 在单个会话中运行且只能向主 agent 汇报——你可以直接与各个队友交互，无需通过 lead。

> 本页描述 v2.1.178 起的 agent teams。设置 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` 后，生成队友不再需要设置步骤，清理在会话退出时自动完成。

## 何时使用 agent teams

**Agent teams 对并行探索有真正价值的任务最有效。** 最强的使用场景：

- **研究和评审**：多个队友同时调查问题的不同方面，然后分享和质疑彼此的发现
- **新模块或功能**：队友各自负责独立部分互不干扰
- **竞争假设调试**：队友并行测试不同理论，更快收敛到答案
- **跨层协调**：跨前端、后端和测试的变更，各由不同队友负责

**Agent teams 增加协调开销并消耗显著更多 token。** 队友能独立运作时效果最好。顺序任务、同文件编辑或高依赖性工作更适合单会话或 [subagent](https://code.claude.com/docs/en/sub-agents)。

### 与 subagent 对比

| 维度 | Subagent | Agent Teams |
| --- | --- | --- |
| **上下文** | 自有上下文窗口；结果返回调用者 | 自有上下文窗口；完全独立 |
| **通信** | 仅向主 agent 汇报结果 | 队友之间直接消息 |
| **协调** | 主 agent 管理所有工作 | 共享任务列表，自协调 |
| **适用于** | 只需结果的聚焦任务 | 需要讨论和协作的复杂工作 |
| **Token 成本** | 较低：结果摘要返回主上下文 | 较高：每个队友是独立的 Claude 实例 |

**需要快速聚焦的工人汇报结果时用 subagent。队友需要分享发现、互相质疑和自主协调时用 agent teams。**

## 启用 agent teams

设置 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` 环境变量为 `1`：

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

## 启动第一个 agent team

**启用后，用自然语言描述任务和想要的队友。** Claude 根据提示生成并协调工作。

示例（三个角色独立、可不等待彼此地探索问题）：

```text
I'm designing a CLI tool that helps developers track TODO comments across
their codebase. Spawn three teammates to explore this from different angles:
one on UX, one on technical architecture, one playing devil's advocate.
```

Claude 填充[共享任务列表](https://code.claude.com/docs/en/interactive-mode#task-list)、为各视角生成队友、让他们探索问题、完成后综合发现。

Lead 的终端在提示输入下方的 agent 面板列出队友：

- **上下箭头**：选择队友
- **Enter**：打开选中队友的记录并直接发消息
- **Escape**：中断选中队友当前的 turn

v2.1.199 起，当任何队友或 subagent 仍在工作时，空闲队友的行保留在面板中。所有 agent 空闲后，空闲行在 30 秒后隐藏（下次 turn 重新出现）；队友仍在运行和可寻址。

超过三个队友空闲时，多出的行折叠为一行（如 `2 idle agents`）。选中后按 Enter 展开，Esc 折叠。工作中、失败的队友和你正在查看的队友始终保持独立行。

如需每个队友在独立分屏面板中，参见[选择显示模式](#选择显示模式)。

## 控制 agent team

**用自然语言告诉 lead 你想要什么。** 它处理团队协调、任务分配和委派。

### 选择显示模式

两种显示模式：

| 模式 | 说明 |
| --- | --- |
| **In-process** | 所有队友在主终端运行。用上下箭头选择队友后按 Enter 查看。任何终端可用，无需额外设置 |
| **Split panes** | 每个队友独立面板。可同时看到所有输出，点击进入面板直接交互。需要 tmux 或 iTerm2 |

默认为 `"in-process"`。在 `~/.claude/settings.json` 中设置 [`teammateMode`](https://code.claude.com/docs/en/settings#available-settings) 覆盖：

```json
{
  "teammateMode": "auto"
}
```

或单次会话标志：

```bash
claude --teammate-mode auto
```

Split-pane 模式需要 [tmux](https://github.com/tmux/tmux/wiki) 或 iTerm2 的 [`it2` CLI](https://github.com/mkusaka/it2)。

> v2.1.186 起，设置 `"iterm2"` 可明确使用 iTerm2 原生分屏面板。

### 指定队友和模型

Claude 根据任务决定队友数量，你也可以明确指定：

```text
Spawn 4 teammates to refactor these modules in parallel. Use Sonnet for
each teammate.
```

**队友默认不继承 lead 的 `/model` 选择。** 在 `/config` 中设置 **Default teammate model** 可更改未指定时使用的模型。选择 **Default (leader's model)** 让队友跟随 lead 的当前模型。

队友继承 lead 的 [effort level](https://code.claude.com/docs/en/model-config#adjust-effort-level)。

### 要求队友先提交计划

对于复杂或有风险的任务，可要求队友先规划再实施：

```text
Spawn an architect teammate to refactor the authentication module.
Require plan approval before they make any changes.
```

**队友完成规划后向 lead 发送计划批准请求。** Lead 审查并批准或带反馈拒绝。被拒绝后队友留在规划模式修订并重新提交。批准后退出规划模式开始实施。

Lead 自主做批准决定。要影响其判断，在提示中给出标准，如"只批准包含测试覆盖的计划"或"拒绝修改数据库 schema 的计划"。

### 直接与队友交谈

每个队友是完整独立的 Claude Code 会话。可直接向任何队友发消息。

- **In-process 模式**：上下箭头选择队友后按 Enter 查看，输入发送消息。按 `x` 停止选中队友。按 `Ctrl+T` 切换任务列表。
- **Split-pane 模式**：点击队友面板直接交互。

查看 in-process 队友时，普通文本和 [skills](https://code.claude.com/docs/en/skills) 发送给该队友，但内置命令仍在 lead 会话中运行。

队友的模型和 fast mode 在生成时固定，`/model` 和 `/fast` 只改变 lead 设置。`/effort` 仍适用于所查看队友的后续 turn。

### 分配和认领任务

**共享任务列表协调团队工作。** 任务有三种状态：pending、in progress、completed。任务还可以依赖其他任务：有未解决依赖的 pending 任务在依赖完成前不能被认领。

- **Lead 分配**：告诉 lead 将哪个任务给哪个队友
- **自认领**：队友完成任务后自动拾取下一个未分配且未阻塞的任务

任务认领使用文件锁防止竞争条件。

### 关闭队友

按名称引用队友来优雅结束会话：

```text
Ask the researcher teammate to shut down
```

Lead 发送关闭请求。队友可批准（优雅退出）或拒绝并给出解释。

团队共享目录在会话结束时自动清理。

### 用 hooks 执行质量门禁

使用 [hooks](https://code.claude.com/docs/en/hooks) 在队友完成工作或任务创建/完成时执行规则：

| Hook | 说明 |
| --- | --- |
| [`TeammateIdle`](https://code.claude.com/docs/en/hooks#teammateidle) | 队友即将空闲时运行。退出码 2 可发送反馈让队友继续工作 |
| [`TaskCreated`](https://code.claude.com/docs/en/hooks#taskcreated) | 任务被创建时运行。退出码 2 阻止创建并发送反馈 |
| [`TaskCompleted`](https://code.claude.com/docs/en/hooks#taskcompleted) | 任务被标记完成时运行。退出码 2 阻止完成并发送反馈 |

## Agent teams 工作原理

### 如何启动

**第一个队友被生成时 agent team 形成**，主会话成为 lead。两种方式生成队友：

- **你请求队友**：给 Claude 一个适合并行工作的任务并明确要求队友
- **Claude 提议队友**：Claude 判断任务适合并行工作时可能建议生成队友。你确认后才执行

两种情况下你始终有控制权。Claude 不会未经你批准就生成队友。

### 架构

| 组件 | 角色 |
| --- | --- |
| **Team lead** | 主 Claude Code 会话，生成队友并协调工作 |
| **Teammates** | 独立的 Claude Code 实例，各自处理分配的任务 |
| **Task list** | 队友认领和完成的共享工作项列表 |
| **Mailbox** | agent 间通信的消息系统 |

系统自动管理任务依赖。队友完成其他任务依赖的任务时，被阻塞的任务无需手动干预即解除阻塞。

团队和任务存储在基于会话 ID 的名称下（`session-` 加会话 ID 前八字符）：

- **团队配置**：`~/.claude/teams/{team-name}/config.json`
- **任务列表**：`~/.claude/tasks/{team-name}/`

团队配置目录在会话结束时移除。任务列表目录持久保留（不上传），恢复的会话保留其任务。保留期受 [`cleanupPeriodDays`](https://code.claude.com/docs/en/settings#available-settings) 控制。

### 使用 subagent 定义作为队友

生成队友时可引用任何[范围](https://code.claude.com/docs/en/sub-agents#choose-the-subagent-scope)的 [subagent](https://code.claude.com/docs/en/sub-agents) 类型。一次定义角色（如 security-reviewer 或 test-runner），既可作为委派的 subagent 又可作为 agent team 队友复用。

```text
Spawn a teammate using the security-reviewer agent type to audit the auth module.
```

**队友遵循定义的 `tools` 白名单和 `model`**，定义内容作为附加指令追加到队友系统提示。团队协调工具（`SendMessage` 和任务管理工具）始终可用，即使 `tools` 限制了其他工具。

> `skills` 和 `mcpServers` 前置字段在定义作为队友运行时不适用。队友从项目和用户设置加载 skills 和 MCP servers。

### 权限

**队友继承 lead 的权限设置。** 如果 lead 用 `--dangerously-skip-permissions` 运行，所有队友也如此。生成后可更改单个队友模式，但不能在生成时设定。

通过 `SendMessage` 发送消息时，接收 agent 被告知消息来自另一个 Claude 会话而非你。队友不能代你批准权限提示或提供同意。在 [auto mode](https://code.claude.com/docs/en/permission-modes#eliminate-prompts-with-auto-mode) 下，分类器将另一个 agent 转发的批准声明视为不信任输入。队友权限提示冒泡到 lead 会话，在那里自己批准。

### 上下文和通信

**每个队友有自己的上下文窗口。** 生成时加载与普通会话相同的项目上下文：CLAUDE.md、MCP servers 和 skills，加上 lead 的生成提示。lead 的对话历史不会传递。

队友共享信息的方式：

- **自动消息传递**：消息自动传递给接收者。Lead 无需轮询更新
- **空闲通知**：队友完成并停止时自动通知 lead。v2.1.198 起，因 API 错误结束 turn 的队友会通知 lead 失败原因
- **共享任务列表**：所有 agent 可见任务状态并认领可用工作
- **队友消息**：按名称向特定队友发消息。要通知所有人，逐个发送

Lead 在生成时为每个队友分配名称。要获得可预测的名称，在生成指令中告诉 lead 叫每个队友什么。

### Token 使用

**Agent teams 比单会话消耗显著更多 token。** 每个队友有自己的上下文窗口，token 用量随活跃队友数线性增长。研究、评审和新功能工作中额外 token 通常物有所值。常规任务中单会话更具成本效益。参见 [agent team token costs](https://code.claude.com/docs/en/costs#agent-team-token-costs)。

## 使用场景示例

### 并行代码审查

```text
Spawn three teammates to review PR #142:
- One focused on security implications
- One checking performance impact
- One validating test coverage
Have them each review and report findings.
```

各审查者从同一 PR 出发但应用不同视角。Lead 在所有人完成后综合发现。

### 竞争假设调查

```text
Users report the app exits after one message instead of staying connected.
Spawn 5 agent teammates to investigate different hypotheses. Have them talk to
each other to try to disprove each other's theories, like a scientific
debate. Update the findings doc with whatever consensus emerges.
```

**辩论结构是关键机制。** 顺序调查受锚定效应影响。多个独立调查者积极尝试推翻彼此，存活下来的理论更可能是真正的根因。

## 最佳实践

### 给队友足够上下文

队友自动加载项目上下文但不继承 lead 对话历史。在生成提示中包含任务特定细节：

```text
Spawn a security reviewer teammate with the prompt: "Review the authentication module
at src/auth/ for security vulnerabilities. Focus on token handling, session
management, and input validation. The app uses JWT tokens stored in
httpOnly cookies. Report any issues with severity ratings."
```

### 选择合适的团队规模

无硬限制，但实际约束存在：

- **Token 成本线性增长**：每个队友独立消耗 token
- **协调开销增加**：更多队友意味着更多通信和潜在冲突
- **收益递减**：超过一定数量后，额外队友不能成比例加速

**大多数工作流从 3-5 个队友开始。** 每队友 5-6 个任务保持高效。15 个独立任务，3 个队友是好的起点。

### 适当分解任务

- **太小**：协调开销超过收益
- **太大**：队友工作太久不检入，浪费风险增加
- **适中**：自包含单元，产出清晰交付物（函数、测试文件、评审）

> Lead 自动将工作分解为任务。如果任务不够，要求 lead 拆分成更小的块。

### 等待队友完成

如果 lead 开始自己实施任务而非等待队友：

```text
Wait for your teammates to complete their tasks before proceeding
```

### 从研究和评审开始

新手建议从有清晰边界且不需写代码的任务开始：审查 PR、研究库、调查 bug。

### 避免文件冲突

两个队友编辑同一文件会导致覆盖。分解工作使每个队友拥有不同文件集。

### 监控和引导

检查队友进度，重定向无效的方法，及时综合发现。

## 故障排除

### 队友不出现

- In-process 模式下，队友在提示输入下方的 agent 面板中。用上下箭头选择后按 Enter 查看
- 消失的队友行是被隐藏而非停止。全面板空闲 30 秒后隐藏，下次 turn 重现
- 检查任务是否足够复杂以保证团队
- 明确请求 split panes 时确保 tmux 已安装：`which tmux`
- iTerm2 需验证 `it2` CLI 已安装且 Python API 已启用

### 权限提示过多

队友权限请求冒泡到 lead。在[权限设置](https://code.claude.com/docs/en/permissions)中预批准常见操作以减少中断。

### 队友遇错停止

选中队友按 Enter 查看输出，然后给予额外指令或生成替代队友继续工作。

v2.1.198 起，来自 lead 或另一队友的消息会唤醒正在等待重试的 in-process 队友。

### Lead 提前关闭

如果 lead 在所有任务实际完成前判断团队已完成，告诉它继续。也可告诉 lead 等待队友完成再继续。

### 残留 tmux 会话

```bash
tmux ls
tmux kill-session -t <session-name>
```

## 限制

Agent teams 是实验性功能，当前限制：

- **无 in-process 队友会话恢复**：`/resume` 和 `/rewind` 不恢复 in-process 队友
- **任务状态可能滞后**：队友有时忘记标记完成
- **关闭可能慢**：队友在当前请求或工具调用完成前不会关闭
- **每会话一个团队**：不能创建额外命名团队或跨会话共享
- **无嵌套团队**：队友不能生成自己的队友
- **In-process 队友无后台 subagent**：队友的 subagent 在前台运行
- **Lead 固定**：主会话终身为 lead，不能提升队友或转移领导权
- **权限在生成时设定**：所有队友继承 lead 模式，生成后可改但不能生成时设定
- **Split panes 需 tmux 或 iTerm2**：不支持 VS Code 内置终端、Windows Terminal 或 Ghostty

> **`CLAUDE.md` 正常工作**：队友从工作目录读取 `CLAUDE.md` 文件，为所有队友提供项目级指导。

## 下一步

- **轻量委派**：[subagent](https://code.claude.com/docs/en/sub-agents) 在会话内生成助手 agent，适合不需 agent 间协调的任务
- **手动并行会话**：[Git worktrees](https://code.claude.com/docs/en/worktrees) 自己运行多个 Claude Code 会话
- **对比方案**：参见 [subagent vs agent team](https://code.claude.com/docs/en/features-overview#compare-similar-features) 对比
