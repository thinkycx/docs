---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】数据使用
description: Anthropic 的 Claude Code 数据使用政策，涵盖训练政策、数据保留、遥测服务和按提供商的默认行为。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/data-usage.md
  - en-source/data-usage.md
---

# 数据使用

> 了解 Anthropic 对 Claude 的数据使用政策。

## 数据政策

### 数据训练政策

**消费者用户（Free、Pro 和 Max 计划）**：我们让你选择是否允许数据用于改进未来的 Claude 模型。开启此设置后，我们将使用 Free、Pro 和 Max 账户的数据训练新模型（包括从这些账户使用 Claude Code 时）。

**商业用户（Team 和 Enterprise 计划、API、第三方平台和 Claude Gov）**：保持现有政策——Anthropic 不使用商业条款下发送到 Claude Code 的代码或提示词训练生成式模型，除非客户已选择向我们提供数据用于模型改进（例如 [Development Partner Program](https://support.claude.com/en/articles/11174108-about-the-development-partner-program)）。

### Development Partner Program

如果你明确选择加入向我们提供训练材料的方式（如 [Development Partner Program](https://support.claude.com/en/articles/11174108-about-the-development-partner-program)），我们可能使用这些材料训练模型。组织管理员可为其组织明确加入。此计划仅适用于 Anthropic 第一方 API，不适用于 Amazon Bedrock 或 Google Cloud Agent Platform 用户。

### 通过 `/feedback` 命令提交反馈

如果你选择通过 `/feedback` 命令发送反馈，我们可能使用你的反馈改进产品和服务。通过 `/feedback` 分享的对话记录保留 5 年。

### 会话质量调查

**「How is Claude doing this session?」提示中，你的响应（包括「Dismiss」）仅记录评分。** 我们不会在评分提示本身中收集或存储任何对话记录、输入、输出或其他会话数据。

评分后可能出现单独的跟进询问「Can Anthropic look at your session transcript to help us improve Claude Code?」：

| 选择 | 行为 |
| :--- | :--- |
| **Yes** | 上传对话记录、子代理记录和原始会话日志文件到 Anthropic。已知 API 密钥和令牌模式在上传前脱敏。源码和文件内容按原样上传。保留最多 6 个月。在 Amazon Bedrock、Google Cloud Agent Platform、Microsoft Foundry 和已登录的 Claude apps gateway 会话中，Yes 将相同内容写入 `~/.claude/feedback-bundles/` 本地存档，不上传 |
| **No** | 拒绝，不发送任何内容 |
| **Don't ask again** | 拒绝并停止此后续问题出现 |

除非你明确选择 **Yes**，否则不上传任何内容。启用了[零数据保留](https://code.claude.com/docs/en/zero-data-retention)、组织策略禁用产品反馈或设置了 `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` 的组织不会看到此跟进。

要禁用调查，设置 `CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY=1`。设置 `DISABLE_TELEMETRY`、`DO_NOT_TRACK` 或 `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` 也会禁用。

### 数据保留

**消费者用户（Free、Pro 和 Max 计划）**：

| 设置 | 保留期 |
| :--- | :--- |
| 允许数据用于模型改进 | 5 年 |
| 不允许数据用于模型改进 | 30 天 |

隐私设置随时可在 [claude.ai/settings/data-privacy-controls](https://claude.ai/settings/data-privacy-controls) 更改。

**商业用户（Team、Enterprise 和 API）**：

| 类型 | 保留期 |
| :--- | :--- |
| 标准 | 30 天 |
| [零数据保留](https://code.claude.com/docs/en/zero-data-retention) | 适用于合格的 Enterprise 账户 |
| 本地缓存 | Claude Code 客户端在 `~/.claude/projects/` 以明文存储会话记录，默认 30 天。通过 `cleanupPeriodDays` 调整 |

## 数据访问

关于[本地 Claude Code](#本地-claude-code-数据流) 和[远程 Claude Code](#云执行数据流) 记录的数据，参见下文。[Remote Control](https://code.claude.com/docs/en/remote-control) 会话遵循本地数据流（所有执行在你的机器上）。

## 本地 Claude Code 数据流

**Claude Code 在本地运行。** 与 LLM 交互时通过网络发送数据，包括所有用户提示词和模型输出，通过 TLS 1.2+ 加密传输。

静态加密取决于模型提供商：

| 提供商 | 静态加密 |
| :--- | :--- |
| Anthropic API | 基础设施级磁盘加密（AES-256）。启用[零数据保留](https://code.claude.com/docs/en/zero-data-retention)则无服务端持久化 |
| Amazon Bedrock | AES-256 + AWS 托管密钥。客户管理密钥可通过 AWS KMS |
| Google Cloud Agent Platform | Google 托管加密密钥。CMEK 可用 |
| Microsoft Foundry | 请求路由到 Anthropic 基础设施，AES-256 磁盘加密 |

### 云执行数据流

**使用 [Web 版 Claude Code](https://code.claude.com/docs/en/claude-code-on-the-web) 时，会话在 Anthropic 托管的虚拟机中运行：**

- **代码和数据存储**：仓库克隆到隔离 VM。数据受账户类型的保留和使用政策约束
- **凭证**：GitHub 认证通过安全代理处理，GitHub 凭证不进入沙箱
- **网络流量**：所有出站流量通过安全代理进行审计日志和滥用防护
- **会话数据**：提示词、代码变更和输出遵循与本地 Claude Code 相同的数据政策

## 遥测服务

**Claude Code 从用户机器连接到 Anthropic 记录操作指标**（如延迟、可靠性和使用模式）。此记录不包含任何代码或文件路径。要退出遥测，设置 `DISABLE_TELEMETRY`。

**Claude Code 连接到 Sentry 进行操作错误记录。** 要退出，设置 `DISABLE_ERROR_REPORTING`。

**运行 `/feedback` 命令时**，对话历史副本发送到 Anthropic。提交前你选择包含多少历史。使用第三方提供商时，`/feedback` 写入 `~/.claude/feedback-bundles/` 本地存档而非发送到 Anthropic。

## 按 API 提供商的默认行为

**使用 Amazon Bedrock、Google Cloud Agent Platform、Microsoft Foundry 或 Claude Platform on AWS 时，错误报告、遥测和 bug 报告默认禁用。** 会话质量调查和 WebFetch 域名安全检查是例外，无论提供商都运行。

设置 `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` 一次性退出所有非必要流量。

| 服务 | Claude API | Google Cloud Agent Platform | Amazon Bedrock | Microsoft Foundry | Claude Platform on AWS |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Anthropic (Metrics) | 默认开 | 默认关 | 默认关 | 默认关 | 默认关 |
| Sentry (Errors) | 默认开 | 默认关 | 默认关 | 默认关 | 默认关 |
| /feedback 报告 | 默认开 | 默认关 | 默认关 | 默认关 | 默认关 |
| 会话质量调查 | 默认开 | 默认开 | 默认开 | 默认开 | 默认开 |
| WebFetch 域名安全检查 | 默认开 | 默认开 | 默认开 | 默认开 | 默认开 |

### WebFetch 域名安全检查

获取 URL 前，WebFetch 工具将请求的主机名发送到 `api.anthropic.com` 检查安全黑名单。仅发送主机名，不发送完整 URL、路径或页面内容。结果按主机名缓存 5 分钟。

此检查无论使用哪个模型提供商都运行，不受 `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` 影响。如果网络阻止 `api.anthropic.com`，WebFetch 请求会失败，直到你允许该域名或设置 `skipWebFetchPreflight: true`。
