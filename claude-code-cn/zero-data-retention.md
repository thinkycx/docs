---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】零数据保留
description: Claude Code 的零数据保留 (ZDR) 功能详解，适用于 Claude for Enterprise 的合格账户。涵盖覆盖范围、禁用功能、模型可用性和申请方式。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/zero-data-retention.md
  - en-source/zero-data-retention.md
---

# 零数据保留

> 了解 Claude Code 的零数据保留 (ZDR)，适用于 Claude for Enterprise 的合格账户。包括覆盖范围、禁用功能和申请方式。

**零数据保留 (ZDR) 适用于 Claude for Enterprise 的合格账户。** 启用 ZDR 后，Claude Code 会话期间生成的提示词和模型响应会实时处理，响应返回后 Anthropic 不存储这些数据（法律要求或打击滥用除外）。

> ZDR 不包含在标准 Claude for Enterprise 计划中，无法从管理设置中启用。适用于合格账户，需要 Anthropic 单独启用。如果你的组织需要 ZDR，[联系销售](https://www.anthropic.com/contact-sales?utm_source=claude_code&utm_medium=docs&utm_content=zero_data_retention_request)或 Anthropic 账户团队确认资格。

**Claude for Enterprise 上的 ZDR 为企业客户提供零数据保留能力，同时保留管理能力：**

- 按用户的成本控制
- [分析](https://code.claude.com/docs/en/analytics)仪表板
- [服务端托管设置](https://code.claude.com/docs/en/server-managed-settings)
- 审计日志

ZDR 仅适用于 Anthropic 直接平台上的 Claude Code on Claude for Enterprise。Amazon Bedrock、Google Cloud Agent Platform 或 Microsoft Foundry 上的 Claude 部署请参考各平台的数据保留政策。

## ZDR 覆盖范围

**ZDR 覆盖 Claude for Enterprise 上的 Claude Code 推理。**

> ZDR 按组织启用。每个新组织需要 Anthropic 账户团队单独启用 ZDR。ZDR 不会自动应用于同一账户下创建的新组织。

### ZDR 覆盖的内容

ZDR 覆盖通过 Claude Code on Claude for Enterprise 进行的模型推理调用。在终端使用 Claude Code 时，发送的提示词和 Claude 生成的响应不被 Anthropic 保留。适用于 ZDR 组织可用的所有模型。某些模型需要数据保留因此在 ZDR 下不可用；参见[ZDR 下的模型可用性](#zdr-下的模型可用性)。

### ZDR 不覆盖的内容

**即使组织启用了 ZDR，以下内容仍遵循[标准数据保留政策](https://code.claude.com/docs/en/data-usage#data-retention)：**

| 功能 | 详情 |
| :--- | :--- |
| claude.ai 聊天 | Web 界面的聊天对话不受 ZDR 覆盖 |
| Cowork | Cowork 会话不受 ZDR 覆盖 |
| Claude Code Analytics | 不存储提示词或模型响应，但收集账户邮箱和使用统计等生产力元数据。贡献指标在 ZDR 组织中不可用 |
| 用户和席位管理 | 账户邮箱和席位分配等管理数据按标准政策保留 |
| 第三方集成 | 第三方工具、MCP 服务器或其他外部集成处理的数据不受 ZDR 覆盖 |

## ZDR 下禁用的功能

**当 Claude for Enterprise 组织启用 ZDR 时，需要存储提示词或补全的功能在后端级别自动禁用：**

| 功能 | 原因 |
| :--- | :--- |
| [Web 版 Claude Code](https://code.claude.com/docs/en/claude-code-on-the-web) | 需要服务端存储对话历史 |
| Desktop 应用的[云会话](https://code.claude.com/docs/en/desktop#cloud-sessions) | 需要持久化会话数据 |
| [Artifacts](https://code.claude.com/docs/en/artifacts) | 需要在 Anthropic 基础设施上存储发布的页面内容 |
| 反馈提交（`/feedback`） | 提交反馈会发送对话数据到 Anthropic |

这些功能在后端被阻止，无论客户端如何显示。尝试使用会返回组织策略不允许该操作的错误。

### ZDR 下的模型可用性

**Claude Fable 5 在启用了零数据保留的组织中不可用。** 该模型类[需要数据保留](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#model-specific-data-retention-requirements)，ZDR 组织的请求无法由其提供服务。

其他模型在 ZDR 下保持可用。Fable 5 不是默认模型，`best` 别名（在 Fable 5 可用时解析为它）在不可用时解析为 Opus（包括 ZDR 组织）。

## 违规时的数据保留

**即使启用了 ZDR，Anthropic 可能在法律要求或处理使用政策违规时保留数据。** 如果会话被标记为违规，Anthropic 可能保留相关输入和输出最长 2 年，与 Anthropic 标准 ZDR 政策一致。

## 申请 ZDR

**要为 Claude Code on Claude for Enterprise 申请 ZDR，[联系销售](https://www.anthropic.com/contact-sales?utm_source=claude_code&utm_medium=docs&utm_content=zero_data_retention_request)或 Anthropic 账户团队。** 账户团队将内部提交请求，Anthropic 确认资格后在你的组织上启用 ZDR。所有启用操作都有审计日志。

如果你目前通过按量付费 API 密钥使用 ZDR for Claude Code，可以迁移到 Claude for Enterprise 以在保持 ZDR 的同时获得管理功能。联系账户团队协调迁移。
