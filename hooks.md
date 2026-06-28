---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】Hooks 参考
description: Claude Code Hooks 的完整参考文档，涵盖生命周期、配置格式、输入输出协议、所有事件类型（20+）的详细规格、Prompt/Agent 钩子、后台执行和安全注意事项。
category: translation
tags: [claude-code, hooks, reference, translation]
refs:
  - https://code.claude.com/docs/en/hooks.md
---

# Hooks 参考文档

> Claude Code Hook 事件、配置 schema、JSON 输入/输出格式、退出码、异步 Hook、HTTP Hook、Prompt Hook 和 MCP 工具 Hook 的完整参考。

<Tip>
  如果你需要快速上手指南和示例，请参阅 [使用 Hooks 实现自动化操作](https://code.claude.com/docs/en/hooks-guide)。
</Tip>

**Hooks 是用户自定义的 shell 命令、HTTP 端点或 LLM 提示词，在 Claude Code 生命周期的特定节点自动执行。** 本文档是事件 schema、配置选项、JSON 输入/输出格式以及异步 Hook、HTTP Hook、MCP 工具 Hook 等高级功能的完整参考。如果你是第一次配置 Hooks，建议先阅读 [指南](https://code.claude.com/docs/en/hooks-guide)。

## Hook 生命周期

**Hooks 在 Claude Code 会话的特定节点触发。** 当某个事件触发且 matcher 匹配成功时，Claude Code 会将事件的 JSON 上下文传递给你的 Hook 处理器。对于命令 Hook，输入通过 stdin 传入；对于 HTTP Hook，输入作为 POST 请求体传入。你的处理器可以检查输入、执行操作，并可选地返回一个决策。

事件分为三种频率：每会话一次（`SessionStart`、`SessionEnd`）、每轮一次（`UserPromptSubmit`、`Stop`、`StopFailure`）、以及代理循环中每次工具调用时（`PreToolUse`、`PostToolUse`）：

<div style={{maxWidth: "500px", margin: "0 auto"}}>
  <Frame>
    <img src="https://mintcdn.com/claude-code/uLsR38F1U_5zPppm/images/hooks-lifecycle.svg?fit=max&auto=format&n=uLsR38F1U_5zPppm&q=85&s=fbdbd78ad9f474da7d344879341341f0" alt="Hook 生命周期图：可选的 Setup 阶段 → SessionStart，然后是每轮循环，包含 UserPromptSubmit、UserPromptExpansion（斜杠命令）、嵌套的代理循环（PreToolUse、PermissionRequest、PostToolUse、PostToolUseFailure、PostToolBatch、SubagentStart/Stop、TaskCreated、TaskCompleted）以及 Stop 或 StopFailure，之后是 TeammateIdle、PreCompact、PostCompact 和 SessionEnd。Elicitation 和 ElicitationResult 嵌套在 MCP 工具执行中，PermissionDenied 是 PermissionRequest 在自动模式下拒绝时的分支，WorktreeCreate、WorktreeRemove、Notification、ConfigChange、InstructionsLoaded、CwdChanged 和 FileChanged 是独立的异步事件，MessageDisplay 是在助手消息文本流式输出时运行的仅展示事件" width="520" height="1228" data-path="images/hooks-lifecycle.svg" />
  </Frame>
</div>

下表汇总了每个事件的触发时机。[Hook 事件](#hook-events) 章节记录了每个事件的完整输入 schema 和决策控制选项。

| 事件 | 触发时机 |
| :--- | :--- |
| `SessionStart` | 会话启动或恢复时 |
| `Setup` | 使用 `--init-only` 启动 Claude Code 时，或在 `-p` 模式下使用 `--init` 或 `--maintenance` 时。用于 CI 或脚本中的一次性准备工作 |
| `UserPromptSubmit` | 你提交提示词后、Claude 处理之前 |
| `UserPromptExpansion` | 用户输入的命令展开为提示词后、发送给 Claude 之前。可以阻止展开 |
| `PreToolUse` | 工具调用执行之前。可以阻止该调用 |
| `PermissionRequest` | 出现权限确认对话框时 |
| `PermissionDenied` | 工具调用被自动模式分类器拒绝时。返回 `{retry: true}` 可告知模型允许重试该被拒绝的工具调用 |
| `PostToolUse` | 工具调用成功后 |
| `PostToolUseFailure` | 工具调用失败后 |
| `PostToolBatch` | 一批并行工具调用全部完成后、下一次模型调用之前 |
| `Notification` | Claude Code 发送通知时 |
| `MessageDisplay` | 助手消息文本展示时 |
| `SubagentStart` | 子代理创建时 |
| `SubagentStop` | 子代理完成时 |
| `TaskCreated` | 通过 `TaskCreate` 创建任务时 |
| `TaskCompleted` | 任务被标记为完成时 |
| `Stop` | Claude 完成响应时 |
| `StopFailure` | 因 API 错误导致当前轮次结束时。此时输出和退出码会被忽略 |
| `TeammateIdle` | [代理团队](https://code.claude.com/docs/en/agent-teams) 中的队友即将进入空闲时 |
| `InstructionsLoaded` | CLAUDE.md 或 `.claude/rules/*.md` 文件被加载到上下文时。在会话启动时触发，也会在会话期间懒加载文件时触发 |
| `ConfigChange` | 会话期间配置文件发生变更时 |
| `CwdChanged` | 工作目录发生变化时（例如 Claude 执行了 `cd` 命令）。适合配合 direnv 等工具进行响应式环境管理 |
| `FileChanged` | 被监视的文件在磁盘上发生变化时。`matcher` 字段指定要监视的文件名 |
| `WorktreeCreate` | 通过 `--worktree` 或 `isolation: "worktree"` 创建 worktree 时。会替代默认的 git 行为 |
| `WorktreeRemove` | worktree 被移除时（会话退出时或子代理完成时） |
| `PreCompact` | 上下文压缩之前 |
| `PostCompact` | 上下文压缩完成之后 |
| `Elicitation` | MCP 服务器在工具调用期间请求用户输入时 |
| `ElicitationResult` | 用户响应 MCP elicitation 之后、响应发回服务器之前 |
| `SessionEnd` | 会话终止时 |

### Hook 的解析流程

**下面用一个阻止危险 shell 命令的 `PreToolUse` Hook 来演示各部分如何配合工作。** `matcher` 将范围缩小到 Bash 工具调用，`if` 条件进一步缩小到匹配 `rm *` 的 Bash 子命令，因此 `block-rm.sh` 只在两个过滤条件都匹配时才会启动：

```json theme={null}
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(rm *)",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-rm.sh",
            "args": []
          }
        ]
      }
    ]
  }
}
```

脚本从 stdin 读取 JSON 输入，提取命令内容，如果包含 `rm -rf` 则返回 `permissionDecision` 为 `"deny"`：

```bash theme={null}
#!/bin/bash
# .claude/hooks/block-rm.sh
COMMAND=$(jq -r '.tool_input.command')

if echo "$COMMAND" | grep -q 'rm -rf'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Destructive command blocked by hook"
    }
  }'
else
  exit 0  # 无决策；走正常权限流程
fi
```

现在假设 Claude Code 决定执行 `Bash "rm -rf /tmp/build"`。以下是完整流程：

<Frame>
  <img src="https://mintcdn.com/claude-code/ikqp3_70mqIahteV/images/hook-resolution.svg?fit=max&auto=format&n=ikqp3_70mqIahteV&q=85&s=be0bf3053550c26de5f54cd64674c197" alt="Hook 解析流程图：PreToolUse 触发 → matcher 检查是否匹配 Bash → if 条件检查是否匹配 Bash(rm *)。如果都匹配，Hook 命令运行并返回 permissionDecision deny，工具调用被阻止，Claude Code 继续执行。如果任一检查不匹配，则跳过 Hook，工具调用正常进行。" width="930" height="270" data-path="images/hook-resolution.svg" />
</Frame>

<Steps>
  <Step title="事件触发">
    `PreToolUse` 事件触发。Claude Code 通过 stdin 将工具输入以 JSON 形式发送给 Hook：

    ```json theme={null}
    { "tool_name": "Bash", "tool_input": { "command": "rm -rf /tmp/build" }, ... }
    ```
  </Step>

  <Step title="Matcher 匹配">
    matcher `"Bash"` 与工具名匹配，因此该 Hook 组被激活。如果省略 matcher 或使用 `"*"`，则该组会在事件每次发生时都被激活。
  </Step>

  <Step title="If 条件匹配">
    `if` 条件 `"Bash(rm *)"` 匹配成功，因为 `rm -rf /tmp/build` 是一个符合 `rm *` 模式的子命令，因此该处理器被启动。如果命令是 `npm test`，`if` 检查就会失败，`block-rm.sh` 不会运行，从而避免了进程启动的开销。`if` 字段是可选的；没有它时，匹配组中的每个处理器都会运行。
  </Step>

  <Step title="Hook 处理器运行">
    脚本检查完整命令并发现了 `rm -rf`，于是向 stdout 打印决策：

    ```json theme={null}
    {
      "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "Destructive command blocked by hook"
      }
    }
    ```

    如果命令是更安全的 `rm` 变体（如 `rm file.txt`），脚本会走 `exit 0`。退出码 0 且无输出表示 Hook 没有需要报告的决策，工具调用将继续走正常的 [权限流程](https://code.claude.com/docs/en/permissions)。Hook 可以拒绝调用，但保持沉默并不意味着批准。
  </Step>

  <Step title="Claude Code 响应结果">
    Claude Code 读取 JSON 决策，阻止工具调用，并将原因展示给 Claude。
  </Step>
</Steps>

下面的 [配置](#configuration) 章节记录了完整 schema，每个 [Hook 事件](#hook-events) 章节记录了你的命令接收什么输入以及可以返回什么输出。

## 配置

**Hooks 在 JSON 设置文件中定义。** 配置有三层嵌套结构：

1. 选择要响应的 [Hook 事件](#hook-events)，如 `PreToolUse` 或 `Stop`
2. 添加 [matcher 组](#matcher-patterns) 来过滤触发条件，如"仅针对 Bash 工具"
3. 定义一个或多个 [Hook 处理器](#hook-handler-fields)，在匹配时运行

请参阅上方 [Hook 的解析流程](#how-a-hook-resolves) 了解带注释的完整示例。

<Note>
  本文档对每一层使用特定术语：**Hook 事件** 指生命周期节点，**matcher 组** 指过滤器，**Hook 处理器** 指实际运行的 shell 命令、HTTP 端点、MCP 工具、提示词或代理。单独的"Hook"指整个功能。
</Note>

### Hook 定义位置

**定义 Hook 的位置决定了它的作用范围：**

| 位置 | 作用范围 | 是否可共享 |
| :--- | :--- | :--- |
| `~/.claude/settings.json` | 你的所有项目 | 否，仅限本机 |
| `.claude/settings.json` | 单个项目 | 是，可提交到仓库 |
| `.claude/settings.local.json` | 单个项目 | 否，Claude Code 创建时会加入 gitignore |
| 托管策略设置 | 整个组织 | 是，由管理员控制 |
| [插件](https://code.claude.com/docs/en/plugins) `hooks/hooks.json` | 插件启用时 | 是，随插件打包 |
| [Skill](https://code.claude.com/docs/en/skills) 或 [代理](https://code.claude.com/docs/en/sub-agents) frontmatter | 组件活跃期间 | 是，在组件文件中定义 |

关于设置文件解析的详细信息，请参阅 [设置](https://code.claude.com/docs/en/settings)。企业管理员可以使用 `allowManagedHooksOnly` 来禁止用户、项目和插件 Hook。托管设置中通过 `enabledPlugins` 强制启用的插件 Hook 不受此限制，管理员可以通过组织市场分发经过审核的 Hook。请参阅 [Hook 配置](https://code.claude.com/docs/en/settings#hook-configuration)。

### Matcher 模式

**`matcher` 字段用于过滤 Hook 何时触发。** matcher 的求值方式取决于它包含的字符：

| Matcher 值 | 求值方式 | 示例 |
| :--- | :--- | :--- |
| `"*"`、`""` 或省略 | 匹配所有 | 在事件每次发生时都触发 |
| 仅包含字母、数字、`_`、空格、`,` 和 `\|` | 精确字符串，或用 `\|` 或 `,`（允许前后有空格）分隔的精确字符串列表 | `Bash` 仅匹配 Bash 工具；`Edit\|Write` 和 `Edit, Write` 分别精确匹配其中任一工具 |
| 包含任何其他字符 | JavaScript 正则表达式 | `^Notebook` 匹配所有以 Notebook 开头的工具；`mcp__memory__.*` 匹配 `memory` 服务器的所有工具 |

逗号分隔符及其前后空格容差需要 Claude Code v2.1.191 或更高版本。`FileChanged` 和 `StopFailure` 事件仅接受 `|` 作为列表分隔符，将 `,` 视为字面字符；下方表格中列出的其他所有事件接受 `|` 或 `,`。

`FileChanged` 事件在构建监视列表时不遵循上述规则。请参阅 [FileChanged](#filechanged)。

**每种事件类型匹配的字段不同：**

| 事件 | Matcher 过滤的内容 | 示例 matcher 值 |
| :--- | :--- | :--- |
| `PreToolUse`、`PostToolUse`、`PostToolUseFailure`、`PermissionRequest`、`PermissionDenied` | 工具名 | `Bash`、`Edit\|Write`、`mcp__.*` |
| `SessionStart` | 会话启动方式 | `startup`、`resume`、`clear`、`compact` |
| `Setup` | 触发 setup 的 CLI 标志 | `init`、`maintenance` |
| `SessionEnd` | 会话结束原因 | `clear`、`resume`、`logout`、`prompt_input_exit`、`bypass_permissions_disabled`、`other` |
| `Notification` | 通知类型 | `permission_prompt`、`idle_prompt`、`auth_success`、`elicitation_dialog`、`elicitation_complete`、`elicitation_response` |
| `SubagentStart` | 代理类型 | `general-purpose`、`Explore`、`Plan` 或自定义代理名 |
| `PreCompact`、`PostCompact` | 触发压缩的原因 | `manual`、`auto` |
| `SubagentStop` | 代理类型 | 与 `SubagentStart` 相同 |
| `ConfigChange` | 配置来源 | `user_settings`、`project_settings`、`local_settings`、`policy_settings`、`skills` |
| `CwdChanged` | 不支持 matcher | 每次目录变更时都触发 |
| `FileChanged` | 要监视的字面文件名（参见 [FileChanged](#filechanged)） | `.envrc\|.env` |
| `StopFailure` | 错误类型 | `rate_limit`、`overloaded`、`authentication_failed`、`oauth_org_not_allowed`、`billing_error`、`invalid_request`、`model_not_found`、`server_error`、`max_output_tokens`、`unknown` |
| `InstructionsLoaded` | 加载原因 | `session_start`、`nested_traversal`、`path_glob_match`、`include`、`compact` |
| `UserPromptExpansion` | 命令名 | 你的 skill 或命令名称 |
| `Elicitation` | MCP 服务器名 | 你配置的 MCP 服务器名称 |
| `ElicitationResult` | MCP 服务器名 | 与 `Elicitation` 相同 |
| `UserPromptSubmit`、`PostToolBatch`、`Stop`、`TeammateIdle`、`TaskCreated`、`TaskCompleted`、`WorktreeCreate`、`WorktreeRemove`、`MessageDisplay` | 不支持 matcher | 每次事件发生时都触发 |

**Matcher 针对 Claude Code 通过 stdin 发送给 Hook 的 [JSON 输入](#hook-input-and-output) 中的某个字段运行。** 对于工具事件，该字段是 `tool_name`。每个 [Hook 事件](#hook-events) 章节都列出了完整的 matcher 值集合和该事件的输入 schema。

以下示例仅在 Claude 写入或编辑文件时运行 lint 脚本：

```json theme={null}
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/lint-check.sh"
          }
        ]
      }
    ]
  }
}
```

`UserPromptSubmit`、`PostToolBatch`、`Stop`、`TeammateIdle`、`TaskCreated`、`TaskCompleted`、`WorktreeCreate`、`WorktreeRemove` 和 `CwdChanged` 不支持 matcher，每次事件发生时都会触发。如果你为这些事件添加了 `matcher` 字段，它会被静默忽略。

**对于工具事件，可以通过在单个 Hook 处理器上设置 [`if` 字段](#common-fields) 来进一步缩小范围。** `if` 使用 [权限规则语法](https://code.claude.com/docs/en/permissions) 来同时匹配工具名和参数，例如 `"Bash(git *)"` 在 Bash 输入的任何子命令匹配 `git *` 时运行，`"Edit(*.ts)"` 仅对 TypeScript 文件运行。

#### 匹配 MCP 工具

**[MCP](https://code.claude.com/docs/en/mcp) 服务器工具在工具事件中作为普通工具出现**（`PreToolUse`、`PostToolUse`、`PostToolUseFailure`、`PermissionRequest`、`PermissionDenied`），因此你可以像匹配其他工具名一样匹配它们。

MCP 工具遵循 `mcp__<server>__<tool>` 的命名模式，例如：

* `mcp__memory__create_entities`：Memory 服务器的创建实体工具
* `mcp__filesystem__read_file`：Filesystem 服务器的读取文件工具
* `mcp__github__search_repositories`：GitHub 服务器的搜索工具

**要匹配某个服务器的所有工具，需在服务器前缀后追加 `.*`。** `.*` 是必需的：类似 `mcp__memory` 的 matcher 仅包含字母和下划线，会被当作精确字符串比较，匹配不到任何工具。

* `mcp__memory__.*` 匹配 `memory` 服务器的所有工具
* `mcp__.*__write.*` 匹配任何服务器上名称以 `write` 开头的工具

以下示例记录 memory 服务器的所有操作，并验证任何 MCP 服务器的写入操作：

```json theme={null}
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__memory__.*",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Memory operation initiated' >> ~/mcp-operations.log"
          }
        ]
      },
      {
        "matcher": "mcp__.*__write.*",
        "hooks": [
          {
            "type": "command",
            "command": "/home/user/scripts/validate-mcp-write.py"
          }
        ]
      }
    ]
  }
}
```

### Hook 处理器字段

**内层 `hooks` 数组中的每个对象就是一个 Hook 处理器：** 在 matcher 匹配时运行的 shell 命令、HTTP 端点、MCP 工具、LLM 提示词或代理。共有五种类型：

* **[命令 Hook](#command-hook-fields)**（`type: "command"`）：运行 shell 命令。脚本通过 stdin 接收事件的 [JSON 输入](#hook-input-and-output)，通过退出码和 stdout 返回结果。
* **[HTTP Hook](#http-hook-fields)**（`type: "http"`）：将事件的 JSON 输入作为 HTTP POST 请求发送到 URL。端点通过响应体返回结果，使用与命令 Hook 相同的 [JSON 输出格式](#json-output)。
* **[MCP 工具 Hook](#mcp-tool-hook-fields)**（`type: "mcp_tool"`）：调用已连接的 [MCP 服务器](https://code.claude.com/docs/en/mcp) 上的工具。工具的文本输出按命令 Hook 的 stdout 处理。
* **[Prompt Hook](#prompt-and-agent-hook-fields)**（`type: "prompt"`）：向 Claude 模型发送提示词进行单轮评估。模型以 JSON 返回 yes/no 决策。请参阅 [基于 Prompt 的 Hook](#prompt-based-hooks)。
* **[Agent Hook](#prompt-and-agent-hook-fields)**（`type: "agent"`）：启动一个子代理，可以使用 Read、Grep 和 Glob 等工具来验证条件后再返回决策。Agent Hook 是实验性功能，可能会变更。请参阅 [基于 Agent 的 Hook](#agent-based-hooks)。

**所有匹配的 Hook 并行运行，相同的处理器会自动去重。** 命令 Hook 按命令字符串和 `args` 去重，HTTP Hook 按 URL 去重。

处理器在当前目录运行，使用 Claude Code 的环境变量。`$CLAUDE_CODE_REMOTE` 环境变量在远程 Web 环境中设为 `"true"`，在本地 CLI 中不设置。

#### 通用字段

**以下字段适用于所有 Hook 类型：**

| 字段 | 是否必填 | 说明 |
| :--- | :--- | :--- |
| `type` | 是 | `"command"`、`"http"`、`"mcp_tool"`、`"prompt"` 或 `"agent"` |
| `if` | 否 | 权限规则语法，用于过滤此 Hook 何时运行，如 `"Bash(git *)"` 或 `"Edit(*.ts)"`。仅当工具调用匹配模式时，Hook 命令才会运行。关于 Bash 模式如何针对子命令、`$()`  和反引号求值，请参阅下方的 [Bash 匹配表](#bash-if-matching)。仅在工具事件（`PreToolUse`、`PostToolUse`、`PostToolUseFailure`、`PermissionRequest`、`PermissionDenied`）上求值。在其他事件上，设置了 `if` 的 Hook 永远不会运行。使用与 [权限规则](https://code.claude.com/docs/en/permissions) 相同的语法 |
| `timeout` | 否 | 超时秒数。默认值：`command`、`http` 和 `mcp_tool` 为 600 秒；`prompt` 为 30 秒；`agent` 为 60 秒。[`UserPromptSubmit`](#userpromptsubmit) 将 `command`、`http` 和 `mcp_tool` 的默认值降低为 30 秒，[`MessageDisplay`](#messagedisplay) 降低为 10 秒 |
| `statusMessage` | 否 | Hook 运行时显示的自定义 spinner 消息 |
| `once` | 否 | 如果为 `true`，在会话中只运行一次然后移除。仅对 [skill frontmatter](#hooks-in-skills-and-agents) 中声明的 Hook 生效；在设置文件和 agent frontmatter 中会被忽略 |

**`if` 字段只接受一条权限规则。** 没有 `&&`、`||` 或列表语法来组合规则；要应用多个条件，请为每个条件定义一个单独的 Hook 处理器。

<span id="bash-if-matching" />**对于 Bash 模式，Hook 命令是否运行取决于模式的形式和 Claude 调用的 Bash 命令。** 前导 `VAR=value` 赋值在匹配前会被去除。

| `if` 模式 | Bash 命令 | Hook 是否运行？ | 原因 |
| :--- | :--- | :--- | :--- |
| `Bash(git *)` | `FOO=bar git push` | 是 | 前导赋值被去除；`git push` 匹配 |
| `Bash(git *)` | `npm test && git push` | 是 | 检查每个子命令；`git push` 匹配 |
| `Bash(rm *)` | `echo $(rm -rf /)` | 是 | 检查 `$()` 和反引号内的命令；`rm -rf /` 匹配 |
| `Bash(rm *)` | `echo $(date)` | 否 | 没有子命令匹配 `rm *` |
| `Bash(git push *)` | `echo $(date)` | 是 | 指定了命令名以外更多内容的模式，在遇到 `$()`、反引号或 `$VAR` 时会无论如何运行 Hook |

**当 Bash 命令无法解析时，过滤器也会开放运行（即无论模式如何都运行你的 Hook）。** 因为 `if` 过滤器是尽力而为的，要强制允许或拒绝，请使用 [权限系统](https://code.claude.com/docs/en/permissions) 而非 Hook。

#### 命令 Hook 字段

**除 [通用字段](#common-fields) 外，命令 Hook 还接受以下字段：**

| 字段 | 是否必填 | 说明 |
| :--- | :--- | :--- |
| `command` | 是 | 要执行的 shell 命令。配合 `args` 使用时为直接启动的可执行文件。请参阅 [Exec 形式和 Shell 形式](#exec-form-and-shell-form) |
| `args` | 否 | 参数列表。存在时，`command` 被解析为可执行文件，直接用 `args` 作为参数向量启动，不经过 shell。请参阅 [Exec 形式和 Shell 形式](#exec-form-and-shell-form) |
| `async` | 否 | 如果为 `true`，在后台运行不阻塞。请参阅 [后台运行 Hook](#run-hooks-in-the-background) |
| `asyncRewake` | 否 | 如果为 `true`，在后台运行并在退出码为 2 时唤醒 Claude。隐含 `async`。Hook 的 stderr（如果 stderr 为空则用 stdout）会作为系统提醒展示给 Claude，以便它对长时间运行的后台失败做出反应 |
| `shell` | 否 | 此 Hook 使用的 shell。接受 `"bash"`（默认）或 `"powershell"`。设为 `"powershell"` 会在 Windows 上通过 PowerShell 运行命令。不需要 `CLAUDE_CODE_USE_POWERSHELL_TOOL`，因为 Hook 直接启动 PowerShell。设置了 `args` 时此字段被忽略 |

<a id="exec-form-and-shell-form" />

##### Exec 形式和 Shell 形式

**命令 Hook 在设置了 `args` 时以 exec 形式运行，省略 `args` 时以 shell 形式运行。** 当 Hook 引用 [路径占位符](#reference-scripts-by-path) 时应设置 `args`，因为每个元素作为一个完整参数传递，无需引号。当需要 shell 功能（如管道或 `&&`）时应省略 `args`，或者两种情况都不涉及时也可省略。

**Exec 形式** 在 `args` 存在时运行。Claude Code 将 `command` 解析为 `PATH` 上的可执行文件，直接用 `args` 作为参数向量启动。没有 shell 参与，因此每个 `args` 元素就是一个精确参数，路径占位符（如 `${CLAUDE_PLUGIN_ROOT}`）在 `command` 和每个 `args` 元素中作为纯字符串替换。撇号、`$` 和反引号等特殊字符原样传递，因为没有 shell 来解释它们。任何平台上都不会发生 shell 标记化。

**Shell 形式** 在 `args` 缺失时运行。`command` 字符串会传递给 shell：macOS 和 Linux 上是 `sh -c`，Windows 上是 Git Bash，或 Git Bash 未安装时是 PowerShell。设置 `shell` 字段可显式选择。shell 会标记化字符串、展开变量、解释管道、`&&`、重定向和 glob。

<Note>
  在 Windows 上，exec 形式要求 `command` 解析为真正的可执行文件（如 `.exe`）。npm、npx、eslint 和其他工具在 `node_modules/.bin` 中安装的 `.cmd` 和 `.bat` 包装脚本不是可执行文件，不能在无 shell 的情况下启动。要在 exec 形式中运行它们，请用 `node` 直接调用底层脚本，例如 `"command": "node", "args": ["${CLAUDE_PLUGIN_ROOT}/node_modules/eslint/bin/eslint.js"]`。`node` 加脚本路径的模式在所有平台上都有效，因为 `node.exe` 是真正的二进制文件。要按名称运行 `.cmd` 或 `.bat` 包装脚本，请使用 shell 形式。
</Note>

以下示例运行插件附带的 Node 脚本。Exec 形式将解析后的脚本路径作为一个完整参数传递，无需引号：

```json theme={null}
{
  "type": "command",
  "command": "node",
  "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/format.js", "--fix"]
}
```

等效的 shell 形式需要引号来处理包含空格或特殊字符的路径：

```json theme={null}
{
  "type": "command",
  "command": "node \"${CLAUDE_PLUGIN_ROOT}\"/scripts/format.js --fix"
}
```

两种形式都支持相同的 [路径占位符](#reference-scripts-by-path)，并且都会在启动的进程中将它们导出为环境变量 `CLAUDE_PROJECT_DIR`、`CLAUDE_PLUGIN_ROOT` 和 `CLAUDE_PLUGIN_DATA`，因此脚本无论以何种方式启动都可以读取 `process.env.CLAUDE_PLUGIN_ROOT`。插件 Hook 还会替换 `${user_config.*}` 值；请参阅 [用户配置](https://code.claude.com/docs/en/plugins-reference#user-configuration)。

<Note>
  在 exec 形式中，`command` 只能是可执行文件名或路径。如果 `command` 是不含路径分隔符的裸名称，并且在设置了 `args` 的情况下还包含空格，Claude Code 会记录警告，因为启动会失败：不存在名为 `node script.js` 的可执行文件。请将多余的标记移到 `args` 中。包含空格的绝对路径（如 `C:\Program Files\nodejs\node.exe`）是单个有效的可执行文件，不会触发警告。
</Note>

#### HTTP Hook 字段

**除 [通用字段](#common-fields) 外，HTTP Hook 还接受以下字段：**

| 字段 | 是否必填 | 说明 |
| :--- | :--- | :--- |
| `url` | 是 | POST 请求发送的目标 URL |
| `headers` | 否 | 以键值对形式提供的额外 HTTP 头。值支持使用 `$VAR_NAME` 或 `${VAR_NAME}` 语法进行环境变量插值。仅 `allowedEnvVars` 中列出的变量会被解析 |
| `allowedEnvVars` | 否 | 允许插值到头部值中的环境变量名称列表。引用未列出变量时会替换为空字符串。任何环境变量插值都需要此字段才能生效 |

**Claude Code 将 Hook 的 [JSON 输入](#hook-input-and-output) 作为 POST 请求体发送，Content-Type 为 `application/json`。** 响应体使用与命令 Hook 相同的 [JSON 输出格式](#json-output)。

错误处理与命令 Hook 不同：非 2xx 响应、连接失败和超时都会产生非阻塞错误，允许继续执行。要阻止工具调用或拒绝权限，请返回 2xx 响应并在 JSON 体中包含 `decision: "block"` 或包含 `permissionDecision: "deny"` 的 `hookSpecificOutput`。

以下示例将 `PreToolUse` 事件发送到本地验证服务，使用 `MY_TOKEN` 环境变量中的令牌进行认证：

```json theme={null}
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "http",
            "url": "http://localhost:8080/hooks/pre-tool-use",
            "timeout": 30,
            "headers": {
              "Authorization": "Bearer $MY_TOKEN"
            },
            "allowedEnvVars": ["MY_TOKEN"]
          }
        ]
      }
    ]
  }
}
```

#### MCP 工具 Hook 字段

**除 [通用字段](#common-fields) 外，MCP 工具 Hook 还接受以下字段：**

| 字段 | 是否必填 | 说明 |
| :--- | :--- | :--- |
| `server` | 是 | 已配置的 MCP 服务器名称。服务器必须已连接；Hook 不会触发 OAuth 或连接流程 |
| `tool` | 是 | 要在该服务器上调用的工具名称 |
| `input` | 否 | 传递给工具的参数。字符串值支持使用 Hook 的 [JSON 输入](#hook-input-and-output) 进行 `${path}` 替换，如 `"${tool_input.file_path}"` |

**工具的文本内容按命令 Hook 的 stdout 处理：** 如果能解析为有效的 [JSON 输出](#json-output)，则作为决策处理；否则作为纯文本显示。如果指定的服务器未连接或工具返回 `isError: true`，Hook 会产生非阻塞错误，继续执行。

MCP 工具 Hook 在 Claude Code 连接到你的 MCP 服务器后对所有 Hook 事件可用。`SessionStart` 和 `Setup` 通常在服务器完成连接之前触发，因此这些事件上的 Hook 应预期首次运行时出现"未连接"错误。

以下示例在每次 `Write` 或 `Edit` 后调用 `my_server` MCP 服务器上的 `security_scan` 工具，传入编辑文件的路径：

```json theme={null}
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "mcp_tool",
            "server": "my_server",
            "tool": "security_scan",
            "input": { "file_path": "${tool_input.file_path}" }
          }
        ]
      }
    ]
  }
}
```

#### Prompt 和 Agent Hook 字段

**除 [通用字段](#common-fields) 外，prompt 和 agent Hook 还接受以下字段：**

| 字段 | 是否必填 | 说明 |
| :--- | :--- | :--- |
| `prompt` | 是 | 发送给模型的提示词文本。使用 `$ARGUMENTS` 作为 Hook 输入 JSON 的占位符。用反斜杠转义可包含字面文本：`\$1.00` 渲染为 `$1.00` |
| `model` | 否 | 用于评估的模型。默认为快速模型 |

### 通过路径引用脚本

**使用以下占位符可相对于项目或插件根目录引用 Hook 脚本，** 无论 Hook 运行时的工作目录是什么：

* `${CLAUDE_PROJECT_DIR}`：项目根目录。Claude Code 也会在 [stdio MCP 服务器](https://code.claude.com/docs/en/mcp#option-3-add-a-local-stdio-server) 和插件 LSP 服务器的环境中设置此变量。
* `${CLAUDE_PLUGIN_ROOT}`：插件的安装目录，用于引用随 [插件](https://code.claude.com/docs/en/plugins) 打包的脚本。每次插件更新时会变化。
* `${CLAUDE_PLUGIN_DATA}`：插件的 [持久化数据目录](https://code.claude.com/docs/en/plugins-reference#persistent-data-directory)，用于存放需要在插件更新后保留的依赖和状态。

**对于引用路径占位符的 Hook，优先使用 [exec 形式](#exec-form-and-shell-form)。** Exec 形式将每个 `args` 元素作为一个完整参数传递，不经过 shell 标记化，因此包含空格或特殊字符的路径无需引号。在 shell 形式中，需要用双引号包裹每个占位符。

<Tabs>
  <Tab title="项目脚本">
    以下示例使用 `${CLAUDE_PROJECT_DIR}` 在每次 `Write` 或 `Edit` 工具调用后，从项目的 `.claude/hooks/` 目录运行样式检查器：

    ```json theme={null}
    {
      "hooks": {
        "PostToolUse": [
          {
            "matcher": "Write|Edit",
            "hooks": [
              {
                "type": "command",
                "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/check-style.sh",
                "args": []
              }
            ]
          }
        ]
      }
    }
    ```
  </Tab>

  <Tab title="插件脚本">
    在 `hooks/hooks.json` 中定义插件 Hook，可带一个顶级 `description` 字段。启用插件后，其 Hook 会与你的用户和项目 Hook 合并。

    以下示例运行随插件打包的格式化脚本：

    ```json theme={null}
    {
      "description": "Automatic code formatting",
      "hooks": {
        "PostToolUse": [
          {
            "matcher": "Write|Edit",
            "hooks": [
              {
                "type": "command",
                "command": "${CLAUDE_PLUGIN_ROOT}/scripts/format.sh",
                "args": [],
                "timeout": 30
              }
            ]
          }
        ]
      }
    }
    ```

    详情请参阅 [插件组件参考](https://code.claude.com/docs/en/plugins-reference#hooks)。
  </Tab>
</Tabs>

### Skill 和 Agent 中的 Hook

**除了设置文件和插件，Hook 还可以通过 frontmatter 直接定义在 [Skill](https://code.claude.com/docs/en/skills) 和 [子代理](https://code.claude.com/docs/en/sub-agents) 中。** 这些 Hook 的作用域限定在组件的生命周期内，仅在组件活跃时运行。

所有 Hook 事件都受支持。对于子代理，`Stop` Hook 会自动转换为 `SubagentStop`，因为子代理完成时触发的就是该事件。

Hook 使用与设置文件 Hook 相同的配置格式，但作用域限定在组件的生命周期内，组件完成时会被清理。

以下 skill 定义了一个 `PreToolUse` Hook，在每次 `Bash` 命令前运行安全验证脚本：

```yaml theme={null}
---
name: secure-operations
description: Perform operations with security checks
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh"
---
```

Agent 在其 YAML frontmatter 中使用相同的格式。

### `/hooks` 菜单

**在 Claude Code 中输入 `/hooks` 可打开已配置 Hook 的只读浏览器。** 菜单显示每个 Hook 事件及其配置的 Hook 数量，允许你深入查看 matcher，并展示每个 Hook 处理器的完整详情。用它来验证配置、检查 Hook 来自哪个设置文件，或查看 Hook 的命令、提示词或 URL。

菜单显示所有五种 Hook 类型：`command`、`prompt`、`agent`、`http` 和 `mcp_tool`。每个 Hook 带有 `[type]` 前缀和一个来源标识，指明其定义位置：

* `User`：来自 `~/.claude/settings.json`
* `Project`：来自 `.claude/settings.json`
* `Local`：来自 `.claude/settings.local.json`
* `Plugin`：来自插件的 `hooks/hooks.json`
* `Session`：为当前会话注册在内存中
* `Built-in`：由 Claude Code 内部注册

选择某个 Hook 会打开详情视图，显示其事件、matcher、类型、来源文件以及完整的命令、提示词或 URL。菜单是只读的：要添加、修改或删除 Hook，请直接编辑设置 JSON 或让 Claude 进行修改。

### 禁用或移除 Hook

**要移除 Hook，从设置 JSON 文件中删除其条目即可。**

**要临时禁用所有 Hook 而不删除它们，** 在设置文件中设置 `"disableAllHooks": true`。目前没有办法在保留配置的同时禁用单个 Hook。

`disableAllHooks` 设置遵循托管设置层级。如果管理员通过托管策略设置配置了 Hook，用户、项目或本地设置中的 `disableAllHooks` 无法禁用那些托管 Hook。只有在托管设置层级设置的 `disableAllHooks` 才能禁用托管 Hook。

直接编辑设置文件中的 Hook 通常会被文件监视器自动拾取。
## Hook 的输入与输出

**命令 Hook 通过 stdin 接收 JSON 数据，通过退出码、stdout 和 stderr 返回结果。** HTTP Hook 接收相同的 JSON 作为 POST 请求体，通过 HTTP 响应体返回结果。本节介绍所有事件通用的字段和行为。每个事件在 [Hook 事件](#hook-events) 章节中有各自的输入 schema 和决策控制选项。

**从 v2.1.139 起，macOS 和 Linux 上的命令 Hook 在独立会话中运行，没有控制终端。** Hook 进程及其子进程无法打开 `/dev/tty`，也无法直接向 Claude Code 界面发送转义序列。Windows 上不存在 `/dev/tty`。要在任何平台上向用户展示消息，请在 JSON 输出中返回 [`systemMessage`](#json-output)。要触发桌面通知、设置窗口标题或响铃，请返回 [`terminalSequence`](#emit-terminal-notifications)。

### 通用输入字段

**Hook 事件接收以下 JSON 字段，以及各事件章节中记录的事件专属字段。** 对于命令 Hook，JSON 通过 stdin 传入；对于 HTTP Hook，JSON 作为 POST 请求体传入。

| 字段 | 说明 |
| :--- | :--- |
| `session_id` | 当前会话标识符 |
| `transcript_path` | 对话 JSON 文件路径 |
| `cwd` | Hook 被调用时的当前工作目录 |
| `permission_mode` | 当前[权限模式](https://code.claude.com/docs/en/permissions#permission-modes)：`"default"`、`"plan"`、`"acceptEdits"`、`"auto"`、`"dontAsk"` 或 `"bypassPermissions"`。并非所有事件都包含此字段，请参考各事件的 JSON 示例 |
| `effort` | 包含 `level` 字段的对象，表示当前轮次使用的[effort 级别](https://code.claude.com/docs/en/model-config#adjust-effort-level)：`"low"`、`"medium"`、`"high"`、`"xhigh"` 或 `"max"`。如果请求的 effort 超过当前模型支持的上限，这里显示的是模型实际降级后的级别。Ultracode 不是独立级别，以 `"xhigh"` 报告。该对象与[状态栏](https://code.claude.com/docs/en/statusline#available-data)中的 `effort` 字段一致。出现在工具使用上下文中触发的事件，如 `PreToolUse`、`PostToolUse`、`Stop` 和 `SubagentStop`（仅当前模型支持 effort 参数时）。该级别也可通过环境变量 `$CLAUDE_EFFORT` 供 Hook 命令和 Bash 工具使用 |
| `hook_event_name` | 触发的事件名称 |

**使用 `--agent` 运行或在子代理内部时，会额外包含两个字段：**

| 字段 | 说明 |
| :--- | :--- |
| `agent_id` | 子代理的唯一标识符。仅当 Hook 在子代理调用内部触发时存在。用于区分子代理 Hook 调用和主线程调用 |
| `agent_type` | 代理名称（例如 `"Explore"` 或 `"security-reviewer"`）。在会话使用 `--agent` 或 Hook 在子代理内部触发时存在。对于子代理，子代理的 type 优先于会话的 `--agent` 值。对于[自定义子代理](https://code.claude.com/docs/en/sub-agents)，这是代理 frontmatter 中的 `name` 字段，而非文件名 |

**只有 [`SessionStart`](#sessionstart) Hook 能接收 `model` 字段，且不保证一定存在。** 不存在 `$CLAUDE_MODEL` 环境变量。Hook 进程继承父环境，因此如果你在 shell 中设置了 `$ANTHROPIC_MODEL`，Hook 可以读取该值，但在会话中通过 `/model` 切换模型时该值不会改变。

例如，一个针对 Bash 命令的 `PreToolUse` Hook 会在 stdin 中收到以下内容：

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/home/user/.claude/projects/.../transcript.jsonl",
  "cwd": "/home/user/my-project",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "npm test"
  }
}
```

`tool_name` 和 `tool_input` 是事件专属字段。每个 [Hook 事件](#hook-events) 章节文档中记录了该事件的附加字段。

### 退出码输出

**Hook 命令的退出码告诉 Claude Code 操作应该继续、被阻止还是被忽略。**

**退出码 0** 表示成功。Claude Code 会解析 stdout 中的 [JSON 输出字段](#json-output)。JSON 输出仅在退出码为 0 时被处理。对于大多数事件，stdout 写入调试日志但不显示在对话记录中。例外是 `UserPromptSubmit`、`UserPromptExpansion` 和 `SessionStart`，其 stdout 会作为上下文添加，Claude 可以看到并据此行动。

**退出码 2** 表示阻止性错误。Claude Code 忽略 stdout 及其中的 JSON，而是将 stderr 文本作为错误消息反馈给 Claude。具体效果取决于事件：`PreToolUse` 阻止工具调用，`UserPromptSubmit` 拒绝提示词，等等。完整列表见[退出码 2 各事件行为](#exit-code-2-behavior-per-event)。

**其他任何退出码** 对大多数 Hook 事件来说是非阻止性错误。对话记录中会显示 `<hook name> hook error` 提示以及 stderr 的第一行，便于在不使用 `--debug` 的情况下定位原因。执行继续，完整的 stderr 写入调试日志。

例如，一个阻止危险 Bash 命令的 Hook 命令脚本：

```bash theme={null}
#!/bin/bash
# Reads JSON input from stdin, checks the command
command=$(jq -r '.tool_input.command' < /dev/stdin)

if [[ "$command" == rm* ]]; then
  echo "Blocked: rm commands are not allowed" >&2
  exit 2  # Blocking error: tool call is prevented
fi

exit 0  # No decision: the normal permission flow applies
```

> **注意：** 对于大多数 Hook 事件，只有退出码 2 能阻止操作。Claude Code 将退出码 1 视为非阻止性错误并继续执行操作，尽管 1 是 Unix 约定的失败码。如果你的 Hook 要执行策略强制，请使用 `exit 2`。例外是 `WorktreeCreate`，任何非零退出码都会中止 worktree 创建。

#### 退出码 2 各事件行为

**退出码 2 是 Hook 发出"停止，不要执行"信号的方式。** 效果取决于事件，因为有些事件代表可以被阻止的操作（如尚未执行的工具调用），而有些代表已经发生或无法阻止的事情。

| Hook 事件 | 可阻止？ | 退出码 2 的效果 |
| :--- | :--- | :--- |
| `PreToolUse` | 是 | 阻止工具调用 |
| `PermissionRequest` | 是 | 拒绝权限请求 |
| `UserPromptSubmit` | 是 | 阻止提示词处理并清除提示词 |
| `UserPromptExpansion` | 是 | 阻止扩展 |
| `Stop` | 是 | 阻止 Claude 停止，继续对话 |
| `SubagentStop` | 是 | 阻止子代理停止 |
| `TeammateIdle` | 是 | 阻止队友进入空闲状态（队友继续工作） |
| `TaskCreated` | 是 | 回滚任务创建 |
| `TaskCompleted` | 是 | 阻止任务被标记为已完成 |
| `ConfigChange` | 是 | 阻止配置更改生效（`policy_settings` 除外） |
| `StopFailure` | 否 | 输出和退出码被忽略 |
| `PostToolUse` | 否 | 将 stderr 展示给 Claude（工具已执行完毕） |
| `PostToolUseFailure` | 否 | 将 stderr 展示给 Claude（工具已失败） |
| `PostToolBatch` | 是 | 在下一次模型调用前停止代理循环 |
| `PermissionDenied` | 否 | 退出码和 stderr 被忽略（拒绝已发生）。使用 JSON `hookSpecificOutput.retry: true` 告知模型可以重试 |
| `Notification` | 否 | 仅向用户显示 stderr |
| `SubagentStart` | 否 | 仅向用户显示 stderr |
| `SessionStart` | 否 | 仅向用户显示 stderr |
| `Setup` | 否 | 仅向用户显示 stderr |
| `SessionEnd` | 否 | 仅向用户显示 stderr |
| `CwdChanged` | 否 | 仅向用户显示 stderr |
| `FileChanged` | 否 | 仅向用户显示 stderr |
| `PreCompact` | 是 | 阻止压缩 |
| `PostCompact` | 否 | 仅向用户显示 stderr |
| `Elicitation` | 是 | 拒绝询问 |
| `ElicitationResult` | 是 | 阻止响应（操作变为拒绝） |
| `WorktreeCreate` | 是 | 任何非零退出码都导致 worktree 创建失败 |
| `WorktreeRemove` | 否 | 失败仅在调试模式下记录日志 |
| `InstructionsLoaded` | 否 | 退出码被忽略 |
| `MessageDisplay` | 否 | 显示原始文本 |

### HTTP 响应处理

**HTTP Hook 使用 HTTP 状态码和响应体代替退出码和 stdout：**

* **2xx 且响应体为空**：成功，等同于退出码 0 无输出
* **2xx 且响应体为纯文本**：成功，文本作为上下文添加
* **2xx 且响应体为 JSON**：成功，按照与命令 Hook 相同的 [JSON 输出](#json-output) schema 解析
* **非 2xx 状态码**：非阻止性错误，继续执行
* **连接失败或超时**：非阻止性错误，继续执行

**与命令 Hook 不同，HTTP Hook 无法仅通过状态码发出阻止信号。** 要阻止工具调用或拒绝权限，需要返回 2xx 响应并在 JSON 响应体中包含相应的决策字段。

### JSON 输出

**退出码只能阻止或静默，但 JSON 输出能提供更精细的控制。** 不必使用退出码 2 来阻止，你可以退出码 0 并将 JSON 对象输出到 stdout。Claude Code 从该 JSON 中读取特定字段来控制行为，包括用于阻止、允许或上报给用户的[决策控制](#decision-control)。

> **注意：** 每个 Hook 只能选择一种方式，不能两者兼用：要么仅用退出码传达信号，要么退出码 0 并输出 JSON 进行结构化控制。Claude Code 仅在退出码为 0 时处理 JSON。如果退出码为 2，任何 JSON 都会被忽略。

**stdout 必须只包含 JSON 对象。** 如果你的 shell 配置文件在启动时打印了文本，可能会干扰 JSON 解析。详见故障排除指南中的 [JSON 验证失败](https://code.claude.com/docs/en/hooks-guide#json-validation-failed)。

**Hook 输出字符串（包括 `additionalContext`、`systemMessage` 和纯 stdout）上限为 10,000 字符。** 超过此限制的输出会被保存到文件，并替换为预览和文件路径，处理方式与大型工具结果相同。

JSON 对象支持三类字段：

* **通用字段**（如 `continue`）在所有事件中生效。下表列出了这些字段。
* **顶层 `decision` 和 `reason`** 被部分事件用于阻止操作或提供反馈。
* **`hookSpecificOutput`** 是一个嵌套对象，用于需要更丰富控制的事件。它需要一个 `hookEventName` 字段设置为事件名称。

| 字段 | 默认值 | 说明 |
| :--- | :--- | :--- |
| `continue` | `true` | 设为 `false` 时，Claude 在 Hook 运行后完全停止处理。优先级高于任何事件专属的决策字段 |
| `stopReason` | 无 | `continue` 为 `false` 时向用户显示的消息。不会展示给 Claude |
| `suppressOutput` | `false` | 设为 `true` 时，隐藏 Hook 的 stdout 使其不出现在对话记录中。stdout 仍会出现在调试日志中 |
| `systemMessage` | 无 | 向用户显示的警告消息 |
| `terminalSequence` | 无 | Claude Code 代为发送的终端转义序列，如桌面通知、窗口标题或响铃。仅允许 OSC `0`/`1`/`2`/`9`/`99`/`777` 和 BEL。如果值包含白名单之外的内容，该字段会被忽略。请使用此字段代替写入 `/dev/tty`（Hook 中不可用） |

要让 Claude 完全停止（不论事件类型）：

```json theme={null}
{ "continue": false, "stopReason": "Build failed, fix errors before continuing" }
```

#### 发送终端通知

**`terminalSequence` 字段需要 Claude Code v2.1.141 或更高版本。**

Hook 运行时没有控制终端，因此直接向 `/dev/tty` 写入转义序列会失败。应在 `terminalSequence` 字段中返回转义序列，由 Claude Code 通过自身的终端写入通道代为发送。这种方式无竞态条件，在 tmux 和 GNU screen 中正常工作，在没有 `/dev/tty` 的 Windows 上也正常工作。

该字段接受一个或多个白名单转义序列组成的字符串：

* OSC `0`、`1`、`2`：窗口和图标标题
* OSC `9`：iTerm2、ConEmu、Windows Terminal 和 WezTerm 通知，包括 `9;4` 任务栏进度
* OSC `99`：Kitty 通知
* OSC `777`：urxvt、Ghostty 和 Warp 通知
* 裸 BEL

序列可以用 BEL 或 ST 终止。白名单之外的任何内容，包括 CSI 光标和颜色序列、OSC 调色板序列、OSC 8 超链接、OSC 52 剪贴板写入和 OSC 1337，都会被拒绝并导致该字段被忽略。

下面的示例在 `Notification` Hook 中触发桌面通知。转义序列使用 `printf` 八进制转义构建，控制字节不会出现在 shell 命令行上；`jq -n --arg` 构建 JSON 输出，确保通知消息中的引号、反斜杠和换行符被正确转义：

```bash theme={null}
#!/bin/bash
# Notification hook: ping the desktop when Claude Code needs attention.
input=$(cat)
title="Claude Code"
body=$(jq -r '.message // "Needs your attention"' <<<"$input")
seq=$(printf '\033]777;notify;%s;%s\007' "$title" "$body")
jq -nc --arg seq "$seq" '{terminalSequence: $seq}'
```

`{ "terminalSequence": "..." }` 的结构在任何 shell 或语言中都相同。在 Windows 上，用 PowerShell 或脚本构建转义字符串，输出相同的 JSON 对象即可。

> **注意：** `terminalSequence` 是此前直接向 `/dev/tty` 写入转义序列的 Hook 的官方替代方案。白名单限制为不会移动光标或改变颜色的序列，因此 Hook 永远不会破坏屏幕上的提示符。

#### 为 Claude 添加上下文

**`additionalContext` 字段将 Hook 中的字符串传入 Claude 的上下文窗口。** Claude Code 会将字符串包装为系统提醒，在 Hook 触发的位置插入对话中。Claude 在下一次模型请求时读取该提醒，但它不会作为聊天消息出现在界面中。

在 `hookSpecificOutput` 中返回 `additionalContext`，同时附带事件名称：

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "This file is generated. Edit src/schema.ts and run `bun generate` instead."
  }
}
```

提醒出现的位置取决于事件：

* [SessionStart](#sessionstart)、[Setup](#setup) 和 [SubagentStart](#subagentstart)：在对话开始处，第一个提示词之前
* [UserPromptSubmit](#userpromptsubmit) 和 [UserPromptExpansion](#userpromptexpansion)：与提交的提示词并列
* [PreToolUse](#pretooluse)、[PostToolUse](#posttooluse)、[PostToolUseFailure](#posttoolusefailure) 和 [PostToolBatch](#posttoolbatch)：紧挨工具结果
* [Stop](#stop) 和 [SubagentStop](#subagentstop)：在轮次末尾。对话会继续，以便 Claude 能根据反馈采取行动。详见 [Stop 决策控制](#stop-decision-control)

**当多个 Hook 为同一事件返回 `additionalContext` 时，Claude 会收到所有值。** 如果某个值超过 10,000 字符，Claude Code 会将完整文本写入会话目录中的文件，并将文件路径和简短预览传递给 Claude。

使用 `additionalContext` 来传递 Claude 应该了解的环境或操作状态信息：

* **环境状态**：当前分支、部署目标或活跃的功能开关
* **条件性项目规则**：刚编辑的文件适用哪个测试命令、在此 worktree 中哪些目录是只读的
* **外部数据**：分配给你的未关闭 issue、最近的 CI 结果、从内部服务获取的内容

对于永远不会变化的指令，优先使用 [CLAUDE.md](https://code.claude.com/docs/en/memory)。它无需运行脚本即可加载，是静态项目约定的标准存放位置。

**将文本写成陈述句而非命令式的系统指令。** 例如"部署目标是 production"或"本仓库使用 `bun test`"这类写法读起来像项目信息。以带外系统命令方式表述的文本可能触发 Claude 的提示注入防御，导致 Claude 将文本展示给你而非作为上下文处理。

**一旦注入，文本会保存在会话记录中。** 对于会话中途事件（如 `PostToolUse` 或 `UserPromptSubmit`），使用 `--continue` 或 `--resume` 恢复时会重放已保存的文本而非重新运行 Hook，因此时间戳或 commit SHA 等值在恢复后会过时。`SessionStart` Hook 在恢复时会再次运行（`source` 设为 `"resume"`），因此可以刷新其上下文。

#### 决策控制

**并非所有事件都支持通过 JSON 阻止或控制行为。** 支持决策的事件各自使用不同的字段来表达决策。写 Hook 前请参考此表：

| 事件 | 决策模式 | 关键字段 |
| :--- | :--- | :--- |
| UserPromptSubmit、UserPromptExpansion、PostToolUse、PostToolUseFailure、PostToolBatch、Stop、SubagentStop、ConfigChange、PreCompact | 顶层 `decision` | `decision: "block"`、`reason`。Stop 和 SubagentStop 还接受 `hookSpecificOutput.additionalContext` 用于[继续对话的非错误反馈](#stop-decision-control) |
| TeammateIdle、TaskCreated、TaskCompleted | 退出码或 `continue: false` | 退出码 2 通过 stderr 反馈阻止操作。JSON `{"continue": false, "stopReason": "..."}` 也会完全停止队友，行为与 `Stop` Hook 一致 |
| PreToolUse | `hookSpecificOutput` | `permissionDecision`（allow/deny/ask/defer）、`permissionDecisionReason` |
| PermissionRequest | `hookSpecificOutput` | `decision.behavior`（allow/deny） |
| PermissionDenied | `hookSpecificOutput` | `retry: true` 告知模型可以重试被拒绝的工具调用 |
| WorktreeCreate | 路径返回 | 命令 Hook 在 stdout 输出路径；HTTP Hook 返回 `hookSpecificOutput.worktreePath`。Hook 失败或缺少路径则创建失败 |
| Elicitation | `hookSpecificOutput` | `action`（accept/decline/cancel）、`content`（accept 时的表单字段值） |
| ElicitationResult | `hookSpecificOutput` | `action`（accept/decline/cancel）、`content`（表单字段值覆盖） |
| MessageDisplay | `hookSpecificOutput` | `displayContent` 替换屏幕显示文本。仅影响显示：对话记录和 Claude 看到的内容保持原样 |
| SessionStart、Setup、SubagentStart | 仅上下文 | `hookSpecificOutput.additionalContext` 为 Claude 添加上下文。SessionStart 还接受 [`initialUserMessage`、`watchPaths`、`sessionTitle` 和 `reloadSkills`](#sessionstart-decision-control)。无阻止或决策控制 |
| WorktreeRemove、Notification、SessionEnd、PostCompact、InstructionsLoaded、StopFailure、CwdChanged、FileChanged | 无 | 无决策控制。仅用于日志记录或清理等副作用 |

**部分事件还支持重写内容，而不只是允许或阻止：**

* `PreToolUse`：`hookSpecificOutput` 下直接使用 `updatedInput` 可在工具运行前替换其参数。详见 [PreToolUse 决策控制](#pretooluse-decision-control)
* `PermissionRequest`：`decision` 对象内的 `updatedInput`。详见 [PermissionRequest 决策控制](#permissionrequest-decision-control)
* `PostToolUse`：`updatedToolOutput` 替换工具的返回结果。详见 [PostToolUse 决策控制](#posttooluse-decision-control)
* `UserPromptSubmit`：无法替换提示词，只能在其旁边注入 `additionalContext`

对于脱敏或转换场景，在 `PreToolUse` 拦截出站的工具输入，在 `PostToolUse` 拦截入站的工具结果。

以下是各种模式的实际示例：

**顶层 decision 模式**

适用于 `UserPromptSubmit`、`UserPromptExpansion`、`PostToolUse`、`PostToolUseFailure`、`PostToolBatch`、`Stop`、`SubagentStop`、`ConfigChange` 和 `PreCompact`。唯一的值是 `"block"`。要允许操作继续，从 JSON 中省略 `decision`，或直接退出码 0 不输出任何 JSON：

```json theme={null}
{
  "decision": "block",
  "reason": "Test suite must pass before proceeding"
}
```

**PreToolUse 模式**

使用 `hookSpecificOutput` 实现更丰富的控制：允许、拒绝或上报给用户。你还可以在工具运行前修改其输入，或为 Claude 注入额外上下文。完整选项详见 [PreToolUse 决策控制](#pretooluse-decision-control)。

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Database writes are not allowed"
  }
}
```

**PermissionRequest 模式**

使用 `hookSpecificOutput` 代替用户允许或拒绝权限请求。允许时，你还可以修改工具的输入或应用权限规则，这样用户就不会再被询问。完整选项详见 [PermissionRequest 决策控制](#permissionrequest-decision-control)。

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "allow",
      "updatedInput": {
        "command": "npm run lint"
      }
    }
  }
}
```

更多示例，包括 Bash 命令验证、提示词过滤和自动审批脚本，请参阅指南中的[可自动化场景](https://code.claude.com/docs/en/hooks-guide#what-you-can-automate)以及 [Bash 命令验证器参考实现](https://github.com/anthropics/claude-code/blob/main/examples/hooks/bash_command_validator_example.py)。
## Hook 事件

每个事件对应 Claude Code 生命周期中可以执行 Hook 的一个节点。下面各节按生命周期顺序排列：从会话初始化、经过代理循环、到会话结束。每节说明事件何时触发、支持哪些 matcher、接收的 JSON 输入，以及如何通过输出控制行为。

### SessionStart

**会话启动或恢复时触发。** 适合加载开发上下文（如现有 issue 或代码库近期变更）或设置环境变量。如果只需要静态上下文，不需要脚本，请改用 [CLAUDE.md](https://code.claude.com/docs/en/memory)。

SessionStart 在每次会话都会触发，因此 Hook 必须保持高速执行。仅支持 `type: "command"` 和 `type: "mcp_tool"` 类型的 Hook。

matcher 的值对应会话的启动方式：

| Matcher   | 触发时机                           |
| :-------- | :--------------------------------- |
| `startup` | 新会话                             |
| `resume`  | `--resume`、`--continue` 或 `/resume` |
| `clear`   | `/clear`                           |
| `compact` | 自动或手动压缩                     |

#### SessionStart 输入

除了[通用输入字段](#common-input-fields)外，SessionStart Hook 还接收 `source`，以及可选的 `model`、`agent_type` 和 `session_title`。`source` 字段表示会话的启动方式：新会话为 `"startup"`，恢复会话为 `"resume"`，`/clear` 后为 `"clear"`，压缩后为 `"compact"`。`model` 字段包含当前活跃的模型标识符。某些情况下（如 `/clear` 之后或通过对话恢复机制恢复会话时）该字段可能缺失，因此读取前应先检查字段是否存在。如果通过 `claude --agent <name>` 启动 Claude Code，`agent_type` 字段会包含代理名称。`session_title` 字段在会话已有标题时（例如通过 `--name` 或 `/rename` 设置）携带当前标题。输出 `sessionTitle` 的 Hook 可以先检查 `session_title`，以避免覆盖用户显式设置的标题。

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "SessionStart",
  "source": "startup",
  "model": "claude-sonnet-4-6"
}
```

#### SessionStart 决策控制

Hook 脚本输出到 stdout 的任何文本都会作为上下文添加给 Claude。除了所有 Hook 都可用的[JSON 输出字段](#json-output)外，还可以返回以下事件特有字段：

| 字段                 | 说明                                                                                                                                                                                                                                                                                     |
| :------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `additionalContext`  | 在对话开始时（第一条 prompt 之前）添加到 Claude 上下文中的字符串。参见[为 Claude 添加上下文](#add-context-for-claude)了解文本的传递方式和应包含的内容                                                                                                                                      |
| `initialUserMessage` | 作为会话第一条用户消息的字符串。在[非交互模式](https://code.claude.com/docs/en/headless)（`-p`）中生效，即使未提供 prompt 也会成为第一轮对话。如果提供了 prompt，则作为下一轮。与 `additionalContext` 附加到现有轮次不同，此字段会创建新的轮次                                               |
| `sessionTitle`       | 设置会话标题，效果等同于 `/rename`。可用于根据启动目录、git 分支或 worktree 名称自动命名会话。仅在 `source` 为 `"startup"` 或 `"resume"` 时生效；`"clear"` 和 `"compact"` 时被忽略                                                                                                         |
| `watchPaths`         | 绝对路径数组，用于在会话期间监控 [FileChanged](#filechanged) 事件                                                                                                                                                                                                                        |
| `reloadSkills`       | 布尔值。设为 `true` 时，Claude Code 会在 SessionStart Hook 完成后重新扫描 [skill](https://code.claude.com/docs/en/skills) 和命令目录，使 Hook 安装的 skill 从第一条 prompt 开始即可在同一会话中使用                                                                                       |

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Current branch: feat/auth-refactor\nUncommitted changes: src/auth.ts, src/login.tsx\nActive issue: #4211 Migrate to OAuth2",
    "sessionTitle": "auth-refactor"
  }
}
```

由于纯 stdout 对该事件已经可以传递到 Claude，只需加载上下文的 Hook 可以直接打印到 stdout 而无需构建 JSON。当需要将上下文与其他字段（如 `suppressOutput` 或 `sessionTitle`）组合时，使用 JSON 格式。

**`reloadSkills` 的使用场景：** SessionStart Hook 安装或更新 skill 时使用。Skill 发现通常在 SessionStart Hook 完成前就已运行，因此 Hook 写入 `~/.claude/skills/` 或 `.claude/skills/` 的文件默认要到下一次会话才可见。以下示例同步一个共享 skill 仓库并请求重新扫描：

```bash theme={null}
#!/bin/bash

git -C ~/.claude/skills/team-skills pull --quiet 2>/dev/null || \
  git clone --quiet https://git.example.com/your-org/team-skills.git ~/.claude/skills/team-skills

echo '{"hookSpecificOutput": {"hookEventName": "SessionStart", "reloadSkills": true}}'
```

#### 持久化环境变量

SessionStart Hook 可以访问 `CLAUDE_ENV_FILE` 环境变量，它提供一个文件路径，用于持久化环境变量供后续 Bash 命令使用。

要设置单个环境变量，将 `export` 语句写入 `CLAUDE_ENV_FILE`。使用追加模式（`>>`）以保留其他 Hook 设置的变量：

```bash theme={null}
#!/bin/bash

if [ -n "$CLAUDE_ENV_FILE" ]; then
  echo 'export NODE_ENV=production' >> "$CLAUDE_ENV_FILE"
  echo 'export DEBUG_LOG=true' >> "$CLAUDE_ENV_FILE"
  echo 'export PATH="$PATH:./node_modules/.bin"' >> "$CLAUDE_ENV_FILE"
fi

exit 0
```

要捕获 setup 命令对环境的全部变更，可以对比执行前后的导出变量：

```bash theme={null}
#!/bin/bash

ENV_BEFORE=$(export -p | sort)

# 运行会修改环境的 setup 命令
source ~/.nvm/nvm.sh
nvm use 20

if [ -n "$CLAUDE_ENV_FILE" ]; then
  ENV_AFTER=$(export -p | sort)
  comm -13 <(echo "$ENV_BEFORE") <(echo "$ENV_AFTER") >> "$CLAUDE_ENV_FILE"
fi

exit 0
```

写入该文件的所有变量将在会话期间 Claude Code 执行的所有后续 Bash 命令中可用。

> **注意：** `CLAUDE_ENV_FILE` 在 SessionStart、[Setup](#setup)、[CwdChanged](#cwdchanged) 和 [FileChanged](#filechanged) Hook 中可用。其他 Hook 类型无法访问此变量。

### Setup

**仅在使用 `--init-only` 启动 Claude Code 时触发，或在 print 模式（`-p`）下使用 `--init` 或 `--maintenance` 时触发。** 普通启动不会触发此事件。用于一次性的依赖安装或通过 CI 或脚本显式触发的定期清理，与普通会话启动分开。如需每次会话初始化，请改用 [SessionStart](#sessionstart)。

matcher 的值对应触发 Hook 的 CLI 标志：

| Matcher       | 触发时机                               |
| :------------ | :------------------------------------- |
| `init`        | `claude --init-only` 或 `claude -p --init` |
| `maintenance` | `claude -p --maintenance`              |

`--init-only` 会运行 Setup Hook 和带 `startup` matcher 的 `SessionStart` Hook，然后退出而不启动对话。`--init` 和 `--maintenance` 仅在与 `-p`（print 模式）结合时触发 Setup Hook；在交互式会话中这两个标志目前不会触发 Setup Hook。

**插件依赖安装模式：** 由于 Setup 并非每次启动都触发，需要安装依赖的插件不能仅依赖 Setup。实际做法是在首次使用时检查依赖是否存在、不存在则安装。例如 Hook 或 skill 检测 `${CLAUDE_PLUGIN_DATA}/node_modules` 是否存在，不存在则运行 `npm install`。参见[持久数据目录](https://code.claude.com/docs/en/plugins-reference#persistent-data-directory)了解安装依赖的存放位置。

#### Setup 输入

除了[通用输入字段](#common-input-fields)外，Setup Hook 还接收 `trigger` 字段，值为 `"init"` 或 `"maintenance"`：

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "Setup",
  "trigger": "init"
}
```

#### Setup 决策控制

**Setup Hook 不能阻断流程。** 退出码为 2 时，stderr 会显示给用户；其他非零退出码时，stderr 仅在使用 `--verbose` 启动时才显示。两种情况下执行都会继续。要将信息传入 Claude 的上下文，在 JSON 输出中返回 `additionalContext`；纯 stdout 仅写入调试日志。除了所有 Hook 都可用的[JSON 输出字段](#json-output)外，还可以返回以下事件特有字段：

| 字段                | 说明                                                              |
| :------------------ | :---------------------------------------------------------------- |
| `additionalContext` | 添加到 Claude 上下文中的字符串。多个 Hook 的值会被拼接            |

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "Setup",
    "additionalContext": "Dependencies installed: node_modules, .venv"
  }
}
```

Setup Hook 可以访问 `CLAUDE_ENV_FILE`。写入该文件的变量会持久化到会话的后续 Bash 命令中，与 [SessionStart Hook](#persist-environment-variables) 一致。仅支持 `type: "command"` 和 `type: "mcp_tool"` 类型的 Hook。

### InstructionsLoaded

**当 `CLAUDE.md` 或 `.claude/rules/*.md` 文件被加载到上下文中时触发。** 此事件在会话启动时对即时加载的文件触发，之后在文件延迟加载时再次触发——例如当 Claude 访问包含嵌套 `CLAUDE.md` 的子目录时，或带有 `paths:` frontmatter 的条件规则匹配时。此 Hook 不支持阻断或决策控制。它以异步方式运行，仅用于可观测性。

matcher 针对 `load_reason` 匹配。例如，使用 `"matcher": "session_start"` 仅对会话启动时加载的文件触发，或使用 `"matcher": "path_glob_match|nested_traversal"` 仅对延迟加载触发。

#### InstructionsLoaded 输入

除了[通用输入字段](#common-input-fields)外，InstructionsLoaded Hook 还接收以下字段：

| 字段                | 说明                                                                                                                                                              |
| :------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `file_path`         | 被加载的指令文件的绝对路径                                                                                                                                        |
| `memory_type`       | 文件的作用域：`"User"`、`"Project"`、`"Local"` 或 `"Managed"`                                                                                                     |
| `load_reason`       | 文件加载的原因：`"session_start"`、`"nested_traversal"`、`"path_glob_match"`、`"include"` 或 `"compact"`。`"compact"` 值在压缩事件后重新加载指令文件时触发          |
| `globs`             | 文件 `paths:` frontmatter 中的路径 glob 模式（如有）。仅在 `path_glob_match` 加载时存在                                                                            |
| `trigger_file_path` | 触发此加载的文件路径，用于延迟加载                                                                                                                                 |
| `parent_file_path`  | 包含此文件的父指令文件路径，用于 `include` 加载                                                                                                                    |

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../transcript.jsonl",
  "cwd": "/Users/my-project",
  "hook_event_name": "InstructionsLoaded",
  "file_path": "/Users/my-project/CLAUDE.md",
  "memory_type": "Project",
  "load_reason": "session_start"
}
```

#### InstructionsLoaded 决策控制

**InstructionsLoaded Hook 没有决策控制能力。** 它不能阻断或修改指令加载。此事件适用于审计日志、合规追踪或可观测性。

### UserPromptSubmit

**用户提交 prompt 后、Claude 处理之前触发。** 可用于根据 prompt/对话添加额外上下文、验证 prompt，或阻断特定类型的 prompt。

`UserPromptSubmit` Hook 对 `command`、`http` 和 `mcp_tool` 类型的默认超时为 30 秒，比这些类型在大多数其他事件中 600 秒的默认值短。因为此 Hook 在每条 prompt 前运行并阻塞模型处理直到完成，卡住的 Hook 会导致会话停滞。如果 Hook 需要更多时间，请在 Hook 条目中设置 `timeout` 字段。

#### UserPromptSubmit 输入

除了[通用输入字段](#common-input-fields)外，UserPromptSubmit Hook 还接收 `prompt` 字段，包含用户提交的文本。

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "UserPromptSubmit",
  "prompt": "Write a function to calculate the factorial of a number"
}
```

#### UserPromptSubmit 决策控制

**`UserPromptSubmit` Hook 可以控制用户 prompt 是否被处理，并可添加上下文。** 所有[JSON 输出字段](#json-output)均可用。

有两种方式在退出码为 0 时向对话添加上下文：

* **纯文本 stdout**：写入 stdout 的任何非 JSON 文本都会作为上下文添加
* **JSON 格式 `additionalContext`**：使用下面的 JSON 格式进行更精细的控制。`additionalContext` 字段会作为上下文添加

纯 stdout 在 transcript 中显示为 Hook 输出。`additionalContext` 字段的添加更加隐蔽。

要阻断一条 prompt，返回 `decision` 设为 `"block"` 的 JSON 对象：

| 字段                     | 说明                                                                                                           |
| :----------------------- | :------------------------------------------------------------------------------------------------------------- |
| `decision`               | `"block"` 阻止 prompt 被处理并从上下文中清除它。省略此字段则允许 prompt 继续处理                                |
| `reason`                 | 当 `decision` 为 `"block"` 时显示给用户。不会添加到上下文中                                                     |
| `additionalContext`      | 添加到 Claude 上下文中的字符串，与提交的 prompt 一同出现。参见[为 Claude 添加上下文](#add-context-for-claude)    |
| `sessionTitle`           | 设置会话标题。可用于根据 prompt 内容自动命名会话                                                                |
| `suppressOriginalPrompt` | 当 `decision` 为 `"block"` 时设为 `true`，可在显示给用户的阻断消息中隐去原始 prompt 文本                        |

```json theme={null}
{
  "decision": "block",
  "reason": "Explanation for decision",
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "My additional context here",
    "sessionTitle": "My session title"
  }
}
```

> **注意：** 简单场景不需要 JSON 格式。要添加上下文，可以在退出码为 0 时直接将纯文本打印到 stdout。需要阻断 prompt 或进行更结构化控制时才使用 JSON。

### UserPromptExpansion

**用户输入的斜杠命令展开为 prompt 后、到达 Claude 之前触发。** 可用于阻断特定命令的直接调用、为特定 skill 注入上下文，或记录用户调用了哪些命令。例如，匹配 `deploy` 的 Hook 可以在审批文件不存在时阻止 `/deploy`，或匹配 review skill 的 Hook 可以将团队的 review checklist 作为 `additionalContext` 追加。

此事件覆盖了 `PreToolUse` 无法覆盖的路径：匹配 `Skill` 工具的 `PreToolUse` Hook 仅在 Claude 调用该工具时触发，但用户直接输入 `/skillname` 会绕过 `PreToolUse`。`UserPromptExpansion` 在这条直接路径上触发。

匹配条件为 `command_name`。将 matcher 留空可对所有 prompt 类型的斜杠命令触发。

#### UserPromptExpansion 输入

除了[通用输入字段](#common-input-fields)外，UserPromptExpansion Hook 还接收 `expansion_type`、`command_name`、`command_args`、`command_source` 和原始 `prompt` 字符串。`expansion_type` 字段对于 skill 和自定义命令为 `slash_command`，对于 MCP 服务器 prompt 为 `mcp_prompt`。

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../00893aaf.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "UserPromptExpansion",
  "expansion_type": "slash_command",
  "command_name": "example-skill",
  "command_args": "arg1 arg2",
  "command_source": "plugin",
  "prompt": "/example-skill arg1 arg2"
}
```

#### UserPromptExpansion 决策控制

**`UserPromptExpansion` Hook 可以阻断展开或添加上下文。** 所有[JSON 输出字段](#json-output)均可用。

| 字段                | 说明                                                                                                          |
| :------------------ | :------------------------------------------------------------------------------------------------------------ |
| `decision`          | `"block"` 阻止斜杠命令展开。省略则允许继续                                                                    |
| `reason`            | 当 `decision` 为 `"block"` 时显示给用户                                                                        |
| `additionalContext` | 添加到 Claude 上下文中的字符串，与展开后的 prompt 一同出现。参见[为 Claude 添加上下文](#add-context-for-claude) |

```json theme={null}
{
  "decision": "block",
  "reason": "This slash command is not available",
  "hookSpecificOutput": {
    "hookEventName": "UserPromptExpansion",
    "additionalContext": "Additional context for this expansion"
  }
}
```

### MessageDisplay

**助手消息流式输出到屏幕时触发。** Claude Code 以批次方式显示消息：每当一批新完成的行准备好渲染时，Hook 运行一次并接收这些行，Claude Code 将 Hook 返回的替换文本渲染在原文位置。长消息会产生多次调用；短消息可能只产生一次。

MessageDisplay 适用于：

* 去除 markdown 以获得简洁显示
* 变换 Agent SDK 应用展示给用户的文本
* 从 Claude 的回复中脱敏 API key 或内部主机名

Claude Code 会等待 Hook 返回后才渲染每一批次，因此 Hook 必须快速执行。如果 Hook 失败或超时，Claude Code 显示原始文本。此事件的默认超时为 10 秒；如果 Hook 需要更多时间，请在 Hook 条目中设置 `timeout` 字段。

**MessageDisplay 仅影响显示：** 替换文本只改变屏幕上渲染的内容。Transcript 和 Claude 看到的内容保持原始文本不变——Claude 永远看不到替换文本，verbose 模式也显示原始内容。Hook 仅接收助手消息文本，因此工具结果和用户输入的文本不受影响。

MessageDisplay 不支持 matcher，对所有流式输出文本的助手消息触发；没有文本的消息（如仅包含工具调用的回复）不会触发。

**非交互模式行为：** 在非交互运行中（包括 Agent SDK 查询和 `claude -p`），MessageDisplay 每条助手消息仅运行一次而非每批次一次。这次单独的调用在消息完成后到达，携带完整消息文本：`index` 为 `0`，`final` 为 `true`，`delta` 包含整条消息。无论哪种模式，收集每条消息 `delta` 文本的 Hook 都会获得相同的总文本量。

#### MessageDisplay 输入

除了[通用输入字段](#common-input-fields)外，MessageDisplay Hook 还接收当前轮次和消息的标识符、本次调用在消息中的位置，以及 `delta` 中的新文本。批次边界取决于文本的流式方式，因此请使用 `index` 和 `final` 来追踪消息进度，而非假设行会以特定方式分组。

| 字段         | 说明                                                                                                                                                                                                                                                                                                                                      |
| :----------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `turn_id`    | 当前轮次的 UUID                                                                                                                                                                                                                                                                                                                           |
| `message_id` | 正在显示的助手消息的 UUID。同一消息的所有批次中保持稳定。这不是 API 的 `msg_...` ID，因此无法与 transcript 中的消息 ID 关联                                                                                                                                                                                                                 |
| `index`      | 本批次在消息中的从零开始的索引                                                                                                                                                                                                                                                                                                             |
| `final`      | 在消息的最后一个批次上为 `true`。每条消息恰好有一个 final 批次                                                                                                                                                                                                                                                                             |
| `delta`      | 自上一批次以来新完成的行，包含结尾换行符。除最后一个批次可能在行中间结束外，始终为完整行。在交互式运行中，当消息以换行符结尾时最后一个批次的 delta 为空——因此应以 `final` 而非非空 delta 作为消息结束信号。在 Agent SDK 和 `claude -p` 运行中，单次调用携带整条消息                                                                              |

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../transcript.jsonl",
  "cwd": "/Users/my-project",
  "hook_event_name": "MessageDisplay",
  "turn_id": "0c9e6a2f-7d41-4f4e-9a15-3f4f7c2b8d10",
  "message_id": "5b2a9c8e-1f63-4d8a-b7c4-9e0d2a6f1c3b",
  "index": 0,
  "final": false,
  "delta": "Here is the plan:\n"
}
```

#### MessageDisplay 输出

除了所有 Hook 都可用的[JSON 输出字段](#json-output)外，MessageDisplay Hook 可以返回 `displayContent` 来替换屏幕上的 delta：

| 字段             | 说明                                                          |
| :--------------- | :------------------------------------------------------------ |
| `displayContent` | 替代 delta 显示的文本。省略则显示原始内容                      |

**MessageDisplay Hook 没有决策控制能力。** 它不能阻断消息，也不能改变 transcript 中存储的内容或发送给 Claude 的内容。

以下示例去除 Claude 回复中的 markdown 格式以获得纯文本显示。脚本从 stdin 读取每个批次，去除 `delta` 中的粗体标记和内联代码反引号，并将结果作为 `displayContent` 返回。

<Tabs>
  <Tab title="macOS/Linux">
    在设置文件中注册该事件的 command Hook：

    ```json theme={null}
    {
      "hooks": {
        "MessageDisplay": [
          {
            "hooks": [
              {
                "type": "command",
                "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/plain-display.sh",
                "args": []
              }
            ]
          }
        ]
      }
    }
    ```

    将以下脚本保存为项目中的 `.claude/hooks/plain-display.sh` 并通过 `chmod +x` 添加可执行权限：

    ```bash theme={null}
    #!/bin/bash
    jq '{hookSpecificOutput: {hookEventName: "MessageDisplay", displayContent: (.delta | gsub("\\*\\*"; "") | gsub("`"; ""))}}'
    ```

    脚本需要 `jq` 在 `PATH` 中可用。
  </Tab>

  <Tab title="Windows (PowerShell)">
    注册通过 PowerShell 运行脚本的 command Hook：

    ```json theme={null}
    {
      "hooks": {
        "MessageDisplay": [
          {
            "hooks": [
              {
                "type": "command",
                "command": "powershell.exe",
                "args": [
                  "-NoProfile",
                  "-ExecutionPolicy",
                  "Bypass",
                  "-File",
                  "${CLAUDE_PROJECT_DIR}/.claude/hooks/plain-display.ps1"
                ]
              }
            ]
          }
        ]
      }
    }
    ```

    `-NoProfile` 标志跳过加载 PowerShell profile 以加快 Hook 启动速度，`-ExecutionPolicy Bypass` 允许 PowerShell 运行本地脚本文件。

    将以下脚本保存为项目中的 `.claude/hooks/plain-display.ps1`：

    ```powershell theme={null}
    $batch = [Console]::In.ReadToEnd() | ConvertFrom-Json
    $text = $batch.delta -replace '\*\*', '' -replace '`', ''
    @{
      hookSpecificOutput = @{
        hookEventName = "MessageDisplay"
        displayContent = $text
      }
    } | ConvertTo-Json
    ```
  </Tab>
</Tabs>

不含 markdown 的批次会原样通过。如果脚本失败（例如缺少 `jq`），Claude Code 会显示原始文本并仅在[调试输出](#debug-hooks)中记录失败，不会在会话中显示。

### PreToolUse

**Claude 生成工具参数后、处理工具调用之前触发。** 匹配条件为工具名：`Bash`、`Edit`、`Write`、`Read`、`Glob`、`Grep`、`Agent`、`WebFetch`、`WebSearch`、`AskUserQuestion`、`ExitPlanMode`，以及任何 [MCP 工具名](#match-mcp-tools)。

使用 [PreToolUse 决策控制](#pretooluse-decision-control)来允许、拒绝、询问或延迟工具调用。

#### PreToolUse 输入

除了[通用输入字段](#common-input-fields)外，PreToolUse Hook 还接收 `tool_name`、`tool_input` 和 `tool_use_id`。`tool_input` 的字段取决于具体工具：

##### Bash

**执行 shell 命令。**

| 字段                | 类型    | 示例               | 说明                                  |
| :------------------ | :------ | :----------------- | :------------------------------------ |
| `command`           | string  | `"npm test"`       | 要执行的 shell 命令                   |
| `description`       | string  | `"Run test suite"` | 命令用途的可选描述                    |
| `timeout`           | number  | `120000`           | 可选超时时间（毫秒）                  |
| `run_in_background` | boolean | `false`            | 是否在后台运行命令                    |

##### Write

**创建或覆盖文件。**

| 字段        | 类型   | 示例                  | 说明                       |
| :---------- | :----- | :-------------------- | :------------------------- |
| `file_path` | string | `"/path/to/file.txt"` | 要写入的文件的绝对路径     |
| `content`   | string | `"file content"`      | 要写入文件的内容           |

##### Edit

**替换现有文件中的字符串。**

| 字段          | 类型    | 示例                  | 说明                       |
| :------------ | :------ | :-------------------- | :------------------------- |
| `file_path`   | string  | `"/path/to/file.txt"` | 要编辑的文件的绝对路径     |
| `old_string`  | string  | `"original text"`     | 要查找并替换的文本         |
| `new_string`  | string  | `"replacement text"`  | 替换后的文本               |
| `replace_all` | boolean | `false`               | 是否替换所有匹配项         |

##### Read

**读取文件内容。**

| 字段        | 类型   | 示例                  | 说明                               |
| :---------- | :----- | :-------------------- | :--------------------------------- |
| `file_path` | string | `"/path/to/file.txt"` | 要读取的文件的绝对路径             |
| `offset`    | number | `10`                  | 可选的起始行号                     |
| `limit`     | number | `50`                  | 可选的读取行数                     |

##### Glob

**按 glob 模式查找文件。**

| 字段      | 类型   | 示例             | 说明                                                               |
| :-------- | :----- | :--------------- | :----------------------------------------------------------------- |
| `pattern` | string | `"**/*.ts"`      | 用于匹配文件的 glob 模式                                           |
| `path`    | string | `"/path/to/dir"` | 可选的搜索目录。默认为当前工作目录                                  |

##### Grep

**使用正则表达式搜索文件内容。**

| 字段          | 类型    | 示例             | 说明                                                                          |
| :------------ | :------ | :--------------- | :---------------------------------------------------------------------------- |
| `pattern`     | string  | `"TODO.*fix"`    | 要搜索的正则表达式模式                                                        |
| `path`        | string  | `"/path/to/dir"` | 可选的搜索文件或目录                                                          |
| `glob`        | string  | `"*.ts"`         | 可选的文件过滤 glob 模式                                                      |
| `output_mode` | string  | `"content"`      | `"content"`、`"files_with_matches"` 或 `"count"`。默认为 `"files_with_matches"` |
| `-i`          | boolean | `true`           | 不区分大小写搜索                                                              |
| `multiline`   | boolean | `false`          | 启用多行匹配                                                                  |

##### WebFetch

**获取并处理网页内容。**

| 字段     | 类型   | 示例                          | 说明                         |
| :------- | :----- | :---------------------------- | :--------------------------- |
| `url`    | string | `"https://example.com/api"`   | 要获取内容的 URL             |
| `prompt` | string | `"Extract the API endpoints"` | 对获取内容运行的 prompt      |

##### WebSearch

**搜索网页。**

| 字段              | 类型   | 示例                           | 说明                                      |
| :---------------- | :----- | :----------------------------- | :---------------------------------------- |
| `query`           | string | `"react hooks best practices"` | 搜索查询                                  |
| `allowed_domains` | array  | `["docs.example.com"]`         | 可选：仅包含这些域名的结果                |
| `blocked_domains` | array  | `["spam.example.com"]`         | 可选：排除这些域名的结果                  |

##### Agent

**创建[子代理](https://code.claude.com/docs/en/sub-agents)。**

| 字段            | 类型   | 示例                       | 说明                                 |
| :-------------- | :----- | :------------------------- | :----------------------------------- |
| `prompt`        | string | `"Find all API endpoints"` | 代理要执行的任务                     |
| `description`   | string | `"Find API endpoints"`     | 任务的简短描述                       |
| `subagent_type` | string | `"Explore"`                | 要使用的专用代理类型                 |
| `model`         | string | `"sonnet"`                 | 可选的模型别名，用于覆盖默认值       |

**PostToolUse 中的 Agent 响应：** 在 `PostToolUse` 中，已完成 Agent 调用的 `tool_response` 携带子代理的最终文本和用量遥测数据。从 Hook 中读取这些字段可记录每个子代理的成本：

| 字段                | 类型   | 示例                                                  | 说明                                                                                                                           |
| :------------------ | :----- | :---------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------- |
| `status`            | string | `"completed"`                                         | 同步调用为 `"completed"`，`run_in_background: true` 时为 `"async_launched"`                                                     |
| `agentId`           | string | `"a4d2c8f1e0b3a297"`                                  | 子代理运行的标识符                                                                                                              |
| `content`           | array  | `[{"type": "text", "text": "Found 12 endpoints..."}]` | 子代理的最终文本块                                                                                                              |
| `resolvedModel`     | string | `"claude-sonnet-4-5"`                                 | 子代理实际运行的模型，可能与请求的模型不同。需要 Claude Code v2.1.174 或更高版本                                                  |
| `totalTokens`       | number | `12450`                                               | 子代理所有轮次的总计费 token 数                                                                                                  |
| `totalDurationMs`   | number | `48211`                                               | 子代理运行的实际耗时（毫秒）                                                                                                     |
| `totalToolUseCount` | number | `7`                                                   | 子代理的工具调用次数                                                                                                             |
| `usage`             | object | `{"input_tokens": 8320, ...}`                         | 按类型细分的 token 用量：`input_tokens`、`output_tokens`、`cache_creation_input_tokens`、`cache_read_input_tokens`               |

对于 `run_in_background: true` 的调用，工具在启动子代理后立即返回，因此 `tool_response` 不携带用量字段。它包含 `status: "async_launched"`、`agentId`、`description`、`prompt`、`outputFile` 和 `resolvedModel`。

`resolvedModel` 字段表示子代理实际运行的模型，可能与 `tool_input` 中的 `model` 值不同（例如当 `availableModels` 或其他覆盖规则生效时）。需要 Claude Code v2.1.174 或更高版本。

<a id="askuserquestion" />

##### AskUserQuestion

**向用户提出一到四个多选问题。**

| 字段        | 类型   | 示例                                                                                                               | 说明                                                                                                                                                                                     |
| :---------- | :----- | :----------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `questions` | array  | `[{"question": "Which framework?", "header": "Framework", "options": [{"label": "React"}], "multiSelect": false}]` | 要展示的问题，每个包含 `question` 字符串、短 `header`、`options` 数组和可选的 `multiSelect` 标志                                                                                          |
| `answers`   | object | `{"Which framework?": "React"}`                                                                                    | 可选。将问题文本映射到所选选项标签。多选答案用逗号连接标签。Claude 不设置此字段；通过 `updatedInput` 提供它以程序化方式回答                                                                 |

##### ExitPlanMode

**展示计划并在 Claude 退出[计划模式](https://code.claude.com/docs/en/permission-modes#analyze-before-you-edit-with-plan-mode)前请求用户批准。** Claude 在调用工具前将计划写入磁盘文件，因此模型生成的 `tool_input` 只携带 `allowedPrompts`。Claude Code 在将输入传递给 Hook 前注入计划内容和文件路径。

| 字段             | 类型   | 示例                                        | 说明                                                                                                                                            |
| :--------------- | :----- | :------------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------- |
| `plan`           | string | `"## Refactor auth\n1. Extract..."`         | Markdown 格式的计划内容。从磁盘计划文件注入                                                                                                      |
| `planFilePath`   | string | `"/Users/.../plans/refactor-auth.md"`       | 计划文件的路径。已注入                                                                                                                           |
| `allowedPrompts` | array  | `[{"tool": "Bash", "prompt": "run tests"}]` | 可选。Claude 请求的基于 prompt 的权限以实施计划，每个包含 `tool` 名称和描述操作类别的 `prompt`                                                     |

在 `PostToolUse` 中，`tool_response` 是一个包含 `plan` 和 `filePath` 字段（承载已批准的计划）的对象，加上内部状态标志。读取 `tool_response.plan` 获取计划内容，而非从磁盘重新读取文件。

#### PreToolUse 决策控制

**`PreToolUse` Hook 可以控制工具调用是否继续执行。** 与其他使用顶层 `decision` 字段的 Hook 不同，PreToolUse 在 `hookSpecificOutput` 对象内返回决策。这赋予它更丰富的控制能力：四种结果（允许、拒绝、询问或延迟）加上在执行前修改工具输入的能力。

| 字段                       | 说明                                                                                                                                                                                                                                                                                   |
| :------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `permissionDecision`       | `"allow"` 跳过权限提示。`"deny"` 阻止工具调用。`"ask"` 提示用户确认。`"defer"` 优雅退出以便工具稍后恢复。[拒绝和询问规则](https://code.claude.com/docs/en/permissions#manage-permissions)仍然会被评估，不受 Hook 返回值影响                                                               |
| `permissionDecisionReason` | 对于 `"allow"` 和 `"ask"`，显示给用户但不显示给 Claude。对于 `"deny"`，显示给 Claude。对于 `"defer"`，被忽略                                                                                                                                                                            |
| `updatedInput`             | 在执行前修改工具的输入参数。替换整个输入对象，因此需将未修改的字段也包含在内。可与 `"allow"` 结合自动批准，或与 `"ask"` 结合将修改后的输入展示给用户。对于 `"defer"`，被忽略                                                                                                               |
| `additionalContext`        | 添加到 Claude 上下文中的字符串，与工具结果一同出现。当 `permissionDecision` 为 `"defer"` 时被忽略。参见[为 Claude 添加上下文](#add-context-for-claude)                                                                                                                                   |

**多个 Hook 的决策优先级：** 当多个 PreToolUse Hook 返回不同决策时，优先级为 `deny` > `defer` > `ask` > `allow`。

**Hook 来源标签：** 当 Hook 返回 `"ask"` 时，显示给用户的权限提示包含标识 Hook 来源的标签，例如 `[User]`、`[Project]`、`[Plugin]` 或 `[Local]`。这帮助用户了解哪个配置源正在请求确认。

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "My reason here",
    "updatedInput": {
      "field_to_modify": "new value"
    },
    "additionalContext": "Current environment: production. Proceed with caution."
  }
}
```

**`AskUserQuestion` 和 `ExitPlanMode` 的特殊处理：** 这两个工具需要用户交互，在[非交互模式](https://code.claude.com/docs/en/headless)（`-p` 标志）下通常会阻塞。返回 `permissionDecision: "allow"` 并带上 `updatedInput` 可满足此要求：Hook 从 stdin 读取工具输入，通过你自己的 UI 收集答案，并通过 `updatedInput` 返回答案使工具无需提示即可运行。仅返回 `"allow"` 不够。对于 `AskUserQuestion`，需要回传原始 `questions` 数组并添加 [`answers`](#askuserquestion) 对象，将每个问题文本映射到所选答案。

> **注意：** PreToolUse 之前使用顶层的 `decision` 和 `reason` 字段，但这些已废弃。请改用 `hookSpecificOutput.permissionDecision` 和 `hookSpecificOutput.permissionDecisionReason`。废弃的值 `"approve"` 和 `"block"` 分别映射到 `"allow"` 和 `"deny"`。PostToolUse 和 Stop 等其他事件继续使用顶层 `decision` 和 `reason` 作为当前格式。

#### 延迟工具调用以供后续恢复

**`"defer"` 适用于将 `claude -p` 作为子进程运行并读取其 JSON 输出的集成**，例如 Agent SDK 应用或基于 Claude Code 构建的自定义 UI。它允许调用进程在工具调用处暂停 Claude、通过自己的界面收集输入，然后从中断处恢复。Claude Code 仅在[非交互模式](https://code.claude.com/docs/en/headless)（`-p` 标志）下接受此值。在交互式会话中，它会记录警告并忽略 Hook 结果。

> **注意：** `defer` 值需要 Claude Code v2.1.89 或更高版本。早期版本不识别该值，工具将通过正常权限流程继续执行。

**`AskUserQuestion` 是典型场景：** Claude 想向用户提问，但没有终端可以回答。完整交互流程如下：

1. Claude 调用 `AskUserQuestion`。`PreToolUse` Hook 触发。
2. Hook 返回 `permissionDecision: "defer"`。工具不执行。进程以 `stop_reason: "tool_deferred"` 退出，待处理的工具调用保留在 transcript 中。
3. 调用进程从 SDK 结果中读取 `deferred_tool_use`，在自己的 UI 中展示问题并等待答案。
4. 调用进程运行 `claude -p --resume <session-id>`。同一个工具调用再次触发 `PreToolUse`。
5. Hook 返回 `permissionDecision: "allow"` 并在 `updatedInput` 中附带答案。工具执行，Claude 继续。

`deferred_tool_use` 字段携带工具的 `id`、`name` 和 `input`。`input` 是 Claude 为工具调用生成的参数，在执行前被捕获：

```json theme={null}
{
  "type": "result",
  "subtype": "success",
  "stop_reason": "tool_deferred",
  "session_id": "abc123",
  "deferred_tool_use": {
    "id": "toolu_01abc",
    "name": "AskUserQuestion",
    "input": { "questions": [{ "question": "Which framework?", "header": "Framework", "options": [{"label": "React"}, {"label": "Vue"}], "multiSelect": false }] }
  }
}
```

**没有超时或重试限制。** 会话保留在磁盘上直到你恢复它，受 [`cleanupPeriodDays`](https://code.claude.com/docs/en/settings#available-settings) 保留策略限制（默认 30 天后删除会话文件）。如果恢复时答案尚未就绪，Hook 可以再次返回 `"defer"`，进程以相同方式退出。调用进程通过最终从 Hook 返回 `"allow"` 或 `"deny"` 来控制何时终止循环。

**`"defer"` 仅在 Claude 单次工具调用时生效。** 如果 Claude 同时发出多个工具调用，`"defer"` 会被忽略并附带警告，工具通过正常权限流程继续。该限制存在的原因是 resume 只能重新运行一个工具：无法在不让批次中其他调用悬而未决的情况下延迟其中一个。

**延迟工具不可用的情况：** 如果恢复时被延迟的工具已不可用，进程在 Hook 触发前以 `stop_reason: "tool_deferred_unavailable"` 和 `is_error: true` 退出。这发生在提供该工具的 MCP 服务器未在恢复的会话中连接时。`deferred_tool_use` 载荷仍会包含，以便你识别哪个工具消失了。

> **注意：** `--resume` 会恢复工具延迟时的权限模式，因此无需再次传递 `--permission-mode`。例外是 `plan` 和 `bypassPermissions`，它们永远不会被继承。在 resume 时显式传递 `--permission-mode` 会覆盖恢复的值。

### PermissionRequest

**当向用户展示权限对话框时触发。** 使用 [PermissionRequest 决策控制](#permissionrequest-decision-control)代替用户进行允许或拒绝。

匹配条件为工具名，与 PreToolUse 相同。

#### PermissionRequest 输入

PermissionRequest Hook 接收与 PreToolUse Hook 相同的 `tool_name` 和 `tool_input` 字段，但没有 `tool_use_id`。可选的 `permission_suggestions` 数组包含用户通常在权限对话框中看到的"始终允许"选项。区别在于触发时机：PermissionRequest Hook 在权限对话框即将展示给用户时运行，而 PreToolUse Hook 在工具执行前运行，不管权限状态如何。

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "PermissionRequest",
  "tool_name": "Bash",
  "tool_input": {
    "command": "rm -rf node_modules",
    "description": "Remove node_modules directory"
  },
  "permission_suggestions": [
    {
      "type": "addRules",
      "rules": [{ "toolName": "Bash", "ruleContent": "rm -rf node_modules" }],
      "behavior": "allow",
      "destination": "localSettings"
    }
  ]
}
```

#### PermissionRequest 决策控制

**`PermissionRequest` Hook 可以允许或拒绝权限请求。** 除了所有 Hook 都可用的[JSON 输出字段](#json-output)外，Hook 脚本可以返回包含以下事件特有字段的 `decision` 对象：

| 字段                 | 说明                                                                                                                                                                                                                    |
| :------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `behavior`           | `"allow"` 授予权限，`"deny"` 拒绝权限。[拒绝和询问规则](https://code.claude.com/docs/en/permissions#manage-permissions)仍然会被评估，因此 Hook 返回 `"allow"` 不会覆盖匹配的拒绝规则                                     |
| `updatedInput`       | 仅用于 `"allow"`：在执行前修改工具的输入参数。替换整个输入对象，因此需将未修改的字段也包含在内。修改后的输入会重新接受拒绝和询问规则的评估                                                                                  |
| `updatedPermissions` | 仅用于 `"allow"`：要应用的[权限更新条目](#permission-update-entries)数组，例如添加允许规则或更改会话权限模式                                                                                                              |
| `message`            | 仅用于 `"deny"`：告诉 Claude 权限被拒绝的原因                                                                                                                                                                           |
| `interrupt`          | 仅用于 `"deny"`：设为 `true` 时停止 Claude                                                                                                                                                                              |

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "allow",
      "updatedInput": {
        "command": "npm run lint"
      }
    }
  }
}
```

#### 权限更新条目

`updatedPermissions` 输出字段和 [`permission_suggestions` 输入字段](#permissionrequest-input)都使用相同的条目对象数组。每个条目有一个 `type` 决定其他字段，以及一个 `destination` 控制变更写入位置。

| `type`              | 字段                               | 效果                                                                                                                                                                    |
| :------------------ | :--------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `addRules`          | `rules`, `behavior`, `destination` | 添加权限规则。`rules` 是 `{toolName, ruleContent?}` 对象数组。省略 `ruleContent` 则匹配整个工具。`behavior` 为 `"allow"`、`"deny"` 或 `"ask"`                             |
| `replaceRules`      | `rules`, `behavior`, `destination` | 用提供的 `rules` 替换指定 `destination` 处给定 `behavior` 的所有规则                                                                                                      |
| `removeRules`       | `rules`, `behavior`, `destination` | 移除匹配给定 `behavior` 的规则                                                                                                                                           |
| `setMode`           | `mode`, `destination`              | 更改权限模式。有效模式为 `default`、`auto`、`acceptEdits`、`dontAsk`、`bypassPermissions` 和 `plan`                                                                       |
| `addDirectories`    | `directories`, `destination`       | 添加工作目录。`directories` 是路径字符串数组                                                                                                                              |
| `removeDirectories` | `directories`, `destination`       | 移除工作目录                                                                                                                                                             |

> **注意：** `setMode` 设为 `bypassPermissions` 仅在会话启动时已有 bypass 模式可用的情况下生效：`--dangerously-skip-permissions`、`--permission-mode bypassPermissions`、`--allow-dangerously-skip-permissions`，或 settings 中 `permissions.defaultMode: "bypassPermissions"`，且该模式未被 [`permissions.disableBypassPermissionsMode`](https://code.claude.com/docs/en/permissions#managed-settings) 禁用。否则该更新为空操作。`bypassPermissions` 无论 `destination` 如何，永远不会作为 `defaultMode` 持久化。

`destination` 字段决定变更是保留在内存中还是持久化到设置文件。

| `destination`     | 写入位置                                    |
| :---------------- | :------------------------------------------ |
| `session`         | 仅在内存中，会话结束时丢弃                  |
| `localSettings`   | `.claude/settings.local.json`               |
| `projectSettings` | `.claude/settings.json`                     |
| `userSettings`    | `~/.claude/settings.json`                   |

Hook 可以将收到的 `permission_suggestions` 之一作为自己的 `updatedPermissions` 输出回传，等同于用户在对话框中选择该"始终允许"选项。

### PostToolUse

**工具成功完成后立即触发。**

匹配条件为工具名，与 PreToolUse 相同。

#### PostToolUse 输入

`PostToolUse` Hook 在工具已成功执行后触发。输入包括 `tool_input`（发送给工具的参数）和 `tool_response`（工具返回的结果）。两者的具体 schema 取决于工具。

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "PostToolUse",
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file.txt",
    "content": "file content"
  },
  "tool_response": {
    "filePath": "/path/to/file.txt",
    "success": true
  },
  "tool_use_id": "toolu_01ABC123...",
  "duration_ms": 12
}
```

| 字段          | 说明                                                                                                  |
| :------------ | :---------------------------------------------------------------------------------------------------- |
| `duration_ms` | 可选。工具执行时间（毫秒）。不包含权限提示和 PreToolUse Hook 花费的时间                                |

#### PostToolUse 决策控制

**`PostToolUse` Hook 可以在工具执行后向 Claude 提供反馈。** 除了所有 Hook 都可用的[JSON 输出字段](#json-output)外，Hook 脚本可以返回以下事件特有字段：

| 字段                   | 说明                                                                                                                       |
| :--------------------- | :------------------------------------------------------------------------------------------------------------------------- |
| `decision`             | `"block"` 在工具结果旁边添加 `reason`。Claude 仍然能看到原始输出；要替换它，使用 `updatedToolOutput`                        |
| `reason`               | 当 `decision` 为 `"block"` 时显示给 Claude 的说明                                                                           |
| `additionalContext`    | 添加到 Claude 上下文中的字符串，与工具结果一同出现。参见[为 Claude 添加上下文](#add-context-for-claude)                      |
| `updatedToolOutput`    | 在发送给 Claude 之前替换工具的输出。值必须匹配工具的输出结构                                                                 |
| `updatedMCPToolOutput` | 仅替换 [MCP 工具](#match-mcp-tools)的输出。建议使用 `updatedToolOutput`，它适用于所有工具                                    |

以下示例替换 `Bash` 调用的输出。替换值匹配 `Bash` 工具的输出结构：

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "Additional information for Claude",
    "updatedToolOutput": {
      "stdout": "[redacted]",
      "stderr": "",
      "interrupted": false,
      "isImage": false
    }
  }
}
```

> **警告：** `updatedToolOutput` 只改变 Claude 看到的内容。Hook 触发时工具已经执行完毕，因此任何已写入的文件、已执行的命令或已发送的网络请求都已生效。遥测数据（如 OpenTelemetry 工具 span 和分析事件）也会在 Hook 运行前捕获原始输出。要在工具运行前阻止或修改工具调用，请改用 [PreToolUse](#pretooluse) Hook。
>
> 替换值必须匹配工具的输出结构。内置工具返回结构化对象而非纯字符串。例如 `Bash` 返回包含 `stdout`、`stderr`、`interrupted` 和 `isImage` 字段的对象。对于内置工具，不匹配输出 schema 的值会被忽略，使用原始输出。MCP 工具输出直接透传，不做 schema 验证。剥除 Claude 需要的错误详情可能导致它在错误假设上继续执行。

### PostToolUseFailure

**工具执行失败时触发。** 此事件在工具调用抛出错误或返回失败结果时触发。用于记录失败、发送告警，或向 Claude 提供纠正反馈。

匹配条件为工具名，与 PreToolUse 相同。

#### PostToolUseFailure 输入

PostToolUseFailure Hook 接收与 PostToolUse 相同的 `tool_name` 和 `tool_input` 字段，以及作为顶层字段的错误信息：

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "PostToolUseFailure",
  "tool_name": "Bash",
  "tool_input": {
    "command": "npm test",
    "description": "Run test suite"
  },
  "tool_use_id": "toolu_01ABC123...",
  "error": "Command exited with non-zero status code 1",
  "is_interrupt": false,
  "duration_ms": 4187
}
```

| 字段           | 说明                                                                                                  |
| :------------- | :---------------------------------------------------------------------------------------------------- |
| `error`        | 描述出错原因的字符串                                                                                  |
| `is_interrupt` | 可选布尔值，指示失败是否由用户中断引起                                                                |
| `duration_ms`  | 可选。工具执行时间（毫秒）。不包含权限提示和 PreToolUse Hook 花费的时间                                |

#### PostToolUseFailure 决策控制

**`PostToolUseFailure` Hook 可以在工具失败后向 Claude 提供上下文。** 除了所有 Hook 都可用的[JSON 输出字段](#json-output)外，Hook 脚本可以返回以下事件特有字段：

| 字段                | 说明                                                                                                |
| :------------------ | :-------------------------------------------------------------------------------------------------- |
| `additionalContext` | 添加到 Claude 上下文中的字符串，与错误信息一同出现。参见[为 Claude 添加上下文](#add-context-for-claude) |

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUseFailure",
    "additionalContext": "Additional information about the failure for Claude"
  }
}
```

### PostToolBatch
**PostToolBatch 在一个批次中所有工具调用完成后、Claude Code 向模型发送下一次请求前触发，每批只触发一次。** `PostToolUse` 针对每个工具各触发一次，并行调用时会并发触发。`PostToolBatch` 则对整个批次只触发一次，适合注入依赖于工具组合结果的上下文。该事件不支持 matcher。

#### PostToolBatch 输入

除了[通用输入字段](#common-input-fields)之外，PostToolBatch 钩子还会收到 `tool_calls` 数组，描述批次中的每个工具调用：

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "PostToolBatch",
  "tool_calls": [
    {
      "tool_name": "Read",
      "tool_input": {"file_path": "/.../ledger/accounts.py"},
      "tool_use_id": "toolu_01...",
      "tool_response": "     1\tfrom __future__ import annotations\n     2\t..."
    },
    {
      "tool_name": "Read",
      "tool_input": {"file_path": "/.../ledger/transactions.py"},
      "tool_use_id": "toolu_02...",
      "tool_response": "     1\tfrom __future__ import annotations\n     2\t..."
    }
  ]
}
```

**`tool_response` 包含模型在对应 `tool_result` 块中看到的内容。** 值为序列化字符串或 content-block 数组，与工具原始输出一致。对于 `Read`，这意味着带行号前缀的文本而非原始文件内容。响应可能很大，请只解析你需要的字段。

> **注意：** `tool_response` 的结构与 `PostToolUse` 不同。`PostToolUse` 传递的是工具的结构化 `Output` 对象（如 `Write` 的 `{filePath: "...", success: true}`）；`PostToolBatch` 传递的则是模型实际看到的序列化 `tool_result` 内容。

#### PostToolBatch 决策控制

**PostToolBatch 钩子可以为 Claude 注入上下文。** 除了所有钩子通用的 [JSON 输出字段](#json-output)外，你的钩子脚本还可以返回以下事件专属字段：

| 字段 | 说明 |
| :--- | :--- |
| `additionalContext` | 在下一次模型调用前注入一次的上下文字符串。详见[为 Claude 添加上下文](#add-context-for-claude)，了解传递方式、内容建议以及恢复会话时的处理逻辑 |

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolBatch",
    "additionalContext": "These files are part of the ledger module. Run pytest before marking the task complete."
  }
}
```

**返回 `decision: "block"` 或 `continue: false` 会在下一次模型调用前停止代理循环。**

### PermissionDenied

**当 [auto 模式](https://code.claude.com/docs/en/permission-modes#eliminate-prompts-with-auto-mode)分类器拒绝某个工具调用时触发。** 该钩子仅在 auto 模式下触发：手动拒绝权限对话框、`PreToolUse` 钩子阻止调用、或 `deny` 规则命中时均不会触发。可用于记录分类器拒绝日志、调整配置，或告知模型可以重试该工具调用。

匹配工具名称，值与 PreToolUse 相同。

#### PermissionDenied 输入

除[通用输入字段](#common-input-fields)外，PermissionDenied 钩子还接收 `tool_name`、`tool_input`、`tool_use_id` 和 `reason`。

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "auto",
  "hook_event_name": "PermissionDenied",
  "tool_name": "Bash",
  "tool_input": {
    "command": "rm -rf /tmp/build",
    "description": "Clean build directory"
  },
  "tool_use_id": "toolu_01ABC123...",
  "reason": "Auto mode denied: command targets a path outside the project"
}
```

| 字段 | 说明 |
| :--- | :--- |
| `reason` | 分类器给出的拒绝原因 |

#### PermissionDenied 决策控制

**PermissionDenied 钩子可以告知模型允许重试被拒绝的工具调用。** 返回一个 JSON 对象，将 `hookSpecificOutput.retry` 设为 `true`：

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionDenied",
    "retry": true
  }
}
```

**当 `retry` 为 `true` 时，Claude Code 会向对话中添加一条消息告知模型可以重试。** 拒绝本身不会被撤销。如果钩子未返回 JSON 或返回 `retry: false`，拒绝生效，模型收到原始拒绝消息。

### Notification

**当 Claude Code 发送通知时触发。** 匹配通知类型：`permission_prompt`、`idle_prompt`、`auth_success`、`elicitation_dialog`、`elicitation_complete`、`elicitation_response`。省略 matcher 则对所有通知类型触发。

可以使用不同的 matcher 对不同通知类型执行不同的处理脚本。以下配置在 Claude 需要权限审批时触发权限告警脚本，在 Claude 空闲时触发另一个通知：

```json theme={null}
{
  "hooks": {
    "Notification": [
      {
        "matcher": "permission_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/permission-alert.sh"
          }
        ]
      },
      {
        "matcher": "idle_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/idle-notification.sh"
          }
        ]
      }
    ]
  }
}
```

#### Notification 输入

除[通用输入字段](#common-input-fields)外，Notification 钩子接收 `message`（通知文本）、可选的 `title`，以及指示触发类型的 `notification_type`。

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "Notification",
  "message": "Claude needs your permission",
  "title": "Permission needed",
  "notification_type": "permission_prompt"
}
```

**Notification 钩子不能阻止或修改通知。** 它们用于副作用操作（如转发通知到外部服务）。通用的 [JSON 输出字段](#json-output)（如 `systemMessage`）仍然适用。

### SubagentStart

**当通过 Agent 工具生成 Claude Code 子代理时触发。** 支持 matcher 按代理类型名称过滤。对于内置代理，类型名称如 `general-purpose`、`Explore` 或 `Plan`。对于[自定义子代理](https://code.claude.com/docs/en/sub-agents)，使用代理 frontmatter 中的 `name` 字段，而非文件名。

#### SubagentStart 输入

除[通用输入字段](#common-input-fields)外，SubagentStart 钩子接收 `agent_id`（子代理唯一标识符）和 `agent_type`（代理名称，内置如 `"general-purpose"`、`"Explore"`、`"Plan"`，或自定义代理名）。

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "SubagentStart",
  "agent_id": "agent-abc123",
  "agent_type": "Explore"
}
```

**SubagentStart 钩子不能阻止子代理创建，但可以向子代理注入上下文。** 除[通用 JSON 输出字段](#json-output)外，可返回：

| 字段 | 说明 |
| :--- | :--- |
| `additionalContext` | 在子代理对话开始时（首个 prompt 之前）添加到子代理上下文中的字符串。详见[为 Claude 添加上下文](#add-context-for-claude) |

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "SubagentStart",
    "additionalContext": "Follow security guidelines for this task"
  }
}
```

### SubagentStop

**当 Claude Code 子代理完成响应后触发。** 匹配代理类型，值与 SubagentStart 相同。

#### SubagentStop 输入

除[通用输入字段](#common-input-fields)外，SubagentStop 钩子接收 `stop_hook_active`、`agent_id`、`agent_type`、`agent_transcript_path` 和 `last_assistant_message`。`agent_type` 用于 matcher 过滤。`transcript_path` 是主会话的对话记录，`agent_transcript_path` 是子代理自身的对话记录（存储在嵌套的 `subagents/` 文件夹中）。`last_assistant_message` 包含子代理最终响应的文本内容，钩子可直接访问而无需解析对话记录文件。

SubagentStop 钩子还会接收 [Stop 输入](#stop-input)中描述的 `background_tasks` 和 `session_crons` 数组（Claude Code v2.1.145 及以上版本可用）。两个数组的作用域为父会话，而非子代理。

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "~/.claude/projects/.../abc123.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "SubagentStop",
  "stop_hook_active": false,
  "agent_id": "def456",
  "agent_type": "Explore",
  "agent_transcript_path": "~/.claude/projects/.../abc123/subagents/agent-def456.jsonl",
  "last_assistant_message": "Analysis complete. Found 3 potential issues...",
  "background_tasks": [],
  "session_crons": []
}
```

**SubagentStop 钩子使用与 [Stop 钩子](#stop-decision-control)相同的决策控制格式**，包括 `hookSpecificOutput.additionalContext`（`hookEventName` 设为 `"SubagentStop"`），用于非错误反馈以保持子代理继续运行。返回 `decision: "block"` 加 `reason` 时，子代理继续运行，`reason` 作为子代理的下一条指令传递。如需在子代理返回后向父会话注入上下文，请改用 [`PostToolUse`](#posttooluse) 钩子匹配 `Agent` 工具。

### TaskCreated

**当通过 `TaskCreate` 工具创建任务时触发。** 可用于强制命名规范、要求任务描述，或阻止创建特定任务。

当 `TaskCreated` 钩子以退出码 2 退出时，任务不会被创建，stderr 消息会作为反馈传递给模型。要直接停止 teammate 而非让其重新运行，返回 JSON `{"continue": false, "stopReason": "..."}`。TaskCreated 钩子不支持 matcher，每次都会触发。

#### TaskCreated 输入

除[通用输入字段](#common-input-fields)外，TaskCreated 钩子接收 `task_id`、`task_subject`，以及可选的 `task_description`、`teammate_name` 和 `team_name`。

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "TaskCreated",
  "task_id": "task-001",
  "task_subject": "Implement user authentication",
  "task_description": "Add login and signup endpoints",
  "teammate_name": "implementer",
  "team_name": "session-a1b2c3d4"
}
```

| 字段 | 说明 |
| :--- | :--- |
| `task_id` | 正在创建的任务标识符 |
| `task_subject` | 任务标题 |
| `task_description` | 任务的详细描述。可能为空 |
| `teammate_name` | 创建任务的 teammate 名称。可能为空 |
| `team_name` | 已废弃。会话派生的团队名称，将在未来版本中移除 |

#### TaskCreated 决策控制

TaskCreated 钩子支持两种控制任务创建的方式：

* **退出码 2**：任务不会被创建，stderr 消息作为反馈传递给模型。
* **JSON `{"continue": false, "stopReason": "..."}`**：直接停止 teammate，行为与 `Stop` 钩子一致。`stopReason` 展示给用户。

以下示例阻止标题不符合要求格式的任务：

```bash theme={null}
#!/bin/bash
INPUT=$(cat)
TASK_SUBJECT=$(echo "$INPUT" | jq -r '.task_subject')

if [[ ! "$TASK_SUBJECT" =~ ^\[TICKET-[0-9]+\] ]]; then
  echo "Task subject must start with a ticket number, e.g. '[TICKET-123] Add feature'" >&2
  exit 2
fi

exit 0
```

### TaskCompleted

**当任务被标记为完成时触发。** 有两种触发场景：任何代理通过 TaskUpdate 工具显式标记任务完成时，或 [agent team](https://code.claude.com/docs/en/agent-teams) teammate 在有进行中任务的情况下结束其回合时。可用于在任务关闭前强制质量门禁（如通过测试或 lint 检查）。

当 `TaskCompleted` 钩子以退出码 2 退出时，任务不会被标记为完成，stderr 消息作为反馈传递给模型。要直接停止 teammate 而非让其重新运行，返回 JSON `{"continue": false, "stopReason": "..."}`。TaskCompleted 钩子不支持 matcher，每次都会触发。

#### TaskCompleted 输入

除[通用输入字段](#common-input-fields)外，TaskCompleted 钩子接收 `task_id`、`task_subject`，以及可选的 `task_description`、`teammate_name` 和 `team_name`。

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "TaskCompleted",
  "task_id": "task-001",
  "task_subject": "Implement user authentication",
  "task_description": "Add login and signup endpoints",
  "teammate_name": "implementer",
  "team_name": "session-a1b2c3d4"
}
```

| 字段 | 说明 |
| :--- | :--- |
| `task_id` | 正在完成的任务标识符 |
| `task_subject` | 任务标题 |
| `task_description` | 任务的详细描述。可能为空 |
| `teammate_name` | 完成任务的 teammate 名称。可能为空 |
| `team_name` | 已废弃。会话派生的团队名称，将在未来版本中移除 |

#### TaskCompleted 决策控制

TaskCompleted 钩子支持两种控制任务完成的方式：

* **退出码 2**：任务不会被标记为完成，stderr 消息作为反馈传递给模型。
* **JSON `{"continue": false, "stopReason": "..."}`**：直接停止 teammate，行为与 `Stop` 钩子一致。`stopReason` 展示给用户。

以下示例在任务完成前运行测试，测试失败时阻止完成：

```bash theme={null}
#!/bin/bash
INPUT=$(cat)
TASK_SUBJECT=$(echo "$INPUT" | jq -r '.task_subject')

# Run the test suite
if ! npm test 2>&1; then
  echo "Tests not passing. Fix failing tests before completing: $TASK_SUBJECT" >&2
  exit 2
fi

exit 0
```

### Stop

**当主 Claude Code 代理完成响应后触发。** 用户中断导致的停止不会触发此钩子。API 错误会触发 [StopFailure](#stopfailure)。

> **提示：** [`/goal`](https://code.claude.com/docs/en/goal) 命令是会话级 prompt 型 Stop 钩子的内置快捷方式。当你想让 Claude 持续工作直到满足某个条件时，无需编写钩子配置，直接使用该命令即可。

#### Stop 输入

除[通用输入字段](#common-input-fields)外，Stop 钩子接收 `stop_hook_active`、`last_assistant_message`、`background_tasks` 和 `session_crons`。`stop_hook_active` 为 `true` 表示 Claude Code 当前正在因 stop 钩子而继续执行。请检查此值或处理对话记录，避免阻塞在永远不会满足的条件上。Claude Code 会在连续 8 次阻塞后强制覆盖钩子并结束回合。

`last_assistant_message` 字段包含 Claude 最终响应的文本内容，钩子可直接访问而无需解析对话记录文件。

`background_tasks` 和 `session_crons` 数组（Claude Code v2.1.145 及以上版本可用）帮助钩子区分"会话已完成"与"会话暂停等待后台任务唤醒"。两个数组在任务注册表可达时存在，无进行中任务或计划任务时为空。

`background_tasks` 中每个条目描述一个进行中的任务，使用以下字段：

| 字段 | 说明 |
| :--- | :--- |
| `id` | 任务标识符 |
| `type` | 友好的任务类型标签，如 `shell`、`subagent`、`monitor`、`workflow`、`teammate`、`cloud session` 或 `MCP task`。每个标签标识创建该任务的 Claude Code 功能。未识别的类型回退为原始判别值 |
| `status` | 当前任务状态 |
| `description` | 自由文本描述，上限 1000 字符，超出部分以 `… [+N chars]` 标记截断 |
| `command` | Shell 命令行，上限 1000 字符。仅 `shell` 任务包含此字段 |
| `agent_type` | 子代理类型名称。仅 `subagent` 任务包含此字段 |
| `server` | MCP 服务器名称。仅 `monitor` 和 `MCP task` 任务包含此字段 |
| `tool` | MCP 工具名称。仅 `monitor` 和 `MCP task` 任务包含此字段 |
| `name` | 工作流名称。仅 `workflow` 任务包含此字段 |

`session_crons` 中每个条目描述一个会话级定时唤醒，来源包括 `CronCreate`、`ScheduleWakeup` 和 `/loop`：

| 字段 | 说明 |
| :--- | :--- |
| `id` | Cron 任务标识符 |
| `schedule` | Cron 表达式，例如 `0 9 * * 1-5` |
| `recurring` | `false` 表示一次性唤醒（schedule 编码单次触发时间），`true` 表示每次匹配都重新触发 |
| `prompt` | Cron 触发时提交的 prompt，上限 1000 字符，超出部分以相同的 `… [+N chars]` 标记截断 |

以下示例展示一个包含一个进行中 shell 任务和一个循环 cron 的 Stop 输入：

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "~/.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "Stop",
  "stop_hook_active": true,
  "last_assistant_message": "I've completed the refactoring. Here's a summary...",
  "background_tasks": [
    {
      "id": "task-001",
      "type": "shell",
      "status": "running",
      "description": "tail logs",
      "command": "tail -f /var/log/syslog"
    }
  ],
  "session_crons": [
    {
      "id": "cron-001",
      "schedule": "0 9 * * 1-5",
      "recurring": true,
      "prompt": "check the build"
    }
  ]
}
```

#### Stop 决策控制

**`Stop` 和 `SubagentStop` 钩子可以控制 Claude 是否继续。** 除所有钩子通用的 [JSON 输出字段](#json-output)外，你的钩子脚本可以返回以下事件专属字段：

| 字段 | 说明 |
| :--- | :--- |
| `decision` | `"block"` 阻止 Claude 停止。省略则允许停止 |
| `reason` | 当 `decision` 为 `"block"` 时必填。告诉 Claude 应当继续的原因 |
| `hookSpecificOutput.additionalContext` | 给 Claude 的非错误反馈。对话继续进行以便 Claude 据此行动，但与 `decision: "block"` 不同的是，它在对话记录中显示为 hook feedback 而非 hook error |

```json theme={null}
{
  "decision": "block",
  "reason": "Must be provided when Claude is blocked from stopping"
}
```

**使用 `additionalContext` 来给 Claude 提供正常指引**（如"完成前请运行测试套件"）。它通过与 `decision: "block"` 相同的循环保护机制（即 `stop_hook_active` 输入和连续 8 次继续上限）保持对话继续，但对话记录将其标记为 `Stop hook feedback` 且不显示 hook error 通知：

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "Stop",
    "additionalContext": "Please run the test suite before finishing"
  }
}
```

### StopFailure

**当回合因 API 错误结束时触发（替代 [Stop](#stop)）。** 输出和退出码会被忽略。可用于记录失败日志、发送告警，或在 Claude 因速率限制、认证问题或其他 API 错误无法完成响应时采取恢复措施。

#### StopFailure 输入

除[通用输入字段](#common-input-fields)外，StopFailure 钩子接收 `error`、可选的 `error_details` 和可选的 `last_assistant_message`。`error` 字段标识错误类型，用于 matcher 过滤。

| 字段 | 说明 |
| :--- | :--- |
| `error` | 错误类型：`rate_limit`、`overloaded`、`authentication_failed`、`oauth_org_not_allowed`、`billing_error`、`invalid_request`、`model_not_found`、`server_error`、`max_output_tokens` 或 `unknown` |
| `error_details` | 错误的附加详情（如果有） |
| `last_assistant_message` | 对话中显示的渲染后错误文本。与 `Stop` 和 `SubagentStop` 不同（那里该字段保存 Claude 的对话输出），`StopFailure` 中它包含 API 错误字符串本身，如 `"API Error: Rate limit reached"` |

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "StopFailure",
  "error": "rate_limit",
  "error_details": "429 Too Many Requests",
  "last_assistant_message": "API Error: Rate limit reached"
}
```

**StopFailure 钩子没有决策控制能力。** 仅用于通知和日志记录。

### TeammateIdle

**当 [agent team](https://code.claude.com/docs/en/agent-teams) teammate 完成回合即将进入空闲状态时触发。** 可用于在 teammate 停止工作前强制质量门禁（如要求通过 lint 检查或验证输出文件存在）。

当 `TeammateIdle` 钩子以退出码 2 退出时，teammate 收到 stderr 消息作为反馈并继续工作而非进入空闲。要直接停止 teammate 而非让其继续运行，返回 JSON `{"continue": false, "stopReason": "..."}`。TeammateIdle 钩子不支持 matcher，每次都会触发。

#### TeammateIdle 输入

除[通用输入字段](#common-input-fields)外，TeammateIdle 钩子接收 `teammate_name` 和 `team_name`。

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "TeammateIdle",
  "teammate_name": "researcher",
  "team_name": "session-a1b2c3d4"
}
```

| 字段 | 说明 |
| :--- | :--- |
| `teammate_name` | 即将进入空闲的 teammate 名称 |
| `team_name` | 已废弃。会话派生的团队名称，将在未来版本中移除 |

#### TeammateIdle 决策控制

TeammateIdle 钩子支持两种控制 teammate 行为的方式：

* **退出码 2**：teammate 收到 stderr 消息作为反馈并继续工作而非进入空闲。
* **JSON `{"continue": false, "stopReason": "..."}`**：直接停止 teammate，行为与 `Stop` 钩子一致。`stopReason` 展示给用户。

以下示例在允许 teammate 进入空闲前检查构建产物是否存在：

```bash theme={null}
#!/bin/bash

if [ ! -f "./dist/output.js" ]; then
  echo "Build artifact missing. Run the build before stopping." >&2
  exit 2
fi

exit 0
```

### ConfigChange

**当会话期间配置文件发生变更时触发。** 可用于审计设置变更、强制安全策略，或阻止未授权的配置文件修改。

ConfigChange 钩子在 settings 文件、托管策略设置和 skill 文件发生变更时触发。输入中的 `source` 字段指示哪种配置发生了变更，可选的 `file_path` 字段提供变更文件的路径。

matcher 按配置来源过滤：

| Matcher | 触发时机 |
| :--- | :--- |
| `user_settings` | `~/.claude/settings.json` 变更时 |
| `project_settings` | `.claude/settings.json` 变更时 |
| `local_settings` | `.claude/settings.local.json` 变更时 |
| `policy_settings` | 托管策略设置变更时 |
| `skills` | `.claude/skills/` 中的 skill 文件变更时 |

以下示例记录所有配置变更用于安全审计：

```json theme={null}
{
  "hooks": {
    "ConfigChange": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/audit-config-change.sh",
            "args": []
          }
        ]
      }
    ]
  }
}
```

#### ConfigChange 输入

除[通用输入字段](#common-input-fields)外，ConfigChange 钩子接收 `source` 和可选的 `file_path`。`source` 字段指示哪种配置类型发生了变更，`file_path` 提供被修改的具体文件路径。

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "ConfigChange",
  "source": "project_settings",
  "file_path": "/Users/.../my-project/.claude/settings.json"
}
```

#### ConfigChange 决策控制

**ConfigChange 钩子可以阻止配置变更生效。** 使用退出码 2 或 JSON `decision` 来阻止变更。被阻止时，新设置不会应用到正在运行的会话。

| 字段 | 说明 |
| :--- | :--- |
| `decision` | `"block"` 阻止配置变更生效。省略则允许变更 |
| `reason` | 当 `decision` 为 `"block"` 时展示给用户的说明 |

```json theme={null}
{
  "decision": "block",
  "reason": "Configuration changes to project settings require admin approval"
}
```

**`policy_settings` 变更不能被阻止。** 钩子仍会为 `policy_settings` 来源触发（可用于审计日志），但任何阻止决策都会被忽略。这确保企业托管设置始终生效。

### CwdChanged

**当会话期间工作目录发生变更时触发**（例如 Claude 执行了 `cd` 命令）。可用于响应目录变更：重新加载环境变量、激活项目专用工具链，或自动运行设置脚本。与 [FileChanged](#filechanged) 配合使用，支持 [direnv](https://direnv.net/) 等按目录管理环境的工具。

CwdChanged 钩子可以访问 `CLAUDE_ENV_FILE`。写入该文件的变量会持久化到会话后续的 Bash 命令中，与 [SessionStart 钩子](#persist-environment-variables)中的行为一致。

CwdChanged 不支持 matcher，每次目录变更都会触发。

#### CwdChanged 输入

除[通用输入字段](#common-input-fields)外，CwdChanged 钩子接收 `old_cwd` 和 `new_cwd`。

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../transcript.jsonl",
  "cwd": "/Users/my-project/src",
  "hook_event_name": "CwdChanged",
  "old_cwd": "/Users/my-project",
  "new_cwd": "/Users/my-project/src"
}
```

#### CwdChanged 输出

除所有钩子通用的 [JSON 输出字段](#json-output)外，CwdChanged 钩子可以返回 `watchPaths` 来动态设置 [FileChanged](#filechanged) 监视的文件路径：

| 字段 | 说明 |
| :--- | :--- |
| `watchPaths` | 绝对路径数组。替换当前动态监视列表（`matcher` 配置中的路径始终被监视）。返回空数组可清除动态列表，这在进入新目录时很常见 |

**CwdChanged 钩子没有决策控制能力。** 不能阻止目录变更。

### FileChanged

**当被监视的文件在磁盘上发生变更时触发。** 适用于在项目配置文件被修改时重新加载环境变量。

该事件的 `matcher` 有两个作用：

* **构建监视列表**：值按 `|` 分割，每个片段作为工作目录中的字面文件名注册。因此 `".envrc|.env"` 精确监视这两个文件。正则模式在此处无用：像 `^\.env` 这样的值会监视字面名为 `^\.env` 的文件。
* **过滤触发的钩子**：当被监视文件变更时，同一个值使用标准[matcher 规则](#matcher-patterns)对变更文件的基本名进行过滤，决定哪些钩子组运行。

FileChanged 钩子可以访问 `CLAUDE_ENV_FILE`。写入该文件的变量会持久化到会话后续的 Bash 命令中，与 [SessionStart 钩子](#persist-environment-variables)中的行为一致。

#### FileChanged 输入

除[通用输入字段](#common-input-fields)外，FileChanged 钩子接收 `file_path` 和 `event`。

| 字段 | 说明 |
| :--- | :--- |
| `file_path` | 发生变更的文件的绝对路径 |
| `event` | 发生了什么：`"change"`（文件修改）、`"add"`（文件创建）或 `"unlink"`（文件删除） |

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../transcript.jsonl",
  "cwd": "/Users/my-project",
  "hook_event_name": "FileChanged",
  "file_path": "/Users/my-project/.envrc",
  "event": "change"
}
```

#### FileChanged 输出

除所有钩子通用的 [JSON 输出字段](#json-output)外，FileChanged 钩子可以返回 `watchPaths` 来动态更新监视的文件路径：

| 字段 | 说明 |
| :--- | :--- |
| `watchPaths` | 绝对路径数组。替换当前动态监视列表（`matcher` 配置中的路径始终被监视）。当你的钩子脚本基于变更文件发现需要额外监视的文件时使用此字段 |

**FileChanged 钩子没有决策控制能力。** 不能阻止文件变更的发生。

### WorktreeCreate

**当你运行 `claude --worktree` 或[子代理使用 `isolation: "worktree"`](https://code.claude.com/docs/en/sub-agents#choose-the-subagent-scope) 时，Claude Code 使用 `git worktree` 创建隔离工作副本。** 如果你配置了 WorktreeCreate 钩子，它会替代默认的 git 行为，让你使用 SVN、Perforce 或 Mercurial 等其他版本控制系统。

由于钩子完全替代了默认行为，[`.worktreeinclude`](https://code.claude.com/docs/en/worktrees#copy-gitignored-files-into-worktrees) 不会被处理。如果需要将 `.env` 等本地配置文件复制到新 worktree，请在钩子脚本中完成。

钩子必须返回创建的 worktree 目录的绝对路径。Claude Code 使用该路径作为隔离会话的工作目录。命令钩子通过 stdout 输出路径；HTTP 钩子通过 `hookSpecificOutput.worktreePath` 返回。

以下示例创建 SVN 工作副本并输出路径供 Claude Code 使用。请将仓库 URL 替换为你自己的：

```json theme={null}
{
  "hooks": {
    "WorktreeCreate": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'NAME=$(jq -r .name); DIR=\"$HOME/.claude/worktrees/$NAME\"; svn checkout https://svn.example.com/repo/trunk \"$DIR\" >&2 && echo \"$DIR\"'"
          }
        ]
      }
    ]
  }
}
```

**该钩子从 stdin 的 JSON 输入中读取 worktree `name`，checkout 一份新副本到新目录，然后输出目录路径。** 最后一行的 `echo` 是 Claude Code 读取的 worktree 路径。将其他输出重定向到 stderr 以避免干扰路径。

#### WorktreeCreate 输入

除[通用输入字段](#common-input-fields)外，WorktreeCreate 钩子接收 `name` 字段。这是新 worktree 的 slug 标识符，由用户指定或自动生成（例如 `bold-oak-a3f2`）。

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "WorktreeCreate",
  "name": "feature-auth"
}
```

#### WorktreeCreate 输出

**WorktreeCreate 钩子不使用标准的允许/阻止决策模型。** 钩子的成功或失败决定结果。钩子必须返回创建的 worktree 目录的绝对路径：

* **命令钩子**（`type: "command"`）：在 stdout 输出路径。
* **HTTP 钩子**（`type: "http"`）：在响应体中返回 `{ "hookSpecificOutput": { "hookEventName": "WorktreeCreate", "worktreePath": "/absolute/path" } }`。

如果钩子失败或未产生路径，worktree 创建会报错失败。

### WorktreeRemove

**[WorktreeCreate](#worktreecreate) 的清理对应物。** 当 worktree 被移除时触发——可能是你退出 `--worktree` 会话并选择移除时，也可能是使用 `isolation: "worktree"` 的子代理完成时。对于基于 git 的 worktree，Claude 会通过 `git worktree remove` 自动清理。如果你为非 git 版本控制系统配置了 WorktreeCreate 钩子，请搭配 WorktreeRemove 钩子来处理清理。没有清理钩子时，worktree 目录会保留在磁盘上。

Claude Code 将 WorktreeCreate 返回的路径作为 `worktree_path` 传入钩子输入。以下示例读取该路径并删除目录：

```json theme={null}
{
  "hooks": {
    "WorktreeRemove": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'jq -r .worktree_path | xargs rm -rf'"
          }
        ]
      }
    ]
  }
}
```

#### WorktreeRemove 输入

除[通用输入字段](#common-input-fields)外，WorktreeRemove 钩子接收 `worktree_path` 字段，即被移除的 worktree 的绝对路径。

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "WorktreeRemove",
  "worktree_path": "/Users/.../my-project/.claude/worktrees/feature-auth"
}
```

**WorktreeRemove 钩子没有决策控制能力。** 不能阻止 worktree 移除，但可以执行清理任务（如移除版本控制状态或归档变更）。钩子失败仅在调试模式下记录日志。

### PreCompact

**在 Claude Code 即将执行压缩操作前触发。**

matcher 值指示压缩是手动触发还是自动触发：

| Matcher | 触发时机 |
| :--- | :--- |
| `manual` | `/compact` |
| `auto` | 上下文窗口满时自动压缩 |

**以退出码 2 退出可阻止压缩。** 对于手动 `/compact`，stderr 消息会展示给用户。也可以通过返回 JSON `"decision": "block"` 来阻止。

阻止自动压缩的效果取决于触发时机。如果压缩是在上下文限制前主动触发的，Claude Code 跳过它，对话继续不压缩。如果压缩是为了恢复 API 已返回的上下文限制错误而触发的，底层错误会浮现，当前请求失败。

#### PreCompact 输入

除[通用输入字段](#common-input-fields)外，PreCompact 钩子接收 `trigger` 和 `custom_instructions`。对于 `manual`，`custom_instructions` 包含用户传给 `/compact` 的内容。对于 `auto`，`custom_instructions` 为空。

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "PreCompact",
  "trigger": "manual",
  "custom_instructions": ""
}
```

### PostCompact

**在 Claude Code 完成压缩操作后触发。** 可用于响应新的压缩状态，例如记录生成的摘要或更新外部状态。

matcher 值与 `PreCompact` 相同：

| Matcher | 触发时机 |
| :--- | :--- |
| `manual` | `/compact` 之后 |
| `auto` | 上下文窗口满时自动压缩之后 |

#### PostCompact 输入

除[通用输入字段](#common-input-fields)外，PostCompact 钩子接收 `trigger` 和 `compact_summary`。`compact_summary` 字段包含压缩操作生成的对话摘要。

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "PostCompact",
  "trigger": "manual",
  "compact_summary": "Summary of the compacted conversation..."
}
```

**PostCompact 钩子没有决策控制能力。** 不能影响压缩结果，但可以执行后续任务。

### SessionEnd

**当 Claude Code 会话结束时触发。** 适用于清理任务、记录会话统计或保存会话状态。支持 matcher 按退出原因过滤。

输入中的 `reason` 字段指示会话结束原因：

| 原因 | 说明 |
| :--- | :--- |
| `clear` | 使用 `/clear` 命令清除会话 |
| `resume` | 通过交互式 `/resume` 切换会话 |
| `logout` | 用户退出登录 |
| `prompt_input_exit` | 用户在 prompt 输入界面可见时退出 |
| `bypass_permissions_disabled` | 绕过权限模式被禁用 |
| `other` | 其他退出原因 |

#### SessionEnd 输入

除[通用输入字段](#common-input-fields)外，SessionEnd 钩子接收 `reason` 字段，指示会话结束原因。所有值见上方[原因表格](#sessionend)。

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "SessionEnd",
  "reason": "other"
}
```

**SessionEnd 钩子没有决策控制能力。** 不能阻止会话终止，但可以执行清理任务。

**SessionEnd 钩子默认超时时间为 1.5 秒。** 适用于会话退出、`/clear` 和通过交互式 `/resume` 切换会话。如果钩子需要更多时间，在钩子配置中设置 `timeout`。总体预算会自动提升到 settings 文件中配置的最高单钩子超时值，上限 60 秒。插件提供的钩子上的超时设置不会提升预算。要显式覆盖预算，设置 `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` 环境变量（毫秒）。

```bash theme={null}
CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS=5000 claude
```

### Elicitation

**当 MCP 服务器在任务执行过程中请求用户输入时触发。** 默认情况下，Claude Code 显示交互式对话框供用户响应。钩子可以拦截此请求并以编程方式响应，完全跳过对话框。

matcher 字段匹配 MCP 服务器名称。

#### Elicitation 输入

除[通用输入字段](#common-input-fields)外，Elicitation 钩子接收 `mcp_server_name`、`message`，以及可选的 `mode`、`url`、`elicitation_id` 和 `requested_schema` 字段。

对于表单模式 elicitation（最常见的情况）：

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "Elicitation",
  "mcp_server_name": "my-mcp-server",
  "message": "Please provide your credentials",
  "mode": "form",
  "requested_schema": {
    "type": "object",
    "properties": {
      "username": { "type": "string", "title": "Username" }
    }
  }
}
```

对于 URL 模式 elicitation（基于浏览器的认证）：

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "Elicitation",
  "mcp_server_name": "my-mcp-server",
  "message": "Please authenticate",
  "mode": "url",
  "url": "https://auth.example.com/login"
}
```

#### Elicitation 输出

**要以编程方式响应而不显示对话框，返回包含 `hookSpecificOutput` 的 JSON 对象：**

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "Elicitation",
    "action": "accept",
    "content": {
      "username": "alice"
    }
  }
}
```

| 字段 | 取值 | 说明 |
| :--- | :--- | :--- |
| `action` | `accept`、`decline`、`cancel` | 接受、拒绝或取消请求 |
| `content` | object | 要提交的表单字段值。仅当 `action` 为 `accept` 时使用 |

退出码 2 拒绝 elicitation 并向用户显示 stderr。

### ElicitationResult

**当用户响应 MCP elicitation 后触发。** 钩子可以观察、修改或阻止响应在发送回 MCP 服务器之前。

matcher 字段匹配 MCP 服务器名称。

#### ElicitationResult 输入

除[通用输入字段](#common-input-fields)外，ElicitationResult 钩子接收 `mcp_server_name`、`action`，以及可选的 `mode`、`elicitation_id` 和 `content` 字段。

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "ElicitationResult",
  "mcp_server_name": "my-mcp-server",
  "action": "accept",
  "content": { "username": "alice" },
  "mode": "form",
  "elicitation_id": "elicit-123"
}
```

#### ElicitationResult 输出

**要覆盖用户的响应，返回包含 `hookSpecificOutput` 的 JSON 对象：**

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "ElicitationResult",
    "action": "decline",
    "content": {}
  }
}
```

| 字段 | 取值 | 说明 |
| :--- | :--- | :--- |
| `action` | `accept`、`decline`、`cancel` | 覆盖用户的操作 |
| `content` | object | 覆盖表单字段值。仅当 `action` 为 `accept` 时有意义 |

退出码 2 阻止响应，将有效操作变更为 `decline`。

## 基于 Prompt 的钩子

**除了命令、HTTP 和 MCP 工具钩子外，Claude Code 还支持基于 prompt 的钩子（`type: "prompt"`）和基于代理的钩子（`type: "agent"`）。** Prompt 钩子使用 LLM 来评估是否允许或阻止某个操作；Agent 钩子生成一个具有工具访问权限的代理验证器。并非所有事件都支持每种钩子类型。

支持全部五种钩子类型（`command`、`http`、`mcp_tool`、`prompt` 和 `agent`）的事件：

* `PermissionDenied`
* `PermissionRequest`
* `PostToolBatch`
* `PostToolUse`
* `PostToolUseFailure`
* `PreToolUse`
* `Stop`
* `SubagentStop`
* `TaskCompleted`
* `TaskCreated`
* `TeammateIdle`
* `UserPromptExpansion`
* `UserPromptSubmit`

仅支持 `command`、`http` 和 `mcp_tool` 钩子，不支持 `prompt` 或 `agent` 的事件：

* `ConfigChange`
* `CwdChanged`
* `Elicitation`
* `ElicitationResult`
* `FileChanged`
* `InstructionsLoaded`
* `Notification`
* `PostCompact`
* `PreCompact`
* `SessionEnd`
* `StopFailure`
* `SubagentStart`
* `WorktreeCreate`
* `WorktreeRemove`

`SessionStart` 和 `Setup` 支持 `command` 和 `mcp_tool` 钩子。不支持 `http`、`prompt` 或 `agent` 钩子。

### Prompt 钩子的工作原理

**Prompt 钩子不执行 Bash 命令，而是：**

1. 将钩子输入和你的 prompt 发送给 Claude 模型（默认使用 Haiku）
2. LLM 返回包含决策的结构化 JSON
3. Claude Code 自动处理该决策

### Prompt 钩子配置

**将 `type` 设为 `"prompt"` 并提供 `prompt` 字符串而非 `command`。** 使用 `$ARGUMENTS` 占位符将钩子的 JSON 输入数据注入 prompt 文本。Claude Code 将组合后的 prompt 和输入发送给快速 Claude 模型，该模型返回 JSON 决策。

以下 `Stop` 钩子要求 LLM 评估所有任务是否完成后才允许 Claude 停止：

```json theme={null}
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Evaluate if Claude should stop: $ARGUMENTS. Check if all tasks are complete."
          }
        ]
      }
    ]
  }
}
```

| 字段 | 必填 | 说明 |
| :--- | :--- | :--- |
| `type` | 是 | 必须为 `"prompt"` |
| `prompt` | 是 | 发送给 LLM 的 prompt 文本。使用 `$ARGUMENTS` 作为钩子输入 JSON 的占位符。如果不包含 `$ARGUMENTS`，输入 JSON 会追加到 prompt 末尾 |
| `model` | 否 | 用于评估的模型。默认为快速模型 |
| `timeout` | 否 | 超时时间（秒）。默认：30 |
| `continueOnBlock` | 否 | 当 prompt 返回 `ok: false` 时，将原因反馈给 Claude 并继续回合而非停止。默认：`false`。实现方式为在结果 `decision: "block"` 上设置 `continue: true`。各事件行为见[响应格式](#response-schema) |

### 响应格式

LLM 必须返回包含以下内容的 JSON：

```json theme={null}
{
  "ok": true | false,
  "reason": "Explanation for the decision"
}
```

| 字段 | 说明 |
| :--- | :--- |
| `ok` | `true` 表示允许。`false` 产生 `decision: "block"`。各事件行为见下文 |
| `reason` | 当 `ok` 为 `false` 时必填。用作阻止原因 |

**`ok: false` 时的行为取决于事件类型：**

* `Stop` 和 `SubagentStop`：原因作为下一条指令反馈给 Claude，回合继续
* `PreToolUse`：工具调用被拒绝，原因作为工具错误返回给 Claude，等同于命令钩子的 `permissionDecision: "deny"`
* `PostToolUse`：默认回合结束，原因在聊天中显示为警告行。设置 `continueOnBlock: true` 可将原因反馈给 Claude 并继续回合
* `PostToolBatch`、`UserPromptSubmit` 和 `UserPromptExpansion`：回合结束，原因显示为警告行。这些事件在 `decision: "block"` 时无论 `continue` 如何都会结束回合
* `PostToolUseFailure`、`TaskCreated` 和 `TaskCompleted`：原因作为工具错误返回给 Claude，类似 `PreToolUse`
* `TeammateIdle`：默认 teammate 停止，原因显示为警告行。设置 `continueOnBlock: true` 可将原因反馈给 teammate 并保持其继续工作
* `PermissionRequest`：`ok: false` 无效。要从钩子拒绝审批，使用返回 `hookSpecificOutput.decision.behavior: "deny"` 的[命令钩子](#command-hook-fields)
* `PermissionDenied`：`ok: false` 无效，因为拒绝已经发生。该事件唯一读取的输出是 `hookSpecificOutput.retry`，而 prompt 和 agent 钩子无法设置它。它们会在此事件上运行，但输出会被丢弃。使用[命令钩子](#command-hook-fields)来返回 `retry`

如果需要对任何事件进行更精细的控制，请使用带有[决策控制](#decision-control)中描述的事件专属字段的[命令钩子](#command-hook-fields)。

### 示例：多条件 Stop 钩子

**以下 `Stop` 钩子使用详细 prompt 在允许 Claude 停止前检查三个条件。** 如果 `"ok"` 为 `false`，Claude 以提供的原因作为下一条指令继续工作。`SubagentStop` 钩子使用相同格式来评估[子代理](https://code.claude.com/docs/en/sub-agents)是否应当停止：

```json theme={null}
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "You are evaluating whether Claude should stop working. Context: $ARGUMENTS\n\nAnalyze the conversation and determine if:\n1. All user-requested tasks are complete\n2. Any errors need to be addressed\n3. Follow-up work is needed\n\nRespond with JSON: {\"ok\": true} to allow stopping, or {\"ok\": false, \"reason\": \"your explanation\"} to continue working.",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

## 基于 Agent 的钩子

> **警告：** Agent 钩子为实验性功能。行为和配置可能在未来版本中变更。生产工作流建议使用[命令钩子](#command-hook-fields)。

**Agent 钩子（`type: "agent"`）类似 prompt 钩子但具有多轮工具访问能力。** 它不是单次 LLM 调用，而是生成一个子代理，该子代理可以读取文件、搜索代码、检查代码库来验证条件。Agent 钩子支持与 prompt 钩子相同的事件。

### Agent 钩子的工作原理

**当 agent 钩子触发时：**

1. Claude Code 生成一个子代理，传入你的 prompt 和钩子的 JSON 输入
2. 子代理可以使用 Read、Grep 和 Glob 等工具进行调查
3. 最多 50 轮后，子代理返回结构化的 `{ "ok": true/false }` 决策
4. Claude Code 按照与 prompt 钩子相同的方式处理该决策

**Agent 钩子适用于验证需要检查实际文件或测试输出的场景**，而不仅仅是评估钩子输入数据本身。

### Agent 钩子配置

**将 `type` 设为 `"agent"` 并提供 `prompt` 字符串。** 配置字段与 [prompt 钩子](#prompt-hook-configuration)相同，只是默认超时更长：

| 字段 | 必填 | 说明 |
| :--- | :--- | :--- |
| `type` | 是 | 必须为 `"agent"` |
| `prompt` | 是 | 描述要验证内容的 prompt。使用 `$ARGUMENTS` 作为钩子输入 JSON 的占位符 |
| `model` | 否 | 使用的模型。默认为快速模型 |
| `timeout` | 否 | 超时时间（秒）。默认：60 |

响应格式与 prompt 钩子相同：`{ "ok": true }` 表示允许，`{ "ok": false, "reason": "..." }` 表示阻止。

以下 `Stop` 钩子在允许 Claude 完成前验证所有单元测试通过：

```json theme={null}
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "agent",
            "prompt": "Verify that all unit tests pass. Run the test suite and check the results. $ARGUMENTS",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

## 后台运行钩子

**默认情况下，钩子会阻塞 Claude 的执行直到完成。** 对于耗时较长的任务（如部署、测试套件或外部 API 调用），设置 `"async": true` 可在后台运行钩子，Claude 同时继续工作。异步钩子不能阻止或控制 Claude 的行为：`decision`、`permissionDecision` 和 `continue` 等响应字段无效，因为它们本应控制的操作已经完成了。

### 配置异步钩子

**在命令钩子配置中添加 `"async": true` 即可在后台运行而不阻塞 Claude。** 该字段仅适用于 `type: "command"` 钩子。

以下钩子在每次 `Write` 工具调用后运行测试脚本。Claude 立即继续工作，而 `run-tests.sh` 最多执行 120 秒。脚本完成后，其输出在下一个对话回合中传递：

```json theme={null}
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/run-tests.sh",
            "async": true,
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

`timeout` 字段设置后台进程的最大运行时间（秒）。未指定时，异步钩子使用与同步钩子相同的 10 分钟默认值。

### 异步钩子的执行方式

**当异步钩子触发时，Claude Code 启动钩子进程并立即继续而不等待其完成。** 钩子通过 stdin 接收与同步钩子相同的 JSON 输入。

后台进程退出后，如果钩子产生了包含 `additionalContext` 字段的 JSON 响应，该内容会在下一个对话回合作为上下文传递给 Claude。`systemMessage` 字段展示给你而非 Claude。

**异步钩子完成通知默认被抑制。** 要查看它们，使用 `Ctrl+O` 启用详细模式或以 `--verbose` 启动 Claude Code。

### 示例：文件变更后运行测试

**以下钩子在 Claude 写入文件时在后台启动测试套件，测试完成后将结果报告给 Claude。** 将此脚本保存到项目中的 `.claude/hooks/run-tests-async.sh` 并使用 `chmod +x` 赋予执行权限：

```bash theme={null}
#!/bin/bash
# run-tests-async.sh

# Read hook input from stdin
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Only run tests for source files
if [[ "$FILE_PATH" != *.ts && "$FILE_PATH" != *.js ]]; then
  exit 0
fi

# Run tests and report results to Claude via additionalContext
RESULT=$(npm test 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  MSG="Tests passed after editing $FILE_PATH"
else
  MSG="Tests failed after editing $FILE_PATH: $RESULT"
fi
jq -nc --arg msg "$MSG" '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $msg}}'
```

然后在项目根目录的 `.claude/settings.json` 中添加以下配置。`async: true` 标志让 Claude 在测试运行时继续工作：

```json theme={null}
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/run-tests-async.sh",
            "args": [],
            "async": true,
            "timeout": 300
          }
        ]
      }
    ]
  }
}
```

### 限制

与同步钩子相比，异步钩子有以下约束：

* 仅 `type: "command"` 钩子支持 `async`。Prompt 钩子不能异步运行。
* 异步钩子不能阻止工具调用或返回决策。钩子完成时，触发操作已经执行完毕。
* 钩子输出在下一个对话回合传递。如果会话空闲，响应会等到下一次用户交互。例外：以退出码 2 退出的 `asyncRewake` 钩子即使在会话空闲时也会立即唤醒 Claude。
* 每次执行创建独立的后台进程。同一异步钩子的多次触发之间没有去重。

## 安全注意事项

### 免责声明

**命令钩子以你的系统用户完整权限运行。**

> **警告：** 命令钩子以你的完整用户权限执行 shell 命令。它们可以修改、删除或访问你的用户账户能访问的任何文件。在将钩子命令添加到配置前，请仔细审查和测试。

### 安全最佳实践

编写钩子时请牢记以下实践：

* **验证和清理输入**：永远不要盲目信任输入数据
* **始终引用 shell 变量**：使用 `"$VAR"` 而非 `$VAR`
* **阻止路径遍历**：检查文件路径中的 `..`
* **使用绝对路径**：为脚本指定完整路径。在 exec 形式中使用 `${CLAUDE_PROJECT_DIR}`，路径无需引号。在 shell 形式中用双引号包裹
* **跳过敏感文件**：避免 `.env`、`.git/`、密钥等

## Windows PowerShell 工具

**在 Windows 上，你可以通过在命令钩子上设置 `"shell": "powershell"` 来在 PowerShell 中运行单个钩子。** 钩子直接启动 PowerShell，因此无论是否设置了 `CLAUDE_CODE_USE_POWERSHELL_TOOL` 都能工作。Claude Code 自动检测 `pwsh.exe`（PowerShell 7+），回退到 `powershell.exe`（5.1）。

```json theme={null}
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "shell": "powershell",
            "command": "Write-Host 'File written'"
          }
        ]
      }
    ]
  }
}
```

## 调试钩子

**钩子执行详情（包括匹配了哪些钩子、退出码、完整的 stdout 和 stderr）会写入调试日志文件。** 使用 `claude --debug-file <path>` 启动 Claude Code 将日志写入已知位置，或运行 `claude --debug` 在 `~/.claude/debug/<session-id>.txt` 读取日志。`--debug` 标志不会打印到终端。

```text theme={null}
[DEBUG] Executing hooks for PostToolUse:Write
[DEBUG] Found 1 hook commands to execute
[DEBUG] Executing hook command: <Your command> with timeout 600000ms
[DEBUG] Hook command completed with status 0: <Your stdout>
```

**要获取更细粒度的钩子匹配详情，设置 `CLAUDE_CODE_DEBUG_LOG_LEVEL=verbose`** 可查看额外的日志行，如钩子 matcher 计数和查询匹配情况。

排查常见问题（如钩子未触发、Stop 钩子持续阻塞或配置错误），请参阅指南中的[限制与故障排除](https://code.claude.com/docs/en/hooks-guide#limitations-and-troubleshooting)。更广泛的诊断指引（涵盖 `/context`、`/doctor` 和设置优先级），请参阅[调试你的配置](https://code.claude.com/docs/en/debug-your-config)。
