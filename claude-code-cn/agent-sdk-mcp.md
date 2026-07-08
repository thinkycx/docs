---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
category: translation
tags: [claude-code, agent-sdk, translation]
description: Claude Agent SDK 的 MCP 集成指南，介绍如何通过 MCP 协议连接外部工具和数据源，涵盖传输类型、工具搜索、认证和错误处理。
refs:
  - https://code.claude.com/docs/en/agent-sdk/mcp
  - en-source/agent-sdk/mcp.md
title: 【译】Agent SDK - MCP 集成
---

# 【译】SDK MCP 集成

> 配置 MCP 服务器以扩展 Agent 的外部工具能力。涵盖传输类型、大型工具集的工具搜索、认证和错误处理。

**[Model Context Protocol (MCP)](https://modelcontextprotocol.io/docs/getting-started/intro) 是连接 AI Agent 与外部工具和数据源的开放标准。** 通过 MCP，你的 Agent 可以查询数据库、与 Slack 和 GitHub 等 API 集成，以及连接其他服务，而无需编写自定义工具实现。

MCP 服务器可以作为本地进程运行、通过 HTTP 连接，或直接在 SDK 应用内执行。

> 本页涵盖 Agent SDK 的 MCP 配置。要将 MCP 服务器添加到 Claude Code CLI 以使其在每个项目中加载，请参阅 [MCP 安装作用域](https://code.claude.com/docs/en/mcp#mcp-installation-scopes)。

## 快速开始

**此示例使用 HTTP 传输连接到 Claude Code 文档 MCP 服务器**，并使用 [`allowedTools`](#允许-mcp-工具) 的通配符来允许服务器的所有工具。

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Use the docs MCP server to explain what hooks are in Claude Code",
  options: {
    mcpServers: {
      "claude-code-docs": {
        type: "http",
        url: "https://code.claude.com/docs/mcp"
      }
    },
    allowedTools: ["mcp__claude-code-docs__*"]
  }
})) {
  if (message.type === "result" && message.subtype === "success") {
    console.log(message.result);
  }
}
```

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


async def main():
    options = ClaudeAgentOptions(
        mcp_servers={
            "claude-code-docs": {
                "type": "http",
                "url": "https://code.claude.com/docs/mcp",
            }
        },
        allowed_tools=["mcp__claude-code-docs__*"],
    )

    async for message in query(
        prompt="Use the docs MCP server to explain what hooks are in Claude Code",
        options=options,
    ):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(message.result)


asyncio.run(main())
```

Agent 连接到文档服务器，搜索关于 hooks 的信息，并返回结果。

## 添加 MCP 服务器

**你可以在代码中调用 `query()` 时配置 MCP 服务器，或在通过 [`settingSources`](#从配置文件) 加载的 `.mcp.json` 文件中配置。**

### 在代码中

直接在 `mcpServers` 选项中传入 MCP 服务器：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "List files in my project",
  options: {
    mcpServers: {
      filesystem: {
        command: "npx",
        args: ["-y", "@modelcontextprotocol/server-filesystem", "/Users/me/projects"]
      }
    },
    allowedTools: ["mcp__filesystem__*"]
  }
})) {
  if (message.type === "result" && message.subtype === "success") {
    console.log(message.result);
  }
}
```

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


async def main():
    options = ClaudeAgentOptions(
        mcp_servers={
            "filesystem": {
                "command": "npx",
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    "/Users/me/projects",
                ],
            }
        },
        allowed_tools=["mcp__filesystem__*"],
    )

    async for message in query(prompt="List files in my project", options=options):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(message.result)


asyncio.run(main())
```

### 从配置文件

