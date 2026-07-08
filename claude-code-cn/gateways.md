---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Gateway 总览
description: Gateway 是组织在 Claude Code 与模型服务商之间运行的代理。本文介绍 gateway 的工作原理、选择 Claude apps gateway 还是自建 gateway、以及与订阅的关系。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/gateways.md
  - en-source/gateways.md
---

# 通过 Gateway 运行 Claude Code

> 将 Claude Code 路由到自托管 gateway 以实现集中凭证管理、使用量跟踪和成本控制。涵盖架构、Anthropic 的 Claude apps gateway 和使用其他 gateway 产品。

**Gateway 是组织在 Claude Code 和模型服务商之间运行的代理。** Claude Code 将 API 流量发送到 gateway 而非直接发送到服务商，gateway 用组织持有的凭证转发请求。开发者向 gateway 认证而非持有服务商凭证，认证、使用量跟踪、预算和审计日志在一个你控制的中心点完成。

Claude Code 在 `claude` 二进制文件中内置了自托管 gateway [Claude apps gateway](https://code.claude.com/docs/en/claude-apps-gateway)，无需额外 gateway 产品。如果组织已经运行 [LLM gateway](https://code.claude.com/docs/en/llm-gateway)，Claude Code 也能配合使用。

## Gateway 如何工作

**每个开发者的 Claude Code 指向 gateway 地址，用 gateway 签发的凭证认证。**

Gateway 认证开发者、应用你配置的访问和预算规则，然后用组织的凭证将请求转发给服务商。服务商可以是 Anthropic API 或[云服务商](https://code.claude.com/docs/en/third-party-integrations)（如 Amazon Bedrock、Google Cloud Agent Platform 或 Microsoft Foundry），由 gateway 配置决定。使用 Claude apps gateway 或其他暴露 Anthropic 格式端点的 gateway 时，更换服务商无需触碰开发者机器。

涉及两类凭证：

| 凭证类型 | 说明 |
| --- | --- |
| 开发者凭证 | 每个开发者持有自己的，由 gateway 签发。用于向 gateway 认证并在使用量追踪中识别身份 |
| 服务商凭证 | Gateway 持有你的服务商账号的一个凭证，所有转发流量共用 |

## 选择 Gateway

Claude Code 支持 Anthropic 自有 gateway 或你组织已运行的 gateway。

### Claude apps gateway

**Claude apps gateway 是 Anthropic 的自托管 gateway，内置于 `claude` 二进制文件中。** 可路由到 Amazon Bedrock、Claude Platform on AWS、Google Cloud、Microsoft Foundry 或 Anthropic API 作为上游。开发者通过 `/login` 用企业 IdP 登录，gateway 按 IdP 组强制模型访问和[托管设置](https://code.claude.com/docs/en/permissions#managed-settings)，并向你的可观测性栈发送 [OpenTelemetry Protocol (OTLP)](https://code.claude.com/docs/en/monitoring-usage) 使用指标。

**因为与每个 Claude Code 版本一起构建和测试**，它转发 Claude Code 发送的 header 和请求字段。独立维护的 gateway 需要随每次版本更新[转发规则](https://code.claude.com/docs/en/llm-gateway-protocol#forward-as-open-lists)；Claude apps gateway 随 CLI 一起发布，无需维护列表。功能差异参见 [Availability and limitations](https://code.claude.com/docs/en/claude-apps-gateway#availability-and-limitations)。

Gateway 登录是浏览器 SSO 步骤，没有 service-token 流程，因此无开发者批准登录的 CI 管道无法通过它认证——直接对服务商配置。Agent SDK 会话和 `claude -p` 在已登录机器上使用该机器的 gateway 会话并受其策略管控。参见 [CI pipelines and remote machines](https://code.claude.com/docs/en/claude-apps-gateway#ci-pipelines-and-remote-machines)。

部署指南参见 [Claude apps gateway](https://code.claude.com/docs/en/claude-apps-gateway)。

### 其他 Gateway

如果组织已运行 LLM gateway 或 API gateway，可以继续使用。Anthropic 不背书、维护或审计其他 gateway 产品，也不支持通过任何 gateway 将 Claude Code 路由到非 Claude 模型。参见 [Other LLM gateways](https://code.claude.com/docs/en/llm-gateway) 了解管理员部署清单、gateway 必须实现什么、以及如何指向它。

## 订阅与 Gateway

**通过 gateway 凭证连接时，用量按 API 费率计入组织的服务商账户**，开发者的 claude.ai 订阅不被使用或收费。设置 [`ANTHROPIC_AUTH_TOKEN`](https://code.claude.com/docs/en/env-vars) 给你运行的 gateway，或通过 `/login` 登录 Claude apps gateway，会关闭该会话的订阅登录。所有转发请求计费到 gateway 服务商凭证背后的账户。

例外情况是仅设置 `ANTHROPIC_BASE_URL` 而无 gateway 凭证时，请求仍通过 gateway 路由，但已保存的 claude.ai 登录保持为活跃凭证，适用订阅的用量限制和计费。[Other LLM gateways](https://code.claude.com/docs/en/llm-gateway#subscriptions-and-gateways) 介绍该配置及 gateway 需要转发什么才能使其工作。

## 与 Gateway 分开配置的内容

**Gateway 路由模型 API 请求。一些你可能以为由它处理的内容实际在别处配置：**

| 内容 | 说明 |
| --- | --- |
| 哪个模型应答 | 用 `/model` 命令或[模型环境变量](https://code.claude.com/docs/en/model-config#setting-your-model)选择。Gateway 决定请求去哪，不决定开发者选哪个模型。Claude apps gateway 可用每组 `availableModels` 白名单限制选择范围 |
| 其他网络流量 | Claude Code 自身的版本检查和下载直接发送到 Anthropic，与 gateway 路径分开。签入 Claude apps gateway 会话时，gateway 凭证禁用 Anthropic 侧分析，且[遥测转发](https://code.claude.com/docs/en/claude-apps-gateway-config#telemetry)配置后 OTLP 导出固定到 gateway。网络仍需允许出站到[必需域名](https://code.claude.com/docs/en/network-config)，或设置 [`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`](https://code.claude.com/docs/en/env-vars) 关闭可选流量 |
| 企业 HTTP 代理 | `HTTPS_PROXY` 介于 Claude Code 和所有服务器之间（包括 gateway）。如果网络需要，在 gateway 之外[配置代理](https://code.claude.com/docs/en/network-config)。Claude apps gateway 的[登录检查代理主机也需在私有网络](https://code.claude.com/docs/en/claude-apps-gateway#prerequisites)；否则将 gateway 主机加入 `NO_PROXY` |

## 下一步

下一页取决于谁运行 gateway：

- [Claude apps gateway](https://code.claude.com/docs/en/claude-apps-gateway)：部署 Anthropic 自托管 gateway（SSO 登录和 OTLP 遥测）
- [Other LLM gateways](https://code.claude.com/docs/en/llm-gateway)：你组织已运行的 gateway 需实现什么，以及如何指向它
- [为组织部署 Claude Code](https://code.claude.com/docs/en/admin-setup)：更广泛的部署决策（gateway 只是其中一部分）
