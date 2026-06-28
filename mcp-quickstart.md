---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】MCP 快速开始
description: 手把手教你为 Claude Code 接入第一个 MCP server，涵盖添加、验证连接、使用工具以及常见错误排查的完整流程。
category: translation
tags: [claude-code, mcp, quickstart, translation]
refs:
  - https://code.claude.com/docs/en/mcp-quickstart.md
---

# 连接 MCP Server

> 为 Claude Code 添加 MCP server，验证连接，找到磁盘上的配置文件。

**MCP 让 Claude Code 调用内置工具集之外的能力。** [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) 为 Claude Code 提供搜索 issue 追踪器、查询数据库、操控浏览器等扩展能力，这些能力来自运行在本机或远端的 MCP server。

本指南带你用 Claude Code CLI 完整走通一个 MCP server 的接入流程。读完后你会掌握：server 的连接和验证方法、配置文件存储位置、以及最常见连接错误的修复方式。

> **提示：** 你也可以通过桌面客户端、VS Code 或 Web 界面添加 MCP server，参见 [从其他界面连接](#从其他界面连接)。

关于 Claude Code 中 MCP server 的所有连接和配置方式，请查阅 [MCP 参考文档](https://code.claude.com/docs/en/mcp)。

## 前置条件

**开始之前，确认你已具备以下环境。**

| 条件 | 说明 |
|------|------|
| Claude Code 已安装 | 参见 [安装指南](https://code.claude.com/docs/en/quickstart) 并完成认证 |
| 终端已打开 | 在任意项目目录下即可，空目录也行 |

## 添加并验证 Server

**以 Claude Code 文档 MCP server 为例，走通完整的"添加 → 验证 → 使用 → 清理"流程。**

下面的示例连接的是 [Claude Code 文档 MCP server](https://code.claude.com/docs/mcp)——一个托管式 server，提供对 Claude Code 文档的全文搜索。它无需认证，也不需要额外配置，非常适合作为你的第一个测试对象。

所有 server 的接入步骤相同：添加、检查连接状态、在会话中使用，最后可选清理。部分 server 会多出一步（如浏览器登录），见 [更多 MCP Server 示例](#更多-mcp-server-示例)。更多可接入的 server 请浏览 [Anthropic 目录](https://code.claude.com/docs/en/mcp#find-and-build-mcp-servers)。

### 步骤 1：添加 MCP Server

**在终端中注册 server。** 注意：这条命令在普通终端中运行，不要在 `claude` 会话内执行——你是在启动对话之前配置 server。

```bash
claude mcp add --transport http claude-code-docs https://code.claude.com/docs/mcp
```

命令各部分说明：

| 部分 | 含义 |
|------|------|
| `claude mcp add` | 向 Claude Code 注册一个 server |
| `--transport http` | 表示 server 是通过 URL 托管的，而非本地进程 |
| `claude-code-docs` | 自定义名称。叫 `docs` 也行，Claude Code 用这个名称在工具调用输出中标注来源，也用于 `claude mcp remove` 等命令引用 |
| `https://code.claude.com/docs/mcp` | server 的托管 URL |

命令输出类似 `Added HTTP MCP server claude-code-docs with URL: https://code.claude.com/docs/mcp to local config`。`local config` 表示该 server 只对当前项目的你生效。若需全局生效（所有项目），使用 user 作用域，见 [修改 Server 作用域](#修改-server-作用域)。

### 步骤 2：检查连接状态

**确认 server 已出现在列表中，并且状态正常。**

```bash
claude mcp list
```

server 会带一个状态标志：

| 状态 | 含义 |
|------|------|
| `✓ Connected` | 可以使用。`claude-code-docs` 应该显示这个状态 |
| `! Connected · tools fetch failed` | 已连接但获取工具列表失败。运行 `claude mcp get <name>` 查看错误详情 |
| `! Needs authentication` | server 可达但需要浏览器登录，或通过 `--header` 传入 token。见 [连接需要登录的 Server](#连接需要登录的-server) |
| `✗ Failed to connect` | server 无响应。见 [故障排查](#故障排查) |
| `✗ Connection error` | 连接尝试抛出异常。见 [故障排查](#故障排查) |
| `⏸ Pending approval` | 项目级 server 尚未批准。见 [直接编辑 .mcp.json](#直接编辑-mcpjson) |

### 步骤 3：使用 Server

**启动会话，让 Claude 调用新 server。**

```bash
claude
```

```text
Use the claude-code-docs server to look up what MCP_TIMEOUT does
```

> **提示：** 通常不需要在 prompt 中指明 server 名称，因为 Claude 会自动选择相关工具。这里显式指定是为了确保演示请求走新接入的 server，而不是走 web fetch 等其他工具。

Claude 第一次调用该 server 时会请求权限。批准后继续。工具调用输出会标注 server 名称，证明答案来自 MCP server 而非 Claude 内置知识。

### 步骤 4：移除 Server（可选）

**不再需要时可以移除。**

```bash
claude mcp remove claude-code-docs
```

> **注意：** 每个已连接的 server 都会占用 [Claude 上下文窗口](https://code.claude.com/docs/en/how-claude-code-works#the-context-window) 的空间，因为其工具名称和指令会加载到每次会话中。移除不再使用的 server 能释放这部分空间。

## Server 存储位置

**`claude mcp add` 把 server 的详细信息写入配置文件。** 默认注册到 `local` 作用域：仅对当前项目的你生效。传入 `--scope user` 可一次注册到所有项目；传入 `--scope project` 则与团队共享。详见 [修改 Server 作用域](#修改-server-作用域)。

> **提示：** `claude mcp add` 在所有 shell 中（包括 PowerShell 和 CMD）用法一致。在 `claude` 会话内，用 `/mcp` 命令查看和管理已添加的 server。

其他添加方式：

- [添加本地 Server](#添加本地-server)：在本机运行程序，而非连接远端 URL。
- [直接编辑 .mcp.json](#直接编辑-mcpjson)：手写 JSON 配置，而非用命令行。
- [连接需要登录的 Server](#连接需要登录的-server)：接入需要浏览器登录的托管式 server。

### 查看配置文件位置

**`claude mcp add` 根据 `--scope` 标志写入不同文件。** 通常不需要手动编辑，但了解位置有助于调试和版本控制。

| 作用域 | 文件 | 生效范围 |
|--------|------|----------|
| `local` | `~/.claude.json`，当前项目条目下 | 仅你本人，仅当前项目（默认） |
| `project` | 项目根目录的 `.mcp.json` | 所有克隆该项目的人 |
| `user` | `~/.claude.json`，顶层 `mcpServers` 键下 | 仅你本人，所有项目 |

Windows 上 `~/.claude.json` 解析为 `%USERPROFILE%\.claude.json`，通常是 `C:\Users\YourName\.claude.json`。如果设置了 [`CLAUDE_CONFIG_DIR`](https://code.claude.com/docs/en/env-vars)，Claude Code 会从该目录读取 `.claude.json`。

运行 `claude mcp get claude-code-docs` 可查看 server 定义存储在哪个作用域。多作用域同时定义同一 server 时的优先级规则见 [MCP 安装作用域](https://code.claude.com/docs/en/mcp#mcp-installation-scopes)。

## 修改 Server 作用域

**作用域在添加时确定，修改需先移除再重新添加。** 以下示例都先移除第一节中创建的 local 条目，确保 server 只有一份定义。如果你在上一节末尾已经移除，跳过此命令：

```bash
claude mcp remove claude-code-docs --scope local
```

### 在所有项目中使用

**以 `user` 作用域重新添加，所有项目生效，仍然仅你本人可见。**

```bash
claude mcp add --scope user --transport http claude-code-docs https://code.claude.com/docs/mcp
```

### 与团队共享

**以 `project` 作用域重新添加，写入项目根目录的 `.mcp.json`。**

```bash
claude mcp add --scope project --transport http claude-code-docs https://code.claude.com/docs/mcp
```

将 `.mcp.json` 提交到版本控制。团队成员克隆仓库后启动 Claude Code 时会看到批准提示，批准后即可连接使用。

## 更多 MCP Server 示例

**第一个示例使用了无需登录的托管式 server。以下示例覆盖另外两种常见形态。**

### 添加本地 Server

**本地 stdio server 是 Claude Code 以子进程方式启动的本机程序，而非通过 URL 访问的远端服务。** 当工具需要访问本地资源（如浏览器、文件系统、数据库 socket）时使用。

以 [Playwright MCP server](https://github.com/microsoft/playwright-mcp) 为例：它为 Claude 提供一个可以导航、点击、读取的浏览器，无需账号。它通过 `npx` 运行，需要 [Node.js](https://nodejs.org/en/download) 18 或更高版本。

#### 步骤 1：添加 Playwright Server

```bash
claude mcp add playwright -- npx -y @playwright/mcp@latest
```

与托管式 server 的三处不同：

| 差异 | 说明 |
|------|------|
| 无 `--transport` 标志 | 本地 server 使用默认的 `stdio` 传输 |
| `--` 分隔符 | 分隔符之后的内容是 Claude Code 启动 server 的命令 |
| `-y` | 告诉 `npx` 自动安装包，不等待确认 |

Playwright 默认驱动本机已安装的 Chrome。如需使用其他浏览器，在 `@playwright/mcp@latest` 后追加 `--browser firefox` 等参数。

#### 步骤 2：检查连接

**`Added` 确认只表示条目已保存，不代表命令已跑通。需要单独检查连接。**

```bash
claude mcp list
```

首次检查可能显示 `✗ Failed to connect`（`npx` 正在下载包），稍等片刻再试。

#### 步骤 3：使用浏览器

给 Claude 一个需要浏览器的任务：

```text
Use playwright to open https://example.com and tell me the page title
```

浏览器窗口会打开，你可以看到它在操作。工具调用输出带有 `playwright` server 名称和动作标签（如 `browser_navigate`）。

你可以让它打开本地 dev server 检查页面渲染是否正常，或按照 bug 报告逐步操作验证。

### 连接需要登录的 Server

**Sentry、Linear、Notion 等托管服务通过 OAuth 认证：添加 URL 后需浏览器登录。**

以 Sentry 为例。连接其他服务时替换其 URL 即可（可在 [Anthropic 目录](https://code.claude.com/docs/en/mcp#find-and-build-mcp-servers) 或服务文档中查找）。

#### 步骤 1：添加 Server

```bash
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp
```

添加后 `claude mcp list` 显示 `! Needs authentication`，这是预期行为——下一步完成登录。

#### 步骤 2：浏览器认证

启动 Claude Code 会话并打开 MCP 面板：

```text
/mcp
```

从列表中选择 `sentry`，回车后选择 `Authenticate`。浏览器会打开 Sentry 登录页面，完成授权。

回到 Claude Code，server 状态变为 connected。如果登录失败或浏览器未打开，见 [故障排查](#故障排查)。

#### 步骤 3：使用 Server

向 Claude 提问需要该服务的问题，如 `What Sentry projects do I have access to?`，检查输出中工具调用是否标注了 `sentry` server 名称。

**使用静态 token 认证的 server** 在添加时通过 `--header "Authorization: Bearer <token>"` 传入 token。完整示例见 [GitHub 接入示例](https://code.claude.com/docs/en/mcp#example-connect-to-github-for-code-reviews)。

## 直接编辑 .mcp.json

**[作用域表](#查看配置文件位置)中的每个文件使用相同的 JSON 格式。** 本节编辑 `.mcp.json`（project 作用域文件）。手动编辑它最有价值，因为它会被提交到仓库，相当于团队共享的配置即代码。

在项目根目录创建 `.mcp.json`。以下示例同时定义了本指南中的两个 server——通过 HTTP 访问的文档 server 和本地 `stdio` 方式的 Playwright server：

```json
{
  "mcpServers": {
    "claude-code-docs": {
      "type": "http",
      "url": "https://code.claude.com/docs/mcp"
    },
    "playwright": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    }
  }
}
```

字段因 server 类型而异：

| Server 类型 | 关键字段 | 含义 |
|-------------|----------|------|
| HTTP | `url` | Claude Code 连接的远端地址 |
| stdio | `command` + `args` | Claude Code 运行的本地命令 |

保存文件后启动新的 Claude Code 会话。Claude Code 在启动时读取 `.mcp.json`。

首次发现项目级 server 时，Claude Code 会要求你批准。这一机制确保克隆的仓库不会在未经你同意的情况下启动本机进程。批准提示，或运行 `/mcp` 稍后批准。

批准后运行 `/mcp` 确认 server 显示为 connected。如果显示错误，见 [故障排查](#故障排查)。

## 从其他界面连接

**本指南使用 `claude mcp` CLI 命令，但 Claude Code 的所有界面都支持 MCP server 接入。**

| 界面 | 操作方式 |
|------|----------|
| Claude Code 桌面客户端 | 通过 [Connectors UI](https://code.claude.com/docs/en/desktop#connect-external-tools) 添加 |
| Claude Desktop 聊天应用 | 与 Claude Code 是不同的应用。要将其 `claude_desktop_config.json` 中的 server 导入 CLI，在 macOS 或 WSL 上运行 `claude mcp add-from-claude-desktop` |
| VS Code | 见 [通过 MCP 连接外部工具](https://code.claude.com/docs/en/vs-code#connect-to-external-tools-with-mcp) |
| Claude Code Web | 从仓库中读取 `.mcp.json`。见 [直接编辑 .mcp.json](#直接编辑-mcpjson) |
| Claude.ai | 在 [claude.ai/customize/connectors](https://claude.ai/customize/connectors) 添加的连接器，用同一账号登录 CLI 时自动加载。见 [使用 Claude.ai 的 MCP server](https://code.claude.com/docs/en/mcp#use-mcp-servers-from-claude-ai) |

## 故障排查

**server 未连接时，先通过 `/mcp`（会话内）或 `claude mcp list`（终端）检查状态，然后对照下表排查。** `/mcp` 面板也允许你在不离开会话的情况下重连或认证。

### /mcp 显示 No MCP servers configured

**Claude Code 在当前目录未找到任何 server。** 常见原因：

- 你在另一个项目中运行了 `claude mcp add`。local 作用域的 server 绑定到添加时所在的项目（仓库根目录，或非 git 仓库时的精确目录）。请在当前项目重新添加，或用 `--scope user` 使其不绑定项目。
- 配置文件路径错误。正确路径是 `~/.claude.json` 和 `<project>/.mcp.json`。Claude Code 不读取 `~/.claude/config/mcp.json`、`~/.claude/mcp.json` 或 `%APPDATA%\Claude\mcp.json` 等路径。

### 状态显示 Failed to connect 或 Connection error

**两种状态都表示 server 未启动或 URL 无响应。** 对于期望 token 而非浏览器登录的 HTTP server 也可能出现此状态。

从 v2.1.191 起，HTTP server 返回 `404 Not Found` 时，在 `/mcp` 中选择该 server 会显示 `MCP endpoint not found at <url>. Check the URL in your MCP config.` 及其尝试的 URL。早期版本只显示通用的 `Error POSTing to endpoint` 消息。将 URL 与 server 文档中的 MCP 端点路径对比，然后运行 `claude mcp remove <name>` 重新用正确 URL 添加。

**对于 HTTP server**，确认 URL 从你的机器可达：

```bash
curl -I https://mcp.sentry.dev/mcp
```

PowerShell 中使用 `curl.exe` 而非 `curl`，避免走到 `Invoke-WebRequest` 别名。

响应告诉你问题类型：

| 响应 | 含义 |
|------|------|
| `404` 或 `405` | server 在线。许多 MCP 端点只响应 POST，这仍然证明 URL 可达 |
| `401` 或 `403` | server 在线但需认证。用浏览器登录方式（见 [连接需要登录的 Server](#连接需要登录的-server)），或通过 `--header "Authorization: Bearer <token>"` 传入 token |
| 无响应 | 检查 URL 和网络 |

**对于 stdio server**，在终端中直接运行配置的命令查看底层错误。以 Playwright server 为例：

```bash
npx -y @playwright/mcp@latest
```

运行结果告诉你问题所在：

- **命令启动并等待输入**：server 本身正常。运行 `claude mcp get <name>` 确认其中显示的命令与你刚才执行的一致。如果不一致，可能是添加时遗漏了 `--` 分隔符。移除后重新添加。如果是手写 `.mcp.json`，检查语法和位置。
- **命令报错**：错误信息会指明缺少什么（如 Node.js 或浏览器）。

### 启动时连接超时

**server 启动时间超过默认的 30 秒超时限制。** stdio server 首次运行时 `npx` 下载包可能较慢。通过 [`MCP_TIMEOUT`](https://code.claude.com/docs/en/env-vars) 环境变量（单位毫秒）增加超时：

```bash
MCP_TIMEOUT=60000 claude
```

PowerShell 中在同一行设置变量：

```powershell
$env:MCP_TIMEOUT = "60000"; claude
```

### Server already exists

**同名 server 已存在于相同作用域。** 先移除现有条目或换个名称：

```bash
claude mcp remove claude-code-docs
```

如果同名存在于多个作用域，`remove` 会报 `exists in multiple scopes`。用 `--scope` 指定移除哪个，例如 `claude mcp remove claude-code-docs --scope local`。

### Server 已连接但无工具出现

**运行 `/mcp` 选中 server 查看工具列表。** 列表为空表示 server 启动了但未注册任何工具，通常是缺少必需的环境变量（如 API key）。

通过 `--env KEY=value` 传入变量，或在 `.mcp.json` 条目的 `env` 字段中设置。具体需要哪些变量请查阅 server 文档。

### .mcp.json 修改不生效

**Claude Code 在会话启动时读取 `.mcp.json`。** 编辑文件后需退出并重启会话。

如果 server 仍未出现，运行 `/mcp` 查看解析警告。Claude Code 会跳过格式错误的条目并在面板中显示问题字段。

如果你之前拒绝了 server 批准提示，重置项目审批：

```bash
claude mcp reset-project-choices
```

### OAuth 登录失败或浏览器未打开

运行 `/mcp`，选中 server，选择 `Authenticate` 重试。如果浏览器未自动打开，复制终端中显示的 URL 手动打开。更多信息见 [远程 MCP server 认证](https://code.claude.com/docs/en/mcp#authenticate-with-remote-mcp-servers)。

## 下一步

**一个 server 接入成功后，探索 MCP 的更多可能。**

- [查找更多 MCP Server](https://code.claude.com/docs/en/mcp#find-and-build-mcp-servers)：浏览 Anthropic 目录
- [与团队共享 Server](https://code.claude.com/docs/en/mcp#mcp-installation-scopes)：通过安装作用域管理
- [为组织管理 MCP 访问](https://code.claude.com/docs/en/managed-mcp)：托管设置和策略控制
- [引用 MCP 资源](https://code.claude.com/docs/en/mcp#use-mcp-resources)：在 prompt 中通过 @ 提及
- [将 MCP prompt 作为命令运行](https://code.claude.com/docs/en/mcp#use-mcp-prompts-as-commands)：从 `/` 菜单调用
- [构建自己的 Server](https://modelcontextprotocol.io/quickstart/server)：使用 MCP SDK