**在项目根目录创建 `.mcp.json` 文件。** 当 `project` 设置源启用时该文件会被读取（默认 `query()` 选项中已启用）。如果你显式设置了 `settingSources`，需包含 `"project"` 才能加载此文件：

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/me/projects"]
    }
  }
}
```

## 允许 MCP 工具

**MCP 工具在 Claude 使用之前需要显式授权。** 没有授权时，Claude 可以看到工具可用但无法调用它们。

### 工具命名规则

MCP 工具遵循命名模式 `mcp__<server-name>__<tool-name>`。例如，名为 `"github"` 的 GitHub 服务器中的 `list_issues` 工具变为 `mcp__github__list_issues`。

### 用 allowedTools 自动批准

**使用 `allowedTools` 自动批准特定 MCP 工具，** 这样 Claude 可以无需权限提示直接使用：

```typescript
const options = {
  mcpServers: {
    // 你的服务器
  },
  allowedTools: [
    "mcp__github__*",            // github 服务器的所有工具
    "mcp__db__query",            // 仅 db 服务器的 query 工具
    "mcp__slack__send_message"   // 仅 slack 的 send_message
  ]
};
```

通配符（`*`）让你可以允许服务器的所有工具，无需逐一列出。

> **对于 MCP 访问，优先使用 `allowedTools` 而非权限模式。** `permissionMode: "acceptEdits"` 不会自动批准 MCP 工具（仅文件编辑和文件系统 Bash 命令）。`permissionMode: "bypassPermissions"` 会自动批准 MCP 工具，但也会禁用其他安全提示（除非显式 [`ask` 规则](https://code.claude.com/docs/en/agent-sdk/permissions#how-permissions-are-evaluated)匹配），这比所需范围更广。`allowedTools` 中的通配符精确授予你想要的 MCP 服务器，不会多也不会少。完整对比见[权限模式](https://code.claude.com/docs/en/agent-sdk/permissions#permission-modes)。

### 发现可用工具

**要查看 MCP 服务器提供了哪些工具，** 查看服务器文档或连接到服务器并检查 `system` init 消息：

```typescript
for await (const message of query({ prompt: "...", options })) {
  if (message.type === "system" && message.subtype === "init") {
    console.log("Available MCP tools:", message.mcp_servers);
  }
}
```

```python
import asyncio
from claude_agent_sdk import query, SystemMessage


async def main():
    async for message in query(prompt="...", options=options):
        if isinstance(message, SystemMessage) and message.subtype == "init":
            print("Available MCP tools:", message.data["mcp_servers"])


