---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】Goal 目标驱动
description: Claude Code 的 /goal 命令允许你设定一个完成条件，Claude 会持续工作直到条件满足。适合有明确终态的大型任务，比如迁移模块、实现设计文档、拆分大文件等场景。
category: translation
tags: [claude-code, goal, translation]
refs: [https://code.claude.com/docs/en/goal.md]
---

# 让 Claude 持续朝目标工作

> **设定完成条件，Claude 自动循环执行直到条件满足。** 用 `/goal` 设定一个完成条件，Claude 会持续跨多轮工作，无需你逐步提示。

> [!NOTE]
> `/goal` 需要 Claude Code v2.1.139 或更高版本。

**`/goal` 命令的核心机制：** 设定一个完成条件后，Claude 会持续朝着目标工作，而不需要你在每一步都手动提示。每轮结束后，一个轻量快速模型会检查条件是否已满足。如果未满足，Claude 会自动开始下一轮，而非把控制权交还给你。条件满足后，goal 自动清除。

**适用场景：** 适合有可验证终态的大型任务：

- 迁移一个模块到新 API，直到所有调用点都能编译且测试通过
- 实现一份设计文档，直到所有验收标准都满足
- 将一个大文件拆分为专注模块，直到每个模块都在体积预算内
- 逐个处理已标记的 issue 积压，直到队列清空

## 保持会话运行的三种方式对比

**三种方式各有侧重，按"什么触发下一轮"来选择。**

| 方式 | 下一轮的触发时机 | 停止条件 |
| :--- | :--- | :--- |
| `/goal` | 上一轮结束后 | 模型确认条件已满足 |
| [`/loop`](https://code.claude.com/docs/en/scheduled-tasks#run-a-prompt-repeatedly-with-%2Floop) | 时间间隔到达 | 你手动停止，或 Claude 判断工作已完成 |
| [Stop hook](https://code.claude.com/docs/en/hooks-guide#prompt-based-hooks) | 上一轮结束后 | 你自定义的脚本或 prompt 来判定 |

**`/goal` 与 Stop hook 的区别：** 两者都在每轮结束后触发。`/goal` 是会话级的快捷方式：输入一个条件，仅在当前会话生效。Stop hook 写在配置文件里，对其作用域内的所有会话生效，可以运行脚本做确定性检查，也可以用 prompt 做模型评估。

**`/goal` 与 Auto mode 的关系：** [Auto mode](https://code.claude.com/docs/en/auto-mode-config) 本身只是在单轮内自动批准工具调用，但不会开启新一轮——Claude 自己判断工作完成就停下。`/goal` 增加了一个独立的评估器，在每轮结束后检查你的条件，由一个全新的模型来判定是否完成，而非执行工作的那个模型。两者互补：Auto mode 免去逐个工具的确认，`/goal` 免去逐轮的确认。

> [!TIP]
> 上述方式都是保持当前会话运行。你也可以安排独立于任何打开会话的定时任务，比如每晚测试或每早分诊。详见 [定时任务选项](https://code.claude.com/docs/en/scheduled-tasks#compare-scheduling-options)。

## 使用 `/goal`

**每个会话同时只能有一个 goal。** 同一个命令根据参数不同，可以设定、查看和清除 goal。

### 设定 goal

**运行 `/goal` 加上你希望满足的条件。** 如果已有一个 goal 处于活跃状态，新 goal 会替换它。

```text
/goal all tests in test/auth pass and the lint step is clean
```

**设定 goal 会立即开始一轮工作，** 条件本身就是指令，不需要再单独发送 prompt。goal 活跃期间，会显示 `◎ /goal active` 指示器以及已运行时长。

**评估器在每轮结束后会返回简短的理由，** 解释条件为何满足或不满足。最近一次的理由会显示在状态视图和 transcript 中，方便你了解 Claude 接下来的工作方向。

> [!NOTE]
> goal 会持续运行直到条件满足或你执行 `/goal clear`。不带参数运行 `/goal` 可以查看已消耗的轮数和 token。

### 编写有效的条件

**评估器只能根据对话中 Claude 已经输出的内容来判断，不会自行执行命令或读取文件。** 所以条件要写成 Claude 的输出能够证明的形式。比如"test/auth 下所有测试通过"就很好，因为 Claude 会运行测试，结果会出现在 transcript 中供评估器读取。

**一个能跨多轮持续有效的条件通常具备：**

- **一个可度量的终态：** 测试结果、构建退出码、文件数量、空队列
- **一个明确的检查方式：** Claude 如何证明它——比如"`npm test` 退出码为 0"或"`git status` 是干净的"
- **重要的约束条件：** 过程中不能改变的东西，比如"不修改其他测试文件"

条件最长支持 4,000 个字符。

**限制运行时长：** 在条件中加入轮数或时间子句，比如 `or stop after 20 turns`。Claude 每轮会报告相对于该子句的进度，评估器从对话中判断。

### 查看状态

**不带参数运行 `/goal` 查看当前状态。**

```text
/goal
```

如果 goal 处于活跃状态，状态会显示：

- 条件内容
- 已运行时长
- 已评估的轮数
- 当前 token 消耗
- 评估器最近一次的理由

如果没有活跃 goal，但当前会话中有已达成的 goal，状态会显示已达成的条件及其持续时间、轮数和 token 消耗。

### 清除 goal

**运行 `/goal clear` 可以在条件满足前手动移除活跃 goal。**

```text
/goal clear
```

`stop`、`off`、`reset`、`none`、`cancel` 都是 `clear` 的别名。运行 `/clear` 开始新对话也会移除任何活跃 goal。

### 恢复带有活跃 goal 的会话

**会话结束时仍活跃的 goal 会在用 `--resume` 或 `--continue` 恢复时一并恢复。** 条件会保留，但轮数计数器、计时器和 token 消耗基线会在恢复时重置。已达成或已清除的 goal 不会被恢复。

### 非交互模式运行

**`/goal` 支持 [非交互模式](https://code.claude.com/docs/en/headless)、[桌面应用](https://code.claude.com/docs/en/desktop) 和 [Remote Control](https://code.claude.com/docs/en/remote-control)。** 用 `-p` 设定 goal 会在单次调用中运行循环直到完成：

```bash
claude -p "/goal CHANGELOG.md has an entry for every PR merged this week"
```

在非交互模式下条件满足前，用 Ctrl+C 可以中断进程。

## 评估机制

**`/goal` 本质上是一个会话级的 [基于 prompt 的 Stop hook](https://code.claude.com/docs/en/hooks#prompt-based-hooks) 的封装。** 每次 Claude 完成一轮后，条件和对话内容会被发送给你配置的[轻量快速模型](https://code.claude.com/docs/en/model-config)（默认是 Haiku）。该模型返回"是/否"判定和简短理由。"否"意味着 Claude 继续工作，理由会作为下一轮的引导。"是"则清除 goal 并在 transcript 中记录一条达成条目。

**评估器的运行环境：** 评估器运行在你会话配置的 provider 上。它不调用工具，只能判断 Claude 已经在对话中输出的内容。

> [!NOTE]
> 评估 token 按轻量快速模型计费，通常相比主轮消耗可以忽略不计。

## 前提条件

**`/goal` 仅在你已接受信任对话框的工作区中运行，** 因为评估器属于 hooks 系统的一部分。当任何配置层级设置了 [`disableAllHooks`](https://code.claude.com/docs/en/hooks#disable-or-remove-hooks) 或在托管配置中设置了 [`allowManagedHooksOnly`](https://code.claude.com/docs/en/settings#hook-configuration) 时，`/goal` 不可用。遇到这些情况，命令会告诉你原因，而非静默无动作。

## 相关文档

- [用 `/loop` 重复运行 prompt](https://code.claude.com/docs/en/scheduled-tasks#run-a-prompt-repeatedly-with-%2Floop)：按时间间隔重复运行，而非直到条件满足
- [基于 prompt 的 hooks](https://code.claude.com/docs/en/hooks-guide#prompt-based-hooks)：当你需要自定义评估逻辑时编写自己的 Stop hook
- [Auto mode](https://code.claude.com/docs/en/auto-mode-config)：自动批准工具调用，让每轮 goal 无人值守运行
- [定时任务对比](https://code.claude.com/docs/en/scheduled-tasks#compare-scheduling-options)：独立于任何打开会话的定时任务
