---
title: 【译】企业部署概览
tags:
  - claude-code
  - enterprise
  - deployment
  - translation
create: 2026-06-28
update: 2026-06-28
author: thinkycx
category: translation
description: 介绍 Claude Code 的企业部署选项，对比 Claude for Teams/Enterprise、Anthropic Console 和各云提供商的差异，并提供代理/网关配置和组织最佳实践。
refs: https://code.claude.com/docs/en/third-party-integrations.md
---

# 企业部署概览

> 了解 Claude Code 如何与各种第三方服务和基础设施集成，以满足企业部署需求。

**组织可以通过 Anthropic 直接部署 Claude Code，也可以通过云提供商部署。** 本页帮助你选择正确的配置。

## 对比部署选项

**对于大多数组织，Claude for Teams 或 Claude for Enterprise 提供最佳体验。** 团队成员通过一个订阅即可获得 Claude Code 和网页版 Claude，拥有集中计费且无需基础设施搭建。

**Claude for Teams** 是自助服务，包含协作功能、管理工具和账单管理。最适合需要快速上手的小型团队。

**Claude for Enterprise** 增加了 SSO 和域名捕获、基于角色的权限、合规 API 访问以及用于在组织范围内部署 Claude Code 配置的托管策略设置。最适合有安全和合规要求的大型组织。

