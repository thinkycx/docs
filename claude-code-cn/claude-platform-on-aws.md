---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】AWS 平台
description: 配置 Claude Code 使用 Claude Platform on AWS，包括 AWS 认证、SigV4 签名、工作区 API 密钥、Agent SDK 集成和代理路由。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/claude-platform-on-aws.md
  - en-source/claude-platform-on-aws.md
---

# Claude Code on Claude Platform on AWS

> 配置 Claude Code 使用 Anthropic 运营的 Claude API，搭配 AWS 认证、IAM 访问控制和 AWS Marketplace 计费。

**Claude Platform on AWS 是 Anthropic 运营的 Claude API，搭配 AWS 认证、IAM 访问控制和 AWS Marketplace 计费。** 请求直接到达 Anthropic 的 API，获得与 [Claude API](https://platform.claude.com/docs) 相同的模型和功能，且发布节奏一致。认证使用 AWS 凭证或工作区 API 密钥，通过 AWS Marketplace 付费。

本指南帮你将 Claude Code 指向已通过 Claude Platform on AWS 创建的工作区。AWS 订阅和工作区设置请参阅 [Claude Platform on AWS 文档](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws)。

> 通过 AWS Marketplace 订阅会创建一个绑定到你 AWS 账户的新 Anthropic 组织。该组织与你在 Anthropic 已有的组织是独立的，凭证不互通。请使用 AWS 关联组织的工作区 ID 和 API 密钥，而非已有的 Claude Console 账号。

## 前提条件

配置 Claude Code 之前需要：

- 通过 AWS Marketplace 的活跃 Claude Platform on AWS 订阅
- AWS 关联 Anthropic 组织中的工作区及其工作区 ID
- 具有 Anthropic 服务调用权限的 IAM 主体，或限定于工作区的 API 密钥
- 环境中的 AWS 凭证、`~/.aws/credentials` 或附加的 IAM 角色（若要使用 SigV4 认证）。AWS CLI 仅在 SSO 登录流程中需要。

## 设置

### 1. 配置 AWS 凭证

**Claude Code 支持两种 Claude Platform on AWS 认证方式：**

**方式 A：AWS 凭证 + SigV4**

Claude Code 使用标准 AWS 凭证链进行 SigV4 签名：环境变量、`~/.aws/credentials` 中的共享凭证、IAM 角色、AWS SSO 会话以及 AWS SDK 支持的其他来源。

本地使用时，在启动 Claude Code 前通过 AWS CLI 登录：

```bash
aws sso login --profile my-profile
export AWS_PROFILE=my-profile
```

CI 和自动化场景中，给 Runner 分配具有 Anthropic 服务调用权限的 IAM 角色并设置 `AWS_REGION`。凭证链自动获取角色。

如果 SSO 凭证在会话中过期，配置 [`awsAuthRefresh`](https://code.claude.com/docs/en/amazon-bedrock#advanced-credential-configuration) 让 Claude Code 重新运行登录命令并重试。自动刷新需要 Claude Code v2.1.198 或更高版本。在 `settings.json` 中添加：

```json
{
  "awsAuthRefresh": "aws sso login --profile my-profile"
}
```

配置 `awsAuthRefresh` 后，`/login` 在 **Using 3rd-party platforms** 下显示 **Claude Platform on AWS - refresh credentials** 选项。

**方式 B：工作区 API 密钥**

工作区 API 密钥是长期有效的密钥，适合不想管理联邦 AWS 凭证的场景。在 AWS Console 的 **Claude Platform on AWS - API keys** 中生成：

```bash
export ANTHROPIC_AWS_API_KEY=sk-ant-xxxxx
```

密钥作为 `x-api-key` 发送，优先于 SigV4，环境中的 AWS 凭证会被忽略。

> `/login` 和 `/logout` 命令不能让你登录 claude.ai 订阅。认证通过 AWS 凭证或工作区 API 密钥进行。例外是配置了 `awsAuthRefresh` 时 `/login` 显示的 refresh credentials 选项。

### 2. 配置 Claude Code

**设置环境变量将 Claude Code 路由到 Claude Platform on AWS：**

```bash
export CLAUDE_CODE_USE_ANTHROPIC_AWS=1
export ANTHROPIC_AWS_WORKSPACE_ID=wrkspc_01ABCDEFGHIJKLMN
export AWS_REGION=us-east-1
```

`ANTHROPIC_AWS_WORKSPACE_ID` 是必需的，每个请求都通过 `anthropic-workspace-id` 头发送。Base URL 从 `AWS_REGION` 计算为 `https://aws-external-anthropic.{region}.api.aws`。要直接覆盖 URL，设置 `ANTHROPIC_AWS_BASE_URL`。

Claude Platform on AWS 即使环境中有 AWS 凭证也需要显式启用。Amazon Bedrock 和 Microsoft Foundry 在提供商路由中优先级更高，因此如果设置了 `CLAUDE_CODE_USE_BEDROCK` 和 `CLAUDE_CODE_USE_FOUNDRY` 需要取消。

### 3. 固定模型版本

**Claude Platform on AWS 使用与直接 Claude API 相同的模型 ID。** 默认别名 `fable`、`opus`、`sonnet` 和 `haiku` 解析为 Claude Code 对该平台的内置默认值，可能滞后于最新版本。未设置 `ANTHROPIC_DEFAULT_OPUS_MODEL` 时，`opus` 别名解析为 Opus 4.7。

如果向团队部署 Claude Code，显式固定模型 ID：

```bash
export ANTHROPIC_DEFAULT_FABLE_MODEL=claude-fable-5
export ANTHROPIC_DEFAULT_OPUS_MODEL=claude-opus-4-7
export ANTHROPIC_DEFAULT_SONNET_MODEL=claude-sonnet-5
export ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-haiku-4-5
```

模型 ID 和别名完整列表参见 [Models overview](https://platform.claude.com/docs/en/about-claude/models/overview)。其他模型相关变量参见[模型配置](https://code.claude.com/docs/en/model-config)。

[Prompt 缓存](https://code.claude.com/docs/en/prompt-caching)自动启用。要请求 1 小时缓存 TTL 而非 5 分钟默认值，设置 `ENABLE_PROMPT_CACHING_1H=1`。1 小时缓存写入按更高费率计费。

## 使用 Agent SDK

[Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) 读取与 CLI 相同的环境变量，所以任何生成 Claude Code 子进程的程序只需导出 `CLAUDE_CODE_USE_ANTHROPIC_AWS`、`ANTHROPIC_AWS_WORKSPACE_ID` 以及 `ANTHROPIC_AWS_API_KEY` 或 AWS 凭证。

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

process.env.CLAUDE_CODE_USE_ANTHROPIC_AWS = "1";
process.env.ANTHROPIC_AWS_WORKSPACE_ID = "wrkspc_01ABCDEFGHIJKLMN";
process.env.AWS_REGION = "us-east-1";

for await (const msg of query({ prompt: "What's in this repo?" })) {
  console.log(msg);
}
```

## 通过企业代理路由

**要通过代理或 [LLM 网关](https://code.claude.com/docs/en/llm-gateway)路由流量，设置 `ANTHROPIC_AWS_BASE_URL`：**

```bash
export CLAUDE_CODE_USE_ANTHROPIC_AWS=1
export ANTHROPIC_AWS_WORKSPACE_ID=wrkspc_01ABCDEFGHIJKLMN
export ANTHROPIC_AWS_BASE_URL=https://anthropic-proxy.example.com
```

如果网关自行签名请求，设置 `CLAUDE_CODE_SKIP_ANTHROPIC_AWS_AUTH=1` 让 Claude Code 发送未签名请求：

```bash
export CLAUDE_CODE_USE_ANTHROPIC_AWS=1
export CLAUDE_CODE_SKIP_ANTHROPIC_AWS_AUTH=1
export ANTHROPIC_AWS_WORKSPACE_ID=wrkspc_01ABCDEFGHIJKLMN
export ANTHROPIC_AWS_BASE_URL=https://anthropic-proxy.example.com
```

## 故障排查

运行 `/status` 查看解析后的提供商、工作区 ID、区域、Base URL 覆盖和 auth-skip 设置。

### `403 Forbidden` 或 `AccessDenied`

Claude Code 解析的 IAM 主体可能缺少调用 Anthropic 服务的权限。检查 AWS 配置文件或 Runner 附加的角色，验证其具有 [IAM action reference](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions) 中记录的 `aws-external-anthropic` 操作权限。

如果设置了 `ANTHROPIC_AWS_API_KEY`，密钥优先于 SigV4，过期密钥会产生相同错误。在 AWS Console 的 **Claude Platform on AWS - API keys** 中重新生成。

### 请求失败提示 missing-workspace 错误

`ANTHROPIC_AWS_WORKSPACE_ID` 可能未设置或为空。每个请求都必须包含工作区 ID。在 AWS Console 服务页的 **Workspaces** 下找到 ID。

### 请求仍发送到 `api.anthropic.com`

`CLAUDE_CODE_USE_ANTHROPIC_AWS` 可能未设置或值不为 truthy。设为 `1` 后运行 `/status` 确认。如果同时设置了 `CLAUDE_CODE_USE_BEDROCK` 或 `CLAUDE_CODE_USE_FOUNDRY`，这些优先级更高。

## 附加资源

- [Claude Platform on AWS 概览](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws)：订阅、工作区设置和产品参考
- [IAM action reference](https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions)：权限和托管策略
