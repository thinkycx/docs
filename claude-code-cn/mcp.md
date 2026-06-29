---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】MCP 工具连接
description: Claude Code 通过 MCP（Model Context Protocol）连接外部工具和数据源的完整指南，涵盖安装配置、认证授权、工具搜索、资源引用等核心功能。
category: translation
tags: [claude-code, mcp, translation]
refs:
  - https://code.claude.com/docs/en/mcp.md
---

# 通过 MCP 连接 Claude Code 与外部工具

> 了解如何通过 Model Context Protocol 将 Claude Code 接入你的工具生态。

**MCP 是连接 Claude Code 与外部工具的开放协议标准。** Claude Code 可以通过 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) 连接数百种外部工具和数据源。MCP server 让 Claude Code 能直接访问你的工具、数据库和 API。

当你发现自己不断从其他工具（如问题追踪器、监控面板）复制数据粘贴到对话中时，就应该考虑接入 MCP server。接入后，Claude 可以直接读取和操作这些系统，不再依赖你手动粘贴。

如果你是第一次接入 MCP server，建议先看 [MCP 快速开始](https://code.claude.com/docs/en/mcp-quickstart) 的手把手教程。本文是完整参考文档。

## MCP 能做什么

**接入 MCP server 后，Claude Code 可以直接操作外部系统完成复杂任务。** 你可以这样用：

| 场景 | 示例 Prompt |
|------|-------------|
| 从需求系统实现功能 | "Add the feature described in JIRA issue ENG-4521 and create a PR on GitHub." |
| 分析监控数据 | "Check Sentry and Statsig to check the usage of the feature described in ENG-4521." |
| 查询数据库 | "Find emails of 10 random users who used feature ENG-4521, based on our PostgreSQL database." |
| 集成设计稿 | "Update our standard email template based on the new Figma designs that were posted in Slack" |
| 自动化工作流 | "Create Gmail drafts inviting these 10 users to a feedback session about the new feature." |
| 响应外部事件 | MCP server 也可以作为 [channel](https://code.claude.com/docs/en/channels) 向会话推送消息，让 Claude 在你离开时响应 Telegram、Discord 或 webhook 事件 |

## 查找和构建 MCP Server

**Anthropic 官方目录提供经过审核的 MCP 连接器，也支持自建。** 在 [Anthropic Directory](https://claude.ai/directory) 浏览已审核的连接器。目录中的远程 server 与 Claude Code 使用相同的 MCP 基础设施，你可以直接用 `claude mcp add` 添加。

> **警告：** 接入前请确认你信任该 server。获取外部内容的 server 可能带来 [prompt 注入风险](https://code.claude.com/docs/en/security#protect-against-prompt-injection)。

要自建 MCP server，参见 [MCP server 构建指南](https://modelcontextprotocol.io/docs/develop/build-server)（协议基础）和 [Claude 连接器构建文档](https://claude.com/docs/connectors/building)（认证、测试和目录提交）。

也可以让 Claude 用官方 [`mcp-server-dev` 插件](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/mcp-server-dev) 帮你脚手架搭建一个 server：

**步骤 1：安装插件**

在 Claude Code 会话中运行：

```
/plugin install mcp-server-dev@claude-plugins-official
```

如果提示 marketplace 找不到，先运行 `/plugin marketplace add anthropics/claude-plugins-official`，再重试安装。安装完成后运行 `/reload-plugins` 在当前会话激活。

**步骤 2：运行构建技能**

```
/mcp-server-dev:build-mcp-server
```

Claude 会询问你的使用场景，然后搭建一个远程 HTTP 或本地 stdio server。

## 安装 MCP Server

**MCP server 有多种安装方式，根据需求选择不同传输协议。**

### 方式一：添加远程 HTTP server

**HTTP 是连接远程 MCP server 的推荐方式，** 也是云端服务最广泛支持的传输协议。

```bash
# 基本语法
claude mcp add --transport http <name> <url>

# 实例：连接 Notion
claude mcp add --transport http notion https://mcp.notion.com/mcp

# 带 Bearer token 的示例
claude mcp add --transport http secure-api https://api.example.com/mcp \
  --header "Authorization: Bearer your-token"
```

在 `.mcp.json`、`~/.claude.json` 或 `claude mcp add-json` 的 JSON 配置中，`type` 字段接受 `streamable-http` 作为 `http` 的别名。MCP 规范中使用 `streamable-http` 这个名称，所以从 server 文档复制的配置无需修改即可使用。

### 方式二：添加远程 SSE server

> **警告：** SSE（Server-Sent Events）传输协议已弃用，优先使用 HTTP server。

```bash
# 基本语法
claude mcp add --transport sse <name> <url>

# 实例：连接 Asana
claude mcp add --transport sse asana https://mcp.asana.com/sse

# 带认证头的示例
claude mcp add --transport sse private-api https://api.company.com/sse \
  --header "X-API-Key: your-key-here"
```

### 方式三：添加本地 stdio server

**stdio server 以本地进程运行，适合需要直接系统访问或自定义脚本的场景。**

Claude Code 会在启动的 server 环境中设置 `CLAUDE_PROJECT_DIR` 变量，指向项目根目录，让你的 server 能解析项目相对路径而无需依赖工作目录。这和 hooks 收到的 `CLAUDE_PROJECT_DIR` 是同一个目录。在 server 内部读取即可，例如 Node 中用 `process.env.CLAUDE_PROJECT_DIR`，Python 中用 `os.environ["CLAUDE_PROJECT_DIR"]`。

server 也可以调用 MCP 的 `roots/list` 请求来获取 Claude Code 的启动目录。

该变量设置在 server 的环境中，而不是 Claude Code 自身的环境中。因此在项目级或用户级 `.mcp.json` 的 `command` 或 `args` 中通过 `${VAR}` 展开引用时需要设默认值，如 `${CLAUDE_PROJECT_DIR:-.}`。插件提供的 MCP 配置会直接替换 `${CLAUDE_PROJECT_DIR}`，不需要默认值。

```bash
# 基本语法
claude mcp add [options] <name> -- <command> [args...]

# 实例：添加 Airtable server
claude mcp add --env AIRTABLE_API_KEY=YOUR_KEY --transport stdio airtable \
  -- npx -y airtable-mcp-server
```

> **重要：用 `--` 分隔 server 参数**
>
> 对于 stdio server，`--`（双短线）将 Claude 自身的选项（如 `--transport`、`--env`、`--scope`）与 server 的命令和参数分开。`--` 之后的所有内容原样传递给 server。
>
> 示例：
> - `claude mcp add --transport stdio myserver -- npx server` → 运行 `npx server`
> - `claude mcp add --env KEY=value --transport stdio myserver -- python server.py --port 8080` → 在环境变量 `KEY=value` 下运行 `python server.py --port 8080`
>
> 如果不加 `--`，Claude Code 会尝试将 server 的参数（如上面的 `--port`）解析为自身的选项。
>
> `--env` 接受多个 `KEY=value` 对。如果 server 名称紧跟 `--env` 后面，CLI 会将其读取为另一个键值对并报错，所以要在 `--env` 和 server 名称之间放至少一个其他选项（如示例所示）。

### 方式四：添加远程 WebSocket server

**WebSocket 保持持久双向连接，适合需要主动推送事件的远程 MCP server。** 如果你的 server 只是响应请求，应优先使用 HTTP（HTTP 支持 OAuth 和 `claude mcp add --transport` 标志，WebSocket 不支持）。

通过 `.mcp.json` 或 `claude mcp add-json` 配置 WebSocket server：

```bash
claude mcp add-json events-server \
  '{"type":"ws","url":"wss://mcp.example.com/socket","headers":{"Authorization":"Bearer YOUR_TOKEN"}}'
```

`type: "ws"` 条目支持与 `http` 相同的 `url`、`headers`、`headersHelper`、`timeout` 和 `alwaysLoad` 字段。认证仅通过 header 实现，可以在 `headers` 中传递静态 token，或用 [`headersHelper`](#使用动态-header-进行自定义认证) 在连接时动态生成。`claude mcp add --transport` 标志不接受 `ws`。

### 管理 Server

**安装后的 server 通过命令行统一管理。**

```bash
# 列出所有配置的 server
claude mcp list

# 查看指定 server 详情
claude mcp get github

# 删除一个 server
claude mcp remove github

# （在 Claude Code 内部）检查 server 状态
/mcp
```

项目级 `.mcp.json` 中等待审批的 server 在 `claude mcp list` 中显示为 `⏸ Pending approval`。需要进入 Claude Code 交互模式审核并批准。`claude mcp get <name>` 对 pending 的 server 显示 `⏸ Pending approval`，对已拒绝的显示 `✗ Rejected`。

`/mcp` 面板在每个已连接 server 旁显示工具数量，并标记声明了 tools 能力但未暴露任何工具的 server。

如果你的请求需要用到某个仍在后台连接的 server 的工具，Claude 会等待该 server 连接完成。开启 [工具搜索](#通过-mcp-工具搜索扩展规模) 时（默认开启），等待发生在 `ToolSearch` 调用内部。在不支持工具搜索的配置中（如 Vertex AI、自定义 `ANTHROPIC_BASE_URL`、或 `ENABLE_TOOL_SEARCH=false`），Claude 改用 `WaitForMcpServers` 工具。

server 名称 `workspace` 为内部保留。如果你的配置定义了该名称的 server，Claude Code 在加载时跳过它并显示重命名警告。

### 动态工具更新

**Claude Code 支持 MCP `list_changed` 通知。** MCP server 可以动态更新可用工具、prompts 和资源，无需断开再重连。当 server 发送 `list_changed` 通知时，Claude Code 自动刷新该 server 的可用能力。

### 自动重连

**HTTP 和 SSE server 断线后会自动指数退避重连。** 最多 5 次尝试，从 1 秒延迟开始每次翻倍。重连期间 server 在 `/mcp` 中显示为 pending 状态。5 次失败后标记为 failed，可从 `/mcp` 手动重试。stdio server 是本地进程，不会自动重连。

初始启动连接失败时也适用相同退避策略。从 v2.1.121 起，初始连接在瞬时错误（5xx 响应、连接拒绝、超时）时最多重试 3 次，之后标记 failed。认证错误和 not-found 错误不重试，因为需要修改配置才能解决。

从 v2.1.191 起，成功连接后的能力发现请求（如 `tools/list`、`prompts/list`、`resources/list`）也对瞬时网络和服务器错误进行最多 3 次短退避重试。认证错误、4xx 响应和请求超时不重试。

### 通过 Channel 推送消息

**MCP server 可以主动向会话推送消息，让 Claude 响应 CI 结果、监控告警或聊天消息等外部事件。** 要启用此功能，server 需声明 `claude/channel` 能力，启动时用 `--channels` 标志选择加入。详见 [Channels](https://code.claude.com/docs/en/channels)（使用官方支持的 channel）或 [Channels 参考](https://code.claude.com/docs/en/channels-reference)（自建 channel）。

### 实用提示

| 提示 | 说明 |
|------|------|
| `--scope` 标志 | `local`（默认）：仅当前项目可见，旧版叫 `project`；`project`：通过 `.mcp.json` 共享给团队；`user`：所有项目可见，旧版叫 `global` |
| 环境变量 | 用 `--env` 设置，如 `--env KEY=value` |
| 启动超时 | 用 `MCP_TIMEOUT` 环境变量配置，如 `MCP_TIMEOUT=10000 claude` 设为 10 秒 |
| 单 server 工具超时 | 在 `.mcp.json` 中添加 `timeout` 字段（毫秒），如 `"timeout": 600000` 为 10 分钟，覆盖 `MCP_TOOL_TIMEOUT` |
| 输出 token 限制 | Claude Code 在 MCP 工具输出超过 10,000 token 时显示警告，用 `MAX_MCP_OUTPUT_TOKENS` 调整上限（如 `MAX_MCP_OUTPUT_TOKENS=50000`） |
| OAuth 认证 | 用 `/mcp` 对需要 OAuth 2.0 认证的远程 server 进行认证 |

每个 server 的 `timeout` 是每次工具调用的硬性时间上限，server 的 progress 通知不会延长。低于 1000 的值会被忽略并回退到 `MCP_TOOL_TIMEOUT`，若该变量也未设置则默认约 28 小时。v2.1.162 之前低于 1000 的值会被下限为 1 秒。

HTTP 和 SSE server 的每请求首字节超时下限为 60 秒。

从 v2.1.187 起，远程（HTTP、SSE、WebSocket 或 claude.ai 连接器）server 的工具调用如果 5 分钟内无响应且无 progress 通知，将中止并报错，而不是等到时间上限。通过 [`CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT`](https://code.claude.com/docs/en/env-vars) 环境变量设置空闲窗口（毫秒），设为 `0` 可禁用。stdio server 是本地进程，不受空闲超时限制。

### 插件提供的 MCP Server

**[插件](https://code.claude.com/docs/en/plugins) 可以捆绑 MCP server，启用插件时自动提供工具和集成。** 插件 MCP server 的工作方式与用户手动配置的完全一致。

**工作原理：**
- 插件在根目录的 `.mcp.json` 或 `plugin.json` 内联定义 MCP server
- 插件启用后，其 MCP server 自动启动
- 插件 MCP 工具与手动配置的 MCP 工具并列显示
- 通过插件安装管理 server，不通过 `/mcp` 命令

**示例配置：**

插件根目录的 `.mcp.json`：

```json
{
  "mcpServers": {
    "database-tools": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/db-server",
      "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"],
      "env": {
        "DB_URL": "${DB_URL}"
      }
    }
  }
}
```

或在 `plugin.json` 内联：

```json
{
  "name": "my-plugin",
  "mcpServers": {
    "plugin-api": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/api-server",
      "args": ["--port", "8080"]
    }
  }
}
```

**插件 MCP 特性：**

| 特性 | 说明 |
|------|------|
| 自动生命周期 | 会话启动时已启用插件的 server 自动连接；会话中启用/禁用插件后运行 `/reload-plugins` 连接/断开 |
| 环境变量 | `${CLAUDE_PLUGIN_ROOT}` 指向插件文件，`${CLAUDE_PLUGIN_DATA}` 用于 [持久化状态](https://code.claude.com/docs/en/plugins-reference#persistent-data-directory)（跨插件更新保留），`${CLAUDE_PROJECT_DIR}` 指向项目根目录 |
| 用户环境访问 | 可访问与手动配置 server 相同的环境变量 |
| 多传输类型 | 支持 stdio、SSE、HTTP 和 WebSocket |

**查看插件 MCP server：**

```bash
# 在 Claude Code 内查看所有 MCP server（包括插件的）
/mcp
```

插件 server 在列表中带有来源标识。

**插件 MCP 工具命名：**

来自插件捆绑 MCP server 的工具名称包含插件名和 server key。完整格式为 `mcp__plugin_<plugin-name>_<server-name>__<tool-name>`，其中 `A-Z`、`a-z`、`0-9`、`_`、`-` 之外的字符替换为 `_`。例如 `my-plugin` 插件的 `database-tools` server 中的 `query` 工具，全名为：

```
mcp__plugin_my-plugin_database-tools__query
```

在 [权限规则](https://code.claude.com/docs/en/permissions)、skill 的 `allowed-tools` 列表或 [子代理的 `tools` 字段](https://code.claude.com/docs/en/sub-agents#available-tools) 中引用工具时使用此全名。

**插件 MCP server 的优势：**
- 工具和 server 捆绑分发
- 无需手动 MCP 配置即可自动设置
- 团队成员安装插件后获得一致的工具集

详见 [插件组件参考](https://code.claude.com/docs/en/plugins-reference#mcp-servers)。

## MCP 安装作用域

**MCP server 可在三个作用域配置，决定加载范围和团队共享方式。** 管理员还可以通过 [托管配置](#托管-mcp-配置) 在企业层面部署。

| 作用域 | 加载范围 | 是否共享给团队 | 存储位置 |
|--------|----------|---------------|----------|
| [Local](#local-作用域) | 仅当前项目 | 否 | `~/.claude.json` |
| [Project](#project-作用域) | 仅当前项目 | 是（通过版本控制） | 项目根目录 `.mcp.json` |
| [User](#user-作用域) | 所有项目 | 否 | `~/.claude.json` |

### Local 作用域

**Local 是默认作用域。** server 仅在添加它的项目中加载，对你私有。Claude Code 将其存储在 `~/.claude.json` 中该项目路径下，不会出现在其他项目中。适用于个人开发 server、实验性配置，或带有不想纳入版本控制的凭证的 server。

> **注意：** MCP server 的 "local scope" 与一般的 local settings 不同。MCP local 作用域 server 存储在 `~/.claude.json`（用户主目录），而一般 local settings 使用 `.claude/settings.local.json`（项目目录）。详见 [Settings](https://code.claude.com/docs/en/settings#settings-files)。

```bash
# 添加 local 作用域 server（默认）
claude mcp add --transport http stripe https://mcp.stripe.com

# 显式指定 local 作用域
claude mcp add --transport http stripe --scope local https://mcp.stripe.com
```

命令将 server 写入 `~/.claude.json` 中当前项目的条目下。在 `/path/to/your/project` 目录运行后的结果：

```json
{
  "projects": {
    "/path/to/your/project": {
      "mcpServers": {
        "stripe": {
          "type": "http",
          "url": "https://mcp.stripe.com"
        }
      }
    }
  }
}
```

### Project 作用域

**Project 作用域通过 `.mcp.json` 实现团队协作。** 配置存储在项目根目录的 `.mcp.json` 文件中，适合纳入版本控制以确保团队成员使用相同的 MCP 工具和服务。

```bash
# 添加 project 作用域 server
claude mcp add --transport http paypal --scope project https://mcp.paypal.com/mcp
```

生成的 `.mcp.json` 格式：

```json
{
  "mcpServers": {
    "shared-server": {
      "command": "/path/to/server",
      "args": [],
      "env": {}
    }
  }
}
```

出于安全考虑，Claude Code 在使用 `.mcp.json` 中的 project 作用域 server 前会请求审批。如需重置审批选择，使用 `claude mcp reset-project-choices` 命令。

### User 作用域

**User 作用域 server 跨项目可用。** 存储在 `~/.claude.json` 中，对你所有项目可用但保持私有。适合常用的个人工具和服务。

```bash
# 添加 user server
claude mcp add --transport http hubspot --scope user https://mcp.hubspot.com/anthropic
```

### 作用域层级和优先级

**同一 server 在多处定义时，Claude Code 使用最高优先级来源的定义，不会跨作用域合并字段。**

1. Local 作用域
2. Project 作用域
3. User 作用域
4. [插件提供的 server](https://code.claude.com/docs/en/plugins)
5. [claude.ai 连接器](#使用-claudeai-的-mcp-server)

三个作用域按名称匹配重复项。插件和连接器按 endpoint 匹配，指向相同 URL 或命令的视为重复。

### `.mcp.json` 中的环境变量展开

**Claude Code 支持在 `.mcp.json` 中展开环境变量。** 团队可以共享配置同时保留机器特定路径和 API key 等敏感值的灵活性。

**支持的语法：**
- `${VAR}`：展开为环境变量 `VAR` 的值
- `${VAR:-default}`：`VAR` 有值时使用其值，否则使用 `default`

**展开位置：** `command`（server 可执行路径）、`args`（命令行参数）、`env`（传递给 server 的环境变量）、`url`（HTTP server）、`headers`（HTTP server 认证）

**带变量展开的示例：**

```json
{
  "mcpServers": {
    "api-server": {
      "type": "http",
      "url": "${API_BASE_URL:-https://api.example.com}/mcp",
      "headers": {
        "Authorization": "Bearer ${API_KEY}"
      }
    }
  }
}
```

如果必需的环境变量未设置且没有默认值，Claude Code 无法解析配置。

## 实用示例

### 示例：用 Sentry 监控错误

```bash
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp
```

用 Sentry 账号认证：

```
/mcp
```

然后排查生产问题：

```
What are the most common errors in the last 24 hours?
```

```
Show me the stack trace for error ID abc123
```

```
Which deployment introduced these new errors?
```

### 示例：连接 GitHub 做代码审查

**GitHub 远程 MCP server 通过 header 传递 personal access token 认证。** 打开 [GitHub token 设置](https://github.com/settings/personal-access-tokens)，生成一个有目标仓库权限的 fine-grained token，然后添加 server：

```bash
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ \
  --header "Authorization: Bearer YOUR_GITHUB_PAT"
```

然后操作 GitHub：

```
Review PR #456 and suggest improvements
```

```
Create a new issue for the bug we just found
```

```
Show me all open PRs assigned to me
```

### 示例：查询 PostgreSQL 数据库

```bash
claude mcp add --transport stdio db -- npx -y @bytebase/dbhub \
  --dsn "postgresql://readonly:pass@prod.db.com:5432/analytics"
```

然后自然语言查询：

```
What's our total revenue this month?
```

```
Show me the schema for the orders table
```

```
Find customers who haven't made a purchase in 90 days
```

## 远程 MCP Server 认证

**许多云端 MCP server 需要认证，Claude Code 支持 OAuth 2.0 安全连接。**

当远程 server 响应 `401 Unauthorized` 或 `403 Forbidden` 时，Claude Code 将其标记为需要认证，在 `/mcp` 中提示你完成 OAuth 流程。返回 `WWW-Authenticate` header 指向授权服务器的自定义 server 也能自动发现。

如果你配置了 `headers.Authorization` 但 server 拒绝了该 header，Claude Code 将连接报告为 failed 而非回退到 OAuth。检查 token 对 MCP endpoint 是否有效，或移除 header 使用 OAuth 流程。

**步骤 1：添加需要认证的 server**

```bash
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp
```

**步骤 2：在 Claude Code 中认证**

```
/mcp
```

然后在浏览器中完成登录。

**认证提示：**
- token 安全存储并自动刷新
- 在 `/mcp` 菜单中用 "Clear authentication" 撤销访问
- 浏览器未自动打开时，复制 URL 手动打开
- 浏览器重定向失败时，将浏览器地址栏中的完整回调 URL 粘贴到 Claude Code 出现的 URL 提示中
- OAuth 认证适用于 HTTP server

### 从命令行认证

**从 v2.1.186 起，`claude mcp login <name>` 可直接在 shell 中完成 OAuth 流程。** 无需打开 `/mcp` 面板。

```bash
claude mcp login sentry
```

清除凭据用 `claude mcp logout <name>`。

从 v2.1.191 起，当无法打开本地浏览器时（如 SSH 会话或无显示服务器的 Linux），命令会打印 URL 而非尝试打开浏览器。在本地机器打开该 URL，然后将重定向 URL 粘贴回命令行。需要交互式终端，所以用 `ssh -t` 连接。用 `--no-browser` 强制 URL 提示模式：

```bash
claude mcp login sentry --no-browser
```

### 使用固定 OAuth 回调端口

**部分 MCP server 需要预注册的特定 redirect URI。** 默认情况下 Claude Code 为 OAuth 回调选择随机可用端口。用 `--callback-port` 固定端口以匹配预注册的 `http://localhost:PORT/callback` 格式 redirect URI。

可以单独使用 `--callback-port`（动态客户端注册）或与 `--client-id` 一起使用（预配置凭据）。

```bash
# 固定回调端口 + 动态客户端注册
claude mcp add --transport http \
  --callback-port 8080 \
  my-server https://mcp.example.com/mcp
```

### 使用预配置的 OAuth 凭据

**部分 MCP server 不支持动态客户端注册（Dynamic Client Registration）。** 如果遇到 "Incompatible auth server: does not support dynamic client registration" 错误，说明 server 需要预配置凭据。Claude Code 也支持使用 Client ID Metadata Document (CIMD) 的 server 并能自动发现。自动发现失败时，先通过 server 的开发者门户注册 OAuth 应用，再提供凭据。

**步骤 1：在 server 端注册 OAuth 应用**

通过 server 的开发者门户创建应用，记下 client ID 和 client secret。如果需要 redirect URI，选择一个端口并注册 `http://localhost:PORT/callback` 格式的 URI，在下一步用相同端口。

**步骤 2：添加 server 并提供凭据**

方法一：`claude mcp add`

```bash
claude mcp add --transport http \
  --client-id your-client-id --client-secret --callback-port 8080 \
  my-server https://mcp.example.com/mcp
```

方法二：`claude mcp add-json`

```bash
claude mcp add-json my-server \
  '{"type":"http","url":"https://mcp.example.com/mcp","oauth":{"clientId":"your-client-id","callbackPort":8080}}' \
  --client-secret
```

方法三：仅固定回调端口（动态客户端注册）

```bash
claude mcp add-json my-server \
  '{"type":"http","url":"https://mcp.example.com/mcp","oauth":{"callbackPort":8080}}'
```

方法四：CI / 环境变量方式（跳过交互提示）

```bash
MCP_CLIENT_SECRET=your-secret claude mcp add --transport http \
  --client-id your-client-id --client-secret --callback-port 8080 \
  my-server https://mcp.example.com/mcp
```

**步骤 3：在 Claude Code 中认证**

运行 `/mcp` 并完成浏览器登录流程。

**提示：**
- client secret 安全存储在系统钥匙串（macOS）或凭据文件中，不在配置中
- 公开 OAuth 客户端无 secret 时，只用 `--client-id` 不加 `--client-secret`
- `--callback-port` 可以搭配或不搭配 `--client-id` 使用
- 这些标志仅适用于 HTTP 和 SSE 传输，对 stdio server 无效
- 用 `claude mcp get <name>` 验证 server 是否配置了 OAuth 凭据

### 覆盖 OAuth 元数据发现

**用 `authServerMetadataUrl` 指向特定的 OAuth 授权服务器元数据 URL，跳过默认发现链。** 当 MCP server 的标准 endpoint 出错，或想通过内部代理路由发现时使用。默认情况下 Claude Code 先检查 RFC 9728 Protected Resource Metadata (`/.well-known/oauth-protected-resource`)，再回退到 RFC 8414 授权服务器元数据 (`/.well-known/oauth-authorization-server`)。

在 `.mcp.json` 中 server 配置的 `oauth` 对象内设置：

```json
{
  "mcpServers": {
    "my-server": {
      "type": "http",
      "url": "https://mcp.example.com/mcp",
      "oauth": {
        "authServerMetadataUrl": "https://auth.example.com/.well-known/openid-configuration"
      }
    }
  }
}
```

URL 必须使用 `https://`。需要 Claude Code v2.1.64 或更高版本。元数据 URL 的 `scopes_supported` 会覆盖上游 server 声明的 scopes。

### 限制 OAuth Scopes

**用 `oauth.scopes` 固定 Claude Code 在授权流程中请求的 scopes。** 这是将 MCP server 限制为安全团队批准的子集的正式方式。值为空格分隔的字符串，匹配 RFC 6749 §3.3 的 `scope` 参数格式。

```json
{
  "mcpServers": {
    "slack": {
      "type": "http",
      "url": "https://mcp.slack.com/mcp",
      "oauth": {
        "scopes": "channels:read chat:write search:read"
      }
    }
  }
}
```

`oauth.scopes` 优先于 `authServerMetadataUrl` 和 server 在 `/.well-known` 发现的 scopes。不设置则由 MCP server 决定请求的 scope 集合。

如果授权服务器在 `scopes_supported` 中声明了 `offline_access`，Claude Code 会将其附加到固定 scopes，以便 access token 可以在无需新的浏览器登录的情况下刷新。

如果 server 后续对工具调用返回 403 `insufficient_scope`，Claude Code 使用相同固定 scopes 重新认证。需要固定集合之外的 scope 时，扩展 `oauth.scopes`。

### 使用动态 Header 进行自定义认证

**如果 MCP server 使用 OAuth 之外的认证方案（如 Kerberos、短期 token 或内部 SSO），用 `headersHelper` 在连接时动态生成 header。** Claude Code 运行该命令并将输出合并到连接 header 中。

```json
{
  "mcpServers": {
    "internal-api": {
      "type": "http",
      "url": "https://mcp.internal.example.com",
      "headersHelper": "/opt/bin/get-mcp-auth-headers.sh"
    }
  }
}
```

也可以内联命令：

```json
{
  "mcpServers": {
    "internal-api": {
      "type": "http",
      "url": "https://mcp.internal.example.com",
      "headersHelper": "echo '{\"Authorization\": \"Bearer '\"$(get-token)\"'\"}'"
    }
  }
}
```

**要求：**
- 命令必须向 stdout 输出 JSON 对象（字符串键值对）
- 命令在 shell 中运行，10 秒超时
- 动态 header 覆盖同名的静态 `headers`

helper 在每次连接时（会话启动和重连）重新执行，不做缓存，token 复用由你的脚本负责。

Claude Code 执行 helper 时设置以下环境变量：

| 变量 | 值 |
|------|-----|
| `CLAUDE_CODE_MCP_SERVER_NAME` | MCP server 的名称 |
| `CLAUDE_CODE_MCP_SERVER_URL` | MCP server 的 URL |

用这些变量可以写一个 helper 脚本服务多个 MCP server。

> **注意：** `headersHelper` 执行任意 shell 命令。在 project 或 local 作用域定义时，仅在接受工作区信任对话框后才运行。

## 通过 JSON 配置添加 MCP Server

**如果你有现成的 JSON 配置，可以直接导入。**

```bash
# 基本语法
claude mcp add-json <name> '<json>'

# 示例：用 JSON 配置添加 HTTP server
claude mcp add-json weather-api '{"type":"http","url":"https://api.weather.com/mcp","headers":{"Authorization":"Bearer token"}}'

# 示例：用 JSON 配置添加 stdio server
claude mcp add-json local-weather '{"type":"stdio","command":"/path/to/weather-cli","args":["--api-key","abc123"],"env":{"CACHE_DIR":"/tmp"}}'

# 示例：带预配置 OAuth 凭据的 HTTP server
claude mcp add-json my-server '{"type":"http","url":"https://mcp.example.com/mcp","oauth":{"clientId":"your-client-id","callbackPort":8080}}' --client-secret
```

验证添加成功：

```bash
claude mcp get weather-api
```

**提示：**
- 确保 JSON 在 shell 中正确转义
- JSON 必须符合 MCP server 配置 schema
- 用 `--scope user` 添加到用户配置而非项目配置

## 从 Claude Desktop 导入 MCP Server

**如果你已在 Claude Desktop 配置过 MCP server，可以一键导入。**

```bash
# 导入
claude mcp add-from-claude-desktop

# 选择要导入的 server（交互式）
# 验证导入结果
claude mcp list
```

**提示：**
- 仅支持 macOS 和 Windows Subsystem for Linux (WSL)
- 从 Claude Desktop 标准配置路径读取
- 用 `--scope user` 添加到用户配置
- 保留 Claude Desktop 中的原始名称
- 同名 server 已存在时自动加数字后缀（如 `server_1`）

## 使用 claude.ai 的 MCP Server

**如果用 claude.ai 账号登录了 Claude Code，在 claude.ai 添加的 MCP server 自动可用。**

**步骤 1：** 在 [claude.ai/customize/connectors](https://claude.ai/customize/connectors) 配置 MCP server。Team 和 Enterprise 计划仅管理员可添加。

**步骤 2：** 在 claude.ai 完成所有认证步骤。

**步骤 3：** 在 Claude Code 中用 `/mcp` 查看和管理。来自 claude.ai 的 server 带有来源标识。

从 v2.1.161 起，你从未登录的连接器折叠在 claude.ai 部分末尾的 `Show unused connectors` 行中，避免组织配置的长列表占满面板。选择该行展开。曾登录的连接器即使当前需要重新认证也保持可见。

claude.ai 连接器仅在活跃 [认证方式](https://code.claude.com/docs/en/authentication#authentication-precedence) 为 claude.ai 订阅时加载。当 `ANTHROPIC_API_KEY`、`ANTHROPIC_AUTH_TOKEN`、`apiKeyHelper` 或第三方提供商（Bedrock、Vertex）激活时不加载，即使之前运行过 `/login`。

如果 `/mcp` 未列出你添加的连接器，运行 `/status` 确认当前认证方式，取消设置相关环境变量或移除 `apiKeyHelper`，再运行 `/login` 选择 claude.ai 账号。

你在 Claude Code 中添加的 server 对指向相同 URL 的 claude.ai 连接器有 [更高优先级](#作用域层级和优先级)。此时 `/mcp` 将连接器显示为 hidden 并说明如何移除重复项。

部分 Anthropic 托管的连接器（如 Microsoft 365、Gmail、Google Calendar）不支持从 Claude Code 本地 OAuth，因为上游身份提供商只接受 claude.ai 注册的 redirect URL。从 v2.1.162 起，在 `/mcp` 中认证这些主机时会提示前往 claude.ai 的 Settings → Connectors 连接。在那里连接后，连接器自动出现在 Claude Code 中。

### 禁用 claude.ai 连接器

在任意 settings 作用域中设置 [`disableClaudeAiConnectors`](https://code.claude.com/docs/en/settings#available-settings) 为 `true`：

```json
{
  "disableClaudeAiConnectors": true
}
```

此设置使用 any-source-true 语义：任何来源的 `true` 具有最高优先级。项目级 `.claude/settings.json` 可以选择退出云连接器，但项目级 `false` 无法重新启用被用户级或策略级 `true` 禁用的连接器。通过 `--mcp-config` 显式传递的 server 不受影响。

也可以设置环境变量，效果相同：

```bash
ENABLE_CLAUDEAI_MCP_SERVERS=false claude
```

要阻止单个连接器而非全部，将其添加到 [`deniedMcpServers`](https://code.claude.com/docs/en/managed-mcp) 中（按名称或 URL 模式）。例如 `serverName` 条目 `"claude.ai Slack"` 阻止 Slack 连接器。要仅在当前项目切换连接器开关，使用 `/mcp` 面板。

> **注意：** 这些客户端设置适用于本地 Claude Code 会话。在 [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web) 会话中，claude.ai 连接器由远程主机配置并作为显式 `--mcp-config` 条目到达，`disableClaudeAiConnectors` 不适用。连接器 URL 也通过会话代理重写，因此针对供应商 URL 的 `deniedMcpServers` `serverUrl` 模式不会匹配。从 claude.ai 组织设置管理云会话可用的连接器。

## 将 Claude Code 作为 MCP Server 使用

**Claude Code 本身也可以作为 MCP server 供其他应用连接。**

```bash
# 以 stdio MCP server 模式启动 Claude
claude mcp serve
```

在 Claude Desktop 的 `claude_desktop_config.json` 中添加配置：

```json
{
  "mcpServers": {
    "claude-code": {
      "type": "stdio",
      "command": "claude",
      "args": ["mcp", "serve"],
      "env": {}
    }
  }
}
```

> **警告：** `command` 字段必须引用 Claude Code 可执行文件。如果 `claude` 不在系统 PATH 中，需要指定完整路径。
>
> 查找完整路径：`which claude`
>
> 使用完整路径：
> ```json
> {
>   "mcpServers": {
>     "claude-code": {
>       "type": "stdio",
>       "command": "/full/path/to/claude",
>       "args": ["mcp", "serve"],
>       "env": {}
>     }
>   }
> }
> ```
>
> 路径不正确会遇到 `spawn claude ENOENT` 错误。

**提示：**
- server 暴露 Claude 的工具如 View、Edit、LS 等
- 在 Claude Desktop 中可以让 Claude 读取目录文件、做编辑等
- 此 MCP server 仅向你的 MCP 客户端暴露 Claude Code 的工具，各工具调用的用户确认由你的客户端负责

## MCP 输出限制和警告

**当 MCP 工具产生大量输出时，Claude Code 帮助管理 token 用量以防上下文溢出。**

| 项目 | 说明 |
|------|------|
| 输出警告阈值 | MCP 工具输出超过 10,000 token 时显示警告 |
| 可配置限制 | 用 `MAX_MCP_OUTPUT_TOKENS` 环境变量调整最大允许值 |
| 默认限制 | 25,000 token |
| 作用域 | 该变量适用于未声明自身限制的工具。声明了 [`anthropic/maxResultSizeChars`](#提升单个工具的限制) 的工具使用其自身值（文本内容），不受 `MAX_MCP_OUTPUT_TOKENS` 影响。返回图片数据的工具仍受该变量限制 |

```bash
export MAX_MCP_OUTPUT_TOKENS=50000
claude
```

适用于查询大数据集/数据库、生成详细报告/文档、处理大量日志的 MCP server。

### 提升单个工具的限制

**如果你在构建 MCP server，可以通过 `_meta["anthropic/maxResultSizeChars"]` 让单个工具返回超过默认持久化阈值的结果。** Claude Code 将该工具的阈值提升到标注值，硬上限 500,000 字符。

适用于返回天然较大但必需输出的工具（如数据库 schema 或完整文件树）。不加标注时，超过默认阈值的结果会持久化到磁盘并在对话中替换为文件引用。

```json
{
  "name": "get_schema",
  "description": "Returns the full database schema",
  "_meta": {
    "anthropic/maxResultSizeChars": 200000
  }
}
```

标注独立于 `MAX_MCP_OUTPUT_TOKENS` 作用于文本内容，用户无需为声明了该标注的工具提高环境变量。返回图片的工具仍受 token 限制。

> **警告：** 如果你频繁遇到不受你控制的 MCP server 的输出警告，考虑提高 `MAX_MCP_OUTPUT_TOKENS`。也可以请求 server 作者添加 `anthropic/maxResultSizeChars` 标注或分页响应。该标注对返回图片的工具无效，对那些只能提高 `MAX_MCP_OUTPUT_TOKENS`。

## 响应 MCP Elicitation 请求

**MCP server 可以在任务执行中请求你的结构化输入。** 当 server 需要自己无法获取的信息时，Claude Code 显示交互对话框并将你的回应传回 server。无需你做配置，对话框在 server 请求时自动出现。

server 可以通过两种方式请求输入：
- **表单模式：** Claude Code 显示带有 server 定义字段的对话框（如用户名和密码），填写并提交
- **URL 模式：** Claude Code 打开浏览器 URL 进行认证或审批，在浏览器完成后在 CLI 确认

要自动响应 elicitation 请求而不显示对话框，使用 [`Elicitation` hook](https://code.claude.com/docs/en/hooks#elicitation)。

如果你在构建使用 elicitation 的 MCP server，参见 [MCP elicitation 规范](https://modelcontextprotocol.io/docs/learn/client-concepts#elicitation)。

## 使用 MCP Resources

**MCP server 可以暴露资源，你可以用 @ 提及来引用，类似引用文件。**

### 引用 MCP 资源

**步骤 1：** 在 prompt 中输入 `@` 查看所有已连接 MCP server 的可用资源。资源与文件一起出现在自动补全菜单中。

**步骤 2：** 用 `@server:protocol://resource/path` 格式引用：

```
Can you analyze @github:issue://123 and suggest a fix?
```

```
Please review the API documentation at @docs:file://api/authentication
```

**步骤 3：** 单个 prompt 中可引用多个资源：

```
Compare @postgres:schema://users with @docs:file://database/user-model
```

**提示：**
- 引用的资源自动获取并作为附件包含
- 资源路径在 @ 提及自动补全中可模糊搜索
- 当 server 支持时，Claude Code 自动提供列出和读取 MCP 资源的工具
- 资源可以包含任何类型的内容（文本、JSON、结构化数据等）

## 通过 MCP 工具搜索扩展规模

**工具搜索通过延迟加载工具定义保持低 MCP 上下文占用。** 会话启动时只加载工具名称和 server 说明，添加更多 MCP server 对上下文窗口的影响很小。Claude Code 不设固定的每 server 工具上限，实际限制取决于上下文窗口预算。

### 工作原理

**工具搜索默认开启。** MCP 工具被延迟加载而非预先放入上下文，Claude 在任务需要时用搜索工具发现相关工具。只有实际使用的工具进入上下文。从你的角度看，MCP 工具的使用方式完全不变。

如果偏好基于阈值的加载方式，设置 `ENABLE_TOOL_SEARCH=auto` 在 schema 占用低于上下文窗口 10% 时预加载，溢出部分才延迟。详见 [配置工具搜索](#配置工具搜索)。

### MCP Server 作者须知

**如果你在构建 MCP server，server instructions 字段在工具搜索启用时更加重要。** server instructions 帮助 Claude 理解何时搜索你的工具，类似 [skills](https://code.claude.com/docs/en/skills) 的工作方式。

添加清晰的 server instructions 说明：
- 工具处理哪类任务
- Claude 何时应搜索你的工具
- server 提供的关键能力

Claude Code 将工具描述和 server instructions 各截断为 2KB。保持简洁避免截断，关键细节放在开头。

### 配置工具搜索

**工具搜索默认开启，MCP 工具延迟加载按需发现。** Vertex AI 上默认禁用。当 `ANTHROPIC_BASE_URL` 指向非第一方主机时也禁用（多数代理不转发 `tool_reference` 块）。显式设置 `ENABLE_TOOL_SEARCH` 可覆盖回退行为。

工具搜索需要支持 `tool_reference` 块的模型。Haiku 模型不支持。Vertex AI 上支持 Claude Sonnet 4.5 及更高、Claude Opus 4.5 及更高版本。

通过 `ENABLE_TOOL_SEARCH` 环境变量控制：

| 值 | 行为 |
|------|------|
| （未设置） | 所有 MCP 工具延迟按需加载。在 Vertex AI 或 `ANTHROPIC_BASE_URL` 为非第一方主机时回退为预加载 |
| `true` | 所有 MCP 工具延迟。即使在 Vertex AI 和代理上也发送 beta header。在低于 Sonnet 4.5 或 Opus 4.5 的 Vertex AI 模型上或不支持 `tool_reference` 块的代理上请求会失败 |
| `auto` | 阈值模式：schema 占上下文窗口 10% 以内则预加载，超出则延迟 |
| `auto:N` | 自定义阈值百分比，N 为 0-100。如 `auto:5` 为 5% |
| `false` | 所有 MCP 工具预加载，不延迟 |

```bash
# 使用自定义 5% 阈值
ENABLE_TOOL_SEARCH=auto:5 claude

# 完全禁用工具搜索
ENABLE_TOOL_SEARCH=false claude
```

也可以在 [settings.json 的 `env` 字段](https://code.claude.com/docs/en/settings#available-settings) 中设置。

或在权限配置中禁用 `ToolSearch` 工具：

```json
{
  "permissions": {
    "deny": ["ToolSearch"]
  }
}
```

### 免除特定 Server 的延迟加载

**如果某个 server 的工具需要始终对 Claude 可见（无需搜索步骤），设置 `alwaysLoad` 为 `true`。** 该 server 的所有工具在会话启动时加载到上下文，不受 `ENABLE_TOOL_SEARCH` 设置影响。仅对少量每轮都需要的工具使用，因为预加载的工具会占用本来可用于对话的上下文。

`.mcp.json` 示例，免除一个 HTTP server 同时其他 server 保持延迟：

```json
{
  "mcpServers": {
    "core-tools": {
      "type": "http",
      "url": "https://mcp.example.com/mcp",
      "alwaysLoad": true
    }
  }
}
```

`alwaysLoad` 适用于所有 server 类型，需要 Claude Code v2.1.121 或更高版本。MCP server 也可以在工具的 `_meta` 对象中标记 `"anthropic/alwaysLoad": true`，对单个工具有相同效果。

设置 `alwaysLoad: true` 同时会阻塞启动直到 server 连接完成（标准 5 秒连接超时上限）。即使 MCP 启动本身[默认非阻塞](https://code.claude.com/docs/en/env-vars)也是如此，因为首次 prompt 构建时这些工具必须就位。其他 server 继续在后台连接。

## 将 MCP Prompts 作为命令使用

**MCP server 可以暴露 prompts，在 Claude Code 中作为命令使用。**

### 执行 MCP Prompts

**步骤 1：** 输入 `/` 查看所有可用命令，包括 MCP server 的。MCP prompts 格式为 `/mcp__servername__promptname`。

**步骤 2：** 无参数执行：

```
/mcp__github__list_prs
```

**步骤 3：** 带参数执行（空格分隔）：

```
/mcp__github__pr_review 456
```

```
/mcp__jira__create_issue "Bug in login flow" high
```

**提示：**
- MCP prompts 从已连接 server 动态发现
- 参数根据 prompt 定义的参数解析
- prompt 结果直接注入对话
- server 和 prompt 名称经过规范化，空格转为下划线

## 托管 MCP 配置

**对于需要集中控制用户可连接 MCP server 的组织，** 参见 [托管 MCP 配置](https://code.claude.com/docs/en/managed-mcp)。涵盖用 `managed-mcp.json` 部署固定 server 集合、用 `allowedMcpServers` 和 `deniedMcpServers` 限制 server，以及 server 被阻止时用户看到的提示。
