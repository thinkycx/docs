---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】状态栏
description: 配置自定义状态栏来监控上下文窗口使用、费用和 git 状态。状态栏通过 shell 脚本接收 JSON 会话数据并输出自定义内容。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/statusline.md
  - en-source/statusline.md
---

# 自定义状态栏

> 配置自定义状态栏来监控 Claude Code 中的上下文窗口使用、费用和 git 状态。

**状态栏是 Claude Code 底部的可定制栏，运行你配置的任何 shell 脚本。** 它通过 stdin 接收 JSON 会话数据并显示脚本输出内容，提供上下文使用、费用、git 状态等信息的持续展示。

状态栏适用于：

- 工作时监控上下文窗口使用
- 跟踪会话费用
- 跨多个会话时需要区分它们
- 始终可见 git 分支和状态

状态栏在内置 footer 徽章上方独立一行渲染，不替换它们。要在对话出现 ID 时在 footer 添加可点击链接徽章（无需编写脚本），配置 [`footerLinksRegexes`](https://code.claude.com/docs/en/settings#footer-link-badges)。

## 设置状态栏

使用 [`/statusline` 命令](#使用-statusline-命令)让 Claude Code 为你生成脚本，或[手动创建脚本](#手动配置状态栏)并添加到设置。

### 使用 /statusline 命令

`/statusline` 命令接受自然语言描述。Claude Code 在 `~/.claude/` 生成脚本文件并自动更新设置：

```text
/statusline show model name and context percentage with a progress bar
```

### 手动配置状态栏

在用户设置（`~/.claude/settings.json`）或[项目设置](https://code.claude.com/docs/en/settings#settings-files)中添加 `statusLine` 字段。设置 `type` 为 `"command"` 并将 `command` 指向脚本路径或内联 shell 命令：

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh",
    "padding": 2
  }
}
```

`command` 字段在 shell 中运行，所以也可使用内联命令代替脚本文件：

```json
{
  "statusLine": {
    "type": "command",
    "command": "jq -r '\"[\\(.model.display_name)] \\(.context_window.used_percentage // 0)% context\"'"
  }
}
```

可选字段：

- `padding`：状态栏内容的额外水平间距（字符数）。默认 `0`
- `refreshInterval`：每 N 秒重新运行命令（最小 `1`）。当状态栏显示时间数据或后台子代理改变 git 状态时设置
- `hideVimModeIndicator`：设为 `true` 压制内置 `-- INSERT --` 文本（当你的脚本自己渲染 vim mode 时）

### 禁用状态栏

运行 `/statusline` 并要求移除（如 `/statusline delete`），或手动从 settings.json 删除 `statusLine` 字段。

## 逐步构建状态栏

以下演示手动创建显示当前模型、工作目录和上下文窗口使用率的状态栏。

**步骤 1：创建读取 JSON 并输出的脚本**

保存到 `~/.claude/statusline.sh`：

```bash
#!/bin/bash
# 读取 Claude Code 通过 stdin 发送的 JSON 数据
input=$(cat)

# 用 jq 提取字段
MODEL=$(echo "$input" | jq -r '.model.display_name')
DIR=$(echo "$input" | jq -r '.workspace.current_dir')
# "// 0" 在字段为 null 时提供回退值
PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)

# 输出状态栏 - ${DIR##*/} 提取文件夹名
echo "[$MODEL] 📁 ${DIR##*/} | ${PCT}% context"
```

**步骤 2：添加执行权限**

```bash
chmod +x ~/.claude/statusline.sh
```

**步骤 3：添加到设置**

在 `~/.claude/settings.json` 中添加：

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh"
  }
}
```

## 工作原理

**Claude Code 运行脚本并通过 stdin 管道传递 JSON 会话数据。** 脚本读取 JSON、提取所需内容并输出文本到 stdout。Claude Code 显示脚本输出的任何内容。

**更新时机：** 在每条新助手消息后、`/compact` 完成后、权限模式变更时或 vim 模式切换时运行。更新以 300ms 去抖。

**输出能力：**

