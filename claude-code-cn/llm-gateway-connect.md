---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Gateway 连接
description: 如何将 Claude Code 连接到组织的 LLM 网关，包括检查已有配置、设置 Base URL 和凭证、验证连接、各平台配置方式及故障排查。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/llm-gateway-connect.md
  - en-source/llm-gateway-connect.md
---

# 连接 Claude Code 到 LLM 网关

> 将 Claude Code 指向组织的 LLM 网关。检查管理员是否已配置好，或自行为 CLI、VS Code、GitHub Actions 和 Agent SDK 设置 Base URL 和凭证，然后验证连接并修复错误。

**[LLM 网关](https://code.claude.com/docs/en/llm-gateway)是组织在 Claude Code 和模型提供商之间运行的代理。** 使用网关时，Claude Code 通过组织签发的凭证认证，而非个人 claude.ai 登录。

本页面面向通过组织网关运行 Claude Code 的开发者，涵盖两条路径：[检查管理员是否已为你配置好](#检查已有配置)，以及未配置时[自行设置](#自行配置-claude-code)。

> - 部署组织网关：[推广 LLM 网关](https://code.claude.com/docs/en/llm-gateway-rollout)
> - Claude Code 向网关发送的内容：[网关协议参考](https://code.claude.com/docs/en/llm-gateway-protocol)

## 检查已有配置

**管理员可能已通过[托管设置](https://code.claude.com/docs/en/settings#settings-files)、设备管理或 [`apiKeyHelper`](#使用-apikeyhelper-轮换凭证) 分发了网关地址和凭证。** Claude Code 启动时会自动识别，无需手动设置。检查方式：

1. **启动 Claude Code**：运行 `claude`。如果出现登录界面而非直接进入会话，说明没有分发网关凭证；按下文[自行配置](#自行配置-claude-code)。

2. **检查 Status 标签**：如果 Claude Code 未显示登录界面直接进入会话，运行 `/status`，打开 **Status** 标签，检查两行内容：
   - `Anthropic base URL`：仅在设置了网关地址时出现。如果不存在，说明 Claude Code 未指向网关。
   - `Auth token` 或 `API key`：显示 `ANTHROPIC_AUTH_TOKEN`、`ANTHROPIC_API_KEY` 或 `apiKeyHelper` 表示网关凭证生效。如果是 `Login method` 行指向 claude.ai 账号，则凭证未分发。

3. **发送测试消息**：关闭 `/status` 菜单，发送任意提示词。收到正常回复即确认网关连接正常。

如果 `/status` 显示正常但消息失败，参见[故障排查表](#排查网关错误)。

## 自行配置 Claude Code

**自行配置网关需要从网关团队获取：**

- 网关的 Base URL
- 凭证：密钥/令牌字符串，或获取凭证的命令

### 设置凭证变量

**根据网关团队告知的凭证类型，设置对应的环境变量：**

| 凭证变量 | 适用场景 |
| :--- | :--- |
| `ANTHROPIC_AUTH_TOKEN` | 网关团队说的是「bearer token」或「Authorization 头」 |
| `ANTHROPIC_API_KEY` | 网关团队说的是「API key」或「x-api-key」 |
| [`apiKeyHelper`](#使用-apikeyhelper-轮换凭证) | 凭证会轮换或来自密钥库 |

如果不确定用哪个，先用 `ANTHROPIC_AUTH_TOKEN`；[验证请求](#验证连接)时会知道是否需要切换。

### 设置 Base URL 和凭证

**将网关 Base URL 和凭证设为环境变量。** 下面示例使用 `ANTHROPIC_AUTH_TOKEN`；如果你选的是 `ANTHROPIC_API_KEY`，请替换。

#### Shell 环境变量方式

```bash
export ANTHROPIC_BASE_URL=https://llm-gateway.example.com
export ANTHROPIC_AUTH_TOKEN=sk-gateway-key
```

PowerShell：

```powershell
$env:ANTHROPIC_BASE_URL = "https://llm-gateway.example.com"
$env:ANTHROPIC_AUTH_TOKEN = "sk-gateway-key"
```

Shell 导出仅对当前终端会话及其启动的程序生效。从 Dock 或开始菜单启动的编辑器不会看到。要持久化，将相同行添加到 Shell 配置文件（如 `~/.zshrc`、`~/.bashrc`），或使用设置文件。

#### 设置文件方式

**在[设置文件](https://code.claude.com/docs/en/settings)的 `env` 块中设置变量，无需依赖 Shell：**

- `~/.claude/settings.json`：适用于所有项目
- `.claude/settings.local.json`：适用于单个项目（确保已加入 .gitignore）

> 不要将凭证放在项目的 `.claude/settings.json` 中——该文件会提交到仓库。

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://llm-gateway.example.com",
    "ANTHROPIC_AUTH_TOKEN": "sk-gateway-key"
  }
}
```

当 Shell 导出和设置文件 `env` 块同时设置同一变量时，设置文件的值优先。运行 `/status` 可查看 Claude Code 使用的 Base URL 和凭证来源。

### 验证连接

**导出变量后，直接向网关发送一个单 token 请求来验证 URL 和凭证：**

```bash
curl -X POST "$ANTHROPIC_BASE_URL/v1/messages" \
  -H "Authorization: Bearer $ANTHROPIC_AUTH_TOKEN" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model": "claude-sonnet-4-6", "max_tokens": 1, "messages": [{"role": "user", "content": "."}]}'
```

如果网关使用 `x-api-key` 头，将 `Authorization` 头替换为 `x-api-key: $ANTHROPIC_API_KEY`。

**判断结果：**
- JSON 响应以 `{"id":"msg_` 开头且包含 `"content":[...]` 字段：网关可达、凭证有效
- 模型名不认识的错误：仍然证明 URL 和凭证有效（网关认证了请求后才拒绝模型名）
- `401`：凭证被拒绝，切换到另一个变量重试

#### 在 Claude Code 中确认

从同一 Shell 启动 `claude`（继承导出的变量），发送消息后运行 `/status`。在 **Status** 标签中，`Anthropic base URL` 行应显示你的网关地址。

### 凭证变量与请求头的映射

**每个变量以不同的 HTTP 头发送凭证：**

| 变量 | 发送方式 |
| :--- | :--- |
| `ANTHROPIC_AUTH_TOKEN` | `Authorization: Bearer` |
| `ANTHROPIC_API_KEY` | `x-api-key` |
| `apiKeyHelper` | 两者都发 |

凭证放错变量时，会以网关不读取的头发送，请求返回 `401`。

### 与已有登录的冲突

**网关凭证变量优先于已保存的 claude.ai 登录或 Console 密钥。** 已保存登录在变量设置期间保留但未使用；取消变量后 Claude Code 会恢复使用。运行 `/status` 确认当前活跃凭证源。要清除已保存登录使网关凭证唯一，运行 `/logout`。

## 各平台配置

### VS Code 扩展

**在 VS Code 用户设置（JSON）的 `claudeCode.environmentVariables` 中设置网关变量：**

```json
{
  "claudeCode.environmentVariables": [
    { "name": "ANTHROPIC_BASE_URL", "value": "https://llm-gateway.example.com" },
    { "name": "ANTHROPIC_AUTH_TOKEN", "value": "sk-gateway-key" }
  ]
}
```

### 桌面应用

桌面应用从[管理员分发的配置](https://claude.com/docs/cowork/3p/gateway)读取网关路由，不从 `ANTHROPIC_BASE_URL` 或 `settings.json` 读取。如果组织未分发，请使用终端 CLI 或 VS Code 扩展。

### GitHub Actions

[Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions) 从工作流 `env` 块读取 `ANTHROPIC_BASE_URL` 和 `ANTHROPIC_CUSTOM_HEADERS`。将凭证作为 action 的 `anthropic_api_key` 输入传递。

x-api-key 网关：

```yaml
env:
  ANTHROPIC_BASE_URL: https://llm-gateway.example.com

steps:
  - uses: anthropics/claude-code-action@v1
    with:
      anthropic_api_key: ${{ secrets.GATEWAY_API_KEY }}
```

Bearer token 网关：

```yaml
env:
  ANTHROPIC_BASE_URL: https://llm-gateway.example.com
  ANTHROPIC_AUTH_TOKEN: ${{ secrets.GATEWAY_API_KEY }}

steps:
  - uses: anthropics/claude-code-action@v1
    with:
      anthropic_api_key: ${{ secrets.GATEWAY_API_KEY }}
```

### Agent SDK

[Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) 没有网关专用选项；它将环境变量传递给生成的 Claude Code 进程。

- **TypeScript**：设置 `options.env` 会完全替换环境。将 `process.env` 展开进去以保留网关变量。
- **Python**：`ClaudeAgentOptions(env=...)` 合并到继承的环境之上，网关变量自动传递。

```ts
const result = query({
  prompt: "...",
  options: {
    env: {
      ...process.env,
      ANTHROPIC_BASE_URL: "https://llm-gateway.example.com",
      ANTHROPIC_AUTH_TOKEN: process.env.GATEWAY_KEY,
    },
  },
})
```

```python
options = ClaudeAgentOptions(
    env={
        "ANTHROPIC_BASE_URL": "https://llm-gateway.example.com",
        "ANTHROPIC_AUTH_TOKEN": os.environ["GATEWAY_KEY"],
    }
)
```

### Slack、Web 和 Remote Control

[Slack 中的 Claude Code](https://code.claude.com/docs/en/slack) 和 [Web 版 Claude Code](https://code.claude.com/docs/en/claude-code-on-the-web) 是 Anthropic 托管的产品，始终使用 Anthropic API，不属于网关部署范围。

[Remote Control](https://code.claude.com/docs/en/remote-control) 和[语音听写](https://code.claude.com/docs/en/voice-dictation)依赖 claude.ai 身份，在 `ANTHROPIC_API_KEY`、`ANTHROPIC_AUTH_TOKEN` 或 `apiKeyHelper` 生效时不可用。自 v2.1.196 起，当 `ANTHROPIC_BASE_URL` 指向非 Anthropic 主机时，Remote Control 也被禁用。

## 附加配置

### 发送自定义请求头

**某些网关需要额外头（如租户标识或路由键）：**

```bash
export ANTHROPIC_CUSTOM_HEADERS="X-Org-Route: prod"
```

设置文件中用 `\n` 分隔多个头：

```json
{
  "env": {
    "ANTHROPIC_CUSTOM_HEADERS": "X-Org-Route: prod\nX-Tenant: example"
  }
}
```

### 将网关模型添加到模型选择器

**模型发现（Model Discovery）在启动时查询网关的模型列表，添加到 `/model` 选择器。**

启用方式：设置 `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1`。需要 Claude Code v2.1.129 或更高版本。

发现的模型标记为「From gateway」。启动 `claude --debug` 并查找 `[gatewayDiscovery]` 行可确认发现结果。

### 使用 apiKeyHelper 轮换凭证

**`apiKeyHelper` 是 Claude Code 运行的命令，用于获取网关凭证而非从静态环境变量读取。**

适用于凭证有过期时间、来自密钥库或 SSO 命令的情况。Helper 是任何将当前凭证打印到 stdout 的 Shell 命令。

```bash
#!/bin/bash
vault kv get -field=api_key secret/llm-gateway/claude-code
```

在 `~/.claude/settings.json` 中引用：

```json
{
  "apiKeyHelper": "~/bin/get-gateway-key.sh"
}
```

Claude Code 默认缓存 helper 输出 5 分钟，收到 HTTP 401 时重新运行。通过 `CLAUDE_CODE_API_KEY_HELPER_TTL_MS` 调整缓存时长（毫秒）。

Helper 的值会同时发送到 `Authorization` 和 `x-api-key` 头。

### 通过网关路由到云服务商

**仅在网关团队明确指定 Amazon Bedrock、Google Cloud Agent Platform、Microsoft Foundry 或 Claude Platform on AWS 时才设置以下配置。**

#### Amazon Bedrock

```bash
export ANTHROPIC_BEDROCK_BASE_URL=https://llm-gateway.example.com/bedrock
export CLAUDE_CODE_SKIP_BEDROCK_AUTH=1
export CLAUDE_CODE_USE_BEDROCK=1
```

#### Google Cloud Agent Platform

```bash
export ANTHROPIC_VERTEX_BASE_URL=https://llm-gateway.example.com/vertex
export ANTHROPIC_VERTEX_PROJECT_ID=your-gcp-project-id
export CLAUDE_CODE_SKIP_VERTEX_AUTH=1
export CLAUDE_CODE_USE_VERTEX=1
export CLOUD_ML_REGION=us-east5
```

#### Microsoft Foundry

```bash
export ANTHROPIC_FOUNDRY_BASE_URL=https://llm-gateway.example.com/foundry
export ANTHROPIC_FOUNDRY_API_KEY=sk-gateway-key
export CLAUDE_CODE_USE_FOUNDRY=1
```

#### Claude Platform on AWS

```bash
export ANTHROPIC_AWS_BASE_URL=https://llm-gateway.example.com/anthropic-aws
export ANTHROPIC_AWS_WORKSPACE_ID=wrkspc_01ABCDEFGHIJKLMN
export CLAUDE_CODE_SKIP_ANTHROPIC_AWS_AUTH=1
export CLAUDE_CODE_USE_ANTHROPIC_AWS=1
```

## 排查网关错误

| 错误 | 原因 | 修复方式 |
| :--- | :--- | :--- |
| 启动警告提示两个凭证源 | 网关凭证和已保存登录同时生效 | 取消变量以使用登录，或运行 `/logout` 以使用网关凭证 |
| `401` 无效令牌 | 凭证不是网关签发的，或在网关不读取的头中 | 确认变量与凭证类型匹配，必要时在网关重新生成密钥 |
| `ConnectionRefused` | Base URL 错误或 VPN/防火墙阻断 | 运行上述 curl 测试，与网关团队确认 URL 和网络路径 |
| HTTP 200 但响应为空或畸形 | 网关或中间代理返回了非 API 响应（如 HTML 错误页） | 用 curl 测试；修复网关返回非 JSON 的路由 |
| `400` 提示 `context_management` 等不支持字段 | 网关转发到不支持 Claude Code 新增字段的上游 | 设置 `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1` |
| `400` 提示 `thinking` 或 `adaptive` | 上游模型不支持自适应推理 | 升级上游；或设置 `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` |
| `400` 上下文/token 超限 | 网关强制了比模型原生窗口更小的上下文限制 | 运行 `/compact` 恢复；设置 `CLAUDE_CODE_AUTO_COMPACT_WINDOW` 为网关限制 |
| 模型不在 `/model` 选择器中 | 网关模型名不在内置列表中 | 启用[网关模型发现](#将网关模型添加到模型选择器) |
| Claude Code 要求登录但 curl 成功 | CLI 没有自己的凭证 | 在 Shell 导出或 `~/.claude/settings.json` 的 `env` 块中设置 `ANTHROPIC_AUTH_TOKEN` |
| 已设 `ANTHROPIC_API_KEY` 但被忽略 | 密钥需一次性批准，之前拒绝的密钥被静默忽略 | 在 `/config` 中启用「Use custom API key」选项 |
| `This machine's managed settings require a first-party login` | 托管设置含 `forceLoginMethod`/`forceLoginOrgUUID`，与网关凭证冲突 | 管理员需移除 forceLogin 或移除网关凭证 |
| `403` HTML 响应但网关日志无请求 | WAF 或反向代理阻止了请求体 | 豁免网关 `/v1/messages` 路径的请求体检查 |
| TLS 证书错误 | Claude Code 运行时不信任 curl 使用的 CA | 设置 `NODE_EXTRA_CA_CERTS` 指向 CA 证书包 |

如果移除网关配置后 Claude Code 反复提示登录，原因通常是凭证存储而非网关；参见[认证错误](https://code.claude.com/docs/en/errors#authentication-errors)。

## 相关资源

- [LLM 网关概览](https://code.claude.com/docs/en/llm-gateway)：网关定义及与订阅的交互
- [为组织推广 LLM 网关](https://code.claude.com/docs/en/llm-gateway-rollout)：管理员部署和分发网关配置的检查清单
- [网关协议参考](https://code.claude.com/docs/en/llm-gateway-protocol)：Claude Code 向网关发送的内容
- [设置](https://code.claude.com/docs/en/settings)：设置文件位置及 `env` 块读取方式
- [认证](https://code.claude.com/docs/en/authentication)：凭证变量、`apiKeyHelper` 和 OAuth 登录的交互
