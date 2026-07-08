---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Gateway 协议
description: Claude Code 与 LLM 网关之间的 API 协议参考，包括端点、请求头和 Body 字段转发、功能降级规则和模型发现。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/llm-gateway-protocol.md
  - en-source/llm-gateway-protocol.md
---

# 网关协议参考

> Claude Code 与 LLM 网关之间的 API 协议：端点、需转发的请求头和 Body 字段、字段被剥离时的功能降级、归属头用于成本追踪、以及模型发现。

**本页面记录 Claude Code 向网关发送的请求内容**，包括调用的端点、网关必须转发的请求头和 Body 字段、以及不转发时哪些功能会失效。面向配置网关产品的运维人员。

已运行的 [Claude apps gateway](https://code.claude.com/docs/en/claude-apps-gateway) 在 `GET /protocol` 提供本协议的机器可读版本。

> - 为组织推广第三方网关：[推广 LLM 网关](https://code.claude.com/docs/en/llm-gateway-rollout)
> - 开发者连接网关：[连接 Claude Code 到 LLM 网关](https://code.claude.com/docs/en/llm-gateway-connect)

本页使用两个术语来描述网关对每个请求头和 Body 字段的处理方式：

- **原样转发**：逐字节传递给上游
- **消费**：网关可读取用于路由、归属或追踪，无需转发

未标记为「原样转发」的字段可由网关自行消费或忽略。

## API 格式

**网关必须向 Claude Code 客户端暴露至少一种以下 API 格式：**

| 格式 | 选择方式 | 端点 | 必须原样转发 |
| :--- | :--- | :--- | :--- |
| Anthropic Messages | `ANTHROPIC_BASE_URL` | `/v1/messages`，`/v1/messages/count_tokens`（可选） | `anthropic-beta` 和 `anthropic-version` 请求头 |
| Amazon Bedrock InvokeModel | `ANTHROPIC_BEDROCK_BASE_URL` + `CLAUDE_CODE_USE_BEDROCK=1` | `/model/{model}/invoke`，`/model/{model}/invoke-with-response-stream` | `anthropic_beta` 和 `anthropic_version` Body 字段 |
| Google Cloud Agent Platform rawPredict | `ANTHROPIC_VERTEX_BASE_URL` + `CLAUDE_CODE_USE_VERTEX=1` | `:rawPredict`，`:streamRawPredict`，`count-tokens:rawPredict`（可选） | `anthropic-beta` 和 `anthropic-version` 请求头，及 `anthropic_version` Body 字段 |

### Foundry 和 Claude Platform on AWS

Microsoft Foundry 和 [Claude Platform on AWS](https://code.claude.com/docs/en/claude-platform-on-aws) 实现 Anthropic Messages 格式。网关前置于 Claude Platform on AWS 时还必须转发 `anthropic-workspace-id` 头。

### 可选端点和启动流量

Token 计数端点是唯一可选的：不存在时，Claude Code 在本地估算上下文用量。推理请求发送到 `/v1/messages?beta=true`，按路径匹配而非完整 URL。

网关还会收到尽力而为的启动流量（可拒绝不影响功能）：`HEAD /` 连通性探测，以及 Amazon Bedrock 格式网关的 `GET /inference-profiles?type=SYSTEM_DEFINED` 请求。

### 流式传输

**推理响应必须流式返回。** Claude Code 逐步消费 Server-Sent Events；缓冲完整响应后才中继会导致客户端卡住。

### 格式不匹配

客户端说哪种格式决定了网关收到什么。常见故障是客户端发往网关的格式与上游接受的格式不匹配。

- 客户端使用 Bedrock 或 Vertex 格式时，Claude Code 只发送那些提供商接受的能力子集
- 客户端使用 Anthropic Messages 格式时，Claude Code 发送完整能力集，即使网关转发到 Bedrock 或 Vertex 上游

弥合这种差异是网关的职责。

## 请求头

**Claude Code 在 API 请求中包含以下头：**

| 头 | 说明 |
| :--- | :--- |
| `Authorization`，`x-api-key` | 开发者的网关凭证 |
| `anthropic-version` | API 版本，当前为 `2023-06-01`。**原样转发** |
| `anthropic-beta` | 逗号分隔的请求能力值。**原样转发**，不要仅允许已知值 |
| `x-claude-code-session-id` | 当前会话唯一标识，用于聚合同一会话的所有请求 |
| `x-claude-code-agent-id` | 发出请求的[子代理](https://code.claude.com/docs/en/sub-agents)标识 |
| `x-claude-code-parent-agent-id` | 生成该代理的父代理标识 |

子代理 ID 每次生成时新建。团队代理（[agent team](https://code.claude.com/docs/en/agent-teams) 的命名成员）跨重连复用稳定的基于名称的 ID。

### 作为开放列表转发

**将请求头和 Body 字段视为开放列表，而非封闭列表。** Claude Code 随版本新增能力，以新的 `anthropic-beta` 值、Body 字段和偶尔新的 `anthropic-*`/`x-claude-code-*` 头出现。

转发到 Anthropic 格式上游时，透传所有 `anthropic-*` 请求头和 Body 字段，而非仅允许当前观察到的。固定在观察列表上的网关在下一个版本引入新能力时会中断它。

## System Prompt 归属块

**Claude Code 在 system prompt 前附加一个简短归属块**，包含客户端版本和会话指纹。`api.anthropic.com` 端点在该块未被修改且作为第一个 system block 到达时会剥离，不影响 prompt 缓存。

要保持该块不进入 prompt：

- 原样转发 `system` 数组，保持该块在首位
- 保持该块在独立数组条目中
- 如果网关必须重组 system 内容，设置 `CLAUDE_CODE_ATTRIBUTION_HEADER=0` 让 Claude Code 省略该块

自 v2.1.181 起，该块在通过自定义 Base URL 路由时对会话生命周期稳定，因此基于完整请求体的网关侧 prompt 缓存可正常工作。

## 功能透传

**Claude Code 将 `ANTHROPIC_BASE_URL` 网关视为 Anthropic 格式端点**，向其发送与 `api.anthropic.com` 相同的 beta 头和 Body 字段。

网关剥离头但保留 Body、或将 Anthropic 格式 Body 转发到不同 schema 的上游时，会产生硬 `400` 错误；只有头和字段同时不存在时功能才静默关闭。

精细粒度工具流（Fine-grained tool streaming）在请求通过自定义 Base URL 路由时默认关闭，开发者设置 `CLAUDE_CODE_ENABLE_FINE_GRAINED_TOOL_STREAMING=1` 时网关才会收到。

| 功能 | 头和 Body 配对 | 中断时的症状 | 修复方式 |
| :--- | :--- | :--- | :--- |
| [自适应推理](https://code.claude.com/docs/en/model-config#adjust-effort-level) | 无 beta 头；发送 `thinking: {"type": "adaptive"}` | `400` 指向 thinking 字段或 adaptive 标签 | 升级上游；或 `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` |
| 上下文管理 | 上下文管理 beta 头 + `context_management` Body 字段 | `400` `Extra inputs are not permitted` | 两者都转发；或 `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1` |
| 扩展上下文 / 交错思考 | 仅 beta 头，无 Body 字段 | 头被剥离时静默不可用 | 原样转发 `anthropic-beta` |
| Beta 工具字段 | 工具相关 beta 头 + 工具 schema 字段 | `400` 指向不认识的工具 schema 字段 | 两者都转发；或 `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1` |
| Effort / 结构化输出 | `output_config` Body 字段 + 各自的 beta 头 | `400` 指向 `output_config` | 字段和头一起转发 |
| Token 计数 | 无 beta 配对；使用 `count_tokens` 端点 | Claude Code 本地估算上下文用量 | 暴露该端点 |

### 自动重试和错误转发

Claude Code 在某些上游拒绝后自动重试并禁用被拒的能力。`thinking` 字段、thinking 签名和会话中间系统消息的拒绝都能通过此方式恢复。

**重试逻辑依赖上游的错误措辞匹配，所以必须原样转发错误响应体。** 网关用自己的封装包裹上游错误会破坏恢复路径。

### 禁用预发布能力

`CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1` 阻止 Claude Code 在所有提供商上发送预发布能力及其 Body 字段，包括上下文管理和 beta 工具字段。不影响自适应推理，也不抑制订阅认证所需的 OAuth 能力。

## 模型发现

**当 `ANTHROPIC_BASE_URL` 指向暴露 Anthropic Messages 格式的网关时，Claude Code 可在启动时查询 `/v1/models` 端点**，将返回的模型添加到 `/model` 选择器。

开发者通过设置 `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1` 启用。默认关闭，避免共享 API 密钥的网关向每个用户暴露所有可访问模型。需要 v2.1.129 或更高版本。

### 何时运行发现

发现仅适用于 Anthropic Messages 格式。以下情况不运行：

- 设置了任何 `CLAUDE_CODE_USE_*` 提供商变量
- `ANTHROPIC_BASE_URL` 未设置或指向 `api.anthropic.com`
- 非必要流量被禁用（通过 `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` 或组织策略）

### 请求和响应

请求为 `GET /v1/models?limit=1000`，3 秒超时，任何重定向视为失败（防止凭证泄漏）。

Claude Code 从响应的 `data` 数组中读取 `id` 和可选的 `display_name`，忽略 `id` 不以 `claude` 或 `anthropic` 开头的条目：

```json
{
  "data": [
    { "id": "claude-sonnet-4-6", "display_name": "Claude Sonnet 4.6" },
    { "id": "claude-opus-4-8" }
  ]
}
```

### 选择器条目和缓存

每个发现的条目标记为「From gateway」。[`availableModels` 托管设置](https://code.claude.com/docs/en/settings#available-settings)限制发现能添加的内容。

结果缓存到 `~/.claude/cache/gateway-models.json`，每次启动刷新。请求失败或网关未实现 `/v1/models` 时，选择器回退到上次启动的缓存或内置模型列表。

## 相关资源

- [网关概览](https://code.claude.com/docs/en/gateways)：网关定义及选择指南
- [第三方 LLM 网关](https://code.claude.com/docs/en/llm-gateway)：推广和订阅交互
- [为组织推广 LLM 网关](https://code.claude.com/docs/en/llm-gateway-rollout)：管理员检查清单
- [连接 Claude Code 到 LLM 网关](https://code.claude.com/docs/en/llm-gateway-connect)：开发者配置和排障表
- [Beta 头参考](https://platform.claude.com/docs/en/api/beta-headers)：当前 `anthropic-beta` 值集合
- [Messages API](https://platform.claude.com/docs/en/api/messages)：Anthropic 格式网关实现的 API 格式
