---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】环境变量
description: Claude Code 通过环境变量控制模型选择、认证、请求路由和功能开关等行为。本文介绍如何设置环境变量、优先级规则，以及完整的变量参考表。
category: translation
tags: [claude-code, env-vars, configuration, translation]
refs:
  - https://code.claude.com/docs/en/env-vars.md
---

# 环境变量

**环境变量是 Claude Code 最底层的配置方式，可以精确控制模型选择、API 认证、请求路由和各类功能开关。**

环境变量可以控制 Claude Code 的模型选择、认证方式、请求路由和功能开关等行为。很多相同的行为也可以通过 [settings 文件](https://code.claude.com/docs/en/settings)、[CLI 参数](https://code.claude.com/docs/en/cli-reference) 或会话内命令（如 `/model`）来配置。

本文涵盖：

- [设置环境变量](#设置环境变量)：在 shell 或 settings 文件中设置
- [优先级规则](#优先级)：同一行为有多种配置方式时，哪个生效
- [变量参考表](#变量参考表)：Claude Code 读取的所有环境变量

## 设置环境变量

**在 shell 中设置的变量只在当前终端会话有效，写入 settings 文件的变量在每次运行 `claude` 时都生效。**

### 在 shell 中设置

启动 `claude` 之前设置变量：

macOS / Linux / WSL：

```bash
export API_TIMEOUT_MS="1200000"
claude
```

要让变量在每次打开终端时都生效，把 `export` 行加入 `~/.bashrc`、`~/.zshrc` 或对应 shell 的 profile 文件。

Windows PowerShell：

```powershell
$env:API_TIMEOUT_MS = "1200000"
claude
```

要永久生效，运行 `[Environment]::SetEnvironmentVariable("API_TIMEOUT_MS", "1200000", "User")` 并重新打开终端。

Windows CMD：

```batch
set API_TIMEOUT_MS=1200000
claude
```

要永久生效，运行 `setx API_TIMEOUT_MS "1200000"` 并重新打开终端。

### 在 settings 文件中设置

**在 `settings.json` 的 `env` 字段下配置环境变量，Claude Code 启动时直接读取，不依赖启动方式。**

```json
// ~/.claude/settings.json
{
  "env": {
    "API_TIMEOUT_MS": "1200000",
    "BASH_DEFAULT_TIMEOUT_MS": "300000"
  }
}
```

选择不同的文件，变量的作用范围也不同：

| 文件 | 作用范围 |
|:---|:---|
| `~/.claude/settings.json` | 所有项目中对你生效 |
| `.claude/settings.json` | 项目中所有人生效（纳入版本管理） |
| `.claude/settings.local.json` | 仅对你在当前项目生效（手动创建时加入 gitignore） |
| Managed settings | 组织内所有人，由管理员部署 |

详见 [Settings 文件](https://code.claude.com/docs/en/settings#settings-files) 和 [Settings 优先级](https://code.claude.com/docs/en/settings#settings-precedence)。

## 优先级

**环境变量优先于 settings 字段；CLI 参数和会话命令的优先级因功能而异。**

当同一行为同时存在环境变量和 settings 字段时，环境变量优先。例如 `ANTHROPIC_MODEL` 覆盖 `model` 设置，`CLAUDE_CODE_AUTO_CONNECT_IDE` 覆盖 `autoConnectIde`。仅当环境变量未设置时，settings 字段才生效。

环境变量与 CLI 参数、会话命令的交互因功能而异：`--model` 和 `/model` 覆盖 `ANTHROPIC_MODEL`，而 `CLAUDE_CODE_EFFORT_LEVEL` 覆盖 `/effort`。具体优先关系见下方变量表中各行的说明。

Claude Code 在启动时读取环境变量，修改后需要重新启动 `claude` 才能生效。

## 变量参考表

**以下是 Claude Code 读取的所有环境变量的完整列表，按功能分类整理。**

### 认证与 API 密钥

| 变量 | 说明 |
|:---|:---|
| `ANTHROPIC_API_KEY` | 作为 `X-Api-Key` 头发送的 API 密钥。设置后即使已登录订阅（Pro/Max/Team/Enterprise），也会使用此密钥。非交互模式（`-p`）下直接使用；交互模式下首次使用时会提示确认。要改回使用订阅，运行 `unset ANTHROPIC_API_KEY` |
| `ANTHROPIC_AUTH_TOKEN` | 自定义 `Authorization` 头的值（会自动加 `Bearer ` 前缀） |
| `ANTHROPIC_AWS_API_KEY` | [Claude Platform on AWS](https://code.claude.com/docs/en/claude-platform-on-aws) 的 Workspace API 密钥，在 AWS 控制台生成。作为 `x-api-key` 发送，优先于 AWS SigV4 |
| `ANTHROPIC_AWS_WORKSPACE_ID` | [Claude Platform on AWS](https://code.claude.com/docs/en/claude-platform-on-aws) 必需字段，每个请求中作为 `anthropic-workspace-id` 头发送 |
| `ANTHROPIC_FOUNDRY_API_KEY` | Microsoft Foundry 认证的 API 密钥（见 [Microsoft Foundry](https://code.claude.com/docs/en/microsoft-foundry)） |
| `ANTHROPIC_WORKSPACE_ID` | [Workload Identity Federation](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation) 的 Workspace ID。当联合规则覆盖多个 workspace 时需要设置 |
| `AWS_BEARER_TOKEN_BEDROCK` | Bedrock API key 认证（见 [Bedrock API keys](https://aws.amazon.com/blogs/machine-learning/accelerate-ai-development-with-amazon-bedrock-api-keys/)） |
| `CLAUDE_CODE_CLIENT_CERT` | mTLS 认证的客户端证书文件路径 |
| `CLAUDE_CODE_CLIENT_KEY` | mTLS 认证的客户端私钥文件路径 |
| `CLAUDE_CODE_CLIENT_KEY_PASSPHRASE` | 加密私钥的密码（可选） |
| `CLAUDE_CODE_OAUTH_REFRESH_TOKEN` | Claude.ai 的 OAuth refresh token。设置后 `claude auth login` 直接换票，不打开浏览器。需配合 `CLAUDE_CODE_OAUTH_SCOPES` |
| `CLAUDE_CODE_OAUTH_SCOPES` | OAuth scopes（空格分隔），如 `"user:profile user:inference user:sessions:claude_code"`。设置 `CLAUDE_CODE_OAUTH_REFRESH_TOKEN` 时必需 |
| `CLAUDE_CODE_OAUTH_TOKEN` | Claude.ai 的 OAuth access token，可替代 `/login`。优先于 keychain 存储的凭据。通过 [`claude setup-token`](https://code.claude.com/docs/en/authentication#generate-a-long-lived-token) 生成 |

### API 端点与路由

| 变量 | 说明 |
|:---|:---|
| `ANTHROPIC_BASE_URL` | 覆盖 API 端点，用于代理或网关。设置为非第一方主机时，[MCP tool search](https://code.claude.com/docs/en/mcp#scale-with-mcp-tool-search) 默认关闭。代理支持 `tool_reference` 时设置 `ENABLE_TOOL_SEARCH=true` |
| `ANTHROPIC_AWS_BASE_URL` | 覆盖 Claude Platform on AWS 端点 URL，用于自定义 region 或 [LLM 网关](https://code.claude.com/docs/en/llm-gateway)。默认 `https://aws-external-anthropic.{AWS_REGION}.api.aws` |
| `ANTHROPIC_BEDROCK_BASE_URL` | 覆盖 Bedrock 端点 URL（见 [Amazon Bedrock](https://code.claude.com/docs/en/amazon-bedrock)） |
| `ANTHROPIC_BEDROCK_MANTLE_BASE_URL` | 覆盖 Bedrock Mantle 端点 URL（见 [Mantle endpoint](https://code.claude.com/docs/en/amazon-bedrock#use-the-mantle-endpoint)） |
| `ANTHROPIC_VERTEX_BASE_URL` | 覆盖 Vertex AI 端点 URL（见 [Google Vertex AI](https://code.claude.com/docs/en/google-vertex-ai)） |
| `ANTHROPIC_FOUNDRY_BASE_URL` | Foundry 资源的完整 base URL（如 `https://my-resource.services.ai.azure.com/anthropic`），替代 `ANTHROPIC_FOUNDRY_RESOURCE` |
| `ANTHROPIC_FOUNDRY_RESOURCE` | Foundry 资源名称（如 `my-resource`）。未设置 `ANTHROPIC_FOUNDRY_BASE_URL` 时必需 |
| `ANTHROPIC_VERTEX_PROJECT_ID` | Vertex AI 请求的 GCP 项目 ID。被 `GCLOUD_PROJECT`、`GOOGLE_CLOUD_PROJECT` 或 credential 文件中的项目覆盖 |
| `CLAUDE_CODE_USE_ANTHROPIC_AWS` | 使用 [Claude Platform on AWS](https://code.claude.com/docs/en/claude-platform-on-aws) |
| `CLAUDE_CODE_USE_BEDROCK` | 使用 [Bedrock](https://code.claude.com/docs/en/amazon-bedrock) |
| `CLAUDE_CODE_USE_FOUNDRY` | 使用 [Microsoft Foundry](https://code.claude.com/docs/en/microsoft-foundry) |
| `CLAUDE_CODE_USE_MANTLE` | 使用 Bedrock [Mantle endpoint](https://code.claude.com/docs/en/amazon-bedrock#use-the-mantle-endpoint) |
| `CLAUDE_CODE_USE_VERTEX` | 使用 [Vertex](https://code.claude.com/docs/en/google-vertex-ai) |
| `CLAUDE_CODE_SKIP_ANTHROPIC_AWS_AUTH` | 跳过 Claude Platform on AWS 的客户端认证，用于网关自行签名请求 |
| `CLAUDE_CODE_SKIP_BEDROCK_AUTH` | 跳过 Bedrock 的 AWS 认证（如通过 LLM 网关时） |
| `CLAUDE_CODE_SKIP_FOUNDRY_AUTH` | 跳过 Microsoft Foundry 的 Azure 认证 |
| `CLAUDE_CODE_SKIP_MANTLE_AUTH` | 跳过 Bedrock Mantle 的 AWS 认证 |
| `CLAUDE_CODE_SKIP_VERTEX_AUTH` | 跳过 Vertex 的 Google 认证 |
| `HTTP_PROXY` | HTTP 代理服务器 |
| `HTTPS_PROXY` | HTTPS 代理服务器 |
| `NO_PROXY` | 不走代理的域名和 IP 列表 |

### 模型配置

| 变量 | 说明 |
|:---|:---|
| `ANTHROPIC_MODEL` | 使用的模型名（见 [Model Configuration](https://code.claude.com/docs/en/model-config#environment-variables)） |
| `ANTHROPIC_CUSTOM_MODEL_OPTION` | 添加到 `/model` 选择器的自定义模型 ID（见 [Model configuration](https://code.claude.com/docs/en/model-config#add-a-custom-model-option)） |
| `ANTHROPIC_CUSTOM_MODEL_OPTION_NAME` | 自定义模型在 `/model` 选择器中的显示名称 |
| `ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION` | 自定义模型在 `/model` 选择器中的显示描述 |
| `ANTHROPIC_CUSTOM_MODEL_OPTION_SUPPORTED_CAPABILITIES` | 见 [Model configuration](https://code.claude.com/docs/en/model-config#customize-pinned-model-display-and-capabilities) |
| `ANTHROPIC_DEFAULT_FABLE_MODEL` | 覆盖默认 Fable 模型（见 [Model configuration](https://code.claude.com/docs/en/model-config#environment-variables)） |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | 覆盖默认 Haiku 模型 |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | 覆盖默认 Opus 模型 |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | 覆盖默认 Sonnet 模型 |
| `ANTHROPIC_DEFAULT_*_MODEL_NAME` | 各模型的显示名称覆盖（`FABLE`/`HAIKU`/`OPUS`/`SONNET`） |
| `ANTHROPIC_DEFAULT_*_MODEL_DESCRIPTION` | 各模型的显示描述覆盖 |
| `ANTHROPIC_DEFAULT_*_MODEL_SUPPORTED_CAPABILITIES` | 各模型的能力声明覆盖 |
| `ANTHROPIC_SMALL_FAST_MODEL` | [已废弃] Haiku 级别后台任务模型名 |
| `ANTHROPIC_SMALL_FAST_MODEL_AWS_REGION` | 使用 Bedrock 时覆盖 Haiku 模型的 AWS region |
| `CLAUDE_CODE_SUBAGENT_MODEL` | 子 agent 使用的模型（见 [Model configuration](https://code.claude.com/docs/en/model-config)） |
| `CLAUDE_CODE_EFFORT_LEVEL` | 模型 effort level：`low`/`medium`/`high`/`xhigh`/`max`/`auto`。优先于 `/effort` 和 `effortLevel` 设置 |
| `CLAUDE_CODE_ALWAYS_ENABLE_EFFORT` | 设为 `1` 即使模型 ID 未被识别为支持 effort 也发送该参数，用于网关自定义模型标识 |
| `ANTHROPIC_BEDROCK_SERVICE_TIER` | Bedrock 服务层（`default`/`flex`/`priority`），作为 `X-Amzn-Bedrock-Service-Tier` 头发送 |

### 超时与重试

| 变量 | 说明 |
|:---|:---|
| `API_TIMEOUT_MS` | API 请求超时（毫秒，默认 600000 即 10 分钟，最大 2147483647）。超过最大值会导致请求立即失败 |
| `API_FORCE_IDLE_TIMEOUT` | 覆盖流式响应 5 分钟无数据的空闲超时。`0` 禁用，`1` 对所有 provider 启用。v2.1.169+ |
| `BASH_DEFAULT_TIMEOUT_MS` | Bash 命令默认超时（默认 120000 即 2 分钟） |
| `BASH_MAX_TIMEOUT_MS` | 模型可设置的 Bash 命令最大超时（默认 600000 即 10 分钟） |
| `CLAUDE_CODE_MAX_RETRIES` | API 请求失败时的重试次数（默认 10，v2.1.186+ 上限 15） |
| `CLAUDE_CODE_RETRY_WATCHDOG` | 设为 `1` 无限重试 429/529 容量错误，适用于无人值守场景。v2.1.186+ |
| `CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS` | 后台子 agent 停滞超时（默认 600000 即 10 分钟） |
| `CLAUDE_STREAM_IDLE_TIMEOUT_MS` | 流式空闲看门狗超时（毫秒），显式设置时最低 300000（5 分钟） |
| `CLAUDE_CODE_CONNECT_TIMEOUT_MS` | v2.1.186 移除，已无效。使用 `API_TIMEOUT_MS` |
| `MCP_TIMEOUT` | MCP 服务器启动超时（默认 30000 即 30 秒） |
| `MCP_TOOL_TIMEOUT` | MCP 工具执行超时（默认约 28 小时） |
| `CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT` | 远程 MCP 工具空闲超时（默认 300000 即 5 分钟），v2.1.187+ |
| `MCP_CONNECT_TIMEOUT_MS` | 阻塞式 MCP 启动等待超时（默认 5000） |
| `CLAUDE_CODE_GLOB_TIMEOUT_SECONDS` | Glob 工具超时（默认 20 秒，WSL 上 60 秒） |

### 请求头与 Beta 功能

| 变量 | 说明 |
|:---|:---|
| `ANTHROPIC_BETAS` | 逗号分隔的额外 `anthropic-beta` 头值，用于在 Claude Code 原生支持前启用 API beta。与 `--betas` 不同，支持所有认证方式 |
| `ANTHROPIC_CUSTOM_HEADERS` | 自定义请求头（`Name: Value` 格式，多个用换行分隔） |
| `CLAUDE_CODE_EXTRA_BODY` | JSON 对象，合并到每个 API 请求体顶层 |
| `CLAUDE_CODE_ATTRIBUTION_HEADER` | 设为 `0` 从 system prompt 中移除版本归属信息，可提高网关的 prompt-cache 命中率 |
| `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` | 设为 `1` 去除 Anthropic 特有的 beta 请求头和 beta 工具 schema 字段，解决代理网关拒绝请求的问题 |
| `DISABLE_INTERLEAVED_THINKING` | 设为 `1` 不发送 interleaved-thinking beta 头 |

### Thinking 与推理

| 变量 | 说明 |
|:---|:---|
| `MAX_THINKING_TOKENS` | 覆盖 extended thinking token 预算。设为 `0` 在 Anthropic API 上禁用 thinking（Fable 5 除外）。非零值在自适应推理模型上被忽略（除非同时禁用自适应推理） |
| `CLAUDE_CODE_DISABLE_THINKING` | 设为 `1` 完全省略 API 请求中的 `thinking` 参数（兼容性选项，用于代理/网关不支持该参数的情况） |
| `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING` | 设为 `1` 禁用 Opus 4.6/Sonnet 4.6 的自适应推理，回退到 `MAX_THINKING_TOKENS` 固定预算。v2.1.111+ 对 Fable 5 和 Opus 4.7+ 无效 |

### 上下文管理与 Compaction

| 变量 | 说明 |
|:---|:---|
| `DISABLE_AUTO_COMPACT` | 设为 `1` 禁用自动 compaction（`/compact` 命令仍可用） |
| `DISABLE_COMPACT` | 设为 `1` 禁用所有 compaction（包括自动和手动 `/compact`） |
| `CLAUDE_CODE_AUTO_COMPACT_WINDOW` | 设置 auto-compaction 计算所用的 token 窗口大小。用较小值（如 `500000`）可在 1M 模型上提前触发压缩 |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | 设置触发自动压缩的窗口百分比（1-100），只能降低阈值 |
| `CLAUDE_CODE_DISABLE_1M_CONTEXT` | 设为 `1` 禁用 1M 上下文窗口支持 |
| `CLAUDE_CODE_MAX_CONTEXT_TOKENS` | 覆盖模型上下文窗口大小（需同时设置 `DISABLE_COMPACT`） |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | 设置大多数请求的最大输出 token 数 |

### 工具行为

| 变量 | 说明 |
|:---|:---|
| `BASH_MAX_OUTPUT_LENGTH` | Bash 输出超过此字符数时保存到文件，Claude 只收到路径和摘要 |
| `CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS` | 覆盖文件读取的默认 token 限制 |
| `CLAUDE_CODE_GLOB_HIDDEN` | 设为 `false` Glob 工具结果排除 dotfiles |
| `CLAUDE_CODE_GLOB_NO_IGNORE` | 设为 `false` Glob 工具遵循 `.gitignore` |
| `CLAUDE_CODE_USE_POWERSHELL_TOOL` | 控制 PowerShell 工具的启用。Windows 无 Git Bash 时默认启用；Linux/macOS 设为 `1` 启用（需 `pwsh` 在 PATH 中） |
| `CLAUDE_CODE_USE_NATIVE_FILE_SEARCH` | 设为 `1` 用 Node.js 文件 API 代替 ripgrep 发现自定义命令 |
| `USE_BUILTIN_RIPGREP` | 设为 `0` 使用系统安装的 `rg` |
| `ENABLE_TOOL_SEARCH` | 控制 MCP tool search 行为：`true`（始终延迟加载）、`auto`/`auto:N`（阈值模式）、`false`（全部预加载） |
| `MAX_MCP_OUTPUT_TOKENS` | MCP 工具响应最大 token 数（默认 25000） |
| `TASK_MAX_OUTPUT_LENGTH` | 子 agent 输出截断阈值（默认 32000，最大 160000） |

### MCP 服务器配置

| 变量 | 说明 |
|:---|:---|
| `MCP_CONNECTION_NONBLOCKING` | v2.1.142+ 默认非阻塞启动。设为 `0` 恢复阻塞式 5 秒连接等待 |
| `MCP_SERVER_CONNECTION_BATCH_SIZE` | 本地 MCP 服务器（stdio）并行连接数（默认 3） |
| `MCP_REMOTE_SERVER_CONNECTION_BATCH_SIZE` | 远程 MCP 服务器（HTTP/SSE）并行连接数（默认 20） |
| `MCP_CLIENT_SECRET` | MCP 服务器 OAuth client secret |
| `MCP_OAUTH_CALLBACK_PORT` | OAuth 回调固定端口 |
| `CLAUDE_CODE_MCP_ALLOWLIST_ENV` | 设为 `1` MCP stdio 服务器仅继承安全基线环境，不继承完整 shell 环境 |
| `ENABLE_CLAUDEAI_MCP_SERVERS` | 设为 `false` 禁用 claude.ai MCP 服务器 |

### Prompt Caching

| 变量 | 说明 |
|:---|:---|
| `DISABLE_PROMPT_CACHING` | 设为 `1` 禁用所有模型的 prompt caching |
| `DISABLE_PROMPT_CACHING_FABLE` | 设为 `1` 禁用 Fable 模型的 prompt caching |
| `DISABLE_PROMPT_CACHING_HAIKU` | 设为 `1` 禁用 Haiku 模型的 prompt caching |
| `DISABLE_PROMPT_CACHING_OPUS` | 设为 `1` 禁用 Opus 模型的 prompt caching |
| `DISABLE_PROMPT_CACHING_SONNET` | 设为 `1` 禁用 Sonnet 模型的 prompt caching |
| `ENABLE_PROMPT_CACHING_1H` | 设为 `1` 请求 1 小时 cache TTL（默认 5 分钟），写入费用更高 |
| `FORCE_PROMPT_CACHING_5M` | 设为 `1` 强制使用 5 分钟 cache TTL，覆盖 `ENABLE_PROMPT_CACHING_1H` |

### 功能开关（禁用类）

| 变量 | 说明 |
|:---|:---|
| `CLAUDE_CODE_DISABLE_FAST_MODE` | 设为 `1` 禁用 [fast mode](https://code.claude.com/docs/en/fast-mode) |
| `CLAUDE_CODE_DISABLE_WORKFLOWS` | 设为 `1` 禁用 [workflows](https://code.claude.com/docs/en/workflows#turn-workflows-off) |
| `CLAUDE_CODE_DISABLE_BUNDLED_SKILLS` | 设为 `1` 禁用内置 skills 和 workflows |
| `CLAUDE_CODE_DISABLE_POLICY_SKILLS` | 设为 `1` 不加载系统级 managed skills |
| `CLAUDE_CODE_DISABLE_CRON` | 设为 `1` 禁用定时任务 |
| `CLAUDE_CODE_DISABLE_AGENT_VIEW` | 设为 `1` 关闭 agent view（`claude agents`、`--bg`、`/background`） |
| `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` | 设为 `1` 禁用所有后台任务功能 |
| `CLAUDE_CODE_DISABLE_ADVISOR_TOOL` | 设为 `1` 禁用 advisor 工具。v2.1.98+ |
| `CLAUDE_CODE_DISABLE_ARTIFACT` | 设为 `1` 禁用 Artifact 工具 |
| `CLAUDE_CODE_DISABLE_ATTACHMENTS` | 设为 `1` 禁用附件处理，`@` 引用作为纯文本发送 |
| `CLAUDE_CODE_DISABLE_AUTO_MEMORY` | 设为 `1` 禁用 auto memory；设为 `0` 强制启用 |
| `CLAUDE_CODE_DISABLE_CLAUDE_MDS` | 设为 `1` 不加载任何 CLAUDE.md 文件 |
| `CLAUDE_CODE_DISABLE_FILE_CHECKPOINTING` | 设为 `1` 禁用文件 checkpointing，`/rewind` 无法恢复代码变更 |
| `CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS` | 设为 `1` 移除 system prompt 中的 git 相关指令 |
| `CLAUDE_CODE_DISABLE_LEGACY_MODEL_REMAP` | 设为 `1` 阻止 Opus 4.0/4.1 自动重映射到当前版本 |
| `CLAUDE_CODE_DISABLE_NONSTREAMING_FALLBACK` | 设为 `1` 禁用流式失败时的非流式回退 |
| `CLAUDE_CODE_DISABLE_TERMINAL_TITLE` | 设为 `1` 禁用终端标题自动更新 |
| `CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY` | 设为 `1` 禁用会话质量调查 |

### 功能开关（启用类）

| 变量 | 说明 |
|:---|:---|
| `CLAUDE_CODE_ENABLE_AUTO_MODE` | 设为 `1` 在 Bedrock/Vertex/Foundry 上启用 auto mode。v2.1.158+ |
| `CLAUDE_CODE_ENABLE_AWAY_SUMMARY` | 覆盖 session recap 开关。`0` 强制关，`1` 强制开 |
| `CLAUDE_CODE_ENABLE_TELEMETRY` | 设为 `1` 启用 OpenTelemetry 数据收集 |
| `CLAUDE_CODE_ENABLE_TASKS` | 控制使用 Task 工具还是 TodoWrite。v2.1.142+ 默认 Task，设为 `0` 回退 |
| `CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION` | 设为 `false` 禁用 prompt 建议 |
| `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY` | 设为 `1` 从网关的 `/v1/models` 端点填充 `/model` 选择器 |
| `CLAUDE_CODE_ENABLE_FINE_GRAINED_TOOL_STREAMING` | 控制工具调用输入的流式传输。Anthropic API 默认启用 |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | 设为 `1` 启用 agent teams（实验功能） |
| `CLAUDE_CODE_FORK_SUBAGENT` | 设为 `1` 允许 Claude 生成 fork 子 agent |
| `CLAUDE_AUTO_BACKGROUND_TASKS` | 设为 `1` 自动将长时间运行的子 agent 移到后台 |

### UI 与终端渲染

| 变量 | 说明 |
|:---|:---|
| `CLAUDE_CODE_NO_FLICKER` | 设为 `1` 启用全屏渲染（减少闪烁） |
| `CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN` | 设为 `1` 禁用全屏渲染，使用经典主屏幕渲染器 |
| `CLAUDE_CODE_DISABLE_VIRTUAL_SCROLL` | 设为 `1` 禁用全屏模式的虚拟滚动 |
| `CLAUDE_CODE_DISABLE_MOUSE` | 设为 `1` 禁用全屏模式的鼠标追踪 |
| `CLAUDE_CODE_ALT_SCREEN_FULL_REPAINT` | 设为 `1` 全屏模式每帧完全重绘 |
| `CLAUDE_CODE_SCROLL_SPEED` | 全屏模式鼠标滚轮倍率（1-20，支持小数如 `0.5`） |
| `CLAUDE_CODE_ACCESSIBILITY` | 设为 `1` 保持原生终端光标可见，支持屏幕放大器 |
| `CLAUDE_AX_SCREEN_READER` | 设为 `1` 输出屏幕阅读器友好格式。v2.1.181+ |
| `CLAUDE_CODE_NATIVE_CURSOR` | 设为 `1` 使用终端原生光标 |
| `CLAUDE_CODE_SYNTAX_HIGHLIGHT` | 设为 `false` 禁用 diff 中的语法高亮 |
| `CLAUDE_CODE_HIDE_CWD` | 设为 `1` 隐藏启动 logo 中的工作目录路径 |
| `CLAUDE_CODE_FORCE_STRIKETHROUGH` | 设为 `1` 强制渲染删除线。v2.1.186+ |
| `CLAUDE_CODE_FORCE_SYNC_OUTPUT` | 设为 `1` 强制启用 DEC 2026 同步输出 |
| `CLAUDE_CODE_TMUX_TRUECOLOR` | 设为 `1` tmux 内允许 24-bit truecolor 输出 |
| `IS_DEMO` | 设为 `1` 启用演示模式，隐藏邮箱和组织名 |

### 子进程与会话环境

| 变量 | 说明 |
|:---|:---|
| `CLAUDECODE` | Claude Code 生成的子进程中设为 `1`（Bash/PowerShell 工具、tmux、hook、MCP 子进程）。IDE 扩展也会在集成终端中设置 |
| `CLAUDE_CODE_CHILD_SESSION` | 仅由 Claude Code 自身在 Bash/PowerShell/Monitor 工具和 hook 命令中设为 `1`。不包括 stdio MCP 服务器。v2.1.172+ |
| `CLAUDE_CODE_SESSION_ID` | 子进程中自动设置为当前 session ID |
| `CLAUDE_CODE_REMOTE` | 云端会话中自动设为 `true` |
| `CLAUDE_CODE_REMOTE_SESSION_ID` | 云端会话的 session ID |
| `CLAUDE_EFFORT` | Bash/hook 子进程中自动设置为当前 effort level |
| `CLAUDE_ENV_FILE` | shell 脚本路径，每次 Bash 命令前 source，用于持久化 virtualenv/conda 激活 |
| `CLAUDE_CODE_SHELL` | 覆盖自动检测的 shell |
| `CLAUDE_CODE_SHELL_PREFIX` | 包装 Claude Code 生成的所有 shell 命令的前缀 |
| `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` | 设为 `1` 从子进程环境中剥离 Anthropic 和云 provider 凭据，减少 prompt injection 窃取密钥的风险。Linux 上还在隔离 PID namespace 中运行 Bash |
| `CLAUDE_CODE_SCRIPT_CAPS` | JSON 对象，限制特定脚本每会话调用次数（配合 `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` 使用） |
| `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR` | 每次 Bash 命令后回到原始工作目录 |
| `CLAUDE_CODE_FORCE_SESSION_PERSISTENCE` | 设为 `1` 强制嵌套会话也持久化。v2.1.172+ |
| `CLAUDE_CODE_SKIP_PROMPT_HISTORY` | 设为 `1` 不写入 prompt 历史和会话记录 |
| `CLAUDE_CODE_RESUME_INTERRUPTED_TURN` | 设为 `1` 自动恢复上次中断的会话（SDK 模式） |
| `CLAUDE_CODE_RESUME_PROMPT` | 覆盖恢复中断会话时注入的继续消息 |

### IDE 与扩展

| 变量 | 说明 |
|:---|:---|
| `CLAUDE_CODE_AUTO_CONNECT_IDE` | 覆盖 IDE 自动连接。`false` 阻止自动连接，`true` 强制尝试连接 |
| `CLAUDE_CODE_IDE_HOST_OVERRIDE` | 覆盖连接 IDE 扩展的主机地址 |
| `CLAUDE_CODE_IDE_SKIP_AUTO_INSTALL` | 跳过 IDE 扩展的自动安装 |
| `CLAUDE_CODE_IDE_SKIP_VALID_CHECK` | 设为 `1` 跳过 IDE lockfile 验证 |

### Memory 与 CLAUDE.md

| 变量 | 说明 |
|:---|:---|
| `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` | 设为 `1` 从 `--add-dir` 指定的目录加载 memory 文件 |
| `CLAUDE_CODE_DISABLE_CLAUDE_MDS` | 设为 `1` 不加载任何 CLAUDE.md 文件 |
| `CLAUDE_CODE_DISABLE_AUTO_MEMORY` | 设为 `1` 禁用 auto memory |

### 插件系统

| 变量 | 说明 |
|:---|:---|
| `CLAUDE_CODE_PLUGIN_CACHE_DIR` | 覆盖插件根目录（marketplace 和 cache 在其子目录下）。默认 `~/.claude/plugins` |
| `CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS` | 插件 git 操作超时（默认 120000） |
| `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE` | 设为 `1` git pull 失败时保留现有 marketplace 缓存 |
| `CLAUDE_CODE_PLUGIN_PREFER_HTTPS` | 设为 `1` 插件克隆使用 HTTPS 而非 SSH |
| `CLAUDE_CODE_PLUGIN_SEED_DIR` | 只读插件种子目录路径（`:`/`;` 分隔），用于容器预装 |
| `CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL` | 设为 `1` 首次运行时不自动添加官方插件市场 |
| `CLAUDE_CODE_SYNC_PLUGIN_INSTALL` | 设为 `1` 非交互模式下同步等待插件安装完成 |
| `CLAUDE_CODE_SYNC_PLUGIN_INSTALL_TIMEOUT_MS` | 同步插件安装超时 |
| `CLAUDE_CODE_ENABLE_BACKGROUND_PLUGIN_REFRESH` | 设为 `1` 后台安装完成后在 turn 边界刷新插件状态 |
| `FORCE_AUTOUPDATE_PLUGINS` | 设为 `1` 即使禁用了主自动更新也强制更新插件 |

### Skills 同步

| 变量 | 说明 |
|:---|:---|
| `CLAUDE_CODE_SYNC_SKILLS` | 设为 `1` 在 `-p` 模式下同步 claude.ai skills 到本地，每 10 分钟刷新 |
| `CLAUDE_CODE_SYNC_SKILLS_WAIT_TIMEOUT_MS` | 首次查询等待 skills 同步的超时（默认 5000） |
| `CLAUDE_CODE_SYNC_SKILLS_INSTALL_TIMEOUT_MS` | 会话中 skills 重新同步超时（默认 30000） |

### 遥测与监控

| 变量 | 说明 |
|:---|:---|
| `DISABLE_TELEMETRY` | 设为 `1` 关闭遥测（不含用户数据如代码/路径/命令） |
| `DO_NOT_TRACK` | 设为 `1` 关闭遥测，等同 `DISABLE_TELEMETRY` |
| `DISABLE_ERROR_REPORTING` | 设为 `1` 关闭 Sentry 错误上报 |
| `DISABLE_GROWTHBOOK` | 设为 `1` 禁用 GrowthBook feature-flag |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | 等同同时设置 `DISABLE_AUTOUPDATER`、`DISABLE_FEEDBACK_COMMAND`、`DISABLE_ERROR_REPORTING`、`DISABLE_TELEMETRY` |
| `CLAUDE_CODE_ENABLE_TELEMETRY` | 设为 `1` 启用 OpenTelemetry 数据收集 |
| `CLAUDE_CODE_ENABLE_FEEDBACK_SURVEY_FOR_OTEL` | 设为 `1` 会话质量调查路由到 OTel collector（不发送到 Anthropic） |
| `OTEL_LOG_RAW_API_BODIES` | 设为 `1` 将 API 请求/响应 JSON 作为日志事件发出；`file:<dir>` 写入磁盘 |
| `OTEL_LOG_TOOL_CONTENT` | 设为 `1` 在 OTel span 中包含工具输入输出内容 |
| `OTEL_LOG_TOOL_DETAILS` | 设为 `1` 在 OTel 中包含工具参数、MCP 服务器名、错误字符串等 |
| `OTEL_LOG_USER_PROMPTS` | 设为 `1` 在 OTel 中包含用户 prompt 文本 |
| `OTEL_METRICS_INCLUDE_ACCOUNT_UUID` | 设为 `false` 从 metrics 中排除 account UUID |
| `OTEL_METRICS_INCLUDE_SESSION_ID` | 设为 `false` 从 metrics 中排除 session ID |
| `OTEL_METRICS_INCLUDE_VERSION` | 设为 `true` 在 metrics 中包含 Claude Code 版本 |
| `OTEL_METRICS_INCLUDE_ENTRYPOINT` | 设为 `true` 在 metrics 中包含会话入口点。v2.1.152+ |
| `OTEL_METRICS_INCLUDE_RESOURCE_ATTRIBUTES` | 设为 `false` 排除 OTEL_RESOURCE_ATTRIBUTES。v2.1.161+ |
| `CLAUDE_CODE_OTEL_FLUSH_TIMEOUT_MS` | OTel span flush 超时（默认 5000） |
| `CLAUDE_CODE_OTEL_SHUTDOWN_TIMEOUT_MS` | OTel 关闭超时（默认 2000） |
| `CLAUDE_CODE_OTEL_HEADERS_HELPER_DEBOUNCE_MS` | 动态 OTel headers 刷新间隔（默认 1740000 即 29 分钟） |
| `CLAUDE_CODE_OTEL_DIAG_STDERR` | 设为 `1` OTel 导出器诊断错误输出到 stderr。v2.1.179+ |
| `CLAUDE_CODE_PROPAGATE_TRACEPARENT` | 设为 `1` 自定义代理下传播 W3C trace context。v2.1.152+ |

### 更新与安装

| 变量 | 说明 |
|:---|:---|
| `DISABLE_AUTOUPDATER` | 设为 `1` 禁用自动后台更新（手动 `claude update` 仍可用） |
| `DISABLE_UPDATES` | 设为 `1` 阻止所有更新（包括手动 `claude update` 和 `claude install`） |
| `CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE` | 设为 `1` 允许 Claude Code 在后台通过包管理器升级 |

### 命令可见性

| 变量 | 说明 |
|:---|:---|
| `DISABLE_FEEDBACK_COMMAND` | 设为 `1` 隐藏 `/feedback` 命令 |
| `DISABLE_DOCTOR_COMMAND` | 设为 `1` 隐藏 `/doctor` 命令 |
| `DISABLE_EXTRA_USAGE_COMMAND` | 设为 `1` 隐藏 `/usage-credits` 命令 |
| `DISABLE_INSTALL_GITHUB_APP_COMMAND` | 设为 `1` 隐藏 `/install-github-app` 命令 |
| `DISABLE_LOGIN_COMMAND` | 设为 `1` 隐藏 `/login` 命令 |
| `DISABLE_LOGOUT_COMMAND` | 设为 `1` 隐藏 `/logout` 命令 |
| `DISABLE_UPGRADE_COMMAND` | 设为 `1` 隐藏 `/upgrade` 命令 |
| `DISABLE_INSTALLATION_CHECKS` | 设为 `1` 禁用安装检查警告 |
| `DISABLE_COST_WARNINGS` | 设为 `1` 禁用费用警告 |

### 调试

| 变量 | 说明 |
|:---|:---|
| `DEBUG` | 设为 `1` 启用调试模式，日志写入 `~/.claude/debug/<session-id>.txt` |
| `CLAUDE_CODE_DEBUG_LOGS_DIR` | 覆盖调试日志文件路径（实际是文件路径而非目录） |
| `CLAUDE_CODE_DEBUG_LOG_LEVEL` | 调试日志最低级别：`verbose`/`debug`（默认）/`info`/`warn`/`error` |

### 流式传输看门狗

| 变量 | 说明 |
|:---|:---|
| `CLAUDE_ENABLE_BYTE_WATCHDOG` | `1` 强制启用字节级流式看门狗，`0` 强制禁用 |
| `CLAUDE_ENABLE_BYTE_WATCHDOG_BEDROCK` | 设为 `1` 在 Bedrock 上启用字节级看门狗 |
| `CLAUDE_ENABLE_STREAM_WATCHDOG` | `1` 强制启用事件级流式看门狗，`0` 强制禁用 |

### 安全与沙箱

| 变量 | 说明 |
|:---|:---|
| `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` | 设为 `1` 从子进程剥离凭据，Linux 上还隔离 PID namespace |
| `CLAUDE_CODE_SCRIPT_CAPS` | 限制脚本调用次数的 JSON 对象 |
| `CLAUDE_CODE_PERFORCE_MODE` | 设为 `1` 启用 Perforce 写保护 |
| `CLAUDE_CODE_SAFE_MODE` | 设为 `1` 安全模式启动，不加载 CLAUDE.md/skills/plugins/hooks/MCP 等 |

### 远程与云端

| 变量 | 说明 |
|:---|:---|
| `CCR_FORCE_BUNDLE` | 设为 `1` 强制 `claude --remote` 打包上传本地仓库 |
| `CLAUDE_CODE_REMOTE` | 云端会话中自动设为 `true` |
| `CLAUDE_CODE_REMOTE_SESSION_ID` | 云端会话 ID |
| `CLAUDE_REMOTE_CONTROL_SESSION_NAME_PREFIX` | Remote Control 自动生成 session 名的前缀 |
| `CLAUDE_CLIENT_PRESENCE_FILE` | 文件存在时跳过 Remote Control 推送通知。v2.1.181+ |

### 其他

| 变量 | 说明 |
|:---|:---|
| `CLAUDE_CODE_API_KEY_HELPER_TTL_MS` | apiKeyHelper 凭据刷新间隔（毫秒） |
| `CLAUDE_CODE_ARTIFACT_AUTO_OPEN` | 设为 `0` 发布 artifact 时不自动打开浏览器 |
| `CLAUDE_CODE_CERT_STORE` | CA 证书来源列表（默认 `bundled,system`） |
| `CLAUDE_CODE_EXIT_AFTER_STOP_DELAY` | 查询循环空闲后自动退出的等待时间（毫秒） |
| `CLAUDE_CODE_GIT_BASH_PATH` | Windows：Git Bash 可执行文件路径 |
| `CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY` | 只读工具和子 agent 最大并行数（默认 10） |
| `CLAUDE_CODE_MAX_TURNS` | 无显式限制时的最大 agent 轮数 |
| `CLAUDE_CODE_NEW_INIT` | 设为 `1` `/init` 运行交互式设置流程 |
| `CLAUDE_CODE_POWERSHELL_RESPECT_EXECUTION_POLICY` | 设为 `1` 不绕过 PowerShell 执行策略 |
| `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS` | `-p` 模式最后一轮后等待后台任务的最长时间（默认 600000） |
| `CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST` | 由宿主平台设置，忽略用户的 provider 配置 |
| `CLAUDE_CODE_PROXY_RESOLVES_HOSTS` | 设为 `1` 让代理执行 DNS 解析 |
| `CLAUDE_CODE_SIMPLE` | 设为 `1` 最小系统 prompt + 仅 Bash/读/写工具 |
| `CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT` | 设为 `1` 使用更短的 system prompt |
| `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` | Stop hook 最大连续阻止次数（默认 8） |
| `CLAUDE_CODE_TASK_LIST_ID` | 跨会话共享任务列表 ID |
| `CLAUDE_CODE_TEAM_NAME` | agent team 成员所属队名 |
| `CLAUDE_CODE_TMPDIR` | 覆盖临时目录（默认 macOS `/tmp`，Linux/Windows `os.tmpdir()`） |
| `CLAUDE_CONFIG_DIR` | 覆盖配置目录（默认 `~/.claude`） |
| `CLAUDE_AGENT_SDK_DISABLE_BUILTIN_AGENTS` | 设为 `1` 禁用内置子 agent 类型（仅 `-p` 模式） |
| `CLAUDE_AGENT_SDK_MCP_NO_PREFIX` | 设为 `1` MCP 工具名不加 `mcp__<server>__` 前缀 |
| `FALLBACK_FOR_ALL_PRIMARY_MODELS` | 设为非空值让所有模型在 overload 时停止重试 |
| `MAX_STRUCTURED_OUTPUT_RETRIES` | `--json-schema` 验证失败的重试次数（默认 5） |
| `SLASH_COMMAND_TOOL_CHAR_BUDGET` | 覆盖 Skill 工具元数据字符预算 |

### Vertex AI Region 覆盖

| 变量 | 说明 |
|:---|:---|
| `VERTEX_REGION_CLAUDE_3_5_HAIKU` | Claude 3.5 Haiku |
| `VERTEX_REGION_CLAUDE_3_5_SONNET` | Claude 3.5 Sonnet |
| `VERTEX_REGION_CLAUDE_3_7_SONNET` | Claude 3.7 Sonnet |
| `VERTEX_REGION_CLAUDE_4_0_OPUS` | Claude 4.0 Opus |
| `VERTEX_REGION_CLAUDE_4_0_SONNET` | Claude 4.0 Sonnet |
| `VERTEX_REGION_CLAUDE_4_1_OPUS` | Claude 4.1 Opus |
| `VERTEX_REGION_CLAUDE_4_5_OPUS` | Claude Opus 4.5 |
| `VERTEX_REGION_CLAUDE_4_5_SONNET` | Claude Sonnet 4.5 |
| `VERTEX_REGION_CLAUDE_4_6_OPUS` | Claude Opus 4.6 |
| `VERTEX_REGION_CLAUDE_4_6_SONNET` | Claude Sonnet 4.6 |
| `VERTEX_REGION_CLAUDE_4_7_OPUS` | Claude Opus 4.7（v2.1.111+） |
| `VERTEX_REGION_CLAUDE_4_8_OPUS` | Claude Opus 4.8（v2.1.154+） |
| `VERTEX_REGION_CLAUDE_FABLE_5` | Claude Fable 5（v2.1.170+） |
| `VERTEX_REGION_CLAUDE_HAIKU_4_5` | Claude Haiku 4.5 |

此外，标准 OpenTelemetry 导出器变量（`OTEL_METRICS_EXPORTER`、`OTEL_LOGS_EXPORTER`、`OTEL_EXPORTER_OTLP_ENDPOINT`、`OTEL_EXPORTER_OTLP_PROTOCOL`、`OTEL_EXPORTER_OTLP_HEADERS`、`OTEL_METRIC_EXPORT_INTERVAL`、`OTEL_RESOURCE_ATTRIBUTES` 及信号特定变体）也受支持。详见 [Monitoring](https://code.claude.com/docs/en/monitoring-usage)。

## 相关文档

- [Settings](https://code.claude.com/docs/en/settings)：所有 settings.json 配置（包括 `env` 字段）
- [CLI reference](https://code.claude.com/docs/en/cli-reference)：启动时参数
- [Network configuration](https://code.claude.com/docs/en/network-config)：代理和 TLS 配置
- [Monitoring](https://code.claude.com/docs/en/monitoring-usage)：OpenTelemetry 配置
