---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】GitHub Enterprise Server
description: 将 Claude Code 连接到自托管的 GitHub Enterprise Server 实例，用于 Web 会话、代码审查和插件市场。涵盖管理员设置、开发者工作流和 Teleport。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/github-enterprise-server.md
  - en-source/github-enterprise-server.md
---

# Claude Code 与 GitHub Enterprise Server

> 将 Claude Code 连接到自托管的 GitHub Enterprise Server 实例，用于 web 会话、代码审查和插件市场。

GitHub Enterprise Server 支持面向 Team 和 Enterprise 计划。

**GitHub Enterprise Server（GHES）支持让你的组织使用 Claude Code 处理托管在自管理 GitHub 实例上的仓库，而非 github.com。** Owner 连接 GHES 实例后，开发者无需任何仓库级配置即可运行 web 会话和获得自动代码审查。GHES 上托管的插件市场也受支持；凭据要求因界面而异，详见 [GHES 上的插件市场](#ghes-上的插件市场)。

github.com 上的仓库请参见 [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web) 和 [Code Review](https://code.claude.com/docs/en/code-review)。要在自己的 CI 基础设施中运行 Claude，参见 [GitHub Actions](https://code.claude.com/docs/en/github-actions)。

## 支持的功能

| 功能 | GHES 支持 | 备注 |
| :--- | :--- | :--- |
| Claude Code on the web | 支持 | Owner 连接 GHES 实例一次；开发者照常使用 `claude --cloud` 或 [claude.ai/code](https://claude.ai/code) |
| Code Review | 支持 | 与 github.com 相同的自动 PR 审查 |
| Claude Security | 支持 | Enterprise 计划公测版，在 [claude.ai/security](https://claude.ai/security) |
| Teleport 会话 | 支持 | 用 `--teleport` 在 web 和终端间移动会话 |
| 插件市场 | 支持 | 凭据要求因界面而异 |
| 贡献指标 | 支持 | 通过 webhook 送达[分析仪表板](https://code.claude.com/docs/en/analytics) |
| GitHub Actions | 支持 | 需要手动设置 workflow；`/install-github-app` 仅限 github.com |
| GitHub MCP server | 不支持 | GitHub MCP server 不支持 GHES 实例 |

## 管理员设置

**Owner 一次性将 GHES 实例连接到 Claude Code。** 之后组织中的开发者无需额外配置即可使用 GHES 仓库。你需要 Claude 组织中的 Owner 或 Primary Owner 角色，以及在 GHES 实例上创建 GitHub App 的权限。

引导设置生成 GitHub App manifest 并重定向你到 GHES 实例一键创建应用。如果环境阻止重定向流程，可使用[手动设置](#手动设置)。

**步骤 1：打开 Claude Code 管理设置**

前往 [claude.ai/admin-settings/claude-code](https://claude.ai/admin-settings/claude-code) 找到 GitHub Enterprise Server 部分。

**步骤 2：开始引导设置**

点击 **Connect**。输入连接的显示名称和 GHES 主机名，例如 `github.example.com`。如果 GHES 实例使用自签名或私有 CA 证书，在可选字段粘贴 CA 证书。

**步骤 3：创建 GitHub App**

点击 **Continue to GitHub Enterprise**。浏览器重定向到你的 GHES 实例并预填应用 manifest。审查配置并点击 **Create GitHub App**。GHES 将你重定向回 Claude，应用凭据自动存储。

**步骤 4：在仓库上安装应用**

从 GHES 实例上的 GitHub App 页面，在你要让 Claude 访问的仓库或组织上安装应用。可以先安装部分后续再添加。

**步骤 5：启用功能**

返回 [claude.ai/admin-settings/claude-code](https://claude.ai/admin-settings/claude-code)，使用与 github.com 相同的配置为 GHES 仓库启用 [Code Review](https://code.claude.com/docs/en/code-review#set-up-code-review)、Claude Security 和[贡献指标](https://code.claude.com/docs/en/analytics#enable-contribution-metrics)。

### GitHub App 权限

manifest 为 GitHub App 配置 Claude 跨 web 会话、Code Review、Claude Security 和贡献指标所需的权限和 webhook 事件：

| 权限 | 访问级别 | 用途 |
| :--- | :--- | :--- |
| Contents | 读写 | 克隆仓库和推送分支 |
| Pull requests | 读写 | 创建 PR 和发布审查评论 |
| Issues | 读写 | 响应 issue 提及 |
| Checks | 读写 | 发布 Code Review check runs |
| Actions | 只读 | 读取 CI 状态用于 auto-fix |
| Repository hooks | 读写 | 接收贡献指标的 webhooks |
| Metadata | 只读 | GitHub 对所有应用的要求 |

应用订阅 `pull_request`、`issue_comment`、`pull_request_review_comment`、`pull_request_review` 和 `check_run` 事件。

### 手动设置

如果引导重定向流程被网络配置阻止，点击 **Add manually** 而非 Connect。在 GHES 实例上使用[上述权限和事件](#github-app-权限)创建 GitHub App，然后在表单中输入凭据：主机名、OAuth client ID 和 secret、GitHub App ID、client ID、client secret、webhook secret 和私钥。

### 网络要求

你的 GHES 实例必须从 Anthropic 基础设施可达，以便 Claude 克隆仓库和发布审查评论。如果 GHES 实例在防火墙后，将 [Anthropic API IP 地址](https://platform.claude.com/docs/en/api/ip-addresses)加入白名单。

## 开发者工作流

**Owner 连接 GHES 实例后，开发者无需任何配置。** Claude Code 从工作目录的 git remote 自动检测 GHES 主机名。

照常从 GHES 实例克隆仓库：

```bash
git clone git@github.example.com:platform/api-service.git
cd api-service
```

然后启动 web 会话。Claude 从 git remote 检测 GHES 主机并通过组织配置的实例路由会话：

```bash
claude --cloud "Add retry logic to the payment webhook handler"
```

会话在 Anthropic 基础设施上运行，从 GHES 克隆仓库并将变更推送回分支。用 `/tasks` 或在 [claude.ai/code](https://claude.ai/code) 监控进度。参见 [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web) 了解完整的云会话工作流包括 diff 审查、auto-fix 和 routines。

### Teleport 会话到终端

用 `claude --teleport` 将 web 会话拉入本地终端。Teleport 在获取分支和加载会话历史前验证你在同一 GHES 仓库的检出中。参见 [teleport 要求](https://code.claude.com/docs/en/claude-code-on-the-web#teleport-requirements)。

## GHES 上的插件市场

**在 GHES 实例上托管插件市场以在组织内分发内部工具。** 市场结构与 github.com 托管的完全相同，但安装方式因你在哪里添加市场而异，凭据也因界面不同：

| 界面 | 安装方式 | 每个用户需要什么 |
| :--- | :--- | :--- |
| Claude Code CLI 和 desktop | 使用机器现有的 git 凭据克隆市场仓库 | 从机器 git 访问 GHES 主机 |
| 托管设置（`extraKnownMarketplaces`） | 注册条目并使用机器 git 凭据克隆 | 从机器 git 访问 GHES 主机 |
| claude.ai 组织插件设置 | Owner 选择 GHES 实例作为源；Anthropic 后端使用[管理员设置](#管理员设置)中的 GitHub App 获取和同步仓库 | 添加后用户无需额外操作 |
| claude.ai 用户设置 | Anthropic 后端使用提交用户的 GitHub Enterprise 连接获取仓库 | 自己的 GitHub Enterprise 账户已连接到 Claude |
| Claude Code on the web | 云会话在沙箱内克隆市场。沙箱仅在会话仓库在同一实例时才能访问 GHES 实例 | 对 GHES 市场不可靠；请使用 CLI、托管设置或 claude.ai |

### 添加 GHES 市场

`owner/repo` 简写总是解析到 github.com。GHES 市场使用完整 git URL。推荐 HTTPS URL：

```bash
/plugin marketplace add https://github.example.com/platform/claude-plugins.git
```

如果机器已信任 GHES 主机，SSH URL 也可：

```bash
/plugin marketplace add git@github.example.com:platform/claude-plugins.git
```

Claude Code 非交互式运行 git，拒绝连接不在机器 `known_hosts` 文件中的 SSH 主机。使用 HTTPS URL 配合 git credential helper 可避免 `known_hosts` 要求。

参见 [Create and distribute a plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces) 了解构建市场的完整指南。

### 通过托管设置预注册 GHES 市场

`extraKnownMarketplaces` 设置预注册市场，让开发者无需手动设置即可获得。它可在[任何设置文件](https://code.claude.com/docs/en/settings#extraknownmarketplaces)中使用；托管设置可组织范围交付：

```json
{
  "extraKnownMarketplaces": {
    "internal-tools": {
      "source": {
        "source": "git",
        "url": "https://github.example.com/platform/claude-plugins.git"
      }
    }
  }
}
```

### 在托管设置中白名单 GHES 市场

如果组织使用[托管设置](https://code.claude.com/docs/en/settings)限制开发者可添加的市场，使用 `hostPattern` 源类型允许 GHES 实例上的所有市场，无需枚举每个仓库：

```json
{
  "strictKnownMarketplaces": [
    {
      "source": "hostPattern",
      "hostPattern": "^github\\.example\\.com$"
    }
  ]
}
```

## 限制

部分功能在 GHES 上的行为与 github.com 不同：

- **`/install-github-app` 命令**：改为在 claude.ai 上按照[管理员设置](#管理员设置)流程操作。如果还需要 GHES 上的 GitHub Actions workflow，手动适配[示例 workflow](https://github.com/anthropics/claude-code-action/blob/main/examples/claude.yml)。
- **GitHub MCP server**：改为使用配置了 GHES 主机的 `gh` CLI。运行 `gh auth login --hostname github.example.com` 认证，然后 Claude 可在会话中使用 `gh` 命令。

## 故障排除

### Web 会话无法克隆仓库

如果 `claude --cloud` 因克隆错误失败，验证 Owner 已为你的 GHES 实例完成设置，且 GitHub App 已安装在你正在使用的仓库上。请连接实例的 Owner 确认 Claude 设置中注册的主机名与你 git remote 中的主机名匹配。

### 市场添加因策略错误失败

如果 `/plugin marketplace add` 因你的 GHES URL 被阻止，你的组织限制了市场来源。请管理员在[托管设置](#在托管设置中白名单-ghes-市场)中为 GHES 主机名添加 `hostPattern` 条目。

### claude.ai 上市场添加因 GitHub 访问错误失败

如果从用户设置添加 GHES 市场失败且显示通用错误如 "Marketplace couldn't be added"，先检查 GitHub Enterprise 连接。这是你自己的 GitHub Enterprise 账户未连接到 Claude 时出现的错误，即使组织的 GHES 实例已配置且其他用户已连接。

要连接 GitHub Enterprise 账户：[claude.ai/code](https://claude.ai/code) 的仓库选择器为每个已配置的 GHES 实例提供连接选项。或者请 Owner 在组织插件设置中添加市场，这移除了每用户连接要求。

### GHES 实例不可达

如果审查或 web 会话超时，你的 GHES 实例可能从 Anthropic 基础设施不可达。确认防火墙允许来自 [Anthropic API IP 地址](https://platform.claude.com/docs/en/api/ip-addresses)的入站连接。

## 相关资源

- [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web)：在云基础设施上运行 Claude Code 会话
- [Code Review](https://code.claude.com/docs/en/code-review)：自动 PR 审查
- [Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)：构建和分发插件目录
- [Analytics](https://code.claude.com/docs/en/analytics)：跟踪使用和贡献指标
- [Managed settings](https://code.claude.com/docs/en/settings)：组织级策略配置
- [Network configuration](https://code.claude.com/docs/en/network-config)：防火墙和 IP 白名单要求
