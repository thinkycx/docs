# Claude Agent SDK Python Demo 集

43 个独立可运行的演示脚本，覆盖 SDK 全部核心功能。

## 运行方式

```bash
cd demos
uv sync                           # 安装依赖
uv run python 01_basic_query.py   # 运行任意 demo
```

## 环境要求

确保以下环境变量已设置（SDK 子进程自动继承）：

```bash
# 方式 1: API Key
export ANTHROPIC_API_KEY="sk-ant-..."

# 方式 2: Token + 自定义端点
export ANTHROPIC_AUTH_TOKEN="your-token"
export ANTHROPIC_BASE_URL="https://your-proxy.example.com/v1/anthropic/"
```

可选模型覆盖：
```bash
export ANTHROPIC_DEFAULT_OPUS_MODEL="aws.claude-opus-4.6"
export ANTHROPIC_DEFAULT_SONNET_MODEL="aws.claude-sonnet-4-5"
```

## Demo 列表

### 基础篇 — query() 入门

| # | 文件 | 说明 | 核心 API |
|---|------|------|----------|
| 01 | `01_basic_query.py` | 最简单的查询 | `query()`, `AssistantMessage`, `TextBlock` |
| 02 | `02_query_with_tools.py` | 带工具的查询 | `allowed_tools`, `ToolUseBlock` |
| 03 | `03_query_max_turns.py` | 轮数限制 | `max_turns`, `ResultMessage.num_turns` |

### 客户端篇 — ClaudeSDKClient

| # | 文件 | 说明 | 核心 API |
|---|------|------|----------|
| 04 | `04_client_basic.py` | 基础用法 | `ClaudeSDKClient`, `receive_response()` |
| 05 | `05_client_multi_turn.py` | 多轮对话 | `client.query()` 多次调用 |
| 06 | `06_client_interrupt.py` | 中断任务 | `client.interrupt()` |
| 07 | `07_client_async_input.py` | 异步输入流 | `AsyncIterable` prompt |

### 工具篇 — 自定义工具

| # | 文件 | 说明 | 核心 API |
|---|------|------|----------|
| 08 | `08_tool_simple.py` | @tool 基础 | `@tool`, `create_sdk_mcp_server` |
| 09 | `09_tool_typeddict_schema.py` | TypedDict 参数 | `TypedDict`, `Annotated` |
| 10 | `10_tool_error_handling.py` | 错误处理 | `is_error: True` |
| 11 | `11_tool_annotations.py` | 工具注解 | `ToolAnnotations` |
| 12 | `12_mcp_external_server.py` | 外部 MCP | `McpStdioServerConfig` |

### Hook 篇 — 事件拦截

| # | 文件 | 说明 | 核心 API |
|---|------|------|----------|
| 13 | `13_hook_pre_tool_use.py` | 工具执行前拦截 | `PreToolUse`, `permissionDecision` |
| 14 | `14_hook_post_tool_use.py` | 工具执行后回调 | `PostToolUse`, `additionalContext` |
| 15 | `15_hook_user_prompt_submit.py` | 注入上下文 | `UserPromptSubmit` |
| 16 | `16_hook_stop.py` | 停止控制 | `Stop`, `continue_`, `stopReason` |
| 17 | `17_hook_notification.py` | 通知事件 | `Notification` |

### Agent 篇 — 子 Agent

| # | 文件 | 说明 | 核心 API |
|---|------|------|----------|
| 18 | `18_agent_definition.py` | 编程定义 Agent | `AgentDefinition` |
| 19 | `19_agent_multi_agents.py` | 多 Agent 协作 | 多个 `AgentDefinition` |
| 20 | `20_agent_filesystem.py` | 文件系统 Agent | `setting_sources` |

### 权限篇 — 权限控制

| # | 文件 | 说明 | 核心 API |
|---|------|------|----------|
| 21 | `21_permission_callback.py` | 权限回调 | `can_use_tool`, `PermissionResultAllow/Deny` |
| 22 | `22_permission_modes.py` | 权限模式 | `PermissionMode` |
| 23 | `23_permission_allow_deny.py` | 允许/禁止列表 | `allowed_tools`, `disallowed_tools` |

### Session 篇 — 会话管理

| # | 文件 | 说明 | 核心 API |
|---|------|------|----------|
| 24 | `24_session_continue.py` | 续接对话 | `continue_conversation=True` |
| 25 | `25_session_resume.py` | 恢复 session | `resume=session_id` |
| 26 | `26_session_fork.py` | Fork session | `fork_session=True` |
| 27 | `27_session_store.py` | Session Store | `InMemorySessionStore` |
| 28 | `28_session_list_and_info.py` | 列出/查询 | `list_sessions()`, `get_session_messages()` |

### 输出篇 — 输出控制

| # | 文件 | 说明 | 核心 API |
|---|------|------|----------|
| 29 | `29_structured_output.py` | 结构化输出 | `output_format`, `structured_output` |
| 30 | `30_streaming_partial.py` | 流式部分消息 | `include_partial_messages`, `StreamEvent` |

### 配置篇 — 运行时配置

| # | 文件 | 说明 | 核心 API |
|---|------|------|----------|
| 31 | `31_system_prompt_string.py` | 字符串 Prompt | `system_prompt="..."` |
| 32 | `32_system_prompt_preset.py` | 预设 Prompt | `{"type": "preset", ...}` |
| 33 | `33_cost_tracking.py` | 成本追踪 | `total_cost_usd`, `usage` |
| 34 | `34_budget_control.py` | 预算控制 | `max_budget_usd` |
| 35 | `35_thinking_config.py` | 思考配置 | `ThinkingConfig`, `ThinkingBlock` |
| 36 | `36_effort_levels.py` | 努力级别 | `effort` |
| 37 | `37_model_selection.py` | 模型选择 | `model`, `fallback_model` |
| 38 | `38_setting_sources.py` | 配置源 | `setting_sources` |

### 高级篇 — 高级功能

| # | 文件 | 说明 | 核心 API |
|---|------|------|----------|
| 39 | `39_error_handling.py` | 错误处理 | 全部异常类型 |
| 40 | `40_file_checkpointing.py` | 文件检查点 | `enable_file_checkpointing` |
| 41 | `41_sandbox_config.py` | 沙盒配置 | `SandboxSettings` |
| 42 | `42_plugins.py` | 插件加载 | `SdkPluginConfig` |
| 43 | `43_rate_limit_handling.py` | 速率限制 | `RateLimitEvent` |

## 学习路线建议

1. **入门**: 01 → 02 → 04 → 05（掌握基本查询和多轮对话）
2. **工具开发**: 08 → 09 → 10 → 11（掌握自定义工具）
3. **行为控制**: 13 → 14 → 21 → 22（掌握 Hook 和权限）
4. **生产部署**: 33 → 34 → 39 → 27（掌握成本、错误、持久化）