了解更多关于 [Team 计划](https://support.claude.com/en/articles/9266767-what-is-the-team-plan)和 [Enterprise 计划](https://support.claude.com/en/articles/9797531-what-is-the-enterprise-plan)。

如果组织有特定的基础设施要求，对比以下选项：

| 特性           | Claude for Teams/Enterprise | Anthropic Console | Amazon Bedrock | Claude Platform on AWS | Google Vertex AI | Microsoft Foundry |
| :------------- | :-------------------------- | :---------------- | :------------- | :--------------------- | :--------------- | :---------------- |
| 最适合         | 大多数组织（推荐）            | 独立开发者         | AWS 原生部署    | AWS Marketplace 计费 + Claude API 功能 | GCP 原生部署     | Azure 原生部署    |
| 计费           | Teams: $150/席位 (Premium) + PAYG<br />Enterprise: [联系销售](https://claude.com/contact-sales) | 按用量付费 | 通过 AWS 按用量付费 | 通过 AWS Marketplace 按用量付费 | 通过 GCP 按用量付费 | 通过 Azure 按用量付费 |
| 区域           | 支持的[国家](https://www.anthropic.com/supported-countries) | 支持的[国家](https://www.anthropic.com/supported-countries) | 多个 AWS [区域](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html) | 多个 AWS 区域 | 多个 GCP [区域](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations) | 多个 Azure [区域](https://azure.microsoft.com/en-us/explore/global-infrastructure/products-by-region/) |
| 提示缓存       | 默认启用                     | 默认启用           | 默认启用        | 默认启用                | 默认启用          | 默认启用           |
| 认证           | Claude.ai SSO 或邮箱         | API 密钥           | API 密钥或 AWS 凭据 | API 密钥或 AWS 凭据  | GCP 凭据          | API 密钥或 Microsoft Entra ID |
| 成本追踪       | 使用面板                     | 使用面板           | AWS Cost Explorer | AWS Cost Explorer   | GCP Billing       | Azure Cost Management |
| 包含网页版 Claude | 是                         | 否                | 否              | 否                    | 否               | 否                 |
| 企业功能       | 团队管理、SSO、使用监控        | 无                | IAM 策略、CloudTrail | IAM 策略、CloudTrail | IAM 角色、Cloud Audit Logs | RBAC 策略、Azure Monitor |

关于每个选项上可用功能的逐项对比，参见[功能可用性](https://code.claude.com/docs/en/feature-availability)。

选择部署选项查看设置说明：

* [Claude for Teams 或 Enterprise](https://code.claude.com/docs/en/authentication#claude-for-teams-or-enterprise)
* [Anthropic Console](https://code.claude.com/docs/en/authentication#claude-console-authentication)
* [Amazon Bedrock](https://code.claude.com/docs/en/amazon-bedrock)
* [Claude Platform on AWS](https://code.claude.com/docs/en/claude-platform-on-aws)
* [Google Vertex AI](https://code.claude.com/docs/en/google-vertex-ai)
* [Microsoft Foundry](https://code.claude.com/docs/en/microsoft-foundry)

## 配置代理和网关

**大多数组织可以直接使用云提供商而无需额外配置。** 但如果组织有特定的网络或管理需求，可能需要配置企业代理或 LLM 网关。这是两种不同的配置，可以组合使用：

* **企业代理**：通过 HTTP/HTTPS 代理路由流量。如果组织要求所有出站流量通过代理服务器进行安全监控、合规或网络策略执行，使用此方式。通过 `HTTPS_PROXY` 或 `HTTP_PROXY` 环境变量配置。详见[企业网络配置](https://code.claude.com/docs/en/network-config)。
* **LLM 网关**：位于 Claude Code 和云提供商之间的服务，处理认证和路由。如果需要跨团队的集中使用追踪、自定义速率限制或预算、或集中认证管理，使用此方式。通过 `ANTHROPIC_BASE_URL`、`ANTHROPIC_BEDROCK_BASE_URL`、`ANTHROPIC_AWS_BASE_URL` 或 `ANTHROPIC_VERTEX_BASE_URL` 环境变量配置。详见 [LLM 网关](https://code.claude.com/docs/en/llm-gateway)。

以下示例展示在 shell 或 shell 配置文件（`.bashrc`、`.zshrc`）中设置的环境变量。其他配置方法参见[设置](https://code.claude.com/docs/en/settings)。

### Amazon Bedrock

**企业代理配置：**

```bash
# Enable Bedrock
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION=us-east-1

# Configure corporate proxy
export HTTPS_PROXY='https://proxy.example.com:8080'
```

**LLM 网关配置：**

```bash
# Enable Bedrock
export CLAUDE_CODE_USE_BEDROCK=1

# Configure LLM gateway
export ANTHROPIC_BEDROCK_BASE_URL='https://your-llm-gateway.com/bedrock'
export CLAUDE_CODE_SKIP_BEDROCK_AUTH=1  # If gateway handles AWS auth
```

### Microsoft Foundry

**企业代理配置：**

```bash
# Enable Microsoft Foundry
export CLAUDE_CODE_USE_FOUNDRY=1
export ANTHROPIC_FOUNDRY_RESOURCE=your-resource
export ANTHROPIC_FOUNDRY_API_KEY=your-api-key  # Or omit for Entra ID auth

# Configure corporate proxy
export HTTPS_PROXY='https://proxy.example.com:8080'
```

**LLM 网关配置：**

```bash
# Enable Microsoft Foundry
export CLAUDE_CODE_USE_FOUNDRY=1

# Configure LLM gateway
export ANTHROPIC_FOUNDRY_BASE_URL='https://your-llm-gateway.com'
export ANTHROPIC_FOUNDRY_API_KEY=your-gateway-key  # Sent as x-api-key
```

### Google Vertex AI

**企业代理配置：**

```bash
# Enable Vertex
export CLAUDE_CODE_USE_VERTEX=1
export CLOUD_ML_REGION=us-east5
export ANTHROPIC_VERTEX_PROJECT_ID=your-project-id

# Configure corporate proxy
export HTTPS_PROXY='https://proxy.example.com:8080'
```

**LLM 网关配置：**

```bash
# Enable Vertex
export CLAUDE_CODE_USE_VERTEX=1

# Configure LLM gateway
export ANTHROPIC_VERTEX_BASE_URL='https://your-llm-gateway.com/vertex'
export CLAUDE_CODE_SKIP_VERTEX_AUTH=1  # If gateway handles GCP auth
export ANTHROPIC_VERTEX_PROJECT_ID=your-gcp-project-id
export CLOUD_ML_REGION=us-east5
```

> **提示：** 在 Claude Code 中使用 `/status` 验证代理和网关配置是否正确应用。

## 组织最佳实践

### 投入文档和记忆

**强烈建议投入文档建设，让 Claude Code 理解你的代码库。** 组织可以在多个级别部署 CLAUDE.md 文件：

* **组织级**：部署到系统目录如 `/Library/Application Support/ClaudeCode/CLAUDE.md`（macOS），用于公司范围标准
* **仓库级**：在仓库根目录创建 `CLAUDE.md` 文件，包含项目架构、构建命令和贡献指南。将其签入版本控制让所有用户受益

详见[记忆与 CLAUDE.md 文件](https://code.claude.com/docs/en/memory)。

### 简化部署

如果有自定义开发环境，创建 "一键安装" Claude Code 的方式是推动组织内采用增长的关键。

### 从引导式使用开始

鼓励新用户先用 Claude Code 做代码库问答，或处理较小的 bug 修复或功能请求。让 Claude Code 制定计划。检查 Claude 的建议，如果偏离方向则给出反馈。随着时间推移，用户更好地理解这种新范式后，他们将更有效地让 Claude Code 以更自主的方式运行。

### 为云提供商固定模型版本

如果通过 [Bedrock](https://code.claude.com/docs/en/amazon-bedrock)、[Vertex AI](https://code.claude.com/docs/en/google-vertex-ai)、[Foundry](https://code.claude.com/docs/en/microsoft-foundry) 或 [Claude Platform on AWS](https://code.claude.com/docs/en/claude-platform-on-aws) 部署，使用 `ANTHROPIC_DEFAULT_FABLE_MODEL`、`ANTHROPIC_DEFAULT_OPUS_MODEL`、`ANTHROPIC_DEFAULT_SONNET_MODEL` 和 `ANTHROPIC_DEFAULT_HAIKU_MODEL` 固定特定模型版本。不固定时，模型别名解析为 Claude Code 对该提供商的内置默认值，可能落后于最新版本且可能尚未在你的账户中启用。固定让你控制用户何时迁移到新模型。参见[模型配置](https://code.claude.com/docs/en/model-config#pin-models-for-third-party-deployments)。

### 配置安全策略

安全团队可以为 Claude Code 配置托管权限——定义允许和不允许做什么——本地配置无法覆盖这些设置。[了解更多](https://code.claude.com/docs/en/security)。

### 利用 MCP 实现集成

**MCP 是为 Claude Code 提供更多信息的好方式，** 例如连接工单管理系统或错误日志。建议一个中心团队配置 MCP 服务器并将 `.mcp.json` 配置签入代码库，让所有用户受益。[了解更多](https://code.claude.com/docs/en/mcp)。

在 Anthropic 内部，我们信任 Claude Code 为每个 Anthropic 代码库的开发提供动力。希望你和我们一样享受使用 Claude Code。

## 下一步

选定部署选项并为团队配置访问后：

1. **推广到团队**：分享安装说明，让团队成员[安装 Claude Code](https://code.claude.com/docs/en/setup) 并用凭据认证。
2. **设置共享配置**：在仓库中创建 [CLAUDE.md 文件](https://code.claude.com/docs/en/memory)，帮助 Claude Code 理解你的代码库和编码标准。
3. **配置权限**：审查[安全设置](https://code.claude.com/docs/en/security)，定义 Claude Code 在你的环境中可以和不可以做什么。
