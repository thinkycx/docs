---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】Fast Mode：加速响应
description: Fast Mode 用更高 token 单价换取 Opus 2.5 倍响应速度。涵盖开关方式、定价对比、成本权衡、适用场景、速率限制回退机制，以及组织管理员启用配置。
category: translation
tags: [claude-code, fast-mode, translation]
refs:
  - https://code.claude.com/docs/en/fast-mode.md
---

# Fast Mode：让 Opus 响应快 2.5 倍

> **核心价值：用更高的 token 单价换取更低的延迟，模型质量不变。**

> [!NOTE]
> Fast Mode 处于 [研究预览阶段](#研究预览)，功能、定价、可用性可能随反馈调整。

**Fast Mode 是 Claude Opus 的高速配置**，最高可将响应速度提升 2.5 倍，代价是更高的 token 单价。用 `/fast` 命令即可切换——需要快速迭代或实时调试时打开，关注成本时关闭。

**Fast Mode 不是另一个模型。** 它使用相同的 Claude Opus，只是通过不同的 API 配置优先保证速度。质量和能力完全一致，只是响应更快。当前支持 Opus 4.8 和 Opus 4.7，不支持 Sonnet、Haiku 等其他模型。

> [!WARNING]
> Opus 4.7 的 Fast Mode 已于 2026 年 6 月 25 日弃用，将在 2026 年 7 月 24 日移除。移除后，Opus 4.7 上的 Fast Mode 请求将直接报错（不会回退到标准 Opus 4.7）。请迁移到 Opus 4.8。

> [!NOTE]
> Fast Mode 需要 Claude Code v2.1.36 或更高版本。用 `claude --version` 检查当前版本。

**关键信息速览：**

| 项目 | 说明 |
|------|------|
| 开启方式 | CLI 中输入 `/fast`（VS Code 扩展暂不支持） |
| Opus 4.8 定价 | $10 / $50 per MTok（输入/输出） |
| Opus 4.7 定价 | $30 / $150 per MTok（输入/输出） |
| 适用范围 | 所有订阅计划（Pro/Max/Team/Enterprise）及 Claude Console |
| 计费方式 | 订阅用户通过 usage credits 计费，不包含在订阅限额内 |

## 切换 Fast Mode

**两种方式开关 Fast Mode：**

- 输入 `/fast` 后按 Tab 切换开/关
- 在 [用户设置文件](https://code.claude.com/docs/en/settings) 中设置 `"fastMode": true`

默认情况下，Fast Mode 跨会话持久保存。管理员可以配置为每次会话重新开始时重置，详见 [每次会话强制手动开启](#每次会话强制手动开启)。

**为了最佳成本效率，在会话开始时就启用 Fast Mode，而非中途切换。** 原因见 [理解成本权衡](#理解成本权衡)。

**启用后的表现：**

- 如果当前使用其他模型，Claude Code 自动切换到 Opus
- 显示确认信息："Fast mode ON"
- 提示符旁出现 `↯` 图标表示 Fast Mode 激活
- 随时运行 `/fast` 可查看当前状态

**关闭 Fast Mode 后不会切回原来的模型**——你仍留在 Opus 上。要切换模型请使用 `/model`。

Opus 4.8 从 Claude Code v2.1.154 起成为 Fast Mode 默认模型。v2.1.142 到 v2.1.153 版本默认使用 Opus 4.7。

## 理解成本权衡

**Fast Mode 的 token 单价高于标准 Opus，倍率因模型而异。**

| 模型 | 输入（每 MTok） | 输出（每 MTok） |
|------|----------------|----------------|
| Opus 4.8 | $10 | $50 |
| Opus 4.7 | $30 | $150 |

Fast Mode 定价在整个 1M token 上下文窗口内统一，不分段。标准 Opus 的对比价格见 [Claude 定价参考](https://platform.claude.com/docs/en/about-claude/pricing)。

**首次启用的成本影响：** 在一个对话中第一次启用 Fast Mode 时，你需要为整个对话上下文按 Fast Mode 未缓存输入价格支付一次费用。对话越深，这笔费用越高——所以从头开始启用更划算。此费用每个对话只收一次，后续关闭再开启不会重复收取。机制详情见 [Fast Mode 与提示缓存的交互](https://code.claude.com/docs/en/prompt-caching#turning-on-fast-mode)。

## 何时使用 Fast Mode

**适合 Fast Mode 的场景**——交互式工作，延迟比成本重要：

- 快速迭代代码修改
- 实时调试会话
- 时间紧迫的任务

**适合标准模式的场景：**

- 长时间自主运行的任务（速度不敏感）
- 批处理或 CI/CD 流水线
- 成本敏感的工作负载

### Fast Mode vs Effort Level

**两者都影响响应速度，但机制完全不同。**

| 设置 | 效果 |
|------|------|
| **Fast Mode** | 模型质量不变，延迟更低，成本更高 |
| **降低 Effort Level** | 减少思考时间，响应更快，复杂任务质量可能下降 |

两者可以叠加：对简单任务同时启用 Fast Mode + 低 [Effort Level](https://code.claude.com/docs/en/model-config#adjust-effort-level)，获得最大速度。

## 使用条件

**Fast Mode 需要同时满足以下条件：**

| 条件 | 说明 |
|------|------|
| Anthropic API 或订阅计划 | 仅通过 Anthropic Console API 和 Claude 订阅计划（使用 usage credits）可用。不支持 Amazon Bedrock、Google Vertex AI、Microsoft Azure Foundry、Claude Platform on AWS |
| Usage Credits 已开启 | 账户必须开启 usage credits（允许超出计划用量计费）。个人账户在 [Console 计费设置](https://platform.claude.com/settings/organization/billing) 开启；Team/Enterprise 需管理员开启 |
| Team/Enterprise 需 Owner 启用 | 默认关闭。Owner 必须显式 [启用 Fast Mode](#为组织启用-fast-mode) |

> [!NOTE]
> Fast Mode 用量直接从 usage credits 扣除，即使你的计划仍有剩余用量也是如此。Fast Mode token 不计入计划包含的用量，从第一个 token 起就按 Fast Mode 费率计费。

> [!NOTE]
> 如果组织未启用 Fast Mode，`/fast` 命令会显示 "Fast mode has been disabled by your organization."。如果组织的 [`availableModels`](https://code.claude.com/docs/en/model-config#restrict-model-selection) 白名单排除了 Fast Mode Opus 模型，`/fast` 会被拒绝并提示 "is not in your organization's allowed models"。例外情况：当前会话已在支持 Fast Mode 的允许 Opus 模型上运行时，`/fast` 会直接在当前模型上启用 Fast Mode。

### 为组织启用 Fast Mode

**启用位置取决于组织使用的产品：**

| 产品 | 操作位置 |
|------|----------|
| Console（API 客户） | 管理员在 [Claude Code preferences](https://platform.claude.com/claude-code/preferences) 中启用 |
| Claude AI（Team / Enterprise） | Owner 在 [Admin Settings > Claude Code](https://claude.ai/admin-settings/claude-code) 中启用 |

也可通过设置环境变量 `CLAUDE_CODE_DISABLE_FAST_MODE=1` 完全禁用 Fast Mode，详见 [环境变量](https://code.claude.com/docs/en/env-vars)。

### 每次会话强制手动开启

**默认行为：** Fast Mode 跨会话保持。管理员可设置 `fastModePerSessionOptIn` 为 `true`，让每次新会话都以 Fast Mode 关闭状态开始，用户需手动输入 `/fast` 开启。

```json
{
  "fastModePerSessionOptIn": true
}
```

在 [managed settings](https://code.claude.com/docs/en/settings#settings-files) 或 [server-managed settings](https://code.claude.com/docs/en/server-managed-settings) 中配置。

**适用场景：** 组织中用户运行多个并发会话时控制成本。用户仍可随时用 `/fast` 启用，但每次新会话都会重置。移除此设置后恢复默认持久行为。

## 处理速率限制

**Fast Mode 有独立于标准 Opus 的速率限制。** Opus 4.8 和 Opus 4.7 的 Fast Mode 共享同一个速率限制池。

**触发速率限制或 usage credits 耗尽时的行为：**

1. Fast Mode 自动回退到标准速度
2. `↯` 图标变灰表示冷却中
3. 继续以标准速度和价格工作
4. 冷却期结束后 Fast Mode 自动恢复

要手动关闭 Fast Mode 而非等待冷却，运行 `/fast`。

## 研究预览

Fast Mode 是研究预览功能，意味着：

- 功能可能根据反馈变化
- 可用性和定价可能调整
- 底层 API 配置可能演进

通过常规 Anthropic 支持渠道反馈问题。

## 相关文档

- [模型配置](https://code.claude.com/docs/en/model-config)：切换模型和调整 effort level
- [有效管理成本](https://code.claude.com/docs/en/costs)：追踪 token 用量和降低成本
- [状态栏配置](https://code.claude.com/docs/en/statusline)：显示模型和上下文信息
