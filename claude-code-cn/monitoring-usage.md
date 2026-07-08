---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】使用监控
description: 通过 OpenTelemetry 追踪 Claude Code 的使用量、成本和工具活动。涵盖快速开始、管理员配置、指标/事件/追踪详情以及安全审计。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/monitoring-usage.md
  - en-source/monitoring-usage.md
---

# 监控

> 了解如何为 Claude Code 启用和配置 OpenTelemetry。

**通过 OpenTelemetry (OTel) 导出遥测数据，追踪组织内 Claude Code 的使用量、成本和工具活动。** Claude Code 通过标准 metrics 协议导出时序指标，通过 logs/events 协议导出事件，可选通过 traces 协议导出分布式追踪。

## 快速开始

通过环境变量配置 OpenTelemetry：

```bash
# 1. 启用遥测
export CLAUDE_CODE_ENABLE_TELEMETRY=1

# 2. 选择导出器（两者都可选——仅配置需要的）
export OTEL_METRICS_EXPORTER=otlp       # 选项: otlp, prometheus, console, none
export OTEL_LOGS_EXPORTER=otlp          # 选项: otlp, console, none

# 3. 配置 OTLP 端点
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# 4. 设置认证（如需要）
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer your-token"

# 5. 调试用: 缩短导出间隔
export OTEL_METRIC_EXPORT_INTERVAL=10000  # 10 秒（默认 60000ms）
export OTEL_LOGS_EXPORT_INTERVAL=5000     # 5 秒（默认 5000ms）

# 6. 运行 Claude Code
claude
```

> 默认导出间隔为 metrics 60 秒、logs 5 秒。设置阶段可用更短间隔调试，生产环境记得恢复。

## 管理员配置

