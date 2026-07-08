# 思考模式与努力级别

## 概述

Claude Agent SDK 提供两个维度来控制模型的推理深度：**ThinkingConfig**（思考模式）和 **EffortLevel**（努力级别）。两者相互配合，让你在响应速度和推理质量之间灵活权衡。

## ThinkingConfig（思考配置）

思考模式控制模型是否使用"扩展思考"（extended thinking）——即在生成最终回答前，先进行内部推理链。

### adaptive（自适应）

模型自行决定何时需要思考、思考多深：

```python
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(
    thinking={"type": "adaptive"},
    model="claude-sonnet-4-20250514",
)

async for msg in query(prompt="设计一个分布式锁方案", options=options):
    pass
```

**特点：**
- Opus 4.6+ 和 Sonnet 4 的默认模式
- 简单问题跳过思考，复杂问题自动激活
- 无需手动调整参数
- 推荐大多数场景使用

### enabled（启用，固定预算）

显式启用思考，并指定令牌预算：

```python
options = ClaudeAgentOptions(
    thinking={"type": "enabled", "budget_tokens": 10000},
    model="claude-sonnet-4-20250514",
)

async for msg in query(prompt="证明这个算法的正确性", options=options):
    pass
```

**特点：**
- 每步最多使用 `budget_tokens` 个令牌进行思考
- 适合需要保证深度推理的场景
- 旧版模型（不支持 adaptive 的）使用此模式
- 预算过小可能限制推理质量，过大浪费令牌

### disabled（禁用）

完全关闭扩展思考：

```python
options = ClaudeAgentOptions(
    thinking={"type": "disabled"},
)

async for msg in query(prompt="今天天气如何", options=options):
    pass
```

**特点：**
- 最快的响应速度
- 适合简单问答、格式转换等不需要深度推理的任务
- 节省令牌开销

## ThinkingBlock 输出

当思考启用时，`AssistantMessage.content` 中会包含 `ThinkingBlock`：

```python
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage

options = ClaudeAgentOptions(
    thinking={"type": "enabled", "budget_tokens": 5000},
)

async for msg in query(prompt="分析竞态条件", options=options):
    if isinstance(msg, AssistantMessage):
        for block in msg.content:
            if block.get("type") == "thinking":
                print(f"思考内容: {block.get('thinking', '')[:200]}...")
                print(f"签名: {block.get('signature', '')[:50]}...")
            elif block.get("type") == "text":
                print(f"回答: {block['text']}")
```

### ThinkingBlock 结构

```python
{
    "type": "thinking",
    "thinking": "让我分析这个竞态条件...",  # 思考文本
    "signature": "EiE8dG...",  # 签名（用于验证思考来源）
}
```

**注意：** 思考内容在流式输出中也会逐步产生。在多步任务中，每步都可能有独立的思考过程。

## EffortLevel（努力级别）

努力级别是更高层次的控制，影响模型在整体任务上投入多少"努力"：

```python
from claude_agent_sdk import query, ClaudeAgentOptions

# 低努力 — 快速简洁
options = ClaudeAgentOptions(effort="low")

# 中等努力
options = ClaudeAgentOptions(effort="medium")

# 高努力（默认）
options = ClaudeAgentOptions(effort="high")

# 超高努力（仅 Opus 4.7）
options = ClaudeAgentOptions(effort="xhigh")

# 最大努力
options = ClaudeAgentOptions(effort="max")
```

### 各级别特征

| 级别 | 推理深度 | 响应速度 | 适用场景 |
|------|----------|----------|----------|
| `"low"` | 最浅 | 最快 | 简单事实查询、格式转换 |
| `"medium"` | 适中 | 较快 | 常规编码、文档撰写 |
| `"high"` | 深入 | 标准 | 复杂编码、架构设计（默认） |
| `"xhigh"` | 很深 | 较慢 | 困难算法、深度分析（仅 Opus 4.7） |
| `"max"` | 最深 | 最慢 | 数学证明、极端复杂推理 |

### 努力级别示例

```python
# 快速代码格式化 — 不需要深度思考
options = ClaudeAgentOptions(
    effort="low",
    system_prompt="格式化以下代码，不做逻辑修改",
)

# 架构设计 — 需要深度推理
options = ClaudeAgentOptions(
    effort="high",
    thinking={"type": "adaptive"},
    system_prompt="设计微服务架构方案",
)

# 安全审计 — 最大努力不遗漏
options = ClaudeAgentOptions(
    effort="max",
    thinking={"type": "enabled", "budget_tokens": 20000},
    system_prompt="进行全面安全审计",
)
```

## ThinkingConfig 与 EffortLevel 的关系

两者互相独立但协同工作：

| 组合 | 行为 |
|------|------|
| `effort="low"` + `thinking=disabled` | 最快、最省令牌 |
| `effort="high"` + `thinking=adaptive` | 标准推荐配置 |
| `effort="max"` + `thinking=enabled(20000)` | 最深推理，适合困难任务 |
| `effort="low"` + `thinking=enabled(5000)` | 有思考但整体控制投入 |

- `effort` 影响模型整体行为倾向（多详细、多仔细）
- `thinking` 控制是否有显式的内部推理步骤

## 已废弃：max_thinking_tokens

```python
# 已废弃，请使用 thinking 参数代替
options = ClaudeAgentOptions(
    max_thinking_tokens=10000,  # ❌ deprecated
)

# 等价的新写法
options = ClaudeAgentOptions(
    thinking={"type": "enabled", "budget_tokens": 10000},  # ✅
)
```

## 生产场景选择指南

### 场景 1：高吞吐 API 服务

```python
# 优先速度和成本
options = ClaudeAgentOptions(
    effort="low",
    thinking={"type": "disabled"},
    model="claude-haiku-4-20250514",
    max_turns=3,
)
```

### 场景 2：代码生成代理

```python
# 平衡质量和速度
options = ClaudeAgentOptions(
    effort="high",
    thinking={"type": "adaptive"},
    model="claude-sonnet-4-20250514",
)
```

### 场景 3：复杂分析任务

```python
# 优先质量
options = ClaudeAgentOptions(
    effort="max",
    thinking={"type": "enabled", "budget_tokens": 15000},
    model="claude-opus-4-20250514",
)
```

### 场景 4：动态调整

根据任务复杂度动态选择配置：

```python
def get_options(task_complexity: str) -> ClaudeAgentOptions:
    configs = {
        "simple": ClaudeAgentOptions(
            effort="low",
            thinking={"type": "disabled"},
        ),
        "moderate": ClaudeAgentOptions(
            effort="medium",
            thinking={"type": "adaptive"},
        ),
        "complex": ClaudeAgentOptions(
            effort="high",
            thinking={"type": "enabled", "budget_tokens": 10000},
        ),
        "extreme": ClaudeAgentOptions(
            effort="max",
            thinking={"type": "enabled", "budget_tokens": 20000},
        ),
    }
    return configs.get(task_complexity, configs["moderate"])
```

## 注意事项

1. **`adaptive` 是推荐默认** — 除非有特殊需求，使用 adaptive 让模型自行决定最合适。

2. **思考令牌计入成本** — thinking tokens 按 output tokens 计费。budget_tokens 大不等于一定消耗那么多，但设得越高上限越高。

3. **`xhigh` 仅限 Opus 4.7** — 在其他模型上使用可能被忽略或降级。

4. **思考内容可能为空** — 即使启用思考，简单问题模型可能选择不思考（adaptive 模式下）。

5. **流式输出中的思考** — 思考内容在流式模式下逐步产生，可能在最终文本之前出现。对于 UI 场景，可选择隐藏思考内容只展示最终回答。
