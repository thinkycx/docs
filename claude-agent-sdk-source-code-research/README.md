# Claude Agent SDK Python 深度研究

基于 [claude-agent-sdk](https://github.com/anthropics/claude-code-sdk-python) Python SDK 源码的深度研究项目，包含完整的中文 API 文档和 43 个可直接运行的功能演示。

## 项目结构

```
├── docs/           中文 API 文档（20 篇 + 附录）
├── demos/          功能演示集（43 个独立可运行 demo）
└── sdk-source/     SDK 源码（clone from GitHub）
```

## 快速开始

```bash
# 运行 Demo
cd demos
uv sync
uv run python 01_basic_query.py
```

## 文档索引

| # | 文档 | 内容 |
|---|------|------|
| 01 | [架构深度解析](docs/01-architecture.md) | SDK 分层架构、通信协议、执行流程 |
| 02 | [快速上手](docs/02-getting-started.md) | 安装、配置、第一个程序 |
| 03 | [query() 函数详解](docs/03-query-function.md) | 一次性查询入口 |
| 04 | [ClaudeSDKClient 详解](docs/04-client.md) | 流式/多轮对话客户端 |
| 05 | [ClaudeAgentOptions 全参数](docs/05-options.md) | 50+ 配置参数分组说明 |
| 06 | [消息类型体系](docs/06-message-types.md) | Message/ContentBlock 完整类型 |
| 07 | [自定义工具系统](docs/07-custom-tools.md) | @tool 装饰器、MCP Server |
| 08 | [Hook 事件系统](docs/08-hooks.md) | 10 种 Hook 事件完整指南 |
| 09 | [子 Agent 系统](docs/09-subagents.md) | AgentDefinition、多 Agent 协作 |
| 10 | [权限控制系统](docs/10-permissions.md) | 六步评估流程、can_use_tool |
| 11 | [Session 管理](docs/11-sessions.md) | 续接/恢复/Fork/Store |
| 12 | [MCP 服务器集成](docs/12-mcp-servers.md) | 四种类型、配置与管理 |
| 13 | [结构化输出](docs/13-structured-output.md) | JSON Schema、校验与重试 |
| 14 | [流式输出](docs/14-streaming.md) | StreamEvent、部分消息 |
| 15 | [成本与预算](docs/15-cost-and-budget.md) | 成本追踪、预算控制 |
| 16 | [错误处理](docs/16-error-handling.md) | 异常层级、ResultMessage 错误 |
| 17 | [System Prompt](docs/17-system-prompt.md) | 字符串/预设/追加三种模式 |
| 18 | [思考与努力级别](docs/18-thinking-and-effort.md) | ThinkingConfig、EffortLevel |
| 19 | [沙盒与安全](docs/19-sandbox.md) | SandboxSettings、安全部署 |
| 20 | [高级主题](docs/20-advanced.md) | Transport/Plugin/Beta/Settings |
| -- | [类型速查表](docs/appendix-types.md) | 全部导出类型分类索引 |

## Demo 索引

### 基础篇（01-03）
| # | Demo | 核心功能 |
|---|------|---------|
| 01 | [basic_query](demos/01_basic_query.py) | query() 最简用法 |
| 02 | [query_with_tools](demos/02_query_with_tools.py) | query() + 工具配置 |
| 03 | [query_max_turns](demos/03_query_max_turns.py) | max_turns 轮数限制 |

### 客户端篇（04-07）
| # | Demo | 核心功能 |
|---|------|---------|
| 04 | [client_basic](demos/04_client_basic.py) | ClaudeSDKClient 基础 |
| 05 | [client_multi_turn](demos/05_client_multi_turn.py) | 多轮对话 |
| 06 | [client_interrupt](demos/06_client_interrupt.py) | 中断任务 |
| 07 | [client_async_input](demos/07_client_async_input.py) | 异步输入流 |

### 工具篇（08-12）
| # | Demo | 核心功能 |
|---|------|---------|
| 08 | [tool_simple](demos/08_tool_simple.py) | @tool 装饰器基础 |
| 09 | [tool_typeddict_schema](demos/09_tool_typeddict_schema.py) | TypedDict 参数定义 |
| 10 | [tool_error_handling](demos/10_tool_error_handling.py) | 工具错误处理 |
| 11 | [tool_annotations](demos/11_tool_annotations.py) | ToolAnnotations 注解 |
| 12 | [mcp_external_server](demos/12_mcp_external_server.py) | 外部 MCP 服务器 |

### Hook 篇（13-17）
| # | Demo | 核心功能 |
|---|------|---------|
| 13 | [hook_pre_tool_use](demos/13_hook_pre_tool_use.py) | PreToolUse 拦截 |
| 14 | [hook_post_tool_use](demos/14_hook_post_tool_use.py) | PostToolUse 回调 |
| 15 | [hook_user_prompt_submit](demos/15_hook_user_prompt_submit.py) | 注入上下文 |
| 16 | [hook_stop](demos/16_hook_stop.py) | Stop 控制 |
| 17 | [hook_notification](demos/17_hook_notification.py) | Notification 事件 |

### Agent 篇（18-20）
| # | Demo | 核心功能 |
|---|------|---------|
| 18 | [agent_definition](demos/18_agent_definition.py) | 编程定义子 Agent |
| 19 | [agent_multi_agents](demos/19_agent_multi_agents.py) | 多 Agent 协作 |
| 20 | [agent_filesystem](demos/20_agent_filesystem.py) | 文件系统 Agent |

### 权限篇（21-23）
| # | Demo | 核心功能 |
|---|------|---------|
| 21 | [permission_callback](demos/21_permission_callback.py) | can_use_tool 回调 |
| 22 | [permission_modes](demos/22_permission_modes.py) | PermissionMode 模式 |
| 23 | [permission_allow_deny](demos/23_permission_allow_deny.py) | 允许/禁止工具列表 |

### Session 篇（24-28）
| # | Demo | 核心功能 |
|---|------|---------|
| 24 | [session_continue](demos/24_session_continue.py) | 续接对话 |
| 25 | [session_resume](demos/25_session_resume.py) | 恢复指定 session |
| 26 | [session_fork](demos/26_session_fork.py) | Fork session |
| 27 | [session_store](demos/27_session_store.py) | InMemorySessionStore |
| 28 | [session_list_and_info](demos/28_session_list_and_info.py) | 列出/查询 session |

### 输出篇（29-30）
| # | Demo | 核心功能 |
|---|------|---------|
| 29 | [structured_output](demos/29_structured_output.py) | JSON Schema 结构化 |
| 30 | [streaming_partial](demos/30_streaming_partial.py) | StreamEvent 流式 |

### 配置篇（31-38）
| # | Demo | 核心功能 |
|---|------|---------|
| 31 | [system_prompt_string](demos/31_system_prompt_string.py) | 自定义字符串 Prompt |
| 32 | [system_prompt_preset](demos/32_system_prompt_preset.py) | 预设 Prompt 模式 |
| 33 | [cost_tracking](demos/33_cost_tracking.py) | 成本追踪 |
| 34 | [budget_control](demos/34_budget_control.py) | 预算控制 |
| 35 | [thinking_config](demos/35_thinking_config.py) | 思考配置 |
| 36 | [effort_levels](demos/36_effort_levels.py) | 努力级别 |
| 37 | [model_selection](demos/37_model_selection.py) | 模型选择 |
| 38 | [setting_sources](demos/38_setting_sources.py) | 配置源控制 |

### 高级篇（39-43）
| # | Demo | 核心功能 |
|---|------|---------|
| 39 | [error_handling](demos/39_error_handling.py) | 错误处理模式 |
| 40 | [file_checkpointing](demos/40_file_checkpointing.py) | 文件检查点 |
| 41 | [sandbox_config](demos/41_sandbox_config.py) | 沙盒配置 |
| 42 | [plugins](demos/42_plugins.py) | 插件加载 |
| 43 | [rate_limit_handling](demos/43_rate_limit_handling.py) | 速率限制处理 |

## 环境要求

- Python >= 3.10
- Claude CLI（SDK 自动捆绑）
- 环境变量：`ANTHROPIC_API_KEY` 或 `ANTHROPIC_AUTH_TOKEN` + `ANTHROPIC_BASE_URL`

## SDK 版本

基于 `claude-agent-sdk` v0.2.111 源码分析。
