# query() 函数详解

## 函数签名

```python
async def query(
    *,
    prompt: str | AsyncIterable[dict[str, Any]],
    options: ClaudeAgentOptions | None = None,
    transport: Transport | None = None,
) -> AsyncIterator[Message]
```

## 参数

### prompt

| 类型 | 说明 |
|------|------|
| `str` | 单次文本消息（最常见用法） |
| `AsyncIterable[dict]` | 异步消息流（高级：流式输入模式） |

字符串 prompt 在内部被包装为 `{"type": "user", "content": prompt}` 发送给 CLI。

### options

`ClaudeAgentOptions` 实例，控制所有行为。传 None 使用全部默认值。

### transport

自定义 Transport 实现。通常不需要，SDK 会自动创建 `SubprocessCLITransport`。

## 返回值

`AsyncIterator[Message]` — 异步迭代器，逐条 yield 消息直到收到 `ResultMessage`。

消息类型包括：
- `SystemMessage` — 初始化信息、任务状态
- `AssistantMessage` — Claude 的回复
- `UserMessage` — 工具执行结果（自动生成）
- `StreamEvent` — 流式部分消息（需 `include_partial_messages=True`）
- `RateLimitEvent` — 速率限制事件
- `ResultMessage` — 最终结果（总是最后一条）

## 基础用法

```python
import anyio
from claude_agent_sdk import query, AssistantMessage, ResultMessage, TextBlock

async def main():
    async for msg in query(prompt="Hello, Claude!"):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(msg, ResultMessage):
            print(f"完成，耗时 {msg.duration_ms}ms")

anyio.run(main)
```

## 带选项的用法

```python
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(
    system_prompt="你是一个简洁的助手，回答不超过20字",
    max_turns=1,
    allowed_tools=["Read"],
    model="claude-sonnet-4-5",
)

async for msg in query(prompt="什么是 Python?", options=options):
    ...
```

## 异步输入流模式

```python
import anyio
from collections.abc import AsyncIterable

async def message_stream() -> AsyncIterable[dict]:
    yield {"type": "user", "content": "第一条消息"}
    await anyio.sleep(1)
    yield {"type": "user", "content": "第二条消息"}

async def main():
    async for msg in query(prompt=message_stream()):
        ...
```

## 内部执行流程

1. 实例化 `InternalClient()`
2. 调用 `client.process_query(prompt, options, transport)`
3. 验证选项 → 物化 session（如有 store） → 创建 Transport → 连接
4. 创建 `Query` 实例 → 启动后台读取 → 发送 initialize → 发送 prompt
5. 逐条 yield 解析后的消息
6. 收到 `result` 消息后，清理资源

## query() vs ClaudeSDKClient

| 特性 | query() | ClaudeSDKClient |
|------|---------|-----------------|
| 使用模式 | 一次性 | 持久连接 |
| 多轮对话 | 不支持 | 支持 |
| 中断 | 不支持 | `client.interrupt()` |
| 运行时控制 | 不支持 | set_permission_mode, set_model 等 |
| can_use_tool | 支持(需 AsyncIterable prompt) | 支持 |
| 简洁度 | 更简洁 | 更灵活 |
| 适用场景 | 批处理、脚本 | 交互应用、长时间运行 |

## 注意事项

- `query()` 在内部始终使用流式模式（streaming mode）
- 结果消息 (`ResultMessage`) 总是迭代器的最后一条
- 如果 options 为 None，等价于 `ClaudeAgentOptions()` 默认值
- `can_use_tool` 回调在 query() 中使用时，prompt 必须是 AsyncIterable（流式输入模式）
