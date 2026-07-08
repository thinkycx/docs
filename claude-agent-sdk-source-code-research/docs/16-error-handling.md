# 错误处理

## 异常层次结构

Claude Agent SDK 定义了清晰的异常层级，所有异常继承自 `ClaudeSDKError`：

```
ClaudeSDKError (基类)
├── CLIConnectionError (连接 CLI 失败)
│   └── CLINotFoundError (找不到 CLI 二进制文件)
├── ProcessError (CLI 进程异常退出，含 exit_code + stderr)
└── CLIJSONDecodeError (CLI 返回的 JSON 格式错误，含 line + original_error)
```

## 异常详解

### ClaudeSDKError

所有 SDK 异常的基类，可用于捕获所有 SDK 相关错误：

```python
from claude_agent_sdk import query, ClaudeAgentOptions, ClaudeSDKError

try:
    async for msg in query(prompt="hello", options=ClaudeAgentOptions()):
        pass
except ClaudeSDKError as e:
    print(f"SDK 错误: {e}")
```

### CLINotFoundError

当系统中找不到 `claude` CLI 时抛出。这是最常见的初始配置错误：

```python
from claude_agent_sdk import query, ClaudeAgentOptions, CLINotFoundError

try:
    async for msg in query(prompt="hello", options=ClaudeAgentOptions()):
        pass
except CLINotFoundError:
    print("错误: 未找到 Claude CLI")
    print("请先安装: npm install -g @anthropic-ai/claude-code")
    print("或确认 claude 命令在 PATH 中")
```

### CLIConnectionError

CLI 存在但无法建立连接（如启动超时、权限问题）：

```python
from claude_agent_sdk import query, ClaudeAgentOptions, CLIConnectionError

try:
    async for msg in query(prompt="hello", options=ClaudeAgentOptions()):
        pass
except CLIConnectionError as e:
    print(f"连接失败: {e}")
    # 可能原因：CLI 版本不兼容、端口冲突等
```

### ProcessError

CLI 进程异常退出，包含退出码和标准错误输出：

```python
from claude_agent_sdk import query, ClaudeAgentOptions, ProcessError

try:
    async for msg in query(prompt="hello", options=ClaudeAgentOptions()):
        pass
except ProcessError as e:
    print(f"进程错误 (退出码 {e.exit_code})")
    print(f"stderr: {e.stderr}")
    # stderr 通常包含有用的诊断信息
    # 如: API key 无效、网络超时等
```

### CLIJSONDecodeError

CLI 返回了非法的 JSON 数据（极罕见，通常表示 CLI bug 或被干扰）：

```python
from claude_agent_sdk import query, ClaudeAgentOptions, CLIJSONDecodeError

try:
    async for msg in query(prompt="hello", options=ClaudeAgentOptions()):
        pass
except CLIJSONDecodeError as e:
    print(f"JSON 解析失败")
    print(f"原始行: {e.line}")
    print(f"原始错误: {e.original_error}")
```

## ResultMessage 错误子类型

除了异常之外，很多错误通过 `ResultMessage` 报告（查询正常完成但结果异常）：

### error_max_turns

超过 `max_turns` 限制，任务未完成就被截断：

```python
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

options = ClaudeAgentOptions(max_turns=3)

async for msg in query(prompt="执行复杂任务", options=options):
    if isinstance(msg, ResultMessage):
        if msg.subtype == "error_max_turns":
            print(f"任务在 {msg.num_turns} 轮后被截断")
            print("考虑增大 max_turns 或简化任务")
```

### error_max_budget_usd

超过预算限制：

```python
if msg.subtype == "error_max_budget_usd":
    print(f"预算超出! 已花费: ${msg.total_cost_usd}")
```

### error_during_execution

运行时错误（工具执行失败、内部异常等）：

```python
if msg.subtype == "error_during_execution":
    print("执行过程中发生错误")
    if msg.errors:
        for error in msg.errors:
            print(f"  - {error}")
```

### error_max_structured_output_retries

结构化输出验证多次失败：

```python
if msg.subtype == "error_max_structured_output_retries":
    print("结构化输出验证失败")
    print("模型多次未能生成符合 schema 的输出")
    # 考虑简化 output_schema 或增加重试次数
```

## ResultMessage 的其他错误信息

### is_error 标志

```python
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

async for msg in query(prompt="任务", options=ClaudeAgentOptions()):
    if isinstance(msg, ResultMessage):
        if msg.is_error:
            print(f"查询失败: subtype={msg.subtype}")
        else:
            print("查询成功完成")
```

### api_error_status

当底层 API 返回 HTTP 错误时（如 429 限流、500 服务器错误）：

```python
if isinstance(msg, ResultMessage):
    if msg.api_error_status:
        status = msg.api_error_status
        if status == 429:
            print("API 限流，请稍后重试")
        elif status == 500:
            print("API 服务器错误")
        elif status == 401:
            print("API Key 无效或已过期")
```

