---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Agent SDK - 可观测性
description: 介绍如何通过 OpenTelemetry 从 Agent SDK 导出 traces、metrics 和事件到可观测性后端，涵盖信号启用、trace 阅读、应用关联、标签过滤和敏感数据控制。
category: translation
tags: [claude-code, agent-sdk, translation]
refs:
  - https://code.claude.com/docs/en/agent-sdk/observability
  - en-source/agent-sdk/observability.md
---

# 基于 OpenTelemetry 的可观测性

> 使用 OpenTelemetry 从 Agent SDK 导出 traces、metrics 和事件到你的可观测性后端。

**在生产环境运行 Agent 时，你需要了解它们做了什么：**

- 调用了哪些工具
- 每次模型请求花了多长时间
- 消耗了多少 token
- 哪里发生了故障

Agent SDK 可将这些数据以 OpenTelemetry traces、metrics 和 log 事件的形式导出到任何接受 OTLP 协议的后端，如 Honeycomb、Datadog、Grafana、Langfuse 或自建 collector。

本指南介绍 SDK 如何发出遥测数据、如何配置导出、以及数据到达后端后如何标记和过滤。如需直接从 SDK 响应流中读取 token 用量和成本而非导出到后端，见 [成本与用量追踪](https://code.claude.com/docs/en/agent-sdk/cost-tracking)。

## 遥测数据如何从 SDK 流出

**Agent SDK 将 Claude Code CLI 作为子进程运行并通过本地管道通信。** CLI 内置了 OpenTelemetry 埋点：围绕每次模型请求和工具执行记录 span，为 token 和成本计数器发出 metrics，为 prompt 和工具结果发出结构化 log 事件。SDK 本身不产生遥测。它将配置传递给 CLI 进程，CLI 直接导出到你的 collector。

**配置通过环境变量传递。** 默认情况下子进程继承你应用的环境，因此可在两处配置遥测：

| 配置位置 | 适用场景 |
|:---|:---|
| 进程环境 | 在 shell、容器或编排器中设置变量，每次 `query()` 调用自动获取，无需代码变更。推荐用于生产部署 |
| 按次调用 options | 在 `ClaudeAgentOptions.env`（Python）或 `options.env`（TypeScript）中设置。当同进程中不同 Agent 需要不同遥测设置时使用。Python 中 `env` 合并到继承环境之上；TypeScript 中 `env` 完全替换继承环境，因此传入对象时需包含 `...process.env` |

**CLI 导出三个独立的 OpenTelemetry 信号。** 每个有自己的启用开关和导出器，可只开启需要的：

| 信号 | 内容 | 启用方式 |
|:---|:---|:---|
| Metrics | token、成本、会话、代码行数和工具决策的计数器 | `OTEL_METRICS_EXPORTER` |
| Log 事件 | 每个 prompt、API 请求、API 错误和工具结果的结构化记录 | `OTEL_LOGS_EXPORTER` |
| Traces | 每次交互、模型请求、工具调用和 hook 的 span（beta） | `OTEL_TRACES_EXPORTER` 加 `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1` |

完整的 metric 名称、事件名称和属性列表见 Claude Code [监控](https://code.claude.com/docs/en/monitoring-usage) 参考。Agent SDK 发出相同的数据，因为它运行的是同一个 CLI。span 名称列于下方 [阅读 Agent traces](#阅读-agent-traces)。

## 启用遥测导出

**遥测默认关闭，设置 `CLAUDE_CODE_ENABLE_TELEMETRY=1` 并选择至少一个导出器后启用。** 最常见的配置是通过 OTLP HTTP 将所有三个信号发送到 collector。

以下示例将变量设在字典中并通过 `options.env` 传递。Agent 运行单个任务，CLI 在循环消费响应流的同时将 span、metrics 和事件导出到 `collector.example.com` 的 collector：

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

OTEL_ENV = {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    # traces 需要此变量（beta）。Metrics 和 log 事件不需要
    "CLAUDE_CODE_ENHANCED_TELEMETRY_BETA": "1",
    # 按信号选择导出器。SDK 场景使用 otlp；见下方说明
    "OTEL_TRACES_EXPORTER": "otlp",
    "OTEL_METRICS_EXPORTER": "otlp",
    "OTEL_LOGS_EXPORTER": "otlp",
    # 标准 OTLP 传输配置
    "OTEL_EXPORTER_OTLP_PROTOCOL": "http/protobuf",
    "OTEL_EXPORTER_OTLP_ENDPOINT": "http://collector.example.com:4318",
    "OTEL_EXPORTER_OTLP_HEADERS": "Authorization=Bearer your-token",
}


async def main():
    options = ClaudeAgentOptions(env=OTEL_ENV)
    async for message in query(
        prompt="List the files in this directory", options=options
    ):
        print(message)


asyncio.run(main())
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

const otelEnv = {
  CLAUDE_CODE_ENABLE_TELEMETRY: "1",
  // traces 需要此变量（beta）。Metrics 和 log 事件不需要
  CLAUDE_CODE_ENHANCED_TELEMETRY_BETA: "1",
  // 按信号选择导出器。SDK 场景使用 otlp；见下方说明
  OTEL_TRACES_EXPORTER: "otlp",
  OTEL_METRICS_EXPORTER: "otlp",
  OTEL_LOGS_EXPORTER: "otlp",
  // 标准 OTLP 传输配置
  OTEL_EXPORTER_OTLP_PROTOCOL: "http/protobuf",
  OTEL_EXPORTER_OTLP_ENDPOINT: "http://collector.example.com:4318",
  OTEL_EXPORTER_OTLP_HEADERS: "Authorization=Bearer your-token",
};

for await (const message of query({
  prompt: "List the files in this directory",
  // env 在 TypeScript 中替换继承环境，因此先展开 process.env
  // 以保留 PATH、ANTHROPIC_API_KEY 等变量
  options: { env: { ...process.env, ...otelEnv } },
})) {
  console.log(message);
}
```

由于子进程默认继承应用环境，你也可以通过在 Dockerfile、Kubernetes manifest 或 shell profile 中导出这些变量来达到相同效果，完全省略 `options.env`。

> `console` 导出器将遥测写入标准输出，而 SDK 使用标准输出作为消息通道。通过 SDK 运行时不要将 `console` 设为导出器值。要本地检查遥测，将 `OTEL_EXPORTER_OTLP_ENDPOINT` 指向本地 collector 或一体化 Jaeger 容器。

### 从短期调用刷新遥测

**CLI 批量发送遥测并按间隔导出。** 正常进程退出时尝试刷新待发数据，但刷新受短超时限制，如果 collector 响应慢 span 仍可能丢失。如果进程在 CLI 关闭前被杀死，批次缓冲区中的数据全部丢失。缩短导出间隔可减少这两个窗口。

默认 metrics 每 60 秒导出一次，traces 和 logs 每 5 秒。以下示例缩短所有三个间隔，使数据在短任务仍在运行时到达 collector：

```python
OTEL_ENV = {
    # ... 前述示例的导出器配置 ...
    "OTEL_METRIC_EXPORT_INTERVAL": "1000",
    "OTEL_LOGS_EXPORT_INTERVAL": "1000",
    "OTEL_TRACES_EXPORT_INTERVAL": "1000",
}
```

```typescript
const otelEnv = {
  // ... 前述示例的导出器配置 ...
  OTEL_METRIC_EXPORT_INTERVAL: "1000",
  OTEL_LOGS_EXPORT_INTERVAL: "1000",
  OTEL_TRACES_EXPORT_INTERVAL: "1000",
};
```

## 阅读 Agent traces

**Traces 提供 Agent 运行最详细的视图。** 设置 `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1` 后，Agent 循环的每一步成为可在 tracing 后端中检查的 span：

| Span 名称 | 作用 |
|:---|:---|
| `claude_code.interaction` | 包裹 Agent 循环的单轮，从接收 prompt 到产出响应 |
| `claude_code.llm_request` | 包裹对 Claude API 的每次调用，属性包含模型名称、延迟和 token 计数 |
| `claude_code.tool` | 包裹每次工具调用，子 span 用于权限等待（`claude_code.tool.blocked_on_user`）和执行本身（`claude_code.tool.execution`） |
| `claude_code.hook` | 包裹每次 [hook](https://code.claude.com/docs/en/agent-sdk/hooks) 执行。除上述变量外还需 detailed beta tracing（`ENABLE_BETA_TRACING_DETAILED=1` 和 `BETA_TRACING_ENDPOINT`） |

`llm_request`、`tool` 和 `hook` span 是其所属 `claude_code.interaction` span 的子 span。当 Agent 通过 Task 工具生成子代理时，子代理的 `llm_request` 和 `tool` span 嵌套在父 Agent 的 `claude_code.tool` span 下，整个委派链在一个 trace 中呈现。

Span 默认携带 `session.id` 属性。当你对同一 [会话](https://code.claude.com/docs/en/agent-sdk/sessions) 进行多次 `query()` 调用时，在后端按 `session.id` 过滤可将它们视为一条时间线。将 `OTEL_METRICS_INCLUDE_SESSION_ID` 设为 falsy 值可省略此属性。

> Tracing 处于 beta 阶段。span 名称和属性可能在版本间变化。详见 [监控参考](https://code.claude.com/docs/en/monitoring-usage#traces-beta) 中的 trace 导出器配置变量。

## 将 traces 关联到你的应用

**SDK 自动将 W3C trace context 传播到 CLI 子进程。** 当你在应用中有活跃的 OpenTelemetry span 时调用 `query()`，SDK 将 `TRACEPARENT` 和 `TRACESTATE` 注入子进程环境，CLI 读取它们使其 `claude_code.interaction` span 成为你 span 的子 span。Agent 运行于是出现在你应用的 trace 内而非断开的根。

启用 trace-context 传播后，CLI 还将 `TRACEPARENT` 转发给它运行的每个 Bash 和 PowerShell 命令。如果通过 Bash 工具启动的命令发出自己的 OpenTelemetry span，这些 span 嵌套在包裹该命令的 `claude_code.tool.execution` span 下。

在 `options.env` 中显式设置 `TRACEPARENT` 时跳过自动注入，这样你可以固定特定的父上下文。交互式 CLI 会话完全忽略入站 `TRACEPARENT`；只有 Agent SDK 和 `claude -p` 运行才遵循它。详见 [监控参考](https://code.claude.com/docs/en/monitoring-usage#traces-beta) 的完整 span 和属性参考。

## 为 Agent 标记遥测

**默认情况下 CLI 报告 `service.name` 为 `claude-code`。** 如果运行多个 Agent 或 SDK 与其他服务导出到同一 collector，覆盖服务名称并添加 resource 属性以便在后端按 Agent 过滤。

以下示例重命名服务并附加部署元数据。这些值作为 OpenTelemetry resource 属性应用于 Agent 发出的每个 span、metric 和事件：

```python
options = ClaudeAgentOptions(
    env={
        # ... 导出器配置 ...
        "OTEL_SERVICE_NAME": "support-triage-agent",
        "OTEL_RESOURCE_ATTRIBUTES": "service.version=1.4.0,deployment.environment=production",
    },
)
```

```typescript
const options = {
  env: {
    ...process.env,
    // ... 导出器配置 ...
    OTEL_SERVICE_NAME: "support-triage-agent",
    OTEL_RESOURCE_ATTRIBUTES:
      "service.version=1.4.0,deployment.environment=production",
  },
};
```

## 将操作归因到终端用户

**CLI 根据调用 Anthropic 时使用的凭证将 [身份属性](https://code.claude.com/docs/en/monitoring-usage#standard-attributes) 附加到每个事件。** 当你构建一个从单一部署服务多个终端用户的应用时，这些属性标识的是你服务的凭证，而非代理所代表行事的终端用户。

**要使工具调用和 MCP 活动可归因到你应用的终端用户，在每次 `query()` 调用时注入终端用户身份作为 resource 属性。** 在插值前对值进行百分号编码，因为 `OTEL_RESOURCE_ATTRIBUTES` [保留逗号、空格和等号](https://code.claude.com/docs/en/monitoring-usage#multi-team-organization-support)。以下示例将请求用户和租户附加到一次请求的每个 span 和事件。假设一个来自 web 框架的 `request` 对象携带用户和租户 ID：

```python
from urllib.parse import quote

options = ClaudeAgentOptions(
    env={
        # ... 导出器配置 ...
        "OTEL_RESOURCE_ATTRIBUTES": f"enduser.id={quote(request.user_id)},tenant.id={quote(request.tenant_id)}",
    },
)
```

```typescript
const options = {
  env: {
    ...process.env,
    // ... 导出器配置 ...
    OTEL_RESOURCE_ATTRIBUTES: `enduser.id=${encodeURIComponent(request.userId)},tenant.id=${encodeURIComponent(request.tenantId)}`,
  },
};
```

附加终端用户身份后，`tool_decision`、`tool_result`、`mcp_server_connection` 和 `permission_mode_changed` 事件（以 `claude_code.` 前缀命名的 log record）成为可转发到 SIEM 平台的每用户审计轨迹。详见 [监控参考](https://code.claude.com/docs/en/monitoring-usage#audit-security-events) 中安全相关事件的完整列表及每个事件携带的属性。

## 控制导出中的敏感数据

**遥测默认是结构性的。** 持续时间、模型名称和工具名称记录在每个 span 上；token 计数在底层 API 请求返回 usage 数据时记录，因此失败或中止请求的 span 可能省略它们。Agent 读写的内容默认不记录。以下 opt-in 变量将内容添加到导出数据：

| 变量 | 添加的内容 |
|:---|:---|
| `OTEL_LOG_USER_PROMPTS=1` | `claude_code.user_prompt` 事件和 `claude_code.interaction` span 上的 prompt 文本 |
| `OTEL_LOG_TOOL_DETAILS=1` | `claude_code.tool_result` 事件上的工具输入参数（文件路径、shell 命令、搜索模式） |
| `OTEL_LOG_TOOL_CONTENT=1` | 完整工具输入输出体作为 `claude_code.tool` 上的 span event，截断于 60 KB。需启用 [tracing](#阅读-agent-traces) |
| `OTEL_LOG_RAW_API_BODIES` | 完整 Anthropic Messages API 请求和响应 JSON 作为 `claude_code.api_request_body` 和 `claude_code.api_response_body` log 事件。设为 `1` 获取截断于 60 KB 的内联体，或 `file:<dir>` 获取磁盘上未截断的体加事件中的 `body_ref` 路径。体包含完整对话历史，extended-thinking 内容已编辑。启用此项隐含同意上述三个变量所揭示的一切 |

除非你的可观测性管道被批准存储 Agent 处理的数据，否则不要设置这些变量。详见 [监控参考](https://code.claude.com/docs/en/monitoring-usage#security-and-privacy) 中属性和编辑行为的完整列表。

## 相关文档

- [成本与用量追踪](https://code.claude.com/docs/en/agent-sdk/cost-tracking)：从消息流中读取 token 和成本数据，无需外部后端
- [托管 Agent SDK](https://code.claude.com/docs/en/agent-sdk/hosting)：在容器中部署 Agent，可在环境层设置 OpenTelemetry 变量
- [监控](https://code.claude.com/docs/en/monitoring-usage)：CLI 发出的每个环境变量、metric 和事件的完整参考
