"""
create: 2026-07-08
update: 2026-07-08
description:
    演示使用 output_format (JSON Schema) 获取结构化输出的功能。
    定义包含 language/year_created/creator/paradigms/is_statically_typed 等字段的 Schema,
    让 Claude 返回 Python 语言信息。结果通过 ResultMessage.structured_output 获取解析后的 dict。
    核心 API: ClaudeAgentOptions(output_format={"type":"json_schema","schema":...}), ResultMessage.structured_output
expect_output:
    - 打印 JSON Schema 定义
    - AssistantMessage 包含原始文本描述
    - ResultMessage.structured_output 为 dict 类型
    - 结构化输出包含 language="Python", year_created=1991, creator 含 "Guido"
    - paradigms 为列表, is_statically_typed=False
usage:
    cd demos && uv run python 29_structured_output.py
"""

import json

import anyio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)


async def main():
    print("=== Demo: 结构化输出 (output_format + JSON Schema) ===\n")

    # 定义输出的 JSON Schema
    output_schema = {
        "type": "json_schema",
        "schema": {
            "type": "object",
            "properties": {
                "language": {
                    "type": "string",
                    "description": "Programming language name",
                },
                "year_created": {
                    "type": "integer",
                    "description": "Year the language was first released",
                },
                "creator": {
                    "type": "string",
                    "description": "Name of the language creator",
                },
                "paradigms": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Programming paradigms supported",
                },
                "is_statically_typed": {
                    "type": "boolean",
                    "description": "Whether the language is statically typed",
                },
                "popularity_rank": {
                    "type": "integer",
                    "description": "Approximate TIOBE index rank (2024)",
                },
            },
            "required": [
                "language",
                "year_created",
                "creator",
                "paradigms",
                "is_statically_typed",
            ],
        },
    }

    print("JSON Schema 定义:")
    print(json.dumps(output_schema["schema"]["properties"], indent=2, ensure_ascii=False))
    print()

    options = ClaudeAgentOptions(
        output_format=output_schema,
        max_turns=1,
        permission_mode="bypassPermissions",
    )

    prompt = "Tell me about Python as a programming language."
    print(f"Prompt: '{prompt}'\n")

    structured_result = None

    async for msg in query(prompt=prompt, options=options):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"  [Assistant raw text] {block.text[:200]}")
        elif isinstance(msg, ResultMessage):
            print(f"\n  [Result] session_id={msg.session_id}")
            print(f"  [Result] is_error={msg.is_error}")
            structured_result = msg.structured_output

    # --- 展示结构化输出 ---
    print("\n--- ResultMessage.structured_output ---")
    if structured_result:
        print(f"  类型: {type(structured_result).__name__}")
        print(f"  内容:")
        if isinstance(structured_result, dict):
            for key, value in structured_result.items():
                print(f"    {key}: {value}")
        else:
            print(f"    {structured_result}")
    else:
        print("  (无结构化输出, 可能因为 CLI 版本不支持)")
        print("  提示: 检查 ResultMessage 的 result 字段作为备用")

    # --- 更复杂的 Schema 示例 ---
    print("\n--- 其他 output_format 示例 ---")
    print("""
# 简单对象
output_format = {
    "type": "json_schema",
    "schema": {
        "type": "object",
        "properties": {
            "answer": {"type": "string"},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        },
        "required": ["answer", "confidence"],
    }
}

# 嵌套对象
output_format = {
    "type": "json_schema",
    "schema": {
        "type": "object",
        "properties": {
            "analysis": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "issues": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                                "description": {"type": "string"},
                            }
                        }
                    }
                }
            }
        }
    }
}
""")

    print("=== Demo 完成 ===")


if __name__ == "__main__":
    anyio.run(main)
