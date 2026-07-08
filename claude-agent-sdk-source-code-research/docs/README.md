# Claude Agent SDK Python 中文文档

基于 `claude-agent-sdk` v0.2.111 源码的完整 API 文档。

## 文档目录

### 核心概念
- [01 架构深度解析](01-architecture.md) — SDK 分层架构、NDJSON 通信协议、执行流程
- [02 快速上手](02-getting-started.md) — 安装、配置、第一个程序

### API 参考
- [03 query() 函数详解](03-query-function.md) — 一次性查询的核心入口
- [04 ClaudeSDKClient 详解](04-client.md) — 流式/多轮/交互式客户端
- [05 ClaudeAgentOptions 全参数](05-options.md) — 50+ 配置参数完整说明
- [06 消息类型体系](06-message-types.md) — 所有 Message 和 ContentBlock 类型

### 功能指南
- [07 自定义工具系统](07-custom-tools.md) — @tool 装饰器、create_sdk_mcp_server
- [08 Hook 事件系统](08-hooks.md) — 10 种 Hook 事件类型完整指南
- [09 子 Agent 系统](09-subagents.md) — AgentDefinition、多 Agent 协作
- [10 权限控制系统](10-permissions.md) — 六步权限评估、can_use_tool 回调
- [11 Session 管理](11-sessions.md) — 续接/恢复/Fork/SessionStore
- [12 MCP 服务器集成](12-mcp-servers.md) — 四种服务器类型配置与管理
- [13 结构化输出](13-structured-output.md) — JSON Schema 输出与校验
- [14 流式输出](14-streaming.md) — StreamEvent、部分消息
- [15 成本与预算](15-cost-and-budget.md) — 成本追踪、max_budget_usd
- [16 错误处理](16-error-handling.md) — 异常类型与 ResultMessage 错误
- [17 System Prompt](17-system-prompt.md) — 系统提示词配置
- [18 思考与努力级别](18-thinking-and-effort.md) — ThinkingConfig、EffortLevel
- [19 沙盒与安全](19-sandbox.md) — 沙盒配置、安全部署
- [20 高级主题](20-advanced.md) — Transport/Plugin/Beta/Settings

### 附录
- [类型速查表](appendix-types.md) — 全部 __all__ 导出类型分类索引
