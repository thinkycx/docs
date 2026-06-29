---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】Claude Code 设置
description: Claude Code 的完整配置体系，包括多层级作用域（managed/user/project/local）、settings.json 所有可用配置项、权限规则、托管设置部署方式，以及环境变量参考。
category: translation
tags: [claude-code, settings, configuration, translation]
refs:
  - https://code.claude.com/docs/en/settings.md
---

# Claude Code 设置

> 通过全局和项目级配置以及环境变量来定制 Claude Code 的行为。

**Claude Code 提供丰富的配置选项来适应不同场景。** 运行 `/config` 命令可以打开标签式设置界面，查看状态信息并修改配置。从 v2.1.181 开始，也可以直接传入 `key=value` 来修改单个选项而无需打开界面，例如 `/config verbose=true`。

## 配置作用域

**Claude Code 采用分层作用域系统来决定配置的生效范围和共享方式。** 理解作用域有助于在个人使用、团队协作和企业部署场景中做出正确的配置选择。

### 可用作用域

| 作用域 | 存储位置 | 影响范围 | 是否与团队共享 |
| :--- | :--- | :--- | :--- |
| **Managed（托管）** | 服务端管理的设置、plist/注册表，或系统级 `managed-settings.json` | 服务端下发：影响所有组织成员；plist/HKLM 注册表/文件：影响本机所有用户；HKCU 注册表：仅影响当前用户 | 是（由 IT 部署） |
| **User（用户）** | `~/.claude/` 目录 | 你本人，跨所有项目 | 否 |
| **Project（项目）** | 仓库中 `.claude/` 目录 | 该仓库的所有协作者 | 是（提交到 git） |
| **Local（本地）** | `.claude/settings.local.json` | 你本人，仅限当前仓库 | 否（Claude Code 创建时会自动 gitignore） |

### 各作用域适用场景

**Managed 作用域** 适合：
- 组织级别必须强制执行的安全策略
- 不可被覆盖的合规要求
- 由 IT/DevOps 统一部署的标准化配置

**User 作用域** 适合：
- 希望在所有项目中生效的个人偏好（主题、编辑器设置）
- 跨项目使用的工具和插件
- API 密钥和认证信息（安全存储）

**Project 作用域** 适合：
- 团队共享设置（权限、hooks、MCP 服务器）
- 全团队应该使用的插件
- 在协作者之间标准化工具链

**Local 作用域** 适合：
- 针对特定项目的个人覆盖
- 共享给团队前先测试配置
- 不适用于其他人的机器特定设置

### 作用域优先级

**同一配置出现在多个作用域时，按以下优先级从高到低生效：**

1. **Managed**（最高）：不可被任何其他作用域覆盖
2. **命令行参数**：临时会话覆盖
3. **Local**：覆盖 project 和 user 设置
4. **Project**：覆盖 user 设置
5. **User**（最低）：仅在其他作用域未指定时生效

例如，如果 user 设置将 `spinnerTipsEnabled` 设为 `true`，而 project 设置将其设为 `false`，则 project 的值生效。权限规则的行为有所不同——它们会**跨作用域合并**，而非覆盖。

### 各功能对应的存储位置

| 功能 | User 位置 | Project 位置 | Local 位置 |
| :--- | :--- | :--- | :--- |
| **Settings** | `~/.claude/settings.json` | `.claude/settings.json` | `.claude/settings.local.json` |
| **Subagents** | `~/.claude/agents/` | `.claude/agents/` | 无 |
| **MCP servers** | `~/.claude.json` | `.mcp.json` | `~/.claude.json`（按项目） |
| **Plugins** | `~/.claude/settings.json` | `.claude/settings.json` | `.claude/settings.local.json` |
| **CLAUDE.md** | `~/.claude/CLAUDE.md` | `CLAUDE.md` 或 `.claude/CLAUDE.md` | `CLAUDE.local.md` |

在 Windows 上，`~/.claude` 路径解析为 `%USERPROFILE%\.claude`。

---

## Settings 文件

**`settings.json` 是 Claude Code 的官方分层配置机制。**

- **用户设置**：定义在 `~/.claude/settings.json`，应用于所有项目。
- **项目设置**：存放在项目目录中：
  - `.claude/settings.json`：提交到版本控制、与团队共享的设置
  - `.claude/settings.local.json`：不提交的设置，适合个人偏好和实验。Claude Code 创建此文件时会自动配置 git 忽略它；手动创建则需要自行添加到 gitignore。
