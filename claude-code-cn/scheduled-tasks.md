---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】定时任务
description: Claude Code 的定时任务机制，包括 /loop 轮询、一次性提醒和 cron 调度工具，用于在会话中自动执行重复性检查或提醒。
category: translation
tags: [claude-code, scheduled-tasks, translation]
refs: [https://code.claude.com/docs/en/scheduled-tasks.md]
---

# 按计划运行提示词

> **核心能力：** 使用 /loop 和 cron 调度工具，在 Claude Code 会话中按间隔重复执行提示词、轮询状态或设置一次性提醒。

> [!NOTE]
> 定时任务需要 Claude Code v2.1.72 或更高版本。通过 `claude --version` 检查当前版本。

**定时任务让 Claude 按间隔自动重复执行提示词。** 适用于轮询部署状态、看护 PR、检查长时间运行的构建结果，或在会话中给自己设置提醒。如果想在事件发生时即时响应而非轮询，参见 [Channels](https://code.claude.com/docs/en/channels)：你的 CI 可以直接把失败推送到会话中。如果想让会话持续执行直到某个条件满足（而非按间隔执行），参见 [`/goal`](https://code.claude.com/docs/en/goal)。

**任务的作用域是会话级别的：** 它们存活于当前对话中，开启新对话后就会停止。通过 `--resume` 或 `--continue` 恢复会话时，未[过期](#七天自动过期)的任务会被带回：7 天内创建的循环任务，或者尚未到达触发时间的一次性任务。如果需要独立于任何会话的持久调度，可以使用 [Routines](https://code.claude.com/docs/en/routines) 在 Anthropic 托管基础设施上创建例程、设置[桌面定时任务](https://code.claude.com/docs/en/desktop-scheduled-tasks)，或使用 [GitHub Actions](https://code.claude.com/docs/en/github-actions)。

## 调度方案对比

Claude Code 提供三种方式来调度循环或一次性任务：

|                    | [云端 (Routines)](https://code.claude.com/docs/en/routines) | [桌面定时任务](https://code.claude.com/docs/en/desktop-scheduled-tasks) | [`/loop`](https://code.claude.com/docs/en/scheduled-tasks) |
| :----------------- | :---------------------------------------------------------- | :---------------------------------------------------------------------- | :--------------------------------------------------------- |
| 运行位置           | Anthropic 云端                                               | 你的机器                                                                | 你的机器                                                   |
| 是否需要机器开启   | 否                                                           | 是                                                                      | 是                                                         |
| 是否需要打开会话   | 否                                                           | 否                                                                      | 是                                                         |
| 重启后是否保留     | 是                                                           | 是                                                                      | 通过 `--resume` 恢复（未过期时）                           |
| 访问本地文件       | 否（使用全新 clone）                                         | 是                                                                      | 是                                                         |
| MCP 服务器         | 按任务配置 Connectors                                        | [配置文件](https://code.claude.com/docs/en/mcp) 和 Connectors           | 继承会话配置                                               |
| 权限提示           | 无（自主运行）                                               | 按任务可配置                                                            | 继承会话配置                                               |
| 自定义调度         | 通过 CLI 中的 `/schedule`                                    | 是                                                                      | 是                                                         |
| 最小间隔           | 1 小时                                                       | 1 分钟                                                                  | 1 分钟                                                     |

> [!TIP]
> **云端任务**适合不依赖本机、需要可靠运行的工作。**桌面任务**适合需要访问本地文件和工具的场景。**`/loop`**适合会话期间的快速轮询。

## 使用 /loop 重复运行提示词

**`/loop` 是会话期间最快的重复执行方式。** 它是一个[内置 skill](https://code.claude.com/docs/en/commands)，间隔和提示词都是可选的，你提供的内容决定了循环的行为方式。

| 你提供的内容     | 示例                         | 行为                                                                        |
| :--------------- | :--------------------------- | :-------------------------------------------------------------------------- |
| 间隔 + 提示词    | `/loop 5m check the deploy`  | 按[固定间隔](#按固定间隔运行)运行你的提示词                                 |
| 仅提示词         | `/loop check the deploy`     | 按 [Claude 自动选择的间隔](#让-claude-选择间隔)运行你的提示词               |
| 仅间隔或什么都不写 | `/loop`                    | 运行[内置维护提示词](#运行内置维护提示词)，或你自定义的 `loop.md`（如果存在） |

你也可以把另一个命令作为提示词传入，例如 `/loop 20m /review-pr 1234`，每次迭代运行一个已保存的 skill 或命令。

### 按固定间隔运行

**指定间隔后，Claude 会将其转换为 cron 表达式并确认。** 它会调度任务并返回执行频率和任务 ID。

```text
/loop 5m check if the deployment finished and tell me what happened
```

间隔可以作为裸标记放在提示词前面（如 `30m`），也可以作为子句跟在后面（如 `every 2 hours`）。支持的单位有：`s`（秒）、`m`（分钟）、`h`（小时）、`d`（天）。

秒会被向上取整到最近的分钟，因为 cron 的最小粒度是一分钟。无法整除的间隔（如 `7m` 或 `90m`）会被四舍五入到最近的可用间隔，Claude 会告诉你最终选取的值。

### 让 Claude 选择间隔

**省略间隔时，Claude 会动态决定等待时长。** 每次迭代结束后，它会根据观察到的情况选择 1 分钟到 1 小时之间的延迟：构建即将完成或 PR 活跃时等待短一些，没有待处理事项时等待长一些。每次迭代结束时会打印选择的延迟及原因。

下面的例子检查 CI 和 review 评论，PR 安静后 Claude 会自动拉长间隔：

```text
/loop check whether CI passed and address any review comments
```

当你请求动态 `/loop` 调度时，Claude 可能会直接使用 [Monitor 工具](https://code.claude.com/docs/en/tools-reference#monitor-tool)。Monitor 在后台运行脚本并流式返回每行输出，避免了轮询，通常比按间隔重新运行提示词更省 token 且响应更快。

动态调度的循环在你的[定时任务列表](#管理定时任务)中和其他任务一样可见，可以用相同方式列出或取消。[抖动规则](#抖动)不适用于它，但[七天过期规则](#七天自动过期)适用：循环会在启动 7 天后自动结束。

> [!NOTE]
> 在 Bedrock、Vertex AI 和 Microsoft Foundry 上，不带间隔的提示词会按固定 10 分钟间隔运行。

### 运行内置维护提示词

**省略提示词时，Claude 会使用内置维护提示词。** 每次迭代中它按顺序处理以下事项：

* 继续对话中未完成的工作
* 维护当前分支的 PR：review 评论、失败的 CI、合并冲突
* 在没有其他待处理事项时执行清理，例如 bug 排查或代码简化

Claude 不会在上述范围之外发起新操作，推送或删除等不可逆操作只有在对话记录已授权的情况下才会继续执行。

```text
/loop
```

裸 `/loop` 按[动态间隔](#让-claude-选择间隔)运行此提示词。加上间隔（如 `/loop 15m`）则按固定间隔运行。要用你自己的默认提示词替换内置的，参见[用 loop.md 自定义默认提示词](#用-loopmd-自定义默认提示词)。

> [!NOTE]
> 在 Bedrock、Vertex AI 和 Microsoft Foundry 上，不带提示词的 `/loop` 会打印使用说明而非运行维护提示词。

### 用 loop.md 自定义默认提示词

**`loop.md` 文件用你自己的指令替换内置维护提示词。** 它定义的是裸 `/loop` 的单一默认提示词，而非多个独立的定时任务；当你在命令行提供了提示词时会被忽略。要在它之外调度更多提示词，使用 `/loop <prompt>` 或[直接让 Claude 操作](#管理定时任务)。

Claude 在两个位置查找文件，使用先找到的那个。

| 路径                | 作用范围                                         |
| :------------------ | :----------------------------------------------- |
| `.claude/loop.md`   | 项目级。两个文件都存在时优先使用。               |
| `~/.claude/loop.md` | 用户级。在没有项目级文件的项目中生效。           |

文件是纯 Markdown，没有格式要求。像直接输入 `/loop` 提示词一样编写即可。下面的例子用来维护一个发布分支：

```markdown
# .claude/loop.md
Check the `release/next` PR. If CI is red, pull the failing job log,
diagnose, and push a minimal fix. If new review comments have arrived,
address each one and resolve the thread. If everything is green and
quiet, say so in one line.
```

编辑 `loop.md` 会在下次迭代生效，所以你可以在循环运行时调整指令。如果两个位置都没有 `loop.md`，则回退到内置维护提示词。文件内容请保持简洁：超过 25,000 字节会被截断。

> [!NOTE]
> 在 Bedrock、Vertex AI 和 Microsoft Foundry 上，`loop.md` 不会被读取，不带提示词的 `/loop` 会打印使用说明。

### 停止循环

**按 `Esc` 即可在循环等待下次迭代时停止它。** 这会清除挂起的唤醒计划，循环不再触发。通过[直接请求 Claude](#管理定时任务) 调度的任务不受 `Esc` 影响，它们会一直存在直到你删除。

在[自适应模式](#让-claude-选择间隔)下，Claude 在任务确定完成后也可以自行结束循环，不再调度下次唤醒。固定间隔的循环会持续运行，直到你停止或[七天到期](#七天自动过期)。

## 设置一次性提醒

**用自然语言描述即可设置一次性提醒。** Claude 会调度一个单次触发的任务，运行后自动删除。

```text
remind me at 3pm to push the release branch
```

```text
in 45 minutes, check whether the integration tests passed
```

Claude 会用 cron 表达式将触发时间锁定到具体的分钟和小时，并确认触发时间。

## 管理定时任务

**用自然语言让 Claude 列出或取消任务，** 也可以直接引用底层工具。

```text
what scheduled tasks do I have?
```

```text
cancel the deploy check job
```

底层使用的工具：

| 工具         | 用途                                                                                     |
| :----------- | :--------------------------------------------------------------------------------------- |
| `CronCreate` | 调度新任务。接受 5 字段 cron 表达式、要运行的提示词，以及是循环还是单次触发。            |
| `CronList`   | 列出所有定时任务及其 ID、调度计划和提示词。                                              |
| `CronDelete` | 通过 ID 取消任务。                                                                       |

每个定时任务有一个 8 字符的 ID，可以传给 `CronDelete`。单个会话最多可容纳 50 个定时任务。

## 定时任务的运行机制

**调度器每秒检查一次到期任务，以低优先级入队执行。** 定时提示词在你的回合之间触发，而不是在 Claude 正在响应时。如果任务到期时 Claude 正忙，提示词会等待当前回合结束后才执行。

所有时间按你的本地时区解释。像 `0 9 * * *` 这样的 cron 表达式表示你运行 Claude Code 的地方的早上 9 点，而不是 UTC。

### 抖动

**为避免所有会话在同一时刻请求 API，调度器会给触发时间加上确定性偏移：**

* 循环任务在调度时间后最多 30 分钟内触发（对于频率高于每小时一次的任务，最多延迟间隔的一半）。例如，整点调度的每小时任务可能在 `:00` 到 `:30` 之间任意时刻触发。
* 调度在整点或半点的一次性任务可能提前最多 90 秒触发。

偏移量由任务 ID 推导，因此同一任务的偏移始终相同。如果精确时间很重要，选择一个不是 `:00` 或 `:30` 的分钟（例如用 `3 9 * * *` 而非 `0 9 * * *`），一次性任务的抖动就不会生效。

### 七天自动过期

**循环任务在创建 7 天后自动过期。** 任务会最后触发一次，然后自行删除。这限制了被遗忘的循环能运行多长时间。如果需要循环任务持续更久，在过期前取消并重新创建，或使用 [Routines](https://code.claude.com/docs/en/routines) 或[桌面定时任务](https://code.claude.com/docs/en/desktop-scheduled-tasks)实现持久调度。

## Cron 表达式参考

`CronCreate` 接受标准的 5 字段 cron 表达式：`minute hour day-of-month month day-of-week`。所有字段支持通配符（`*`）、单值（`5`）、步进（`*/15`）、范围（`1-5`）和逗号分隔列表（`1,15,30`）。

| 示例           | 含义                 |
| :------------- | :------------------- |
| `*/5 * * * *`  | 每 5 分钟            |
| `0 * * * *`    | 每小时整点           |
| `7 * * * *`    | 每小时第 7 分钟      |
| `0 9 * * *`    | 每天早上 9 点        |
| `0 9 * * 1-5`  | 工作日早上 9 点      |
| `30 14 15 3 *` | 3 月 15 日下午 2:30  |

day-of-week 用 `0` 或 `7` 表示周日，`6` 表示周六。不支持 `L`、`W`、`?` 等扩展语法，也不支持 `MON` 或 `JAN` 等名称别名。

当 day-of-month 和 day-of-week 同时受限时，日期只要匹配其中一个字段即满足条件。这遵循标准 vixie-cron 语义。

## 禁用定时任务

在环境变量中设置 `CLAUDE_CODE_DISABLE_CRON=1` 可完全禁用调度器。cron 工具和 `/loop` 将不可用，已调度的任务也会停止触发。完整的禁用标志列表参见[环境变量](https://code.claude.com/docs/en/env-vars)。

## 限制

**会话级调度存在固有约束：**

* 任务仅在 Claude Code 运行且空闲时触发。关闭终端或退出会话后任务不再触发。
* 不会补执行错过的触发。如果任务的调度时间在 Claude 处理长时间请求期间过去了，空闲后只会触发一次，不会按错过的次数补执行。
* 开启全新对话会清除所有会话级任务。通过 `claude --resume` 或 `claude --continue` 恢复时，未过期的任务会被恢复：创建 7 天内的循环任务，以及触发时间尚未过去的一次性任务。后台 Bash 和 monitor 任务在恢复时不会被还原。

如果需要无人值守的 cron 驱动自动化：

* [Routines](https://code.claude.com/docs/en/routines)：在 Anthropic 托管基础设施上按计划运行、通过 API 调用触发，或响应 GitHub 事件
* [GitHub Actions](https://code.claude.com/docs/en/github-actions)：在 CI 中使用 `schedule` 触发器
* [桌面定时任务](https://code.claude.com/docs/en/desktop-scheduled-tasks)：在本地机器上运行