asyncio.run(main())
```

## 传输类型

**MCP 服务器使用不同的传输协议与 Agent 通信。** 查看服务器文档确认其支持的传输方式：

* 文档给出一个**要运行的命令**（如 `npx @modelcontextprotocol/server-github`）→ 使用 stdio
* 文档给出一个 **URL** → 使用 HTTP 或 SSE
* 你在代码中构建自己的工具 → 使用 SDK MCP 服务器

### stdio 服务器

**通过 stdin/stdout 通信的本地进程。** 用于在同一台机器上运行的 MCP 服务器：

在代码中：

```typescript
const options = {
  mcpServers: {
    github: {
      command: "npx",
      args: ["-y", "@modelcontextprotocol/server-github"],
      env: {
        GITHUB_TOKEN: process.env.GITHUB_TOKEN
      }
    }
  },
  allowedTools: ["mcp__github__list_issues", "mcp__github__search_issues"]
};
```

```python
options = ClaudeAgentOptions(
    mcp_servers={
        "github": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {"GITHUB_TOKEN": os.environ["GITHUB_TOKEN"]},
        }
    },
    allowed_tools=["mcp__github__list_issues", "mcp__github__search_issues"],
)
```

`.mcp.json` 配置文件：

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

### HTTP/SSE 服务器

**用于云托管的 MCP 服务器和远程 API：**

在代码中：

```typescript
const options = {
  mcpServers: {
    "remote-api": {
      type: "sse",
      url: "https://api.example.com/mcp/sse",
      headers: {
        Authorization: `Bearer ${process.env.API_TOKEN}`
      }
    }
  },
  allowedTools: ["mcp__remote-api__*"]
};
```

```python
options = ClaudeAgentOptions(
    mcp_servers={
        "remote-api": {
            "type": "sse",
            "url": "https://api.example.com/mcp/sse",
            "headers": {"Authorization": f"Bearer {os.environ['API_TOKEN']}"},
        }
    },
    allowed_tools=["mcp__remote-api__*"],
)
```

`.mcp.json` 配置文件：

```json
{
  "mcpServers": {
    "remote-api": {
      "type": "sse",
      "url": "https://api.example.com/mcp/sse",
      "headers": {
        "Authorization": "Bearer ${API_TOKEN}"
      }
    }
  }
}
```

对于 streamable HTTP 传输，使用 `"type": "http"`。在 `.mcp.json` 和其他 JSON 配置文件中，`"streamable-http"` 作为 `"http"` 的别名被接受。编程方式的 `mcpServers` 选项只接受 `"http"`。

### SDK MCP 服务器

**直接在应用代码中定义自定义工具，** 而不是运行单独的服务器进程。实现细节见[自定义工具指南](https://code.claude.com/docs/en/agent-sdk/custom-tools)。

## MCP 工具搜索

**当配置了大量 MCP 工具时，工具定义可能占据上下文窗口的很大部分。** 工具搜索通过从上下文中隐藏工具定义来解决此问题，仅加载 Claude 每个回合需要的工具。

工具搜索默认启用。配置选项和详情见[工具搜索](https://code.claude.com/docs/en/agent-sdk/tool-search)。

更多详情（包括最佳实践和与自定义 SDK 工具配合使用工具搜索），见[工具搜索指南](https://code.claude.com/docs/en/agent-sdk/tool-search)。

## 认证

**大多数 MCP 服务器需要认证才能访问外部服务。** 通过服务器配置中的环境变量传递凭证。

### 通过环境变量传递凭证

使用 `env` 字段向 MCP 服务器传递 API 密钥、令牌和其他凭证：

在代码中：

```typescript
const options = {
  mcpServers: {
    github: {
      command: "npx",
      args: ["-y", "@modelcontextprotocol/server-github"],
      env: {
        GITHUB_TOKEN: process.env.GITHUB_TOKEN
      }
    }
  },
  allowedTools: ["mcp__github__list_issues"]
};
```

```python
options = ClaudeAgentOptions(
    mcp_servers={
        "github": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {"GITHUB_TOKEN": os.environ["GITHUB_TOKEN"]},
        }
    },
    allowed_tools=["mcp__github__list_issues"],
)
```

`.mcp.json` 配置文件：

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

`${GITHUB_TOKEN}` 语法在运行时展开环境变量。

完整的带调试日志的示例见[从仓库列出 Issues](#从仓库列出-issues)。

### 远程服务器的 HTTP Headers

**对于 HTTP 和 SSE 服务器，直接在服务器配置中传递认证 headers：**

在代码中：

```typescript
const options = {
  mcpServers: {
    "secure-api": {
      type: "http",
      url: "https://api.example.com/mcp",
      headers: {
        Authorization: `Bearer ${process.env.API_TOKEN}`
      }
    }
  },
  allowedTools: ["mcp__secure-api__*"]
};
```

```python
options = ClaudeAgentOptions(
    mcp_servers={
        "secure-api": {
            "type": "http",
            "url": "https://api.example.com/mcp",
            "headers": {"Authorization": f"Bearer {os.environ['API_TOKEN']}"},
        }
    },
    allowed_tools=["mcp__secure-api__*"],
)
```

`.mcp.json` 配置文件：

```json
{
  "mcpServers": {
    "secure-api": {
      "type": "http",
      "url": "https://api.example.com/mcp",
      "headers": {
        "Authorization": "Bearer ${API_TOKEN}"
      }
    }
  }
}
```

`${API_TOKEN}` 语法在运行时展开环境变量。

### OAuth2 认证

**[MCP 规范支持 OAuth 2.1](https://modelcontextprotocol.io/specification/2025-03-26/basic/authorization) 用于授权。** SDK 不自动处理 OAuth 流程，但你可以在应用中完成 OAuth 流程后通过 headers 传递 access token：

```typescript
// 在应用中完成 OAuth 流程后
const accessToken = await getAccessTokenFromOAuthFlow();

const options = {
  mcpServers: {
    "oauth-api": {
      type: "http",
      url: "https://api.example.com/mcp",
      headers: {
        Authorization: `Bearer ${accessToken}`
      }
    }
  },
  allowedTools: ["mcp__oauth-api__*"]
};
```

```python
# 在应用中完成 OAuth 流程后
access_token = await get_access_token_from_oauth_flow()

