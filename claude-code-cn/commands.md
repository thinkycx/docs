---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】斜杠命令
description: Claude Code 中所有可用命令的完整参考，包括内置命令和内置 Skill。覆盖从项目初始化、模型切换、权限管理到代码审查、并行任务编排等各阶段常用命令。
category: translation
tags: [claude-code, commands, translation]
refs:
  - https://code.claude.com/docs/en/commands.md
---

# 斜杠命令

> Claude Code 中所有可用命令的完整参考，包括内置命令和内置 Skill。

**命令是 Claude Code 会话内的控制指令，用于快速切换模型、管理权限、清除上下文、运行工作流等。** 输入 `/` 即可查看全部可用命令，输入 `/` 加若干字母可过滤匹配。

命令只在消息开头才会被识别。命令名后面跟的文本作为参数传入。

## 典型工作流中的命令分布

**不同阶段适合不同命令，下面按典型流程逐段梳理。**

**首次进入仓库。** 运行 `/init` 生成初始 `CLAUDE.md`，再用 `/memory` 进一步完善。用 `/mcp` 和 `/agents` 配好 MCP 服务器或子 Agent，用 `/permissions` 设置审批规则。

**任务进行中。** `/plan` 在大改动前切换到计划模式；`/model` 和 `/effort` 调整推理强度。对话过长时，`/context` 查看上下文分布，`/compact` 压缩摘要；`/btw` 可以问一个不污染对话历史的快速旁白问题。

