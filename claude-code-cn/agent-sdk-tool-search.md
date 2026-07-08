---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Agent SDK - 工具搜索
description: 通过工具搜索让 Agent 扩展到数千个工具——按需动态发现和加载所需工具，而非一次性全部加入上下文窗口。涵盖工作原理、配置方式、优化策略和限制。
category: translation
tags: [claude-code, agent-sdk, tool-search, translation]
refs:
  - https://code.claude.com/docs/en/agent-sdk/tool-search
  - en-source/agent-sdk/tool-search.md
---

# 通过工具搜索扩展到海量工具

> 让 Agent 扩展到数千个工具——按需动态发现和加载所需工具

**工具搜索让 Agent 能处理数百甚至数千个工具，通过按需动态发现和加载来实现。** 无需一次性将所有工具定义加入上下文窗口，Agent 会搜索工具目录并只加载需要的工具。

这种方式解决了工具库规模扩大时的两个挑战：

| 挑战 | 说明 |
|:---|:---|
| 上下文效率 | 工具定义可能占据上下文窗口的很大比例（50 个工具可能占用 10-20K token），留给实际工作的空间变少 |
| 工具选择准确度 | 同时加载超过 30-50 个工具时，选择准确度会下降 |

工具搜索默认启用。

## 工作原理

**当工具搜索激活时，工具定义不会进入上下文窗口。** Agent 接收可用工具的摘要，当任务需要尚未加载的能力时进行搜索。3-5 个最相关的工具会被加载到上下文中，在后续轮次中保持可用。如果对话足够长，SDK 压缩早期消息以释放空间时，之前发现的工具可能被移除，Agent 会在需要时重新搜索。

工具搜索在 Claude 首次发现工具时增加一次额外往返（搜索步骤），但对于大型工具集，这被每轮更小的上下文所抵消。工具少于约 10 个时，一次性全部加载通常更快。

关于底层 API 机制的详情，参见[API 中的工具搜索](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)。

> **注意：** 除 Haiku 外，所有 Claude 模型都支持工具搜索。

## 配置工具搜索

**工具搜索默认开启。** 在 Google Cloud Agent Platform 上默认禁用（支持 Claude Sonnet 4.5 及以上和 Claude Opus 4.5 及以上）。当 `ANTHROPIC_BASE_URL` 指向非第一方主机时也会禁用（因为大多数代理不转发 `tool_reference` 块）。可以通过 `ENABLE_TOOL_SEARCH` 环境变量覆盖默认值：

| 值 | 行为 |
|:---|:---|
| （未设置） | 工具搜索开启。工具定义延迟加载、按需发现。在 Google Cloud Agent Platform 或非第一方 `ANTHROPIC_BASE_URL` 上回退到前置加载 |
| `true` | 工具搜索始终开启。即使在 Google Cloud Agent Platform 和代理上也发送 beta header。在低于 Sonnet 4.5 或 Opus 4.5 的 Google Cloud 模型上，或不支持 `tool_reference` 块的代理上会请求失败 |
| `auto` | 检查所有工具定义的合计 token 数与模型上下文窗口的比例。超过 10% 时激活工具搜索，低于 10% 时所有工具正常加入上下文 |
| `auto:N` | 与 `auto` 相同但使用自定义百分比。`auto:5` 在工具定义超过上下文窗口 5% 时激活。值越低越早激活 |
| `false` | 工具搜索关闭。所有工具定义每轮都加入上下文 |

工具搜索适用于所有已注册的工具，无论来自远程 MCP 服务器还是[自定义 SDK MCP 服务器](https://code.claude.com/docs/en/agent-sdk/custom-tools)。使用 `auto` 时，阈值基于所有服务器上所有工具定义的合计大小。

在 `query()` 的 `env` 选项中设置该值。以下示例连接到一个暴露大量工具的远程 MCP 服务器，用通配符预批准所有工具，并使用 `auto:5` 让工具搜索在定义超过上下文窗口 5% 时激活：

TypeScript：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Find and run the appropriate database query",
  options: {
    mcpServers: {
      "enterprise-tools": {
        // 连接到远程 MCP 服务器
        type: "http",
        url: "https://tools.example.com/mcp"
      }
    },
    allowedTools: ["mcp__enterprise-tools__*"], // 通配符预批准该服务器的所有工具
    env: {
      ENABLE_TOOL_SEARCH: "auto:5" // 工具超过上下文 5% 时激活工具搜索
    }
  }
})) {
  if (message.type === "result" && message.subtype === "success") {
    console.log(message.result);
  }
}
```

Python：

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


async def main():
    options = ClaudeAgentOptions(
        mcp_servers={
            "enterprise-tools": {
                "type": "http",
                "url": "https://tools.example.com/mcp",
            }
        },
        allowed_tools=[
            "mcp__enterprise-tools__*"
        ],  # 通配符预批准该服务器的所有工具
        env={
            "ENABLE_TOOL_SEARCH": "auto:5"  # 工具超过上下文 5% 时激活工具搜索
        },
    )

    async for message in query(
        prompt="Find and run the appropriate database query",
        options=options,
    ):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(message.result)


asyncio.run(main())
```

将 `ENABLE_TOOL_SEARCH` 设为 `"false"` 会禁用工具搜索，每轮都将所有工具定义加入上下文。这省去了搜索往返，当工具集较小（少于约 10 个工具）且定义能轻松放入上下文窗口时可能更快。

## 优化工具发现

**搜索机制根据工具名称和描述进行匹配。** 像 `search_slack_messages` 这样的名称比 `query_slack` 能匹配更广泛的请求。包含具体关键词的描述（"Search Slack messages by keyword, channel, or date range"）比泛化描述（"Query Slack"）匹配更多查询。

还可以在系统提示中添加一段列出可用工具类别的内容。这让 Agent 了解有哪些类型的工具可以搜索：

```text
You can search for tools to interact with Slack, GitHub, and Jira.
```

## 限制

| 限制项 | 数值 |
|:---|:---|
| 最大工具数 | 目录中最多 10,000 个工具 |
| 搜索结果 | 每次搜索返回 3-5 个最相关的工具 |
| 模型支持 | 除 Haiku 外的所有 Claude 模型 |

## 相关文档

* [API 中的工具搜索](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)：工具搜索的完整 API 文档，包括自定义实现
* [连接 MCP 服务器](https://code.claude.com/docs/en/agent-sdk/mcp)：通过 MCP 服务器连接外部工具
* [自定义工具](https://code.claude.com/docs/en/agent-sdk/custom-tools)：用 SDK MCP 服务器构建自己的工具
* [TypeScript SDK 参考](https://code.claude.com/docs/en/agent-sdk/typescript)：完整 API 参考
* [Python SDK 参考](https://code.claude.com/docs/en/agent-sdk/python)：完整 API 参考
