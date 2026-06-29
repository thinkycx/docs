---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】安全机制
description: Claude Code 的安全架构与最佳实践：基于权限的分层防护、防范 Prompt 注入、MCP 安全、IDE 安全、云端执行安全，以及面向团队的安全建议。
category: translation
tags: [claude-code, security, translation]
refs:
  - https://code.claude.com/docs/en/security.md
---

# 安全机制

> Claude Code 的安全防护措施和安全使用的最佳实践。

---

## 安全设计理念

### 安全基石

**代码安全是最高优先级，Claude Code 从底层就按安全优先来构建。**

Claude Code 的开发遵循 Anthropic 完整的安全体系。你可以在 [Anthropic Trust Center](https://trust.anthropic.com) 获取更多资源（SOC 2 Type 2 报告、ISO 27001 证书等）。

---

### 基于权限的架构

**默认只读，需要修改操作时必须经过用户明确授权。**

Claude Code 默认只有只读权限。当需要额外操作（编辑文件、运行测试、执行命令）时，会请求明确授权。用户可以选择单次批准，也可以设为自动允许。

Claude Code 在运行可能修改系统的 Bash 命令前必须获得批准。内置的只读命令（如 `ls`、`cat`、`git status`）无需确认即可执行。这种设计让用户和组织可以直接配置权限策略。

权限配置的详细说明见 [权限配置](https://code.claude.com/docs/en/permissions)。

---

### 内置防护机制

**针对 Agent 系统的风险，提供多层防护。**

| 防护机制 | 说明 |
| :--- | :--- |
| 沙箱化 Bash 工具 | 通过文件系统和网络隔离来 [沙箱化](https://code.claude.com/docs/en/sandboxing) Bash 命令，减少权限弹窗的同时保持安全。用 `/sandbox` 启用，划定 Claude Code 可自主工作的边界 |
| 写入范围限制 | Claude Code 只能写入启动目录及其子目录——无法在未经授权的情况下修改父目录文件。虽然可以读取工作目录外的文件（方便访问系统库和依赖），但写入操作严格限定在项目范围内 |
| 缓解权限疲劳 | 支持按用户、按代码库、按组织预设安全命令白名单 |
| Accept Edits 模式 | 自动批准文件编辑和一组固定的文件系统 Bash 命令（如 `mkdir`、`touch`、`rm`、`mv`、`cp`、`sed`），限定在工作目录路径内。其他 Bash 命令和超出范围的路径仍需确认 |

---

### 用户责任

**Claude Code 只有你授予的权限，审核命令和代码的安全性是你的责任。**

Claude Code 只能执行你批准的操作。批准前务必审核建议的代码和命令是否安全。

---

## 防范 Prompt 注入

**Prompt 注入是攻击者试图通过插入恶意文本来篡改 AI 助手指令的技术。Claude Code 提供了多重防护。**

### 核心防护

| 防护层 | 说明 |
| :--- | :--- |
| 权限系统 | 敏感操作需要明确批准 |
| 上下文感知分析 | 通过分析完整请求上下文来检测潜在有害指令 |
| 输入净化 | 通过处理用户输入来防止命令注入 |
| 网络命令审批 | `curl`、`wget` 等从网络获取内容的命令默认不会自动批准。它们和其他非只读 Bash 命令一样需要确认，你可以单次批准或添加 `Bash(curl *)` 这样的明确允许规则。若要完全禁止，将其加入 [`permissions.deny`](https://code.claude.com/docs/en/permissions#tool-specific-permission-rules) |

---

### 隐私保护

**通过多项措施保护数据隐私。**

| 措施 | 说明 |
| :--- | :--- |
| 有限留存期 | 敏感信息的留存时间受限（详见 [Privacy Center](https://privacy.anthropic.com/en/articles/10023548-how-long-do-you-store-my-data)） |
| 受限访问 | 用户会话数据的访问受到严格限制 |
| 训练数据偏好 | 用户可控制数据是否用于训练。消费者用户可随时修改 [隐私设置](https://claude.ai/settings/privacy) |

详情请参阅 [商业服务条款](https://www.anthropic.com/legal/commercial-terms)（Team、Enterprise 和 API 用户）或 [消费者条款](https://www.anthropic.com/legal/consumer-terms)（Free、Pro 和 Max 用户）以及 [隐私政策](https://www.anthropic.com/legal/privacy)。

---

### 额外安全措施

**多层纵深防御，覆盖网络请求、上下文隔离、信任验证等方面。**

| 措施 | 说明 |
| :--- | :--- |
| 网络请求审批 | 发起网络请求的工具默认需要用户批准 |
| 隔离的上下文窗口 | Web fetch 使用独立的上下文窗口，避免将潜在恶意 prompt 注入主上下文 |
| 信任验证 | 首次运行代码库和新 MCP 服务器时需要信任验证 |
| 命令注入检测 | 可疑 Bash 命令即使已在白名单中也需要手动批准 |
| 默认拒绝（Fail-closed） | 未匹配规则的命令默认需要手动批准 |
| 自然语言描述 | 复杂 Bash 命令会附带解释说明，方便用户理解 |
| 安全凭据存储 | API key 和 token 在 macOS 上存入 Keychain，在 Windows 和 Linux 上通过文件权限保护。详见 [凭据管理](https://code.claude.com/docs/en/authentication#credential-management) |

> **关于信任验证的说明：**
> - 使用 `-p` 参数以非交互模式运行时，信任验证会被跳过
> - 在 home 目录直接启动 Claude Code 时，信任确认仅对当前会话有效、不会写入磁盘，每次启动都会重新提示。建议从项目子目录启动，信任确认会按目录持久化保存

> **Windows WebDAV 安全风险：** 在 Windows 上运行 Claude Code 时，建议不要启用 WebDAV 或允许 Claude Code 访问包含 WebDAV 子目录的 `\\*` 路径。[微软已废弃 WebDAV](https://learn.microsoft.com/en-us/windows/whats-new/deprecated-features#:~:text=The%20Webclient%20\(WebDAV\)%20service%20is%20deprecated)。启用 WebDAV 可能让 Claude Code 触发对远程主机的网络请求，绕过权限系统。

---

### 处理不受信内容的最佳实践

1. 批准前审查建议的命令
2. 避免将不受信内容直接通过管道传给 Claude
3. 验证对关键文件的修改
4. 使用虚拟机（VM）运行脚本和进行工具调用，尤其在与外部 Web 服务交互时
5. 通过 `/feedback` 报告可疑行为

> **注意：** 这些防护措施能显著降低风险，但没有系统能完全免疫所有攻击。使用任何 AI 工具时都应保持良好的安全习惯。

---

## MCP 安全

**Claude Code 允许配置 MCP 服务器，但安全性由用户自行把控。**

Claude Code 允许用户配置 Model Context Protocol (MCP) 服务器。允许使用的 MCP 服务器列表作为 Claude Code 设置的一部分，由工程师提交到源码管理中。

建议自行编写 MCP 服务器或使用来自可信提供方的 MCP 服务器。你可以为 MCP 服务器配置 Claude Code 权限。Anthropic 会根据其 [上架标准](https://claude.com/docs/connectors/building/review-criteria) 审核连接器后再加入 [Anthropic 目录](https://claude.ai/directory)，但不会对任何 MCP 服务器进行安全审计或管理。

---

## IDE 安全

在 IDE 中运行 Claude Code 的安全相关信息，参见 [VS Code 安全与隐私](https://code.claude.com/docs/en/vs-code#security-and-privacy)。

---

## 云端执行安全

**在 Web 端使用 Claude Code 时，有额外的安全控制。**

| 安全控制 | 说明 |
| :--- | :--- |
| 隔离虚拟机 | 每个云端会话在独立的、由 Anthropic 管理的 VM 中运行 |
| 网络访问控制 | 网络访问默认受限，可配置为禁用或仅允许特定域名 |
| 凭据保护 | 认证通过安全代理完成——沙箱内使用受限凭据，再由代理转换为你的实际 GitHub 认证 token |
| 分支限制 | Git push 操作仅限当前工作分支 |
| 审计日志 | 云端环境中的所有操作均被记录，用于合规和审计 |
| 自动清理 | 会话结束后，云端环境自动终止销毁 |

详见 [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web)。

---

**Remote Control 的工作方式不同：** Web 界面连接到本地机器上运行的 Claude Code 进程。所有代码执行和文件访问都在本地进行，与本地 Claude Code 会话传输的数据相同——通过 TLS 经 Anthropic API 传输。不涉及云端 VM 或沙箱。连接使用多个短期、窄范围的凭据，每个凭据功能受限且独立过期，以限制单个凭据泄露的影响范围。

---

## 安全最佳实践

### 处理敏感代码

| 建议 | 说明 |
| :--- | :--- |
| 审查变更 | 批准前审查所有建议的修改 |
| 项目级权限 | 为敏感代码库使用项目级权限设置 |
| 容器隔离 | 考虑使用 [dev containers](https://code.claude.com/docs/en/devcontainer) 获得额外隔离 |
| 定期审计 | 使用 `/permissions` 定期检查权限设置 |

---

### 团队安全

| 建议 | 说明 |
| :--- | :--- |
| 托管设置 | 使用 [managed settings](https://code.claude.com/docs/en/settings#settings-files) 强制执行组织标准 |
| 版本控制共享 | 通过版本控制共享已批准的权限配置 |
| 培训 | 对团队成员进行安全最佳实践培训 |
| 使用监控 | 通过 [OpenTelemetry metrics](https://code.claude.com/docs/en/monitoring-usage) 监控 Claude Code 使用情况 |
| 设置变更审计 | 使用 [`ConfigChange` hooks](https://code.claude.com/docs/en/hooks#configchange) 审计或阻止会话中的设置变更 |

---

### 报告安全问题

如果你发现 Claude Code 的安全漏洞：

1. 不要公开披露
2. 通过 [HackerOne 项目](https://hackerone.com/4f1f16ba-10d3-4d09-9ecc-c721aad90f24/embedded_submissions/new) 提交报告
3. 附上详细的复现步骤
4. 在我们修复之前不要公开披露

---

## 相关资源

| 资源 | 说明 |
| :--- | :--- |
| [安全指导插件](https://code.claude.com/docs/en/security-guidance) | 让 Claude 在会话中审查并修复自身代码变更中的漏洞 |
| [沙箱环境](https://code.claude.com/docs/en/sandbox-environments) | 对比各种隔离方案，选择适合你威胁模型的方案 |
| [沙箱化](https://code.claude.com/docs/en/sandboxing) | Bash 命令的文件系统和网络隔离 |
| [权限配置](https://code.claude.com/docs/en/permissions) | 配置权限和访问控制 |
| [使用监控](https://code.claude.com/docs/en/monitoring-usage) | 跟踪和审计 Claude Code 活动 |
| [开发容器](https://code.claude.com/docs/en/devcontainer) | 安全隔离的开发环境 |
| [Anthropic Trust Center](https://trust.anthropic.com) | 安全认证与合规 |
