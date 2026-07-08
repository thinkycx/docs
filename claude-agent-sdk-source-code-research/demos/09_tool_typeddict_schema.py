"""
create: 2026-07-08
update: 2026-07-08
description:
    使用 TypedDict 定义复杂工具 schema。演示核心 API: @tool with TypedDict schema,
    Annotated for descriptions, NotRequired for optional fields。
    用 TypedDict + Annotated 定义结构化的工具参数（含类型、描述、可选字段），
    实现 get_weather 和 convert_temperature 两个工具，展示比 dict schema 更精确的参数定义方式。
expect_output:
    - Claude 调用 get_weather({'city': 'Tokyo'}) 返回 28 celsius
    - Claude 调用 convert_temperature 将 28 celsius 转为 fahrenheit (82.4)
    - 最终文本包含 Tokyo 的温度信息（摄氏和华氏）
    - ResultMessage 显示 num_turns=3
usage:
    cd demos && uv run python 09_tool_typeddict_schema.py
"""

import sys
from typing import Annotated

import anyio

if sys.version_info >= (3, 11):
    from typing import NotRequired, TypedDict
else:
    from typing_extensions import NotRequired, TypedDict

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    create_sdk_mcp_server,
    query,
    tool,
)


# 使用 TypedDict 定义工具输入的完整 schema
class WeatherInput(TypedDict):
    """天气查询参数"""
    city: Annotated[str, "The city name to query weather for"]
    unit: Annotated[NotRequired[str], "Temperature unit: celsius or fahrenheit"]


class ConvertInput(TypedDict):
    """温度转换参数"""
    value: Annotated[float, "The temperature value to convert"]
    from_unit: Annotated[str, "Source unit: celsius or fahrenheit"]
    to_unit: Annotated[str, "Target unit: celsius or fahrenheit"]


# 使用 TypedDict 作为 input_schema
@tool("get_weather", "Get current weather for a city (mock data)", WeatherInput)
async def get_weather(args: dict) -> dict:
    """模拟天气查询工具"""
    city = args["city"]
    unit = args.get("unit", "celsius")

    # 模拟数据
    mock_data = {
        "Tokyo": {"celsius": 28, "fahrenheit": 82},
        "London": {"celsius": 15, "fahrenheit": 59},
        "New York": {"celsius": 22, "fahrenheit": 72},
    }

    if city in mock_data:
        temp = mock_data[city][unit]
        return {
            "content": [{"type": "text", "text": f"Weather in {city}: {temp}° {unit}"}]
        }
    return {
        "content": [{"type": "text", "text": f"Weather in {city}: 20° {unit} (default)"}]
    }


@tool("convert_temperature", "Convert temperature between celsius and fahrenheit", ConvertInput)
async def convert_temperature(args: dict) -> dict:
    """温度转换工具"""
    value = args["value"]
    from_unit = args["from_unit"]
    to_unit = args["to_unit"]

    if from_unit == "celsius" and to_unit == "fahrenheit":
        result = value * 9 / 5 + 32
    elif from_unit == "fahrenheit" and to_unit == "celsius":
        result = (value - 32) * 5 / 9
    else:
        result = value

    return {
        "content": [{"type": "text", "text": f"{value}° {from_unit} = {result:.1f}° {to_unit}"}]
    }


async def main():
    server = create_sdk_mcp_server(
        name="weather",
        version="1.0.0",
        tools=[get_weather, convert_temperature],
    )

    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        mcp_servers={"weather": server},
        allowed_tools=["get_weather", "convert_temperature"],
        max_turns=3,
    )

    print("=== TypedDict Schema 工具演示 ===\n")

    async for message in query(
        prompt="What's the weather in Tokyo? Convert it to fahrenheit.",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"  Claude: {block.text}")
                elif isinstance(block, ToolUseBlock):
                    print(f"  [调用] {block.name}({block.input})")
            print()

        elif isinstance(message, ResultMessage):
            print(f"[完成] 轮次={message.num_turns}")


if __name__ == "__main__":
    anyio.run(main)