**管理员可通过[托管设置文件](https://code.claude.com/docs/en/settings#settings-files)为所有用户配置 OpenTelemetry：**

```json
{
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp",
    "OTEL_LOGS_EXPORTER": "otlp",
    "OTEL_EXPORTER_OTLP_PROTOCOL": "grpc",
    "OTEL_EXPORTER_OTLP_ENDPOINT": "http://collector.example.com:4317",
    "OTEL_EXPORTER_OTLP_HEADERS": "Authorization=Bearer example-token"
  }
}
```

> 托管设置中定义的环境变量优先级高，用户无法覆盖。

Claude Code 不会将 `OTEL_*` 环境变量传递给它生成的子进程（Bash 工具、hooks、MCP 服务器、语言服务器）。

## 配置详情

### 常用配置变量

| 环境变量 | 说明 | 示例值 |
| :--- | :--- | :--- |
| `CLAUDE_CODE_ENABLE_TELEMETRY` | 启用遥测（必需） | `1` |
| `OTEL_METRICS_EXPORTER` | Metrics 导出器类型，逗号分隔 | `console`, `otlp`, `prometheus`, `none` |
| `OTEL_LOGS_EXPORTER` | Logs/events 导出器类型 | `console`, `otlp`, `none` |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | OTLP 协议 | `grpc`, `http/json`, `http/protobuf` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP 收集器端点 | `http://localhost:4317` |
| `OTEL_EXPORTER_OTLP_HEADERS` | OTLP 认证头 | `Authorization=Bearer token` |
| `OTEL_METRIC_EXPORT_INTERVAL` | 导出间隔毫秒（默认 60000） | `5000`, `60000` |
| `OTEL_LOGS_EXPORT_INTERVAL` | Logs 导出间隔毫秒（默认 5000） | `1000`, `10000` |
| `OTEL_LOG_USER_PROMPTS` | 记录用户提示词内容（默认禁用） | `1` 启用 |
| `OTEL_LOG_ASSISTANT_RESPONSES` | 记录助手响应文本（默认禁用）。未设置时回退到 `OTEL_LOG_USER_PROMPTS`。需要 v2.1.193+ | `1` 启用，`0` 保持脱敏 |
| `OTEL_LOG_TOOL_DETAILS` | 记录工具参数和输入（默认禁用） | `1` 启用 |
| `OTEL_LOG_TOOL_CONTENT` | 记录工具输入输出内容（需要 tracing，截断 60KB） | `1` 启用 |
| `OTEL_LOG_RAW_API_BODIES` | 导出完整 API 请求/响应 JSON | `1` 内联截断 60KB；`file:<dir>` 写文件 |
| `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE` | 指标时间性（默认 `delta`） | `delta`, `cumulative` |

### mTLS 认证

取决于 OTLP 协议：

| 协议 | 客户端证书变量 | 信任收集器 CA |
| :--- | :--- | :--- |
| `http/protobuf`, `http/json` | `CLAUDE_CODE_CLIENT_CERT`, `CLAUDE_CODE_CLIENT_KEY` | `NODE_EXTRA_CA_CERTS` |
| `grpc` | `OTEL_EXPORTER_OTLP_CLIENT_KEY`, `OTEL_EXPORTER_OTLP_CLIENT_CERTIFICATE` | `OTEL_EXPORTER_OTLP_CERTIFICATE` |

### 指标基数控制

| 环境变量 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `OTEL_METRICS_INCLUDE_SESSION_ID` | 包含 session.id | `true` |
| `OTEL_METRICS_INCLUDE_VERSION` | 包含 app.version | `false` |
| `OTEL_METRICS_INCLUDE_ACCOUNT_UUID` | 包含 user.account_uuid 和 user.account_id | `true` |
| `OTEL_METRICS_INCLUDE_ENTRYPOINT` | 包含 app.entrypoint | `false` |
| `OTEL_METRICS_INCLUDE_RESOURCE_ATTRIBUTES` | 包含 `OTEL_RESOURCE_ATTRIBUTES` 中的键 | `true` |

### 追踪（Beta）

**分布式追踪导出 span，将每个用户提示词关联到它触发的 API 请求和工具执行。**

默认关闭。启用方式：设置 `CLAUDE_CODE_ENABLE_TELEMETRY=1` 和 `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1`，然后设置 `OTEL_TRACES_EXPORTER`。

| 环境变量 | 说明 | 示例值 |
| :--- | :--- | :--- |
| `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA` | 启用 span 追踪（必需） | `1` |
| `OTEL_TRACES_EXPORTER` | 追踪导出器类型 | `console`, `otlp`, `none` |
| `OTEL_EXPORTER_OTLP_TRACES_PROTOCOL` | 追踪协议 | `grpc`, `http/json`, `http/protobuf` |
| `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` | 追踪端点 | `http://localhost:4318/v1/traces` |

Span 默认脱敏用户提示词、工具输入和工具内容。设置 `OTEL_LOG_USER_PROMPTS=1`、`OTEL_LOG_TOOL_DETAILS=1`、`OTEL_LOG_TOOL_CONTENT=1` 以包含。

追踪激活时，Bash 和 PowerShell 子进程自动继承 `TRACEPARENT` 环境变量（W3C trace context）。

#### Span 层级

```text
claude_code.interaction
├── claude_code.llm_request
├── claude_code.hook                    (需要 detailed beta tracing)
└── claude_code.tool
    ├── claude_code.tool.blocked_on_user
    ├── claude_code.tool.execution
    └── (Agent tool) subagent spans
```

### 动态头

**企业环境需要动态认证时，可配置脚本生成头。** 仅适用于 `http/protobuf` 和 `http/json` 协议。

在 `.claude/settings.json` 中添加：

```json
{
  "otelHeadersHelper": "/bin/generate_opentelemetry_headers.sh"
}
```

脚本必须输出有效 JSON（字符串键值对），默认每 29 分钟刷新。

### 多团队组织支持

通过 `OTEL_RESOURCE_ATTRIBUTES` 添加自定义属性区分团队：

```bash
export OTEL_RESOURCE_ATTRIBUTES="department=engineering,team.id=platform,cost_center=eng-123"
```

## 可用指标和事件

### 标准属性

所有指标和事件共享以下属性：

| 属性 | 说明 |
| :--- | :--- |
| `session.id` | 唯一会话标识 |
| `organization.id` | 组织 UUID |
| `user.account_uuid` | 账户 UUID |
| `user.account_id` | 匹配 Anthropic admin API 的账户 ID |
| `user.id` | 首次运行时生成的随机匿名标识 |
| `user.email` | 用户邮箱（OAuth 认证时） |
| `terminal.type` | 终端类型 |

### 指标

| 指标名 | 说明 | 单位 |
| :--- | :--- | :--- |
| `claude_code.session.count` | CLI 会话启动数 | count |
| `claude_code.lines_of_code.count` | 修改的代码行数 | count |
| `claude_code.pull_request.count` | 创建的 PR 数 | count |
| `claude_code.commit.count` | 创建的 git commit 数 | count |
| `claude_code.cost.usage` | 会话成本 | USD |
| `claude_code.token.usage` | Token 使用量 | tokens |
| `claude_code.code_edit_tool.decision` | 代码编辑工具权限决策数 | count |
| `claude_code.active_time.total` | 活跃时间 | s |

### 事件

Claude Code 通过 OpenTelemetry logs/events 导出以下事件：

| 事件名 | 说明 |
| :--- | :--- |
| `claude_code.user_prompt` | 用户提交提示词 |
| `claude_code.assistant_response` | 模型返回文本响应（v2.1.193+） |
| `claude_code.tool_result` | 工具执行完成 |
| `claude_code.api_request` | 每个 API 请求 |
| `claude_code.api_error` | API 请求失败 |
| `claude_code.api_refusal` | API 返回 `stop_reason: "refusal"` |
| `claude_code.api_request_body` | API 请求体（需 `OTEL_LOG_RAW_API_BODIES`） |
| `claude_code.api_response_body` | API 响应体（需 `OTEL_LOG_RAW_API_BODIES`） |
| `claude_code.tool_decision` | 工具权限决策 |
| `claude_code.permission_mode_changed` | 权限模式切换 |
| `claude_code.auth` | 登录/登出 |
| `claude_code.mcp_server_connection` | MCP 服务器连接/断开 |
| `claude_code.internal_error` | 内部错误 |
| `claude_code.plugin_installed` | 插件安装 |
| `claude_code.plugin_loaded` | 插件加载 |
| `claude_code.skill_activated` | Skill 调用 |
| `claude_code.compaction` | 会话压缩完成 |
| `claude_code.feedback_survey` | 会话质量调查 |
| `claude_code.hook_registered` | Hook 注册 |
| `claude_code.hook_execution_start` | Hook 开始执行 |
| `claude_code.hook_execution_complete` | Hook 执行完成 |

#### 事件关联属性

`prompt.id`（UUID v4）将同一用户提示词触发的所有事件关联起来。按 `prompt.id` 过滤可获取处理该提示词期间的全部 user_prompt、api_request 和 tool_result 事件。

#### 工具决策事件的 source 值

| source 值 | 含义 |
| :--- | :--- |
| `config` | 基于项目设置、允许/拒绝规则、权限模式等自动决策 |
| `hook` | PreToolUse 或 PermissionRequest hook 返回了决策 |
| `user_permanent` | 用户选择了「不再询问」 |
| `user_temporary` | 用户选择了一次性允许或会话期间允许 |
| `user_abort` | 用户关闭了权限提示 |
| `user_reject` | 用户选择了「No」 |

## 解读指标和事件数据

### 使用量监控

| 指标 | 分析机会 |
| :--- | :--- |
| `claude_code.token.usage` | 按 type/用户/团队/模型/skill/plugin 分析 |
| `claude_code.session.count` | 跟踪采用率和参与度 |
| `claude_code.lines_of_code.count` | 按模型衡量生产力 |
| `claude_code.commit.count` / `pull_request.count` | 了解开发工作流影响 |

### 成本监控

`claude_code.cost.usage` 支持按团队/个人跟踪趋势、识别高用量会话、按 `skill.name`/`plugin.name`/`agent.name` 归属支出。

> 成本指标是近似值。正式计费数据请参考 API 提供商（Claude Console、Amazon Bedrock 或 Google Cloud Agent Platform）。

## 审计安全事件

**OpenTelemetry 事件是 Claude Code 活动的审计数据源。** 每个事件携带身份属性，将工具调用、MCP 活动和权限决策关联到触发它们的用户。

### 将操作归属到用户

标准属性包含认证用户身份：`user.email`、`user.account_uuid`、`user.account_id`、`organization.id`。MCP 工具调用、Bash 命令和文件编辑归属于启动会话的开发者。

使用直接 API 密钥或第三方提供商时，只有 `user.id` 和 `session.id` 填充。此时通过 `OTEL_RESOURCE_ATTRIBUTES` 附加用户身份。

### 审计 MCP 活动

启用 logs 导出器并设置 `OTEL_LOG_TOOL_DETAILS=1`，每个 MCP 操作产生携带服务器名、工具名和调用参数的结构化事件。

### 发送事件到 SIEM

将 `OTEL_EXPORTER_OTLP_LOGS_ENDPOINT` 指向 SIEM 的 OTLP 接收器：

```json
{
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_LOGS_EXPORTER": "otlp",
    "OTEL_LOG_TOOL_DETAILS": "1",
    "OTEL_EXPORTER_OTLP_LOGS_PROTOCOL": "http/protobuf",
    "OTEL_EXPORTER_OTLP_LOGS_ENDPOINT": "https://siem.example.com:4318/v1/logs",
    "OTEL_EXPORTER_OTLP_HEADERS": "Authorization=Bearer your-siem-token"
  }
}
```

## 后端选择建议

### 指标后端
- 时序数据库（如 Prometheus）：速率计算、聚合指标
- 列存储（如 ClickHouse）：复杂查询、唯一用户分析
- 全功能可观测性平台（如 Honeycomb、Datadog、Grafana Cloud）：高级查询、可视化、告警

### 事件/日志后端
- 日志聚合系统（如 Elasticsearch、Loki）：全文搜索、日志分析
- 列存储（如 ClickHouse）：结构化事件分析
- 全功能可观测性平台：指标与事件关联

### 追踪后端
- 分布式追踪系统（如 Jaeger、Zipkin、Grafana Tempo）：span 可视化、请求瀑布图
- 全功能可观测性平台：追踪搜索和与指标/日志关联

## 服务信息

所有指标和事件携带以下资源属性：

- `service.name`: `claude-code`
- `service.version`: 当前 Claude Code 版本
- `os.type`: 操作系统类型
- `os.version`: 操作系统版本
- `host.arch`: 主机架构
- Meter Name: `com.anthropic.claude_code`

## 安全和隐私

- OpenTelemetry 导出是 opt-in 的，需要明确配置
- 原始文件内容和代码片段不包含在指标或事件中
- 通过 OAuth 认证时 `user.email` 包含在遥测属性中
- 用户提示词内容默认不收集，仅记录长度
- 助手响应文本默认不收集，仅记录长度
- 工具输入参数默认不记录
- 原始 API 请求/响应体默认不记录
- Claude 扩展思考内容始终从导出体中脱敏

## 在 Amazon Bedrock 上监控

详细的 Amazon Bedrock 监控指南参见 [Claude Code Monitoring Implementation (Amazon Bedrock)](https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock/blob/main/assets/docs/MONITORING.md)。

## ROI 测量资源

综合 ROI 测量指南参见 [Claude Code ROI Measurement Guide](https://github.com/anthropics/claude-code-monitoring-guide)。
