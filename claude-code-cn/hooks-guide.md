---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】Hooks 自动化指南
description: Claude Code 的 Hooks 机制允许你在文件编辑、任务完成、需要输入等关键生命周期节点自动执行 shell 命令。本文覆盖了通知、格式化、权限控制、上下文注入等常见场景，以及 prompt/agent/HTTP 类型 hook 的进阶用法。
category: translation
tags: [claude-code, hooks, automation, translation]
refs:
  - https://code.claude.com/docs/en/hooks-guide.md
---

# 用 Hooks 实现自动化

> 当 Claude Code 编辑文件、完成任务或等待输入时，自动执行 shell 命令。可用于代码格式化、桌面通知、命令拦截、项目规则强制执行等场景。

**Hooks 是确定性的自动化机制，让你在 Claude Code 生命周期的关键节点注入自定义 shell 命令，确保特定动作必然执行，而不是依赖 LLM "选择"去做。** 你可以用 hook 强制执行项目规范、自动化重复性操作、将 Claude Code 与现有工具链集成。

如果需要依赖判断力而非确定性规则的决策，可以使用 [prompt 类型 hook](#prompt-类型-hook) 或 [agent 类型 hook](#agent-类型-hook)，它们会调用 Claude 模型来评估条件。

其他扩展 Claude Code 的方式：[skills](https://code.claude.com/docs/en/skills) 给 Claude 额外指令和可执行命令，[subagents](https://code.claude.com/docs/en/sub-agents) 在隔离上下文中运行任务，[plugins](https://code.claude.com/docs/en/plugins) 打包扩展以跨项目复用。

> [!TIP]
> 本文覆盖常见场景和入门步骤。完整的事件 schema、JSON 输入/输出格式、异步 hook 和 MCP 工具 hook 等进阶特性，参见 [Hooks 参考文档](https://code.claude.com/docs/en/hooks)。

## 配置你的第一个 Hook

**通过在 settings 文件中添加 `hooks` 配置块来创建 hook。** 以下示例创建一个桌面通知 hook，当 Claude 等待你输入时发送提醒，这样你不用一直盯着终端。

### 步骤 1：添加 hook 到 settings

打开 `~/.claude/settings.json`，添加一个 `Notification` hook。下面的示例使用 macOS 的 `osascript`；Linux 和 Windows 的命令见[获取输入通知](#获取-claude-等待输入时的通知)。

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude Code needs your attention\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

如果 settings 文件已有 `hooks` 键，把 `Notification` 作为现有事件键的兄弟节点添加，不要替换整个对象。每个事件名是 `hooks` 对象内的一个键：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write" }]
      }
    ],
    "Notification": [
      {
        "matcher": "",
        "hooks": [{ "type": "command", "command": "osascript -e 'display notification \"Claude Code needs your attention\" with title \"Claude Code\"'" }]
      }
    ]
  }
}
```

你也可以在 CLI 中描述你想要的效果，让 Claude 帮你写 hook。

### 步骤 2：验证配置

输入 `/hooks` 打开 hooks 浏览器。你会看到所有可用 hook 事件的列表，已配置 hook 的事件旁边会显示数量。选择 `Notification` 确认你的新 hook 出现在列表中。

### 步骤 3：测试 hook

按 `Esc` 返回 CLI。让 Claude 做一个需要权限的操作，然后切换离开终端。你应该会收到桌面通知。

> [!TIP]
> `/hooks` 菜单是只读的。要添加、修改或删除 hook，直接编辑 settings JSON 或让 Claude 帮你改。

## 你能自动化什么

**Hooks 让你在 Claude Code 生命周期的关键节点执行代码：编辑后格式化文件、执行前拦截命令、等待输入时发通知、会话开始时注入上下文等等。** 完整事件列表见 [Hooks 参考文档](https://code.claude.com/docs/en/hooks#hook-lifecycle)。

以下每个示例都包含现成的配置块，可直接添加到 [settings 文件](#配置-hook-的存放位置)。最常用的模式：

- [获取 Claude 等待输入时的通知](#获取-claude-等待输入时的通知)
- [编辑后自动格式化代码](#编辑后自动格式化代码)
- [阻止编辑受保护文件](#阻止编辑受保护文件)
- [压缩后重新注入上下文](#压缩后重新注入上下文)
- [审计配置变更](#审计配置变更)
- [目录或文件变更时重新加载环境](#目录或文件变更时重新加载环境)
- [自动批准特定权限弹窗](#自动批准特定权限弹窗)

关于使用独立模型审查并将结果回馈到会话的生产级示例，参见 [security-guidance 插件如何与 Claude Code 集成](https://code.claude.com/docs/en/security-guidance#how-the-plugin-integrates-with-claude-code)。

### 获取 Claude 等待输入时的通知

**当 Claude 完成工作并等待你输入时发送桌面通知，这样你可以放心切换到其他任务，不用反复查看终端。**

此 hook 使用 `Notification` 事件，当 Claude 等待输入或权限时触发。以下是各平台的原生通知命令，添加到 `~/.claude/settings.json`：

**macOS：**

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude Code needs your attention\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

> macOS 故障排除：`osascript` 通过内置的 Script Editor 应用路由通知。如果 Script Editor 没有通知权限，命令会静默失败。先在终端运行一次 `osascript -e 'display notification "test"'`，然后打开**系统设置 > 通知**，找到 **Script Editor**，开启**允许通知**。

**Linux：**

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "notify-send 'Claude Code' 'Claude Code needs your attention'"
          }
        ]
      }
    ]
  }
}
```

