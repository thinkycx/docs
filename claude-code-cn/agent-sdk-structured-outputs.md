---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Agent SDK - 结构化输出
description: 介绍如何通过 JSON Schema、Zod 或 Pydantic 从 Agent 工作流中获取经过验证的结构化 JSON 数据，实现类型安全的多轮工具调用后结构化返回。
category: translation
tags: [claude-code, agent-sdk, translation]
refs:
  - https://code.claude.com/docs/en/agent-sdk/structured-outputs
  - en-source/agent-sdk/structured-outputs.md
---

# 从 Agent 获取结构化输出

> 通过 JSON Schema、Zod 或 Pydantic 从 Agent 工作流返回经过验证的 JSON。在多轮工具调用之后，获得类型安全的结构化数据。

**结构化输出让你精确定义需要从 Agent 获取的数据格式。** Agent 可以使用任何工具完成任务，最终返回符合你 schema 定义的经过验证的 JSON。定义一个 [JSON Schema](https://json-schema.org/understanding-json-schema/about) 来描述你需要的数据结构，SDK 会根据 schema 验证输出，不匹配时自动重试。如果在重试限制内验证仍未通过，返回错误而非结构化数据；详见 [错误处理](#错误处理)。

**如需完整类型安全，可用 Zod（TypeScript）或 Pydantic（Python）定义 schema，获取强类型对象。** 详见 [类型安全的 Schema](#类型安全的-schema-zod-与-pydantic)。

## 为什么需要结构化输出？

**Agent 默认返回自由文本，适合聊天但不适合程序化处理。** 结构化输出提供可直接传递给应用逻辑、数据库或 UI 组件的类型化数据。

以一个菜谱应用为例：Agent 搜索网页并返回菜谱。

| 对比维度 | 无结构化输出 | 有结构化输出 |
|:---|:---|:---|
| 返回格式 | 自由文本（Markdown） | 类型化 JSON |
| 使用方式 | 需手动解析标题、时间、配料等 | 直接用于 UI 渲染 |
| 一致性 | 每次格式可能不同 | 严格符合 schema |

**无结构化输出时的返回示例：**

```text
Here's a classic chocolate chip cookie recipe!

**Chocolate Chip Cookies**
Prep time: 15 minutes | Cook time: 10 minutes

Ingredients:
- 2 1/4 cups all-purpose flour
- 1 cup butter, softened
...
```

你需要自行解析标题、将 "15 minutes" 转为数字、分离配料和步骤，还要处理不同响应间的格式不一致问题。

**有结构化输出时的返回示例：**

```json
{
  "name": "Chocolate Chip Cookies",
  "prep_time_minutes": 15,
  "cook_time_minutes": 10,
  "ingredients": [
    { "item": "all-purpose flour", "amount": 2.25, "unit": "cups" },
    { "item": "butter, softened", "amount": 1, "unit": "cup" }
  ],
  "steps": ["Preheat oven to 375°F", "Cream butter and sugar"]
}
```

类型化数据，可直接用于 UI。

## 快速开始

**定义 JSON Schema，通过 `outputFormat`（TypeScript）或 `output_format`（Python）传入 `query()`。** Agent 完成时，结果消息包含 `structured_output` 字段，存放经过验证且符合 schema 的数据。

以下示例让 Agent 调研 Anthropic 并以结构化输出返回公司名称、成立年份和总部地址。

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

// 定义你期望的返回数据格式
const schema = {
  type: "object",
  properties: {
    company_name: { type: "string" },
    founded_year: { type: "number" },
    headquarters: { type: "string" }
  },
  required: ["company_name"]
};

for await (const message of query({
  prompt: "Research Anthropic and provide key company information",
  options: {
    outputFormat: {
      type: "json_schema",
      schema: schema
    }
  }
})) {
  // 结果消息的 structured_output 包含验证后的数据
  if (message.type === "result" && message.subtype === "success" && message.structured_output) {
    console.log(message.structured_output);
    // { company_name: "Anthropic", founded_year: 2021, headquarters: "San Francisco, CA" }
  }
}
```

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

# 定义你期望的返回数据格式
schema = {
    "type": "object",
    "properties": {
        "company_name": {"type": "string"},
        "founded_year": {"type": "number"},
        "headquarters": {"type": "string"},
    },
    "required": ["company_name"],
}


async def main():
    async for message in query(
        prompt="Research Anthropic and provide key company information",
        options=ClaudeAgentOptions(
            output_format={"type": "json_schema", "schema": schema}
        ),
    ):
        # 结果消息的 structured_output 包含验证后的数据
        if isinstance(message, ResultMessage) and message.structured_output:
            print(message.structured_output)
            # {'company_name': 'Anthropic', 'founded_year': 2021, 'headquarters': 'San Francisco, CA'}


asyncio.run(main())
```

## 类型安全的 Schema：Zod 与 Pydantic

**不必手写 JSON Schema，可用 Zod（TypeScript）或 Pydantic（Python）定义 schema。** 这些库自动生成 JSON Schema，并让你将响应解析为全类型对象，在整个代码库中享有自动补全和类型检查。

以下示例定义了一个功能实现计划的 schema，包含摘要、步骤列表（每步有复杂度等级）和潜在风险。Agent 规划功能并返回类型化的 `FeaturePlan` 对象，你可以通过 `plan.summary` 和 `plan.steps` 以完整类型安全的方式访问属性。

```typescript
import { z } from "zod";
import { query } from "@anthropic-ai/claude-agent-sdk";

// 用 Zod 定义 schema
const FeaturePlan = z.object({
  feature_name: z.string(),
  summary: z.string(),
  steps: z.array(
    z.object({
      step_number: z.number(),
      description: z.string(),
      estimated_complexity: z.enum(["low", "medium", "high"])
    })
  ),
  risks: z.array(z.string())
});

type FeaturePlan = z.infer<typeof FeaturePlan>;

// 转换为 JSON Schema
const schema = z.toJSONSchema(FeaturePlan);

// 在 query 中使用
for await (const message of query({
  prompt:
    "Plan how to add dark mode support to a React app. Break it into implementation steps.",
  options: {
    outputFormat: {
      type: "json_schema",
      schema: schema
    }
  }
})) {
  if (message.type === "result" && message.subtype === "success" && message.structured_output) {
    // 验证并获取完整类型的结果
    const parsed = FeaturePlan.safeParse(message.structured_output);
    if (parsed.success) {
      const plan: FeaturePlan = parsed.data;
      console.log(`Feature: ${plan.feature_name}`);
      console.log(`Summary: ${plan.summary}`);
      plan.steps.forEach((step) => {
        console.log(`${step.step_number}. [${step.estimated_complexity}] ${step.description}`);
      });
    }
  }
}
```

```python
import asyncio
from pydantic import BaseModel
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


class Step(BaseModel):
    step_number: int
    description: str
    estimated_complexity: str  # 'low', 'medium', 'high'


class FeaturePlan(BaseModel):
    feature_name: str
    summary: str
    steps: list[Step]
    risks: list[str]


async def main():
    async for message in query(
        prompt="Plan how to add dark mode support to a React app. Break it into implementation steps.",
        options=ClaudeAgentOptions(
            output_format={
                "type": "json_schema",
                "schema": FeaturePlan.model_json_schema(),
            }
        ),
    ):
        if isinstance(message, ResultMessage) and message.structured_output:
            # 验证并获取完整类型的结果
            plan = FeaturePlan.model_validate(message.structured_output)
            print(f"Feature: {plan.feature_name}")
            print(f"Summary: {plan.summary}")
            for step in plan.steps:
                print(
                    f"{step.step_number}. [{step.estimated_complexity}] {step.description}"
                )


asyncio.run(main())
```

**使用 Zod/Pydantic 的优势：**

| 优势 | 说明 |
|:---|:---|
| 完整类型推断 | TypeScript 自动推断类型，Python 提供 type hints |
| 运行时验证 | 通过 `safeParse()` 或 `model_validate()` 进行验证 |
| 更好的错误信息 | 验证失败时提供清晰的错误描述 |
| 可组合、可复用 | schema 可拆分、组合、跨模块复用 |

## 输出格式配置

**`outputFormat`（TypeScript）或 `output_format`（Python）接受一个对象，包含以下字段：**

| 字段 | 说明 |
|:---|:---|
| `type` | 设为 `"json_schema"` 以启用结构化输出 |
| `schema` | 一个 [JSON Schema](https://json-schema.org/understanding-json-schema/about) 对象，定义输出结构。可通过 Zod 的 `z.toJSONSchema()` 或 Pydantic 的 `.model_json_schema()` 生成 |

SDK 支持标准 JSON Schema 特性，包括所有基本类型（object、array、string、number、boolean、null）、`enum`、`const`、`required`、嵌套对象和 `$ref` 定义。完整的支持特性和限制列表见 [JSON Schema 限制](https://platform.claude.com/docs/en/build-with-claude/structured-outputs#json-schema-limitations)。

## 示例：TODO 追踪 Agent

**此示例演示结构化输出如何与多步工具调用配合工作。** Agent 需要在代码库中查找 TODO 注释，再对每个注释查询 git blame 信息。Agent 自主决定使用哪些工具（Grep 搜索、Bash 执行 git 命令），将结果组合为一个结构化响应。

schema 中包含可选字段（`author` 和 `date`），因为并非所有文件都能获取到 git blame 信息。Agent 填入能找到的信息，其余省略。

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

// 定义 TODO 提取的数据结构
const todoSchema = {
  type: "object",
  properties: {
    todos: {
      type: "array",
      items: {
        type: "object",
        properties: {
          text: { type: "string" },
          file: { type: "string" },
          line: { type: "number" },
          author: { type: "string" },
          date: { type: "string" }
        },
        required: ["text", "file", "line"]
      }
    },
    total_count: { type: "number" }
  },
  required: ["todos", "total_count"]
};

// Agent 使用 Grep 查找 TODO，Bash 获取 git blame 信息
for await (const message of query({
  prompt: "Find all TODO comments in this codebase and identify who added them",
  options: {
    outputFormat: {
      type: "json_schema",
      schema: todoSchema
    }
  }
})) {
  if (message.type === "result" && message.subtype === "success" && message.structured_output) {
    const data = message.structured_output as { total_count: number; todos: Array<{ file: string; line: number; text: string; author?: string; date?: string }> };
    console.log(`Found ${data.total_count} TODOs`);
    data.todos.forEach((todo) => {
      console.log(`${todo.file}:${todo.line} - ${todo.text}`);
      if (todo.author) {
        console.log(`  Added by ${todo.author} on ${todo.date}`);
      }
    });
  }
}
```

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

# 定义 TODO 提取的数据结构
todo_schema = {
    "type": "object",
    "properties": {
        "todos": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "file": {"type": "string"},
                    "line": {"type": "number"},
                    "author": {"type": "string"},
                    "date": {"type": "string"},
                },
                "required": ["text", "file", "line"],
            },
        },
        "total_count": {"type": "number"},
    },
    "required": ["todos", "total_count"],
}


async def main():
    # Agent 使用 Grep 查找 TODO，Bash 获取 git blame 信息
    async for message in query(
        prompt="Find all TODO comments in this codebase and identify who added them",
        options=ClaudeAgentOptions(
            output_format={"type": "json_schema", "schema": todo_schema}
        ),
    ):
        if isinstance(message, ResultMessage) and message.structured_output:
            data = message.structured_output
            print(f"Found {data['total_count']} TODOs")
            for todo in data["todos"]:
                print(f"{todo['file']}:{todo['line']} - {todo['text']}")
                if "author" in todo:
                    print(f"  Added by {todo['author']} on {todo['date']}")


asyncio.run(main())
```

## 错误处理

**当 Agent 无法生成符合 schema 的有效 JSON 时，结构化输出生成会失败。** 典型原因包括：schema 对于任务而言过于复杂、任务本身含义模糊、Agent 达到重试上限仍无法修复验证错误。此外也可能在无验证失败的情况下发生：[模型回退](https://code.claude.com/docs/en/model-config#automatic-model-fallback) 可能在流式传输过程中撤回已完成的输出，如果没有重试替代，运行以同样的错误结束。检查结果消息的 `errors` 字段可以区分这两种原因，以便调试 schema。

**结果消息的 `subtype` 字段指示发生了什么：**

| subtype | 含义 |
|:---|:---|
| `success` | 输出已成功生成并通过验证 |
| `error_max_structured_output_retries` | 多次尝试后仍无有效输出（验证失败，或模型回退撤回后无成功重试） |

以下示例检查 `subtype` 字段来判断输出是否成功生成：

```typescript
for await (const msg of query({
  prompt: "Extract contact info from the document",
  options: {
    outputFormat: {
      type: "json_schema",
      schema: contactSchema
    }
  }
})) {
  if (msg.type === "result") {
    if (msg.subtype === "success" && msg.structured_output) {
      // 使用验证后的输出
      console.log(msg.structured_output);
    } else if (msg.subtype === "error_max_structured_output_retries") {
      // 处理失败 - 用更简单的 prompt 重试、回退到非结构化输出等
      console.error("Could not produce valid output");
    }
  }
}
```

```python
async for message in query(
    prompt="Extract contact info from the document",
    options=ClaudeAgentOptions(
        output_format={"type": "json_schema", "schema": contact_schema}
    ),
):
    if isinstance(message, ResultMessage):
        if message.subtype == "success" and message.structured_output:
            # 使用验证后的输出
            print(message.structured_output)
        elif message.subtype == "error_max_structured_output_retries":
            # 处理失败
            print("Could not produce valid output")
```

**避免错误的建议：**

| 建议 | 说明 |
|:---|:---|
| 保持 schema 聚焦 | 深层嵌套且有大量必填字段的 schema 更难满足。先简单再逐步加复杂度 |
| schema 与任务匹配 | 如果任务可能不包含 schema 所需的全部信息，将那些字段设为可选 |
| 使用清晰的 prompt | 含义模糊的 prompt 让 Agent 更难确定应该产出什么 |

## 相关资源

- [JSON Schema 文档](https://json-schema.org/)：学习 JSON Schema 语法，定义嵌套对象、数组、枚举和验证约束
- [API 结构化输出](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)：在 Claude API 中直接使用结构化输出，适用于无需工具调用的单轮请求
- [自定义工具](https://code.claude.com/docs/en/agent-sdk/custom-tools)：为 Agent 提供自定义工具，在返回结构化输出之前调用
