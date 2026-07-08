# 结构化输出

结构化输出让 Agent 以符合 JSON Schema 的格式返回结果，适用于需要程序化处理 Agent 响应的场景。

## 基本用法

通过 `output_format` 选项指定输出的 JSON Schema：

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    prompt="你是一个代码分析助手",
    output_format={
        "type": "json_schema",
        "schema": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "代码分析摘要",
                },
                "issues": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "severity": {
                                "type": "string",
                                "enum": ["critical", "warning", "info"],
                            },
                            "description": {"type": "string"},
                            "line": {"type": "integer"},
                            "suggestion": {"type": "string"},
                        },
                        "required": ["severity", "description"],
                    },
                },
                "overall_quality": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10,
                },
            },
            "required": ["summary", "issues", "overall_quality"],
        },
    },
)

result = await query(
    prompt="分析 src/auth.py 的代码质量",
    options=options,
)
```

## 读取结构化输出

结构化输出存储在 `ResultMessage.structured_output` 字段中：

```python
import json

result = await query(prompt="...", options=options)

# result 是 ResultMessage
if result.structured_output is not None:
    data = json.loads(result.structured_output)
    print(f"Summary: {data['summary']}")
    print(f"Quality: {data['overall_quality']}/10")

    for issue in data["issues"]:
        print(f"  [{issue['severity']}] {issue['description']}")
else:
    # 可能因为重试耗尽等原因没有结构化输出
    print("No structured output available")
```

## 验证与重试机制

SDK 内置了自动验证和重试机制：

1. Agent 生成响应后，SDK 验证输出是否符合 JSON Schema
2. 如果验证失败，SDK 自动将错误信息反馈给 Agent，要求重新生成
3. 重试达到上限后，`ResultMessage.subtype` 设置为 `"error_max_structured_output_retries"`

```python
result = await query(prompt="...", options=options)

if result.subtype == "error_max_structured_output_retries":
    print("结构化输出验证失败，已达最大重试次数")
    # 此时 structured_output 可能为 None 或最后一次（无效的）尝试
    # 可以 fallback 到纯文本处理
    print(f"原始文本: {result.text}")
else:
    # 正常获取结构化输出
    data = json.loads(result.structured_output)
```

## 与工具调用的交互

当 Agent 同时使用工具和结构化输出时，执行顺序为：

1. Agent 先执行所有需要的工具调用（Read、Bash 等）
2. 收集工具执行结果
3. 基于工具结果生成符合 Schema 的结构化输出

```python
options = ClaudeAgentOptions(
    prompt="分析项目依赖",
    allowed_tools=["Read", "Bash"],
    permission_mode="bypassPermissions",
    output_format={
        "type": "json_schema",
        "schema": {
            "type": "object",
            "properties": {
                "dependencies": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "version": {"type": "string"},
                            "is_outdated": {"type": "boolean"},
                            "latest_version": {"type": "string"},
                        },
                        "required": ["name", "version", "is_outdated"],
                    },
                },
                "total_count": {"type": "integer"},
                "outdated_count": {"type": "integer"},
            },
            "required": ["dependencies", "total_count", "outdated_count"],
        },
    },
)

# Agent 会先读取 package.json，执行 npm outdated 等，
# 然后将结果整理为结构化 JSON 输出
result = await query(
    prompt="检查 package.json 中的依赖是否有过时的版本",
    options=options,
)
```

## 嵌套 Schema 示例

结构化输出支持任意复杂的嵌套结构：

```python
schema = {
    "type": "object",
    "properties": {
        "project": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "language": {"type": "string"},
                "framework": {"type": "string"},
            },
            "required": ["name", "language"],
        },
        "architecture": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "enum": ["monolith", "microservices", "serverless", "modular"],
                },
                "layers": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "responsibility": {"type": "string"},
                            "dependencies": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["name", "responsibility"],
                    },
                },
            },
            "required": ["pattern", "layers"],
        },
        "recommendations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["performance", "security", "maintainability", "testing"],
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                    },
                    "description": {"type": "string"},
                    "effort_days": {"type": "number"},
                },
                "required": ["category", "priority", "description"],
            },
        },
    },
    "required": ["project", "architecture", "recommendations"],
}

options = ClaudeAgentOptions(
    prompt="你是一个资深架构师",
    allowed_tools=["Read", "Bash"],
    permission_mode="bypassPermissions",
    output_format={"type": "json_schema", "schema": schema},
)
```

## 使用 ClaudeSDKClient（流式模式）

```python
import anyio
import json
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    ResultMessage,
)

async def main():
    options = ClaudeAgentOptions(
        output_format={
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "answer": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "sources": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["answer", "confidence"],
            },
        },
        allowed_tools=["Read"],
        permission_mode="bypassPermissions",
    )

    async with ClaudeSDKClient(options) as client:
        await client.query("README.md 中描述的项目目标是什么？")

        async for msg in client.receive_response():
            if isinstance(msg, ResultMessage):
                if msg.subtype == "error_max_structured_output_retries":
                    print("结构化输出失败")
                elif msg.structured_output:
                    data = json.loads(msg.structured_output)
                    print(f"Answer: {data['answer']}")
                    print(f"Confidence: {data['confidence']}")
                    if data.get("sources"):
                        print(f"Sources: {', '.join(data['sources'])}")

anyio.run(main)
```

## 类型安全建议

结合 Python 的 TypedDict 或 Pydantic 模型使用，提升类型安全：

```python
from typing import TypedDict
import json

# 方式 1: TypedDict
class CodeAnalysis(TypedDict):
    summary: str
    issues: list[dict]
    overall_quality: float

result = await query(prompt="...", options=options)
data: CodeAnalysis = json.loads(result.structured_output)
# IDE 可以提供字段补全

# 方式 2: Pydantic (推荐)
from pydantic import BaseModel

class Issue(BaseModel):
    severity: str
    description: str
    line: int | None = None
    suggestion: str | None = None

class CodeAnalysisResult(BaseModel):
    summary: str
    issues: list[Issue]
    overall_quality: float

result = await query(prompt="...", options=options)
analysis = CodeAnalysisResult.model_validate_json(result.structured_output)
# 完整的类型检查和验证

# 还可以从 Pydantic 模型自动生成 JSON Schema
schema = CodeAnalysisResult.model_json_schema()
options = ClaudeAgentOptions(
    output_format={"type": "json_schema", "schema": schema},
)
```

## 注意事项

- `output_format` 中的 Schema 必须是有效的 JSON Schema（Draft 7+）
- 结构化输出是 Agent 的最终输出，工具调用发生在生成结构化输出之前
- Schema 越复杂，Agent 生成正确输出的难度越高，建议保持合理的复杂度
- `required` 字段确保关键数据一定存在，可选字段用于非关键补充信息
- 重试失败时可以检查 `result.text` 获取原始文本，做降级处理
- 结构化输出与 `include_partial_messages` 兼容，但部分消息中不包含最终的结构化结果
- 枚举类型（`enum`）可以有效约束输出值范围，推荐在分类字段中使用