**Windows (PowerShell)：**

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "powershell.exe -Command \"[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms'); [System.Windows.Forms.MessageBox]::Show('Claude Code needs your attention', 'Claude Code')\""
          }
        ]
      }
    ]
  }
}
```

空 `matcher` 表示所有通知类型都触发。如需仅在特定事件时触发，设置为以下值之一：

| Matcher 值 | 触发时机 |
| :--- | :--- |
| `permission_prompt` | Claude 需要你批准一个工具调用 |
| `idle_prompt` | Claude 已完成，等待你的下一个 prompt |
| `auth_success` | 认证完成 |
| `elicitation_dialog` | MCP server 打开了一个 elicitation 表单 |
| `elicitation_complete` | MCP elicitation 表单被提交或关闭 |
| `elicitation_response` | MCP elicitation 响应被发送回 server |

输入 `/hooks` 选择 `Notification` 确认 hook 已注册。完整事件 schema 见 [Notification 参考](https://code.claude.com/docs/en/hooks#notification)。

### 编辑后自动格式化代码

**每次 Claude 编辑文件后自动运行 Prettier，保持格式一致，无需手动干预。**

此 hook 使用 `PostToolUse` 事件配合 `Edit|Write` matcher，仅在文件编辑工具之后运行。在 v2.1.191 及以后版本中，也可以写成 `Edit,Write`，因为 `|` 和 `,` 在工具名 matcher 中是等价的列表分隔符。命令通过 `jq` 提取被编辑的文件路径，然后传给 Prettier。添加到项目根目录的 `.claude/settings.json`：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write"
          }
        ]
      }
    ]
  }
}
```

> [!NOTE]
> 本文的 Bash 示例使用 `jq` 解析 JSON。安装方式：`brew install jq`（macOS）、`apt-get install jq`（Debian/Ubuntu），或见 [jq 下载页](https://jqlang.github.io/jq/download/)。

### 阻止编辑受保护文件

**防止 Claude 修改 `.env`、`package-lock.json` 或 `.git/` 下的文件。Claude 会收到说明编辑被阻止的反馈，从而调整策略。**

此示例使用独立脚本，hook 调用该脚本。脚本检查目标文件路径是否匹配受保护模式列表，匹配则以退出码 2 阻止编辑。

**步骤 1：创建 hook 脚本**

保存为 `.claude/hooks/protect-files.sh`：

```bash
#!/bin/bash
# protect-files.sh

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

PROTECTED_PATTERNS=(".env" "package-lock.json" ".git/")

for pattern in "${PROTECTED_PATTERNS[@]}"; do
  if [[ "$FILE_PATH" == *"$pattern"* ]]; then
    echo "Blocked: $FILE_PATH matches protected pattern '$pattern'" >&2
    exit 2
  fi
done

exit 0
```

**步骤 2：赋予执行权限（macOS/Linux）**

```bash
chmod +x .claude/hooks/protect-files.sh
```

**步骤 3：注册 hook**

在 `.claude/settings.json` 中添加 `PreToolUse` hook，使其在任何 `Edit` 或 `Write` 工具调用之前运行脚本：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/protect-files.sh"
          }
        ]
      }
    ]
  }
}
```

### 压缩后重新注入上下文

**当 Claude 的上下文窗口满了，compaction 会压缩对话以释放空间，这可能丢失重要细节。使用 `SessionStart` hook 配合 `compact` matcher，在每次压缩后重新注入关键上下文。**

命令写到 stdout 的任何文本都会被加入 Claude 的上下文。以下示例提醒 Claude 项目约定和当前工作。添加到项目根目录的 `.claude/settings.json`：

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "compact",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Reminder: use Bun, not npm. Run bun test before committing. Current sprint: auth refactor.'"
          }
        ]
      }
    ]
  }
}
```

