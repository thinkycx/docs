---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】托管 MCP
description: 通过 managed-mcp.json、允许列表和拒绝列表控制组织中用户可添加或连接的 MCP 服务器。涵盖完全管控、策略过滤和监控等多种模式。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/managed-mcp.md
  - en-source/managed-mcp.md
---

# 控制组织的 MCP 服务器访问

> 通过托管配置文件、允许列表和拒绝列表限制用户可添加或连接的 MCP 服务器。

**默认情况下，运行 Claude Code 的任何人都可以连接任意 [MCP 服务器](https://code.claude.com/docs/en/mcp)。** Anthropic 在将连接器添加到 [Anthropic Directory](https://claude.ai/directory) 前会审查其[上架标准](https://claude.com/docs/connectors/building/review-criteria)，但不安全审计或管理任何 MCP 服务器。作为管理员，你可以限制组织中运行哪些服务器，从部署固定的审批集到完全禁用 MCP。

本页介绍：

- [选择模式](#选择模式)
- [用 `managed-mcp.json` 完全管控](#用-managed-mcpjson-完全管控)，包括[禁用 MCP](#完全禁用-mcp)
- [用允许列表和拒绝列表进行策略控制](#基于策略的允许列表和拒绝列表控制)
- [用户看到的限制信息](#用户如何看到限制)
- [监控组织使用的服务器](#监控-mcp-使用)

## 选择模式

**Claude Code 支持不同限制级别。** 每种模式使用以下一种或两种机制：`managed-mcp.json` 部署固定集，`allowedMcpServers`/`deniedMcpServers` 过滤用户配置的内容。

| 模式 | 作用 | 配置方式 |
| :--- | :--- | :--- |
| **禁用 MCP** | 所有位置不加载任何服务器 | `managed-mcp.json` 含空服务器 map |
| **固定部署** | 每个用户获得相同服务器且不能添加其他 | `managed-mcp.json` 含你要的服务器 |
| **审批目录** | 发布审批服务器列表；用户从中添加，其他被阻止 | `allowedMcpServers` + `allowManagedMcpServersOnly: true` |
| **仅插件服务器** | 服务器只能来自插件；用户不能自行添加 | [`strictPluginOnlyCustomization`](https://code.claude.com/docs/en/settings#strictpluginonlycustomization) 列表中含 `mcp` |
| **软允许列表** | 强制允许列表，用户可在自己设置中扩展 | `allowedMcpServers`（不带 `allowManagedMcpServersOnly`） |
| **仅拒绝列表** | 阻止已知有问题的服务器，允许其他一切 | `deniedMcpServers` |
| **无限制** | 用户可添加任何服务器 | 不部署任何托管 MCP 配置 |

## 用 managed-mcp.json 完全管控

**部署 `managed-mcp.json` 后，Claude Code 仅加载该文件定义的服务器。** 用户不能添加、修改或使用其他 MCP 服务器（包括插件提供的）。该文件还会压制 claude.ai 连接器，除非你[允许它们与托管集共存](#允许-claudeai-连接器与托管集共存)。

`managed-mcp.json` 是独立文件，无法通过[服务器托管设置](https://code.claude.com/docs/en/server-managed-settings)交付。任何能以管理员权限写入系统路径的进程都可以部署它。大规模部署通常通过设备管理工具。Claude Code 在以下路径查找：

| 平台 | 路径 |
| :--- | :--- |
| macOS | `/Library/Application Support/ClaudeCode/managed-mcp.json` |
| Linux 和 WSL | `/etc/claude-code/managed-mcp.json` |
| Windows | `C:\Program Files\ClaudeCode\managed-mcp.json` |

文件格式与项目级 [`.mcp.json`](https://code.claude.com/docs/en/mcp#project-scope) 相同：

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/"
    },
    "sentry": {
      "type": "http",
      "url": "https://mcp.sentry.dev/mcp"
    },
    "company-internal": {
      "type": "stdio",
      "command": "/usr/local/bin/company-mcp-server",
      "args": ["--config", "/etc/company/mcp-config.json"],
      "env": {
        "COMPANY_API_URL": "https://internal.example.com"
      }
    }
  }
}
```

### 使用每用户凭据认证

**机器上的任何用户都可以读取此文件，所以不要在 `env` 块中存储 API key 或其他凭据。** 通过以下方式传递每用户凭据：

- [`${VAR}` 扩展](https://code.claude.com/docs/en/mcp#environment-variable-expansion-in-mcp-json)从每个用户的环境读取密钥
- [OAuth 或每用户 headers](https://code.claude.com/docs/en/mcp#authenticate-with-remote-mcp-servers) 让每个用户以自己身份认证
- [`headersHelper`](https://code.claude.com/docs/en/mcp#use-dynamic-headers-for-custom-authentication) 在连接时生成凭据

### 验证配置

确认文件生效的两个检查：

1. `claude mcp list` 仅显示 `managed-mcp.json` 中的服务器。如果用户自己的服务器仍出现，文件未被读取；检查路径和权限。
2. `claude mcp add --transport http test https://example.com/mcp` 以 `Cannot add MCP server: enterprise MCP configuration is active and has exclusive control over MCP servers` 失败。

### 完全禁用 MCP

部署包含空服务器 map 的 `managed-mcp.json` 以阻止所有 MCP 服务器：

```json
{
  "mcpServers": {}
}
```

用户在 `/mcp` 中看不到任何服务器，`claude mcp add` 以企业策略错误失败。

### 允许 claude.ai 连接器与托管集共存

部署 `managed-mcp.json` 默认压制 [claude.ai 连接器](https://code.claude.com/docs/en/mcp#use-mcp-servers-from-claude-ai)。要在 `managed-mcp.json` 服务器旁加载那些连接器，在[托管设置源](https://code.claude.com/docs/en/admin-setup#decide-how-settings-reach-devices)中设置 `"allowAllClaudeAiMcps": true`。需要 Claude Code v2.1.149 或更高版本。

## 基于策略的允许列表和拒绝列表控制

**允许列表和拒绝列表过滤哪些已配置的服务器可以加载。** 它们不是注册表：服务器仍需由用户、插件或 `managed-mcp.json` 先添加，然后允许/拒绝列表才适用。

### 按 URL、命令或名称匹配服务器

`allowedMcpServers` 和 `deniedMcpServers` 是条目列表。每个条目是包含单个键的对象：

| 键 | 匹配 | 用于 |
| :--- | :--- | :--- |
| `serverUrl` | 远程服务器 URL，精确或带 `*` 通配符 | HTTP 和 SSE 服务器 |
| `serverCommand` | 启动 stdio 服务器的精确命令和参数 | Stdio 服务器 |
| `serverName` | 用户分配的标签。仅精确匹配；不展开通配符 | 两种类型（但见下方警告） |

`serverName` 条目不是安全控制。名称是用户运行 `claude mcp add` 时分配的标签而非底层服务器，用户可以将任何服务器命名为 `github`。要强制实际运行哪些服务器，添加 `serverCommand` 或 `serverUrl` 条目。

### 服务器如何被评估

加载服务器前（包括 `managed-mcp.json` 中的），Claude Code 按顺序运行三个检查：

1. **合并列表。** 每个设置源的允许列表和拒绝列表合并为一个允许列表和一个拒绝列表。
2. **检查拒绝列表。** 匹配任何拒绝列表条目的服务器被阻止。没有什么能覆盖拒绝列表匹配。
3. **检查允许列表。** 如果 `allowedMcpServers` 在任何地方都未设置，通过拒绝列表的每个服务器都加载。如果已设置，服务器必须匹配的内容取决于类型。

| 服务器类型 | 允许条件 |
| :--- | :--- |
| 远程（HTTP 或 SSE） | 匹配 `serverUrl` 条目。`serverName` 匹配仅在允许列表不含 `serverUrl` 条目时计入 |
| Stdio | 匹配 `serverCommand` 条目。`serverName` 匹配仅在允许列表不含 `serverCommand` 条目时计入 |

两个匹配规则：

- **命令精确匹配。** 每个参数按顺序。`["npx", "-y", "server"]` 不匹配 `["npx", "server"]`。
- **URL 支持 `*` 通配符**，包括 scheme 中。主机名匹配不区分大小写。路径保持大小写敏感。

### 示例配置

```json
{
  "allowedMcpServers": [
    { "serverUrl": "https://api.githubcopilot.com/*" },
    { "serverUrl": "https://mcp.sentry.dev/*" },
    { "serverCommand": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "."] },
    { "serverCommand": ["python", "/usr/local/bin/approved-server.py"] },
    { "serverUrl": "https://mcp.example.com/*" },
    { "serverUrl": "https://*.internal.example.com/*" }
  ],
  "deniedMcpServers": [
    { "serverName": "dangerous-server" },
    { "serverCommand": ["npx", "-y", "unapproved-package"] },
    { "serverUrl": "https://*.untrusted.example.com/*" }
  ]
}
```

### 将允许列表限制为仅托管设置

要使托管允许列表成为唯一生效的，在托管设置文件中设置 `allowManagedMcpServersOnly`：

```json
{
  "allowManagedMcpServersOnly": true,
  "allowedMcpServers": [
    { "serverUrl": "https://api.githubcopilot.com/*" },
    { "serverUrl": "https://*.internal.example.com/*" }
  ]
}
```

当 `allowManagedMcpServersOnly` 为 `true` 时，用户、项目和 local 设置中的允许列表被忽略。拒绝列表仍从所有来源合并。

## 用户如何看到限制

| 限制 | 用户看到的 |
| :--- | :--- |
| `managed-mcp.json` 存在且用户运行 `claude mcp add` | `Cannot add MCP server: enterprise MCP configuration is active and has exclusive control over MCP servers` |
| 服务器在拒绝列表中且用户运行 `claude mcp add` | `Cannot add MCP server "<name>": server is explicitly blocked by enterprise policy` |
| 服务器不在允许列表中且用户运行 `claude mcp add` | `Cannot add MCP server "<name>": not allowed by enterprise policy` |
| 之前配置的服务器现在被策略阻止 | 服务器静默从 `/mcp` 和 `claude mcp list` 消失，无警告 |

最后一种情况中，用户不会收到策略导致服务器消失的信号，所以部署新限制时告知受影响的用户哪些服务器被阻止。

## 监控 MCP 使用

配置 [OpenTelemetry 导出](https://code.claude.com/docs/en/monitoring-usage)后，Claude Code 可记录用户调用了哪些 MCP 服务器和工具。设置 `OTEL_LOG_TOOL_DETAILS=1` 在工具事件中包含 MCP 服务器和工具名称，然后在收集器中聚合以查看用户实际连接了哪些服务器。

## 配置汇总

| 配置面 | 控制什么 | 位置 | 交付方式 |
| :--- | :--- | :--- | :--- |
| `managed-mcp.json` | 固定服务器集，独占控制 | 系统路径 | MDM、GPO、fleet 管理。无法通过服务器托管设置 |
| `allowedMcpServers` | 允许的服务器列表 | 任何[设置文件](https://code.claude.com/docs/en/settings#settings-files) | 要强制执行，需[托管设置源](https://code.claude.com/docs/en/admin-setup#decide-how-settings-reach-devices) |
| `deniedMcpServers` | 阻止的服务器列表 | 任何设置文件；所有来源合并 | 同 `allowedMcpServers` |
| `allowManagedMcpServersOnly` | 将允许列表锁定为仅托管来源 | 仅托管设置源 | 同 `allowedMcpServers` |
| `allowAllClaudeAiMcps` | 让 claude.ai 连接器与 `managed-mcp.json` 共存 | 仅托管设置源 | 同 `allowedMcpServers` |

## 相关资源

- [Decide what to enforce](https://code.claude.com/docs/en/admin-setup#decide-what-to-enforce)：MCP 限制与权限规则、沙箱等管理控制
- [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp)：完整 MCP 参考
- [Settings](https://code.claude.com/docs/en/settings)：设置层级和托管设置优先级
- [Server-managed settings](https://code.claude.com/docs/en/server-managed-settings)：从 Claude.ai 管理控制台交付设置
- [Security](https://code.claude.com/docs/en/security)：这些控制所防御的威胁模型
