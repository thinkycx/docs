---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】无头模式
description: 介绍如何通过 Agent SDK 以编程方式运行 Claude Code，包括 CLI 非交互模式、管道数据、结构化输出、流式响应、工具自动授权等常见用法。
category: translation
tags: [claude-code, headless, automation, translation]
refs: [https://code.claude.com/docs/en/headless.md]
---

# 以编程方式运行 Claude Code

> **通过 Agent SDK，你可以在 CLI、Python 或 TypeScript 中以编程方式调用 Claude Code。**

[Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) 提供了与 Claude Code 相同的工具、Agent 循环和上下文管理能力。你可以通过 CLI 在脚本和 CI/CD 中使用它，也可以通过 [Python](https://code.claude.com/docs/en/agent-sdk/python) 和 [TypeScript](https://code.claude.com/docs/en/agent-sdk/typescript) 包获得完整的编程控制。

**在非交互模式下运行 Claude Code，只需传入 `-p` 加上你的 Prompt，再搭配任意 [CLI 选项](https://code.claude.com/docs/en/cli-reference)：**

```bash
claude -p "Find and fix the bug in auth.py" --allowedTools "Read,Edit,Bash"
```

本文介绍如何通过 CLI（`claude -p`）使用 Agent SDK。如果你需要结构化输出、工具审批回调和原生消息对象，请参阅完整的 [Agent SDK 文档](https://code.claude.com/docs/en/agent-sdk/overview)。

## 基本用法

**添加 `-p`（或 `--print`）标志即可以非交互模式运行任何 `claude` 命令。** 所有 [CLI 选项](https://code.claude.com/docs/en/cli-reference) 都支持与 `-p` 配合使用，包括：

- `--continue` 用于[继续对话](#继续对话)
- `--allowedTools` 用于[自动授权工具](#自动授权工具)
- `--output-format` 用于[获取结构化输出](#获取结构化输出)

下面这个例子会让 Claude 回答关于代码库的问题并打印结果：

```bash
claude -p "What does the auth module do?"
```

### 使用 bare 模式加速启动

**添加 `--bare` 可跳过钩子、技能、插件、MCP 服务器、自动记忆和 CLAUDE.md 的自动加载，从而缩短启动时间。** 不加 `--bare` 时，`claude -p` 会加载与交互式会话相同的[上下文](https://code.claude.com/docs/en/how-claude-code-works#the-context-window)，包括工作目录或 `~/.claude` 中配置的所有内容。

bare 模式适用于 CI 和脚本场景——保证每台机器上得到相同的结果。同时 `~/.claude` 里的钩子或项目 `.mcp.json` 中的 MCP 服务器都不会执行，因为 bare 模式不会读取它们。只有你显式传入的标志才会生效。

下面这个例子在 bare 模式下运行一次性摘要任务，并预授权 Read 工具以避免权限提示：

```bash
claude --bare -p "Summarize this file" --allowedTools "Read"
```

**在 bare 模式下，Claude 默认可以使用 Bash、文件读取和文件编辑工具。** 如果需要加载额外的上下文，使用以下标志：

| 需要加载的内容 | 使用的标志 |
|---|---|
| 系统 Prompt 追加内容 | `--append-system-prompt`、`--append-system-prompt-file` |
| 配置 | `--settings <file-or-json>` |
| MCP 服务器 | `--mcp-config <file-or-json>` |
| 自定义 Agent | `--agents <json>` |
| 插件 | `--plugin-dir <path>`、`--plugin-url <url>` |

bare 模式会跳过 OAuth 和钥匙串读取。Anthropic 认证必须通过 `ANTHROPIC_API_KEY` 或 `--settings` JSON 中的 `apiKeyHelper` 提供。Bedrock、Vertex 和 Foundry 使用各自的 provider 凭证。

> **提示：** `--bare` 是脚本和 SDK 调用的推荐模式，未来版本中将成为 `-p` 的默认行为。

### 退出时的后台任务处理

**如果 Claude 在 `claude -p` 运行期间启动了[后台 Bash 任务](https://code.claude.com/docs/en/tools-reference#bash-tool-behavior)（例如开发服务器或 watch 构建），该 shell 会在 Claude 返回最终结果且 stdin 关闭后约五秒钟被终止。** 这个宽限期允许刚好在结果之后完成的任务仍然能输出内容。在 v2.1.163 之前，一个永不退出的后台进程会无限期挂起 `claude -p` 调用。

后台[子 Agent](https://code.claude.com/docs/en/sub-agents) 和工作流不受五秒宽限期限制，因为它们的结果属于最终输出的一部分，所以 `claude -p` 会等待它们完成。从 v2.1.182 起，等待时间默认上限为十分钟，以防止卡住的后台 Agent 无限期占用进程。可以通过 [`CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS`](https://code.claude.com/docs/en/env-vars) 调整上限，设为 `0` 则无限等待。

## 使用示例

**以下示例展示了常见的 CLI 模式。** 在 CI 和其他脚本调用中，建议添加 [`--bare`](#使用-bare-模式加速启动) 以避免加载本地配置。

### 通过管道传输数据

**非交互模式会读取 stdin，你可以像使用其他命令行工具一样通过管道输入数据并重定向输出。**

下面这个例子将构建错误日志管道传入 Claude，并将解释写入文件：

```bash
cat build-error.txt | claude -p 'concisely explain the root cause of this build error' > output.txt
```

使用 `--output-format json` 时，响应负载中包含 `total_cost_usd` 和按模型拆分的费用，脚本调用方可以按次追踪开支而无需查看[用量面板](https://code.claude.com/docs/en/costs)。

> **注意：** 从 Claude Code v2.1.128 起，管道输入的 stdin 上限为 10MB。超出上限时，Claude Code 会输出明确的错误信息并以非零状态退出。如需处理更大的输入，请将内容写入文件并在 Prompt 中引用文件路径。

### 在构建脚本中使用 Claude

**你可以在脚本中封装非交互调用，将 Claude 用作项目级的 linter 或 reviewer。**

下面这个 `package.json` 脚本将与 `main` 分支的 diff 管道传入 Claude，要求报告拼写错误。由于 diff 通过管道传入，Claude 不需要 Bash 权限来读取它；转义的双引号保证了在 Windows 上的兼容性：

```json
{
  "scripts": {
    "lint:claude": "git diff main | claude -p \"you are a typo linter. for each typo in this diff, report filename:line on one line and the issue on the next. return nothing else.\""
  }
}
```

### 获取结构化输出

**使用 `--output-format` 控制响应的返回格式：**

- `text`（默认）：纯文本输出
- `json`：包含结果、会话 ID 和元数据的结构化 JSON
- `stream-json`：以换行符分隔的 JSON，用于实时流式传输

下面这个例子以 JSON 格式返回项目摘要及会话元数据，文本结果在 `result` 字段中：

```bash
claude -p "Summarize this project" --output-format json
```

**如果需要符合特定 schema 的输出，** 使用 `--output-format json` 搭配 `--json-schema` 和一个 [JSON Schema](https://json-schema.org/) 定义。响应中包含请求的元数据（会话 ID、用量等），结构化输出位于 `structured_output` 字段。

下面这个例子提取函数名并以字符串数组形式返回：

```bash
claude -p "Extract the main function names from auth.py" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"functions":{"type":"array","items":{"type":"string"}}},"required":["functions"]}'
```

> **技巧：** 使用 [jq](https://jqlang.github.io/jq/) 解析响应并提取特定字段：
>
> ```bash
> # 提取文本结果
> claude -p "Summarize this project" --output-format json | jq -r '.result'
>
> # 提取结构化输出
> claude -p "Extract function names from auth.py" \
>   --output-format json \
>   --json-schema '{"type":"object","properties":{"functions":{"type":"array","items":{"type":"string"}}},"required":["functions"]}' \
>   | jq '.structured_output'
> ```

### 流式响应

**使用 `--output-format stream-json` 搭配 `--verbose` 和 `--include-partial-messages` 可以逐 token 接收生成内容。** 每一行是一个代表事件的 JSON 对象：

```bash
claude -p "Explain recursion" --output-format stream-json --verbose --include-partial-messages
```

下面这个例子使用 [jq](https://jqlang.github.io/jq/) 过滤文本增量并只显示流式文本。`-r` 标志输出原始字符串（无引号），`-j` 无换行拼接以实现连续流式输出：

```bash
claude -p "Write a poem" --output-format stream-json --verbose --include-partial-messages | \
  jq -rj 'select(.type == "stream_event" and .event.delta.type? == "text_delta") | .event.delta.text'
```

**当 API 请求因可重试错误失败时，Claude Code 会在重试前发出 `system/api_retry` 事件。** 你可以用它来展示重试进度或实现自定义退避逻辑。

| 字段 | 类型 | 说明 |
|---|---|---|
| `type` | `"system"` | 消息类型 |
| `subtype` | `"api_retry"` | 标识这是一个重试事件 |
| `attempt` | integer | 当前尝试次数，从 1 开始 |
| `max_retries` | integer | 允许的最大重试次数 |
| `retry_delay_ms` | integer | 距离下次尝试的毫秒数 |
| `error_status` | integer 或 null | HTTP 状态码；连接错误无 HTTP 响应时为 `null` |
| `error` | string | 错误分类：`authentication_failed`、`oauth_org_not_allowed`、`billing_error`、`rate_limit`、`overloaded`、`invalid_request`、`model_not_found`、`server_error`、`max_output_tokens` 或 `unknown` |
| `uuid` | string | 唯一事件标识符 |
| `session_id` | string | 事件所属的会话 |

**`system/init` 事件报告会话元数据，** 包括模型、工具、MCP 服务器和已加载的插件。它是流中的第一个事件，除非设置了 [`CLAUDE_CODE_SYNC_PLUGIN_INSTALL`](https://code.claude.com/docs/en/env-vars)（此时 `plugin_install` 事件在它之前）。使用 plugin 字段可以在 CI 中检测插件是否加载失败：

| 字段 | 类型 | 说明 |
|---|---|---|
| `plugins` | array | 成功加载的插件，每个包含 `name` 和 `path` |
| `plugin_errors` | array | 插件加载时的错误，每个包含 `plugin`、`type` 和 `message`。包括未满足的依赖版本和 `--plugin-dir` 加载失败（如路径不存在或归档无效）。受影响的插件被降级且不在 `plugins` 中。无错误时省略该字段 |

**设置 [`CLAUDE_CODE_SYNC_PLUGIN_INSTALL`](https://code.claude.com/docs/en/env-vars) 后，** Claude Code 会在首轮之前安装 marketplace 插件时发出 `system/plugin_install` 事件。用这些事件在你的 UI 中展示安装进度。

| 字段 | 类型 | 说明 |
|---|---|---|
| `type` | `"system"` | 消息类型 |
| `subtype` | `"plugin_install"` | 标识这是一个插件安装事件 |
| `status` | `"started"`、`"installed"`、`"failed"` 或 `"completed"` | `started` 和 `completed` 包裹整个安装过程；`installed` 和 `failed` 报告各个 marketplace 的结果 |
| `name` | string（可选） | marketplace 名称，出现在 `installed` 和 `failed` 状态中 |
| `error` | string（可选） | 失败信息，出现在 `failed` 状态中 |
| `uuid` | string | 唯一事件标识符 |
| `session_id` | string | 事件所属的会话 |

如需通过回调和消息对象进行编程式流处理，请参阅 Agent SDK 文档中的[实时流式响应](https://code.claude.com/docs/en/agent-sdk/streaming-output)。

### 自动授权工具

**使用 `--allowedTools` 让 Claude 无需确认即可使用特定工具。** 下面这个例子运行测试套件并修复失败用例，允许 Claude 执行 Bash 命令、读取和编辑文件而无需请求权限：

```bash
claude -p "Run the test suite and fix any failures" \
  --allowedTools "Bash,Read,Edit"
```

**如果想为整个会话设置基线权限而不是逐个列出工具，** 可以传入[权限模式](https://code.claude.com/docs/en/permission-modes)。`dontAsk` 会拒绝不在 `permissions.allow` 规则或[只读命令集](https://code.claude.com/docs/en/permissions#read-only-commands)中的所有操作，适合锁定的 CI 环境。`acceptEdits` 允许 Claude 无需确认即可写入文件，同时自动批准常见的文件系统命令如 `mkdir`、`touch`、`mv` 和 `cp`。其他 shell 命令和网络请求仍需要 `--allowedTools` 条目或 `permissions.allow` 规则，否则运行时会中止：

```bash
claude -p "Apply the lint fixes" --permission-mode acceptEdits
```

### 创建提交

**下面这个例子审查暂存的变更并创建一个带有合适信息的提交：**

```bash
claude -p "Look at my staged changes and create an appropriate commit" \
  --allowedTools "Bash(git diff *),Bash(git log *),Bash(git status *),Bash(git commit *)"
```

`--allowedTools` 标志使用[权限规则语法](https://code.claude.com/docs/en/settings#permission-rule-syntax)。末尾的 ` *` 启用前缀匹配，所以 `Bash(git diff *)` 允许任何以 `git diff` 开头的命令。`*` 前面的空格很重要：没有它，`Bash(git diff*)` 还会匹配 `git diff-index`。

> **注意：** 用户调用的[技能](https://code.claude.com/docs/en/skills)和自定义命令在 `-p` 模式下可用：在 Prompt 字符串中包含 `/skill-name`，Claude Code 会在运行前展开它。打开交互对话框的内置命令（如 `/login`）在 `-p` 模式下不可用。要在 `-p` 调用中更改设置，向 `/config` 传入 `key=value`，例如 `/config thinking=false`。

### 自定义系统 Prompt

**使用 `--append-system-prompt` 在保留 Claude Code 默认行为的同时添加指令。** 下面这个例子将 PR diff 管道传入 Claude，并指示它以安全工程师的身份审查漏洞：

```bash
gh pr diff "$1" | claude -p \
  --append-system-prompt "You are a security engineer. Review for vulnerabilities." \
  --output-format json
```

更多选项请参阅[系统 Prompt 标志](https://code.claude.com/docs/en/cli-reference#system-prompt-flags)，包括 `--system-prompt` 完全替换默认 Prompt。

### 继续对话

**使用 `--continue` 继续最近的对话，或使用 `--resume` 加会话 ID 继续特定对话。** 下面这个例子先运行一次审查，然后发送后续 Prompt：

```bash
# 第一次请求
claude -p "Review this codebase for performance issues"

# 继续最近的对话
claude -p "Now focus on the database queries" --continue
claude -p "Generate a summary of all issues found" --continue
```

如果你在并行运行多个对话，捕获会话 ID 以恢复特定对话：

```bash
session_id=$(claude -p "Start a review" --output-format json | jq -r '.session_id')
claude -p "Continue that review" --resume "$session_id"
```

两个命令需要在同一目录下运行：会话 ID 查找的作用域限定在当前项目目录及其 git worktree 中。完整的作用域规则请参阅[恢复会话](https://code.claude.com/docs/en/sessions#resume-a-session)。

## 后续阅读

- [Agent SDK 快速入门](https://code.claude.com/docs/en/agent-sdk/quickstart)：用 Python 或 TypeScript 构建你的第一个 Agent
- [CLI 参考](https://code.claude.com/docs/en/cli-reference)：所有 CLI 标志和选项
- [GitHub Actions](https://code.claude.com/docs/en/github-actions)：在 GitHub 工作流中使用 Agent SDK
- [GitLab CI/CD](https://code.claude.com/docs/en/gitlab-ci-cd)：在 GitLab 管道中使用 Agent SDK