- **多行**：每个 `echo` 语句显示为独立行
- **颜色**：使用 [ANSI 转义码](https://en.wikipedia.org/wiki/ANSI_escape_code#Colors)如 `\033[32m` 表示绿色
- **链接**：使用 [OSC 8 转义序列](https://en.wikipedia.org/wiki/ANSI_escape_code#OSC) 使文本可点击（需支持超链接的终端如 iTerm2、Kitty 或 WezTerm）

**终端尺寸：** 读取 `COLUMNS` 和 `LINES` 环境变量。Claude Code 在运行脚本前设置这些值（需 v2.1.153 或更高版本）。

状态栏在本地运行，不消耗 API token。

## 可用数据

**Claude Code 通过 stdin 发送以下 JSON 字段：**

| 字段 | 说明 |
| :--- | :--- |
| `model.id`, `model.display_name` | 当前模型标识符和显示名 |
| `cwd`, `workspace.current_dir` | 当前工作目录（两者相同值；推荐 `workspace.current_dir`） |
| `workspace.project_dir` | Claude Code 启动的目录 |
| `workspace.added_dirs` | 通过 `/add-dir` 或 `--add-dir` 添加的额外目录 |
| `workspace.git_worktree` | 当前目录在链接 worktree 中时的 worktree 名称 |
| `workspace.repo.host`, `.owner`, `.name` | 从 `origin` remote 解析的仓库身份 |
| `cost.total_cost_usd` | 会话估算费用（USD） |
| `cost.total_duration_ms` | 会话启动以来的总时间（毫秒） |
| `cost.total_api_duration_ms` | 等待 API 响应的总时间（毫秒） |
| `cost.total_lines_added`, `.total_lines_removed` | 代码变更行数 |
| `context_window.total_input_tokens`, `.total_output_tokens` | 上下文窗口中的 token 数 |
| `context_window.context_window_size` | 最大上下文窗口大小（token） |
| `context_window.used_percentage` | 预计算的上下文窗口使用百分比 |
| `context_window.remaining_percentage` | 预计算的剩余百分比 |
| `context_window.current_usage` | 上次 API 调用的 token 计数细分 |
| `exceeds_200k_tokens` | 最近 API 响应的总 token 是否超过 200k |
| `effort.level` | 当前推理 effort（`low`、`medium`、`high`、`xhigh` 或 `max`） |
| `thinking.enabled` | 扩展思考是否启用 |
| `rate_limits.five_hour.used_percentage`, `.seven_day.used_percentage` | 5 小时或 7 天速率限制消耗百分比 |
| `rate_limits.five_hour.resets_at`, `.seven_day.resets_at` | 速率限制重置时间（Unix epoch 秒） |
| `session_id` | 唯一会话标识符 |
| `session_name` | 自定义会话名（通过 `--name` 或 `/rename` 设置时） |
| `prompt_id` | 当前处理的用户 prompt 的 UUID |
| `transcript_path` | 对话记录文件路径 |
| `version` | Claude Code 版本 |
| `output_style.name` | 当前输出风格名称 |
| `vim.mode` | vim 模式启用时的当前模式 |
| `agent.name` | 使用 `--agent` 标志时的代理名称 |
| `pr.number`, `pr.url` | 当前分支的开放 PR |
| `pr.review_state` | PR 审查状态 |
| `worktree.name`, `.path`, `.branch` | `--worktree` 会话中的 worktree 信息 |

**可能缺失的字段**（JSON 中不存在）：`session_name`、`prompt_id`、`workspace.git_worktree`、`workspace.repo`、`effort`、`vim`、`agent`、`pr`、`worktree`、`rate_limits`。

**可能为 `null` 的字段**：`context_window.current_usage`、`context_window.used_percentage`、`context_window.remaining_percentage`。

### 上下文窗口字段

`context_window` 对象描述最近 API 响应的实时上下文窗口。v2.1.132 起，`total_input_tokens` 和 `total_output_tokens` 反映当前上下文使用而非累计会话总量。

`current_usage` 对象包含：`input_tokens`、`output_tokens`、`cache_creation_input_tokens`、`cache_read_input_tokens`。

`used_percentage` 仅从输入 token 计算：`input_tokens + cache_creation_input_tokens + cache_read_input_tokens`，不包含 `output_tokens`。

## 示例

### 上下文窗口使用率

显示当前模型和带进度条的上下文窗口使用率：

```bash
#!/bin/bash
input=$(cat)

MODEL=$(echo "$input" | jq -r '.model.display_name')
PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)

BAR_WIDTH=10
FILLED=$((PCT * BAR_WIDTH / 100))
EMPTY=$((BAR_WIDTH - FILLED))
BAR=""
[ "$FILLED" -gt 0 ] && printf -v FILL "%${FILLED}s" && BAR="${FILL// /▓}"
[ "$EMPTY" -gt 0 ] && printf -v PAD "%${EMPTY}s" && BAR="${BAR}${PAD// /░}"

echo "[$MODEL] $BAR $PCT%"
```

### 带颜色的 Git 状态

显示 git 分支和颜色编码的暂存/修改文件指示器：

```bash
#!/bin/bash
input=$(cat)

MODEL=$(echo "$input" | jq -r '.model.display_name')
DIR=$(echo "$input" | jq -r '.workspace.current_dir')

GREEN='\033[32m'
YELLOW='\033[33m'
RESET='\033[0m'

if git rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git branch --show-current 2>/dev/null)
    STAGED=$(git diff --cached --numstat 2>/dev/null | wc -l | tr -d ' ')
    MODIFIED=$(git diff --numstat 2>/dev/null | wc -l | tr -d ' ')

    GIT_STATUS=""
    [ "$STAGED" -gt 0 ] && GIT_STATUS="${GREEN}+${STAGED}${RESET}"
    [ "$MODIFIED" -gt 0 ] && GIT_STATUS="${GIT_STATUS}${YELLOW}~${MODIFIED}${RESET}"

    echo -e "[$MODEL] 📁 ${DIR##*/} | 🌿 $BRANCH $GIT_STATUS"
else
    echo "[$MODEL] 📁 ${DIR##*/}"
fi
```

### 费用和时间跟踪

```bash
#!/bin/bash
input=$(cat)

MODEL=$(echo "$input" | jq -r '.model.display_name')
COST=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')
DURATION_MS=$(echo "$input" | jq -r '.cost.total_duration_ms // 0')

COST_FMT=$(printf '$%.2f' "$COST")
DURATION_SEC=$((DURATION_MS / 1000))
MINS=$((DURATION_SEC / 60))
SECS=$((DURATION_SEC % 60))

echo "[$MODEL] 💰 $COST_FMT | ⏱️ ${MINS}m ${SECS}s"
```

### 速率限制使用

显示 Claude.ai 订阅速率限制（仅 Pro/Max 用户可见）：

```bash
#!/bin/bash
input=$(cat)

MODEL=$(echo "$input" | jq -r '.model.display_name')
FIVE_H=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
WEEK=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')

LIMITS=""
[ -n "$FIVE_H" ] && LIMITS="5h: $(printf '%.0f' "$FIVE_H")%"
[ -n "$WEEK" ] && LIMITS="${LIMITS:+$LIMITS }7d: $(printf '%.0f' "$WEEK")%"

[ -n "$LIMITS" ] && echo "[$MODEL] | $LIMITS" || echo "[$MODEL]"
```

### 缓存耗时操作

脚本频繁运行。`git status` 等命令在大仓库中可能慢。用临时文件缓存 git 信息，每 5 秒才刷新一次。用 JSON 输入中的 `session_id` 作为缓存文件名的一部分（跨调用稳定且跨会话唯一）。

### Windows 配置

在 Windows 上，Claude Code 通过 Git Bash（如已安装）或 PowerShell 运行状态栏命令。

Git Bash 将未引用反斜杠作为转义字符处理，所以 `command` 字符串中的文件路径用正斜杠书写。`~` 简写也可用。

PowerShell 脚本示例配置：

```json
{
  "statusLine": {
    "type": "command",
    "command": "powershell -NoProfile -File C:/Users/username/.claude/statusline.ps1"
  }
}
```

## 子代理状态栏

`subagentStatusLine` 设置为 agent 面板中的每个[子代理](https://code.claude.com/docs/en/sub-agents)渲染自定义行内容：

```json
{
  "subagentStatusLine": {
    "type": "command",
    "command": "~/.claude/subagent-statusline.sh"
  }
}
```

## 提示

- **用模拟输入测试**：`echo '{"model":{"display_name":"Opus"},...}' | ./statusline.sh`
- **保持输出简短**：状态栏宽度有限
- **缓存慢操作**：参见[缓存示例](#缓存耗时操作)

## 故障排除

- **状态栏不出现**：验证脚本可执行（`chmod +x`）；检查输出到 stdout 而非 stderr；如果 `disableAllHooks` 为 `true` 则状态栏也被禁用
- **显示 `--` 或空值**：第一次 API 响应前字段可能为 `null`；用 `// 0` 处理空值
- **OSC 8 链接不可点击**：确认终端支持（iTerm2、Kitty、WezTerm）；Terminal.app 不支持
- **工作区信任要求**：状态栏命令需要接受当前目录的工作区信任对话框
