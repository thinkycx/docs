# 架构深度解析

## 总体架构

Claude Agent SDK 的核心设计是**作为 Claude CLI 的编程接口**。SDK 本身并不直接调用 Anthropic API，而是启动一个 `claude` CLI 子进程，通过 stdin/stdout 的 NDJSON 协议进行双向通信。

```
┌─────────────────────────────────────────────────────────┐
│  用户代码                                                 │
│  ┌───────────────────────┐  ┌─────────────────────────┐ │
│  │  query()              │  │  ClaudeSDKClient        │ │
│  │  (一次性查询)          │  │  (流式/多轮对话)         │ │
│  └──────────┬────────────┘  └────────────┬────────────┘ │
│             │                            │              │
│             ▼                            ▼              │
│  ┌──────────────────────────────────────────────────┐   │
│  │  InternalClient                                   │   │
│  │  (选项验证、Session 物化、生命周期管理)              │   │
│  └────────────────────────┬─────────────────────────┘   │
│                           ▼                             │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Query                                            │   │
│  │  (控制协议、消息路由、Hook 调度、MCP 桥接)          │   │
│  └────────────────────────┬─────────────────────────┘   │
│                           ▼                             │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Transport (抽象层)                                │   │
│  │  SubprocessCLITransport (默认实现)                  │   │
│  └────────────────────────┬─────────────────────────┘   │
└───────────────────────────┼─────────────────────────────┘
                            │ stdin/stdout (NDJSON)
                            ▼
┌──────────────────────────────────────────────────────────┐
│  Claude CLI 子进程                                        │
│  - 管理 Claude API 调用                                   │
│  - 执行内置工具 (Bash, Read, Write, Edit...)             │
│  - 管理上下文窗口和压缩                                   │
│  - 处理权限和安全策略                                     │
└──────────────────────────────────────────────────────────┘
```

## 分层详解

### 第 1 层：公开 API

两个入口点面向不同场景：

| 入口 | 场景 | 特点 |
|------|------|------|
| `query()` | 一次性任务 | async generator，用完即走 |
| `ClaudeSDKClient` | 交互式/多轮 | 持久连接，支持中断、多次查询、运行时控制 |

### 第 2 层：InternalClient

负责：
- 验证 `ClaudeAgentOptions` 的合法性
- 当从 SessionStore 恢复时，将远程 session 物化到本地临时目录
- 创建 Transport 和 Query 实例
- 管理生命周期（确保子进程正确关闭）

### 第 3 层：Query（控制协议核心）

Query 是整个 SDK 的心脏，负责：

1. **消息路由**：从 Transport 读取 NDJSON 行，按 type 字段分发
2. **控制协议**：处理 CLI 发来的 `control_request`（权限询问、Hook 回调、MCP 消息）
3. **SDK MCP 桥接**：将 JSONRPC 消息路由到进程内 MCP Server
4. **并发管理**：使用 anyio memory stream 解耦读取与消费

### 第 4 层：Transport

抽象接口，默认实现为 `SubprocessCLITransport`：
- CLI 发现：优先使用捆绑 CLI，然后 PATH 搜索
- 版本检查：确保 CLI >= 2.0.0
- 命令构建：将 Options 翻译为 CLI 参数
- 优雅关闭：SIGTERM → 等待 → SIGKILL

## NDJSON 通信协议

SDK 与 CLI 之间使用换行分隔的 JSON (NDJSON) 通信：

### SDK → CLI (stdin)

```json
{"type": "user", "content": "Hello"}
{"type": "control_response", "request_id": "abc123", "response": {...}}
```

### CLI → SDK (stdout)

```json
{"type": "assistant", "content": [...], "model": "claude-sonnet-4-5"}
{"type": "system", "subtype": "init", "data": {"tools": [...], "slash_commands": [...]}}
{"type": "control_request", "request_id": "xyz", "request": {"subtype": "can_use_tool", ...}}
{"type": "result", "subtype": "success", "total_cost_usd": 0.003, ...}
{"type": "transcript_mirror", "filePath": "...", "entries": [...]}
```

### 控制协议消息类型

| 方向 | type | 用途 |
|------|------|------|
| SDK→CLI | control_response | 响应 CLI 的控制请求 |
| CLI→SDK | control_request | 权限询问(can_use_tool)、Hook回调、MCP消息 |
| CLI→SDK | control_cancel_request | 取消进行中的控制请求 |
| CLI→SDK | transcript_mirror | Session 转写条目（不暴露给用户） |
| SDK→CLI | control_request | SDK 发起的控制操作（interrupt/set_permission_mode 等） |

## MCP 工具集成架构

```
┌─────────────────────────────────────────────┐
│ SDK 进程                                     │
│                                             │
│  ┌─────────────────────┐                    │
│  │ @tool 定义的工具     │ ← 进程内 MCP Server │
│  │ create_sdk_mcp_server│                    │
│  └──────────┬──────────┘                    │
│             │ JSONRPC (内存路由)              │
│  ┌──────────┴──────────────────────────┐    │
│  │ Query._handle_sdk_mcp_request()     │    │
│  └──────────┬──────────────────────────┘    │
│             │ control_response               │
└─────────────┼───────────────────────────────┘
              │ NDJSON
┌─────────────┼───────────────────────────────┐
│ CLI 子进程   │                               │
│             │ control_request(mcp_message)   │
│  ┌──────────┴──────────────────────────┐    │
│  │ 工具调度器                           │    │
│  │ - SDK MCP工具 → control_request      │    │
│  │ - 外部MCP → stdio/sse/http          │    │
│  │ - 内置工具 → 本地执行                 │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

## 异步运行时

SDK 使用 **anyio** 作为异步抽象层，同时兼容：
- asyncio（默认，`anyio.run(main)` 或 `asyncio.run(main())`）
- trio（需显式指定 `anyio.run(main, backend="trio")`）

核心异步原语：
- `anyio.create_memory_object_stream` — 消息解耦（buffer=100）
- `anyio.open_process` — 子进程管理
- `anyio.Event` — 控制请求的请求/响应配对
- `anyio.create_task_group` — 并发任务管理

## 生命周期图

```
query() 调用:
  ┌─ InternalClient.process_query()
  │   ├─ validate_session_store_options()
  │   ├─ materialize_resume_session()  (如有 session_store)
  │   ├─ SubprocessCLITransport.connect()  → 启动子进程
  │   ├─ Query.start()  → 启动后台读取循环
  │   ├─ Query.initialize()  → 发送 initialize 控制请求
  │   ├─ transport.write(user_message)
  │   ├─ yield messages...  → 逐条返回消息
  │   └─ finally:
  │       ├─ Query.close()  → 停止读取、关闭 transport
  │       └─ materialized.cleanup()  → 清理临时目录
  └─ done

ClaudeSDKClient 生命周期:
  ┌─ client = ClaudeSDKClient(options)
  ├─ await client.connect(prompt)  → 同上启动流程
  ├─ async for msg in client.receive_response():  → 逐条消息
  ├─ await client.query("follow up")  → 发送新消息
  ├─ await client.interrupt()  → 中断当前任务
  ├─ ...更多交互...
  └─ await client.disconnect()  → 优雅关闭
```
