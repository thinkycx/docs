---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】LLM Gateway
description: 介绍如何将 Claude Code 路由到组织已运行的第三方 LLM 网关，包括网关的连接方式、组织级推广流程和网关协议。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/llm-gateway.md
  - en-source/llm-gateway.md
---

# 第三方 LLM 网关

> 将 Claude Code 路由到组织已有的 LLM 网关。涵盖连接方式、组织推广流程以及 Claude Code 向网关发送的请求内容。

**本节介绍如何使用组织已运行的第三方网关产品，而非 [Claude apps gateway](https://code.claude.com/docs/en/claude-apps-gateway)。** 关于网关的定位、工作原理以及如何在 Claude apps gateway 和第三方产品之间选择，请参阅[网关概览](https://code.claude.com/docs/en/gateways)。

> 快速导航：
> - 开发者连接现有网关：[连接 Claude Code 到网关](https://code.claude.com/docs/en/llm-gateway-connect)
> - 管理员为组织推广网关：[部署和分发网关](https://code.claude.com/docs/en/llm-gateway-rollout)
> - 配置网关产品：[网关协议参考](https://code.claude.com/docs/en/llm-gateway-protocol)

**任何暴露[支持的 API 格式](https://code.claude.com/docs/en/llm-gateway-protocol#api-formats)的网关都可以使用。** Anthropic 不为第三方网关产品提供背书、维护或审计，也不支持通过任何网关将 Claude Code 路由到非 Claude 模型。请按照网关产品自身的文档完成部署，然后参考下文的[推广步骤](#推广网关)完成 Claude Code 侧配置。

## 网关的价值

**网关为组织提供了统一的管理入口：**

| 能力 | 说明 |
| :--- | :--- |
| 凭证管理 | 提供商密钥保留在服务端，开发者只持有网关凭证 |
| 用量追踪 | 按开发者或团队归属用量，无论哪个提供商处理请求 |
| 成本控制 | 在一处集中管理预算和速率限制 |
| 审计日志 | 记录每个模型请求，满足合规需求 |
| 提供商切换 | 在网关配置中更换提供商，无需修改开发者机器 |

除「提供商切换」外，其余能力无论上游是 Anthropic API 还是[云服务商](https://code.claude.com/docs/en/third-party-integrations)都适用。提供商切换在不重新配置开发者机器的前提下生效，还需要网关暴露一个统一的 [Anthropic 格式端点](https://code.claude.com/docs/en/llm-gateway-protocol#api-formats)——如果网关暴露的是提供商自有格式，则客户端配置仍然绑定到该提供商。

**权衡点：网关成为组织自行运维的基础设施。** Claude Code 每个版本都会新增能力，网关若不转发这些能力，相应功能就会失效。因此网关产品需要随 Claude Code 演进保持更新。[网关协议参考](https://code.claude.com/docs/en/llm-gateway-protocol)详述了需要转发的内容。

## 推广网关

**无论选用哪款网关产品，推广流程都相同：**

1. **部署网关**：配置提供商凭证，使网关能认证并转发请求。
2. **为每位开发者签发网关凭证**：按人归属用量，离职时吊销单个凭证。
3. **通过[托管设置文件](https://code.claude.com/docs/en/settings#settings-files)和密钥工具分发配置**：让每台机器都能获取 Base URL 和凭证。分发到位后开发者无需手动配置。若尚未建立设置分发机制，开发者可参照[连接页面](https://code.claude.com/docs/en/llm-gateway-connect)自行设置变量。
4. **让每位开发者[在 Claude Code 中确认配置](https://code.claude.com/docs/en/llm-gateway-connect#check-for-an-existing-configuration)**：在依赖网关之前暴露分发问题。

[为组织推广 LLM 网关](https://code.claude.com/docs/en/llm-gateway-rollout)一文逐步讲解了每个步骤及各步骤需分发的配置文件。网关只是组织设置的一部分；策略执行、用量可见性和数据处理决策请参阅[为组织设置 Claude Code](https://code.claude.com/docs/en/admin-setup)。

## 订阅与网关

**当[网关凭证变量](https://code.claude.com/docs/en/llm-gateway-connect#set-the-credential-variable)或 `apiKeyHelper` 生效时，开发者的 claude.ai 订阅不被使用。** 凭证替代了订阅登录，订阅的用量限制不适用。流量按 token 计费给凭证所有者（如组织的 Anthropic Console 账号，或 Amazon Bedrock、Google Cloud Agent Platform、Microsoft Foundry 账号）。

[`ANTHROPIC_BASE_URL`](https://code.claude.com/docs/en/llm-gateway-connect#set-the-base-url-and-credential) 是将 Claude Code 指向网关的变量。仅设置该变量而不设置网关凭证时，不会替代订阅——请求仍路由到网关，但已保存的 claude.ai 登录仍是活跃凭证，其用量限制和计费仍然适用。此时网关若要向 Anthropic 转发该流量，必须在 `anthropic-beta` 中转发 OAuth 能力；参见[请求头参考](https://code.claude.com/docs/en/llm-gateway-protocol#request-headers)。

## 相关页面

- [网关概览](https://code.claude.com/docs/en/gateways)：网关工作原理及选择指南
- [Claude apps gateway](https://code.claude.com/docs/en/claude-apps-gateway)：Anthropic 自托管网关，支持 SSO 登录和 OTLP 遥测
- [连接 Claude Code 到 LLM 网关](https://code.claude.com/docs/en/llm-gateway-connect)：设置 Base URL 和凭证，含各平台配置和排障表
- [为组织推广 LLM 网关](https://code.claude.com/docs/en/llm-gateway-rollout)：管理员部署网关、签发凭证和分发托管设置的检查清单
- [网关协议参考](https://code.claude.com/docs/en/llm-gateway-protocol)：Claude Code 向网关发送的内容，包括端点、需转发的请求头和功能透传
