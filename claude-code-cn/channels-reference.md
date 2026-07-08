---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Channels 参考
description: Channels MCP 服务器技术参考，覆盖 capability 声明、notification 事件格式、reply tool 暴露、发送者门控和权限转发的完整合约。
category: translation
tags: [claude-code, channels-reference, translation]
refs:
  - https://code.claude.com/docs/en/channels-reference.md
  - en-source/channels-reference.md
---

# Channels 参考

**构建一个 MCP 服务器，将 webhook、告警和聊天消息推送到 Claude Code 会话中。**

> Channels 处于 [research preview](https://code.claude.com/docs/en/channels#research-preview) 阶段，需要 Claude Code v2.1.80 或更高版本。Team 和 Enterprise 组织必须[显式启用](https://code.claude.com/docs/en/channels#enterprise-controls)。

Channel 是一个 MCP 服务器，向 Claude Code 会话推送事件让 Claude 对终端外发生的事情做出反应。

你可以构建单向或双向 channel。单向 channel 转发告警、webhook 或监控事件。双向 channel 还暴露 reply tool 让 Claude 回复消息。带受信发送者路径的 channel 还可选择转发权限提示。

本页覆盖：

- [概览](#概览)：channel 工作原理
- [需要什么](#需要什么)：要求和步骤
- [示例：构建 webhook 接收器](#示例构建-webhook-接收器)
- [服务器选项](#服务器选项)
- [通知格式](#通知格式)
- [暴露 reply tool](#暴露-reply-tool)
- [入站消息门控](#入站消息门控)
- [转发权限提示](#转发权限提示)

## 概览

**Channel 是运行在与 Claude Code 相同机器上的 MCP 服务器。** Claude Code 将其作为子进程启动，通过 stdio 通信。

- **聊天平台**（Telegram、Discord）：插件本地运行并轮询平台 API。无需暴露 URL
- **Webhook**（CI、监控）：服务器监听本地 HTTP 端口。外部系统 POST 到该端口

## 需要什么

唯一硬性要求是 [`@modelcontextprotocol/sdk`](https://www.npmjs.com/package/@modelcontextprotocol/sdk) 包和 Node.js 兼容运行时（Bun/Node/Deno）。

你的服务器需要：

1. 声明 `claude/channel` capability 让 Claude Code 注册通知监听器
2. 在事件发生时发射 `notifications/claude/channel` 事件
3. 通过 stdio transport 连接

## 示例：构建 webhook 接收器

**完整单文件服务器，监听 HTTP 请求并转发到 Claude Code 会话。**

### 1. 创建项目

```bash
mkdir webhook-channel && cd webhook-channel
bun add @modelcontextprotocol/sdk
```

### 2. 编写 channel 服务器

```ts
// webhook.ts
#!/usr/bin/env bun
import { Server } from '@modelcontextprotocol/sdk/server/index.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'

const mcp = new Server(
  { name: 'webhook', version: '0.0.1' },
  {
    capabilities: { experimental: { 'claude/channel': {} } },
    instructions: 'Events from the webhook channel arrive as <channel source="webhook" ...>. They are one-way: read them and act, no reply expected.',
  },
)

await mcp.connect(new StdioServerTransport())

Bun.serve({
  port: 8788,
  hostname: '127.0.0.1',
  async fetch(req) {
    const body = await req.text()
    await mcp.notification({
      method: 'notifications/claude/channel',
      params: {
        content: body,
        meta: { path: new URL(req.url).pathname, method: req.method },
      },
    })
    return new Response('ok')
  },
})
```

### 3. 注册到 Claude Code

```json
// .mcp.json
{
  "mcpServers": {
    "webhook": { "command": "bun", "args": ["./webhook.ts"] }
  }
}
```

### 4. 测试

```bash
# 启动（research preview 需要开发标志）
claude --dangerously-load-development-channels server:webhook

# 在另一个终端发送测试 webhook
curl -X POST localhost:8788 -d "build failed on main: https://ci.example.com/run/1234"
```

事件到达时以 `<channel>` 标签形式出现：

```text
<channel source="webhook" path="/" method="POST">build failed on main: https://ci.example.com/run/1234</channel>
```

## 服务器选项

| 字段 | 类型 | 描述 |
|------|------|------|
| `capabilities.experimental['claude/channel']` | object | 必填。始终 `{}`。注册通知监听器 |
| `capabilities.experimental['claude/channel/permission']` | object | 可选。声明可接收权限转发请求 |
| `capabilities.tools` | object | 仅双向。启用工具发现 |
| `instructions` | string | 推荐。添加到 Claude 系统 prompt |

## 通知格式

| 字段 | 类型 | 描述 |
|------|------|------|
| `content` | string | 事件正文。成为 `<channel>` 标签体 |
| `meta` | <code>Record&lt;string, string&gt;</code> | 可选。每个条目成为 `<channel>` 标签属性 |

```ts
await mcp.notification({
  method: 'notifications/claude/channel',
  params: {
    content: 'build failed on main: https://ci.example.com/run/1234',
    meta: { severity: 'high', run_id: '1234' },
  },
})
```

通知不被确认。`await` 在消息写入 transport 时 resolve，不是 Claude 处理后。事件按顺序排队处理。

## 暴露 reply tool

**双向 channel 暴露标准 MCP tool 让 Claude 回复消息。** 三个组件：

1. `Server` 构造器 capabilities 中的 `tools: {}` 条目
2. 定义 tool schema 和发送逻辑的 handler
3. `instructions` 告诉 Claude 何时和如何调用 tool

```ts
mcp.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{
    name: 'reply',
    description: 'Send a message back over this channel',
    inputSchema: {
      type: 'object',
      properties: {
        chat_id: { type: 'string', description: 'The conversation to reply in' },
        text: { type: 'string', description: 'The message to send' },
      },
      required: ['chat_id', 'text'],
    },
  }],
}))
```

## 入站消息门控

**未设门控的 channel 是 prompt injection 向量。** 任何能到达你端点的人都能在 Claude 面前放文本。

在调用 `mcp.notification()` 前检查发送者身份白名单：

```ts
const allowed = new Set(loadAllowlist())

if (!allowed.has(message.from.id)) {  // 门控在发送者而非聊天室
  return  // 静默丢弃
}
await mcp.notification({ ... })
```

门控在发送者身份（`message.from.id`），而非聊天/房间身份。群聊中两者不同。

## 转发权限提示

> 需要 Claude Code v2.1.81 或更高版本。

**当 Claude 调用需要批准的工具时，双向 channel 可以选择并行接收相同提示并转发到你的其他设备。** 本地终端和远程都保持活跃，先到的答案生效。

### 工作流程

1. Claude Code 生成短 request ID 并通知你的服务器
2. 服务器将提示和 ID 转发到聊天应用
3. 远程用户以 yes/no + ID 回复
4. 入站 handler 解析回复为裁决

### 权限请求字段

| 字段 | 描述 |
|------|------|
| `request_id` | 5 个小写字母（`a-z` 不含 `l`）。必须在回复中回显 |
| `tool_name` | 工具名称，如 `Bash` 或 `Write` |
| `description` | 人类可读摘要 |
| `input_preview` | 工具参数 JSON 字符串，截断到 200 字符 |

裁决格式：`notifications/claude/channel/permission`，含 `request_id` 和 `behavior`（`'allow'` 或 `'deny'`）。

### 添加到聊天桥接

1. 在 `experimental` capabilities 添加 `'claude/channel/permission': {}`
2. 注册 `notifications/claude/channel/permission_request` 通知 handler
3. 在入站 handler 中识别 `yes <id>` / `no <id>` 格式并发射裁决

```ts
const PERMISSION_REPLY_RE = /^\s*(y|yes|n|no)\s+([a-km-z]{5})\s*$/i

// 匹配则发射裁决，否则作为正常聊天转发
```

## 打包为插件

将 channel 包装为 [plugin](https://code.claude.com/docs/en/plugins) 并发布到 [marketplace](https://code.claude.com/docs/en/plugin-marketplaces) 使其可安装可共享。

## 另见

- [Channels](https://code.claude.com/docs/en/channels) — 安装和使用 Telegram、Discord、iMessage 或 fakechat
- [Working channel implementations](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins) — 完整服务器代码
- [MCP](https://code.claude.com/docs/en/mcp) — channel 服务器实现的底层协议
- [Plugins](https://code.claude.com/docs/en/plugins) — 打包 channel 让用户用 `/plugin install` 安装