你可以把 `echo` 替换为任何生成动态输出的命令，比如 `git log --oneline -5` 显示最近提交。如果要在每次会话启动时注入上下文，考虑使用 [CLAUDE.md](https://code.claude.com/docs/en/memory)。环境变量相关见参考文档的 [`CLAUDE_ENV_FILE`](https://code.claude.com/docs/en/hooks#persist-environment-variables)。

### 审计配置变更

**跟踪会话期间 settings 或 skills 文件的变更。`ConfigChange` 事件在外部进程或编辑器修改配置文件时触发，你可以用来记录变更日志或阻止未授权修改。**

以下示例把每次变更追加到审计日志。添加到 `~/.claude/settings.json`：

```json
{
  "hooks": {
    "ConfigChange": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "jq -c '{timestamp: now | todate, source: .source, file: .file_path}' >> ~/claude-config-audit.log"
          }
        ]
      }
    ]
  }
}
```

matcher 可按配置类型过滤：`user_settings`、`project_settings`、`local_settings`、`policy_settings` 或 `skills`。要阻止变更生效，以退出码 2 退出或返回 `{"decision": "block"}`。参见 [ConfigChange 参考](https://code.claude.com/docs/en/hooks#configchange)。

### 目录或文件变更时重新加载环境

**一些项目根据所在目录设置不同的环境变量。[direnv](https://direnv.net/) 等工具在 shell 中自动处理，但 Claude 的 Bash 工具不会自动感知这些变化。**

组合 `SessionStart` 和 `CwdChanged` hook 可以解决。`SessionStart` 为启动目录加载变量，`CwdChanged` 在 Claude 每次切换目录时重新加载。两者都写入 `CLAUDE_ENV_FILE`，Claude Code 会在每次 Bash 命令前将其作为脚本前导执行。添加到 `~/.claude/settings.json`：

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "direnv export bash > \"$CLAUDE_ENV_FILE\""
          }
        ]
      }
    ],
    "CwdChanged": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "direnv export bash > \"$CLAUDE_ENV_FILE\""
          }
        ]
      }
    ]
  }
}
```

需在每个有 `.envrc` 的目录运行一次 `direnv allow`。如果使用 devbox 或 nix 替代 direnv，用 `devbox shellenv` 或 `devbox global shellenv` 替换 `direnv export bash` 即可。

要监听特定文件而非每次目录变更，使用 `FileChanged` 配合 `matcher`，列出要监听的文件名（用 `|` 分隔）。该值被拆分为字面文件名而非正则表达式。以下示例监听工作目录中的 `.envrc` 和 `.env`：

```json
{
  "hooks": {
    "FileChanged": [
      {
        "matcher": ".envrc|.env",
        "hooks": [
          {
            "type": "command",
            "command": "direnv export bash > \"$CLAUDE_ENV_FILE\""
          }
        ]
      }
    ]
  }
}
```

参见 [CwdChanged](https://code.claude.com/docs/en/hooks#cwdchanged) 和 [FileChanged](https://code.claude.com/docs/en/hooks#filechanged) 参考条目了解输入 schema、`watchPaths` 输出和 `CLAUDE_ENV_FILE` 细节。

### 自动批准特定权限弹窗

**跳过你总是允许的工具调用的审批对话框。** 以下示例自动批准 `ExitPlanMode`（Claude 完成计划展示并请求继续时调用的工具），这样你不用每次计划就绪时都点确认。

与上面退出码的示例不同，自动批准需要 hook 向 stdout 写入 JSON decision。`PermissionRequest` hook 在 Claude Code 即将显示权限对话框时触发，返回 `"behavior": "allow"` 即代表你批准。

matcher 范围限定为仅 `ExitPlanMode`，不影响其他弹窗。添加到 `~/.claude/settings.json`：

```json
{
  "hooks": {
    "PermissionRequest": [
      {
        "matcher": "ExitPlanMode",
        "hooks": [
          {
            "type": "command",
            "command": "echo '{\"hookSpecificOutput\": {\"hookEventName\": \"PermissionRequest\", \"decision\": {\"behavior\": \"allow\"}}}'"
          }
        ]
      }
    ]
  }
}
```

当 hook 批准时，Claude Code 退出计划模式并恢复进入计划模式前的权限模式。会话记录中显示 "Allowed by PermissionRequest hook"。hook 路径始终保持当前对话：它不能清除上下文并启动全新的实现会话。

要设置特定的权限模式，hook 输出可以包含 `updatedPermissions` 数组和 `setMode` 条目。`mode` 值可以是 `default`、`acceptEdits` 或 `bypassPermissions`，`destination: "session"` 表示仅应用于当前会话。

> [!NOTE]
> `bypassPermissions` 仅在会话启动时已启用绕过模式的情况下生效：`--dangerously-skip-permissions`、`--permission-mode bypassPermissions`、`--allow-dangerously-skip-permissions`，或 settings 中 `permissions.defaultMode: "bypassPermissions"`，且未被 [`permissions.disableBypassPermissionsMode`](https://code.claude.com/docs/en/permissions#managed-settings) 禁用。它永远不会被持久化为 `defaultMode`。

要将会话切换到 `acceptEdits` 模式，hook 向 stdout 写入以下 JSON：

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "allow",
      "updatedPermissions": [
        { "type": "setMode", "mode": "acceptEdits", "destination": "session" }
      ]
    }
  }
}
```

