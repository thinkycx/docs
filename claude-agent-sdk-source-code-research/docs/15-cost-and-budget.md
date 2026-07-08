# 成本与预算

## 概述

Claude Agent SDK 提供完整的成本控制和使用量追踪能力。通过 `max_budget_usd` 设置预算上限，通过 `ResultMessage` 的成本字段获取详细使用统计，实现生产环境的成本可观测性。

## 预算限制

### max_budget_usd

在 `ClaudeAgentOptions` 中设置最大花费上限（单位：美元）：

```python
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(
    max_budget_usd=0.50,  # 限制单次查询最多花费 $0.50
    model="claude-sonnet-4-20250514",
)

async for msg in query(prompt="分析这段代码", options=options):
    pass
```

当花费超过预算时，SDK 会终止执行并返回一个 `ResultMessage`，其 `subtype` 为 `"error_max_budget_usd"`。

### task_budget（API 侧令牌预算）

`TaskBudget` 用于在 API 层面设置令牌限制：

```python
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(
    task_budget={
        "max_input_tokens": 100000,
        "max_output_tokens": 50000,
    },
)

async for msg in query(prompt="总结文档", options=options):
    pass
```

`task_budget` 与 `max_budget_usd` 的区别：
- `max_budget_usd` — 客户端估算的美元预算，基于令牌用量和模型定价计算
- `task_budget` — API 侧的令牌硬限制，由服务端执行

两者可以同时使用，取先触发的为准。

## ResultMessage 成本字段

每次查询结束时，`ResultMessage` 包含完整的成本和性能数据：

```python
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

async for msg in query(prompt="Hello", options=ClaudeAgentOptions()):
    if isinstance(msg, ResultMessage):
        # 成本估算
        print(f"预估花费: ${msg.total_cost_usd}")

        # 时间统计
        print(f"总耗时: {msg.duration_ms}ms")
        print(f"API 调用耗时: {msg.duration_api_ms}ms")
        print(f"非 API 耗时: {msg.duration_ms - msg.duration_api_ms}ms")

        # 令牌用量
        print(f"总令牌用量: {msg.usage}")
        print(f"对话轮次: {msg.num_turns}")

        # 按模型分组的用量
        print(f"各模型用量: {msg.model_usage}")
```

### 字段详解

| 字段 | 类型 | 说明 |
|------|------|------|
| `total_cost_usd` | `float \| None` | 客户端估算的总花费（美元），非计费权威值 |
| `duration_ms` | `int \| None` | 从查询开始到结束的总时间（毫秒） |
| `duration_api_ms` | `int \| None` | 仅 API 调用消耗的时间（不含工具执行等） |
| `usage` | `dict \| None` | 总令牌用量，含 input/output tokens |
| `num_turns` | `int \| None` | 模型-用户交互的总轮次数 |
| `model_usage` | `dict \| None` | 按模型名称分组的详细用量 |

### usage 字段结构

```python
# msg.usage 典型结构
{
    "input_tokens": 1523,
    "output_tokens": 847,
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 1200,
}
```

### model_usage 字段结构

当使用多个模型（如主模型 + 子代理模型）时，`model_usage` 提供按模型的细分：

```python
# msg.model_usage 典型结构
{
    "claude-sonnet-4-20250514": {
        "input_tokens": 1523,
        "output_tokens": 847,
        "cost_usd": 0.012,
    },
    "claude-haiku-4-20250514": {
        "input_tokens": 500,
        "output_tokens": 200,
        "cost_usd": 0.001,
    },
}
```

## AssistantMessage 的逐步用量

每个 `AssistantMessage` 包含该步骤的令牌用量：

```python
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage

async for msg in query(prompt="写一个函数", options=ClaudeAgentOptions()):
    if isinstance(msg, AssistantMessage):
        if msg.usage:
            print(f"本步骤输入令牌: {msg.usage.get('input_tokens')}")
            print(f"本步骤输出令牌: {msg.usage.get('output_tokens')}")
```

这对于监控多步骤任务中每步的消耗很有用。

## 预算超出处理