- **托管设置**：面向需要集中管控的组织，Claude Code 支持多种下发机制。所有机制使用相同的 JSON 格式，且不可被用户或项目设置覆盖。
- **其他配置**：存储在 `~/.claude.json` 中，包含 OAuth 会话、user 和 local 作用域的 MCP 服务器配置、按项目的状态（已允许的工具、信任设置）以及各种缓存。项目作用域的 MCP 服务器单独存储在 `.mcp.json` 中。

### settings.json 示例

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test *)",
      "Read(~/.zshrc)"
    ],
    "deny": [
      "Bash(curl *)",
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ]
  },
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp"
  },
  "companyAnnouncements": [
    "Welcome to Acme Corp! Review our code guidelines at docs.acme.com",
    "Reminder: Code reviews required for all PRs",
    "New security policy in effect"
  ]
}
```

### 配置何时生效

**大部分配置修改后会被实时监控并重新加载，无需重启即可生效。** 这包括 `permissions`、`hooks`、`apiKeyHelper` 等。

以下配置在会话启动时读取一次，需要重启才能生效：
- `model`：会话中可以用 `/model` 切换
- `outputStyle`：系统提示词的一部分，在 `/clear` 或重启时重建

### 所有可用配置项

`settings.json` 支持以下配置项：

| 配置项 | 说明 | 示例 |
| :--- | :--- | :--- |
| `advisorModel` | 服务端 advisor 工具使用的模型。支持模型别名如 `"opus"`、`"sonnet"`、`"fable"`（v2.1.170+），或完整模型 ID。运行 `/advisor` 时自动写入，清除可禁用 advisor。需要 v2.1.98+ | `"opus"` |
| `agent` | 将主线程作为指定子代理运行，并设为 `claude agents` 分派会话的默认代理。会应用该子代理的系统提示词、工具限制和模型 | `"code-reviewer"` |
| `agentPushNotifEnabled` | **默认**：`false`。Remote Control 连接时，允许 Claude 向手机发送主动推送通知（如长任务完成时）。需要 v2.1.119+ | `true` |
| `allowAllClaudeAiMcps` | （仅 Managed）部署 `managed-mcp.json` 时仍加载 claude.ai 连接器（否则 managed-mcp.json 会独占控制并抑制它们） | `true` |
| `allowedHttpHookUrls` | HTTP hooks 可访问的 URL 白名单，支持 `*` 通配符。设置后不匹配的 URL 会被阻止。未定义=不限制，空数组=全部阻止。跨配置源合并 | `["https://hooks.example.com/*"]` |
| `allowedMcpServers` | （仅 Managed）用户可配置的 MCP 服务器白名单。未定义=不限制，空数组=全部禁止。黑名单优先于白名单 | `[{ "serverName": "github" }]` |
| `allowManagedHooksOnly` | （仅 Managed）仅加载 managed hooks、SDK hooks 和 managed 中 `enabledPlugins` 强制启用的插件 hooks，阻止用户和项目的 hooks | `true` |
| `allowManagedMcpServersOnly` | （仅 Managed）仅 managed 中的 `allowedMcpServers` 生效。`deniedMcpServers` 仍然跨所有来源合并 | `true` |
| `allowManagedPermissionRulesOnly` | （仅 Managed）阻止用户和项目设置定义 `allow`/`ask`/`deny` 权限规则，仅 managed 中的规则生效 | `true` |
| `alwaysThinkingEnabled` | 所有会话默认启用扩展思考。通常通过 `/config` 配置。设置 `MAX_THINKING_TOKENS=0` 可强制关闭思考（Fable 5 除外，其无法关闭思考） | `true` |
| `apiKeyHelper` | 自定义命令（通过系统 shell 执行），生成认证值。该值作为 `X-Api-Key` 和 `Authorization: Bearer` 头发送。刷新间隔由 `CLAUDE_CODE_API_KEY_HELPER_TTL_MS` 控制 | `/bin/generate_temp_api_key.sh` |
| `attribution` | 自定义 git 提交和 PR 的署名。详见署名设置 | `{"commit": "🤖 Generated with Claude Code", "pr": ""}` |
| `autoCompactEnabled` | **默认**：`true`。上下文接近限制时自动压缩对话。环境变量 `DISABLE_AUTO_COMPACT` 可禁用 | `false` |
| `autoMemoryDirectory` | 自动记忆的自定义存储目录。接受绝对路径或 `~/` 前缀路径 | `"~/my-memory-dir"` |
| `autoMemoryEnabled` | **默认**：`true`。启用自动记忆。设为 `false` 后 Claude 不再读写自动记忆目录。会话中可用 `/memory` 切换 | `false` |
| `autoMode` | 自定义 auto 模式分类器的阻止和允许规则。包含 `environment`、`allow`、`soft_deny`、`hard_deny` 数组。数组中包含 `"$defaults"` 可继承内置规则。不从共享项目设置读取 | `{"soft_deny": ["$defaults", "Never run terraform apply"]}` |
| `autoScrollEnabled` | **默认**：`true`。全屏渲染时跟随新输出滚动到底部 | `false` |
| `autoUpdatesChannel` | **默认**：`"latest"`。更新频道。`"stable"` 通常延迟约一周发布并跳过有重大回退的版本。环境变量 `DISABLE_AUTOUPDATER` 可完全禁用自动更新 | `"stable"` |
| `availableModels` | 限制用户可选的模型范围（主会话、子代理、技能和 advisor 都受影响） | `["sonnet", "haiku"]` |
| `awaySummaryEnabled` | 离开终端几分钟后返回时显示一行会话摘要。设为 `false` 或在 `/config` 关闭 Session recap 可禁用 | `true` |
| `awsAuthRefresh` | 刷新 AWS 凭证的自定义脚本 | `aws sso login --profile myprofile` |
| `awsCredentialExport` | 输出 AWS 凭证 JSON 的自定义脚本 | `/bin/generate_aws_grant.sh` |
| `axScreenReader` | 渲染屏幕阅读器友好的输出：纯文本、无装饰边框和动画。强制使用经典渲染器。环境变量 `CLAUDE_AX_SCREEN_READER` 和 `--ax-screen-reader` 标志优先。需要 v2.1.181+ | `true` |
| `blockedMarketplaces` | （仅 Managed）市场黑名单。在插件安装、更新、刷新和自动更新时强制执行 | `[{ "source": "github", "repo": "untrusted/plugins" }]` |
| `channelsEnabled` | （仅 Managed）为组织启用 channels。Claude.ai Team/Enterprise 计划中未设置或 `false` 时 channels 被阻止 | `true` |
| `claudeMd` | （仅 Managed）作为组织托管记忆注入的 CLAUDE.md 风格指令。仅在 managed 或 policy 设置中生效 | `"Always run make lint before committing."` |
| `claudeMdExcludes` | 加载记忆时跳过的 `CLAUDE.md` 文件的 glob 模式或绝对路径 | `["**/vendor/**/CLAUDE.md"]` |
| `cleanupPeriodDays` | **默认**：`30` 天，最小 `1`。超过此天数的会话文件在启动时删除。也控制孤立子代理 worktree 的自动清理 | `20` |
| `companyAnnouncements` | 启动时向用户显示的公告。多条时随机展示 | `["Welcome to Acme Corp!"]` |
| `defaultShell` | **默认**：`"bash"`（Windows 上无 Bash 时为 `"powershell"`）。输入框 `!` 命令的默认 shell | `"powershell"` |
| `deniedMcpServers` | （仅 Managed）被显式阻止的 MCP 服务器黑名单。黑名单优先于白名单 | `[{ "serverName": "filesystem" }]` |
| `disableAgentView` | 关闭后台代理和代理视图：`claude agents`、`--bg`、`/background` 以及按需 supervisor | `true` |
| `disableAllHooks` | 禁用所有 hooks 和自定义状态行 | `true` |
| `disableArtifact` | 禁用 Artifact 工具（将会话输出发布为 claude.ai 上的私有网页） | `true` |
| `disableAutoMode` | 设为 `"disable"` 阻止 auto 模式激活。从 `Shift+Tab` 循环中移除 `auto`，拒绝 `--permission-mode auto` | `"disable"` |
| `disableBundledSkills` | 禁用 Claude Code 自带的技能和工作流。内置斜杠命令如 `/init` 仍可输入但对模型隐藏。插件和 `.claude/skills/` 中的技能不受影响 | `true` |
| `disableClaudeAiConnectors` | 禁用 claude.ai MCP 连接器，不自动获取或连接。任何来源中设为 `true` 都会生效（项目级 `false` 无法覆盖用户或策略级的 `true`） | `true` |
| `disableDeepLinkRegistration` | 设为 `"disable"` 阻止注册 `claude-cli://` 协议处理器 | `"disable"` |
| `disabledMcpjsonServers` | 拒绝 `.mcp.json` 中指定名称的 MCP 服务器 | `["filesystem"]` |
| `disableRemoteControl` | 禁用 Remote Control：阻止 `claude remote-control`、`--remote-control` 标志、自动启动和会话内开关。需要 v2.1.128+ | `true` |
| `disableSkillShellExecution` | 禁用技能和自定义命令中 `` !`...` `` 和 ` ```! ` 块的内联 shell 执行。Bundled 和 managed 技能不受影响 | `true` |
| `disableWorkflows` | **默认**：`false`。禁用动态工作流和内置工作流命令 | `true` |
| `editorMode` | **默认**：`"normal"`。输入提示的键绑定模式：`"normal"` 或 `"vim"` | `"vim"` |
| `effortLevel` | 跨会话持久化的努力等级。接受 `"low"`、`"medium"`、`"high"` 或 `"xhigh"`。`--effort` 和 `CLAUDE_CODE_EFFORT_LEVEL` 可覆盖 | `"xhigh"` |
| `enableAllProjectMcpServers` | 自动批准项目 `.mcp.json` 中定义的所有 MCP 服务器 | `true` |
| `enabledMcpjsonServers` | 批准 `.mcp.json` 中指定名称的 MCP 服务器 | `["memory", "github"]` |
| `enforceAvailableModels` | 将 `availableModels` 白名单扩展到 Default 模型。设为 `true` 时 Default 选项回退到白名单中第一个可用项。需要 v2.1.175+ | `true` |
| `env` | 应用于每个会话及其子进程的环境变量。v2.1.143 起 `NO_COLOR`/`FORCE_COLOR` 传递给子进程但不改变 Claude Code 界面颜色 | `{"FOO": "bar"}` |
| `fallbackModel` | 主模型过载或不可用时按顺序尝试的备用模型。`"default"` 展开为默认模型。链最多三个模型。不跨配置文件合并 | `["claude-sonnet-4-6", "claude-haiku-4-5"]` |
| `fastModePerSessionOptIn` | 设为 `true` 时快速模式不跨会话持久化，每个会话需手动用 `/fast` 启用 | `true` |
| `feedbackSurveyRate` | 会话质量调查出现的概率（0–1）。设为 `0` 完全抑制 | `0.05` |
| `fileCheckpointingEnabled` | **默认**：`true`。每次编辑前创建文件快照以支持 `/rewind` 恢复 | `false` |
| `fileSuggestion` | 为 `@` 文件自动补全配置自定义脚本 | `{"type": "command", "command": "~/.claude/file-suggestion.sh"}` |
| `footerLinksRegexes` | 正则匹配轮次输出时在页脚渲染可点击徽章。需要 v2.1.176+ | `[{"type": "regex", "pattern": "\\b(?<key>PROJ-\\d+)\\b", "url": "https://issues.example.com/browse/{key}", "label": "{key}"}]` |
| `forceLoginMethod` | 限制登录方式：`claudeai` 仅 Claude.ai 账户，`console` 仅 Console 账户。设为 managed 时会阻止 API 密钥认证的会话 | `"claudeai"` |
| `forceLoginOrgUUID` | 要求登录属于指定 Anthropic 组织。接受单个 UUID 或 UUID 数组。空数组会失败并阻止登录 | `"xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"` |
| `forceRemoteSettingsRefresh` | （仅 Managed）阻塞 CLI 启动直到远程托管设置从服务器刷新完成。获取失败则 CLI 退出而非使用缓存 | `true` |
| `gcpAuthRefresh` | GCP 凭证过期时刷新 Application Default Credentials 的自定义脚本 | `gcloud auth application-default login` |
| `hooks` | 在生命周期事件时运行的自定义命令。详见 [hooks 文档](https://code.claude.com/docs/en/hooks) | 见 hooks 文档 |
| `httpHookAllowedEnvVars` | HTTP hooks 可内插到头部的环境变量白名单。设置后每个 hook 的有效 `allowedEnvVars` 为与此列表的交集 | `["MY_TOKEN", "HOOK_SECRET"]` |
| `includeGitInstructions` | **默认**：`true`。在系统提示词中包含内置的 commit/PR 工作流指令和 git status 快照。设为 `false` 可移除（如使用自定义 git 工作流技能时） | `false` |
| `inputNeededNotifEnabled` | **默认**：`false`。权限提示或问题等待输入时向手机发送推送通知。需要 v2.1.119+ | `true` |
| `language` | 配置 Claude 的首选回复语言。也影响语音听写和自动生成的会话标题。v2.1.176 起未设置时会话标题匹配对话语言 | `"japanese"` |
| `maxSkillDescriptionChars` | **默认**：`1536`。每个技能在 Claude 每轮看到的技能列表中 `description` + `when_to_use` 的字符上限。增大保留长描述但消耗更多上下文 | `2048` |
| `minimumVersion` | 防止自动更新和 `claude update` 安装低于此版本的版本。不阻止启动（阻止启动用 `requiredMinimumVersion`） | `"2.1.100"` |
| `model` | 覆盖默认模型。`--model` 和 `ANTHROPIC_MODEL` 可在会话级别覆盖 | `"claude-sonnet-4-6"` |
| `modelOverrides` | 将 Anthropic 模型 ID 映射到提供商特定 ID（如 Bedrock inference profile ARN） | `{"claude-opus-4-6": "arn:aws:bedrock:..."}` |
| `otelHeadersHelper` | 生成动态 OpenTelemetry 头的脚本。启动时和定期运行。刷新间隔由 `CLAUDE_CODE_OTEL_HEADERS_HELPER_DEBOUNCE_MS` 控制 | `/bin/generate_otel_headers.sh` |
| `outputStyle` | 调整系统提示词的输出风格 | `"Explanatory"` |
| `parentSettingsBehavior` | （仅 Managed）**默认**：`"first-wins"`。控制嵌入宿主进程（如 Agent SDK）提供的 managed 设置在已有 admin 部署层时是否生效。`"merge"` 允许在 admin 层下面生效但只能收紧策略 | `"merge"` |
| `permissions` | 权限规则配置，详见下方权限配置部分 | |
| `plansDirectory` | **默认**：`~/.claude/plans`。计划文件的存储路径 | `"./plans"` |
| `pluginSuggestionMarketplaces` | （仅 Managed）允许出现上下文安装建议的市场名称列表 | `["acme-corp-plugins"]` |
| `pluginTrustMessage` | （仅 Managed）附加到插件安装前信任警告的自定义消息 | `"All plugins from our marketplace are approved by IT"` |
| `policyHelper` | 启动时动态计算 managed 设置的管理员部署可执行文件。仅从 MDM 或系统级 `managed-settings.json` 中生效。需要 v2.1.136+ | `{"path": "/usr/local/bin/claude-policy"}` |
| `preferredNotifChannel` | **默认**：`"auto"`。通知方式：`"auto"`、`"terminal_bell"`、`"iterm2"`、`"iterm2_with_bell"`、`"kitty"`、`"ghostty"` 或 `"notifications_disabled"` | `"terminal_bell"` |
| `prefersReducedMotion` | 减少或禁用 UI 动画（加载动画、闪烁效果等），用于无障碍 | `true` |
| `prUrlTemplate` | PR 徽章的 URL 模板。支持 `{host}`、`{owner}`、`{repo}`、`{number}`、`{url}` 替换。可用于将 PR 链接指向内部代码评审工具 | `"https://reviews.example.com/{owner}/{repo}/pull/{number}"` |
| `remoteControlAtStartup` | 每个交互式会话启动时自动连接 Remote Control。`true` 总是自动连接，`false` 永不自动连接 | `false` |
| `requiredMaximumVersion` | （仅 Managed）允许启动的最大版本。超过则退出并提示安装批准版本。自动更新和 `claude update` 跳过超出上限的版本 | `"2.1.150"` |
| `requiredMinimumVersion` | （仅 Managed）允许启动的最小版本。低于则退出并提示更新。`claude update`/`install`/`doctor` 在低于下限时仍可工作以便恢复 | `"2.1.150"` |
| `respectGitignore` | **默认**：`true`。`@` 文件选择器是否遵守 `.gitignore` 模式 | `false` |
| `respondToBashCommands` | **默认**：`true`。输入框 `!` shell 命令执行后是否让 Claude 回复。设为 `false` 则仅将命令输出加入上下文而不触发回复。需要 v2.1.186+ | `false` |

---

## 权限配置

**`permissions` 对象控制 Claude 可以免确认使用哪些工具。**

| 字段 | 说明 |
| :--- | :--- |
| `permissions.allow` | 允许无需确认直接执行的工具模式列表 |
| `permissions.deny` | 始终阻止的工具模式列表 |
| `permissions.ask` | 需要用户确认的工具模式列表 |

权限规则使用 `ToolName(pattern)` 格式，`*` 为通配符。

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test *)",
      "Read(~/.zshrc)"
    ],
    "deny": [
      "Bash(curl *)",
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ]
  }
}
```