**并行执行。** `/agents` 管理 [子 Agent](https://code.claude.com/docs/en/sub-agents)，`/tasks` 列出当前会话的后台任务。`/background` 将整个会话转为 [后台 Agent](https://code.claude.com/docs/en/agent-view) 释放终端。对跨代码库的大规模变更，`/batch` 分解为独立单元，每个在独立 [worktree](https://code.claude.com/docs/en/worktrees) 中并行执行。详见 [并行运行 Agent](https://code.claude.com/docs/en/agents)。

**发布前。** `/diff` 查看变更，`/code-review` 检查正确性 Bug 和优化点（加 `--fix` 可自动修复），`/review` 对 GitHub PR 做同样的只读审查，`/security-review` 做更深入的安全审查。`/code-review ultra` 在云端运行多 Agent 审查。

**会话之间。** `/clear` 清空上下文开始新任务但保留项目记忆。`/resume` 和 `/branch` 恢复或分叉早期对话。`/teleport` 把 Web 会话拉到终端，`/remote-control` 从另一台设备继续当前会话。

**出问题时。** `/rewind` 将代码和对话回滚到检查点，或部分摘要。`/doctor` 和 `/debug` 诊断安装和运行时问题，`/feedback` 附带会话上下文提交 Bug。

## 所有命令

**下表列出 Claude Code 中所有命令。** 大多数是内置命令，行为由 CLI 直接编码。两种特殊标记：

* **[Skill](https://code.claude.com/docs/en/skills#bundled-skills)**：内置 Skill。工作方式和你自己编写的 Skill 一样——给 Claude 一段 Prompt，Claude 在相关场景下也会自动调用。
* **[Workflow](https://code.claude.com/docs/en/workflows#bundled-workflows)**：内置[动态工作流](https://code.claude.com/docs/en/workflows)，将工作分配给多个子 Agent 并在后台运行。

如需添加自定义命令，参见 [Skills](https://code.claude.com/docs/en/skills)。

表中 `<arg>` 表示必选参数，`[arg]` 表示可选参数。

> [!NOTE]
> 并非所有命令对所有用户可见，可用性取决于平台、订阅计划和环境。例如 `/desktop` 仅在 macOS/Windows 且以 Claude 订阅登录时显示，`/upgrade` 仅对 Pro 和 Max 计划用户显示。

| 命令 | 用途 |
| :--- | :--- |
| `/add-dir <path>` | **添加工作目录。** 在当前会话中增加一个可访问的目录。大部分 `.claude/` 配置[不会从新增目录中加载](https://code.claude.com/docs/en/permissions#additional-directories-grant-file-access-not-configuration)。之后可从该目录用 `--continue` 或 `--resume` 恢复会话 |
| `/advisor [model\|off]` | **启用/禁用 Advisor 工具。** 让第二个模型在关键节点提供[指导建议](https://code.claude.com/docs/en/advisor)。接受 `opus`、`sonnet`、`fable`（v2.1.170+）或完整模型 ID。无参数时打开选择器。需 v2.1.98+ |
| `/agents` | **管理 [Agent](https://code.claude.com/docs/en/sub-agents) 配置** |
| `/autofix-pr [prompt]` | **自动修复 PR。** 启动一个 [Cloud Claude Code](https://code.claude.com/docs/en/claude-code-on-the-web#auto-fix-pull-requests) 会话，监控当前分支的 PR，CI 失败或收到 review 评论时自动推送修复。通过 `gh pr view` 检测 PR；默认修复所有 CI 失败和评论，传入 prompt 可定制，如 `/autofix-pr only fix lint and type errors`。需 `gh` CLI 和 Cloud 访问权限 |
| `/background [prompt]` | **转为后台 Agent。** 将当前会话分离为 [后台 Agent](https://code.claude.com/docs/en/agent-view) 释放终端。传入 prompt 则分离前发送一条指令。用 `claude agents` 监控。别名：`/bg` |
| `/batch <instruction>` | **[Skill] 大规模并行变更编排。** 分析代码库，将工作分解为 5-30 个独立单元并展示计划。批准后，为每个单元在独立 [git worktree](https://code.claude.com/docs/en/worktrees) 中启动一个[后台子 Agent](https://code.claude.com/docs/en/sub-agents#run-subagents-in-foreground-or-background)，分别实现、测试并开 PR。需 git 仓库。示例：`/batch migrate src/ from Solid to React` |
| `/branch [name]` | **分叉对话。** 在当前节点创建对话分支，可尝试不同方向而不丢失原对话。原对话可通过 `/resume` 返回。如果只想把侧任务交给后台子 Agent 而非自己切进去，用 `/fork` |
| `/btw <question>` | **问一个[旁白问题](https://code.claude.com/docs/en/interactive-mode#side-questions-with-%2Fbtw)，不加入对话历史** |
| `/cd <path>` | **切换工作目录。** 将会话移到新目录，Prompt Cache 保留；新目录的 [`CLAUDE.md`](https://code.claude.com/docs/en/memory) 以消息追加而非重建系统 Prompt。会话存储迁移到新目录的项目存储中。可通过 [`Cd` 权限规则](https://code.claude.com/docs/en/permissions#cd)限制或禁用。需 v2.1.169+；更早版本报 `Unknown command: /cd`。仅新增额外目录而不移动会话用 `/add-dir` |
| `/chrome` | **配置 [Claude in Chrome](https://code.claude.com/docs/en/chrome) 设置** |
| `/claude-api [migrate\|managed-agents-onboard]` | **[Skill] 加载 Claude API 参考资料。** 根据项目语言（Python、TypeScript、Java、Go、Ruby、C#、PHP、cURL）加载 API 参考和 Managed Agents 参考。涵盖工具调用、流式、Batch、结构化输出等。当代码导入 `anthropic` 或 `@anthropic-ai/sdk` 时自动激活。`/claude-api migrate` 升级现有 API 代码到更新模型；`/claude-api managed-agents-onboard` 交互式创建新 Managed Agent |
| `/clear [name]` | **清空对话开始新会话。** 前次对话保留在 `/resume` 中，传入 name 为其命名。如只想释放上下文但继续当前对话，用 `/compact`。别名：`/reset`、`/new` |
| `/code-review [level] [--fix] [--comment] [target]` | **[Skill] 审查当前 diff。** 检查正确性 Bug 和可优化项。`--fix` 自动修复，`--comment` 发 GitHub PR 行内评论，`ultra` 运行云端[深度审查](https://code.claude.com/docs/en/ultrareview)。v2.1.154 起 `/simplify` 单独运行清理审查。级别：`low`/`medium`/`high`/`xhigh`/`max`/`ultra`。详见 [本地审查 diff](https://code.claude.com/docs/en/code-review#review-a-diff-locally) |
| `/color [color\|default]` | **设置当前会话 Prompt 栏颜色。** 可选：`red`、`blue`、`green`、`yellow`、`purple`、`orange`、`pink`、`cyan`。`default` 重置，无参数随机。[Remote Control](https://code.claude.com/docs/en/remote-control) 连接时颜色同步到 claude.ai/code |
| `/compact [instructions]` | **压缩上下文。** 摘要对话释放空间，可传入摘要聚焦指令。参见[压缩如何处理规则、Skill 和记忆文件](https://code.claude.com/docs/en/context-window#what-survives-compaction) |
| `/config [key=value ...]` | **打开设置界面。** 调整主题、模型、[输出风格](https://code.claude.com/docs/en/output-styles)等。v2.1.181+ 支持直接传 `key=value` 设置，如 `/config thinking=false`。v2.1.182+ 支持简写键名，如 `/config theme=dark`。`key=value` 格式也可在非交互模式（`-p`）和 [Remote Control](https://code.claude.com/docs/en/remote-control) 中使用。`/config --help` 列出所有可设置项。别名：`/settings` |
| `/context [all]` | **可视化当前上下文使用。** 以彩色网格展示；显示优化建议（工具占用过高、记忆膨胀、容量警告）。[全屏模式](https://code.claude.com/docs/en/fullscreen)下折叠明细以保持网格可见，传 `all` 展开 |
| `/copy [N]` | **复制最后一条助手回复到剪贴板。** 传入数字 N 复制倒数第 N 条。有代码块时弹出交互选择器。在选择器中按 `w` 写入文件（SSH 场景有用） |
| `/cost` | `/usage` 的别名 |
| `/debug [description]` | **[Skill] 调试日志。** 为当前会话启用 debug 日志并排查问题。默认不开启（除非 `claude --debug` 启动）。`/debug` 从运行该命令的时间点开始捕获日志。可传入问题描述聚焦分析 |
| `/deep-research <question>` | **[Workflow] 深度研究。** 针对一个问题扇出 Web 搜索，抓取并交叉验证来源，合成带引用的研究报告 |
| `/desktop` | **在 Claude Code Desktop 应用中继续当前会话。** 需 macOS/Windows + Claude 订阅。别名：`/app` |
| `/diff` | **交互式 diff 查看器。** 显示未提交变更和每轮 diff。左右键切换 git diff 和各轮次，上下键浏览文件 |
| `/doctor` | **诊断安装和配置。** 结果显示状态图标，按 `f` 让 Claude 修复问题 |
| `/effort [level\|auto]` | **设置模型[推理强度](https://code.claude.com/docs/en/model-config#adjust-effort-level)。** 接受 `low`/`medium`/`high`/`xhigh`/`max`/`ultracode`；可用级别取决于模型，`max` 和 `ultracode` 仅当前会话生效。`ultracode` 组合了 `xhigh` 推理和自动[工作流](https://code.claude.com/docs/en/workflows#let-claude-decide-with-ultracode)编排。`auto` 重置为模型默认值。无参数时打开交互滑块，左右键选择级别、Enter 确认。立即生效无需等待当前响应完成 |
| `/exit` | **退出 CLI。** 在已附加的[后台会话](https://code.claude.com/docs/en/agent-view#attach-to-a-session)中执行此命令只是 detach，会话继续运行。别名：`/quit` |
| `/export [filename]` | **导出当前对话为纯文本。** 传入文件名直接写入；否则弹出对话框选择复制到剪贴板或保存到文件 |
| `/fast [on\|off]` | **切换 [Fast 模式](https://code.claude.com/docs/en/fast-mode)** |
| `/feedback [report]` | **提交反馈、报 Bug 或分享对话。** 别名：`/bug`、`/share` |
| `/fewer-permission-prompts` | **[Skill] 减少权限弹窗。** 扫描你的 Transcript，找出常见只读 Bash 和 MCP 工具调用，将白名单写入项目 `.claude/settings.json` |
| `/focus` | **切换聚焦视图。** 只显示最后的 Prompt、一行工具摘要（含 edit diffstat）和最终响应。设置持续跨会话；可通过 [`viewMode`](https://code.claude.com/docs/en/settings#available-settings) 覆盖。仅在[全屏渲染](https://code.claude.com/docs/en/fullscreen)下可用 |
| `/fork <directive>` | **派生子 Agent。** 启动一个[分叉子 Agent](https://code.claude.com/docs/en/sub-agents#fork-the-current-conversation)：继承完整对话，在后台执行指令，完成后结果返回你的对话。自己切进分支用 `/branch`。v2.1.161 之前 `/fork` 是 `/branch` 的别名 |
| `/goal [condition\|clear]` | **设置[目标](https://code.claude.com/docs/en/goal)。** Claude 跨轮持续工作直到条件满足。无参数时显示当前/最近达成的目标。`clear`/`stop`/`off`/`reset`/`none`/`cancel` 提前移除 |
| `/heapdump` | **输出 JS 堆快照和内存明细到 `~/Desktop`（Linux 无 Desktop 时写入 home）。** 用于诊断高内存占用。参见[故障排查](https://code.claude.com/docs/en/troubleshooting#high-cpu-or-memory-usage) |
| `/help` | **显示帮助和可用命令** |
| `/hooks` | **查看 [Hook](https://code.claude.com/docs/en/hooks) 配置** |
| `/ide` | **管理 IDE 集成并显示状态** |
| `/init` | **初始化项目 `CLAUDE.md`。** 设置 `CLAUDE_CODE_NEW_INIT=1` 可开启交互式流程，同时配置 Skill、Hook 和个人记忆文件 |
| `/insights` | **生成使用分析报告。** 包含项目区域、交互模式、摩擦点等 |
| `/install-github-app` | **安装 Claude GitHub App。** 可选步骤配置 [GitHub Actions](https://code.claude.com/docs/en/github-actions) 工作流和密钥 |
| `/install-slack-app` | **安装 Claude Slack App。** 打开浏览器完成 OAuth 流程 |
| `/keybindings` | **打开[键盘快捷键](https://code.claude.com/docs/en/keybindings)文件** |
| `/login` | **登录 Anthropic 账号** |
| `/logout` | **登出 Anthropic 账号** |
| `/loop [interval] [prompt]` | **[Skill] 循环执行 Prompt。** 省略 interval 时 Claude 自行控制节奏。省略 prompt 时（[如有](https://code.claude.com/docs/en/scheduled-tasks#run-the-built-in-maintenance-prompt)）运行自主维护检查或 `.claude/loop.md` 中的 Prompt。示例：`/loop 5m check if the deploy finished`。参见[定时任务](https://code.claude.com/docs/en/scheduled-tasks)。别名：`/proactive` |
| `/mcp [reconnect <server>\|enable\|disable [<server>\|all]]` | **管理 MCP 服务器连接和 OAuth 认证。** 无参数打开交互列表；`reconnect <server>` 重连断开的服务器；`enable`/`disable` 加服务器名或 `all` 切换连接状态 |
| `/memory` | **编辑 `CLAUDE.md` 记忆文件，** 启用/禁用[自动记忆](https://code.claude.com/docs/en/memory#auto-memory)，查看自动记忆条目 |
| `/mobile` | **显示下载 Claude 移动端 App 的二维码。** 别名：`/ios`、`/android` |
| `/model [model]` | **切换 AI 模型并保存为新会话默认值。** 支持左右键[调整推理强度](https://code.claude.com/docs/en/model-config#adjust-effort-level)。无参数打开选择器；按 `s` 仅对当前会话切换。对话中已有输出时会要求确认（因为下次响应需重新读取完整历史且无缓存）。确认后立即生效 |
| `/passes` | **分享 Claude Code 免费周。** 仅在账号符合条件时可见 |
| `/permissions` | **管理工具权限的 allow/ask/deny 规则。** 打开交互对话框查看各范围规则、增删规则、管理工作目录、查看 [auto 模式近期拒绝记录](https://code.claude.com/docs/en/auto-mode-config#review-denials)。别名：`/allowed-tools` |
| `/plan [description]` | **进入计划模式。** 传入描述可立即开始该任务，如 `/plan fix the auth bug` |
| `/plugin [subcommand]` | **管理 [插件](https://code.claude.com/docs/en/plugins)。** 无参数打开插件菜单；子命令：`list`、`install`、`enable`、`disable` |
| `/powerup` | **通过交互式动画演示发现 Claude Code 功能** |
| `/pr-comments [PR]` | **（已移除）** v2.1.91 移除。请直接让 Claude 查看 PR 评论。早期版本中可获取 GitHub PR 评论，自动检测当前分支 PR 或传入 URL/编号。需 `gh` CLI |
| `/privacy-settings` | **查看和更新隐私设置。** 仅 Pro/Max 计划用户可用 |
| `/radio` | **在浏览器打开 Claude FM lo-fi 电台。** 无浏览器时输出流 URL。Bedrock/Vertex/Foundry 不可用 |
| `/recap` | **按需生成当前会话的一行摘要。** 参见[自动 Session Recap](https://code.claude.com/docs/en/interactive-mode#session-recap) |
| `/release-notes` | **查看更新日志。** 交互式版本选择器，可选具体版本或显示全部 |
| `/reload-plugins [--force]` | **重新加载所有活跃[插件](https://code.claude.com/docs/en/plugins)。** 无需重启即应用更改。报告各组件重载数量和加载错误。当重载会变更 MCP 工具并使 Prompt Cache 失效时发出警告，需 `--force` 强制执行 |
| `/reload-skills` | **重新扫描 [Skill](https://code.claude.com/docs/en/skills) 和命令目录。** 会话中新增或修改的 Skill 无需重启即可使用。报告可用数量和增减情况。v2.1.152+ 可用 |
| `/remote-control` | **开启[远程控制](https://code.claude.com/docs/en/remote-control)，** 从 claude.ai 操控当前会话。别名：`/rc` |
| `/remote-env` | **选择[云端 Agent](https://code.claude.com/docs/en/claude-code-on-the-web#configure-your-environment) 的默认环境** |
| `/rename [name]` | **重命名当前会话并在 Prompt 栏显示。** 无参数时从对话历史自动生成 |
| `/resume [session]` | **恢复对话。** 通过 ID 或名称恢复，或打开会话选择器。v2.1.144 起[后台会话](https://code.claude.com/docs/en/agent-view)在选择器中标记 `bg`。别名：`/continue` |
| `/review [PR]` | **审查 GitHub PR。** 使用与 `/code-review` 相同的引擎。无参数列出可选 PR。云端审查见 [`/code-review ultra`](https://code.claude.com/docs/en/ultrareview) |
| `/rewind` | **回滚对话和/或代码到之前的检查点，或从选定消息摘要。** 参见[检查点机制](https://code.claude.com/docs/en/checkpointing)。别名：`/checkpoint`、`/undo` |
| `/run` | **[Skill] 运行应用。** 启动并驱动项目应用，直接在运行中验证变更。参见[运行和验证应用](https://code.claude.com/docs/en/skills#run-and-verify-your-app)。需 v2.1.145+ |
| `/run-skill-generator` | **[Skill] 生成 run Skill。** 教会 `/run` 和 `/verify` 如何从干净环境构建和启动项目，写入项目级 Skill。需 v2.1.145+ |
| `/sandbox` | **切换[沙盒模式](https://code.claude.com/docs/en/sandboxing)。** 仅支持平台可用 |
| `/schedule [description]` | **创建、更新、列出或运行 [Routine](https://code.claude.com/docs/en/routines)。** 在 Anthropic 托管的云基础设施上执行，Claude 以对话方式引导配置。别名：`/routines` |
| `/scroll-speed` | **调整鼠标滚轮[滚动速度](https://code.claude.com/docs/en/fullscreen#mouse-wheel-scrolling)。** 对话框打开时可一边滚动一边预览效果。仅[全屏渲染](https://code.claude.com/docs/en/fullscreen)可用，JetBrains IDE 终端不适用 |
| `/security-review` | **安全审查。** 分析当前分支待提交变更的安全漏洞：注入、认证问题、数据泄露等 |
| `/setup-bedrock` | **配置 [Amazon Bedrock](https://code.claude.com/docs/en/amazon-bedrock)。** 通过交互向导设置认证、Region 和模型。仅 `CLAUDE_CODE_USE_BEDROCK=1` 时可见。首次使用可从登录界面进入 |
| `/setup-vertex` | **配置 [Google Vertex AI](https://code.claude.com/docs/en/google-vertex-ai)。** 通过交互向导设置认证、项目、Region 和模型。仅 `CLAUDE_CODE_USE_VERTEX=1` 时可见。首次使用可从登录界面进入 |
| `/simplify [target]` | **[Skill] 清理优化代码。** 四个审查 [Agent](https://code.claude.com/docs/en/sub-agents) 并行运行，覆盖：复用已有 helper、简化、效率优化、抽象层级是否合理。v2.1.154+ 不再检查正确性 Bug（正确性用 `/code-review`）。早期版本等同于 `/code-review --fix`。可传入路径或 PR 引用 |
| `/skills` | **列出可用 [Skill](https://code.claude.com/docs/en/skills)。** 按 `t` 按 Token 数排序。按 `Space` [隐藏 Skill 不对 Claude 或 `/` 菜单可见](https://code.claude.com/docs/en/skills#override-skill-visibility-from-settings)，按 `Enter` 保存 |
| `/stats` | `/usage` 的别名，打开 Stats 标签页 |
| `/status` | **打开设置界面（Status 标签页）。** 显示版本、模型、账号和连接状态。Claude 正在响应时也可使用 |
| `/statusline` | **配置 [Status Line](https://code.claude.com/docs/en/statusline)。** 描述你想显示的内容，或无参数从 shell prompt 自动配置 |
| `/stickers` | **订购 Claude Code 贴纸** |
| `/stop` | **停止当前[后台会话](https://code.claude.com/docs/en/agent-view)。** 仅在 attach 到后台会话时可用；transcript 和 worktree 保留。detach 而不停止用 `/exit` 或按 `←` |
| `/tasks` | **查看和管理所有后台运行任务。** 别名：`/bashes` |
| `/team-onboarding` | **生成团队 Onboarding 指南。** 从过去 30 天的 Claude Code 使用历史分析命令、MCP 服务器用量，生成 Markdown 指南。Pro/Max/Team/Enterprise 用户还会获得可分享链接 |
| `/teleport` | **将 [Cloud 会话](https://code.claude.com/docs/en/claude-code-on-the-web#from-web-to-terminal)拉到终端。** 打开选择器，获取分支和对话。别名：`/tp`。需 claude.ai 订阅 |
| `/terminal-setup` | **配置终端键绑定（Shift+Enter 等）。** 仅在需要的终端中可见（VS Code、Cursor、Devin Desktop、Alacritty、Zed） |
| `/theme` | **更换颜色主题。** 包含 `auto`（跟随终端明暗）、明暗变体、色盲友好（daltonized）主题、ANSI 主题（使用终端调色板）和 `~/.claude/themes/` 或插件中的[自定义主题](https://code.claude.com/docs/en/terminal-config#create-a-custom-theme)。可选 **New custom theme...** 创建新主题 |
| `/tui [default\|fullscreen]` | **切换终端 UI 渲染器并重新启动（保留对话）。** `fullscreen` 启用[无闪烁 alt-screen 渲染](https://code.claude.com/docs/en/fullscreen)。无参数时打印当前渲染器 |
| `/ultraplan <prompt>` | **在 [Ultraplan](https://code.claude.com/docs/en/ultraplan) 会话中起草计划，** 在浏览器中审阅，然后远程执行或发回终端 |
| `/ultrareview [PR]` | **在云端沙盒中运行深度多 Agent 代码审查（[Ultrareview](https://code.claude.com/docs/en/ultrareview)）。** 推荐用 `/code-review ultra` 调用，`/ultrareview` 保留为别名。Pro/Max 含 3 次免费，之后需[用量积分](https://support.claude.com/en/articles/12429409-extra-usage-for-paid-claude-plans) |
| `/upgrade` | **打开升级页面切换更高订阅计划** |
| `/usage` | **显示会话费用、计划用量上限和活动统计。** Pro/Max/Team/Enterprise 计划包含按 Skill、子 Agent、插件和 MCP 服务器的用量明细。参见[费用追踪指南](https://code.claude.com/docs/en/costs#using-the-%2Fusage-command)。别名：`/cost`、`/stats` |
| `/usage-credits` | **配置用量积分，** 达到上限后继续使用。之前名为 `/extra-usage` |
| `/verify` | **[Skill] 验证代码变更。** 构建并运行应用观察结果，而非依赖测试或类型检查。参见[运行和验证应用](https://code.claude.com/docs/en/skills#run-and-verify-your-app)。需 v2.1.145+ |
| `/vim` | **（已移除）** v2.1.92 移除。切换 Vim/Normal 编辑模式请用 `/config` → Editor mode |
| `/voice [hold\|tap\|off]` | **切换[语音输入](https://code.claude.com/docs/en/voice-dictation)，** 或指定模式。需 Claude.ai 账号 |
| `/web-setup` | **连接 GitHub 账号到 [Cloud Claude Code](https://code.claude.com/docs/en/web-quickstart#connect-from-your-terminal)。** 使用本地 `gh` CLI 凭据。`/schedule` 在 GitHub 未连接时自动提示 |
| `/workflows` | **打开[工作流](https://code.claude.com/docs/en/workflows#watch-the-run)进度视图，** 查看、暂停、恢复或保存运行中和已完成的工作流 |

## MCP Prompts

**MCP 服务器可以暴露 Prompt，这些 Prompt 以命令形式出现。** 格式为 `/mcp__<server>__<prompt>`，从已连接的服务器动态发现。详见 [MCP Prompts](https://code.claude.com/docs/en/mcp#use-mcp-prompts-as-commands)。

## 另请参阅

* [Skills](https://code.claude.com/docs/en/skills)：创建自定义命令
* [交互模式](https://code.claude.com/docs/en/interactive-mode)：键盘快捷键、Vim 模式和命令历史
* [CLI 参考](https://code.claude.com/docs/en/cli-reference)：启动时参数
