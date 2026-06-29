---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】Amazon Bedrock
description: 介绍如何通过 Amazon Bedrock 配置和使用 Claude Code，涵盖登录向导、手动配置、IAM 权限、模型版本固定、Mantle 端点以及常见问题排查。
category: translation
tags: [claude-code, bedrock, aws, translation]
refs:
  - https://code.claude.com/docs/en/amazon-bedrock.md
---

# 在 Amazon Bedrock 上使用 Claude Code

> 了解如何通过 Amazon Bedrock 配置 Claude Code，包括设置、IAM 配置和问题排查。

## 前提条件

**在配置 Claude Code 使用 Bedrock 之前，确保具备以下条件：**

- 已启用 Bedrock 访问的 AWS 账户
- 在 Bedrock 中可访问目标 Claude 模型（例如 Claude Sonnet 4.6）
- 已安装并配置 AWS CLI（可选——仅在没有其他凭证获取机制时需要）
- 适当的 IAM 权限

要使用自己的 Bedrock 凭证登录，参见下文的[使用 Bedrock 登录](#使用-bedrock-登录)。要在团队中部署 Claude Code，请使用[手动配置](#手动配置)步骤并在部署前[固定模型版本](#4-固定模型版本)。

## 使用 Bedrock 登录

**如果你已有 AWS 凭证并想通过 Bedrock 使用 Claude Code，登录向导会引导你完成配置。** AWS 侧的前提条件只需每个账户完成一次；向导负责处理 Claude Code 侧的配置。

配置步骤：

1. **在 AWS 账户中启用 Anthropic 模型** - 在 [Amazon Bedrock 控制台](https://console.aws.amazon.com/bedrock/)中打开模型目录，选择一个 Anthropic 模型并提交用例表单。提交后立即获得访问权限。关于 AWS Organizations 请参见[提交用例详情](#1-提交用例详情)，关于权限请参见 [IAM 配置](#iam-配置)
2. **启动 Claude Code 并选择 Bedrock** - 运行 `claude`。在登录提示处选择 **3rd-party platform**，然后选择 **Amazon Bedrock**
3. **按向导提示操作** - 选择 AWS 认证方式：从 `~/.aws` 目录检测到的 AWS profile、Bedrock API key、access key 和 secret，或环境中已有的凭证。向导会获取你的区域，验证账户可调用哪些 Claude 模型，并允许你固定版本。结果保存到[用户设置文件](https://code.claude.com/docs/en/settings)的 `env` 块中，无需手动导出环境变量

登录后，随时运行 `/setup-bedrock` 可重新打开向导，更改凭证、区域或模型固定设置。

## 手动配置

**通过环境变量配置 Bedrock（而非向导），适用于 CI 或脚本化的企业部署。**

### 1. 提交用例详情

首次使用 Anthropic 模型的用户需要提交用例详情，每个 AWS 账户只需提交一次。

1. 确保拥有下述 IAM 权限
2. 导航到 [Amazon Bedrock 控制台](https://console.aws.amazon.com/bedrock/)
3. 从 **Model catalog** 选择一个 Anthropic 模型
4. 填写用例表单。提交后立即获得访问权限

如果使用 AWS Organizations，可以从管理账户使用 [`PutUseCaseForModelAccess` API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_PutUseCaseForModelAccess.html) 提交一次表单。此调用需要 `bedrock:PutUseCaseForModelAccess` IAM 权限。审批会自动扩展到子账户。

### 2. 配置 AWS 凭证

**Claude Code 使用默认 AWS SDK 凭证链。** 通过以下方式之一配置凭证：

**方式 A：AWS CLI 配置**

```bash
aws configure
```

**方式 B：环境变量（access key）**

```bash
export AWS_ACCESS_KEY_ID=your-access-key-id
export AWS_SECRET_ACCESS_KEY=your-secret-access-key
export AWS_SESSION_TOKEN=your-session-token
```

**方式 C：环境变量（SSO profile）**

```bash
aws sso login --profile=<your-profile-name>

export AWS_PROFILE=your-profile-name
```

**方式 D：AWS Management Console 凭证**

```bash
aws login
```

更多信息参见 [aws login 文档](https://docs.aws.amazon.com/signin/latest/userguide/command-line-sign-in.html)。

**方式 E：Bedrock API keys**

```bash
export AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
```

Bedrock API keys 提供更简单的认证方式，无需完整 AWS 凭证。[了解更多关于 Bedrock API keys](https://aws.amazon.com/blogs/machine-learning/accelerate-ai-development-with-amazon-bedrock-api-keys/)。

#### 高级凭证配置

**Claude Code 支持 AWS SSO 和企业身份提供商的自动凭证刷新。** 将以下设置添加到 Claude Code 设置文件（文件位置参见[设置](https://code.claude.com/docs/en/settings)）。

这两个设置有不同的触发条件：

| 设置 | 触发时机 |
| --- | --- |
| `awsAuthRefresh` | 仅在 Claude Code 检测到 AWS 凭证过期时运行（本地时间戳判断或 Bedrock 返回凭证错误），然后用刷新后的凭证重试请求 |
| `awsCredentialExport` | 在会话启动和每次凭证重载时运行，即使默认凭证链中的凭证仍有效。适用于 Bedrock 账户需要与默认凭证链不同的跨账户凭证 |

##### 配置示例

```json
{
  "awsAuthRefresh": "aws sso login --profile myprofile",
  "env": {
    "AWS_PROFILE": "myprofile"
  }
}
```

##### 配置设置说明

**`awsAuthRefresh`**：用于修改 `.aws` 目录的命令（如更新凭证、SSO 缓存或配置文件）。命令输出会显示给用户，但不支持交互式输入。适合基于浏览器的 SSO 流程——CLI 显示 URL 或代码，你在浏览器中完成认证。

**`awsCredentialExport`**：仅在无法修改 `.aws` 且必须直接返回凭证时使用。此命令在凭证需要刷新时运行，不仅限于凭证过期。输出静默捕获，不显示给用户。命令必须输出以下格式的 JSON：

```json
{
  "Credentials": {
    "AccessKeyId": "value",
    "SecretAccessKey": "value",
    "SessionToken": "value",
    "Expiration": "2026-01-01T00:00:00Z"
  }
}
```

从 Claude Code v2.1.181 起，也接受 `aws configure export-credentials --format process` 的扁平输出格式，键在顶层而非嵌套在 `Credentials` 下。

`Expiration` 是可选的。从 Claude Code v2.1.176 起，当命令返回有效的 ISO 8601 `Expiration` 时，Claude Code 会缓存凭证到过期前五分钟。没有该字段或更早版本则缓存一小时。

### 3. 配置 Claude Code

**设置以下环境变量启用 Bedrock：**

```bash
# 启用 Bedrock 集成
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION=us-east-1  # 如果 AWS profile 已设置区域则可选

# 可选：覆盖 small/fast 模型的 AWS 区域（Bedrock 和 Mantle）
# 在 Bedrock 上，需要同时设置 ANTHROPIC_DEFAULT_HAIKU_MODEL 或已弃用的 ANTHROPIC_SMALL_FAST_MODEL 才生效
export ANTHROPIC_SMALL_FAST_MODEL_AWS_REGION=us-west-2

# 可选：覆盖 Bedrock 端点 URL（自定义端点或网关）
# export ANTHROPIC_BEDROCK_BASE_URL=https://bedrock-runtime.us-east-1.amazonaws.com
```

启用 Bedrock 时需注意：

- 从 v2.1.172 起，仅在需要覆盖 AWS profile 区域或 profile 没有区域时才需设置 `AWS_REGION`。Claude Code 按以下优先级解析区域：`AWS_REGION` > `AWS_DEFAULT_REGION` > 活动 AWS profile 中的 `region`（先读共享凭证文件再读共享配置文件，与 AWS SDK 一致）> `us-east-1`。活动 profile 为 `AWS_PROFILE`（若已设置），否则为 `default`。运行 `/status` 可查看解析后的区域。v2.1.171 及更早版本不读取 AWS 配置文件，需显式设置 `AWS_REGION`
- 使用 Bedrock 时 `/logout` 命令不可用，因为认证通过 AWS 凭证处理
- WebSearch 工具在 Bedrock 上不可用。参见 [WebSearch 工具行为](https://code.claude.com/docs/en/tools-reference#websearch-tool-behavior)
- 可以使用设置文件存放 `AWS_PROFILE` 等不希望泄露到其他进程的环境变量。参见[设置](https://code.claude.com/docs/en/settings)

### 4. 固定模型版本

> 部署到多用户时务必固定特定模型版本。不固定的话，`sonnet` 和 `opus` 等别名会解析为 Claude Code 内置的 Bedrock 默认值，该默认值可能落后于最新发布且未在你的账户中可用。Claude Code 在启动时如果默认版本不可用会[回退](#启动时模型检查)到前一版本，但固定版本让你能控制用户何时切换到新模型。

设置以下环境变量为特定的 Bedrock 模型 ID：

不设置 `ANTHROPIC_DEFAULT_OPUS_MODEL` 时，Bedrock 上的 `opus` 别名解析为 Opus 4.6。设置为 Opus 4.8 ID 以使用最新模型：

```bash
export ANTHROPIC_DEFAULT_OPUS_MODEL='us.anthropic.claude-opus-4-8'
export ANTHROPIC_DEFAULT_SONNET_MODEL='us.anthropic.claude-sonnet-4-6'
export ANTHROPIC_DEFAULT_HAIKU_MODEL='us.anthropic.claude-haiku-4-5-20251001-v1:0'
```

这些变量使用跨区域推理配置文件 ID（带 `us.` 前缀）。如果使用不同的区域前缀或应用推理配置文件，请相应调整。在 AWS GovCloud 区域使用 `us-gov.` 前缀。当前和历史模型 ID 参见[模型概览](https://platform.claude.com/docs/en/about-claude/models/overview)。环境变量完整列表参见[模型配置](https://code.claude.com/docs/en/model-config#pin-models-for-third-party-deployments)。

未设置固定变量时 Claude Code 使用的默认模型：

| 模型类型 | 默认值 |
| :--- | :--- |
| 主模型 | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` |
| Small/fast 模型 | 与主模型相同 |

后台任务（如会话标题生成）使用 small/fast 模型，通常是 Haiku 级别模型。在 Bedrock 上，Claude Code 将其默认为主模型，因为 Haiku 可能未在每个账户或区域启用。要使用 Haiku 处理后台任务，请将 `ANTHROPIC_DEFAULT_HAIKU_MODEL` 设为你账户中可用的模型 ID。

进一步自定义模型：

```bash
# 使用推理配置文件 ID
export ANTHROPIC_MODEL='us.anthropic.claude-sonnet-4-6'
export ANTHROPIC_DEFAULT_HAIKU_MODEL='us.anthropic.claude-haiku-4-5-20251001-v1:0'

# 使用应用推理配置文件 ARN
export ANTHROPIC_MODEL='arn:aws:bedrock:us-east-2:your-account-id:application-inference-profile/your-model-id'

# 可选：按需禁用 prompt 缓存
export DISABLE_PROMPT_CACHING=1

# 可选：请求 1 小时 prompt 缓存 TTL（默认 5 分钟）
export ENABLE_PROMPT_CACHING_1H=1
```

1 小时缓存 TTL 的计费费率高于默认 5 分钟。参见[缓存生命周期](https://code.claude.com/docs/en/prompt-caching#cache-lifetime)。

> Prompt 缓存并非在所有 Bedrock 区域可用。如果缓存 token 计数始终为零，请查阅 Bedrock 文档中的[支持的模型、区域和限制](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html#prompt-caching-models)。

#### 为每个模型版本映射推理配置文件

**`ANTHROPIC_DEFAULT_*_MODEL` 环境变量为每个模型家族配置一个推理配置文件。** 如果组织需要在 `/model` 选择器中暴露同一家族的多个版本，每个版本路由到各自的应用推理配置文件 ARN，请在[设置文件](https://code.claude.com/docs/en/settings#settings-files)中使用 `modelOverrides`。

以下示例将四个 Opus 版本映射到不同的 ARN，用户无需绕过组织的推理配置文件即可在它们之间切换：

```json
{
  "modelOverrides": {
    "claude-opus-4-7": "arn:aws:bedrock:us-east-2:123456789012:application-inference-profile/opus-47-prod",
    "claude-opus-4-6": "arn:aws:bedrock:us-east-2:123456789012:application-inference-profile/opus-46-prod",
    "claude-opus-4-5-20251101": "arn:aws:bedrock:us-east-2:123456789012:application-inference-profile/opus-45-prod",
    "claude-opus-4-1-20250805": "arn:aws:bedrock:us-east-2:123456789012:application-inference-profile/opus-41-prod"
  }
}
```

当用户在 `/model` 中选择其中一个版本时，Claude Code 使用映射的 ARN 调用 Bedrock。没有覆盖的版本回退到内置的 Bedrock 模型 ID 或启动时发现的匹配推理配置文件。关于覆盖如何与 `availableModels` 及其他模型设置交互，参见[按版本覆盖模型 ID](https://code.claude.com/docs/en/model-config#override-model-ids-per-version)。

## 启动时模型检查

**Claude Code 启动时会验证它要使用的模型在你的账户中是否可访问。** 此检查需要 Claude Code v2.1.94 或更高版本。

如果你固定的模型版本低于当前 Claude Code 默认值，且你的账户可以调用新版本，Claude Code 会提示你更新固定设置。接受则将新模型 ID 写入[用户设置文件](https://code.claude.com/docs/en/settings)并重启 Claude Code。拒绝将被记住，直到下一次默认版本变更。指向[应用推理配置文件 ARN](#为每个模型版本映射推理配置文件) 的固定会被跳过，因为它们由管理员管理。

如果你未固定模型且当前默认在账户中不可用，Claude Code 会在当前会话回退到前一版本并显示通知。回退不会持久化。在 Bedrock 账户中启用新模型或[固定版本](#4-固定模型版本)以使选择永久生效。

## IAM 配置

**创建包含 Claude Code 所需权限的 IAM 策略：**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowModelAndInferenceProfileAccess",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:ListInferenceProfiles",
        "bedrock:GetInferenceProfile"
      ],
      "Resource": [
        "arn:aws:bedrock:*:*:inference-profile/*",
        "arn:aws:bedrock:*:*:application-inference-profile/*",
        "arn:aws:bedrock:*:*:foundation-model/*"
      ]
    },
    {
      "Sid": "AllowMarketplaceSubscription",
      "Effect": "Allow",
      "Action": [
        "aws-marketplace:ViewSubscriptions",
        "aws-marketplace:Subscribe"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:CalledViaLast": "bedrock.amazonaws.com"
        }
      }
    }
  ]
}
```

如需更严格的权限，可将 Resource 限制为特定的推理配置文件 ARN。

`bedrock:GetInferenceProfile` 让 Claude Code 将[应用推理配置文件 ARN](#为每个模型版本映射推理配置文件) 解析为底层基础模型，用于为该模型选择正确的请求格式。

如果 token 缺少此权限，Claude Code 会自动重试一次（使用替代格式）进行恢复，请求仍然成功但每个新模型多一次往返。授予此权限可避免重试。这最常出现在 `AWS_BEARER_TOKEN_BEDROCK` 部署中，token 的策略通常比完整 IAM 角色更窄。

详情参见 [Bedrock IAM 文档](https://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html)。

> 建议为 Claude Code 创建专用 AWS 账户以简化成本追踪和访问控制。

## 1M token 上下文窗口

**Claude Opus 4.6 及更高版本以及 Sonnet 4.6 在 Amazon Bedrock 上支持 [1M token 上下文窗口](https://platform.claude.com/docs/en/build-with-claude/context-windows#1m-token-context-window)。** 当你选择 1M 模型变体时，Claude Code 自动启用扩展上下文窗口。

[设置向导](#使用-bedrock-登录)在固定模型时提供 1M 上下文选项。要为手动固定的模型启用，在模型 ID 后追加 `[1m]`。详情参见[为第三方部署固定模型](https://code.claude.com/docs/en/model-config#pin-models-for-third-party-deployments)。

## 服务层级

**[Amazon Bedrock 服务层级](https://docs.aws.amazon.com/bedrock/latest/userguide/service-tiers-inference.html)让你在成本和延迟之间权衡。** 将 `ANTHROPIC_BEDROCK_SERVICE_TIER` 设为 `default`、`flex` 或 `priority`：

```bash
export ANTHROPIC_BEDROCK_SERVICE_TIER=priority
```

Claude Code 在每个请求中以 `X-Amzn-Bedrock-Service-Tier` 头发送此值。层级可用性因模型和区域而异。预留容量使用[预配置吞吐量](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html) ARN 作为模型 ID，而非此设置。

## AWS Guardrails

**[Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) 让你为 Claude Code 实现内容过滤。** 在 [Amazon Bedrock 控制台](https://console.aws.amazon.com/bedrock/)创建 Guardrail，发布版本，然后将 Guardrail 头添加到[设置文件](https://code.claude.com/docs/en/settings)。如果使用跨区域推理配置文件，需在 Guardrail 上启用 Cross-Region inference。

配置示例：

```json
{
  "env": {
    "ANTHROPIC_CUSTOM_HEADERS": "X-Amzn-Bedrock-GuardrailIdentifier: your-guardrail-id\nX-Amzn-Bedrock-GuardrailVersion: 1"
  }
}
```

## 使用 Mantle 端点

**Mantle 是一个 Amazon Bedrock 端点，通过原生 Anthropic API 格式（而非 Bedrock Invoke API）提供 Claude 模型。** 使用与本页前面描述的相同 AWS 凭证、IAM 权限和 `awsAuthRefresh` 配置。

> Mantle 需要 Claude Code v2.1.94 或更高版本。运行 `claude --version` 检查。

### 启用 Mantle

在已配置 AWS 凭证的情况下，设置 `CLAUDE_CODE_USE_MANTLE` 将请求路由到 Mantle 端点：

```bash
export CLAUDE_CODE_USE_MANTLE=1
export AWS_REGION=us-east-1
```

Claude Code 从 AWS 区域构造端点 URL。从 v2.1.172 起，区域解析优先级与[上文 Bedrock](#3-配置-claude-code) 相同；更早版本仅使用 `AWS_REGION`。要覆盖自定义端点或网关的 URL，设置 `ANTHROPIC_BEDROCK_MANTLE_BASE_URL`。

在 Claude Code 中运行 `/status` 确认。提供商行在 Mantle 活动时显示 `Amazon Bedrock (Mantle)`。

### 选择 Mantle 模型

Mantle 使用带 `anthropic.` 前缀且不含版本后缀的模型 ID，例如 `anthropic.claude-haiku-4-5`。你账户可用的模型取决于组织被授予的权限；更多模型 ID 见 AWS 提供的入门材料。联系 AWS 账户团队申请白名单模型访问。

通过 `--model` 标志或 Claude Code 内的 `/model` 设置模型：

```bash
claude --model anthropic.claude-haiku-4-5
```

### 同时运行 Mantle 和 Invoke API

**Mantle 可用的模型可能不包含你目前使用的所有模型。** 同时设置 `CLAUDE_CODE_USE_BEDROCK` 和 `CLAUDE_CODE_USE_MANTLE` 让 Claude Code 在同一会话中调用两个端点。匹配 Mantle 格式的模型 ID 路由到 Mantle，其他所有模型 ID 走 Bedrock Invoke API。

```bash
export CLAUDE_CODE_USE_BEDROCK=1
export CLAUDE_CODE_USE_MANTLE=1
```

要在 `/model` 选择器中显示 Mantle 模型，在[设置文件](https://code.claude.com/docs/en/settings)的 `availableModels` 中列出其 ID。此设置还会将选择器限制为列出的条目。列出 `anthropic.claude-haiku-4-5` 会从选择器中移除裸 `haiku` 别名，因此也要列出你想保留可选的版本前缀或完整 ID。Mantle ID 和 `haiku` 别名解析为同一模型家族，合并只保留更具体的条目。参见[合并行为](https://code.claude.com/docs/en/model-config#merge-behavior)：

```json
{
  "availableModels": ["opus", "sonnet", "claude-haiku-4-5", "anthropic.claude-haiku-4-5"]
}
```

带 `anthropic.` 前缀的条目作为自定义选择器选项添加并路由到 Mantle。用你账户被授予的模型 ID 替换 `anthropic.claude-haiku-4-5`。关于 `availableModels` 如何与其他模型设置交互，参见[限制模型选择](https://code.claude.com/docs/en/model-config#restrict-model-selection)。

当两个提供商都活动时，`/status` 显示 `Amazon Bedrock + Amazon Bedrock (Mantle)`。

### 通过网关路由 Mantle

如果组织通过集中式 [LLM 网关](https://code.claude.com/docs/en/llm-gateway)路由模型流量并在服务端注入 AWS 凭证，禁用客户端认证让 Claude Code 发送不带 SigV4 签名或 `x-api-key` 头的请求：

```bash
export CLAUDE_CODE_USE_MANTLE=1
export CLAUDE_CODE_SKIP_MANTLE_AUTH=1
export ANTHROPIC_BEDROCK_MANTLE_BASE_URL=https://your-gateway.example.com
```

### Mantle 环境变量

以下变量专用于 Mantle 端点。完整列表参见[环境变量](https://code.claude.com/docs/en/env-vars)。

| 变量 | 用途 |
| :--- | :--- |
| `CLAUDE_CODE_USE_MANTLE` | 启用 Mantle 端点。设为 `1` 或 `true` |
| `ANTHROPIC_BEDROCK_MANTLE_BASE_URL` | 覆盖默认 Mantle 端点 URL |
| `CLAUDE_CODE_SKIP_MANTLE_AUTH` | 跳过客户端认证（代理场景） |
| `ANTHROPIC_SMALL_FAST_MODEL_AWS_REGION` | 覆盖 Haiku 级模型的 AWS 区域（与 Bedrock 共享） |

## 问题排查

### SSO 和企业代理的认证循环

**如果使用 AWS SSO 时浏览器标签页反复弹出，从[设置文件](https://code.claude.com/docs/en/settings)中移除 `awsAuthRefresh` 设置。** 当企业 VPN 或 TLS 检查代理中断 SSO 浏览器流程时会出现此问题。Claude Code 将中断的连接视为认证失败，重新运行 `awsAuthRefresh`，无限循环。

如果网络环境干扰自动基于浏览器的 SSO 流程，在启动 Claude Code 之前手动运行 `aws sso login`，而不是依赖 `awsAuthRefresh`。

### 区域问题

如果遇到区域问题：

- 检查模型可用性：`aws bedrock list-inference-profiles --region your-region`
- 切换到支持的区域：`export AWS_REGION=us-east-1`
- 考虑使用推理配置文件进行跨区域访问

如果收到 "on-demand throughput isn't supported" 错误：

- 将模型指定为[推理配置文件](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html) ID

Claude Code 使用 Bedrock [Invoke API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InvokeModelWithResponseStream.html)，不支持 Converse API。

### Mantle 端点错误

如果设置 `CLAUDE_CODE_USE_MANTLE` 后 `/status` 未显示 `Amazon Bedrock (Mantle)`，说明变量未到达进程。确认在启动 `claude` 的 shell 中已导出该变量，或在[设置文件](https://code.claude.com/docs/en/settings)的 `env` 块中设置。

凭证有效时从 Mantle 端点收到 `403`，意味着你的 AWS 账户未被授予访问所请求模型的权限。联系 AWS 账户团队申请访问。

包含模型 ID 的 `400` 错误意味着该模型不在 Mantle 上提供。Mantle 有自己独立于标准 Bedrock 目录的模型列表，推理配置文件 ID（如 `us.anthropic.claude-sonnet-4-6`）不会起作用。使用 Mantle 格式的 ID，或启用[两个端点](#同时运行-mantle-和-invoke-api)让 Claude Code 将每个请求路由到模型可用的端点。

## 相关资源

- [Bedrock 文档](https://docs.aws.amazon.com/bedrock/)
- [Bedrock 定价](https://aws.amazon.com/bedrock/pricing/)
- [Bedrock 推理配置文件](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html)
- [Bedrock token 消耗与配额](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-token-burndown.html)
- [Claude Code on Amazon Bedrock: 快速设置指南](https://community.aws/content/2tXkZKrZzlrlu0KfH8gST5Dkppq/claude-code-on-amazon-bedrock-quick-setup-guide)
- [Claude Code 监控实现（Bedrock）](https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock/blob/main/assets/docs/MONITORING.md)
