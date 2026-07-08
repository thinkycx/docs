---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】认证
description: Claude Code 支持多种认证方式：claude.ai 订阅、Console 账号、云服务商凭证和 Claude apps gateway。本文介绍登录流程、团队认证配置和凭证管理。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/authentication.md
  - en-source/authentication.md
---

# 认证

> 登录 Claude Code 并为个人、团队和组织配置认证方式。

**Claude Code 支持多种认证方式。** 个人用户可用 claude.ai 账号登录，团队可使用 Claude for Teams/Enterprise、Claude Console、或 Amazon Bedrock、Google Cloud Agent Platform、Microsoft Foundry 等云服务商。

## 登录 Claude Code

[安装 Claude Code](https://code.claude.com/docs/en/setup#install-claude-code) 后，在终端运行 `claude`。首次启动时会打开浏览器窗口进行登录。

如果浏览器未自动打开，按 `c` 复制登录 URL 到剪贴板，然后粘贴到浏览器中。

如果浏览器显示登录码而非自动重定向，将其粘贴到终端的 `Paste code here if prompted` 提示处。这通常发生在 WSL2、SSH 会话和容器中，因为浏览器无法连接到 Claude Code 的本地回调服务器。

支持的账号类型：

| 账号类型 | 说明 |
| --- | --- |
| Claude Pro 或 Max 订阅 | 用 claude.ai 账号登录。订阅地址 [claude.com/pricing](https://claude.com/pricing) |
| Claude for Teams 或 Enterprise | 用团队管理员邀请的 claude.ai 账号登录 |
| Claude Console | 用 Console 凭证登录。管理员需先[邀请你](#claude-console-认证) |
| 云服务商 | 使用 [Amazon Bedrock](https://code.claude.com/docs/en/amazon-bedrock)、[Google Cloud Agent Platform](https://code.claude.com/docs/en/google-vertex-ai) 或 [Microsoft Foundry](https://code.claude.com/docs/en/microsoft-foundry) 时，运行 `claude` 前设置所需环境变量。无需浏览器登录 |
| Cloud gateway | 组织运行自托管 [Claude apps gateway](https://code.claude.com/docs/en/claude-apps-gateway) 时，通过 `/login` 使用企业 SSO 登录。gateway 颁发的 token 是会话的唯一凭证 |

运行 `/logout` 注销并重新认证。

登录遇到问题请参见[认证故障排除](https://code.claude.com/docs/en/troubleshoot-install#login-and-authentication)。

## 配置团队认证

团队和组织可通过以下方式配置 Claude Code 访问：

- [Claude for Teams 或 Enterprise](#claude-for-teams-或-enterprise)
- [Claude Console](#claude-console-认证)
- [Claude apps gateway](https://code.claude.com/docs/en/claude-apps-gateway)：自托管 gateway，通过 IdP 登录并路由推理至配置的云服务商
- [Amazon Bedrock](https://code.claude.com/docs/en/amazon-bedrock)
- [Google Cloud Agent Platform](https://code.claude.com/docs/en/google-vertex-ai)
- [Microsoft Foundry](https://code.claude.com/docs/en/microsoft-foundry)

### Claude for Teams 或 Enterprise

**[Claude for Teams](https://claude.com/pricing) 和 [Claude for Enterprise](https://anthropic.com/contact-sales) 为组织提供最佳体验。** 团队成员同时获得 Claude Code 和 Claude Web 访问权限，集中计费和团队管理。

- **Claude for Teams**：自助计划，含协作功能、管理工具和计费管理。适合小团队。
- **Claude for Enterprise**：增加 SSO、域名捕获、基于角色的权限、合规 API 和托管策略设置。适合有安全合规要求的大组织。

配置步骤：

1. 订阅 [Claude for Teams](https://claude.com/pricing) 或联系销售获取 [Claude for Enterprise](https://anthropic.com/contact-sales)
2. 从管理面板邀请团队成员
3. 团队成员安装 Claude Code 并用 claude.ai 账号登录

### Claude Console 认证

**对于偏好 API 计费的组织，可通过 Claude Console 配置访问。**

配置步骤：

1. 使用现有 Console 账号或创建新账号
2. 添加用户（两种方式）：
   - Console 内批量邀请：Settings -> Members -> Invite
   - [设置 SSO](https://support.claude.com/en/articles/13132885-setting-up-single-sign-on-sso)
3. 分配角色：
   - **Claude Code** 角色：用户只能创建 Claude Code API key
   - **Developer** 角色：用户可创建任何类型的 API key
4. 用户完成设置：接受邀请 -> 检查[系统要求](https://code.claude.com/docs/en/setup#system-requirements) -> [安装 Claude Code](https://code.claude.com/docs/en/setup#install-claude-code) -> 用 Console 凭证登录

### 云服务商认证

使用 Amazon Bedrock、Google Cloud Agent Platform 或 Microsoft Foundry 的团队：

1. 按照对应文档设置：[Amazon Bedrock](https://code.claude.com/docs/en/amazon-bedrock)、[Google Cloud Agent Platform](https://code.claude.com/docs/en/google-vertex-ai) 或 [Microsoft Foundry](https://code.claude.com/docs/en/microsoft-foundry)
2. 将环境变量和生成云凭证的说明分发给用户。[管理配置](https://code.claude.com/docs/en/settings)中有更多细节
3. 用户[安装 Claude Code](https://code.claude.com/docs/en/setup#install-claude-code)

## 凭证管理

**Claude Code 安全地管理认证凭证：**

- **存储位置**：
  - macOS：存储在加密的 macOS Keychain 中
  - Linux：存储在 `~/.claude/.credentials.json`，文件权限 `0600`
  - Windows：存储在 `%USERPROFILE%\.claude\.credentials.json`，继承用户配置文件目录的访问控制
  - 如果设置了 `CLAUDE_CONFIG_DIR` 环境变量（Linux/Windows），`.credentials.json` 在该目录下
  - Claude Code 通过 `/login` 和 `/logout` 管理 `.credentials.json`。路由请求到自定义 API 端点请设置 [`ANTHROPIC_BASE_URL`](https://code.claude.com/docs/en/env-vars) 环境变量
- **支持的认证类型**：Claude.ai 凭证、Claude API 凭证、Azure Auth、Bedrock Auth、Vertex Auth 和 [Claude apps gateway](https://code.claude.com/docs/en/claude-apps-gateway) 会话 token
- **自定义凭证脚本**：[`apiKeyHelper`](https://code.claude.com/docs/en/settings#available-settings) 设置可配置运行一个返回 API key 的 shell 脚本
- **刷新间隔**：默认 `apiKeyHelper` 在 5 分钟后或 HTTP 401 响应时被调用。设置 `CLAUDE_CODE_API_KEY_HELPER_TTL_MS` 环境变量自定义刷新间隔
- **慢 helper 提示**：如果 `apiKeyHelper` 超过 10 秒返回 key，Claude Code 在提示栏显示警告。如果经常看到此提示，检查凭证脚本是否可优化

`apiKeyHelper`、`ANTHROPIC_API_KEY` 和 `ANTHROPIC_AUTH_TOKEN` 适用于 CLI 及其封装的界面（VS Code 扩展、Agent SDK、GitHub Actions）。Claude Desktop 和云会话不调用 `apiKeyHelper` 也不读取这些环境变量：它们使用 OAuth，除非桌面会话运行[组织分发的第三方推理配置](https://code.claude.com/docs/en/llm-gateway-connect#desktop-app)。

### 认证优先级

**多个凭证同时存在时，Claude Code 按以下顺序选择：**

| 优先级 | 凭证 | 说明 |
| --- | --- | --- |
| 1 | 云服务商凭证 | 设置了 `CLAUDE_CODE_USE_BEDROCK`、`CLAUDE_CODE_USE_VERTEX` 或 `CLAUDE_CODE_USE_FOUNDRY` 时 |
| 2 | `ANTHROPIC_AUTH_TOKEN` 环境变量 | 作为 `Authorization: Bearer` header 发送。用于通过 bearer token 认证的 [LLM gateway](https://code.claude.com/docs/en/llm-gateway) |
| 3 | `ANTHROPIC_API_KEY` 环境变量 | 作为 `X-Api-Key` header 发送。用于 [Claude Console](https://platform.claude.com) 的直接 API 访问。交互模式下首次使用会提示确认 |
| 4 | [`apiKeyHelper`](https://code.claude.com/docs/en/settings#available-settings) 脚本输出 | 用于动态或轮换凭证，如从 vault 获取的短期 token |
| 5 | `CLAUDE_CODE_OAUTH_TOKEN` 环境变量 | 由 [`claude setup-token`](#生成长期-token) 生成的长期 OAuth token。用于无法浏览器登录的 CI 管道 |
| 6 | `/login` 的订阅 OAuth 凭证 | Claude Pro、Max、Team 和 Enterprise 用户的默认方式 |

**已登录的 [Claude apps gateway](https://code.claude.com/docs/en/claude-apps-gateway) 会话在此列表之外**，属于服务商选择级别（类似 Bedrock / Vertex），优先级高于以上所有。gateway 会话存在时，CLI 使用 gateway token 认证，即使设置了 `CLAUDE_CODE_USE_BEDROCK` 等变量，bearer token、API key 和 `apiKeyHelper` 也不会被使用。

如果你有活跃的 Claude 订阅同时设置了 `ANTHROPIC_API_KEY`，API key 确认后优先使用。如果 key 属于已禁用或过期的组织可能导致认证失败。运行 `unset ANTHROPIC_API_KEY` 回退到订阅，用 `/status` 确认当前方式。

[Claude Code on the Web](https://code.claude.com/docs/en/claude-code-on-the-web) 始终使用订阅凭证。沙箱环境中的 `ANTHROPIC_API_KEY` 和 `ANTHROPIC_AUTH_TOKEN` 不会覆盖它们。

### 生成长期 token

**对于无法进行交互式浏览器登录的 CI 管道、脚本等环境**，用 `claude setup-token` 生成一年有效期的 OAuth token：

```bash
claude setup-token
```

该命令引导你完成 OAuth 授权并将 token 打印到终端。**不会保存 token 到任何位置**——复制并设置为 `CLAUDE_CODE_OAUTH_TOKEN` 环境变量：

```bash
export CLAUDE_CODE_OAUTH_TOKEN=your-token
```

此 token 使用你的 Claude 订阅认证，需要 Pro、Max、Team 或 Enterprise 计划。仅限推理用途，不能建立 [Remote Control](https://code.claude.com/docs/en/remote-control) 会话。

[Bare mode](https://code.claude.com/docs/en/headless#start-faster-with-bare-mode) 不读取 `CLAUDE_CODE_OAUTH_TOKEN`。如果脚本传入 `--bare`，请使用 `ANTHROPIC_API_KEY` 或 `apiKeyHelper` 认证。
