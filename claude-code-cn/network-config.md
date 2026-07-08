---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】网络配置
description: 为企业环境配置 Claude Code 的代理服务器、自定义 CA 证书和 mTLS 认证，以及网络访问白名单要求。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/network-config.md
  - en-source/network-config.md
---

# 企业网络配置

> 在企业环境中配置 Claude Code 的代理服务器、自定义 CA 证书（Certificate Authority）和 mTLS 双向认证。

**Claude Code 通过环境变量支持各种企业网络和安全配置。** 包括通过企业代理路由流量、信任自定义 CA、以及使用 mTLS 客户端证书进行增强安全认证。

本页所有环境变量也可在 [`settings.json`](https://code.claude.com/docs/en/settings) 中配置。

## 代理配置

### 环境变量

Claude Code 遵循标准代理环境变量：

```bash
# HTTPS 代理（推荐）
export HTTPS_PROXY=https://proxy.example.com:8080

# HTTP 代理（HTTPS 不可用时）
export HTTP_PROXY=http://proxy.example.com:8080

# 绕过代理的请求 - 空格分隔格式
export NO_PROXY="localhost 192.168.1.1 example.com .example.com"
# 绕过代理的请求 - 逗号分隔格式
export NO_PROXY="localhost,192.168.1.1,example.com,.example.com"
# 所有请求绕过代理
export NO_PROXY="*"
```

Claude Code 不支持 SOCKS 代理。

### 基本认证

如果代理需要基本认证，在代理 URL 中包含凭据：

```bash
export HTTPS_PROXY=http://username:password@proxy.example.com:8080
```

避免在脚本中硬编码密码。请使用环境变量或安全凭据存储。

对于需要高级认证（NTLM、Kerberos 等）的代理，考虑使用支持你的认证方式的 LLM 网关服务。

## CA 证书存储

**默认情况下，Claude Code 同时信任其内置的 Mozilla CA 证书和操作系统的证书存储。** 读取操作系统存储需要有 `tls.getCACertificates` 的运行时：原生安装器始终具备此能力，npm 安装需要 Node 22.15 或更高版本。较旧的 Node 版本仅应用内置集和 `NODE_EXTRA_CA_CERTS`。CrowdStrike Falcon 和 Zscaler 等企业 TLS 检查代理在其根证书安装到操作系统信任存储且运行时可读取时，无需额外配置即可工作。

`CLAUDE_CODE_CERT_STORE` 接受逗号分隔的来源列表。可识别的值为 `bundled`（Claude Code 自带的 Mozilla CA 集）和 `system`（操作系统信任存储）。默认为 `bundled,system`。

仅信任内置 Mozilla CA 集：

```bash
export CLAUDE_CODE_CERT_STORE=bundled
```

仅信任操作系统证书存储：

```bash
export CLAUDE_CODE_CERT_STORE=system
```

`CLAUDE_CODE_CERT_STORE` 没有专用的 `settings.json` schema 键。通过 `~/.claude/settings.json` 中的 `env` 块设置，或直接在进程环境中设置。

## 自定义 CA 证书

如果企业环境使用自定义 CA，配置 Claude Code 直接信任它：

```bash
export NODE_EXTRA_CA_CERTS=/path/to/ca-cert.pem
```

## mTLS 认证

**需要客户端证书认证的企业环境：**

```bash
# 客户端证书
export CLAUDE_CODE_CLIENT_CERT=/path/to/client-cert.pem

# 客户端私钥
export CLAUDE_CODE_CLIENT_KEY=/path/to/client-key.pem

# 可选：加密私钥的密码
export CLAUDE_CODE_CLIENT_KEY_PASSPHRASE="your-passphrase"
```

Claude Code 在启动时读取证书和密钥文件，并在每次应用设置时重新读取（包括会话期间设置变更时）。要轮换证书和密钥，替换相同路径的文件即可。

## 网络访问要求

**Claude Code 需要访问以下 URL。** 在代理配置和防火墙规则中将这些加入白名单，尤其在容器化或受限网络环境中。

| URL | 用途 |
| :--- | :--- |
| `api.anthropic.com` | Claude API 请求 |
| `claude.ai` | claude.ai 账户认证 |
| `platform.claude.com` | Anthropic Console 账户认证 |
| `downloads.claude.ai` | 插件可执行文件下载；原生安装器和自动更新器 |
| `storage.googleapis.com` | 2.1.116 之前版本的原生安装器和自动更新器 |
| `bridge.claudeusercontent.com` | [Chrome 中的 Claude](https://code.claude.com/docs/en/chrome) 扩展 WebSocket 桥接 |
| `*.claudeusercontent.com` | 在 claude.ai 查看 [artifacts](https://code.claude.com/docs/en/artifacts)。查看器从此源的沙箱子域加载每个 artifact 的内容。需在查看器的浏览器中放行，CLI 本身不需要 |
| `raw.githubusercontent.com` | [`/release-notes`](https://code.claude.com/docs/en/commands) 的变更日志和更新后的发布说明；插件市场安装计数 |

如果通过 npm 安装 Claude Code 或自行管理二进制分发，终端用户可能不需要访问 `downloads.claude.ai` 或 `storage.googleapis.com`。

Claude Code 还默认发送可选的运营遥测，可通过环境变量禁用。参见[遥测服务](https://code.claude.com/docs/en/data-usage#telemetry-services)了解如何在最终确定白名单前禁用。

使用 [Amazon Bedrock](https://code.claude.com/docs/en/amazon-bedrock)、[Google Cloud Agent Platform](https://code.claude.com/docs/en/google-vertex-ai)、[Microsoft Foundry](https://code.claude.com/docs/en/microsoft-foundry) 或已登录的 [Claude apps gateway](https://code.claude.com/docs/en/claude-apps-gateway) 会话时，模型流量和认证走你的提供商或网关而非 `api.anthropic.com`、`claude.ai` 或 `platform.claude.com`。WebFetch 工具仍会调用 `api.anthropic.com` 做[域名安全检查](https://code.claude.com/docs/en/data-usage#webfetch-domain-safety-check)，除非你在[设置](https://code.claude.com/docs/en/settings)中设置 `skipWebFetchPreflight: true`。

[Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web) 和 [Code Review](https://code.claude.com/docs/en/code-review) 从 Anthropic 托管的基础设施连接到你的仓库。如果你的 GitHub Enterprise Cloud 组织按 IP 限制访问，启用[已安装 GitHub Apps 的 IP 白名单继承](https://docs.github.com/en/enterprise-cloud@latest/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/managing-allowed-ip-addresses-for-your-organization#allowing-access-by-github-apps)。Claude GitHub App 注册了其 IP 范围，启用此设置即可允许访问而无需手动配置。要[手动将范围添加到白名单](https://docs.github.com/en/enterprise-cloud@latest/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/managing-allowed-ip-addresses-for-your-organization#adding-an-allowed-ip-address)或配置其他防火墙，参见 [Anthropic API IP 地址](https://platform.claude.com/docs/en/api/ip-addresses)。

对于防火墙后的自托管 [GitHub Enterprise Server](https://code.claude.com/docs/en/github-enterprise-server) 实例，将同样的 [Anthropic API IP 地址](https://platform.claude.com/docs/en/api/ip-addresses)加入白名单，以便 Anthropic 基础设施能访问你的 GHES 主机来克隆仓库和发布审查评论。

## 其他资源

- [Claude Code 设置](https://code.claude.com/docs/en/settings)
- [环境变量参考](https://code.claude.com/docs/en/env-vars)
- [故障排除指南](https://code.claude.com/docs/en/troubleshooting)
