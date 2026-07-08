---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】法律合规
description: Claude Code 的法律协议、合规认证和安全信息，包括许可证、商业协议、BAA 和可接受使用政策。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/legal-and-compliance.md
  - en-source/legal-and-compliance.md
---

# 法律和合规

> Claude Code 的法律协议、合规认证和安全信息。

## 法律协议

### 许可证

你对 Claude Code 的使用受以下条款约束：

- [商业条款](https://www.anthropic.com/legal/commercial-terms)——适用于 Team、Enterprise 和 Claude API 用户
- [消费者服务条款](https://www.anthropic.com/legal/consumer-terms)——适用于 Free、Pro 和 Max 用户

### 商业协议

**无论你是直接使用 Claude API（1P）还是通过 Amazon Bedrock 或 Google Cloud Agent Platform（3P）访问，现有商业协议将适用于 Claude Code 使用**（除非双方另有约定）。

## 合规

### 医疗保健合规（BAA）

**如果客户与我们签署了 Business Associate Agreement (BAA) 并希望使用 Claude Code，BAA 将自动扩展覆盖 Claude Code**——前提是客户已签署 BAA 且已激活[零数据保留 (ZDR)](https://code.claude.com/docs/en/zero-data-retention)。BAA 适用于通过 Claude Code 流经的 API 流量。ZDR 按组织启用，每个组织必须单独启用 ZDR 才能受 BAA 覆盖。

## 使用政策

### 可接受使用

Claude Code 使用受 [Anthropic Usage Policy](https://www.anthropic.com/legal/aup) 约束。Pro 和 Max 计划公布的使用限制假设 Claude Code 和 Agent SDK 的个人正常使用。

### 认证和凭证使用

Claude Code 通过 OAuth 令牌或 API 密钥与 Anthropic 服务器认证：

- **OAuth 认证**：专为 Claude Free、Pro、Max、Team 和 Enterprise 订阅计划的购买者设计，支持 Claude Code 和其他原生 Anthropic 应用的正常使用。更多信息参见 [Logging in to your Claude account](https://support.claude.com/en/articles/13189465-logging-in-to-your-claude-account)。
- **开发者**：构建与 Claude 能力交互的产品或服务的开发者（包括使用 [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) 的），应通过 [Claude Console](https://platform.claude.com/) 或支持的云提供商使用 API 密钥认证。Anthropic 不允许第三方开发者提供 Claude.ai 登录或代表其用户通过 Free、Pro 或 Max 计划凭证路由请求。

Anthropic 保留采取措施执行这些限制的权利，且可能在不事先通知的情况下执行。

关于你的使用场景允许的认证方式，请[联系销售](https://www.anthropic.com/contact-sales?utm_source=claude_code&utm_medium=docs&utm_content=legal_compliance_contact_sales)。

## 安全和信任

### 信任和安全

更多信息参见 [Anthropic Trust Center](https://trust.anthropic.com) 和 [Transparency Hub](https://www.anthropic.com/transparency)。

### 安全漏洞报告

Anthropic 通过 HackerOne 管理安全计划。[使用此表单报告漏洞](https://hackerone.com/4f1f16ba-10d3-4d09-9ecc-c721aad90f24/embedded_submissions/new)。

---

Copyright Anthropic PBC. All rights reserved. 使用受适用的 Anthropic 服务条款约束。