### 权限合并规则

**权限规则与标量设置不同，它们跨作用域合并而非覆盖。** 所有作用域的规则会被组合在一起，deny 规则无论来自哪个作用域都优先于 allow 规则。

---

## Hook 配置

**`hooks` 设置用于在生命周期事件时运行自定义命令。**

- `allowedHttpHookUrls`：限制 HTTP hooks 可访问的 URL（支持通配符模式）
- `httpHookAllowedEnvVars`：控制 HTTP hooks 可内插到头部的环境变量
- `allowManagedHooksOnly` 设为 `true` 时（仅 Managed），仅 managed hooks、SDK hooks 和 managed `enabledPlugins` 中强制启用的插件 hooks 被加载，用户和项目的 hooks 被阻止

---

## 署名设置

**`attribution` 配置自定义 git 提交和 PR 的署名文本。**

```json
{
  "attribution": {
    "commit": "🤖 Generated with Claude Code",
    "pr": ""
  }
}
```

---

## 文件建议设置

**`fileSuggestion` 为 `@` 文件自动补全配置自定义脚本。**

```json
{
  "fileSuggestion": {
    "type": "command",
    "command": "~/.claude/file-suggestion.sh"
  }
}
```

---

## 页脚链接徽章

**`footerLinksRegexes` 在正则匹配轮次输出时渲染可点击的页脚徽章。** 每个条目包含 `pattern`（正则）、`url` 模板（用命名捕获组中的 `{name}` 占位符填充）和可选 `label`。仅从 user、`--settings` 标志和 managed 设置读取。需要 v2.1.176+。

