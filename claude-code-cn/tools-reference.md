---
title: 【译】工具参考
tags:
  - claude-code
  - tools
  - reference
  - translation
create: 2026-06-28
update: 2026-06-28
author: thinkycx
category: translation
description: Claude Code 内置工具的完整参考手册，包括每个工具的权限要求、行为细节和配置方式。
refs: https://code.claude.com/docs/en/tools-reference.md
---

# 工具参考

> Claude Code 可使用的工具完整参考，包括权限要求和每个工具的行为细节。

**Claude Code 拥有一组内置工具来帮助它理解和修改你的代码库。** 工具名称是你在[权限规则](https://code.claude.com/docs/en/permissions#tool-specific-permission-rules)、[subagent 工具列表](https://code.claude.com/docs/en/sub-agents)和 [hook matcher](https://code.claude.com/docs/en/hooks) 中使用的确切字符串。要完全禁用某个工具，将其名称添加到[权限设置](https://code.claude.com/docs/en/permissions#tool-specific-permission-rules)的 `deny` 数组中。

要添加自定义工具，连接 [MCP 服务器](https://code.claude.com/docs/en/mcp)。要用可复用的基于提示的工作流扩展 Claude，编写 [skill](https://code.claude.com/docs/en/skills)——它通过已有的 `Skill` 工具运行而非添加新的工具条目。

| 工具                  | 描述                                                                                                                                                                           | 需要权限 |
| :-------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- |
| `Agent`               | 生成一个拥有独立上下文窗口的 [subagent](https://code.claude.com/docs/en/sub-agents) 来处理任务。参见 [Agent 工具行为](#agent-工具行为)                                            | 否       |
| `Artifact`            | 将 HTML 或 Markdown 文件发布为 [artifact](https://code.claude.com/docs/en/artifacts)：一个可在组织内分享的私有交互页面。需要 Team 或 Enterprise 计划和 `/login` 认证              | 是       |
| `AskUserQuestion`     | 提出多选问题以收集需求或澄清歧义                                                                                                                                                | 否       |
| `Bash`                | 在你的环境中执行 shell 命令。参见 [Bash 工具行为](#bash-工具行为)                                                                                                                 | 是       |
| `CronCreate`          | 在当前会话中调度循环或单次提示。任务限于会话范围，通过 `--resume` 或 `--continue` 恢复。参见[计划任务](https://code.claude.com/docs/en/scheduled-tasks)                             | 否       |
| `CronDelete`          | 按 ID 取消计划任务                                                                                                                                                              | 否       |
| `CronList`            | 列出会话中所有计划任务                                                                                                                                                          | 否       |
| `Edit`                | 对文件进行精确编辑。参见 [Edit 工具行为](#edit-工具行为)                                                                                                                          | 是       |
| `EnterPlanMode`       | 切换到 plan 模式，在编码前设计方案                                                                                                                                               | 否       |
| `EnterWorktree`       | 创建隔离的 [git worktree](https://code.claude.com/docs/en/worktrees) 并切换进入。传 `path` 可切换到已有 worktree                                                                 | 否       |
| `ExitPlanMode`        | 展示计划供批准并退出 plan 模式                                                                                                                                                   | 是       |
| `ExitWorktree`        | 退出 worktree 会话并返回原始目录                                                                                                                                                 | 否       |
| `Glob`                | 基于模式匹配查找文件。参见 [Glob 工具行为](#glob-工具行为)                                                                                                                        | 否       |
| `Grep`                | 搜索文件内容中的模式。参见 [Grep 工具行为](#grep-工具行为)                                                                                                                        | 否       |
| `ListMcpResourcesTool`| 列出已连接 [MCP 服务器](https://code.claude.com/docs/en/mcp)暴露的资源                                                                                                           | 否       |
| `LSP`                 | 通过语言服务器的代码智能：跳转定义、查找引用、报告类型错误和警告。参见 [LSP 工具行为](#lsp-工具行为)                                                                                 | 否       |
| `Monitor`             | 在后台运行命令并将每行输出反馈给 Claude，以便它对日志条目、文件变化或轮询状态做出反应。参见 [Monitor 工具](#monitor-工具)                                                             | 是       |
| `NotebookEdit`        | 修改 Jupyter notebook 单元格。参见 [NotebookEdit 工具行为](#notebookedit-工具行为)                                                                                                | 是       |
| `PowerShell`          | 原生执行 PowerShell 命令。参见 [PowerShell 工具](#powershell-工具)                                                                                                                | 是       |
| `PushNotification`    | 发送桌面通知；连接[远程控制](https://code.claude.com/docs/en/remote-control)时还发送手机推送。不支持 Bedrock/Vertex/Foundry                                                       | 否       |
| `Read`                | 读取文件内容。参见 [Read 工具行为](#read-工具行为)                                                                                                                                 | 否       |
| `ReadMcpResourceTool`  | 按 URI 读取特定 MCP 资源                                                                                                                                                        | 否       |
| `RemoteTrigger`       | 在 claude.ai 上创建、更新、运行和列出 [Routines](https://code.claude.com/docs/en/routines)。支撑 `/schedule` 命令。需要 Pro/Max/Team/Enterprise 计划                               | 否       |
| `ScheduleWakeup`      | 重新调度[自定步调 `/loop`](https://code.claude.com/docs/en/scheduled-tasks#let-claude-choose-the-interval) 的下一次迭代                                                           | 否       |
| `SendMessage`         | 向 [agent team](https://code.claude.com/docs/en/agent-teams) 队友发送消息，或按 agent ID [恢复 subagent](https://code.claude.com/docs/en/sub-agents#resume-subagents)             | 否       |
| `ShareOnboardingGuide`| 上传 `ONBOARDING.md` 并返回分享链接。从 `/team-onboarding` 调用                                                                                                                  | 是       |
| `Skill`               | 在主对话中执行 [skill](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill)                                                                                       | 是       |
| `TaskCreate`          | 在任务列表中创建新任务                                                                                                                                                           | 否       |
| `TaskGet`             | 获取特定任务的完整详情                                                                                                                                                           | 否       |
| `TaskList`            | 列出所有任务及其当前状态                                                                                                                                                         | 否       |
| `TaskOutput`          | （已弃用）获取后台任务的输出。建议改用 `Read` 读取任务的输出文件路径                                                                                                               | 否       |
| `TaskStop`            | 按 ID 终止运行中的后台任务                                                                                                                                                       | 否       |
| `TaskUpdate`          | 更新任务状态、依赖、详情或删除任务                                                                                                                                               | 否       |
| `TodoWrite`           | 管理会话任务清单。v2.1.142 起默认禁用，已被 `TaskCreate`/`TaskGet`/`TaskList`/`TaskUpdate` 替代。设置 `CLAUDE_CODE_ENABLE_TASKS=0` 可重新启用                                       | 否       |
| `ToolSearch`          | 启用[工具搜索](https://code.claude.com/docs/en/mcp#scale-with-mcp-tool-search)时搜索和加载延迟工具                                                                                | 否       |
| `WaitForMcpServers`   | 等待仍在后台连接的 MCP 服务器就绪。仅在工具搜索禁用时出现                                                                                                                         | 否       |
| `WebFetch`            | 从指定 URL 获取内容。参见 [WebFetch 工具行为](#webfetch-工具行为)                                                                                                                  | 是       |
| `WebSearch`           | 执行网络搜索。参见 [WebSearch 工具行为](#websearch-工具行为)                                                                                                                       | 是       |
| `Workflow`            | 运行[动态工作流](https://code.claude.com/docs/en/workflows)：在后台编排多个 subagent 并返回一个汇总结果的脚本                                                                      | 是       |
| `Write`               | 创建或覆盖文件。参见 [Write 工具行为](#write-工具行为)                                                                                                                             | 是       |

## 通过权限规则和 hook 配置工具

**大多数情况下，Claude 自行决定何时使用这些工具，你在交互中不需要指定工具名。** 你在定义权限和其他配置时直接引用工具名：

* 在设置中的 [`permissions.allow` 和 `permissions.deny`](https://code.claude.com/docs/en/settings#available-settings) 以及 `/permissions` 界面
* 在 `--allowedTools` 和 `--disallowedTools` [CLI 标志](https://code.claude.com/docs/en/cli-reference)
* 在 Agent SDK 的 [`allowedTools` 和 `disallowedTools`](https://code.claude.com/docs/en/agent-sdk/permissions#allow-and-deny-rules) 选项
* 在 [subagent 的 `tools` 或 `disallowedTools`](https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields) frontmatter
* 在 [skill 的 `allowed-tools`](https://code.claude.com/docs/en/skills#frontmatter-reference) frontmatter
* 在 hook 的 [`if` 条件](https://code.claude.com/docs/en/hooks-guide#filter-by-tool-name-and-arguments-with-the-if-field)

所有这些都接受相同的规则格式 `ToolName(specifier)`。specifier 取决于工具，多个工具共享格式：

| 规则格式                       | 适用于                    | 详情                                                                |
| :---------------------------- | :------------------------ | :------------------------------------------------------------------ |
| `Bash(npm run *)`             | Bash, Monitor             | [命令模式匹配](https://code.claude.com/docs/en/permissions#bash)     |
| `PowerShell(Get-ChildItem *)` | PowerShell                | [命令模式匹配](https://code.claude.com/docs/en/permissions#powershell) |
| `Read(~/secrets/**)`          | Read, Grep, Glob, LSP     | [路径模式匹配](https://code.claude.com/docs/en/permissions#read-and-edit) |
| `Edit(/src/**)`               | Edit, Write, NotebookEdit | [路径模式匹配](https://code.claude.com/docs/en/permissions#read-and-edit) |
| `Skill(deploy *)`             | Skill                     | [Skill 名称匹配](https://code.claude.com/docs/en/skills#restrict-claude's-skill-access) |
| `Agent(Explore)`              | Agent                     | [Subagent 类型匹配](https://code.claude.com/docs/en/permissions#agent-subagents) |
| `WebFetch(domain:example.com)`| WebFetch                  | [域名匹配](https://code.claude.com/docs/en/permissions#webfetch)     |
| `WebSearch`                   | WebSearch                 | 无 specifier；整体允许或拒绝该工具                                     |

未列出的工具（如 `ExitPlanMode` 或 `ShareOnboardingGuide`）只接受裸工具名，没有 specifier。

`Edit(...)` allow 规则同时授予对相同路径的读取权限，无需匹配的 `Read(...)` 规则。

Hook `matcher` 字段使用裸工具名，不是带括号的规则格式。参见 [matcher 模式](https://code.claude.com/docs/en/hooks#matcher-patterns)了解匹配规则。每个工具传递给 hook 中 `tool_input` 的字段名参见 [PreToolUse 输入参考](https://code.claude.com/docs/en/hooks#pretooluse-input)。

## Agent 工具行为

**Agent 工具在独立上下文窗口中生成 subagent。** Subagent 自主完成任务，然后向父对话返回单个文本结果。父方看不到 subagent 的中间工具调用或输出，只有最终结果。要限制 subagent 运行的轮次，在 [subagent 定义](https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields)中设置 `maxTurns`。

同一 Agent 工具在启用 fork 模式时也启动 [forked subagent](https://code.claude.com/docs/en/sub-agents#fork-the-current-conversation)。Fork 继承完整的父对话而非从头开始，始终在后台运行，但仍在终端中显示权限提示。本节其余部分描述命名 subagent。

命名 subagent 可使用的工具取决于 [subagent 定义](https://code.claude.com/docs/en/sub-agents)中的 `tools` 和 `disallowedTools` 字段：

* **两者都未设置**：subagent 继承父方可用的所有工具
* **仅设 `tools`**：subagent 只获得列出的工具
* **仅设 `disallowedTools`**：subagent 获得除列出工具外的所有父方工具
* **两者都设**：`disallowedTools` 优先。同时出现在两个列表中的工具被移除

启动 subagent 本身不会提示权限。Subagent 自己的工具调用在运行时根据你的权限规则检查：

* **前台 subagent** 显示与主对话中相同的权限提示，在每次工具调用发生时
* **后台 subagent**（v2.1.186 起）在主会话中显示权限提示。提示指明是哪个 subagent 在请求，按 Esc 拒绝该次工具调用但不停止 subagent

要从一开始就限制 subagent 可触达的范围，缩小其 `tools` 字段、从列表中去掉 Bash、或在设置中设置 deny 规则。参见[控制 subagent 能力](https://code.claude.com/docs/en/sub-agents#control-subagent-capabilities)。

## Bash 工具行为

**Bash 工具在独立进程中运行每条命令，** 具有以下持久化行为：

* 当 Claude 在主会话中运行 `cd` 时，新的工作目录会延续到后续 Bash 命令，前提是它位于项目目录或通过 `--add-dir`/`additionalDirectories` 添加的[额外工作目录](https://code.claude.com/docs/en/permissions#working-directories)内。Subagent 会话永远不延续工作目录变更。
  * 如果 `cd` 到了这些目录之外，Claude Code 重置到项目目录并在工具结果中追加 `Shell cwd was reset to <dir>`。
  * 要禁用此延续行为使每条 Bash 命令都从项目目录开始，设置 `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR=1`。
* 环境变量不持久。一条命令中的 `export` 不会在下一条中可用。
* Shell 启动文件中定义的别名和 shell 函数可用。会话启动时，Claude Code 根据你的 shell 加载 `~/.zshrc`、`~/.bashrc` 或 `~/.profile`，捕获结果中的别名、函数和 shell 选项，并应用到每条 Bash 命令。

在启动 Claude Code 之前激活你的 virtualenv 或 conda 环境。要使环境变量跨 Bash 命令持久化，在启动前设置 [`CLAUDE_ENV_FILE`](https://code.claude.com/docs/en/env-vars) 指向一个 shell 脚本，或使用 [SessionStart hook](https://code.claude.com/docs/en/hooks#persist-environment-variables) 动态填充。

两个限制约束每条命令：

* **超时**：默认两分钟。Claude 可以通过 `timeout` 参数请求每条命令最多 10 分钟。使用 [`BASH_DEFAULT_TIMEOUT_MS` 和 `BASH_MAX_TIMEOUT_MS`](https://code.claude.com/docs/en/env-vars) 覆盖默认值和上限。
* **输出长度**：默认 30,000 字符。命令输出超过此限制时，Claude Code 将完整输出保存到会话目录中的文件，并给 Claude 文件路径加上开头的短预览。Claude 在需要其余内容时读取或搜索该文件。使用 [`BASH_MAX_OUTPUT_LENGTH`](https://code.claude.com/docs/en/env-vars) 提高限制，上限为 150,000 字符。

对于长时间运行的进程（如开发服务器或 watch 构建），Claude 可以设置 `run_in_background: true` 将命令作为后台任务启动并继续工作。使用 `/tasks` 列出和停止后台任务。

## Edit 工具行为

**Edit 工具执行精确的字符串替换。** 它接受 `old_string` 和 `new_string`，将前者替换为后者。不使用正则或模糊匹配。

三项检查必须通过才能应用编辑：

* **编辑前必须读取**：Claude 必须在当前对话中读取过该文件，且自该次读取后文件在磁盘上未发生变更。此检查在字符串匹配之前运行。
* **匹配**：`old_string` 必须在文件中完全匹配出现。单个空白或缩进字符的差异就足以错过。
* **唯一性**：`old_string` 必须恰好出现一次。出现多次时，Claude 要么提供更长的包含足够上下文的字符串来确定唯一出现，要么设置 `replace_all: true` 替换所有。

通过 Bash 查看文件也满足编辑前读取要求，条件是命令为 `cat`、`head`、`tail`、`sed -n 'X,Yp'`、`grep`、`egrep` 或 `fgrep`，作用于单个文件且无管道或重定向。管道输出和其他 Bash 命令不算，这些情况下 Claude 必须使用 Read。

这只影响编辑资格而非权限。[Read 和 Edit deny 规则](https://code.claude.com/docs/en/permissions#tool-specific-permission-rules)也适用于 Claude Code 在 Bash 中识别的文件命令（如 `cat`、`head`、`tail`、`sed`、`grep`），但不覆盖间接打开文件的任意子进程（如自行打开文件的 Python 或 Node 脚本）。要获得覆盖每个进程的 OS 级执行，[启用沙箱](https://code.claude.com/docs/en/sandboxing)。

## Glob 工具行为

**Glob 工具按名称模式查找文件。** 支持标准 glob 语法，包括 `**` 用于递归目录匹配：

* `**/*.js` 匹配任何深度的所有 `.js` 文件
* `src/**/*.ts` 匹配 `src/` 下的所有 `.ts` 文件
* `*.{json,yaml}` 匹配当前目录中的 `.json` 和 `.yaml` 文件

结果按修改时间排序，上限 100 个文件。如果触达上限，Claude 在结果中看到截断标志并可以缩窄模式。

Glob 默认不遵守 `.gitignore`，因此它同时找到 gitignore 的文件和已跟踪的文件。这与 [Grep](#grep-工具行为) 不同，后者跳过 gitignore 的文件。要让 Glob 遵守 `.gitignore`，在启动 Claude Code 前设置 `CLAUDE_CODE_GLOB_NO_IGNORE=false`。

## Grep 工具行为

**Grep 工具搜索文件内容中的模式。** [Glob](#glob-工具行为) 按名称查找文件，Grep 查找文件内部的行。

Grep 基于 [ripgrep](https://github.com/BurntSushi/ripgrep) 构建，使用 ripgrep 的正则语法而非 POSIX grep。包含正则元字符的模式需要转义。例如，在 Go 代码中查找 `interface{}` 需要模式 `interface\{\}`。

三种输出模式控制返回内容：

* `files_with_matches`：仅文件路径，无行内容。这是默认值。
* `content`：匹配行附带文件和行号。
* `count`：每个文件的匹配计数。

Claude 可以用 `glob` 参数（如 `**/*.tsx`）按文件限定结果，或用 `type` 参数（如 `py` 或 `rust`）按语言限定。默认情况下模式在单行内匹配。Claude 可以设置 `multiline: true` 跨行匹配。

Grep 遵守 `.gitignore`，跳过 gitignore 的文件。要搜索 gitignore 的文件，Claude 直接传入其路径。

## LSP 工具行为

**LSP 工具为 Claude 提供来自运行中语言服务器的代码智能。** 每次文件编辑后，它自动报告类型错误和警告，使 Claude 无需单独构建步骤即可修复问题。Claude 也可以直接调用它来导航代码：

* 跳转到符号定义
* 查找符号的所有引用
* 获取某位置的类型信息
* 列出文件中的符号
* 按名称搜索工作区中的符号
* 查找接口的实现
* 追踪调用层次

该工具在你安装对应语言的[代码智能插件](https://code.claude.com/docs/en/discover-plugins#code-intelligence)之前处于非活跃状态。插件捆绑语言服务器配置，你另行安装服务器二进制文件。

## Monitor 工具

> **注意：** Monitor 工具需要 Claude Code v2.1.98 或更高版本。

**Monitor 工具让 Claude 在后台监视某些东西并在变化时做出反应，不暂停对话。** 可以让 Claude：

* Tail 日志文件并在错误出现时标记
* 轮询 PR 或 CI 任务并在状态变化时报告
* 监视目录的文件变化
* 跟踪任何长时间运行脚本的输出

Claude 编写一个小脚本进行监视，在后台运行，并在输出到达时接收每一行。你在同一会话中继续工作，Claude 在事件到达时插话。通过要求 Claude 取消或结束会话来停止 monitor。

Monitor 使用与 Bash 相同的[权限规则](https://code.claude.com/docs/en/permissions#tool-specific-permission-rules)，你为 Bash 设置的 `allow` 和 `deny` 模式也适用于此。在 Amazon Bedrock、Google Vertex AI 或 Microsoft Foundry 上不可用。设置了 `DISABLE_TELEMETRY` 或 `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` 时也不可用。

插件可以声明在插件活跃时自动启动的 monitor，无需让 Claude 启动。参见[插件 monitor](https://code.claude.com/docs/en/plugins-reference#monitors)。

## NotebookEdit 工具行为

**NotebookEdit 逐单元格修改 Jupyter notebook，通过 `cell_id` 定位单元格。** 它不像 [Edit](#edit-工具行为) 对普通文件那样执行跨 notebook 的字符串替换。

三种编辑模式控制对目标单元格的操作：

* `replace`：覆盖单元格内容。这是默认值。
* `insert`：在目标之后添加新单元格。无 `cell_id` 时新单元格放在 notebook 开头。需要 `cell_type` 设为 `code` 或 `markdown`。
* `delete`：删除目标单元格。

权限规则使用 `Edit(...)` 路径格式。如 `Edit(notebooks/**)` 这样的规则覆盖该目录中文件的 NotebookEdit 调用。

## PowerShell 工具

**PowerShell 工具让 Claude 原生运行 PowerShell 命令。** 在 Windows 上意味着命令在 PowerShell 中运行而非通过 Git Bash 路由。

### 启用 PowerShell 工具

在环境或 `settings.json` 中设置 `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`：

```json
{
  "env": {
    "CLAUDE_CODE_USE_POWERSHELL_TOOL": "1"
  }
}
```

在 Windows 上设置为 `0` 可退出渐进推出。在 Linux、macOS 和 WSL 上，该工具需要 PowerShell 7 或更高版本：安装 `pwsh` 并确保它在 `PATH` 上。

Claude Code 用 `-ExecutionPolicy Bypass` 在进程范围内启动 PowerShell，因此 `.ps1` 脚本和模块导入在默认 Windows 安装上无需更改机器策略即可工作。进程范围绕过不覆盖组策略的 `MachinePolicy` 或 `UserPolicy`，企业锁定仍然适用。要遵循机器的有效执行策略，设置 `CLAUDE_CODE_POWERSHELL_RESPECT_EXECUTION_POLICY=1`。

### 设置、hook 和 skill 中的 shell 选择

三个额外设置控制 PowerShell 的使用位置：

* [`settings.json`](https://code.claude.com/docs/en/settings#available-settings) 中的 `"defaultShell": "powershell"`：通过 PowerShell 路由交互式 `!` 命令。需要启用 PowerShell 工具。
* 单个[命令 hook](https://code.claude.com/docs/en/hooks#command-hook-fields) 上的 `"shell": "powershell"`：在 PowerShell 中运行该 hook。Hook 直接启动 PowerShell，无论 `CLAUDE_CODE_USE_POWERSHELL_TOOL` 如何。
* [skill frontmatter](https://code.claude.com/docs/en/skills#frontmatter-reference) 中的 `shell: powershell`：在 PowerShell 中运行 `` !`command` `` 块。需要启用 PowerShell 工具。

Bash 工具部分描述的主会话工作目录重置行为同样适用于 PowerShell 命令，包括 `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR` 环境变量。

### 预览限制

PowerShell 工具在预览期间有以下已知限制：

* 不加载 PowerShell 配置文件
* 在 Windows 上不支持沙箱

## Read 工具行为

**Read 工具接受文件路径并返回带行号的内容。** Claude 被指示始终传递绝对路径。

默认情况下 Read 从文件开头返回。当全文件读取超过 token 限制时，Read 返回第一页并附带 `PARTIAL view` 通知，告诉 Claude 它收到了多少文件内容以及如何用 `offset` 和 `limit` 读取更多。传递显式 `offset` 或 `limit` 的读取如果仍超过 token 限制则返回错误。

Read 除纯文本外还处理多种文件类型：

* **图片**：PNG、JPG 等图片格式作为 Claude 可以看到的视觉内容返回，而非原始字节。Claude Code 在发送前调整大小和重新压缩大图片以适应模型的图片尺寸限制。如果 Claude 遗漏了大图片中的细微像素级细节，要求它先裁剪感兴趣区域（例如通过 Bash 使用 ImageMagick）。
* **PDF**：Claude 整体读取短 `.pdf` 文件。超过 10 页的 PDF 使用 `pages` 参数分范围读取，如 `"1-5"`，每次最多 20 页。
* **Jupyter notebook**：`.ipynb` 文件返回所有单元格及其输出，包括代码、markdown 和可视化内容。

Read 只读取文件，不读取目录。Claude 通过 Bash 工具使用 `ls` 列出目录内容。

## WebFetch 工具行为

**WebFetch 接受一个 URL 和描述要提取内容的提示。** 它获取页面，当服务器返回 HTML 时将响应转换为 Markdown，然后使用一个小而快的模型对内容运行提示。大多数获取中 Claude 收到的是该模型的回答而非原始页面。转换步骤不可配置。

这使得 WebFetch 设计上是有损的。提取提示决定什么到达 Claude，因此说页面未提及某事的结果可能只意味着提示没有问到。让 Claude 用更具体的提示重新获取，或通过 Bash 使用 `curl` 获取未处理的页面。

几个行为塑造了 Claude 收到的响应：

* HTTP URL 自动升级为 HTTPS
* 大页面在处理前截断到固定字符限制
* 响应缓存 15 分钟，重复获取同一 URL 快速返回
* 当 URL 重定向到不同主机时，WebFetch 返回命名原始 URL 和重定向目标的文本结果而非跟随。Claude 随后用第二次 WebFetch 调用获取新 URL

在默认和 `acceptEdits` 权限模式下，WebFetch 在首次访问新域名时提示，但内置的预批准文档域名集合无需提示即可获取。要预先允许另一个域名而不提示，添加权限规则如 `WebFetch(domain:example.com)`。`auto` 和 `bypassPermissions` [权限模式](https://code.claude.com/docs/en/permissions#permission-modes)完全跳过提示。

`deny`、`ask` 或 `allow` 中的显式 `WebFetch(domain:...)` 规则优先于预批准集合，因此你可以阻止预批准域名或要求对其提示。

WebFetch 设置以 `Claude-User` 开头的 `User-Agent` 头，以及偏好 Markdown 而非 HTML 的 `Accept` 头，以便支持内容协商的服务器可以直接返回 Markdown。[沙箱](https://code.claude.com/docs/en/sandboxing)网络规则单独配置，因此你希望沙箱进程访问的域名仍需显式沙箱权限规则。

## WebSearch 工具行为

**WebSearch 对 Anthropic 的 [web search](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool) 后端运行查询并返回结果标题和 URL。** 它不获取结果页面。要阅读 Claude 在搜索结果中找到的页面，它后续使用 [WebFetch](#webfetch-工具行为)。

该工具每次调用可能发出最多八次后端搜索，在返回结果前内部优化搜索。Claude 可以用 `allowed_domains` 限定只包含特定主机的结果，或用 `blocked_domains` 排除。两个列表不能在单次调用中组合。

搜索后端不可配置。要使用不同提供商搜索，添加暴露搜索工具的 [MCP 服务器](https://code.claude.com/docs/en/mcp)。

WebSearch 权限规则不接受 specifier。`allow` 或 `deny` 中的裸 `WebSearch` 条目是唯一形式。

> **注意：** WebSearch 在 Claude API 和 Microsoft Foundry 上可用。在 Google Cloud Vertex AI 上适用于 Claude 4 模型（包括 Opus、Sonnet 和 Haiku）。Amazon Bedrock 不暴露服务器端网络搜索工具。

## Write 工具行为

**Write 工具创建新文件或用提供的完整内容覆盖现有文件。** 它不追加或合并。

如果目标路径已存在，Claude 必须在当前对话中至少读取过该文件一次才能覆盖。对未读取的现有文件进行 Write 会返回错误。此约束不适用于新文件。

通过 Bash 查看文件也满足此要求，遵循 [Edit 工具行为](#edit-工具行为)中描述的相同规则。

对于现有文件的局部修改，Claude 使用 Edit 而非 Write。

## 检查哪些工具可用

你的确切工具集取决于提供商、平台和设置。要检查运行会话中加载了什么，直接问 Claude：

```text
What tools do you have access to?
```

Claude 给出会话摘要。要获取确切的 MCP 工具名称，运行 `/mcp`。

> **注意：** [advisor 工具](https://code.claude.com/docs/en/advisor)是 API 运行的[服务器工具](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool)，而非 Claude Code 实现的工具。它没有可在权限规则或 hook matcher 中引用的名称。

## 另请参阅

* [MCP 服务器](https://code.claude.com/docs/en/mcp)：通过连接外部服务器添加自定义工具
* [权限](https://code.claude.com/docs/en/permissions)：权限系统、规则语法和工具特定模式
* [Subagents](https://code.claude.com/docs/en/sub-agents)：为 subagent 配置工具访问
* [Hooks](https://code.claude.com/docs/en/hooks-guide)：在工具执行前后运行自定义命令
