# 快速上手

## 安装

```bash
# 使用 pip
pip install claude-agent-sdk

# 使用 uv（推荐）
uv add claude-agent-sdk
```

**系统要求**：Python >= 3.10

## 认证配置

SDK 通过环境变量认证，三种方式：

### 方式 1：Anthropic API Key（最常见）
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 方式 2：Token + 自定义 Base URL（内部代理）
```bash
export ANTHROPIC_AUTH_TOKEN="your-token"
export ANTHROPIC_BASE_URL="https://your-proxy.example.com/v1/anthropic/"
```

### 方式 3：云平台（Bedrock/Vertex/Foundry）
```bash
# Amazon Bedrock
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION=us-west-2

# Google Vertex AI
export CLAUDE_CODE_USE_VERTEX=1
export CLOUD_ML_REGION=us-east5
export ANTHROPIC_VERTEX_PROJECT_ID=your-project
```

## 第一个程序

```python
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage, TextBlock

async def main():
    async for message in query(prompt="用一句话解释什么是 Python"):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print(f"\n费用: ${message.total_cost_usd:.4f}")

anyio.run(main)
```

运行：
```bash
uv run python first_query.py
```

## 运行 Demo 项目

```bash
git clone <this-repo>
cd demos
uv sync
uv run python 01_basic_query.py
```

## 两个核心入口

### query() — 一次性任务

```python
async for msg in query(prompt="...", options=ClaudeAgentOptions(...)):
    # 处理消息
```

适用场景：单次查询、批处理、无需后续交互。

### ClaudeSDKClient — 交互式对话

```python
async with ClaudeSDKClient(options) as client:
    await client.query("第一个问题")
    async for msg in client.receive_response():
        # 处理消息

    await client.query("追问")
    async for msg in client.receive_response():
        # 处理消息
```

适用场景：多轮对话、需要中断、运行时控制权限/模型。

## 消息处理模式

SDK 返回的消息流包含多种类型：

```python
from claude_agent_sdk import (
    AssistantMessage, ResultMessage, UserMessage,
    SystemMessage, StreamEvent, TextBlock, ToolUseBlock
)

async for message in query(prompt="..."):
    match message:
        case AssistantMessage():
            # Claude 的回复（可包含文本、工具调用、思考等）
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        case ResultMessage():
            # 最终结果（包含成本、耗时、状态）
            print(f"状态: {message.subtype}")
            print(f"费用: ${message.total_cost_usd}")
        case SystemMessage():
            # 系统事件（初始化、任务状态等）
            pass
```

## 环境变量总览

| 变量 | 用途 |
|------|------|
| `ANTHROPIC_API_KEY` | API 密钥 |
| `ANTHROPIC_AUTH_TOKEN` | Token 认证（替代 API Key） |
| `ANTHROPIC_BASE_URL` | 自定义 API 端点 |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | Opus 模型 ID 覆盖 |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Sonnet 模型 ID 覆盖 |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Haiku 模型 ID 覆盖 |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | 禁止非必要网络请求 |
| `CLAUDE_CODE_USE_BEDROCK` | 启用 Bedrock |
| `CLAUDE_CODE_USE_VERTEX` | 启用 Vertex |
