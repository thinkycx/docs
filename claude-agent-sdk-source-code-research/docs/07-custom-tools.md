# 自定义工具系统

SDK 支持定义在 Python 进程内运行的自定义工具，通过 MCP (Model Context Protocol) 协议集成到 Claude。

## @tool 装饰器

```python
def tool(
    name: str,
    description: str,
    input_schema: type | dict[str, Any],
    annotations: ToolAnnotations | None = None,
) -> Callable[[handler], SdkMcpTool]
```

### 基础用法

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("add", "加两个数", {"a": float, "b": float})
async def add(args):
    result = args["a"] + args["b"]
    return {"content": [{"type": "text", "text": f"结果: {result}"}]}
```

### 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `name` | str | 工具唯一标识符，Claude 用此名称调用 |
| `description` | str | 工具功能描述，帮助 Claude 理解何时使用 |
| `input_schema` | type \| dict | 输入参数定义 |
| `annotations` | ToolAnnotations \| None | 工具行为注解 |

### 输入 Schema 三种写法

#### 方式 1：简单字典
```python
@tool("greet", "问候用户", {"name": str, "language": str})
async def greet(args):
    return {"content": [{"type": "text", "text": f"Hello, {args['name']}!"}]}
```

#### 方式 2：TypedDict（推荐复杂场景）
```python
from typing import TypedDict, Annotated

class SearchInput(TypedDict):
    query: Annotated[str, "搜索关键词"]
    max_results: Annotated[int, "最大结果数"]

@tool("search", "搜索文档", SearchInput)
async def search(args):
    ...
```

#### 方式 3：原生 JSON Schema
```python
schema = {
    "type": "object",
    "properties": {
        "text": {"type": "string", "description": "要翻译的文本"},
        "target_lang": {"type": "string", "enum": ["zh", "en", "ja"]}
    },
    "required": ["text", "target_lang"]
}

@tool("translate", "翻译文本", schema)
async def translate(args):
    ...
```

### 支持的 Python 类型映射

| Python 类型 | JSON Schema 类型 |
|-------------|-----------------|
| `str` | `"string"` |
| `int` | `"integer"` |
| `float` | `"number"` |
| `bool` | `"boolean"` |
| `list` | `"array"` |
| `list[str]` | `"array"` + items |
| `dict` | `"object"` |
| `Optional[X]` / `X \| None` | X 的 schema |
| `Annotated[X, "desc"]` | X + description |
| `TypedDict` | 完整 object schema |

## 工具返回值格式

```python
# 正常返回文本
return {"content": [{"type": "text", "text": "结果文本"}]}

# 返回错误
return {"content": [{"type": "text", "text": "错误信息"}], "is_error": True}

# 返回图片
return {"content": [{"type": "image", "data": base64_data, "mimeType": "image/png"}]}

# 返回资源链接
return {"content": [{"type": "resource_link", "name": "文件", "uri": "file:///path"}]}

# 多个内容块
return {"content": [
    {"type": "text", "text": "找到 3 个结果:"},
    {"type": "text", "text": "1. ..."},
    {"type": "text", "text": "2. ..."},
]}
```

## create_sdk_mcp_server()

```python
def create_sdk_mcp_server(
    name: str,
    version: str = "1.0.0",
    tools: list[SdkMcpTool] | None = None,
) -> McpSdkServerConfig
```

创建进程内 MCP 服务器，将多个工具组合为一个服务：

```python
@tool("add", "加法", {"a": float, "b": float})
async def add(args):
    return {"content": [{"type": "text", "text": str(args["a"] + args["b"])}]}

@tool("multiply", "乘法", {"a": float, "b": float})
async def multiply(args):
    return {"content": [{"type": "text", "text": str(args["a"] * args["b"])}]}

calculator = create_sdk_mcp_server("calc", tools=[add, multiply])
```

## 使用自定义工具

```python
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(
    mcp_servers={"calc": calculator},
    allowed_tools=["mcp__calc__add", "mcp__calc__multiply"],
)

async for msg in query(prompt="计算 15 * 7 + 3", options=options):
    ...
```

## 工具命名规则

SDK MCP 工具的名称遵循格式：`mcp__<server_name>__<tool_name>`

- `server_name` — `mcp_servers` 字典的键
- `tool_name` — `@tool` 装饰器中的 name 参数

例如：
```python
mcp_servers={"weather": weather_server}
# 工具名: mcp__weather__get_forecast
```

## ToolAnnotations

```python
from mcp.types import ToolAnnotations

@tool(
    "read_file", "读取文件内容", {"path": str},
    annotations=ToolAnnotations(
        readOnlyHint=True,       # 只读操作
        destructiveHint=False,    # 非破坏性
        idempotentHint=True,     # 幂等
        openWorldHint=False,      # 不访问外部
    )
)
async def read_file(args):
    ...
```

注解帮助 Claude 理解工具的安全特性，影响权限评估。

## 访问应用状态

工具可以直接访问 Python 进程中的变量：

```python
database = {}  # 应用状态

@tool("store", "存储数据", {"key": str, "value": str})
async def store(args):
    database[args["key"]] = args["value"]
    return {"content": [{"type": "text", "text": f"已存储 {args['key']}"}]}

@tool("retrieve", "检索数据", {"key": str})
async def retrieve(args):
    value = database.get(args["key"], "未找到")
    return {"content": [{"type": "text", "text": value}]}
```

## 错误处理最佳实践

```python
@tool("divide", "除法", {"a": float, "b": float})
async def divide(args):
    if args["b"] == 0:
        return {
            "content": [{"type": "text", "text": "错误：除数不能为零"}],
            "is_error": True
        }
    result = args["a"] / args["b"]
    return {"content": [{"type": "text", "text": f"{result}"}]}
```

设置 `is_error: True` 后，Claude 会知道工具执行失败，并尝试其他方式完成任务。

## 与 ClaudeSDKClient 配合

```python
async with ClaudeSDKClient(options) as client:
    await client.query("使用计算器算 100 / 3")
    async for msg in client.receive_response():
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, ToolUseBlock):
                    print(f"调用: {block.name}({block.input})")
                elif isinstance(block, TextBlock):
                    print(block.text)
```
