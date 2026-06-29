---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】模型配置
description: Claude Code 的模型配置详解，涵盖模型别名、模型选择限制、特殊模型行为（opusplan/fallback/effort level/extended thinking/extended context）以及第三方部署的模型固定方案。
category: translation
tags: [claude-code, model-config, translation]
refs:
  - https://code.claude.com/docs/en/model-config.md
---

# 模型配置

> Claude Code 的模型配置方式，包括 `opusplan` 等模型别名的使用

## 可用模型

**Claude Code 的 `model` 设置支持「模型别名」和「模型名称」两种写法。** 具体来说：

* **模型别名** — 简短易记的名字，如 `opus`、`sonnet`
* **模型名称** — 完整的模型标识
  * Anthropic API：完整的 **[模型名称](https://platform.claude.com/docs/en/about-claude/models/overview)**
  * Bedrock：inference profile ARN
  * Foundry：deployment name
  * Vertex：version name

> **注意：** `ANTHROPIC_BASE_URL` 只改变请求发送的目标地址，不改变回答问题的模型。如需通过 LLM 网关路由请求，参见 [LLM gateways](https://code.claude.com/docs/en/llm-gateway)。

### 模型别名

**别名让你不必记住完整版本号就能选择模型。** 别名会随时间更新指向最新推荐版本。

| 模型别名 | 行为说明 |
| --- | --- |
| **`default`** | 特殊值，清除模型覆盖设置，恢复为账户类型对应的推荐模型。本身不是别名 |
| **`best`** | 组织有 Fable 5 访问权限时使用 Fable 5，否则使用最新 Opus |
| **`fable`** | 使用 Claude Fable 5，适合最困难、最长时间运行的任务 |
| **`sonnet`** | 使用最新 Sonnet，适合日常编码 |
| **`opus`** | 使用最新 Opus，适合复杂推理 |
| **`haiku`** | 使用快速高效的 Haiku，适合简单任务 |
| **`sonnet[1m]`** | Sonnet + [100 万 token 上下文窗口](https://platform.claude.com/docs/en/build-with-claude/context-windows#1m-token-context-window)，适合长会话 |
| **`opus[1m]`** | Opus + [100 万 token 上下文窗口](https://platform.claude.com/docs/en/build-with-claude/context-windows#1m-token-context-window)，适合长会话 |
| **`opusplan`** | 规划阶段用 `opus`，执行阶段自动切换到 `sonnet` |

**各 API 提供商的别名解析情况不同：**

| 提供商 | `opus` 解析为 | `sonnet` 解析为 |
| --- | --- | --- |
| Anthropic API | Opus 4.8 | Sonnet 4.6 |
| Claude Platform on AWS | Opus 4.7 | Sonnet 4.6 |
| Bedrock / Vertex / Foundry | Opus 4.6 | Sonnet 4.5 |

在 Bedrock、Vertex 和 Foundry 上，更新的模型需要显式指定完整模型名称，或设置 `ANTHROPIC_DEFAULT_OPUS_MODEL` / `ANTHROPIC_DEFAULT_SONNET_MODEL` 环境变量。

如果需要固定到特定版本（不随别名更新），使用完整模型名如 `claude-opus-4-8`，或设置对应的环境变量。

> **注意：** Opus 4.8 需要 Claude Code v2.1.154 或更高版本。运行 `claude update` 升级。

### 使用 Fable 5

**[Claude Fable 5](https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5) 是 Claude Code 中能力最强的模型，适合超出单次完成范围的大型任务。** 它能维持长时间的自主会话，在行动前先调查，比小模型更频繁地验证自己的工作。

Fable 5 不是默认模型，需通过 `/model fable` 选择。当安全分类器标记请求时（最常见于网络安全和生物领域），会触发[自动模型回退](#自动模型回退)。

使用 Fable 5 的最佳实践：

* **描述结果而非步骤** — 告诉它你想要的结果，让它自己规划路径。配合 [goal](https://code.claude.com/docs/en/goal) 使用效果更佳
* **交给它模糊问题** — 根因调查、故障排查、架构决策等需要深入探索的场景最能发挥优势
* **不需要提醒它验证** — 它会自动验证工作成果，无需额外提示
* **敢于交给它大任务** — 你通常需要拆分的工作可以整个交给它，它不会在长会话中丢失上下文

> **注意：** Fable 5 需要 Claude Code v2.1.170 或更高版本。旧版本的模型选择器不会显示 Fable 5。Fable 5 在 [zero data retention](https://code.claude.com/docs/en/zero-data-retention) 模式下不可用。

### 设置模型

**模型可以通过以下方式配置（按优先级从高到低）：**

| 优先级 | 方式 | 说明 |
| --- | --- | --- |
| 1 | 会话中切换 | `/model <alias\|name>` 立即切换；无参数的 `/model` 打开选择器 |
| 2 | 启动时指定 | `claude --model <alias\|name>` |
| 3 | 环境变量 | `ANTHROPIC_MODEL=<alias\|name>` |
| 4 | 设置文件 | `model` 字段 |

从 v2.1.153 起，`/model` 会将选择保存为新会话的默认值（写入用户设置的 `model` 字段）。在选择器中：

* `Enter`：切换模型并保存为默认
* `s`：仅当前会话切换

`--model` 和 `ANTHROPIC_MODEL` 只对启动时的会话生效。要同时在不同终端使用不同模型，各终端用自己的 `--model` 启动。

恢复的会话（`claude --resume`、`--continue`、`/resume`）保持保存时的模型，不受当前 `model` 设置影响。如果该模型已退役或被 [`availableModels`](#限制模型选择) 排除，则回退到正常优先级顺序。

当启动时的模型来自项目或托管设置而非你自己的选择时，启动头会显示是哪个设置文件指定的。

当请求的模型有退役日期或被自动重映射到新版本时，Claude Code 会显示警告。交互会话显示为启动通知；从 v2.1.182 起，[非交互模式](https://code.claude.com/docs/en/headless)的默认文本输出格式也会写到 stderr。`--output-format json` 和 `stream-json` 时不显示 stderr 警告，可从 [result message](https://code.claude.com/docs/en/headless#get-structured-output) 的 `modelUsage` 字段读取实际模型。

示例：

```bash theme={null}
# Start with Opus
claude --model opus

# Switch to Sonnet during session
/model sonnet
```

设置文件示例：

```json theme={null}
{
    "permissions": {
        ...
    },
    "model": "opus"
}
```

## 限制模型选择

**企业管理员可通过 `availableModels` 限制用户可选的模型。** 在[托管或策略设置](https://code.claude.com/docs/en/settings#settings-files)中配置，条目可以是模型族（如 `sonnet`）、版本前缀（如 `claude-sonnet-4-5`）或完整模型 ID。

设置 `availableModels` 后，白名单在所有可指定模型的位置生效：

* **主会话模型** — `/model`、`--model`、`ANTHROPIC_MODEL`、`model` 设置、恢复会话时的模型
* **别名解析** — `ANTHROPIC_DEFAULT_OPUS_MODEL` 等环境变量不能将允许的别名重定向到白名单外的模型
* **Fast 模式** — `/fast` 在会隐式切换到白名单外 Opus 时拒绝切换
* **子代理模型** — [子代理](https://code.claude.com/docs/en/sub-agents#choose-a-model)前置信息的 `model` 字段、Agent tool 的 `model` 参数等
* **Skill 和 Command 模型** — [skills 和 commands](https://code.claude.com/docs/en/skills) 前置信息的 `model`
* **Advisor 模型** — [`advisorModel`](https://code.claude.com/docs/en/advisor) 设置和 `--advisor` 标志
* **后台代理模型** — [dispatch picker](https://code.claude.com/docs/en/agent-view) 中选择的模型

**被阻止时的行为：**

| 场景 | 行为 |
| --- | --- |
| `/model` 切换到被阻止的模型 | 拒绝并报错 |
| `--model`/`ANTHROPIC_MODEL`/`model` 设置被阻止 | 启动时替换为默认模型并显示警告 |
| 子代理/skill/command 的 model 被阻止 | 回退到继承或默认模型 |
| `advisorModel` 被阻止 | 禁用本次会话的 advisor |
| `--advisor` 值被阻止 | 启动时直接退出报错 |

自动模型变更同样受白名单检查：[fallback chain](#回退模型链) 中白名单外的元素被丢弃；`opusplan` 的 plan-mode 升级到被排除的模型时跳过；自动模型回退目标被排除时不执行回退。

```json theme={null}
{
  "availableModels": ["sonnet", "haiku"]
}
```

### 各平台的覆盖情况

**每个平台都会执行白名单，但送达机制不同。**

| 送达机制 | CLI 和 IDE | Desktop 本地会话 | Web/移动/云会话 | Agent SDK 和非交互 | Cowork |
| --- | --- | --- | --- | --- | --- |
| [Server-managed settings](https://code.claude.com/docs/en/server-managed-settings) | 生效 | 生效 | 生效 | 生效 | 不送达 |
| [MDM 或托管设置文件](https://code.claude.com/docs/en/settings#settings-files) | 生效 | 生效 | 不送达 | 生效 | 视部署情况 |

关键点：

* 云会话运行在 Anthropic 管理的 VM 上，设备上部署的设置无法到达，需通过 server-managed settings 送达白名单
* Cowork 不是 Claude Code 平台，不接收 server-managed settings
* Bedrock/Vertex/Foundry 等第三方提供商不接收 server-managed settings，需通过 MDM 或托管设置文件送达
* server-managed 送达要求会话用组织登录或直接配置的 API key 认证。通过 [`apiKeyHelper`](https://code.claude.com/docs/en/settings#available-settings) 脚本生成 key 的环境应通过 MDM/托管设置文件送达

### 默认模型的行为

**`availableModels` 单独使用时不影响 Default 选项**，除非同时设置了 [`enforceAvailableModels`](#对默认模型强制白名单)。Default 仍然可用，解析为[基于订阅层级的系统运行时默认值](#default-模型设置)。

空的 `availableModels` 数组不会触发 Default 模型强制：`availableModels: []` 时，命名模型选择被阻止，但账户类型的 Default 模型仍可用。

### 对默认模型强制白名单

**设置 `enforceAvailableModels: true` 可将白名单扩展到 Default 选项。** 需要 Claude Code v2.1.175 或更高版本。

```json theme={null}
{
  "availableModels": ["sonnet", "haiku"],
  "enforceAvailableModels": true
}
```

当账户类型的默认模型不在白名单中时，Default 选项会解析为 `availableModels` 中第一个允许且可用的模型。这适用于所有到达 default 的场景：会话启动、选择 Default、fallback chain 中的 `"default"` 关键字、被排除选择被丢弃时的回退。

`enforceAvailableModels` 在 `availableModels` 未设置或为空时无效，无法将用户锁定在所有模型之外。

### 完全控制用户使用的模型

**`model` 设置是初始选择而非强制。** 要完全控制模型体验，需组合以下设置：

| 设置 | 作用 |
| --- | --- |
| `availableModels` | 限制用户可切换的模型 |
| `enforceAvailableModels` | 让 Default 也遵循白名单 |
| `model` | 设置会话启动时的初始模型 |
| `ANTHROPIC_DEFAULT_*_MODEL` 环境变量 | 控制 Default 和各别名解析的具体版本 |

完整示例 — 让用户默认用 Sonnet 4.5，选择器只允许 Sonnet 和 Haiku，Default 也受限：

```json theme={null}
{
  "model": "claude-sonnet-4-5",
  "availableModels": ["claude-sonnet-4-5", "haiku"],
  "enforceAvailableModels": true,
  "env": {
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-sonnet-4-5"
  }
}
```

没有 `enforceAvailableModels` 或 `env` 时，用户选择 Default 会绕过版本固定。两个设置覆盖不同范围：`enforceAvailableModels` 让 Default 遵循白名单，`env` 固定别名解析到具体版本。

### 合并行为

**最高优先级的托管设置源定义的 `availableModels` 单独适用，不合并。** 管理员部署的托管源之间也不合并。用户/项目/本地设置的列表会按[常规数组合并规则](https://code.claude.com/docs/en/settings#settings-precedence)拼接去重。

从 v2.1.175 起，托管列表替换低优先级条目（旧版本会合并）。

列表中，指定某族具体模型的条目（版本前缀或完整 ID）会禁用该族的通配符：`["sonnet", "claude-sonnet-4-5"]` 只允许 Sonnet 4.5，不允许所有 Sonnet。

### Mantle 模型 ID

**启用 [Bedrock Mantle endpoint](https://code.claude.com/docs/en/amazon-bedrock#use-the-mantle-endpoint) 时**，`availableModels` 中以 `anthropic.` 开头的条目会作为自定义选项加入 `/model` 选择器并路由到 Mantle endpoint。Mantle ID 包含族名，因此算作具体条目，会禁用该族通配符。

### 组织级模型限制

**组织管理员可在 Claude Console 中禁用特定模型。** 适合通过 Anthropic API 认证、只需要一个全组织开关的场景。需要 Claude Code v2.1.187 或更高版本。

受限模型从 `/model` 选择器中隐藏。两种限制同时生效：模型必须同时被 `availableModels` 允许且未被组织限制，才能选择。

组织限制送达给 Anthropic API 和 LLM gateway 部署的会话。Bedrock、Vertex、Foundry 和 Claude Platform on AWS 的会话不接收，需用 `availableModels` 替代。

## 特殊模型行为

### `default` 模型设置

**Default 模型因账户类型而异：**

| 账户类型 | 默认模型 |
| --- | --- |
| Max、Team Premium、Enterprise 按量付费、Anthropic API | Opus 4.8 |
| Claude Platform on AWS | Opus 4.7 |
| Pro、Team Standard、Enterprise 订阅席位 | Sonnet 4.6 |
| Bedrock、Vertex、Foundry | Sonnet 4.5 |

Enterprise 按量付费指按使用量而非订阅席位计费的 Enterprise 组织。

当托管设置[对默认模型强制白名单](#对默认模型强制白名单)且账户类型默认值不在 `availableModels` 中时，`default` 解析为强制后的 Default 而非上表值。

Fable 5 在任何账户类型上都不是默认模型。只有主动选择（`/model fable`、`model` 设置或 `best` 别名）才会使用。

### `opusplan` 模型设置

**`opusplan` 提供自动化的混合方案：规划用 Opus 推理，执行用 Sonnet 高效生成。**

* **Plan 模式** — 使用 `opus` 进行复杂推理和架构决策
* **Execution 模式** — 自动切换到 `sonnet` 生成代码和实现

Plan 阶段的 Opus 使用与 `opus` 设置相同的上下文窗口。订阅层级自动升级 Opus 到 1M 上下文时，`opusplan` 的 plan 模式也会获得升级。要在非自动升级层级强制两个阶段都用 1M，设置模型为 `opusplan[1m]`。

当 [`availableModels`](#限制模型选择) 排除 Opus 时，`opusplan` 在 plan 模式保持使用 Sonnet。类似地，排除 Sonnet 时 Haiku 会话在 plan 模式保持 Haiku。

如果想让 Claude 在任务执行中自行决定何时咨询第二个模型（而非在 plan 边界切换），参见 [advisor tool](https://code.claude.com/docs/en/advisor)。

### 回退模型链

**当主模型过载、不可用或返回不可重试的服务器错误时，Claude Code 可切换到备用模型。** 认证、计费、速率限制、请求大小和传输错误不会触发切换。

配置一个或多个备用模型后，Claude Code 按顺序尝试，切换时显示通知。切换仅持续当前轮次，下次消息重新尝试主模型。链上限为去重后三个模型。

单次会话设置：

```bash theme={null}
claude --fallback-model sonnet,haiku
```

持久化到设置中：

```json theme={null}
{
  "fallbackModel": ["claude-sonnet-4-6", "claude-haiku-4-5"]
}
```

`--fallback-model` 优先于 `fallbackModel` 设置。元素支持模型名或别名，`"default"` 展开为默认模型。

跳过元素的两种情况：不可达的模型（如已退役）被跳过，继续下一个；白名单外的元素在读取链时被丢弃。

### 自动模型回退

**本节讲的是 Fable 5 基于内容的回退。可用性回退参见[回退模型链](#回退模型链)。**

Fable 5 运行时有网络安全和生物内容的安全分类器。分类器标记请求时，Claude Code 在默认 Opus 模型上重新运行该请求并在记录中显示通知：Anthropic API 和 LLM gateway 上为 Opus 4.8，Claude Platform on AWS 上为 Opus 4.7。

会话随后在该 Opus 模型上继续。要返回 Fable 5，运行 `/model fable`。

回退目标受 [`availableModels`](#限制模型选择) 检查。目标被阻止时不发生回退，标记请求以正常错误结束。

#### 检查触发回退的原因

回退可能在会话第一次请求就触发（在你发送任何异常内容之前），因为首次请求携带工作区上下文（CLAUDE.md 内容和 git status）。包含安全或生物材料的仓库可能仅凭上下文就触发分类器。

要检查是否是自定义内容导致触发，使用 `claude --safe-mode` 启动，它禁用 CLAUDE.md、skills、MCP servers 和 hooks 等自定义内容。Git status 和目录名不是自定义内容，仍会包含。

#### 切换前询问

**要在每次请求被标记时决定如何处理（而非自动切换）**，运行 `/config` 关闭 "switch models when a message is flagged"。标记请求时会暂停会话，提供两个选项：切换到 Opus，或编辑 prompt 后在 Fable 5 上重试。

特殊情况：

* 两个模型都标记同一请求时，可编辑重试或开新会话
* 移动端 [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web) 不支持编辑重试，需切换模型或在桌面端继续
* [非交互模式](https://code.claude.com/docs/en/cli-reference#cli-flags)中标记请求直接以拒绝结束
* 回退目标被白名单阻止时不显示 prompt，标记请求直接以拒绝结束

#### 在 Bedrock、Vertex AI 和 Foundry 上启用回退

**在第三方提供商上，模型 ID 是提供商特定的，自动回退需要 Claude Code 能识别两个模型：**

* 当前模型需被识别为 Fable 5：ID 包含 `claude-fable-5`、匹配 `ANTHROPIC_DEFAULT_FABLE_MODEL`、或通过 [`modelOverrides`](#按版本覆盖模型-id) 映射
* 回退目标需解析为 Opus：`ANTHROPIC_DEFAULT_OPUS_MODEL` 的值（如设置），否则为提供商模型列表中的 Opus 4.8

任一模型无法识别时不自动切换，标记请求以拒绝消息结束。要启用，设置 `ANTHROPIC_DEFAULT_FABLE_MODEL` 为你的 Fable 5 ID，`ANTHROPIC_DEFAULT_OPUS_MODEL` 为 Opus 4.8 ID。

#### 安全研究和生物工作负载

进攻性安全或生物领域（渗透测试、CTF、生物相关代码库）会频繁触发回退，常在首次请求就发生。对于实质性生物工作，几乎所有请求都会被重路由。

这是这些领域的预期路由，不是账户标记。如果组织需要 Fable 级能力处理此类工作，联系 Anthropic 账户团队了解可信访问计划。

### 调整推理投入等级（Effort Level）

**[Effort levels](https://platform.claude.com/docs/en/build-with-claude/effort) 控制自适应推理，让模型根据任务复杂度决定是否思考以及思考多少。** 低投入更快更便宜，适合简单任务；高投入提供更深层推理，适合复杂问题。

各模型支持的等级：

| 模型 | 支持的等级 |
| --- | --- |
| Fable 5 | `low`, `medium`, `high`, `xhigh`, `max` |
| Opus 4.8 和 Opus 4.7 | `low`, `medium`, `high`, `xhigh`, `max` |
| Opus 4.6 和 Sonnet 4.6 | `low`, `medium`, `high`, `max` |

设置了模型不支持的等级时，Claude Code 回退到不超过该等级的最高支持等级。例如 `xhigh` 在 Opus 4.6 上以 `high` 运行。

**默认 effort：**

| 模型 | 默认等级 |
| --- | --- |
| Fable 5、Opus 4.8、Opus 4.6、Sonnet 4.6 | `high` |
| Opus 4.7 | `xhigh` |

首次运行 Fable 5、Opus 4.8 或 Opus 4.7 时，Claude Code 应用该模型的默认 effort，即使你之前为其他模型设了不同等级。

`low`/`medium`/`high`/`xhigh` 跨会话持久化。`max` 提供最深度推理但仅限当前会话（除非通过 `CLAUDE_CODE_EFFORT_LEVEL` 环境变量设置）。

`/effort` 菜单还提供 `ultracode` — 这是 Claude Code 设置而非模型 effort level：它向模型发送 `xhigh`，并让 Claude 额外为实质性任务编排[动态工作流](https://code.claude.com/docs/en/workflows)。仅限当前会话。通过 `/effort` 设置，或通过 `--settings` / Agent SDK control request 传递 `"ultracode": true`。

#### 选择合适的等级

| 等级 | 适用场景 |
| --- | --- |
| `low` | 短小、范围明确、对延迟敏感但对智能不敏感的任务 |
| `medium` | 成本敏感的工作，可牺牲部分智能 |
| `high` | 平衡 token 消耗和智能。多数模型的默认值 |
| `xhigh` | 更深层推理，更高 token 消耗。Opus 4.7 的默认值 |
| `max` | 可能改善高难度任务表现，但可能有边际递减和过度思考。使用前先测试 |
| `ultracode` | 为每个实质性任务规划[动态工作流](https://code.claude.com/docs/en/workflows)，每消息 `xhigh` 推理。仅限会话 |

Effort scale 按模型校准，同名等级在不同模型上代表的底层值不同。

#### 使用 ultrathink 做单次深度推理

在 prompt 中包含 `ultrathink` 可请求该轮更深度的推理，不改变会话 effort 设置。Claude Code 识别此关键词并添加上下文指令，API 层面的 effort level 不变。其他短语如 "think"、"think hard"、"think more" 作为普通 prompt 文本传递，不被识别为关键词。

#### 设置 effort level 的方式

| 方式 | 说明 |
| --- | --- |
| `/effort` | 无参数打开交互滑块；加等级名直接设置；`/effort auto` 重置为模型默认 |
| `/model` 中 | 选模型时用左右方向键调整 |
| `--effort` 标志 | 启动时传等级名，单次会话有效 |
| `CLAUDE_CODE_EFFORT_LEVEL` | 环境变量，优先级最高 |
| 设置文件 `effortLevel` | 接受 `low`/`medium`/`high`/`xhigh`，不接受 `max` 和 `ultracode` |
| Skill/subagent frontmatter `effort` | 覆盖该 skill/subagent 运行时的 effort |

优先级：环境变量 > 配置的等级 > 模型默认。Frontmatter effort 在 skill/subagent 活跃时覆盖会话等级，但不覆盖环境变量。

Effort 滑块在 `/model` 中选择支持的模型时出现。当前等级也显示在 logo 和 spinner 旁（如 "with low effort"）。

#### 自适应推理与固定思考预算

**自适应推理让思考在每步都是可选的，Claude 可以对常规 prompt 更快响应，对需要深思的步骤保留深度思考。** 如果想让 Claude 比当前等级更多或更少地思考，可在 prompt 或 CLAUDE.md 中直接说明。

Opus 4.7 及更高版本始终使用自适应推理，Fable 5 也是。固定思考预算模式和 `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING` 不适用于它们。

在 Opus 4.6 和 Sonnet 4.6 上，可设置 `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` 恢复到由 `MAX_THINKING_TOKENS` 控制的固定思考预算。参见[环境变量](https://code.claude.com/docs/en/env-vars)。

### 扩展思考（Extended Thinking）

**扩展思考是 Claude 在响应前输出的推理过程。** 在支持[自适应推理](#调整推理投入等级effort-level)的模型上，effort level 是控制思考量的主要手段；以下设置控制思考的开关和显示方式。

| 控制项 | 设置方式 |
| --- | --- |
| 当前会话切换 | macOS 按 `Option+T`，Windows/Linux 按 `Alt+T` |
| 全局默认 | `/config` 切换 thinking mode，保存为 `alwaysThinkingEnabled` |
| 无论 effort 都禁用 | 设置 [`MAX_THINKING_TOKENS=0`](https://code.claude.com/docs/en/env-vars)（Anthropic API 上关闭思考，Fable 5 除外；第三方提供商上省略 `thinking` 参数，自适应推理模型可能仍会思考） |

Fable 5 无法关闭思考。会话切换、`alwaysThinkingEnabled` 和 `MAX_THINKING_TOKENS=0` 对其无效。

思考输出默认折叠。按 `Ctrl+O` 切换 verbose 模式查看灰色斜体的推理过程。Anthropic API 上的交互会话默认接收编辑过的 thinking blocks，如需完整摘要设置 `showThinkingSummaries: true`。所有生成的 thinking tokens 都会计费，无论折叠或编辑。

### 扩展上下文（Extended Context）

**Fable 5、Opus 4.6 及更高版本和 Sonnet 4.6 支持 [100 万 token 上下文窗口](https://platform.claude.com/docs/en/build-with-claude/context-windows#1m-token-context-window)。**

可用性因模型和计划而异：

| 计划 | Opus 1M 上下文 | Sonnet 1M 上下文 |
| --- | --- | --- |
| Max、Team、Enterprise | 订阅包含 | 需要 [usage credits](https://support.claude.com/en/articles/12429409-extra-usage-for-paid-claude-plans) |
| Pro | 需要 usage credits | 需要 usage credits |
| API 和按量付费 | 完全可用 | 完全可用 |

在 Max/Team/Enterprise 上，Opus 自动升级到 1M 上下文。Anthropic API 上，Fable 5、Opus 4.8 和 Opus 4.7 始终以 1M 窗口运行。Sonnet 1M 不属于自动升级，在所有订阅计划上都需要 usage credits。

禁用 1M 上下文：设置 `CLAUDE_CODE_DISABLE_1M_CONTEXT=1`。

1M 窗口使用标准模型定价，超过 200K 的 token 没有溢价。订阅包含 extended context 的计划从订阅扣除；通过 usage credits 访问的从 credits 扣除。

使用 `[1m]` 后缀：

```bash theme={null}
# Use the opus[1m] or sonnet[1m] alias
/model opus[1m]
/model sonnet[1m]

# Or append [1m] to a full model name
/model claude-opus-4-8[1m]
```

## 查看当前模型

在以下两处可查看当前使用的模型：

* [Status line](https://code.claude.com/docs/en/statusline)（如有配置）
* `/status`（同时显示账户信息）

## 添加自定义模型选项

**使用 `ANTHROPIC_CUSTOM_MODEL_OPTION` 向 `/model` 选择器添加自定义条目，不替换内置别名。** 适合测试 Claude Code 未默认列出的模型 ID。LLM gateway 部署时如果启用了 `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1`，选择器可从 gateway 的 `/v1/models` 填充，此变量只在 discovery 禁用或未返回所需模型时才需要。参见 [gateway model discovery](https://code.claude.com/docs/en/llm-gateway-protocol#model-discovery)。

示例：

```bash theme={null}
export ANTHROPIC_CUSTOM_MODEL_OPTION="my-gateway/claude-opus-4-8"
export ANTHROPIC_CUSTOM_MODEL_OPTION_NAME="Opus via Gateway"
export ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION="Custom deployment routed through the internal LLM gateway"
```

自定义条目出现在选择器底部。`_NAME` 和 `_DESCRIPTION` 可选，省略时用模型 ID 做名称，描述默认为 `Custom model (<model-id>)`。

Claude Code 不验证 `ANTHROPIC_CUSTOM_MODEL_OPTION` 中的模型 ID。当 `availableModels` 设置时，需将自定义 ID 也加入白名单。包含族名的自定义 ID（如 `my-gateway/claude-opus-4-8`）算作该族的具体条目，会禁用通配符。

## 环境变量

**以下环境变量控制别名映射的具体模型名称：**

| 环境变量 | 说明 |
| --- | --- |
| `ANTHROPIC_DEFAULT_FABLE_MODEL` | `fable` 别名使用的模型，也是第三方提供商上 Claude Code 识别 Fable 5 的依据 |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | `opus` 别名使用的模型，或 `opusplan` Plan Mode 激活时的模型 |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | `sonnet` 别名使用的模型，或 `opusplan` 非 Plan Mode 时的模型 |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | `haiku` 别名使用的模型，或[后台功能](https://code.claude.com/docs/en/costs#background-token-usage)使用的模型 |
| `CLAUDE_CODE_SUBAGENT_MODEL` | 所有[子代理](https://code.claude.com/docs/en/sub-agents#choose-a-model)和[代理团队](https://code.claude.com/docs/en/agent-teams)使用的模型。覆盖 `model` 参数和 frontmatter。设为 `inherit` 使用正常模型解析 |

> 注意：`ANTHROPIC_SMALL_FAST_MODEL` 已弃用，由 `ANTHROPIC_DEFAULT_HAIKU_MODEL` 替代。

### 为第三方部署固定模型

**通过 Bedrock/Vertex/Foundry/Claude Platform on AWS 部署时，在推送给用户前先固定模型版本。**

不固定时，Claude Code 使用别名解析为各提供商的内置默认 ID，该默认值可能落后于最新 Anthropic 发布且可能未在用户账户中启用。不可用时，Bedrock 和 Vertex 用户会看到通知并回退到前一版本；Foundry 用户会看到错误。

> **警告：** 将模型环境变量设为特定版本 ID 作为初始设置的一部分。固定让你控制用户何时迁移到新模型。

各提供商示例：

| 提供商 | 示例 |
| --- | --- |
| Bedrock | `export ANTHROPIC_DEFAULT_OPUS_MODEL='us.anthropic.claude-opus-4-8'` |
| Vertex AI | `export ANTHROPIC_DEFAULT_OPUS_MODEL='claude-opus-4-8'` |
| Foundry | `export ANTHROPIC_DEFAULT_OPUS_MODEL='claude-opus-4-8'` |

对 `ANTHROPIC_DEFAULT_FABLE_MODEL`、`ANTHROPIC_DEFAULT_SONNET_MODEL` 和 `ANTHROPIC_DEFAULT_HAIKU_MODEL` 应用相同模式。所有提供商的当前和历史模型 ID 参见 [Models overview](https://platform.claude.com/docs/en/about-claude/models/overview)。

为固定模型启用 extended context，在环境变量值后加 `[1m]`：

```bash theme={null}
export ANTHROPIC_DEFAULT_OPUS_MODEL='claude-opus-4-8[1m]'
```

`[1m]` 后缀对 `opus`/`sonnet` 别名的所有使用生效，包括 `opusplan` 的 plan-mode Opus 阶段。Claude Code 发送前会剥离后缀。只在底层模型支持 1M 时添加。后缀按变量读取，一个变量中没有 `[1m]` 的模型即使在另一个变量中设了 `[1m]` 也使用 200K。

> 通过 MDM 或托管设置文件送达的 `availableModels` 白名单在第三方提供商上仍然适用。过滤基于别名、版本前缀或完整提供商模型 ID 匹配。`us.anthropic.` 等提供商前缀不被剥离，要允许特定模型需列出选择器显示的相同 ID，或通过 [`modelOverrides`](#按版本覆盖模型-id) 映射。白名单条目和请求模型的 `[1m]` 后缀在匹配前都被剥离。

### 自定义固定模型的显示和能力

**固定第三方提供商上的模型时，提供商特定 ID 会在选择器中原样显示，Claude Code 可能无法识别模型支持哪些功能。** 可通过伴随环境变量覆盖显示名称和声明能力。

这些变量在 Bedrock、Vertex、Foundry 等第三方提供商上生效。`_NAME` 和 `_DESCRIPTION` 在 `ANTHROPIC_BASE_URL` 指向 LLM gateway 时也生效。直连 `api.anthropic.com` 时无效。

| 环境变量 | 说明 |
| --- | --- |
| `ANTHROPIC_DEFAULT_OPUS_MODEL_NAME` | 选择器中固定 Opus 模型的显示名 |
| `ANTHROPIC_DEFAULT_OPUS_MODEL_DESCRIPTION` | 选择器中固定 Opus 模型的描述 |
| `ANTHROPIC_DEFAULT_OPUS_MODEL_SUPPORTED_CAPABILITIES` | 固定 Opus 模型支持的能力（逗号分隔） |

`_NAME`、`_DESCRIPTION`、`_SUPPORTED_CAPABILITIES` 后缀同样适用于 `ANTHROPIC_DEFAULT_SONNET_MODEL`、`ANTHROPIC_DEFAULT_HAIKU_MODEL`、`ANTHROPIC_DEFAULT_FABLE_MODEL` 和 `ANTHROPIC_CUSTOM_MODEL_OPTION`。

支持的能力值：

| 能力值 | 启用的功能 |
| --- | --- |
| `effort` | Effort levels 和 `/effort` 命令 |
| `xhigh_effort` | `xhigh` effort level |
| `max_effort` | `max` effort level |
| `thinking` | 扩展思考 |
| `adaptive_thinking` | 自适应推理 |
| `interleaved_thinking` | 工具调用间的思考 |

设置 `_SUPPORTED_CAPABILITIES` 时，列出的能力启用，未列出的禁用。未设置时 Claude Code 基于模型 ID 自动检测。

完整示例：

```bash theme={null}
export ANTHROPIC_DEFAULT_OPUS_MODEL='arn:aws:bedrock:us-east-1:123456789012:custom-model/abc'
export ANTHROPIC_DEFAULT_OPUS_MODEL_NAME='Opus via Bedrock'
export ANTHROPIC_DEFAULT_OPUS_MODEL_DESCRIPTION='Opus 4.7 routed through a Bedrock custom endpoint'
export ANTHROPIC_DEFAULT_OPUS_MODEL_SUPPORTED_CAPABILITIES='effort,xhigh_effort,max_effort,thinking,adaptive_thinking,interleaved_thinking'
```

### 按版本覆盖模型 ID

**族级环境变量每族只能配置一个 ID。如果需要同一族中多个版本映射到不同提供商 ID，使用 `modelOverrides` 设置。**

`modelOverrides` 将各 Anthropic 模型 ID 映射到 Claude Code 发送给提供商 API 的字符串。用户在选择器中选择映射的模型时，Claude Code 使用你配置的值。

适用于企业管理员将各模型版本路由到特定 Bedrock inference profile ARN、Vertex 版本名或 Foundry deployment name，用于治理、成本分配或区域路由。

在[设置文件](https://code.claude.com/docs/en/settings#settings-files)中配置：

```json theme={null}
{
  "modelOverrides": {
    "claude-opus-4-7": "arn:aws:bedrock:us-east-2:123456789012:application-inference-profile/opus-prod",
    "claude-opus-4-6": "arn:aws:bedrock:us-east-2:123456789012:application-inference-profile/opus-46-prod",
    "claude-sonnet-4-6": "arn:aws:bedrock:us-east-2:123456789012:application-inference-profile/sonnet-prod"
  }
}
```

Key 必须是 [Models overview](https://platform.claude.com/docs/en/about-claude/models/overview) 中列出的 Anthropic 模型 ID。带日期的 ID 需完整包含日期后缀。未知 key 被忽略。

Override 替换选择器中各条目背后的内置模型 ID。在 Bedrock 上，override 优先于启动时自动发现的 inference profiles。通过 `ANTHROPIC_MODEL`、`--model` 或 `ANTHROPIC_DEFAULT_*_MODEL` 直接提供的值按原样传递给提供商，不经 `modelOverrides` 转换。

`modelOverrides` 与 `availableModels` 协同工作。白名单基于 Anthropic 模型 ID 评估而非 override 值，因此 `availableModels` 中的 `"opus"` 在版本被映射到 ARN 时仍然匹配。`enforceAvailableModels` 在托管设置中时，enforced Default 仅通过最高优先级托管源的 `modelOverrides` 解析。

### Prompt 缓存配置

**Claude Code 自动使用 [prompt caching](https://code.claude.com/docs/en/prompt-caching) 优化性能和降低成本。** 可全局或按模型层级禁用：

| 环境变量 | 说明 |
| --- | --- |
| `DISABLE_PROMPT_CACHING` | 设为 `1` 全局禁用，优先于按模型设置 |
| `DISABLE_PROMPT_CACHING_HAIKU` | 设为 `1` 仅禁用 Haiku 的缓存 |
| `DISABLE_PROMPT_CACHING_SONNET` | 设为 `1` 仅禁用 Sonnet 的缓存 |
| `DISABLE_PROMPT_CACHING_OPUS` | 设为 `1` 仅禁用 Opus 的缓存 |
| `DISABLE_PROMPT_CACHING_FABLE` | 设为 `1` 仅禁用 Fable 的缓存 |

更改缓存 TTL 或了解 cache miss 触发条件，参见 [How Claude Code uses prompt caching](https://code.claude.com/docs/en/prompt-caching)。
