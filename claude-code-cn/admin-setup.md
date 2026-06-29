---
title: 【译】组织管理设置
tags:
  - claude-code
  - admin
  - enterprise
  - translation
create: 2026-06-28
update: 2026-06-28
author: thinkycx
category: translation
description: 面向管理员的 Claude Code 部署决策指南，涵盖 API 提供商选择、托管设置分发、策略执行、使用监控和数据处理等方面。
refs: https://code.claude.com/docs/en/admin-setup.md
---

# 为组织设置 Claude Code

> 面向管理员的 Claude Code 部署决策指南，涵盖 API 提供商选择、托管设置分发、策略执行、使用监控和数据处理。

**Claude Code 通过托管设置来执行组织策略，这些设置优先于开发者的本地配置。** 你可以通过 Claude 管理控制台、移动设备管理 (MDM) 系统或磁盘上的文件来下发这些设置。设置控制 Claude 可以访问哪些工具、命令、服务器和网络目标。

本页按顺序介绍部署决策。每行链接到下方的详细章节以及该领域的参考页面。

> **注意：** SSO、SCIM 用户供应和席位分配在 Claude 账户级别配置。相关步骤参见 [Claude 企业管理员指南](https://claude.com/resources/tutorials/claude-enterprise-administrator-guide)和[席位分配](https://support.claude.com/en/articles/11845131-use-claude-code-with-your-team-or-enterprise-plan)。

| 决策                                          | 你在选择什么                       | 参考文档                                                                                                                                 |
| :-------------------------------------------- | :-------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------- |
| [选择 API 提供商](#选择-api-提供商)            | Claude Code 的认证方式和计费渠道    | [认证](https://code.claude.com/docs/en/authentication)、[Bedrock](https://code.claude.com/docs/en/amazon-bedrock)、[Vertex AI](https://code.claude.com/docs/en/google-vertex-ai)、[Foundry](https://code.claude.com/docs/en/microsoft-foundry) |
| [决定设置如何到达设备](#决定设置如何到达设备)    | 托管策略如何送达开发者机器          | [服务器管理设置](https://code.claude.com/docs/en/server-managed-settings)、[设置文件](https://code.claude.com/docs/en/settings#settings-files) |
| [决定执行什么策略](#决定执行什么策略)           | 允许哪些工具、命令和集成            | [权限](https://code.claude.com/docs/en/permissions)、[沙箱](https://code.claude.com/docs/en/sandboxing)                                   |
| [设置使用可见性](#设置使用可见性)               | 如何追踪花费和采用情况              | [分析](https://code.claude.com/docs/en/analytics)、[监控](https://code.claude.com/docs/en/monitoring-usage)、[成本](https://code.claude.com/docs/en/costs) |
| [审查数据处理](#审查数据处理)                   | 数据留存和合规态势                 | [数据使用](https://code.claude.com/docs/en/data-usage)、[安全](https://code.claude.com/docs/en/security)                                  |

## 选择 API 提供商

**Claude Code 通过以下几种 API 提供商之一连接 Claude。你的选择影响计费、认证、继承的合规态势以及开发者可用的 Claude Code 功能。**

| 提供商                       | 适用场景                                                                          |
| :--------------------------- | :-------------------------------------------------------------------------------- |
| Claude for Teams / Enterprise | 希望 Claude Code 和 claude.ai 统一在一个按席位计费的订阅中，无需运维基础设施。推荐方案。 |
| Claude Console               | API 优先或需要按用量付费                                                            |
| Amazon Bedrock               | 希望继承现有 AWS 合规控制和计费                                                      |
| Google Vertex AI             | 希望继承现有 GCP 合规控制和计费                                                      |
| Microsoft Foundry            | 希望继承现有 Azure 合规控制和计费                                                    |

部分 Claude Code 功能需要 claude.ai 账户。[网页版 Claude Code](https://code.claude.com/docs/en/claude-code-on-the-web)、[Routines](https://code.claude.com/docs/en/routines)、[代码审查](https://code.claude.com/docs/en/code-review)、[远程控制](https://code.claude.com/docs/en/remote-control)和 [Chrome 扩展](https://code.claude.com/docs/en/chrome)无法仅通过 Console API 密钥或云提供商凭据使用。如果通过 Bedrock、Vertex 或 Foundry 部署，需要规划开发者是否还需要 Claude for Teams 或 Enterprise 席位。每个功能页面列出了其计划要求。

完整的提供商对比（涵盖认证、区域和功能对等）参见[企业部署概览](https://code.claude.com/docs/en/third-party-integrations)。每个提供商的认证设置参见[认证](https://code.claude.com/docs/en/authentication)。

无论选择哪个提供商，[网络配置](https://code.claude.com/docs/en/network-config)中的代理和防火墙要求都适用。如果需要在多个提供商前面放一个统一端点或集中请求日志，参见 [LLM 网关](https://code.claude.com/docs/en/llm-gateway)。

## 决定设置如何到达设备

**托管设置定义优先于开发者本地配置的策略。** Claude Code 按以下优先顺序检查四个来源，并应用第一个返回非空配置的来源。

| 机制               | 分发方式                                                                                                                                                                                           | 优先级 | 平台           |
| :----------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----- | :------------- |
| 服务器管理          | claude.ai 管理控制台                                                                                                                                                                               | 最高   | 全部           |
| plist / 注册表策略  | macOS: `com.anthropic.claudecode` plist<br />Windows: `HKLM\SOFTWARE\Policies\ClaudeCode`                                                                                                          | 高     | macOS, Windows |
| 基于文件的托管      | macOS: `/Library/Application Support/ClaudeCode/managed-settings.json`<br />Linux 和 WSL: `/etc/claude-code/managed-settings.json`<br />Windows: `C:\Program Files\ClaudeCode\managed-settings.json` | 中     | 全部           |
| Windows 用户注册表  | `HKCU\SOFTWARE\Policies\ClaudeCode`                                                                                                                                                                | 最低   | 仅 Windows     |

服务器管理设置在认证时到达设备，活跃会话期间每小时刷新，无需端点基础设施。需要 Claude for Teams 或 Enterprise 计划，因此使用其他提供商的部署需要选择基于文件或 OS 级别的机制。

如果组织混合使用多个提供商，为 claude.ai 用户配置[服务器管理设置](https://code.claude.com/docs/en/server-managed-settings)，并为其他用户提供[基于文件或 plist/注册表的回退](https://code.claude.com/docs/en/settings#settings-files)，确保所有人都能收到托管策略。

plist 和 HKLM 注册表位置适用于任何提供商，并且因为需要管理员权限写入而具有防篡改能力。HKCU 处的 Windows 用户注册表无需提权即可写入，应视为便捷默认值而非强制执行渠道。

默认情况下，WSL 只读取 `/etc/claude-code` 处的 Linux 文件路径。要将 Windows 注册表和 `C:\Program Files\ClaudeCode` 策略扩展到同一台机器上的 WSL，在这两个仅管理员可写的 Windows 来源中设置 [`wslInheritsWindowsSettings: true`](https://code.claude.com/docs/en/settings#available-settings)。

无论选择哪种机制，托管值优先于用户和项目设置。数组设置（如 `permissions.allow` 和 `permissions.deny`）合并所有来源的条目，开发者可以扩展托管列表但不能移除。对于[两个例外](https://code.claude.com/docs/en/settings#settings-precedence)（`fallbackModel` 和 `availableModels`），托管值替换而非合并较低层。

参见[服务器管理设置](https://code.claude.com/docs/en/server-managed-settings)和[设置文件与优先级](https://code.claude.com/docs/en/settings#settings-files)。

## 决定执行什么策略

**托管设置可以锁定工具、沙箱执行环境、限制 MCP 服务器和插件来源、以及控制哪些 hook 运行。** 每行是一个控制面及驱动它的设置键。

| 控制面                            | 作用                                                                                          | 关键设置                                                                                         |
| :------------------------------- | :-------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------- |
| [权限规则](https://code.claude.com/docs/en/permissions) | 允许、询问或拒绝特定工具和命令                                                                  | `permissions.allow`、`permissions.deny`                                                          |
| [权限锁定](https://code.claude.com/docs/en/permissions#managed-only-settings) | 仅托管权限规则生效；禁用 `--dangerously-skip-permissions`                                       | `allowManagedPermissionRulesOnly`、`permissions.disableBypassPermissionsMode`                     |
| [沙箱](https://code.claude.com/docs/en/sandboxing) | OS 级文件系统和网络隔离，支持域名白名单                                                          | `sandbox.enabled`、`sandbox.network.allowedDomains`                                               |
| [托管策略 CLAUDE.md](https://code.claude.com/docs/en/memory#deploy-organization-wide-claude-md) | 全组织指令在每个会话中加载，不可排除                                                              | 托管策略路径下的文件                                                                              |
| [MCP 服务器控制](https://code.claude.com/docs/en/managed-mcp) | 限制用户可添加或连接的 MCP 服务器，或部署固定集合                                                 | `allowedMcpServers`、`deniedMcpServers`、`allowManagedMcpServersOnly`，或已部署的 `managed-mcp.json` |
| [插件市场控制](https://code.claude.com/docs/en/plugin-marketplaces#managed-marketplace-restrictions) | 限制用户可添加和安装的市场来源                                                                   | `strictKnownMarketplaces`、`blockedMarketplaces`                                                  |
| [自定义锁定](https://code.claude.com/docs/en/settings#strictpluginonlycustomization) | 阻止来自用户和项目来源的 skill、agent、hook 和 MCP 服务器，只允许来自插件或托管设置                  | `strictPluginOnlyCustomization`                                                                   |
| [Hook 限制](https://code.claude.com/docs/en/settings#hook-configuration) | 仅加载托管 hook；限制 HTTP hook URL                                                             | `allowManagedHooksOnly`、`allowedHttpHookUrls`                                                    |
| [禁用 Agent 视图](https://code.claude.com/docs/en/agent-view#how-background-sessions-are-hosted) | 关闭 `claude agents`、`--bg`、`/background` 和按需 supervisor                                   | `disableAgentView`                                                                                |
| [模型限制](https://code.claude.com/docs/en/model-config#restrict-model-selection) | `availableModels` 过滤选择器中显示的模型。添加 `enforceAvailableModels` 还约束自动选择的默认模型   | `availableModels`、`enforceAvailableModels`                                                       |
| [版本下限](https://code.claude.com/docs/en/settings) | 防止自动更新安装低于组织最低要求的版本                                                           | `minimumVersion`                                                                                  |
| [要求版本范围](https://code.claude.com/docs/en/settings) | 运行版本不在组织批准范围内时拒绝启动。比 `minimumVersion` 更强                                    | `requiredMinimumVersion`、`requiredMaximumVersion`                                                |

权限规则和沙箱覆盖不同层面。拒绝 WebFetch 阻止 Claude 的 fetch 工具，但如果允许 Bash，`curl` 和 `wget` 仍可访问任何 URL。沙箱通过 OS 级别的网络域名白名单来弥补这个漏洞。

这些控制防御的威胁模型参见[安全](https://code.claude.com/docs/en/security)。

## 设置使用可见性

**根据需要报告的内容选择监控方式。**

| 能力            | 提供内容                                | 可用性         | 起步位置                                           |
| :-------------- | :-------------------------------------- | :------------- | :------------------------------------------------- |
| 使用监控         | 会话、工具和 token 的 OpenTelemetry 导出 | 所有提供商     | [监控使用](https://code.claude.com/docs/en/monitoring-usage) |
| 分析面板         | 每用户指标、贡献追踪、排行榜             | 仅 Anthropic   | [分析](https://code.claude.com/docs/en/analytics)          |
| 成本追踪         | 花费限制、速率限制和使用归因             | 仅 Anthropic   | [成本](https://code.claude.com/docs/en/costs)              |

云提供商通过 AWS Cost Explorer、GCP Billing 或 Azure Cost Management 暴露花费。Claude for Teams 和 Enterprise 计划包含使用面板，位于 [claude.ai/analytics/claude-code](https://claude.ai/analytics/claude-code)。

## 审查数据处理

**在 Team、Enterprise、Claude API 和云提供商计划中，Anthropic 不会使用你的代码或提示训练模型。** 你的 API 提供商决定数据留存和合规态势。

| 主题                  | 需要了解的内容                                                    | 起步位置                                                       |
| :-------------------- | :--------------------------------------------------------------- | :------------------------------------------------------------- |
| 数据使用策略           | Anthropic 收集什么、保留多久、什么永远不会用于训练                  | [数据使用](https://code.claude.com/docs/en/data-usage)          |
| 零数据留存 (ZDR)       | 请求完成后不存储任何内容。面向符合条件的 Claude for Enterprise 账户  | [零数据留存](https://code.claude.com/docs/en/zero-data-retention) |
| 安全架构              | 网络模型、加密、认证、审计跟踪                                     | [安全](https://code.claude.com/docs/en/security)                |

如果需要请求级审计日志或按数据敏感度路由流量，在开发者和提供商之间放置 [LLM 网关](https://code.claude.com/docs/en/llm-gateway)。监管要求和认证参见[法律与合规](https://code.claude.com/docs/en/legal-and-compliance)。

## 验证与上线

**配置完托管设置后，让开发者在 Claude Code 中运行 `/status`。** Status 标签页的 `Setting sources` 行应显示 `Enterprise managed settings`，后面括号注明来源：`(remote)`、`(plist)`、`(HKLM)`、`(HKCU)` 或 `(file)`。参见[验证活跃设置](https://code.claude.com/docs/en/settings#verify-active-settings)。

分享以下资源帮助开发者上手：

* [快速入门](https://code.claude.com/docs/en/quickstart)：从安装到项目使用的首次会话指南
* [常见工作流](https://code.claude.com/docs/en/common-workflows)：代码审查、重构和调试等日常任务的模式
* [Claude 101](https://anthropic.skilljar.com/claude-101) 和 [Claude Code 实战](https://anthropic.skilljar.com/claude-code-in-action)：Anthropic Academy 自学课程

对于登录问题，引导开发者查看[认证故障排除](https://code.claude.com/docs/en/troubleshoot-install#login-and-authentication)。最常见的修复方法：

* 运行 `/logout` 再 `/login` 切换账户
* 如果缺少企业认证选项，运行 `claude update`
* 更新后重启终端

如果开发者看到 "You haven't been added to your organization yet"，说明其席位未包含 Claude Code 访问权限，需要在管理控制台中更新。

## 下一步

选定提供商和分发机制后，继续详细配置：

* [服务器管理设置](https://code.claude.com/docs/en/server-managed-settings)：通过 Claude 管理控制台下发托管策略
* [设置参考](https://code.claude.com/docs/en/settings)：所有设置键、文件位置和优先级规则
* [Monorepo 和大型仓库](https://code.claude.com/docs/en/large-codebases)：面向 monorepo 部署的按目录配置模式
* [Amazon Bedrock](https://code.claude.com/docs/en/amazon-bedrock)、[Google Vertex AI](https://code.claude.com/docs/en/google-vertex-ai)、[Microsoft Foundry](https://code.claude.com/docs/en/microsoft-foundry)：提供商特定的部署
* [Claude 企业管理员指南](https://claude.com/resources/tutorials/claude-enterprise-administrator-guide)：SSO、SCIM、席位管理和推广剧本