### permission_denials

记录查询过程中被拒绝的权限请求：

```python
if isinstance(msg, ResultMessage):
    if msg.permission_denials:
        print("以下操作被拒绝:")
        for denial in msg.permission_denials:
            print(f"  - {denial}")
```

### errors 列表

通用错误信息列表：

```python
if isinstance(msg, ResultMessage):
    if msg.errors:
        for error in msg.errors:
            print(f"错误: {error}")
```

### DeferredToolUse

当 Hook 延迟了一个工具调用时（非错误，但需要应用层处理）：

```python
from claude_agent_sdk import DeferredToolUse

# 在流式消息中可能收到 DeferredToolUse
# 表示某个工具调用被 hook 暂缓执行
# 应用层需要决定是否批准执行
```

## 完整错误处理模板

### 基础模板

```python
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    ResultMessage,
    ClaudeSDKError,
    CLINotFoundError,
    CLIConnectionError,
    ProcessError,
    CLIJSONDecodeError,
)

async def safe_query(prompt: str) -> ResultMessage | None:
    """带完整错误处理的查询函数"""
    try:
        result = None
        async for msg in query(prompt=prompt, options=ClaudeAgentOptions()):
            if isinstance(msg, ResultMessage):
                result = msg

        # 检查 ResultMessage 级别的错误
        if result:
            if result.is_error:
                handle_result_error(result)
            return result

    except CLINotFoundError:
        print("请安装 Claude CLI: npm install -g @anthropic-ai/claude-code")
        raise
    except CLIConnectionError as e:
        print(f"无法连接到 CLI: {e}")
        raise
    except ProcessError as e:
        print(f"CLI 进程错误 (code={e.exit_code}): {e.stderr}")
        raise
    except CLIJSONDecodeError as e:
        print(f"协议错误: {e.original_error}")
        raise
    except ClaudeSDKError as e:
        print(f"未知 SDK 错误: {e}")
        raise

    return None


def handle_result_error(result: ResultMessage):
    """处理 ResultMessage 中的各类错误"""
    match result.subtype:
        case "error_max_turns":
            print(f"任务超出轮次限制 ({result.num_turns} 轮)")
        case "error_max_budget_usd":
            print(f"超出预算 (${result.total_cost_usd})")
        case "error_during_execution":
            print(f"执行错误: {result.errors}")
        case "error_max_structured_output_retries":
            print("结构化输出验证失败")
        case _:
            print(f"未知错误类型: {result.subtype}")
```

### 生产级重试模板

```python
import asyncio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    ResultMessage,
    ProcessError,
    CLIConnectionError,
)

async def resilient_query(
    prompt: str,
    max_retries: int = 3,
    backoff_base: float = 1.0,
) -> ResultMessage | None:
    """带指数退避重试的查询"""
    last_error = None

    for attempt in range(max_retries):
        try:
            result = None
            async for msg in query(prompt=prompt, options=ClaudeAgentOptions()):
                if isinstance(msg, ResultMessage):
                    result = msg

            if result:
                # API 限流 → 重试
                if result.api_error_status == 429:
                    wait = backoff_base * (2 ** attempt)
                    print(f"限流，{wait}s 后重试...")
                    await asyncio.sleep(wait)
                    continue

                # 服务器错误 → 重试
                if result.api_error_status and result.api_error_status >= 500:
                    wait = backoff_base * (2 ** attempt)
                    print(f"服务器错误 {result.api_error_status}，{wait}s 后重试...")
                    await asyncio.sleep(wait)
                    continue

                return result

        except (ProcessError, CLIConnectionError) as e:
            last_error = e
            wait = backoff_base * (2 ** attempt)
            print(f"尝试 {attempt+1}/{max_retries} 失败: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(wait)

    if last_error:
        raise last_error
    return None
```

## 最佳实践

1. **始终检查 `ResultMessage.is_error`** — 即使没有抛出异常，查询也可能逻辑失败。

2. **优先处理 `CLINotFoundError`** — 这是部署时最常见的问题，应该给出清晰的安装指引。

3. **`ProcessError.stderr` 包含有用信息** — 不要忽略 stderr，它通常包含 API 错误的详细描述（如 key 过期的具体原因）。

4. **区分可重试和不可重试错误**：
   - 可重试：429 限流、5xx 服务器错误、`CLIConnectionError`（临时）
   - 不可重试：401 认证失败、`CLINotFoundError`、预算超出

5. **日志记录完整上下文** — 错误发生时记录 `subtype`、`api_error_status`、`errors`、`permission_denials` 等全部字段，便于排查。

6. **不要吞掉异常** — 在生产中，至少要记录日志或上报监控，即使选择不向用户暴露细节。
