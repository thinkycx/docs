---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Advisor 决策升级
description: Claude Code 的 Advisor 工具让主模型在关键决策点咨询更强的模型获取指导。本文介绍如何启用 advisor、模型配对规则、计费方式和与其他功能的对比。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/advisor.md
  - en-source/advisor.md
---

# Advisor 决策升级

> 为主模型配对一个更强的 advisor 模型，让 Claude 在任务关键节点主动请求指导。

**Advisor 是实验性功能，需要 Claude Code v2.1.98 或更高版本，仅支持 Anthropic API。** 不支持 Amazon Bedrock、Google Cloud Agent Platform 或 Microsoft Foundry。行为、定价和可用性可能变化。

**Advisor 工具让 Claude 在任务关键时刻咨询第二个更强的模型。** 例如在确定方案前、遇到重复错误时、或在声明任务完成前。Advisor 会接收完整对话（包括所有工具调用和结果），返回指导意见供 Claude 继续执行。

Advisor 以 [server tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool) 的形式在 Anthropic 基础设施上运行，订阅用户和 API 计费账户均可使用。你选择哪个模型做 advisor，Claude 自行决定何时调用。

本页介绍如何启用 advisor、可用的模型配对、会话中的展示方式以及计费规则。

## 何时使用 advisor

**Advisor 适合大部分步骤是常规操作、但方案质量决定成败的长任务。** 例如大规模重构、持续报错的调试、以及需要独立核查才能结项的任务。