**保持 matcher 尽可能窄。** 匹配 `.*` 或留空 matcher 会自动批准所有权限弹窗，包括文件写入和 shell 命令。完整 decision 字段见 [PermissionRequest 参考](https://code.claude.com/docs/en/hooks#permissionrequest-decision-control)。

## Hook 的工作原理

**Hook 事件在 Claude Code 生命周期的特定点触发。当事件触发时，所有匹配的 hook 并行执行，相同命令会自动去重。** 下表列出每个事件及其触发时机：

| 事件 | 触发时机 |
| :--- | :--- |
| `SessionStart` | 会话开始或恢复时 |
| `Setup` | 使用 `--init-only` 启动，或在 `-p` 模式下使用 `--init`/`--maintenance` 时。用于 CI 或脚本的一次性准备 |
| `UserPromptSubmit` | 你提交 prompt 时，在 Claude 处理之前 |
| `UserPromptExpansion` | 用户输入的命令展开为 prompt 时，在到达 Claude 之前。可以阻止展开 |
| `PreToolUse` | 工具调用执行之前。可以阻止 |
| `PermissionRequest` | 权限对话框出现时 |
| `PermissionDenied` | 工具调用被 auto mode 分类器拒绝时。返回 `{retry: true}` 告诉模型可以重试 |
| `PostToolUse` | 工具调用成功后 |
| `PostToolUseFailure` | 工具调用失败后 |
| `PostToolBatch` | 一批并行工具调用全部完成后，下一次模型调用之前 |
| `Notification` | Claude Code 发送通知时 |
| `MessageDisplay` | assistant 消息文本显示时 |
| `SubagentStart` | subagent 生成时 |
| `SubagentStop` | subagent 完成时 |
| `TaskCreated` | 通过 `TaskCreate` 创建任务时 |
| `TaskCompleted` | 任务被标记为完成时 |
| `Stop` | Claude 完成响应时 |
| `StopFailure` | 回合因 API 错误结束时。输出和退出码被忽略 |
| `TeammateIdle` | [agent team](https://code.claude.com/docs/en/agent-teams) 中的队友即将空闲时 |
| `InstructionsLoaded` | CLAUDE.md 或 `.claude/rules/*.md` 文件被加载到上下文时。在会话开始和文件延迟加载期间触发 |
| `ConfigChange` | 会话期间配置文件变更时 |
| `CwdChanged` | 工作目录变更时，例如 Claude 执行 `cd` 命令。适用于配合 direnv 等工具的响应式环境管理 |
| `FileChanged` | 被监听的文件在磁盘上变更时。`matcher` 字段指定要监听的文件名 |
| `WorktreeCreate` | 通过 `--worktree` 或 `isolation: "worktree"` 创建 worktree 时。替代默认 git 行为 |
| `WorktreeRemove` | worktree 被移除时，会话退出或 subagent 完成时 |
| `PreCompact` | 上下文压缩之前 |
| `PostCompact` | 上下文压缩完成后 |
| `Elicitation` | MCP server 在工具调用期间请求用户输入时 |
| `ElicitationResult` | 用户响应 MCP elicitation 后，响应发送回 server 之前 |
| `SessionEnd` | 会话终止时 |

每个 hook 有一个 `type` 决定其运行方式。大多数 hook 使用 `"type": "command"` 执行 shell 命令。还有四种类型可用：

| 类型 | 说明 |
| :--- | :--- |
| `"type": "http"` | 向 URL POST 事件数据。见 [HTTP hooks](#http-hooks) |
| `"type": "mcp_tool"` | 调用已连接 MCP server 上的工具。见 [MCP tool hooks](https://code.claude.com/docs/en/hooks#mcp-tool-hook-fields) |
| `"type": "prompt"` | 单轮 LLM 评估。见 [Prompt 类型 hook](#prompt-类型-hook) |
| `"type": "agent"` | 多轮验证，带工具访问。实验性功能，可能变更。见 [Agent 类型 hook](#agent-类型-hook) |

### 合并多个 Hook 的结果

**当多个 hook 匹配同一事件时，所有 hook 命令都执行完成后再合并结果。一个 hook 返回 `deny` 不会阻止兄弟 hook 执行。** 不要依赖某个 hook 的 `deny` 来抑制另一个 hook 的副作用。

合并逻辑：对于 `PreToolUse` 权限决策，最严格的答案获胜，优先级为 `deny` > `defer` > `ask` > `allow`。所有 hook 的 `additionalContext` 文本都会保留并一起传递给 Claude。

以下示例在 `Bash` 上注册两个 `PreToolUse` hook。第一个把每条命令追加到日志文件并退出 0。第二个运行脚本，当命令包含 `rm -rf` 时以退出码 2 拒绝：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r .tool_input.command >> ~/.claude/bash.log"
          },
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-rm-rf.sh"
          }
        ]
      }
    ]
  }
}
```

当 Claude 尝试运行 `rm -rf /tmp/build` 时，两个 hook 并行执行。日志 hook 写入命令到 `~/.claude/bash.log` 并退出 0（无决策）。护栏 hook 退出 2（拒绝）。deny 获胜，Claude Code 阻止命令并将护栏的 stderr 反馈给 Claude。日志条目仍然被写入，因为日志 hook 已经执行过了。

### 读取输入和返回输出

**Hook 通过 stdin、stdout、stderr 和退出码与 Claude Code 通信。** 事件触发时，Claude Code 将事件特定数据以 JSON 形式传入脚本的 stdin。脚本读取数据、执行逻辑、通过退出码告诉 Claude Code 下一步做什么。

#### Hook 输入

每个事件包含 `session_id` 和 `cwd` 等公共字段，但各事件类型添加不同数据。例如，当 Claude 运行 Bash 命令时，`PreToolUse` hook 在 stdin 收到类似：

```json
{
  "session_id": "abc123",          // 本次会话的唯一 ID
  "cwd": "/Users/sarah/myproject", // 事件触发时的工作目录
  "hook_event_name": "PreToolUse", // 哪个事件触发了此 hook
  "tool_name": "Bash",             // Claude 即将使用的工具
  "tool_input": {                  // Claude 传给工具的参数
    "command": "npm test"          // 对 Bash 来说就是 shell 命令
  }
}
```

脚本可以解析该 JSON 并对任何字段采取行动。`UserPromptSubmit` hook 获取 `prompt` 文本，`SessionStart` hook 获取 `source`（startup、resume、clear、compact），以此类推。公共字段见 [Common input fields](https://code.claude.com/docs/en/hooks#common-input-fields)，各事件的特有 schema 见对应章节。

#### Hook 输出

**脚本通过向 stdout 或 stderr 写入内容并以特定退出码退出来告诉 Claude Code 下一步做什么。** 例如，一个想阻止命令的 `PreToolUse` hook：

```bash
#!/bin/bash
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command')

if echo "$COMMAND" | grep -q "drop table"; then
  echo "Blocked: dropping tables is not allowed" >&2  # stderr 变为 Claude 的反馈
  exit 2                                               # exit 2 = 阻止操作
fi

