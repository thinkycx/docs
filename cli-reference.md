---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】CLI 参考
description: Claude Code 命令行界面的完整参考手册，涵盖所有可用命令、标志参数及系统提示词定制方式。
category: translation
tags: [claude-code, cli, reference, translation]
refs:
  - https://code.claude.com/docs/en/cli-reference.md
---

# CLI 参考

> Claude Code 命令行界面的完整参考，包括命令和标志参数。

## CLI 命令

**通过这些命令可以启动会话、管道传入内容、恢复对话和管理更新。**

| 命令 | 说明 | 示例 |
| :--- | :--- | :--- |
| `claude` | 启动交互式会话 | `claude` |
| `claude "query"` | 带初始提示词启动交互式会话 | `claude "explain this project"` |
| `claude -p "query"` | 通过 SDK 查询后退出 | `claude -p "explain this function"` |
| `cat file \| claude -p "query"` | 处理管道传入的内容 | `cat logs.txt \| claude -p "explain"` |
| `claude -c` | 继续当前目录最近的对话 | `claude -c` |
| `claude -c -p "query"` | 通过 SDK 继续对话 | `claude -c -p "Check for type errors"` |
| `claude -r "<session>" "query"` | 通过 ID 或名称恢复会话 | `claude -r "auth-refactor" "Finish this PR"` |
| `claude update` | 更新到最新版本 | `claude update` |
| `claude install [version]` | 安装或重新安装原生二进制文件。接受版本号（如 `2.1.118`）或 `stable`、`latest`。参见[安装指定版本](https://code.claude.com/docs/en/setup#install-a-specific-version) | `claude install stable` |
| `claude auth login` | 登录 Anthropic 账号。使用 `--email` 预填邮箱，`--sso` 强制 SSO 认证，`--console` 通过 Anthropic Console 登录以使用 API 计费而非 Claude 订阅 | `claude auth login --console` |
| `claude auth logout` | 退出 Anthropic 账号 | `claude auth logout` |
| `claude auth status` | 以 JSON 显示认证状态。使用 `--text` 输出人类可读格式。已登录返回退出码 0，未登录返回 1 | `claude auth status` |
| `claude agents` | 打开 [Agent 视图](https://code.claude.com/docs/en/agent-view)来监控和调度并行后台会话。使用 `--cwd <path>` 仅显示该目录下的会话，使用 `--json` 以 JSON 数组输出（`--json --all` 还包含已完成的后台会话）。支持 `--permission-mode`、`--model`、`--effort`、`--agent` 设置[调度默认值](https://code.claude.com/docs/en/agent-view#permission-mode-model-and-effort)。也接受 `--settings`、`--add-dir`、`--plugin-dir`、`--mcp-config` 参数。需要交互式终端 | `claude agents --json` |
| `claude attach <id>` | 附加到一个[后台会话](https://code.claude.com/docs/en/agent-view#manage-sessions-from-the-shell) | `claude attach 7c5dcf5d` |
| `claude auto-mode defaults` | 以 JSON 输出内置的 [auto 模式](https://code.claude.com/docs/en/permission-modes#eliminate-prompts-with-auto-mode)分类器规则。使用 `claude auto-mode config` 查看应用 settings 后的有效配置 | `claude auto-mode defaults > rules.json` |
| `claude daemon status` | 输出后台会话[守护进程](https://code.claude.com/docs/en/agent-view#the-supervisor-process)的状态、版本、socket 目录和 worker 数量。守护进程未运行时退出码为 1 | `claude daemon status` |
| `claude daemon stop --any` | 停止后台会话[守护进程](https://code.claude.com/docs/en/agent-view#the-supervisor-process)及其托管的会话。传入 `--keep-workers` 可保留后台会话运行，下次启动时会重新连接。`--any` 确认停止按需启动的守护进程。用于恢复[无响应的守护进程](https://code.claude.com/docs/en/agent-view#agent-view-says-the-background-service-did-not-respond) | `claude daemon stop --any --keep-workers` |
| `claude logs <id>` | 输出[后台会话](https://code.claude.com/docs/en/agent-view#manage-sessions-from-the-shell)的最近输出 | `claude logs 7c5dcf5d` |
| `claude mcp` | 配置 Model Context Protocol (MCP) 服务器 | 参见 [Claude Code MCP 文档](https://code.claude.com/docs/en/mcp) |
| `claude mcp login <name>` | 执行已配置 MCP 服务器的 OAuth 流程，无需打开交互式 `/mcp` 面板。适用于 HTTP、SSE 和 claude.ai connector 类型服务器。SSH 环境下加 `--no-browser` 打印授权 URL 而非打开浏览器。需要 v2.1.186+。参见[从命令行认证](https://code.claude.com/docs/en/mcp#authenticate-from-the-command-line) | `claude mcp login sentry` |
| `claude mcp logout <name>` | 清除 MCP 服务器的已存储 OAuth 凭证。需要 v2.1.186+ | `claude mcp logout sentry` |
| `claude plugin` | 管理 Claude Code [插件](https://code.claude.com/docs/en/plugins)。别名：`claude plugins`。参见[插件参考](https://code.claude.com/docs/en/plugins-reference#cli-commands-reference)了解子命令 | `claude plugin install code-review@claude-plugins-official` |
| `claude project purge [path]` | 删除项目的所有本地 Claude Code 状态：会话记录、任务列表、调试日志、文件编辑历史、提示词历史条目，以及 `~/.claude.json` 中的项目条目。省略 `[path]` 进入交互式选择。标志：`--dry-run` 预览，`-y`/`--yes` 跳过确认，`-i`/`--interactive` 逐项确认，`--all` 处理所有项目。参见[清除本地数据](https://code.claude.com/docs/en/claude-directory#clear-local-data) | `claude project purge ~/work/repo --dry-run` |
| `claude remote-control` | 启动 [Remote Control](https://code.claude.com/docs/en/remote-control) 服务器，从 claude.ai 或 Claude 应用控制 Claude Code。以服务器模式运行（无本地交互会话）。参见[服务器模式标志](https://code.claude.com/docs/en/remote-control#start-a-remote-control-session) | `claude remote-control --name "My Project"` |
| `claude respawn <id>` | 重启[后台会话](https://code.claude.com/docs/en/agent-view#manage-sessions-from-the-shell)（运行中或已停止），保留对话上下文。使用 `--all` 重启所有运行中的会话，例如在更新 Claude Code 二进制文件后 | `claude respawn 7c5dcf5d` |
| `claude rm <id>` | 从列表中移除[后台会话](https://code.claude.com/docs/en/agent-view#manage-sessions-from-the-shell)。会话记录仍保留在本地，可通过 `claude --resume` 访问 | `claude rm 7c5dcf5d` |
| `claude setup-token` | 生成长期 OAuth token，用于 CI 和脚本。输出 token 到终端但不保存。需要 Claude 订阅。参见[生成长期 token](https://code.claude.com/docs/en/authentication#generate-a-long-lived-token) | `claude setup-token` |
| `claude stop <id>` | 停止[后台会话](https://code.claude.com/docs/en/agent-view#manage-sessions-from-the-shell)。也接受 `claude kill` | `claude stop 7c5dcf5d` |
| `claude ultrareview [target]` | 非交互式运行 [ultrareview](https://code.claude.com/docs/en/ultrareview#run-ultrareview-non-interactively)。输出发现到 stdout，成功退出 0，失败退出 1。使用 `--json` 获取原始数据，`--timeout <minutes>` 覆盖默认 30 分钟超时 | `claude ultrareview 1234 --json` |

**输入错误的子命令时，Claude Code 会提示最接近的匹配并退出。** 例如 `claude udpate` 会打印 `Did you mean claude update?`。

## CLI 标志参数

**通过命令行标志可自定义 Claude Code 的行为。** `claude --help` 不会列出所有标志，因此某个标志不在 `--help` 输出中不代表它不可用。

| 标志 | 说明 | 示例 |
| :--- | :--- | :--- |
| `--add-dir` | 添加额外的工作目录，允许 Claude 读写其中的文件。授予文件访问权限；这些目录下的大多数 `.claude/` 配置[不会被发现](https://code.claude.com/docs/en/permissions#additional-directories-grant-file-access-not-configuration)。会验证路径是否为有效目录。要跨会话持久化可设置 [`permissions.additionalDirectories`](https://code.claude.com/docs/en/settings#permission-settings) | `claude --add-dir ../apps ../lib` |
| `--advisor <model>` | 为当前会话启用服务端 [advisor 工具](https://code.claude.com/docs/en/advisor)，传入模型别名：`opus`、`sonnet`、`fable`（v2.1.170+），或完整模型 ID。优先级高于 `advisorModel` 设置。需要 v2.1.98+ | `claude --advisor opus` |
| `--agent` | 指定当前会话使用的 agent（覆盖 `agent` 设置） | `claude --agent my-custom-agent` |
| `--agents` | 通过 JSON 动态定义自定义 subagent。字段与 subagent [frontmatter](https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields) 相同，加一个 `prompt` 字段作为 agent 指令 | `claude --agents '{"reviewer":{"description":"Reviews code","prompt":"You are a code reviewer"}}'` |
| `--allow-dangerously-skip-permissions` | 将 `bypassPermissions` 添加到 `Shift+Tab` 模式循环中（不会以该模式启动）。允许从 `plan` 等模式开始，后续切换到 `bypassPermissions`。参见[权限模式](https://code.claude.com/docs/en/permission-modes#skip-all-checks-with-bypasspermissions-mode) | `claude --permission-mode plan --allow-dangerously-skip-permissions` |
| `--allowedTools`, `--allowed-tools` | 无需权限提示即可执行的工具。参见[权限规则语法](https://code.claude.com/docs/en/settings#permission-rule-syntax)了解模式匹配。要限制可用工具，使用 `--tools` | `"Bash(git log *)" "Bash(git diff *)" "Read"` |
| `--append-system-prompt` | 在默认系统提示词末尾追加自定义文本 | `claude --append-system-prompt "Always use TypeScript"` |
| `--append-system-prompt-file` | 从文件加载额外系统提示词文本并追加到默认提示词 | `claude --append-system-prompt-file ./extra-rules.txt` |
| `--ax-screen-reader` | 渲染屏幕阅读器友好的输出：纯文本，无装饰性边框或动画。强制使用经典渲染器，[`tui`](https://code.claude.com/docs/en/settings#available-settings) 设置对该会话无效。优先级高于 [`CLAUDE_AX_SCREEN_READER`](https://code.claude.com/docs/en/env-vars) 和 [`axScreenReader`](https://code.claude.com/docs/en/settings#available-settings) 设置。需要 v2.1.181+ | `claude --ax-screen-reader` |
| `--bare` | 最小模式：跳过 hooks、skills、plugins、MCP 服务器、auto memory 和 CLAUDE.md 的自动发现，使脚本调用启动更快。Claude 仅可使用 Bash、文件读取和文件编辑工具。设置 [`CLAUDE_CODE_SIMPLE`](https://code.claude.com/docs/en/env-vars)。参见 [bare 模式](https://code.claude.com/docs/en/headless#start-faster-with-bare-mode) | `claude --bare -p "query"` |
| `--betas` | API 请求中包含的 beta headers（仅 API key 用户） | `claude --betas interleaved-thinking` |
| `--bg`, `--background` | 作为[后台 agent](https://code.claude.com/docs/en/agent-view) 启动会话并立即返回。输出会话 ID 和管理命令。与 `--exec` 组合运行 shell 命令作为后台任务，或与 `--agent` 组合运行特定 subagent | `claude --bg "investigate the flaky test"` |
| `--channels` | （研究预览）MCP 服务器的 [channel](https://code.claude.com/docs/en/channels) 通知监听列表。空格分隔的 `plugin:<name>@<marketplace>` 条目。需要 Claude.ai 认证 | `claude --channels plugin:my-notifier@my-marketplace` |
| `--chrome` | 启用 [Chrome 浏览器集成](https://code.claude.com/docs/en/chrome)用于 Web 自动化和测试 | `claude --chrome` |
| `--continue`, `-c` | 加载当前目录最近的对话。包括通过 `/add-dir` 添加了本目录的会话 | `claude --continue` |
| `--dangerously-load-development-channels` | 启用不在批准允许列表上的 [channel](https://code.claude.com/docs/en/channels-reference#test-during-the-research-preview)，用于本地开发。接受 `plugin:<name>@<marketplace>` 和 `server:<name>` 条目。会提示确认 | `claude --dangerously-load-development-channels server:webhook` |
| `--dangerously-skip-permissions` | 跳过权限提示。等同于 `--permission-mode bypassPermissions`。参见[权限模式](https://code.claude.com/docs/en/permission-modes#skip-all-checks-with-bypasspermissions-mode)了解跳过和不跳过的内容 | `claude --dangerously-skip-permissions` |
| `--debug` | 启用调试模式，支持可选的分类过滤（例如 `"api,hooks"` 或 `"!statsig,!file"`） | `claude --debug "api,mcp"` |
| `--debug-file <path>` | 将调试日志写入指定文件路径。隐式启用调试模式。优先级高于 `CLAUDE_CODE_DEBUG_LOGS_DIR` | `claude --debug-file /tmp/claude-debug.log` |
| `--disable-slash-commands` | 禁用当前会话的所有 skills 和命令 | `claude --disable-slash-commands` |
| `--disallowedTools`, `--disallowed-tools` | 拒绝规则。裸工具名移除匹配工具：`"Edit"` 移除 Edit，`"*"` 移除所有工具，`"mcp__*"` 移除所有 MCP 工具。作用域规则如 `Bash(rm *)` 保留工具但拒绝匹配的调用 | `"Bash(git log *)" "Bash(git diff *)" "Edit"` |
| `--effort` | 设置当前会话的[努力等级](https://code.claude.com/docs/en/model-config#adjust-effort-level)。选项：`low`、`medium`、`high`、`xhigh`、`max`；可用等级取决于模型。覆盖 [`effortLevel`](https://code.claude.com/docs/en/settings#available-settings) 设置，不持久化 | `claude --effort high` |
| `--enable-auto-mode` | 已在 v2.1.111 移除。Auto 模式现在默认在 `Shift+Tab` 循环中；使用 `--permission-mode auto` 以该模式启动 | `claude --permission-mode auto` |
| `--exclude-dynamic-system-prompt-sections` | 将逐机器变化的部分（工作目录、环境信息、内存路径、git-repo 标记）从系统提示词移到第一条用户消息中。提高不同用户和机器执行相同任务时的 prompt-cache 命中率。仅在使用默认系统提示词时有效；设置了 `--system-prompt` 或 `--system-prompt-file` 时忽略。适合与 `-p` 组合用于脚本化多用户工作负载 | `claude -p --exclude-dynamic-system-prompt-sections "query"` |
| `--exec` | 运行 shell 命令作为 PTY 支持的后台任务，而非启动 Claude 会话。与 `--bg` 组合使用 | `claude --bg --exec 'pytest -x'` |
| `--fallback-model` | 当主模型过载或不可用（例如已退役模型）时自动回退到指定模型。接受逗号分隔列表，按顺序尝试。参见[回退模型链](https://code.claude.com/docs/en/model-config#fallback-model-chains)。跨会话持久化可使用 [`fallbackModel` 设置](https://code.claude.com/docs/en/settings#available-settings)，该标志优先级更高 | `claude --fallback-model sonnet,haiku` |
| `--fork-session` | 恢复时创建新会话 ID 而非复用原始 ID（与 `--resume` 或 `--continue` 组合使用） | `claude --resume abc123 --fork-session` |
| `--from-pr` | 恢复关联特定 PR 的会话。接受 PR 号、GitHub/GitHub Enterprise PR URL、GitLab MR URL 或 Bitbucket PR URL。Claude 创建 PR 时自动关联 | `claude --from-pr 123` |
| `--ide` | 启动时自动连接 IDE（仅当恰好有一个有效 IDE 可用时） | `claude --ide` |
| `--init` | 在会话前运行带 `init` 匹配器的 [Setup hooks](https://code.claude.com/docs/en/hooks#setup)（仅 print 模式） | `claude -p --init "query"` |
| `--init-only` | 运行 [Setup](https://code.claude.com/docs/en/hooks#setup) 和 `SessionStart` hooks 后退出，不启动对话 | `claude --init-only` |
| `--include-hook-events` | 在输出流中包含所有 hook 生命周期事件。需要 `--output-format stream-json` | `claude -p --output-format stream-json --verbose --include-hook-events "query"` |
| `--include-partial-messages` | 在输出中包含部分流式事件。需要 `--print` 和 `--output-format stream-json` | `claude -p --output-format stream-json --verbose --include-partial-messages "query"` |
| `--input-format` | 指定 print 模式的输入格式（选项：`text`、`stream-json`） | `claude -p --output-format json --input-format stream-json` |
| `--json-schema` | Agent 完成工作流后获取符合 JSON Schema 的验证输出（仅 print 模式，参见[结构化输出](https://code.claude.com/docs/en/agent-sdk/structured-outputs)） | `claude -p --json-schema '{"type":"object","properties":{...}}' "query"` |
| `--maintenance` | 在会话前运行带 `maintenance` 匹配器的 [Setup hooks](https://code.claude.com/docs/en/hooks#setup)（仅 print 模式） | `claude -p --maintenance "query"` |
| `--max-budget-usd` | API 调用的最大花费限额（美元），达到后停止（仅 print 模式） | `claude -p --max-budget-usd 5.00 "query"` |
| `--max-turns` | 限制 agentic 轮次数（仅 print 模式）。达到限制时以错误退出。默认无限制 | `claude -p --max-turns 3 "query"` |
| `--mcp-config` | 从 JSON 文件或字符串加载 MCP 服务器（空格分隔） | `claude --mcp-config ./mcp.json` |
| `--model` | 设置当前会话使用的模型，可用别名（`sonnet`、`opus`、`haiku`、`fable`）或模型全名。覆盖 [`model`](https://code.claude.com/docs/en/settings#available-settings) 设置和 [`ANTHROPIC_MODEL`](https://code.claude.com/docs/en/model-config#environment-variables) | `claude --model claude-sonnet-4-6` |
| `--name`, `-n` | 设置会话显示名称，在 `/resume` 和终端标题中显示。可通过 `claude --resume <name>` 恢复命名会话。[`/rename`](https://code.claude.com/docs/en/commands) 可在会话中改名并在提示栏显示 | `claude -n "my-feature-work"` |
| `--no-chrome` | 禁用当前会话的 [Chrome 浏览器集成](https://code.claude.com/docs/en/chrome) | `claude --no-chrome` |
| `--no-session-persistence` | 禁用会话持久化，会话不保存到磁盘也不能恢复。仅 print 模式。环境变量 [`CLAUDE_CODE_SKIP_PROMPT_HISTORY`](https://code.claude.com/docs/en/env-vars) 在任何模式下有相同效果 | `claude -p --no-session-persistence "query"` |
| `--output-format` | 指定 print 模式的输出格式（选项：`text`、`json`、`stream-json`） | `claude -p "query" --output-format json` |
| `--permission-mode` | 以指定[权限模式](https://code.claude.com/docs/en/permission-modes)启动。接受 `default`、`acceptEdits`、`plan`、`auto`、`dontAsk` 或 `bypassPermissions`。覆盖 settings 中的 `defaultMode` | `claude --permission-mode plan` |
| `--permission-prompt-tool` | 指定 MCP 工具来处理非交互模式下的权限提示 | `claude -p --permission-prompt-tool mcp_auth_tool "query"` |
| `--plugin-dir` | 从目录或 `.zip` 归档加载插件（仅当前会话）。每个标志接受一个路径，多个插件需重复使用：`--plugin-dir A --plugin-dir B.zip` | `claude --plugin-dir ./my-plugin` |
| `--plugin-url` | 从 URL 获取插件 `.zip` 归档（仅当前会话）。可重复使用，或在一个引号值中传入空格分隔的 URL | `claude --plugin-url https://example.com/plugin.zip` |
| `--print`, `-p` | 不进入交互模式直接输出响应（参见 [Agent SDK 文档](https://code.claude.com/docs/en/agent-sdk/overview)了解编程式用法） | `claude -p "query"` |
| `--prompt-suggestions` | 每轮后发出 `prompt_suggestion` 消息，预测下一个用户提示词。需要 `--print`、`--output-format stream-json` 和 `--verbose`。参见[提示词建议](https://code.claude.com/docs/en/interactive-mode#prompt-suggestions) | `claude -p --prompt-suggestions --output-format stream-json --verbose "query"` |
| `--remote` | 在 claude.ai 上创建新的 [Web 会话](https://code.claude.com/docs/en/claude-code-on-the-web)并传入任务描述 | `claude --remote "Fix the login bug"` |
| `--remote-control`, `--rc` | 启动带 [Remote Control](https://code.claude.com/docs/en/remote-control#start-a-remote-control-session) 的交互式会话，使你也可以从 claude.ai 或 Claude 应用控制它。可选传入会话名称 | `claude --remote-control "My Project"` |
| `--remote-control-session-name-prefix <prefix>` | 未设置显式名称时自动生成的 [Remote Control](https://code.claude.com/docs/en/remote-control) 会话名称前缀。默认使用机器主机名，生成如 `myhost-graceful-unicorn` 的名称。也可通过 `CLAUDE_REMOTE_CONTROL_SESSION_NAME_PREFIX` 设置 | `claude remote-control --remote-control-session-name-prefix dev-box` |
| `--replay-user-messages` | 将 stdin 的用户消息回显到 stdout 作为确认。需要 `--input-format stream-json` 和 `--output-format stream-json` | `claude -p --input-format stream-json --output-format stream-json --verbose --replay-user-messages` |
| `--resume`, `-r` | 通过 ID 或名称恢复特定会话，或显示交互式选择器。选择器和名称搜索包含通过 `/add-dir` 添加了本目录的会话；传入会话 ID 仅搜索当前项目目录及其 git worktree。从 v2.1.144 起，[后台会话](https://code.claude.com/docs/en/agent-view)在选择器中标记 `bg` | `claude --resume auth-refactor` |
| `--safe-mode` | 禁用所有自定义项启动，用于排查配置问题：不加载 CLAUDE.md、skills、plugins、hooks、MCP 服务器、自定义命令和 agent、输出样式、workflows、自定义主题、自定义快捷键、状态栏和文件建议命令、LSP 服务器及 auto-memory。认证、模型选择、内置工具和权限正常工作，这与 [`--bare`](https://code.claude.com/docs/en/headless#start-faster-with-bare-mode) 不同。Managed settings 策略仍生效。适合检查是否是某个自定义项触发了 [Fable 5 的自动回退](https://code.claude.com/docs/en/model-config#automatic-model-fallback)。设置 [`CLAUDE_CODE_SAFE_MODE`](https://code.claude.com/docs/en/env-vars)。需要 v2.1.169+ | `claude --safe-mode` |
| `--session-id` | 使用指定的会话 ID（必须是有效的 UUID） | `claude --session-id "550e8400-e29b-41d4-a716-446655440000"` |
| `--setting-sources` | 逗号分隔的 setting 来源列表（`user`、`project`、`local`） | `claude --setting-sources user,project` |
| `--settings` | 指定 settings JSON 文件路径或内联 JSON 字符串。这里设置的值会覆盖 `settings.json` 中的同名 key，未设置的 key 保留文件值。参见 [settings 优先级](https://code.claude.com/docs/en/settings#settings-precedence) | `claude --settings ./settings.json` |
| `--strict-mcp-config` | 仅使用 `--mcp-config` 中的 MCP 服务器，忽略所有其他 MCP 配置 | `claude --strict-mcp-config --mcp-config ./mcp.json` |
| `--system-prompt` | 用自定义文本替换整个系统提示词 | `claude --system-prompt "You are a Python expert"` |
| `--system-prompt-file` | 从文件加载系统提示词，替换默认提示词 | `claude --system-prompt-file ./custom-prompt.txt` |
| `--teleport` | 在本地终端恢复一个 [Web 会话](https://code.claude.com/docs/en/claude-code-on-the-web) | `claude --teleport` |
| `--teammate-mode` | 设置 [agent 团队](https://code.claude.com/docs/en/agent-teams)队友的显示方式：`in-process`（默认）、`auto`、`tmux`、或 `iterm2`（v2.1.186+ 新增）。默认值从 v2.1.179 起由 `auto` 改为 `in-process`。覆盖 [`teammateMode`](https://code.claude.com/docs/en/settings#available-settings) 设置。参见[选择显示模式](https://code.claude.com/docs/en/agent-teams#choose-a-display-mode) | `claude --teammate-mode auto` |
| `--tmux` | 为 worktree 创建 tmux 会话。需要 `--worktree`。在 iTerm2 可用时使用原生 pane；传入 `--tmux=classic` 使用传统 tmux | `claude -w feature-auth --tmux` |
| `--tools` | 限制 Claude 可使用的内置工具。`""` 禁用所有，`"default"` 所有可用，或指定工具名如 `"Bash,Edit,Read"`。不影响 MCP 工具；要同时拒绝 MCP 工具使用 `--disallowedTools "mcp__*"`，或传入 `--strict-mcp-config` 且不带 `--mcp-config` 使不加载任何 MCP 服务器 | `claude --tools "Bash,Edit,Read"` |
| `--verbose` | 启用详细日志，显示完整的逐轮输出。覆盖当前会话的 [`viewMode`](https://code.claude.com/docs/en/settings#available-settings) 设置 | `claude --verbose` |
| `--version`, `-v` | 输出版本号 | `claude -v` |
| `--worktree`, `-w` | 在隔离的 [git worktree](https://code.claude.com/docs/en/worktrees) 中启动 Claude，路径为 `<repo>/.claude/worktrees/<name>`。未提供名称时自动生成。传入 `#<number>` 或 GitHub PR URL 可从 `origin` 拉取该 PR 并基于它创建 worktree 分支 | `claude -w feature-auth` |

### 系统提示词标志

**Claude Code 提供四个标志用于自定义系统提示词，在交互和非交互模式下都可使用。**

| 标志 | 行为 | 示例 |
| :--- | :--- | :--- |
| `--system-prompt` | 替换整个默认提示词 | `claude --system-prompt "You are a Python expert"` |
| `--system-prompt-file` | 用文件内容替换 | `claude --system-prompt-file ./prompts/review.txt` |
| `--append-system-prompt` | 追加到默认提示词之后 | `claude --append-system-prompt "Always use TypeScript"` |
| `--append-system-prompt-file` | 将文件内容追加到默认提示词之后 | `claude --append-system-prompt-file ./style-rules.txt` |

**`--system-prompt` 与 `--system-prompt-file` 互斥。** append 标志可以与任一替换标志组合使用。

**根据 Claude Code 的默认身份是否适合你的任务来选择。** 当 Claude 仍应作为编码助手，同时遵循你的额外规则时使用 append 标志：逐次调用的指令、输出格式化、或 `-p` 脚本的领域上下文。追加会保留默认的工具指导、安全指令和编码规范，你只需提供差异部分。当界面、身份或权限模型与 Claude Code 默认不同时使用替换标志——例如流水线中无人监控的非编码 agent。替换会丢弃所有默认提示词，包括工具指导和安全指令，因此你需要自行负责任务所需的内容。

**这些标志仅对当前调用生效。** 对于可切换和项目共享的持久化角色，使用[输出样式](https://code.claude.com/docs/en/output-styles)。对于 Claude 应始终遵循的项目规范，使用 [CLAUDE.md](https://code.claude.com/docs/en/memory)。[Agent SDK 系统提示词指南](https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts#decide-on-a-starting-point)有更深入的讨论。

## 另见

- [Chrome 扩展](https://code.claude.com/docs/en/chrome) - 浏览器自动化和 Web 测试
- [交互模式](https://code.claude.com/docs/en/interactive-mode) - 快捷键、输入模式和交互功能
- [快速入门](https://code.claude.com/docs/en/quickstart) - Claude Code 入门指南
- [常见工作流](https://code.claude.com/docs/en/common-workflows) - 高级工作流和模式
- [设置](https://code.claude.com/docs/en/settings) - 配置选项
- [Agent SDK 文档](https://code.claude.com/docs/en/agent-sdk/overview) - 编程式用法和集成