短任务或每一步都需要最强模型的工作不太适合。对于后者，可以直接[切换主模型](https://code.claude.com/docs/en/model-config#setting-your-model)，或查看 [advisor 与 opusplan 和 subagent 的对比](#与相关功能对比)。

## 启用 advisor

三种方式设置 advisor 模型：

| 方式 | 说明 |
| --- | --- |
| `/advisor` 命令 | 在会话中设置或更改 advisor，并保存为默认值 |
| `advisorModel` 设置 | 在[设置文件](https://code.claude.com/docs/en/settings)中配置持久默认值 |
| `--advisor` 启动标志 | 仅对单次会话生效 |

只要其中任何一种设置了 advisor 模型，主模型[支持](#选择-advisor-模型)时即启用。要关闭请参考[关闭 advisor](#关闭-advisor)。

> 使用 Fable 5 作为 advisor 需要 Claude Code v2.1.170 或更高版本，以及组织的 [Fable 5 访问权限](https://code.claude.com/docs/en/model-config#work-with-fable-5)。

### 使用 `/advisor` 命令

不带参数运行 `/advisor` 打开可选 advisor 列表，或直接指定模型：

```
/advisor opus
```

**选择会保存到用户设置的 `advisorModel` 中，跨会话持久生效。** 如果组织的 [`availableModels`](https://code.claude.com/docs/en/model-config#restrict-model-selection) 白名单排除了已保存的 advisor 模型，advisor 不会被调用，直到你用 `/advisor` 选择一个被允许的模型。如果当前主模型不支持 advisor，选择仍会保存，在切换到[兼容主模型](#选择-advisor-模型)时自动激活。

### 在设置中配置 `advisorModel`

无需打开会话即可配置 advisor 默认值：

```json
{
  "advisorModel": "opus"
}
```

### 使用 `--advisor` 启动标志

单次会话中设置 advisor 而不改变保存的设置：

```bash
claude --advisor opus
```

**该标志优先于 `advisorModel` 设置。** 如果会话主模型不支持 advisor，或请求的 advisor 模型被组织白名单排除，命令会报错退出。

## 选择 advisor 模型

**Advisor 必须至少与主模型同等能力。** 各主模型可接受的 advisor 如下：

| 主模型 | 可用 Advisor | 备注 |
| --- | --- | --- |
| Haiku 4.5 | Fable、Opus、Sonnet | Haiku 可调用 advisor 但不能作为 advisor |
| Sonnet 4.6 | Fable、Opus、Sonnet | |
| Sonnet 5 | Fable、Opus、Sonnet 5 | Sonnet 4.6 作为 advisor 会被拒绝 |
| Opus 4.6 | Fable、Opus、Sonnet 5 | Sonnet 5 和 Opus 4.6 能力等级相同，因此 Opus 4.6 主模型接受 Sonnet 5 advisor |
| Opus 4.7 或更高 | Fable、Opus 4.7、Opus 4.8 | Opus 4.7 和 4.8 能力等级相同，互为 advisor。Opus 4.7 主模型配 Opus 4.6 或 Sonnet 5 advisor 会被拒绝 |
| Fable 5（v2.1.170+） | Fable | Opus 或 Sonnet 作为 advisor 会被拒绝 |

Fable 5 需要 Claude Code v2.1.170 或更高版本以及 Fable 5 访问权限，无论作为主模型还是 advisor。

设置 advisor 时使用 `opus`、`sonnet` 或 `fable` 别名（解析为各模型最新版本），也可使用完整模型 ID 如 `claude-opus-4-8`。

**Subagent 继承已配置的 advisor，并对自身模型执行相同的配对检查。**

Claude Code 在发送请求前验证配对：

- 如果 advisor 能力弱于主模型，advisor 不会附加到主模型请求上（`/advisor` 命令输出和通知会显示此情况）。子模型满足配对条件的 subagent 仍可使用 advisor。
- 如果主模型或 advisor 是 Claude Code 无法识别的模型，advisor 不会附加。

### 常见模型配对

任何可接受的配对都能工作。下表按成本与能力的不同平衡方式列出常见组合：

| 配对 | 适用场景 |
| --- | --- |
| Sonnet 主 + Opus advisor | Sonnet 处理常规工作，将方案决策、歧义故障和完成检查升级给 Opus |
| Sonnet 主 + Fable advisor | 在决策点获得 Fable 5 指导，无需全程运行 Fable 5。需要 v2.1.170+ 和 Fable 5 权限 |
| Haiku 主 + Opus advisor | 最低成本主模型搭配强规划。比纯 Haiku 贵但比切换到 Sonnet 或 Opus 便宜 |
| Opus 主 + Opus advisor | 第二个 Opus 审查第一个。适合高风险任务，独立核查比成本更重要 |
| Fable 主 + Fable advisor | Fable 5 可用时的最强组合（v2.1.170+）。Fable 等级高于 Opus 和 Sonnet，是 Fable 主模型唯一可接受的 advisor |
| Sonnet 主 + Sonnet advisor | 低成本二次审查，捕捉常规疏漏 |

## Claude 何时咨询 advisor

**Claude 自行决定何时调用 advisor。** 倾向于在确定方案前、错误反复出现时、以及声明任务完成前咨询，但时机由模型驱动而非规则控制。

你可以在提示中要求咨询，例如 `consult the advisor before you continue`。没有设置可以限制或强制 advisor 调用次数；如果想让 Claude 更多或更少地咨询，直接在指示中说明。

## 会话中的展示

**当 Claude 调用 advisor 时，记录中显示 `Advising` 行和 advisor 模型名。** 结果返回后确认 advisor 已审查对话。按 `Ctrl+O` 展开查看 advisor 的完整指导。

Claude 通常遵循 advisor 指导，但当自身证据与具体建议矛盾时会灵活调整：如果推荐步骤实际执行失败，或文件内容与建议矛盾，Claude 会指出冲突而非无条件遵循。

Advisor 总是接收完整对话，由 Claude 控制调用时机。如需更多控制或不同配置，请参考 [advisor 与 subagent 和 opusplan 的对比](#与相关功能对比)。

## 费用

**每次 advisor 调用将对话发送给 advisor 模型，按 advisor 模型费率消耗 token。** API 计费用户按 advisor 模型的输入/输出费率计费。订阅用户的 advisor 使用计入计划用量限额。

Claude 仅在决策点调用 advisor，因此配对快速主模型和强 advisor 通常比全程运行强模型便宜。Advisor 用量计入 [`/usage`](https://code.claude.com/docs/en/costs#track-your-costs) 显示的会话总量。

API 响应中 advisor token 的报告方式详见 Claude API 文档的 [Usage and billing](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#usage-and-billing)。

## 对 prompt 缓存的影响

**会话中启用或禁用 advisor 不会使主模型的 [prompt cache](https://code.claude.com/docs/en/prompt-caching) 失效。** 与[切换模型或 effort level](https://code.claude.com/docs/en/prompt-caching#actions-that-invalidate-the-cache) 不同，切换 `/advisor` 保持缓存前缀完整，advisor 返回的指导作为记录一部分在后续 turn 被缓存。

Advisor 模型自身读取对话不被缓存。每次 advisor 调用都完整处理记录，调用间不复用。

## 要求

Advisor 工具需要满足以下全部条件：

| 要求 | 说明 |
| --- | --- |
| Claude Code v2.1.98 或更高 | 运行 `claude update` 升级 |
| 仅 Anthropic API | Advisor 是服务端执行的工具。不支持 Amazon Bedrock、Google Cloud Agent Platform 或 Microsoft Foundry。通过配置 `ANTHROPIC_BASE_URL` 的 [LLM gateway](https://code.claude.com/docs/en/llm-gateway) 使用时，取决于 gateway 是否将请求原样转发至 Anthropic API |
| 支持的主模型 | Opus 4.6+、Sonnet 4.6+ 或 Haiku 4.5。Fable 5 在 v2.1.170+ 同样支持 |

## 关闭 advisor

运行 `/advisor off` 或在 `/advisor` 选择器中选择 **No advisor** 即可停止使用并清除已保存的 `advisorModel`：

```
/advisor off
```

**彻底禁用 advisor 工具**，设置 `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`。`/advisor` 命令不可用，任何已配置的 `advisorModel` 被忽略。`--advisor` 标志仍可传入但无效果，现有脚本不会报错。详见[环境变量](https://code.claude.com/docs/en/env-vars)。

## 与相关功能对比

**Advisor 是组合模型优势的多种方式之一。** 根据你希望第二个模型在什么时机介入来选择：

| 方式 | 强模型何时运行 | 如何触发 |
| --- | --- | --- |
| Advisor 工具 | 在任务中的决策点 | Claude 认为需要指导时主动调用 |
| [`opusplan`](https://code.claude.com/docs/en/model-config#opusplan-model-setting) | 规划模式期间（受 `availableModels` 限制），然后切换到 Sonnet 执行 | 你进入规划模式 |
| [Subagent](https://code.claude.com/docs/en/sub-agents#choose-a-model) 设置 `model` | 整个委派子任务 | Claude 委派，或你调用 subagent |
| [`/model`](https://code.claude.com/docs/en/model-config#setting-your-model) | 后续所有 turn | 你切换模型 |

## 相关阅读

- [模型配置](https://code.claude.com/docs/en/model-config)：切换模型、设置 effort level、使用 `opusplan`
- [有效管理成本](https://code.claude.com/docs/en/costs)：跟踪跨模型 token 使用
- [Claude API 中的 Advisor 工具](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool)：了解底层 server tool 或直接通过 Messages API 使用
- [The advisor strategy](https://claude.com/blog/the-advisor-strategy)：为什么快速主模型搭配强 advisor 的策略有效