options = ClaudeAgentOptions(
    mcp_servers={
        "oauth-api": {
            "type": "http",
            "url": "https://api.example.com/mcp",
            "headers": {"Authorization": f"Bearer {access_token}"},
        }
    },
    allowed_tools=["mcp__oauth-api__*"],
)
```

## 示例

### 从仓库列出 Issues

**此示例连接到 [GitHub MCP 服务器](https://github.com/modelcontextprotocol/servers/tree/main/src/github) 列出最近的 Issues。** 包含调试日志以验证 MCP 连接和工具调用。

运行前，创建具有 `repo` 作用域的 [GitHub 个人访问令牌](https://github.com/settings/tokens) 并设置为环境变量：

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "List the 3 most recent issues in anthropics/claude-code",
  options: {
    mcpServers: {
      github: {
        command: "npx",
        args: ["-y", "@modelcontextprotocol/server-github"],
        env: {
          GITHUB_TOKEN: process.env.GITHUB_TOKEN
        }
      }
    },
    allowedTools: ["mcp__github__list_issues"]
  }
})) {
  // 验证 MCP 服务器连接成功
  if (message.type === "system" && message.subtype === "init") {
    console.log("MCP servers:", message.mcp_servers);
  }

  // 记录 Claude 调用 MCP 工具的时机
  if (message.type === "assistant") {
    for (const block of message.message.content) {
      if (block.type === "tool_use" && block.name.startsWith("mcp__")) {
        console.log("MCP tool called:", block.name);
      }
    }
  }

  // 打印最终结果
  if (message.type === "result" && message.subtype === "success") {
    console.log(message.result);
  }
}
```

```python
import asyncio
import os
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    ResultMessage,
    SystemMessage,
    AssistantMessage,
)


async def main():
    options = ClaudeAgentOptions(
        mcp_servers={
            "github": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"],
                "env": {"GITHUB_TOKEN": os.environ["GITHUB_TOKEN"]},
            }
        },
        allowed_tools=["mcp__github__list_issues"],
    )

    async for message in query(
        prompt="List the 3 most recent issues in anthropics/claude-code",
        options=options,
    ):
        # 验证 MCP 服务器连接成功
        if isinstance(message, SystemMessage) and message.subtype == "init":
            print("MCP servers:", message.data.get("mcp_servers"))

        # 记录 Claude 调用 MCP 工具的时机
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "name") and block.name.startswith("mcp__"):
                    print("MCP tool called:", block.name)

        # 打印最终结果
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(message.result)


asyncio.run(main())
```

### 查询数据库

**此示例使用 [Postgres MCP 服务器](https://github.com/modelcontextprotocol/servers/tree/main/src/postgres) 查询数据库。** 连接字符串作为参数传递给服务器。Agent 自动发现数据库 schema、编写 SQL 查询并返回结果：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

// 从环境变量获取连接字符串
const connectionString = process.env.DATABASE_URL;

for await (const message of query({
  // 自然语言查询 - Claude 编写 SQL
  prompt: "How many users signed up last week? Break it down by day.",
  options: {
    mcpServers: {
      postgres: {
        command: "npx",
        // 将连接字符串作为参数传递给服务器
        args: ["-y", "@modelcontextprotocol/server-postgres", connectionString]
      }
    },
    // 只允许读查询，不允许写
    allowedTools: ["mcp__postgres__query"]
  }
})) {
  if (message.type === "result" && message.subtype === "success") {
    console.log(message.result);
  }
}
```

```python
import asyncio
import os
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


async def main():
    # 从环境变量获取连接字符串
    connection_string = os.environ["DATABASE_URL"]

    options = ClaudeAgentOptions(
        mcp_servers={
            "postgres": {
                "command": "npx",
                # 将连接字符串作为参数传递给服务器
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-postgres",
                    connection_string,
                ],
            }
        },
        # 只允许读查询，不允许写
        allowed_tools=["mcp__postgres__query"],
    )

    # 自然语言查询 - Claude 编写 SQL
    async for message in query(
        prompt="How many users signed up last week? Break it down by day.",
        options=options,
    ):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(message.result)