```json
{
  "footerLinksRegexes": [
    {
      "type": "regex",
      "pattern": "\\b(?<key>PROJ-\\d+)\\b",
      "url": "https://issues.example.com/browse/{key}",
      "label": "{key}"
    }
  ]
}
```

---

## 托管设置部署

**组织可通过多种机制部署不可覆盖的 managed 设置。**

### 文件方式

| 操作系统 | 路径 |
| :--- | :--- |
| **macOS** | `/Library/Application Support/ClaudeCode/managed-settings.json` |
| **Linux / WSL** | `/etc/claude-code/managed-settings.json` |
| **Windows** | `C:\Program Files\ClaudeCode\managed-settings.json` |

> 注意：Windows 旧路径 `C:\ProgramData\ClaudeCode\managed-settings.json` 从 v2.1.75 起不再支持。

### Drop-in 目录

`managed-settings.json` 旁的 `managed-settings.d/` 目录支持独立策略片段：
- `managed-settings.json` 作为基础先合并
- 目录中所有 `*.json` 文件按字母排序后依次合并
- 标量值后覆盖前，数组串联并去重，对象深度合并
- 以 `.` 开头的隐藏文件被忽略
- 建议使用数字前缀控制顺序：`10-telemetry.json`、`20-security.json`

### 托管 MCP 配置