```python
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

options = ClaudeAgentOptions(
    max_budget_usd=0.01,  # 极低预算，容易触发
    model="claude-sonnet-4-20250514",
)

result = None
async for msg in query(prompt="写一篇3000字的文章", options=options):
    if isinstance(msg, ResultMessage):
        result = msg

if result and result.subtype == "error_max_budget_usd":
    print("预算已用尽！")
    print(f"已花费: ${result.total_cost_usd}")
    print(f"预算上限: $0.01")
    # 可以选择以更高预算重试
```

## 生产环境成本追踪模式

### 模式 1：单次查询成本记录

```python
import json
import logging
from datetime import datetime
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

logger = logging.getLogger("cost_tracker")

async def tracked_query(prompt: str, user_id: str):
    options = ClaudeAgentOptions(
        max_budget_usd=1.00,
        model="claude-sonnet-4-20250514",
    )

    result = None
    async for msg in query(prompt=prompt, options=options):
        if isinstance(msg, ResultMessage):
            result = msg

    if result:
        cost_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "cost_usd": result.total_cost_usd,
            "duration_ms": result.duration_ms,
            "duration_api_ms": result.duration_api_ms,
            "num_turns": result.num_turns,
            "usage": result.usage,
            "model_usage": result.model_usage,
            "is_error": result.is_error,
            "subtype": result.subtype,
        }
        logger.info(f"Query cost: {json.dumps(cost_record)}")

    return result
```

### 模式 2：累积成本预警

```python
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

class CostAccumulator:
    def __init__(self, daily_budget: float = 100.0):
        self.daily_budget = daily_budget
        self.daily_cost = 0.0
        self.query_count = 0

    async def execute(self, prompt: str) -> ResultMessage | None:
        remaining = self.daily_budget - self.daily_cost
        if remaining <= 0:
            raise RuntimeError("日预算已用尽")

        options = ClaudeAgentOptions(
            # 单次预算不超过剩余额度
            max_budget_usd=min(1.0, remaining),
        )

        result = None
        async for msg in query(prompt=prompt, options=options):
            if isinstance(msg, ResultMessage):
                result = msg

        if result and result.total_cost_usd:
            self.daily_cost += result.total_cost_usd
            self.query_count += 1

            # 超过 80% 预算时预警
            if self.daily_cost > self.daily_budget * 0.8:
                print(f"警告: 已使用 {self.daily_cost/self.daily_budget*100:.1f}% 日预算")

        return result
```

### 模式 3：逐步令牌监控

```python
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

async def monitored_query(prompt: str):
    options = ClaudeAgentOptions(max_budget_usd=2.00)

    step_costs = []
    async for msg in query(prompt=prompt, options=options):
        if isinstance(msg, AssistantMessage) and msg.usage:
            step_costs.append({
                "input_tokens": msg.usage.get("input_tokens", 0),
                "output_tokens": msg.usage.get("output_tokens", 0),
            })
            total_input = sum(s["input_tokens"] for s in step_costs)
            total_output = sum(s["output_tokens"] for s in step_costs)
            print(f"步骤 {len(step_costs)}: 累计 input={total_input}, output={total_output}")

        if isinstance(msg, ResultMessage):
            print(f"\n最终成本: ${msg.total_cost_usd}")
            print(f"总步骤数: {len(step_costs)}")
```

## 重要注意事项

1. **`total_cost_usd` 是客户端估算值**，不是计费权威数据。实际账单以 Anthropic 控制台为准。估算可能因缓存命中、定价变更等因素与实际值有微小差异。

2. **`duration_api_ms` vs `duration_ms`**：两者的差值反映了工具执行、Hook 处理等非 API 时间。如果差值过大，说明工具执行是瓶颈。

3. **`num_turns` 与 `max_turns` 的关系**：`num_turns` 是实际发生的轮次，`max_turns` 是上限。如果 `num_turns == max_turns`，说明任务可能未完成。

4. **多模型场景**：使用子代理时，`model_usage` 会包含所有模型的分别统计，而 `total_cost_usd` 是总和。

5. **字段可能为 None**：所有成本字段都是可选的。在异常终止或极早期错误时，某些字段可能缺失。