asyncio.run(main())
```

## 错误处理

**MCP 服务器可能因各种原因连接失败：** 服务器进程可能未安装、凭证可能无效、或远程服务器可能不可达。

SDK 在每次查询开始时发出一个 subtype 为 `init` 的 `system` 消息。此消息包含每个 MCP 服务器的连接状态。检查 `status` 字段以在 Agent 开始工作前检测连接失败：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Process data",
  options: {
    mcpServers: {
      "data-processor": dataServer
    }
  }
})) {
  if (message.type === "system" && message.subtype === "init") {
    const failedServers = message.mcp_servers.filter((s) => s.status !== "connected");

    if (failedServers.length > 0) {
      console.warn("Failed to connect:", failedServers);
    }
  }

  if (message.type === "result" && message.subtype === "error_during_execution") {
    console.error("Execution failed");
  }
}
```

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, SystemMessage, ResultMessage


async def main():
    options = ClaudeAgentOptions(mcp_servers={"data-processor": data_server})

    async for message in query(prompt="Process data", options=options):
        if isinstance(message, SystemMessage) and message.subtype == "init":
            failed_servers = [
                s
                for s in message.data.get("mcp_servers", [])
                if s.get("status") != "connected"
            ]

            if failed_servers:
                print(f"Failed to connect: {failed_servers}")

        if (
            isinstance(message, ResultMessage)
            and message.subtype == "error_during_execution"
        ):
            print("Execution failed")


asyncio.run(main())
```

## 故障排查

### 服务器显示 "failed" 状态

**检查 `init` 消息查看哪些服务器连接失败：**

```typescript
if (message.type === "system" && message.subtype === "init") {
  for (const server of message.mcp_servers) {
    if (server.status === "failed") {
      console.error(`Server ${server.name} failed to connect`);
    }
  }
}
```

常见原因：

| 问题 | 解决方案 |
| :--- | :--- |
| 缺少环境变量 | 确保所需的令牌和凭证已设置。对于 stdio 服务器，检查 `env` 字段是否匹配服务器期望的内容 |
| 服务器未安装 | 对于 `npx` 命令，验证包存在且 Node.js 在 PATH 中 |
| 无效的连接字符串 | 对于数据库服务器，验证连接字符串格式和数据库可访问性 |
| 网络问题 | 对于远程 HTTP/SSE 服务器，检查 URL 是否可达以及防火墙是否允许连接 |

### 工具未被调用

**如果 Claude 看到了工具但不使用它们，** 检查是否已通过 `allowedTools` 授予权限：

```typescript
const options = {
  mcpServers: {
    // 你的服务器
  },
  allowedTools: ["mcp__servername__*"] // 自动批准来自此服务器的调用
};
```

### 连接超时

**MCP 服务器连接默认 30 秒后超时。** 如果你的服务器启动需要更长时间，连接会失败。使用 [`MCP_TIMEOUT`](https://code.claude.com/docs/en/env-vars) 环境变量提高限制（单位毫秒）。对于需要更多启动时间的服务器，也可考虑：

* 使用更轻量的服务器（如果可用）
* 在启动 Agent 之前预热服务器
* 检查服务器日志以找出启动缓慢的原因

## 相关资源

* [自定义工具指南](https://code.claude.com/docs/en/agent-sdk/custom-tools)：构建在 SDK 应用中运行的 MCP 服务器
* [权限配置](https://code.claude.com/docs/en/agent-sdk/permissions)：通过 `allowedTools` 和 `disallowedTools` 控制 Agent 可以使用哪些 MCP 工具
* [TypeScript SDK 参考](https://code.claude.com/docs/en/agent-sdk/typescript)：完整 API 参考，包括 MCP 配置选项
* [Python SDK 参考](https://code.claude.com/docs/en/agent-sdk/python)：完整 API 参考，包括 MCP 配置选项
* [MCP 服务器目录](https://github.com/modelcontextprotocol/servers)：浏览可用的数据库、API 等 MCP 服务器
