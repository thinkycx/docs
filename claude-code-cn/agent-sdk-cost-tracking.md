---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Agent SDK - 成本追踪
description: Claude Agent SDK 成本追踪指南，涵盖 token 用量统计、费用估算、按模型拆分、跨调用累计、缓存 token 追踪及 1 小时缓存 TTL 配置。
category: translation
tags: [claude-code, agent-sdk, translation]
refs:
  - https://code.claude.com/docs/en/agent-sdk/cost-tracking
  - en-source/agent-sdk/cost-tracking.md
---

# 成本与用量追踪

> 了解如何通过 Claude Agent SDK 追踪 token 用量、估算费用，以及配置 prompt 缓存。

**SDK 在每次与 Claude 交互后提供详细的 token 用量信息。** 本指南说明如何正确追踪用量并理解费用报告，特别是在并行工具调用和多步对话场景下。

完整 API 文档参见 [TypeScript SDK 参考](https://code.claude.com/docs/en/agent-sdk/typescript) 和 [Python SDK 参考](https://code.claude.com/docs/en/agent-sdk/python)。

> **注意：`total_cost_usd` 和 `costUSD` 字段是客户端估算值，不是权威账单数据。** SDK 基于打包时内置的价格表在本地计算，以下场景可能导致估算值与实际账单偏差：
>
> * 定价变更
> * 已安装的 SDK 版本无法识别某个模型
> * 存在客户端无法建模的计费规则
>
> 这些字段适用于开发洞察和粗略预算。权威账单请使用 [Usage and Cost API](https://platform.claude.com/docs/en/build-with-claude/usage-cost-api) 或 [Claude Console](https://platform.claude.com/usage) 的 Usage 页面。不要基于这些字段向终端用户收费或触发财务决策。

## 理解 token 用量

**TypeScript 和 Python SDK 暴露相同的用量数据，但字段名不同。**

* **TypeScript** 在每条 assistant 消息上提供每步 token 明细（`message.message.id`、`message.message.usage`），在 result 消息上提供 `modelUsage` 按模型拆分费用，以及累计总量。
* **Python** 在每条 assistant 消息上提供每步 token 明细（`message.usage`、`message.message_id`），在 result 消息上提供 `model_usage` 按模型拆分费用，以及累计总量（`total_cost_usd` 和 `usage` 字典）。

两个 SDK 使用相同的底层成本模型和数据粒度，区别仅在字段命名和嵌套位置。

**成本追踪依赖于理解 SDK 对用量数据的作用域划分：**

| 概念 | 说明 |
|:---|:---|
| **`query()` 调用** | SDK `query()` 函数的一次调用。单次调用可能包含多步（Claude 回复 → 使用工具 → 获取结果 → 再次回复）。每次调用结束时产出一条 `result` 消息。 |
| **步骤（Step）** | `query()` 调用中的一次请求/响应周期。每步产出带有 token 用量的 assistant 消息。 |
| **会话（Session）** | 通过 session ID（使用 `resume` 选项）关联的一系列 `query()` 调用。会话中每次 `query()` 调用独立报告自身费用。 |

下图展示单次 `query()` 调用的消息流，每步报告 token 用量，最后给出累计估算：

![消息用量流程图](https://mintcdn.com/claude-code/ikqp3_70mqIahteV/images/agent-sdk/message-usage-flow.svg?fit=max&auto=format&n=ikqp3_70mqIahteV&q=85&s=68497aee338e01cc745323af7aea378e)

### 步骤一：每步产出 assistant 消息

**Claude 回复时发送一条或多条 assistant 消息。** 在 TypeScript 中，每条 assistant 消息包含嵌套的 `BetaMessage`（通过 `message.message` 访问），其中有 `id` 和带 token 计数的 `usage` 对象（`input_tokens`、`output_tokens`）。在 Python 中，`AssistantMessage` 数据类直接通过 `message.usage` 和 `message.message_id` 暴露相同数据。当 Claude 在一个回合中使用多个工具时，该回合所有消息共享同一 ID——需按 ID 去重以避免重复计算。

### 步骤二：result 消息提供累计估算

**`query()` 调用完成时，SDK 发出一条 result 消息。** 它包含 `total_cost_usd` 和累计 `usage`。TypeScript 对应 [`SDKResultMessage`](https://code.claude.com/docs/en/agent-sdk/typescript#sdkresultmessage)，Python 对应 [`ResultMessage`](https://code.claude.com/docs/en/agent-sdk/python#resultmessage)。如果进行多次 `query()` 调用（例如多轮会话），每条 result 只反映该次调用的费用。如果只需要估算总量，可以忽略每步用量，直接读取这个值。

## 获取单次查询的总费用

**result 消息标志着一次 `query()` 调用的 agent 循环结束。** 它包含 `total_cost_usd`——该次调用所有步骤的累计估算费用。成功和错误结果都包含此字段。如果使用会话进行多次 `query()` 调用，每条 result 只反映该次调用的费用。

以下示例遍历 `query()` 调用的消息流，在 `result` 消息到达时打印总费用：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

try {
  for await (const message of query({ prompt: "Summarize this project" })) {
    if (message.type === "result") {
      console.log(`Total cost: $${message.total_cost_usd}`);
    }
  }
} catch (error) {
  // 单次 query() 在产出错误 result 后会抛出异常。如果失败来自错误 result，
  // 它仍携带 total_cost_usd，上面的分支已经运行过；连接或进程故障不产出 result 消息。
  console.error(`Session ended with an error: ${error}`);
}
```

```python
from claude_agent_sdk import query, ResultMessage
import asyncio


async def main():
    try:
        async for message in query(prompt="Summarize this project"):
            if isinstance(message, ResultMessage):
                print(f"Total cost: ${message.total_cost_usd or 0}")
    except Exception as error:
        # 单次 query() 在产出错误 result 后会抛出异常。如果失败来自错误 result，
        # 它仍携带 total_cost_usd，上面的分支已经运行过；连接或进程故障不产出 result 消息。
        print(f"Session ended with an error: {error}")


asyncio.run(main())
```

## 按步骤和按模型追踪用量

本节示例使用 TypeScript 字段名。Python 中等价字段为 [`AssistantMessage.usage`](https://code.claude.com/docs/en/agent-sdk/python#assistantmessage) 和 `AssistantMessage.message_id`（按步骤用量），以及 [`ResultMessage.model_usage`](https://code.claude.com/docs/en/agent-sdk/python#resultmessage)（按模型拆分）。

### 按步骤追踪用量

**每条 assistant 消息包含嵌套的 `BetaMessage`，其中有 `id` 和 `usage` 对象。** 当 Claude 并行使用工具时，多条消息共享同一 `id` 和相同用量数据。记录已计数的 ID，跳过重复项以避免虚高总量。

> **注意：并行工具调用会产生多条 assistant 消息，其嵌套 `BetaMessage` 共享同一 `id` 和相同用量。必须按 ID 去重以获取准确的每步 token 计数。**

以下示例累计所有步骤的 input 和 output token，每个唯一消息 ID 只计数一次：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

const seenIds = new Set<string>();
let totalInputTokens = 0;
let totalOutputTokens = 0;

try {
  for await (const message of query({ prompt: "Summarize this project" })) {
    if (message.type === "assistant") {
      const msgId = message.message.id;

      // 并行工具调用共享同一 ID，只计数一次
      if (!seenIds.has(msgId)) {
        seenIds.add(msgId);
        totalInputTokens += message.message.usage.input_tokens;
        totalOutputTokens += message.message.usage.output_tokens;
      }
    }
  }
} catch (error) {
  // 单次 query() 在产出错误 result 后会抛出异常，
  // 下方的合计仍反映失败前已运行步骤的数据。
  console.error(`Session ended with an error: ${error}`);
}

console.log(`Steps: ${seenIds.size}`);
console.log(`Input tokens: ${totalInputTokens}`);
console.log(`Output tokens: ${totalOutputTokens}`);
```

### 按模型拆分用量

**result 消息包含 `modelUsage`，一个从模型名称到每模型 token 计数和费用的映射。** 当运行多个模型（例如 Haiku 用于子代理、Opus 用于主代理）时，这可以帮助了解 token 的去向。

以下示例运行一次查询并打印每个模型的费用和 token 拆分：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

try {
  for await (const message of query({ prompt: "Summarize this project" })) {
    if (message.type !== "result") continue;

    for (const [modelName, usage] of Object.entries(message.modelUsage)) {
      console.log(`${modelName}: $${usage.costUSD.toFixed(4)}`);
      console.log(`  Input tokens: ${usage.inputTokens}`);
      console.log(`  Output tokens: ${usage.outputTokens}`);
      console.log(`  Cache read: ${usage.cacheReadInputTokens}`);
      console.log(`  Cache creation: ${usage.cacheCreationInputTokens}`);
    }
  }
} catch (error) {
  // 单次 query() 在产出错误 result 后会抛出异常。如果失败来自错误 result，
  // 上面的按模型拆分已经打印过；连接或进程故障不产出 result 消息。
  console.error(`Session ended with an error: ${error}`);
}
```

## 跨多次调用累计费用

**每次 `query()` 调用返回自身的 `total_cost_usd`。** SDK 不提供会话级别的总量，因此如果应用进行多次 `query()` 调用（例如多轮会话或跨不同用户），需要自行累加。

以下示例依次运行两次 `query()` 调用，将每次调用的 `total_cost_usd` 加到运行总量中，并打印单次和合计费用：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

// 跨多次 query() 调用追踪累计费用
let totalSpend = 0;

const prompts = [
  "Read the files in src/ and summarize the architecture",
  "List all exported functions in src/auth.ts"
];

for (const prompt of prompts) {
  try {
    for await (const message of query({ prompt })) {
      if (message.type === "result") {
        totalSpend += message.total_cost_usd;
        console.log(`This call: $${message.total_cost_usd}`);
      }
    }
  } catch (error) {
    // 单次 query() 在产出错误 result 后会抛出异常。如果失败来自错误 result，
    // 该次调用的费用已被计入；连接或进程故障不产出 result 消息。继续处理下一个 prompt。
    console.error(`Call failed: ${error}`);
  }
}

console.log(`Total spend: $${totalSpend.toFixed(4)}`);
```

```python
from claude_agent_sdk import query, ResultMessage
import asyncio


async def main():
    # 跨多次 query() 调用追踪累计费用
    total_spend = 0.0

    prompts = [
        "Read the files in src/ and summarize the architecture",
        "List all exported functions in src/auth.ts",
    ]

    for prompt in prompts:
        try:
            async for message in query(prompt=prompt):
                if isinstance(message, ResultMessage):
                    cost = message.total_cost_usd or 0
                    total_spend += cost
                    print(f"This call: ${cost}")
        except Exception as error:
            # 单次 query() 在产出错误 result 后会抛出异常。如果失败来自错误 result，
            # 该次调用的费用已被计入；连接或进程故障不产出 result 消息。继续处理下一个 prompt。
            print(f"Call failed: {error}")

    print(f"Total spend: ${total_spend:.4f}")


asyncio.run(main())
```

## 处理错误、缓存与 token 差异

**为了准确追踪费用，需要考虑失败的对话、缓存 token 定价和偶发的报告不一致。**

### 解决 output token 差异

在少数情况下，可能观察到同一 ID 的消息有不同的 `output_tokens` 值。此时：

1. **使用最大值：** 一组消息中最后一条通常包含准确的总量。
2. **以 result 消息为准：** result 消息中的 `total_cost_usd` 反映 SDK 跨所有步骤的累计估算，比自行汇总每步数值更可靠。它仍然是估算值，可能与实际账单不同。
3. **报告不一致：** 在 [Claude Code GitHub 仓库](https://github.com/anthropics/claude-code/issues) 提交 issue。

### 追踪失败对话的费用

**成功和错误 result 消息都包含 `usage` 和 `total_cost_usd`。** 如果对话中途失败，在失败点之前已经消耗了 token。无论 result 的 `subtype` 是什么，都应该读取费用数据。

### 追踪缓存 token

**Agent SDK 自动使用 [prompt 缓存](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) 来降低重复内容的费用。** 无需自行配置缓存。usage 对象包含两个额外的缓存追踪字段：

| 字段 | 说明 |
|:---|:---|
| `cache_creation_input_tokens` | 用于创建新缓存条目的 token（费率高于标准 input token） |
| `cache_read_input_tokens` | 从已有缓存条目读取的 token（费率低于标准 input token） |

将这些字段与 `input_tokens` 分开追踪以了解缓存节省情况。TypeScript 中这些字段定义在 [`Usage`](https://code.claude.com/docs/en/agent-sdk/typescript#usage) 对象上。Python 中它们作为 [`ResultMessage.usage`](https://code.claude.com/docs/en/agent-sdk/python#resultmessage) 字典的键出现（例如 `message.usage.get("cache_read_input_tokens", 0)`）。

### 将 prompt 缓存 TTL 延长至一小时

**当使用 API key 认证或运行在 Amazon Bedrock、Google Cloud Agent Platform 或 Microsoft Foundry 上时，SDK 写入的缓存条目默认使用 5 分钟 TTL。** 如果工作负载在同一系统提示词和上下文上运行多个短会话，且会话间隔超过 5 分钟，缓存会在会话之间过期，每个新会话都要付全价 input 费用。

要请求 1 小时 TTL 的缓存写入，设置 [`ENABLE_PROMPT_CACHING_1H`](https://code.claude.com/docs/en/env-vars) 环境变量。可以在 shell 或容器环境中导出，也可以通过 `options.env` 传入。

以下示例为运行在 Amazon Bedrock 上的 agent 启用 1 小时 TTL：

```python
from claude_agent_sdk import ClaudeAgentOptions, query
import asyncio


async def main():
    options = ClaudeAgentOptions(
        env={
            "CLAUDE_CODE_USE_BEDROCK": "1",
            "ENABLE_PROMPT_CACHING_1H": "1",
        },
    )

    async for message in query(prompt="Summarize this project", options=options):
        print(message)


asyncio.run(main())
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

const options = {
  env: {
    ...process.env,
    CLAUDE_CODE_USE_BEDROCK: "1",
    ENABLE_PROMPT_CACHING_1H: "1",
  },
};

for await (const message of query({ prompt: "Summarize this project", options })) {
  console.log(message);
}
```

**1 小时 TTL 的缓存写入费率高于 5 分钟写入。** 启用此选项是用更高的写入费用换取更多的缓存读取。详细定价参见 [prompt caching pricing](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)。Claude 订阅用户已自动获得 1 小时 TTL，无需设置此变量。

## 相关文档

* [TypeScript SDK 参考](https://code.claude.com/docs/en/agent-sdk/typescript) - 完整 API 文档
* [SDK 概述](https://code.claude.com/docs/en/agent-sdk/overview) - SDK 入门
* [SDK 权限](https://code.claude.com/docs/en/agent-sdk/permissions) - 管理工具权限
