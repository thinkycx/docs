---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】Google Vertex AI
description: 介绍如何通过 Google Vertex AI 配置和使用 Claude Code，涵盖登录向导、手动配置、区域设置、IAM 权限、模型版本固定以及常见问题排查。
category: translation
tags: [claude-code, vertex-ai, gcp, translation]
refs:
  - https://code.claude.com/docs/en/google-vertex-ai.md
---

# 在 Google Vertex AI 上使用 Claude Code

> 了解如何通过 Google Vertex AI 配置 Claude Code，包括设置、IAM 配置和问题排查。

## 前提条件

**在配置 Claude Code 使用 Vertex AI 之前，确保具备以下条件：**

- 已启用计费的 Google Cloud Platform (GCP) 账户
- 已启用 Vertex AI API 的 GCP 项目
- 可访问目标 Claude 模型（例如 Claude Sonnet 4.6）
- 已安装并配置 Google Cloud SDK (`gcloud`)
- 在目标 GCP 区域已分配配额

要使用自己的 Vertex AI 凭证登录，参见下文的[使用 Vertex AI 登录](#使用-vertex-ai-登录)。要在团队中部署 Claude Code，请使用[手动配置](#手动配置)步骤并在部署前[固定模型版本](#5-固定模型版本)。

## 使用 Vertex AI 登录

**如果你已有 Google Cloud 凭证并想通过 Vertex AI 使用 Claude Code，登录向导会引导你完成配置。** GCP 侧的前提条件只需每个项目完成一次；向导负责处理 Claude Code 侧的配置。

> Vertex AI 设置向导需要 Claude Code v2.1.98 或更高版本。运行 `claude --version` 检查。

配置步骤：

1. **在 GCP 项目中启用 Claude 模型** - 为项目[启用 Vertex AI API](#1-启用-vertex-ai-api)，然后在 [Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/model-garden) 中申请访问所需的 Claude 模型。权限信息参见 [IAM 配置](#iam-配置)
2. **启动 Claude Code 并选择 Vertex AI** - 运行 `claude`。在登录提示处选择 **3rd-party platform**，然后选择 **Google Vertex AI**
3. **按向导提示操作** - 选择 Google Cloud 认证方式：来自 `gcloud` 的 Application Default Credentials、服务账户密钥文件，或环境中已有的凭证。向导检测你的项目和区域，验证项目可调用哪些 Claude 模型，并允许你固定版本。结果保存到[用户设置文件](https://code.claude.com/docs/en/settings)的 `env` 块中，无需手动导出环境变量

登录后，随时运行 `/setup-vertex` 可重新打开向导，更改凭证、项目、区域或模型固定设置。

## 区域配置

**Claude Code 支持 Vertex AI 的 [global](https://cloud.google.com/blog/products/ai-machine-learning/global-endpoint-for-claude-models-generally-available-on-vertex-ai)、多区域和区域端点。** 将 `CLOUD_ML_REGION` 设置为 `global`、多区域位置（如 `eu` 或 `us`）或特定区域（如 `us-east5`）。Claude Code 会为每种形式选择正确的 Vertex AI 主机名，包括多区域位置的 `aiplatform.eu.rep.googleapis.com` 和 `aiplatform.us.rep.googleapis.com` 主机。

> Vertex AI 可能不在每种端点类型上都支持 Claude Code 默认模型。模型可用性在[特定区域](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations#genai-partner-models)、多区域位置和 [global 端点](https://cloud.google.com/vertex-ai/generative-ai/docs/partner-models/use-partner-models#supported_models)之间有差异。你可能需要切换到支持的位置或指定支持的模型。

## 手动配置

**通过环境变量配置 Vertex AI（而非向导），适用于 CI 或脚本化的企业部署。**

### 1. 启用 Vertex AI API

在 GCP 项目中启用 Vertex AI API：

```bash
# 设置项目 ID
gcloud config set project YOUR-PROJECT-ID

# 启用 Vertex AI API
gcloud services enable aiplatform.googleapis.com
```

### 2. 申请模型访问

在 Vertex AI 中申请访问 Claude 模型：

1. 导航到 [Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)
2. 搜索 "Claude" 模型
3. 申请访问所需的 Claude 模型（例如 Claude Sonnet 4.6）
4. 等待审批（可能需要 24-48 小时）

### 3. 配置 GCP 凭证

**Claude Code 使用标准 Google Cloud 认证。** 更多信息参见 [Google Cloud 认证文档](https://cloud.google.com/docs/authentication)。

Claude Code v2.1.121 或更高版本通过相同的 Application Default Credentials 链支持[基于 X.509 证书的 Workload Identity Federation](https://cloud.google.com/iam/docs/workload-identity-federation-with-x509-certificates)。将 `GOOGLE_APPLICATION_CREDENTIALS` 设置为凭证配置文件的路径。

> Claude Code 使用 `ANTHROPIC_VERTEX_PROJECT_ID` 作为 Vertex AI 请求的项目 ID。`GCLOUD_PROJECT` 和 `GOOGLE_CLOUD_PROJECT` 环境变量以及 `GOOGLE_APPLICATION_CREDENTIALS` 引用的凭证文件优先级高于它。如果都未设置，则从 `gcloud` 配置或关联的服务账户解析项目 ID。

#### 高级凭证配置

**Claude Code 通过 `gcpAuthRefresh` 设置支持 GCP 自动凭证刷新。** 当 Claude Code 检测到 GCP 凭证过期或无法加载时，会运行配置的命令获取新凭证后重试请求。

```json
{
  "gcpAuthRefresh": "gcloud auth application-default login",
  "env": {
    "ANTHROPIC_VERTEX_PROJECT_ID": "your-project-id"
  }
}
```

命令输出会显示给用户，但不支持交互式输入。适合基于浏览器的认证流程——CLI 显示 URL，你在浏览器中完成认证。刷新命令在认证未完成时三分钟后超时。如果在项目设置（如 `.claude/settings.json`）中设置 `gcpAuthRefresh`，命令仅在你接受工作区信任提示后运行。

### 4. 配置 Claude Code

**设置以下环境变量：**

```bash
# 启用 Vertex AI 集成
export CLAUDE_CODE_USE_VERTEX=1
export CLOUD_ML_REGION=global
export ANTHROPIC_VERTEX_PROJECT_ID=YOUR-PROJECT-ID

# 可选：覆盖 Vertex 端点 URL（自定义端点或网关）
# export ANTHROPIC_VERTEX_BASE_URL=https://aiplatform.googleapis.com

# 可选：按需禁用 prompt 缓存
export DISABLE_PROMPT_CACHING=1

# 可选：请求 1 小时 prompt 缓存 TTL（默认 5 分钟）
export ENABLE_PROMPT_CACHING_1H=1

# 当 CLOUD_ML_REGION=global 时，为不支持 global 端点的模型覆盖区域
export VERTEX_REGION_CLAUDE_HAIKU_4_5=us-east5
export VERTEX_REGION_CLAUDE_4_6_SONNET=europe-west1
```

大多数模型版本都有对应的 `VERTEX_REGION_CLAUDE_*` 变量。完整列表参见[环境变量参考](https://code.claude.com/docs/en/env-vars)。查看 [Vertex Model Garden](https://console.cloud.google.com/vertex-ai/model-garden) 确定哪些模型支持 global 端点、哪些仅支持区域端点。

[Prompt 缓存](https://code.claude.com/docs/en/prompt-caching)默认自动启用。设置 `DISABLE_PROMPT_CACHING=1` 可禁用。设置 `ENABLE_PROMPT_CACHING_1H=1` 请求 1 小时缓存 TTL（默认 5 分钟）；1 小时 TTL 的缓存写入费率更高。如需更高速率限制，联系 Google Cloud 支持。使用 Vertex AI 时 `/logout` 命令不可用，因为认证通过 Google Cloud 凭证处理。

Claude Code 在 Vertex AI 上默认禁用 [MCP 工具搜索](https://code.claude.com/docs/en/mcp#scale-with-mcp-tool-search)，MCP 工具定义会预先加载。Vertex AI 对 Claude Sonnet 4.5 及更高版本和 Claude Opus 4.5 及更高版本支持工具搜索。设置 `ENABLE_TOOL_SEARCH=true` 可在这些模型上启用。更早的 Vertex AI 模型不接受所需的 beta header，启用工具搜索时请求会失败。

### 5. 固定模型版本

> 部署到多用户时务必固定特定模型版本。不固定的话，`sonnet` 和 `opus` 等别名会解析为 Claude Code 内置的 Vertex AI 默认值，该默认值可能落后于最新发布且未在你的项目中启用。Claude Code 在启动时如果默认版本不可用会[回退](#启动时模型检查)到前一版本，但固定版本让你能控制用户何时切换到新模型。

设置以下环境变量为特定的 Vertex AI 模型 ID：

不设置 `ANTHROPIC_DEFAULT_OPUS_MODEL` 时，Vertex 上的 `opus` 别名解析为 Opus 4.6。设置为 Opus 4.8 ID 以使用最新模型：

```bash
export ANTHROPIC_DEFAULT_OPUS_MODEL='claude-opus-4-8'
export ANTHROPIC_DEFAULT_SONNET_MODEL='claude-sonnet-4-6'
export ANTHROPIC_DEFAULT_HAIKU_MODEL='claude-haiku-4-5@20251001'
```

当前和历史模型 ID 参见[模型概览](https://platform.claude.com/docs/en/about-claude/models/overview)。环境变量完整列表参见[模型配置](https://code.claude.com/docs/en/model-config#pin-models-for-third-party-deployments)。

未设置固定变量时 Claude Code 使用的默认模型：

| 模型类型 | 默认值 |
| :--- | :--- |
| 主模型 | `claude-sonnet-4-5@20250929` |
| Small/fast 模型 | 与主模型相同 |

后台任务（如会话标题生成）使用 small/fast 模型，通常是 Haiku 级别模型。在 Vertex AI 上，Claude Code 将其默认为主模型，因为 Haiku 可能未在每个项目或区域启用。要使用 Haiku 处理后台任务，请将 `ANTHROPIC_DEFAULT_HAIKU_MODEL` 设为你项目中可用的模型 ID。

进一步自定义模型：

```bash
export ANTHROPIC_MODEL='claude-opus-4-8'
export ANTHROPIC_DEFAULT_HAIKU_MODEL='claude-haiku-4-5@20251001'
```

## 启动时模型检查

**Claude Code 启动时会验证它要使用的模型在你的项目中是否可访问。** 此检查需要 Claude Code v2.1.98 或更高版本。

如果你固定的模型版本低于当前 Claude Code 默认值，且你的项目可以调用新版本，Claude Code 会提示你更新固定设置。接受则将新模型 ID 写入[用户设置文件](https://code.claude.com/docs/en/settings)并重启 Claude Code。拒绝将被记住，直到下一次默认版本变更。

如果你未固定模型且当前默认在项目中不可用，Claude Code 会在当前会话回退到前一版本并显示通知。回退不会持久化。在 [Model Garden](https://console.cloud.google.com/vertex-ai/model-garden) 中启用新模型或[固定版本](#5-固定模型版本)以使选择永久生效。

## IAM 配置

**分配所需的 IAM 权限：**

`roles/aiplatform.user` 角色包含所需权限：

- `aiplatform.endpoints.predict` - 模型调用和 token 计数所需

如需更严格的权限，创建仅包含上述权限的自定义角色。

详情参见 [Vertex IAM 文档](https://cloud.google.com/vertex-ai/docs/general/access-control)。

> 建议为 Claude Code 创建专用 GCP 项目以简化成本追踪和访问控制。

## 1M token 上下文窗口

**Claude Opus 4.6 及更高版本以及 Sonnet 4.6 在 Vertex AI 上支持 [1M token 上下文窗口](https://platform.claude.com/docs/en/build-with-claude/context-windows#1m-token-context-window)。** 当你选择 1M 模型变体时，Claude Code 自动启用扩展上下文窗口。

[设置向导](#使用-vertex-ai-登录)在固定模型时提供 1M 上下文选项。要为手动固定的模型启用，在模型 ID 后追加 `[1m]`。详情参见[为第三方部署固定模型](https://code.claude.com/docs/en/model-config#pin-models-for-third-party-deployments)。

## 问题排查

**如果遇到 "Could not load the default credentials" 错误：**

- 运行 `gcloud auth application-default login` 设置 Application Default Credentials
- 将 `GOOGLE_APPLICATION_CREDENTIALS` 设置为服务账户密钥文件路径
- 参见[配置 GCP 凭证](#3-配置-gcp-凭证)了解所有选项

**如果遇到配额问题：**

- 通过 [Cloud Console](https://cloud.google.com/docs/quotas/view-manage) 查看当前配额或申请配额增加

**如果遇到 "model not found" 404 错误：**

- 确认模型在 [Model Garden](https://console.cloud.google.com/vertex-ai/model-garden) 中已启用
- 验证模型在你指定的位置可用。某些模型仅在 `global` 或多区域位置（如 `eu` 和 `us`）提供，不在特定区域
- 如果使用 `CLOUD_ML_REGION=global`，检查模型是否在 [Model Garden](https://console.cloud.google.com/vertex-ai/model-garden) 的 "Supported features" 下支持 global 端点。对于不支持 global 端点的模型，可以：
  - 通过 `ANTHROPIC_MODEL` 或 `ANTHROPIC_DEFAULT_HAIKU_MODEL` 指定支持的模型
  - 使用 `VERTEX_REGION_<MODEL_NAME>` 环境变量设置区域或多区域位置

**如果遇到 429 错误：**

- 对于区域端点，确保主模型和 small/fast 模型在你选择的区域受支持
- 考虑切换到 `CLOUD_ML_REGION=global` 以获得更好的可用性

## 相关资源

- [Vertex AI 文档](https://cloud.google.com/vertex-ai/docs)
- [Vertex AI 定价](https://cloud.google.com/vertex-ai/pricing)
- [Vertex AI 配额和限制](https://cloud.google.com/vertex-ai/docs/quotas)