exit 0  # exit 0 = 无决策；正常权限流程继续
```

退出码决定后续行为：

| 退出码 | 行为 |
| :--- | :--- |
| **Exit 0** | hook 无异议，操作正常进行。对 `PreToolUse` 来说不是批准工具调用：正常[权限流程](https://code.claude.com/docs/en/permissions)仍然适用。对 `UserPromptSubmit`、`UserPromptExpansion` 和 `SessionStart` hook，你写到 stdout 的内容会被加入 Claude 的上下文 |
| **Exit 2** | 操作被阻止。向 stderr 写入原因，Claude 会收到作为反馈以便调整。某些事件不能被阻止：对 `SessionStart`、`Setup`、`Notification` 等，exit 2 会向用户显示 stderr 但执行继续。完整列表见 [exit code 2 behavior per event](https://code.claude.com/docs/en/hooks#exit-code-2-behavior-per-event) |
| **其他退出码** | 操作继续进行。会话记录显示 `<hook name> hook error` 通知加 stderr 第一行；完整 stderr 进入[调试日志](https://code.claude.com/docs/en/hooks#debug-hooks) |

#### 结构化 JSON 输出

**退出码只能阻止或保持沉默。要获得更多控制，以退出 0 结束并向 stdout 打印 JSON 对象。**

> [!NOTE]
> 用 exit 2 配合 stderr 消息来阻止，或用 exit 0 配合 JSON 做结构化控制。不要混用：exit 2 时 Claude Code 会忽略 JSON。

例如，`PreToolUse` hook 可以拒绝工具调用并告诉 Claude 原因，或升级为让用户审批：

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Use rg instead of grep for better performance"
  }
}
```

`"deny"` 时，Claude Code 取消工具调用并把 `permissionDecisionReason` 反馈给 Claude。`PreToolUse` 专用的 `permissionDecision` 值：

| 值 | 行为 |
| :--- | :--- |
| `"allow"` | 跳过交互式权限弹窗。deny 和 ask 规则（包括企业管理的 deny 列表）仍然适用 |
| `"deny"` | 取消工具调用并把原因发送给 Claude |
| `"ask"` | 正常向用户显示权限弹窗 |

第四个值 `"defer"` 在使用 `-p` 标志的[非交互模式](https://code.claude.com/docs/en/headless)下可用。它退出进程但保留工具调用，以便 Agent SDK wrapper 收集输入并恢复。见 [Defer a tool call for later](https://code.claude.com/docs/en/hooks#defer-a-tool-call-for-later)。

返回 `"allow"` 跳过交互弹窗但不会覆盖[权限规则](https://code.claude.com/docs/en/permissions#manage-permissions)。如果 deny 规则匹配该工具调用，即使 hook 返回 `"allow"` 调用也会被阻止。如果 ask 规则匹配，用户仍会被提示。这意味着来自任何 settings 范围（包括[managed settings](https://code.claude.com/docs/en/settings#settings-files)）的 deny 规则始终优先于 hook 的批准。

其他事件使用不同的决策模式。例如，`PostToolUse` 和 `Stop` hook 使用顶级 `decision: "block"` 字段，`PermissionRequest` 使用 `hookSpecificOutput.decision.behavior`。完整按事件分类见[汇总表](https://code.claude.com/docs/en/hooks#decision-control)。

对于 `UserPromptSubmit` hook，使用 `additionalContext` 注入文本到 Claude 的上下文。Prompt 类型 hook（`type: "prompt"`）输出处理方式不同：见 [Prompt 类型 hook](#prompt-类型-hook)。

### 用 Matcher 过滤 Hook

**没有 matcher 时，hook 在事件每次发生时都触发。Matcher 让你缩小范围。** 例如，如果你只想在文件编辑后（而非每次工具调用后）运行格式化器：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "prettier --write ..." }
        ]
      }
    ]
  }
}
```

`"Edit|Write"` matcher 仅在 Claude 使用 `Edit` 或 `Write` 工具时触发，不在使用 `Bash`、`Read` 或其他工具时触发。匹配器语法详见 [Matcher patterns](https://code.claude.com/docs/en/hooks#matcher-patterns)。

> [!NOTE]
> Claude 也可以通过 `Bash` 工具运行 shell 命令来创建或修改文件。如果你的 hook 必须捕获每次文件变更（如合规扫描或审计日志），添加一个 [`Stop`](https://code.claude.com/docs/en/hooks#stop) hook 在每轮结束时扫描工作树。如果要逐次调用覆盖，同时匹配 `Bash` 并在脚本中用 `git status --porcelain` 列出修改和未跟踪文件。

各事件类型的 matcher 过滤对象：

| 事件 | Matcher 过滤什么 | 示例值 |
| :--- | :--- | :--- |
| `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `PermissionDenied` | 工具名称 | `Bash`, `Edit\|Write`, `mcp__.*` |
| `SessionStart` | 会话启动方式 | `startup`, `resume`, `clear`, `compact` |
| `Setup` | 触发 setup 的 CLI 标志 | `init`, `maintenance` |
| `SessionEnd` | 会话结束原因 | `clear`, `resume`, `logout`, `prompt_input_exit`, `bypass_permissions_disabled`, `other` |
| `Notification` | 通知类型 | `permission_prompt`, `idle_prompt`, `auth_success`, `elicitation_dialog`, `elicitation_complete`, `elicitation_response` |
| `SubagentStart` | agent 类型 | `general-purpose`, `Explore`, `Plan`, 或自定义 agent 名 |
| `PreCompact`, `PostCompact` | 压缩触发原因 | `manual`, `auto` |
| `SubagentStop` | agent 类型 | 同 `SubagentStart` |
| `ConfigChange` | 配置来源 | `user_settings`, `project_settings`, `local_settings`, `policy_settings`, `skills` |
| `StopFailure` | 错误类型 | `rate_limit`, `overloaded`, `authentication_failed`, `oauth_org_not_allowed`, `billing_error`, `invalid_request`, `model_not_found`, `server_error`, `max_output_tokens`, `unknown` |
| `InstructionsLoaded` | 加载原因 | `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact` |
| `Elicitation` | MCP server 名称 | 你配置的 MCP server 名称 |
| `ElicitationResult` | MCP server 名称 | 同 `Elicitation` |
| `FileChanged` | 要监听的字面文件名（见 [FileChanged](https://code.claude.com/docs/en/hooks#filechanged)） | `.envrc\|.env` |
| `UserPromptExpansion` | 命令名称 | 你的 skill 或命令名称 |
| `UserPromptSubmit`, `PostToolBatch`, `Stop`, `TeammateIdle`, `TaskCreated`, `TaskCompleted`, `WorktreeCreate`, `WorktreeRemove`, `CwdChanged`, `MessageDisplay` | 不支持 matcher | 每次发生都触发 |

更多 matcher 示例：

**记录每条 Bash 命令：**

仅匹配 `Bash` 工具调用并记录每条命令。`PostToolUse` 在命令完成后触发，`tool_input.command` 包含执行的内容：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.command' >> ~/.claude/command-log.txt"
          }
        ]
      }
    ]
  }
}
```

**匹配 MCP 工具：**

MCP 工具命名约定与内置工具不同：`mcp__<server>__<tool>`，其中 `<server>` 是 MCP server 名，`<tool>` 是它提供的工具。例如 `mcp__github__search_repositories` 或 `mcp__filesystem__read_file`。用正则 matcher 定位特定 server 的所有工具，或用 `mcp__.*__write.*` 跨 server 匹配。详见 [Match MCP tools](https://code.claude.com/docs/en/hooks#match-mcp-tools)。

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__github__.*",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"GitHub tool called: $(jq -r '.tool_name')\" >&2"
          }
        ]
      }
    ]
  }
}
```