存储为同一系统目录下的 `managed-mcp.json`。

### MDM / 操作系统级策略

| 平台 | 机制 |
| :--- | :--- |
| **macOS** | `com.anthropic.claudecode` managed preferences，顶级键对应 `managed-settings.json`，通过 Jamf/Kandji 等 MDM 工具下发配置描述文件 |
| **Windows（管理员）** | 注册表 `HKLM\SOFTWARE\Policies\ClaudeCode`，值名 `Settings`（REG_SZ/REG_EXPAND_SZ）内容为 JSON。通过 Group Policy 或 Intune 部署 |
| **Windows（用户级）** | 注册表 `HKCU\SOFTWARE\Policies\ClaudeCode`，优先级最低，仅在无管理员级来源时使用 |

### 服务端管理的设置

通过 Anthropic 服务器经 Claude.ai 管理控制台下发。

### 策略助手（Policy Helper）

```json
{
  "policyHelper": {
    "path": "/usr/local/bin/claude-policy"
  }
}
```

管理员部署的可执行文件，在启动时动态计算 managed 设置。仅从 MDM 或系统级 `managed-settings.json` 中生效（v2.1.136+）。

### 无效 Managed 设置的行为

**安全相关字段在值无效时采用安全失败策略：**

| 字段 | 无效时的行为 |
| :--- | :--- |
| `allowedMcpServers` | 空白名单（不允许任何 MCP 服务器） |
| `allowManagedMcpServersOnly` | 视为 `true` |
| `availableModels` | 空白名单（仅 Default 模型可用） |
| `enforceAvailableModels` | 视为 `true` |
| `forceLoginOrgUUID` | 不允许任何组织登录 |
| `deniedMcpServers` | 剥离无效条目，执行有效子集 |
| `sandbox.credentials` | 剥离无效条目，执行有效子集 |

