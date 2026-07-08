---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】功能可用性
description: 对比 Claude Code 各功能在 Anthropic 订阅计划、Anthropic Console、Amazon Bedrock、Claude Platform on AWS、Google Cloud Agent Platform 和 Microsoft Foundry 上的可用性。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/feature-availability.md
  - en-source/feature-availability.md
---

# 功能可用性

> 对比 Claude Code 各功能在 Anthropic 订阅计划、Anthropic Console、Amazon Bedrock、Claude Platform on AWS、Google Cloud Agent Platform 和 Microsoft Foundry 上的可用性。

**Claude Code CLI 和所有本地运行的功能在每个提供商上表现一致。** 各提供商的设置说明参见[企业部署概览](https://code.claude.com/docs/en/third-party-integrations)。要快速了解你的提供商缺少什么，参见[按提供商汇总](#按提供商汇总)。

表格中：✓ 表示可用，✗ 表示不可用，「见注释」指向部分支持的脚注。

## 按模型提供商的可用性

**认证方式决定 Claude Code 能使用哪些功能：**

- **Claude 订阅**：通过 claude.ai 账户登录（Pro、Max、Team 或 Enterprise）
- **Anthropic Console**：使用 Anthropic API 密钥认证
- **Amazon Bedrock**：使用 Bedrock 模型目录中的 Claude 模型，设置 `CLAUDE_CODE_USE_BEDROCK`
- **Claude Platform on AWS**：通过 AWS Marketplace 购买但调用 Anthropic API，设置 `CLAUDE_CODE_USE_ANTHROPIC_AWS`
- **Google Cloud Agent Platform**：Google 运营，设置 `CLAUDE_CODE_USE_VERTEX`
- **Microsoft Foundry**：Anthropic 在 Azure 上运营，设置 `CLAUDE_CODE_USE_FOUNDRY`

### 所有提供商通用功能

以下在每个提供商上表现一致：

- [CLI](https://code.claude.com/docs/en/quickstart) 和 [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview)
- [VS Code](https://code.claude.com/docs/en/vs-code) 和 [JetBrains](https://code.claude.com/docs/en/jetbrains) 扩展
- [子代理](https://code.claude.com/docs/en/sub-agents)、[Hooks](https://code.claude.com/docs/en/hooks-guide)、[命令](https://code.claude.com/docs/en/commands)、[Skills](https://code.claude.com/docs/en/skills)
- [CLAUDE.md 记忆](https://code.claude.com/docs/en/memory)、[插件](https://code.claude.com/docs/en/plugins)、[MCP 服务器](https://code.claude.com/docs/en/mcp)
- [检查点](https://code.claude.com/docs/en/checkpointing)、[沙箱](https://code.claude.com/docs/en/sandboxing)、[Workflows](https://code.claude.com/docs/en/workflows)
- [OpenTelemetry 指标](https://code.claude.com/docs/en/monitoring-usage) 和[托管设置文件](https://code.claude.com/docs/en/settings#settings-files)

### 需要 Claude 订阅的功能

以下需要 claude.ai 账户登录，API 密钥或第三方提供商无法使用：

- [Web 版 Claude Code](https://code.claude.com/docs/en/claude-code-on-the-web)、移动版、[Slack 版](https://code.claude.com/docs/en/slack)
- [Claude Code Desktop](https://code.claude.com/docs/en/desktop)
- [Routines](https://code.claude.com/docs/en/routines)（`/schedule`）
- [Ultraplan](https://code.claude.com/docs/en/ultraplan) 和 [Ultrareview](https://code.claude.com/docs/en/ultrareview)
- [Code Review](https://code.claude.com/docs/en/code-review)：Team 和 Enterprise 计划
- [Remote Control](https://code.claude.com/docs/en/remote-control)
- [Chrome 扩展](https://code.claude.com/docs/en/chrome)
- [Computer use](https://code.claude.com/docs/en/computer-use)：Pro 和 Max 计划
- [Artifacts](https://code.claude.com/docs/en/artifacts)：Pro、Max、Team 和 Enterprise 计划
- [语音听写](https://code.claude.com/docs/en/voice-dictation)

### 按提供商变化的 CLI 能力

| 功能 | Claude 订阅 | Anthropic Console | Amazon Bedrock | Claude Platform on AWS | Google Cloud Agent Platform | Microsoft Foundry |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| [Web 搜索](https://code.claude.com/docs/en/tools-reference#websearch-tool-behavior) | ✓ | ✓ | ✗ | ✓ | Claude 4 及以上 | ✓ |
| [Fast mode](https://code.claude.com/docs/en/fast-mode) | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| [Auto mode](https://code.claude.com/docs/en/auto-mode-config) | ✓ | ✓ | 需 `CLAUDE_CODE_ENABLE_AUTO_MODE` | ✓ | 需 `CLAUDE_CODE_ENABLE_AUTO_MODE` | 需 `CLAUDE_CODE_ENABLE_AUTO_MODE` |
| [Advisor](https://code.claude.com/docs/en/advisor) | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| [Channels](https://code.claude.com/docs/en/channels) | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| [`/loop` 定时任务](https://code.claude.com/docs/en/scheduled-tasks) | ✓ | ✓ | 仅显式间隔 | ✓ | 仅显式间隔 | 仅显式间隔 |
| [GitHub Actions](https://code.claude.com/docs/en/github-actions) / [GitLab CI/CD](https://code.claude.com/docs/en/gitlab-ci-cd) | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |

### 管理和分析

| 功能 | Claude 订阅 | Anthropic Console | Amazon Bedrock | Claude Platform on AWS | Google Cloud Agent Platform | Microsoft Foundry |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| [分析仪表板和 API](https://code.claude.com/docs/en/analytics) | ✓（Team/Enterprise） | ✓ | ✗ | ✗ | ✗ | ✗ |
| [服务端托管设置](https://code.claude.com/docs/en/server-managed-settings) | ✓（Team/Enterprise） | ✓（Team/Enterprise） | ✗ | ✗ | ✗ | ✗ |
| [零数据保留](https://code.claude.com/docs/en/zero-data-retention) | ✓（合格 Enterprise） | ✓（合格账户） | 取决于 AWS 协议 | ✓（合格账户） | 取决于 Google Cloud 协议 | 取决于 Azure 协议 |

> 通过 [LLM 网关](https://code.claude.com/docs/en/llm-gateway)认证时，功能可用性匹配网关转发到的底层提供商。

### 按提供商汇总

**Amazon Bedrock**

- **不可用**：所有需要订阅的功能 + Web 搜索、Fast mode、Advisor、Channels、分析仪表板、服务端托管设置
- **部分支持**：Auto mode（需 `CLAUDE_CODE_ENABLE_AUTO_MODE`）、`/loop`（仅显式间隔）、ZDR（取决于 AWS 协议）
- **替代方案**：定时任务用 `/loop` + 显式间隔；云会话用 GitHub Actions / GitLab CI/CD；Web 查找用 WebFetch 工具 + 具体 URL

**Claude Platform on AWS**

- **不可用**：所有需要订阅的功能 + Fast mode、Advisor、Channels、分析仪表板、服务端托管设置
- **Bedrock 不支持但此处可用**：Web 搜索、Auto mode（无需 opt-in）、`/loop` 自适应节奏

**Google Cloud Agent Platform**

- **不可用**：所有需要订阅的功能 + Fast mode、Advisor、Channels、分析仪表板、服务端托管设置
- **部分支持**：Web 搜索（Claude 4+ 模型）、Auto mode（需 opt-in）、`/loop`（仅显式间隔）、ZDR（取决于 Google Cloud 协议）

**Microsoft Foundry**

- **不可用**：所有需要订阅的功能 + Fast mode、Advisor、Channels、GitHub Actions、GitLab CI/CD、分析仪表板、服务端托管设置
- **部分支持**：Auto mode（需 opt-in）、`/loop`（仅显式间隔）、ZDR（取决于 Azure 协议）

**Anthropic Console**

- **不可用**：所有需要订阅的功能
- CLI 变化能力中的所有功能均可用

## 按订阅计划的可用性

**通过 claude.ai 账户登录时，计划决定以下功能的可用性：**

| 功能 | Pro | Max | Team | Enterprise |
| :--- | :--- | :--- | :--- | :--- |
| [Web 版 Claude Code](https://code.claude.com/docs/en/claude-code-on-the-web) | ✓ | ✓ | ✓ | ✓（需 premium seat） |
| [Routines](https://code.claude.com/docs/en/routines) | ✓ | ✓ | ✓ | ✓ |
| [Remote Control](https://code.claude.com/docs/en/remote-control) | ✓ | ✓ | Admin 启用 | Admin 启用 |
| [Channels](https://code.claude.com/docs/en/channels) | ✓ | ✓ | Admin 启用 | Admin 启用 |
| [Computer use](https://code.claude.com/docs/en/computer-use) | ✓ | ✓ | ✗ | ✗ |
| [Code Review](https://code.claude.com/docs/en/code-review) | ✗ | ✗ | ✓ | ✓ |
| [Artifacts](https://code.claude.com/docs/en/artifacts) | ✓ | ✓ | ✓ | Admin 启用 |
| [分析仪表板和贡献指标](https://code.claude.com/docs/en/analytics) | ✗ | ✗ | ✓ | ✓ |
| [服务端托管设置](https://code.claude.com/docs/en/server-managed-settings) | ✗ | ✗ | ✓ | ✓ |
| SSO | ✗ | ✗ | ✓ | ✓ |
| SCIM | ✗ | ✗ | ✗ | ✓ |
| [Compliance API](https://platform.claude.com/docs/en/api/admin-api/compliance/overview) | ✗ | ✗ | ✗ | ✓ |
| [零数据保留](https://code.claude.com/docs/en/zero-data-retention) | ✗ | ✗ | ✗ | ✓（需单独启用） |

## 模型可用性

各提供商和区域的 Claude 模型和上下文窗口大小参见[模型配置](https://code.claude.com/docs/en/model-config)和 [Models overview](https://platform.claude.com/docs/en/about-claude/models/overview)。Vision、PDF 输入和扩展思考是模型能力而非 Claude Code 功能，在提供该模型的所有提供商上工作。

## 相关资源

- [企业部署概览](https://code.claude.com/docs/en/third-party-integrations)：跨提供商比较认证、计费和区域
- 提供商设置指南：[Amazon Bedrock](https://code.claude.com/docs/en/amazon-bedrock)、[Claude Platform on AWS](https://code.claude.com/docs/en/claude-platform-on-aws)、[Google Cloud Agent Platform](https://code.claude.com/docs/en/google-vertex-ai)、[Microsoft Foundry](https://code.claude.com/docs/en/microsoft-foundry)
- [平台和集成](https://code.claude.com/docs/en/platforms)：Claude Code 运行平台