**会话结束时清理：**

`SessionEnd` 支持按会话结束原因匹配。此 hook 仅在 `clear`（运行 `/clear` 时）触发，正常退出不触发：

```json
{
  "hooks": {
    "SessionEnd": [
      {
        "matcher": "clear",
        "hooks": [
          {
            "type": "command",
            "command": "rm -f /tmp/claude-scratch-*.txt"
          }
        ]
      }
    ]
  }
}
```

完整 matcher 语法见 [Hooks 参考文档](https://code.claude.com/docs/en/hooks#configuration)。

#### 用 `if` 字段按工具名称和参数过滤

> [!NOTE]
> `if` 字段需要 Claude Code v2.1.85 及以上版本。更早版本会忽略它并在每次匹配调用时运行 hook。

**`if` 字段使用[权限规则语法](https://code.claude.com/docs/en/permissions)，按工具名称和参数组合过滤 hook，仅在工具调用匹配时才启动 hook 进程。** 这比 `matcher` 更精确 -- `matcher` 仅在组级别按工具名过滤。

例如，仅在 Claude 使用 `git` 命令时运行 hook，而非所有 Bash 命令：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(git *)",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/check-git-policy.sh"
          }
        ]
      }
    ]
  }
}
```

hook 是否执行取决于 `if` 模式和 Claude 调用的 Bash 命令：

| `if` 模式 | Bash 命令 | Hook 执行？ | 原因 |
| :--- | :--- | :--- | :--- |
| `Bash(git *)` | `git push` | 是 | 命令名匹配 |
| `Bash(git *)` | `npm test && git push` | 是 | 每个子命令都会检查；`git push` 匹配 |
| `Bash(git *)` | `echo $(git log)` | 是 | `$()` 和反引号内的命令也会被检查；`git log` 匹配 |
| `Bash(git *)` | `echo $(date)` | 否 | 没有子命令匹配 `git *` |
| `Bash(git push *)` | `echo $(date)` | 是 | 指定了命令名以外参数的模式，遇到 `$()`、反引号或 `$VAR` 时会照样运行 hook |

当 Bash 命令无法解析时，过滤器也会 fail open（照样运行 hook）。因为过滤是 best-effort 的，用[权限系统](https://code.claude.com/docs/en/permissions)而非 hook 来强制执行硬性 allow 或 deny。

`if` 字段接受与权限规则相同的模式：`"Bash(git *)"`, `"Edit(*.ts)"` 等。要匹配多个工具名，使用各自带 `if` 值的独立处理器，或在 `matcher` 级别用管道符分隔。

`if` 仅对工具事件有效：`PreToolUse`、`PostToolUse`、`PostToolUseFailure`、`PermissionRequest` 和 `PermissionDenied`。添加到其他事件会阻止 hook 运行。

### 配置 Hook 的存放位置

**Hook 的存放位置决定其作用范围：**

| 位置 | 作用范围 | 可共享 |
| :--- | :--- | :--- |
| `~/.claude/settings.json` | 你的所有项目 | 否，仅本机 |
| `.claude/settings.json` | 单个项目 | 是，可提交到仓库 |
| `.claude/settings.local.json` | 单个项目 | 否，Claude Code 创建时会 gitignore |
| Managed policy settings | 组织范围 | 是，管理员控制 |
| [Plugin](https://code.claude.com/docs/en/plugins) `hooks/hooks.json` | 插件启用时 | 是，打包在插件中 |
| [Skill](https://code.claude.com/docs/en/skills) 或 [agent](https://code.claude.com/docs/en/sub-agents) frontmatter | skill 或 agent 活跃时 | 是，定义在组件文件中 |

在 Claude Code 中运行 [`/hooks`](https://code.claude.com/docs/en/hooks#the-%2Fhooks-menu) 浏览按事件分组的所有已配置 hook。要禁用 hook，在 settings 文件中设置 `"disableAllHooks": true`。在 managed settings 中配置的 hook 仍会运行，除非 `disableAllHooks` 也在那里设置。

如果在 Claude Code 运行期间直接编辑 settings 文件，文件监听器通常会自动检测 hook 变更。

## Prompt 类型 Hook

**对于需要判断力而非确定性规则的决策，使用 `type: "prompt"` hook。** Claude Code 不执行 shell 命令，而是将你的 prompt 和 hook 的输入数据发送给 Claude 模型（默认 Haiku）做决策。可以通过 `model` 字段指定其他模型。

模型的唯一任务是返回 yes/no 决策的 JSON：

| 返回值 | 行为 |
| :--- | :--- |
| `"ok": true` | 操作继续 |
| `"ok": false` | 取决于事件类型：`Stop` 和 `SubagentStop` 把 `reason` 反馈给 Claude 让它继续工作；`PreToolUse` 拒绝工具调用并将 `reason` 作为工具错误返回；`PostToolUse`、`PostToolBatch`、`UserPromptSubmit` 和 `UserPromptExpansion` 结束回合并在聊天中显示 `reason` 作为警告 |

以下示例使用 `Stop` hook 询问模型是否所有请求的任务都已完成。如果模型返回 `"ok": false`，Claude 继续工作并将 `reason` 作为下一条指令：

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Check if all tasks are complete. If not, respond with {\"ok\": false, \"reason\": \"what remains to be done\"}."
          }
        ]
      }
    ]
  }
}
```