`requiredMinimumVersion` 和 `requiredMaximumVersion` 采用**安全开放**策略：无效值被剥离而非强制执行。

---

## 环境变量

**`env` 设置中的环境变量应用于每个会话及其所有子进程。**

```json
{
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp"
  }
}
```

### 常用环境变量参考

| 变量 | 说明 |
| :--- | :--- |
| `CLAUDE_CODE_ENABLE_TELEMETRY` | 启用遥测（`"1"`） |
| `OTEL_METRICS_EXPORTER` | OpenTelemetry 指标导出器（如 `"otlp"`） |
| `CLAUDE_CODE_API_KEY_HELPER_TTL_MS` | `apiKeyHelper` 的刷新间隔 |
| `DISABLE_AUTO_COMPACT` | 禁用自动压缩 |
| `CLAUDE_CODE_DISABLE_AUTO_MEMORY` | 禁用自动记忆 |
| `CLAUDE_CODE_EFFORT_LEVEL` | 覆盖当前会话的努力等级 |
| `MAX_THINKING_TOKENS` | 设为 `0` 强制关闭思考（Anthropic API 上有效，Fable 5 除外） |
| `DISABLE_AUTOUPDATER` | 完全禁用自动更新 |
| `CLAUDE_CODE_DISABLE_FILE_CHECKPOINTING` | 禁用文件快照 |
| `CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY` | 抑制会话质量调查 |
| `CLAUDE_CODE_DISABLE_AGENT_VIEW` | 禁用代理视图（`"1"`） |
| `CLAUDE_CODE_DISABLE_ARTIFACT` | 禁用 Artifact 工具（`"1"`） |
| `CLAUDE_CODE_DISABLE_BUNDLED_SKILLS` | 禁用内置技能（`"1"`） |
| `CLAUDE_CODE_DISABLE_WORKFLOWS` | 禁用动态工作流（`"1"`） |
| `CLAUDE_CODE_ENABLE_AWAY_SUMMARY` | 启用离开摘要 |
| `CLAUDE_CODE_SKIP_PROMPT_HISTORY` | 完全禁用会话记录写入 |
| `CLAUDE_CODE_USE_POWERSHELL_TOOL` | 启用 PowerShell 工具（`1`） |
| `CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS` | 禁用 git 指令（覆盖 `includeGitInstructions`） |
| `ANTHROPIC_MODEL` | 覆盖当前会话的默认模型 |
| `CLAUDE_CODE_OTEL_HEADERS_HELPER_DEBOUNCE_MS` | `otelHeadersHelper` 的刷新间隔 |
| `CLAUDE_AX_SCREEN_READER` | 启用屏幕阅读器模式 |
| `NO_COLOR` / `FORCE_COLOR` | 传递给子进程（v2.1.143+）；在 shell 中启动 `claude` 前设置可改变界面颜色 |
