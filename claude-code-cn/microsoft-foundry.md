---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Microsoft Foundry
description: 通过 Microsoft Foundry 配置 Claude Code 的完整指南，包括 Azure 资源创建、认证方式、模型版本固定和故障排查。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/microsoft-foundry.md
  - en-source/microsoft-foundry.md
---

# Claude Code on Microsoft Foundry

> 通过 Microsoft Foundry 配置 Claude Code，包括设置、配置和故障排查。

## 前提条件

配置 Claude Code 使用 Microsoft Foundry 之前，确保你拥有：

- 具有 Microsoft Foundry 访问权限的 Azure 订阅
- 创建 Microsoft Foundry 资源和部署的 RBAC 权限
- Azure CLI 已安装并配置（可选——仅在没有其他凭证获取机制时需要）

> 如果你要向多个用户部署 Claude Code，请在推广前先[固定模型版本](#4-固定模型版本)。

## 设置

### 1. 创建 Microsoft Foundry 资源

**在 Azure 中创建 Claude 资源：**

1. 进入 [Microsoft Foundry 门户](https://ai.azure.com/)
2. 创建新资源，记录资源名称
3. 为 Claude 模型创建部署：
   - Claude Opus
   - Claude Sonnet
   - Claude Haiku

### 2. 配置 Azure 凭证

**Claude Code 支持两种 Microsoft Foundry 认证方式：**

**方式 A：API Key 认证**

1. 在 Microsoft Foundry 门户进入你的资源
2. 前往 **Endpoints and keys** 部分
3. 复制 **API Key**
4. 设置环境变量：

```bash
export ANTHROPIC_FOUNDRY_API_KEY=your-azure-api-key
```

**方式 B：Microsoft Entra ID 认证**

未设置 `ANTHROPIC_FOUNDRY_API_KEY` 时，Claude Code 自动使用 Azure SDK [默认凭证链](https://learn.microsoft.com/en-us/azure/developer/javascript/sdk/authentication/credential-chains#defaultazurecredential-overview)，支持多种本地和远程工作负载认证方式。

本地环境通常使用 Azure CLI：

```bash
az login
```

> 使用 Microsoft Foundry 时，`/logout` 命令不可用，因为认证通过 Azure 凭证处理。

### 3. 配置 Claude Code

**设置以下环境变量启用 Microsoft Foundry：**

```bash
# 启用 Microsoft Foundry 集成
export CLAUDE_CODE_USE_FOUNDRY=1

# Azure 资源名称（替换 {resource}）
export ANTHROPIC_FOUNDRY_RESOURCE={resource}
# 或提供完整 Base URL：
# export ANTHROPIC_FOUNDRY_BASE_URL=https://{resource}.services.ai.azure.com/anthropic
```

### 4. 固定模型版本

> **务必为每个部署固定具体模型版本。** 不固定时，`sonnet` 和 `opus` 等别名解析为 Claude Code 对 Microsoft Foundry 的内置默认值，可能滞后于最新版本且你的账户中可能尚未可用。Microsoft Foundry 没有启动时的模型检查，因此默认值不可用时请求直接失败。创建 Azure 部署时选择具体模型版本而非「自动更新到最新」。

设置模型变量匹配步骤 1 中创建的部署名称：

```bash
export ANTHROPIC_DEFAULT_OPUS_MODEL='claude-opus-4-8'
export ANTHROPIC_DEFAULT_SONNET_MODEL='claude-sonnet-5'
export ANTHROPIC_DEFAULT_HAIKU_MODEL='claude-haiku-4-5'
```

未设置 `ANTHROPIC_DEFAULT_OPUS_MODEL` 时，Microsoft Foundry 上的 `opus` 别名解析为 Opus 4.6。设为 Opus 4.8 ID 以使用最新模型。

后台任务（如会话标题生成）使用小/快模型，通常是 Haiku 级别。Microsoft Foundry 上 Claude Code 默认将其设为主模型，因为不是每个账户都有 Haiku 部署。要使用 Haiku 做后台任务，设置 `ANTHROPIC_DEFAULT_HAIKU_MODEL`。

当前和旧版模型 ID 参见 [Models overview](https://platform.claude.com/docs/en/about-claude/models/overview)。环境变量完整列表参见[模型配置](https://code.claude.com/docs/en/model-config#pin-models-for-third-party-deployments)。

[Prompt 缓存](https://code.claude.com/docs/en/prompt-caching)自动启用。要请求 1 小时缓存 TTL（而非 5 分钟默认值），设置以下变量（1 小时缓存写入按更高费率计费）：

```bash
export ENABLE_PROMPT_CACHING_1H=1
```

### 5. 运行 Claude Code

环境变量设置完成后，从项目目录启动：

```bash
claude
```

Claude Code 读取 `CLAUDE_CODE_USE_FOUNDRY` 和其他 Microsoft Foundry 变量，在首个提示词时连接到 Azure 资源。与 Amazon Bedrock 和 Google Cloud Agent Platform 不同，Microsoft Foundry 没有交互式设置向导，步骤 3 和 4 中的环境变量是唯一配置路径。

## Azure RBAC 配置

`Azure AI User` 和 `Cognitive Services User` 默认角色包含调用 Claude 模型所需的全部权限。

如需更严格的权限，创建自定义角色：

```json
{
  "permissions": [
    {
      "dataActions": [
        "Microsoft.CognitiveServices/accounts/providers/*"
      ]
    }
  ]
}
```

详见 [Microsoft Foundry RBAC 文档](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/rbac-azure-ai-foundry)。

## 故障排查

如果收到错误「Failed to get token from azureADTokenProvider: ChainedTokenCredential authentication failed」：

- 在环境中配置 Entra ID，或设置 `ANTHROPIC_FOUNDRY_API_KEY`

## 附加资源

- [Microsoft Foundry 文档](https://learn.microsoft.com/en-us/azure/ai-foundry/what-is-azure-ai-foundry)
- [Microsoft Foundry 模型](https://ai.azure.com/explore/models)
- [Microsoft Foundry 定价](https://azure.microsoft.com/en-us/pricing/details/ai-foundry/)
