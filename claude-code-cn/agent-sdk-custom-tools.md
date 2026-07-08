---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Agent SDK - 自定义工具
description: 使用 Claude Agent SDK 的进程内 MCP 服务器定义自定义工具，让 Claude 调用你的函数、请求 API 和执行领域特定操作，涵盖工具定义、注册、权限、错误处理和返回图片/资源。
category: translation
tags: [claude-code, agent-sdk, translation]
refs:
  - https://code.claude.com/docs/en/agent-sdk/custom-tools.md
  - en-source/agent-sdk/custom-tools.md
---

# 自定义工具

> 使用 Agent SDK 的进程内 MCP 服务器定义自定义工具，让 Claude 调用你的函数、请求 API 和执行领域特定操作

**自定义工具通过让你定义 Claude 可以在对话中调用的函数来扩展 Agent SDK。** 使用 SDK 的进程内 MCP 服务器，你可以让 Claude 访问数据库、外部 API、领域特定逻辑或你应用需要的任何能力。

本指南涵盖如何用输入 schema 和处理器定义工具、将它们打包到 MCP 服务器中、传给 `query`、控制 Claude 可访问的工具，以及错误处理、工具注解和返回非文本内容（如图片）。

## 快速参考

| 你想... | 做法 |
|:---|:---|
| 定义工具 | 使用 [`@tool`](https://code.claude.com/docs/en/agent-sdk/python#tool)（Python）或 [`tool()`](https://code.claude.com/docs/en/agent-sdk/typescript#tool)（TypeScript），指定 name、description、schema 和 handler。参见 [创建自定义工具](#创建自定义工具) |
| 注册工具给 Claude | 用 `create_sdk_mcp_server` / `createSdkMcpServer` 包裹并传给 `query()` 的 `mcpServers`。参见 [调用自定义工具](#调用自定义工具) |
| 预批准工具 | 添加到 allowed tools。参见 [配置 allowed tools](#配置-allowed-tools) |
| 从 Claude 上下文中移除内置工具 | 传 `tools` 数组只列出你想要的内置工具。参见 [配置 allowed tools](#配置-allowed-tools) |
| 让 Claude 并行调用工具 | 对无副作用的工具设置 `readOnlyHint: true`。参见 [添加工具注解](#添加工具注解) |
| 控制 Claude 看到的错误消息 | 返回 `isError: true` 自行组装消息，而非暴露原始异常。参见 [错误处理](#错误处理) |
| 返回图片或文件 | 在 content 数组中使用 `image` 或 `resource` 块。参见 [返回图片和资源](#返回图片和资源) |
| 返回机器可读 JSON 结果 | 在结果上设置 `structuredContent`。参见 [返回结构化数据](#返回结构化数据) |
| 扩展到大量工具 | 使用 [tool search](https://code.claude.com/docs/en/agent-sdk/tool-search) 按需加载 |

## 创建自定义工具

**工具由四部分定义，** 作为参数传给 TypeScript 的 [`tool()`](https://code.claude.com/docs/en/agent-sdk/typescript#tool) 辅助函数或 Python 的 [`@tool`](https://code.claude.com/docs/en/agent-sdk/python#tool) 装饰器：

- **Name：** Claude 用来调用工具的唯一标识符。
- **Description：** 工具做什么。Claude 读取此描述决定何时调用。
- **Input schema：** Claude 必须提供的参数。TypeScript 中始终是 [Zod schema](https://zod.dev/)，handler 的 `args` 自动从中获取类型。Python 中是名称到类型的 dict（如 `{"latitude": float}`），SDK 自动转换为 JSON Schema。Python 装饰器也接受完整 [JSON Schema](https://json-schema.org/understanding-json-schema/about) dict（需要枚举、范围、可选字段或嵌套对象时）。
- **Handler：** Claude 调用工具时运行的异步函数。接收验证后的参数，必须返回包含以下字段的对象：
  - `content`（必须）：结果块数组，每个块的 `type` 为 `"text"`、`"image"`、`"audio"`、`"resource"` 或 `"resource_link"`。
  - `structuredContent`（可选）：JSON 对象，作为机器可读数据随 `content` 一起返回。
  - `isError`（可选）：设为 `true` 表示工具调用失败，Claude 可以据此反应。

定义工具后，用 [`createSdkMcpServer`](https://code.claude.com/docs/en/agent-sdk/typescript#createsdkmcpserver)（TypeScript）或 [`create_sdk_mcp_server`](https://code.claude.com/docs/en/agent-sdk/python#create_sdk_mcp_server)（Python）包裹到服务器中。服务器在应用进程内运行，不是独立进程。

### 天气工具示例

**下面的示例定义一个 `get_temperature` 工具并包裹到 MCP 服务器中。** 仅设置工具；要传给 `query` 并运行，参见下方 [调用自定义工具](#调用自定义工具)。

**Python：**

```python
from typing import Any
import httpx
from claude_agent_sdk import tool, create_sdk_mcp_server


# 定义工具：name, description, input schema, handler
@tool(
    "get_temperature",
    "Get the current temperature at a location",
    {"latitude": float, "longitude": float},
)
async def get_temperature(args: dict[str, Any]) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": args["latitude"],
                "longitude": args["longitude"],
                "current": "temperature_2m",
                "temperature_unit": "fahrenheit",
            },
        )
        data = response.json()

    # 返回 content 数组 - Claude 将此视为工具结果
    return {
        "content": [
            {
                "type": "text",
                "text": f"Temperature: {data['current']['temperature_2m']}°F",
            }
        ]
    }


# 将工具包裹在进程内 MCP 服务器中
weather_server = create_sdk_mcp_server(
    name="weather",
    version="1.0.0",
    tools=[get_temperature],
)
```

**TypeScript：**

```typescript
import { tool, createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";

// 定义工具：name, description, input schema, handler
const getTemperature = tool(
  "get_temperature",
  "Get the current temperature at a location",
  {
    latitude: z.number().describe("Latitude coordinate"), // .describe() 添加 Claude 可见的字段描述
    longitude: z.number().describe("Longitude coordinate")
  },
  async (args) => {
    // args 从 schema 获取类型：{ latitude: number; longitude: number }
    const response = await fetch(
      `https://api.open-meteo.com/v1/forecast?latitude=${args.latitude}&longitude=${args.longitude}&current=temperature_2m&temperature_unit=fahrenheit`
    );
    const data: any = await response.json();

    // 返回 content 数组 - Claude 将此视为工具结果
    return {
      content: [{ type: "text", text: `Temperature: ${data.current.temperature_2m}°F` }]
    };
  }
);

// 将工具包裹在进程内 MCP 服务器中
const weatherServer = createSdkMcpServer({
  name: "weather",
  version: "1.0.0",
  tools: [getTemperature]
});
```

参见 [`tool()`](https://code.claude.com/docs/en/agent-sdk/typescript#tool) TypeScript 参考或 [`@tool`](https://code.claude.com/docs/en/agent-sdk/python#tool) Python 参考了解完整参数详情。

> **提示：** 使参数可选：TypeScript 中给 Zod 字段加 `.default()`。Python 中 dict schema 将每个 key 视为必需，因此将参数从 schema 中去掉，在 description 字符串中提及，handler 中用 `args.get()` 读取。下方 [`get_precipitation_chance` 工具](#添加更多工具) 展示了两种模式。

### 调用自定义工具

**通过 `mcpServers` 选项将创建的 MCP 服务器传给 `query`。** `mcpServers` 中的 key 成为每个工具全限定名的 `{server_name}` 段：`mcp__{server_name}__{tool_name}`。在 `allowedTools` 中列出该名称以免权限提示。

以下代码复用上例中的 `weatherServer` 向 Claude 询问特定位置的天气：

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


async def main():
    options = ClaudeAgentOptions(
        mcp_servers={"weather": weather_server},
        allowed_tools=["mcp__weather__get_temperature"],
    )

    async for message in query(
        prompt="What's the temperature in San Francisco?",
        options=options,
    ):
        # ResultMessage 是所有工具调用完成后的最终消息
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(message.result)


asyncio.run(main())
```

### 添加更多工具

**服务器可以容纳 `tools` 数组中的任意多个工具。** 多个工具时，可以在 `allowedTools` 中逐一列出，或用通配符 `mcp__weather__*` 覆盖服务器暴露的所有工具。

下面的示例向天气服务器添加第二个工具 `get_precipitation_chance`：

**Python：**

```python
# 为同一服务器定义第二个工具
@tool(
    "get_precipitation_chance",
    "Get the hourly precipitation probability for a location. "
    "Optionally pass 'hours' (1-24) to control how many hours to return.",
    {"latitude": float, "longitude": float},
)
async def get_precipitation_chance(args: dict[str, Any]) -> dict[str, Any]:
    # 'hours' 不在 schema 中 - 用 .get() 读取使其可选
    hours = args.get("hours", 12)
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": args["latitude"],
                "longitude": args["longitude"],
                "hourly": "precipitation_probability",
                "forecast_days": 1,
            },
        )
        data = response.json()
    chances = data["hourly"]["precipitation_probability"][:hours]

    return {
        "content": [
            {
                "type": "text",
                "text": f"Next {hours} hours: {'%, '.join(map(str, chances))}%",
            }
        ]
    }


# 用两个工具重建服务器
weather_server = create_sdk_mcp_server(
    name="weather",
    version="1.0.0",
    tools=[get_temperature, get_precipitation_chance],
)
```

此数组中的每个工具在每个 Turn 都消耗上下文窗口空间。如果定义了几十个工具，参见 [tool search](https://code.claude.com/docs/en/agent-sdk/tool-search) 按需加载。

### 添加工具注解

**[工具注解](https://modelcontextprotocol.io/docs/concepts/tools#tool-annotations) 是描述工具行为的可选元数据。** 在 TypeScript 中作为 `tool()` 的第五个参数传入，Python 中通过 `@tool` 装饰器的 `annotations` 关键字参数。所有 hint 字段都是布尔值。

| 字段 | 默认值 | 含义 |
|:---|:---|:---|
| `readOnlyHint` | `false` | 工具不修改环境。控制是否可以与其他只读工具并行调用 |
| `destructiveHint` | `true` | 工具可能执行破坏性更新。仅供参考 |
| `idempotentHint` | `false` | 相同参数重复调用无额外效果。仅供参考 |
| `openWorldHint` | `true` | 工具访问进程外的系统。仅供参考 |

注解是元数据，非强制执行。标记 `readOnlyHint: true` 的工具如果 handler 确实写入磁盘仍然会写。保持注解与 handler 一致。

示例 — 为天气工具添加 `readOnlyHint`：

```python
from claude_agent_sdk import tool, ToolAnnotations


@tool(
    "get_temperature",
    "Get the current temperature at a location",
    {"latitude": float, "longitude": float},
    annotations=ToolAnnotations(
        readOnlyHint=True
    ),  # 让 Claude 可以将此工具与其他只读调用批量执行
)
async def get_temperature(args):
    return {"content": [{"type": "text", "text": "..."}]}
```

参见 `ToolAnnotations` 在 [TypeScript](https://code.claude.com/docs/en/agent-sdk/typescript#toolannotations) 或 [Python](https://code.claude.com/docs/en/agent-sdk/python#toolannotations) 参考中的定义。

## 控制工具访问

天气工具示例注册了服务器并在 `allowedTools` 中列出了工具。本节讲解工具名称的构建方式以及有多个工具或想限制内置工具时如何控制访问。

### 工具名称格式

MCP 工具暴露给 Claude 时，名称遵循特定格式：

- 模式：`mcp__{server_name}__{tool_name}`
- 示例：`weather` 服务器中名为 `get_temperature` 的工具变成 `mcp__weather__get_temperature`

### 配置 allowed tools

**`tools` 选项和 allowed/disallowed 列表影响两个层面：** 可用性（工具是否出现在 Claude 上下文中）和权限（Claude 尝试调用时是否被批准）。`tools` 和裸名 `disallowedTools` 条目改变可用性。`allowedTools` 和有范围的 `disallowedTools` 规则仅改变权限。

| 选项 | 层面 | 效果 |
|:---|:---|:---|
| `tools: ["Read", "Grep"]` | 可用性 | 仅列出的内置工具在 Claude 上下文中。未列出的内置工具被移除。MCP 工具不受影响 |
| `tools: []` | 可用性 | 所有内置工具被移除。Claude 只能使用你的 MCP 工具 |
| allowed tools | 权限 | 列出的工具无需权限提示即可运行。未列出的工具仍可用；调用走 [权限流程](https://code.claude.com/docs/en/agent-sdk/permissions) |
| disallowed tools | 两者 | 裸工具名如 `"Bash"` 从 Claude 上下文中移除工具（等同于从 `tools` 中省略）。有范围的规则如 `"Bash(rm *)"` 保留工具可见但拒绝匹配的调用 |

要完全移除内置工具，从 `tools` 中省略或在 `disallowedTools`（Python：`disallowed_tools`）中列出其裸名；两者都让工具不在上下文中，Claude 不会尝试使用它。有范围的 `disallowedTools` 规则阻止匹配的调用但保留工具可见，Claude 可能浪费一个 Turn 去尝试它。参见 [配置权限](https://code.claude.com/docs/en/agent-sdk/permissions) 了解完整评估顺序。

## 错误处理

**Handler 错误不会终止 Agent 循环。** SDK 的进程内 MCP 服务器捕获未处理异常并作为错误结果返回，因此你如何报告错误决定了 Claude 读到什么，而非查询是否失败：

| 发生了什么 | 结果 |
|:---|:---|
| Handler 抛出未捕获异常 | MCP 服务器将其转换为携带原始异常消息的错误结果。Claude 看到该消息，Agent 循环继续 |
| Handler 捕获错误并返回 `isError: true`（TS）/ `"is_error": True`（Python） | Claude 看到你组装的消息。你可以添加原始异常缺少的上下文（如哪个请求失败或该尝试什么） |

两种情况下 Claude 都可以重试、尝试不同工具或解释失败。当原始异常消息不足以让 Claude 行动时，自行捕获错误。

示例 — 在 handler 内捕获两种失败并组装 Claude 看到的错误消息：

```python
import json
import httpx
from typing import Any


@tool(
    "fetch_data",
    "Fetch data from an API",
    {"endpoint": str},  # 简单 schema
)
async def fetch_data(args: dict[str, Any]) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(args["endpoint"])
            if response.status_code != 200:
                # 作为工具结果返回失败以便 Claude 反应
                # is_error 标记这是失败调用而非奇怪的数据
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"API error: {response.status_code} {response.reason_phrase}",
                        }
                    ],
                    "is_error": True,
                }

            data = response.json()
            return {"content": [{"type": "text", "text": json.dumps(data, indent=2)}]}
    except Exception as e:
        # 组装 Claude 读到的消息。未捕获异常会以原始 str(e) 到达 Claude
        return {
            "content": [{"type": "text", "text": f"Failed to fetch data: {str(e)}"}],
            "is_error": True,
        }
```

## 返回图片和资源

**工具结果中的 `content` 数组接受 `text`、`image`、`audio`、`resource` 和 `resource_link` 块。** 可以在同一响应中混合使用。TypeScript 中 audio 块会保存到磁盘，Claude 收到包含保存文件路径的 text 块；Python 中 SDK 丢弃 audio 块并记录警告。Resource link 块被转换为包含链接的 name、URI 和 description 的 text 块。

### 图片

**image 块以内联方式携带图片字节，编码为 base64。** 没有 URL 字段。要返回 URL 上的图片，在 handler 中获取它、读取响应字节并 base64 编码后返回。结果作为视觉输入处理。

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `type` | `"image"` | |
| `data` | `string` | Base64 编码字节。仅原始 base64，不带 `data:image/...;base64,` 前缀 |
| `mimeType` | `string` | 必须。如 `image/png`、`image/jpeg`、`image/webp`、`image/gif` |

```python
import base64
import httpx


# 定义从 URL 获取图片并返回给 Claude 的工具
@tool("fetch_image", "Fetch an image from a URL and return it to Claude", {"url": str})
async def fetch_image(args):
    async with httpx.AsyncClient() as client:  # 获取图片字节
        response = await client.get(args["url"])

    return {
        "content": [
            {
                "type": "image",
                "data": base64.b64encode(response.content).decode(
                    "ascii"
                ),  # Base64 编码原始字节
                "mimeType": response.headers.get(
                    "content-type", "image/png"
                ),  # 从响应读取 MIME 类型
            }
        ]
    }
```

### 资源（Resources）

**resource 块嵌入一段由 URI 标识的内容。** URI 是给 Claude 引用的标签；实际内容在块的 `text` 或 `blob` 字段中。当工具产出的内容适合用名称稍后引用时使用，如生成的文件或外部系统的记录。

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `type` | `"resource"` | |
| `resource.uri` | `string` | 内容标识符。任何 URI scheme |
| `resource.text` | `string` | 文本内容。提供此字段或 `blob`，不能两者都有 |
| `resource.blob` | `string` | Base64 编码的二进制内容。仅 TypeScript；Python SDK 丢弃二进制资源并记录警告 |
| `resource.mimeType` | `string` | 可选 |

示例 — 从工具 handler 返回 resource 块：

```python
return {
    "content": [
        {
            "type": "resource",
            "resource": {
                "uri": "file:///tmp/report.md",  # 给 Claude 引用的标签，非 SDK 读取的路径
                "mimeType": "text/markdown",
                "text": "# Report\n...",  # 实际内容，内联
            },
        }
    ]
}
```

这些块形状来自 MCP `CallToolResult` 类型。参见 [MCP 规范](https://modelcontextprotocol.io/specification/2025-06-18/server/tools#tool-result) 了解完整定义。

## 返回结构化数据

**`structuredContent` 是结果上的可选 JSON 对象，独立于 `content` 数组。** 用它返回原始值让 Claude 以精确字段读取，而非从文本字符串或图片中解析。

设置 `structuredContent` 时，Claude 收到 JSON 加上 `content` 中的 image 或 resource 块。`content` 中的 text 块不转发，因为假定它们是结构化数据的重复。下面的示例在同一 handler 中将图表渲染为 image 块并在 `structuredContent` 中返回背后的数据点。

```typescript
return {
  content: [
    {
      type: "image",
      data: chartPngBuffer.toString("base64"),
      mimeType: "image/png"
    }
  ],
  structuredContent: {
    series: "temperature_2m",
    unit: "fahrenheit",
    points: [62.1, 63.4, 65.0, 64.2]
  }
};
```

> Python 的 `@tool` 装饰器仅转发 handler 返回 dict 中的 `content` 和 `is_error`。要从 Python 返回 `structuredContent`，运行 [独立 MCP 服务器](https://code.claude.com/docs/en/agent-sdk/mcp) 而非进程内 SDK 服务器。

## 示例：单位转换器

**此工具在长度、温度和重量的单位间转换值。** 用户可以问 "convert 100 kilometers to miles" 或 "what is 72°F in Celsius"，Claude 从请求中选择正确的单位类型和单位。

它演示了两种模式：

- **枚举 schema：** `unit_type` 被约束为固定值集。TypeScript 中用 `z.enum()`。Python 中 dict schema 不支持枚举，需要完整 JSON Schema dict。
- **不支持的输入处理：** 转换对未找到时，handler 返回 `isError: true` 让 Claude 告诉用户出了什么问题，而非将失败当作正常结果。

```python
from typing import Any
from claude_agent_sdk import tool, create_sdk_mcp_server


# TypeScript 中的 z.enum() 在 JSON Schema 中变为 "enum" 约束。
# Dict schema 没有等价物，因此需要完整 JSON Schema。
@tool(
    "convert_units",
    "Convert a value from one unit to another",
    {
        "type": "object",
        "properties": {
            "unit_type": {
                "type": "string",
                "enum": ["length", "temperature", "weight"],
                "description": "Category of unit",
            },
            "from_unit": {
                "type": "string",
                "description": "Unit to convert from, e.g. kilometers, fahrenheit, pounds",
            },
            "to_unit": {"type": "string", "description": "Unit to convert to"},
            "value": {"type": "number", "description": "Value to convert"},
        },
        "required": ["unit_type", "from_unit", "to_unit", "value"],
    },
)
async def convert_units(args: dict[str, Any]) -> dict[str, Any]:
    conversions = {
        "length": {
            "kilometers_to_miles": lambda v: v * 0.621371,
            "miles_to_kilometers": lambda v: v * 1.60934,
            "meters_to_feet": lambda v: v * 3.28084,
            "feet_to_meters": lambda v: v * 0.3048,
        },
        "temperature": {
            "celsius_to_fahrenheit": lambda v: (v * 9) / 5 + 32,
            "fahrenheit_to_celsius": lambda v: (v - 32) * 5 / 9,
            "celsius_to_kelvin": lambda v: v + 273.15,
            "kelvin_to_celsius": lambda v: v - 273.15,
        },
        "weight": {
            "kilograms_to_pounds": lambda v: v * 2.20462,
            "pounds_to_kilograms": lambda v: v * 0.453592,
            "grams_to_ounces": lambda v: v * 0.035274,
            "ounces_to_grams": lambda v: v * 28.3495,
        },
    }

    key = f"{args['from_unit']}_to_{args['to_unit']}"
    fn = conversions.get(args["unit_type"], {}).get(key)

    if not fn:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Unsupported conversion: {args['from_unit']} to {args['to_unit']}",
                }
            ],
            "is_error": True,
        }

    result = fn(args["value"])
    return {
        "content": [
            {
                "type": "text",
                "text": f"{args['value']} {args['from_unit']} = {result:.4f} {args['to_unit']}",
            }
        ]
    }


converter_server = create_sdk_mcp_server(
    name="converter",
    version="1.0.0",
    tools=[convert_units],
)
```

服务器定义后，像天气示例一样传给 `query`。下面的示例在循环中发送三个不同 prompt 展示同一工具处理不同单位类型：

```python
import asyncio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    ResultMessage,
    AssistantMessage,
    ToolUseBlock,
)


async def main():
    options = ClaudeAgentOptions(
        mcp_servers={"converter": converter_server},
        allowed_tools=["mcp__converter__convert_units"],
    )

    prompts = [
        "Convert 100 kilometers to miles.",
        "What is 72°F in Celsius?",
        "How many pounds is 5 kilograms?",
    ]

    for prompt in prompts:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, ToolUseBlock):
                        print(f"[tool call] {block.name}({block.input})")
            elif isinstance(message, ResultMessage) and message.subtype == "success":
                print(f"Q: {prompt}\nA: {message.result}\n")


asyncio.run(main())
```

## 下一步

**自定义工具将异步函数包裹为标准接口。** 可以在同一服务器中混合本页的模式：一个服务器可以同时包含数据库工具、API 网关工具和图片渲染器。

后续方向：

- 服务器增长到几十个工具时，参见 [tool search](https://code.claude.com/docs/en/agent-sdk/tool-search) 延迟加载。
- 要连接外部 MCP 服务器（文件系统、GitHub、Slack）而非自建，参见 [连接 MCP 服务器](https://code.claude.com/docs/en/agent-sdk/mcp)。
- 要控制哪些工具自动运行、哪些需审批，参见 [配置权限](https://code.claude.com/docs/en/agent-sdk/permissions)。

## 相关文档

- [TypeScript SDK 参考](https://code.claude.com/docs/en/agent-sdk/typescript)
- [Python SDK 参考](https://code.claude.com/docs/en/agent-sdk/python)
- [MCP 文档](https://modelcontextprotocol.io)
- [SDK 概览](https://code.claude.com/docs/en/agent-sdk/overview)