完整配置选项见 [Prompt-based hooks](https://code.claude.com/docs/en/hooks#prompt-based-hooks) 参考。

## Agent 类型 Hook

> [!WARNING]
> Agent hook 为实验性功能。行为和配置可能在未来版本中变更。生产环境建议使用 [command hooks](https://code.claude.com/docs/en/hooks#command-hook-fields)。

**当验证需要检查文件或运行命令时，使用 `type: "agent"` hook。** 与仅做单次 LLM 调用的 prompt hook 不同，agent hook 生成一个 subagent，它可以读取文件、搜索代码、使用其他工具来验证条件再返回决策。

Agent hook 使用与 prompt hook 相同的 `"ok"` / `"reason"` 响应格式，但默认超时更长（60 秒）且最多 50 轮工具使用。

以下示例在 Claude 停止前验证测试是否通过：

```json
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

当 hook 输入数据足以做决策时用 prompt hook。当需要验证代码库的实际状态时用 agent hook。

完整配置选项见 [Agent-based hooks](https://code.claude.com/docs/en/hooks#agent-based-hooks) 参考。

## HTTP Hooks

**使用 `type: "http"` hook 向 HTTP 端点 POST 事件数据，而非运行 shell 命令。** 端点收到与 command hook 在 stdin 上收到的相同 JSON，并通过 HTTP 响应体以相同 JSON 格式返回结果。

HTTP hook 适用于让 web server、云函数或外部服务处理 hook 逻辑：例如一个跨团队记录工具使用事件的共享审计服务。

以下示例将每次工具使用发送到本地日志服务：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "http",
            "url": "http://localhost:8080/hooks/tool-use",
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

端点应返回使用与 command hook 相同[输出格式](https://code.claude.com/docs/en/hooks#json-output)的 JSON 响应体。要阻止工具调用，返回带适当 `hookSpecificOutput` 字段的 2xx 响应。HTTP 状态码本身不能阻止操作。

Header 值支持环境变量插值，使用 `$VAR_NAME` 或 `${VAR_NAME}` 语法。只有 `allowedEnvVars` 数组中列出的变量会被解析；其他 `$VAR` 引用保持为空。

完整配置选项和响应处理见 [HTTP hooks](https://code.claude.com/docs/en/hooks#http-hook-fields) 参考。

## 限制与排障

### 限制

- Command hook 仅通过 stdout、stderr 和退出码通信。它们不能触发 `/` 命令或工具调用。通过 `additionalContext` 返回的文本作为系统提醒注入，Claude 将其读取为纯文本。HTTP hook 通过响应体通信
- Hook 超时因类型而异。可用每个 hook 的 `timeout` 字段（秒）覆盖：
  - `command`, `http`, `mcp_tool`：10 分钟。`UserPromptSubmit` 降低到 30 秒，`MessageDisplay` 降低到 10 秒
  - `prompt`：30 秒
  - `agent`：60 秒
- `PostToolUse` hook 无法撤销操作，因为工具已经执行过了
- `PermissionRequest` hook 在[非交互模式](https://code.claude.com/docs/en/headless)（`-p`）下不触发。用 `PreToolUse` hook 做自动化权限决策
- `Stop` hook 在 Claude 每次完成响应时触发，不仅限于任务完成时。用户中断不触发。API 错误触发 [StopFailure](https://code.claude.com/docs/en/hooks#stopfailure)
- 当多个 PreToolUse hook 返回 [`updatedInput`](https://code.claude.com/docs/en/hooks#pretooluse) 来改写工具参数时，最后完成的那个获胜。因为 hook 并行运行，顺序不确定。避免多个 hook 修改同一工具的输入

### Hook 与权限模式

**PreToolUse hook 在任何权限模式检查之前触发。** 返回 `permissionDecision: "deny"` 的 hook 即使在 `bypassPermissions` 模式或 `--dangerously-skip-permissions` 下也会阻止工具。这让你可以强制执行用户无法通过切换权限模式绕过的策略。

反过来不成立：hook 返回 `"allow"` 不会绕过 settings 中的 deny 规则。Hook 可以收紧限制但不能放松到超过权限规则允许的程度。

### Hook 不触发

Hook 已配置但从未执行。

- 运行 `/hooks` 确认 hook 出现在正确事件下
- 检查 matcher 模式是否精确匹配工具名（matcher 区分大小写）
- 确认触发的是正确的事件类型（如 `PreToolUse` 在工具执行前触发，`PostToolUse` 在执行后触发）
- 如果在非交互模式（`-p`）下使用 `PermissionRequest` hook，改用 `PreToolUse`

### 输出中出现 Hook error

会话记录中看到类似 "PreToolUse hook error: ..." 的消息。

- 脚本意外以非零码退出。通过管道输入样本 JSON 手动测试：
  ```bash
  echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' | ./my-hook.sh
  echo $?  # 检查退出码
  ```
- 如果看到 "command not found"，使用绝对路径或 `${CLAUDE_PROJECT_DIR}` 引用脚本。要完全避免 shell 引号问题，添加 `"args": []` 切换到 [exec 形式](https://code.claude.com/docs/en/hooks#exec-form-and-shell-form)，直接生成脚本而不经过 shell
- 如果看到 "jq: command not found"，安装 `jq` 或用 Python/Node.js 解析 JSON
- 如果脚本完全没运行，确保它可执行：`chmod +x ./my-hook.sh`

### `/hooks` 显示无 hook 配置

你编辑了 settings 文件但 hook 没出现在菜单中。

- 文件编辑通常会被自动检测。如果几秒后仍未出现，文件监听器可能遗漏了变更：重启会话强制重新加载
- 确认 JSON 有效（不允许尾逗号和注释）
- 确认 settings 文件位于正确位置：`.claude/settings.json` 用于项目 hook，`~/.claude/settings.json` 用于全局 hook

### Stop hook 达到阻止上限

Claude 持续工作而不停止，然后以 Stop hook 连续阻止过多次的警告结束回合。

Claude Code 在 Stop hook 连续阻止 8 次无进展后会覆盖它。你的 hook 脚本需要检查是否已经触发过继续。从 JSON 输入解析 `stop_hook_active` 字段，如果为 `true` 则提前退出：

```bash
#!/bin/bash
INPUT=$(cat)
if [ "$(echo "$INPUT" | jq -r '.stop_hook_active')" = "true" ]; then
  exit 0  # 允许 Claude 停止
fi
# ... 后续 hook 逻辑
```

如果你的 hook 确实需要超过八次迭代才能收敛，用 [`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`](https://code.claude.com/docs/en/env-vars) 提高上限。

### JSON 校验失败

Claude Code 显示 JSON 解析错误，但你的 hook 脚本输出的是有效 JSON。

当 Claude Code 运行 shell 形式的 command hook（没有 `args` 的）时，macOS 和 Linux 上生成 `sh -c`，Windows 上默认使用 Git Bash。这个 shell 是非交互的，但 Git Bash 和某些配置（如 `BASH_ENV` 指向 `~/.bashrc`）仍会 source 你的 profile。如果 profile 中有无条件的 `echo` 语句，输出会被加到你 hook 的 JSON 前面：

```text
Shell ready on arm64
{"decision": "block", "reason": "Not allowed"}
```

Claude Code 尝试将此解析为 JSON 时失败。修复方法是在 shell profile 中包裹 echo 语句，仅在交互式 shell 中运行：

```bash
# In ~/.zshrc or ~/.bashrc
if [[ $- == *i* ]]; then
  echo "Shell ready"
fi
```

`$-` 变量包含 shell 标志，`i` 表示交互式。Hook 在非交互 shell 中运行，所以 echo 被跳过。

### 调试技巧

**会话记录视图（`Ctrl+O` 切换）为每个触发的 hook 显示一行摘要：** 成功时无声，阻止性错误显示 stderr，非阻止性错误显示 `<hook name> hook error` 通知加 stderr 第一行。

要查看完整执行细节（哪些 hook 匹配、退出码、stdout、stderr），读取调试日志。用 `claude --debug-file /tmp/claude.log` 启动写入已知路径，然后在另一个终端 `tail -f /tmp/claude.log`。如果启动时没加该标志，在会话中运行 `/debug` 启用日志并找到日志路径。

## 进一步了解

- [Hooks 参考文档](https://code.claude.com/docs/en/hooks)：完整事件 schema、JSON 输出格式、异步 hook 和 MCP tool hook
- [安全注意事项](https://code.claude.com/docs/en/hooks#security-considerations)：在共享或生产环境部署 hook 前务必阅读
- [Bash 命令验证器示例](https://github.com/anthropics/claude-code/blob/main/examples/hooks/bash_command_validator_example.py)：完整的参考实现
