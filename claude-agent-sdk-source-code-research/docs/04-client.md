# ClaudeSDKClient 详解

## 类定义

```python
class ClaudeSDKClient:
    def __init__(
        self,
        options: ClaudeAgentOptions | None = None,
        transport: Transport | None = None,
    )
```

## 核心方法

### 生命周期管理

```python
async def connect(self, prompt: str | AsyncIterable[dict] | None = None) -> None
async def disconnect(self) -> None
async def __aenter__(self) -> ClaudeSDKClient
async def __aexit__(...) -> bool
```

### 消息收发

```python
async def query(self, prompt: str | AsyncIterable[dict], session_id: str = "default") -> None
async def receive_messages(self) -> AsyncIterator[Message]
async def receive_response(self) -> AsyncIterator[Message]  # 到 ResultMessage 为止
```

### 运行时控制

```python
async def interrupt(self) -> None
async def set_permission_mode(self, mode: PermissionMode) -> None
async def set_model(self, model: str | None = None) -> None
async def rewind_files(self, user_message_id: str) -> None
async def reconnect_mcp_server(self, server_name: str) -> None
async def toggle_mcp_server(self, server_name: str, enabled: bool) -> None
async def stop_task(self, task_id: str) -> None
```

### 状态查询

```python
async def get_mcp_status(self) -> McpStatusResponse
async def get_context_usage(self) -> ContextUsageResponse
async def get_server_info(self) -> dict[str, Any] | None
```

## 使用模式

### 模式 1：Context Manager（推荐）

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock

async def main():
    options = ClaudeAgentOptions(allowed_tools=["Read", "Bash"])

    async with ClaudeSDKClient(options) as client:
        await client.query("列出当前目录的文件")
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(block.text)
```

### 模式 2：手动生命周期

```python
client = ClaudeSDKClient(options)
try:
    await client.connect()
    await client.query("Hello")
    async for msg in client.receive_response():
        ...
finally:
    await client.disconnect()
```

## 多轮对话

```python
async with ClaudeSDKClient(options) as client:
    # 第一轮
    await client.query("创建一个 Python 函数计算斐波那契数")
    async for msg in client.receive_response():
        handle(msg)

    # 第二轮（上下文保持）
    await client.query("给这个函数添加缓存装饰器")
    async for msg in client.receive_response():
        handle(msg)

    # 第三轮
    await client.query("为它写单元测试")
    async for msg in client.receive_response():
        handle(msg)
```

## 中断机制

```python
async with ClaudeSDKClient(options) as client:
    await client.query("分析整个代码库并写一份详细报告")

    # 等待一段时间后中断
    await anyio.sleep(5)
    await client.interrupt()

    # 中断后可以发新查询
    await client.query("只分析 src/ 目录")
    async for msg in client.receive_response():
        handle(msg)
```

## receive_messages() vs receive_response()

| 方法 | 行为 |
|------|------|
| `receive_messages()` | 持续 yield 所有消息，不自动停止 |
| `receive_response()` | yield 消息直到收到 ResultMessage，然后停止 |

`receive_response()` 是最常用的模式，适合 "发一条 → 等完成" 的交互模式。

`receive_messages()` 适用于需要持续监听的场景（如后台任务监控）。

## 运行时控制

### 动态切换权限模式

```python
await client.set_permission_mode("bypassPermissions")
await client.query("修改所有配置文件")
async for msg in client.receive_response():
    ...
await client.set_permission_mode("default")  # 恢复
```

### 动态切换模型

```python
await client.set_model("claude-sonnet-4-5")
await client.query("简单问题")
...
await client.set_model("claude-opus-4-5")
await client.query("复杂推理任务")
```

### 文件检查点回退

```python
options = ClaudeAgentOptions(enable_file_checkpointing=True)
async with ClaudeSDKClient(options) as client:
    await client.query("重构 main.py")
    async for msg in client.receive_response():
        if isinstance(msg, UserMessage) and msg.uuid:
            last_user_msg_id = msg.uuid

    # 发现结果不满意，回退
    await client.rewind_files(last_user_msg_id)
```

### MCP 服务器管理

```python
# 查询所有 MCP 服务器状态
status = await client.get_mcp_status()

# 重连某个服务器
await client.reconnect_mcp_server("my-server")

# 禁用/启用服务器
await client.toggle_mcp_server("my-server", enabled=False)
```

## 连接初始化流程

`connect()` 内部执行：
1. 验证 session_store 选项
2. 物化恢复 session（如有 store + resume）
3. 创建 SubprocessCLITransport
4. 提取 SDK MCP servers
5. 创建 Query 实例
6. 启动后台读取循环
7. 发送 initialize 控制请求（传递 hooks、agents 配置）
8. 发送初始 prompt（如有）

## 注意事项

- `can_use_tool` 回调仅在 ClaudeSDKClient 模式下完全支持
- `permission_prompt_tool_name` 与 `can_use_tool` 互斥
- 使用 context manager 时，`connect()` 在 `__aenter__` 中自动调用
- `disconnect()` 在 `__aexit__` 中自动调用，即使发生异常
- Query 对象的 `close()` 方法使用 `anyio.CancelScope(shield=True)` 确保即使取消也能正确清理
