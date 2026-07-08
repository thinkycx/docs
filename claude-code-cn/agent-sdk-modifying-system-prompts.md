---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Agent SDK - 系统提示词
description: Claude Agent SDK 系统提示词定制指南，涵盖 claude_code 预设与自定义提示词的选择决策、CLAUDE.md 项目级指令、输出风格、append 追加模式、跨用户缓存优化及四种方案对比。
category: translation
tags: [claude-code, agent-sdk, translation]
refs:
  - https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts
  - en-source/agent-sdk/modifying-system-prompts.md
---

# 修改系统提示词

> 在 `claude_code` 预设和自定义系统提示词之间选择，并通过 CLAUDE.md、输出风格、append 或完全自定义提示词来定制行为。

**系统提示词定义 Claude 的行为、能力和响应风格。** 如果是 CLI 或 IDE 类编码工具（有人观看并引导工作），从 `claude_code` 预设开始。如果 agent 有不同的界面、身份或权限模型，则编写自己的提示词。

本页涵盖：

* [系统提示词工作原理](#系统提示词工作原理)——选择预设、预设加 `append`、或自定义提示词的决策表
* [定制 agent 行为](#定制-agent-行为)——通过 CLAUDE.md 文件、输出风格、`append` 或自定义字符串
* [四种方案对比](#四种方案对比)——按持久性、作用域和保留内容对比
* [组合使用](#组合使用)——多种定制方法叠加

## 系统提示词工作原理

**系统提示词是塑造 Claude 在整个对话中行为的初始指令集。** Agent SDK 有三个起点：

| 起点 | 说明 |
|:---|:---|
| **极简默认** | 不设置 `systemPrompt`（TS）/ `system_prompt`（Python）时，SDK 使用只覆盖工具调用的极简提示词，省略 Claude Code 的编码指南、响应风格和项目上下文。这与 `claude -p` 不同——后者默认使用完整的 Claude Code 提示词。如果从 CLI 迁移且想保持一致行为，设置 `claude_code` 预设。 |
| **`claude_code` 预设** | Claude Code CLI 使用的完整系统提示词，包含工具使用指导、代码风格和格式指南、响应语气和详细程度规则、安全与安全性指令、以及工作目录和环境的上下文。设置 `systemPrompt: { type: "preset", preset: "claude_code" }`（TS）或 `system_prompt={"type": "preset", "preset": "claude_code"}`（Python），可选加 `append` 在末尾追加自己的指令。 |
| **自定义字符串** | 你自己编写的提示词。SDK 只发送你提供的内容。 |

### 选择起点

**决定因素是你的 agent 与 Claude Code 的相似程度**——即一个在仓库中操作的编码 agent，有人观看流式输出并引导工作。你的产品离这个定位越远，越需要自己编写提示词。

| 你正在构建 | 使用 | 获得 |
|:---|:---|:---|
| CLI 或 IDE 类编码工具，有人观看并引导，Claude Code 默认行为即你所需 | `claude_code` 预设 | 完整 Claude Code 提示词：工具指导、安全规则、终端友好响应、仓库规范感知 |
| 同上，加上产品特定规则如编码标准、输出格式或领域上下文 | `claude_code` 预设 + `append` | 上述全部，加上你的指令追加在预设之后。不删除任何内容，是最低风险的定制 |
| 界面、身份或权限模型不同于 Claude Code 的 agent，或非编码 agent | 自定义提示词字符串 | 只有你写的内容。你需要自行负责替换 agent 仍然需要的工具指导和安全指令 |
| 无 agent 人格的薄工具调用循环，所有行为通过 user prompt 提供 | 不设置 `systemPrompt` | 极简默认：仅工具调用支持 |

"不同于 Claude Code" 通常意味着以下之一：

* **不同界面**：输出不是由触发者在终端中阅读。聊天 UI、结构化输出消费者和非编码自动化各自需要匹配其输出渲染和审阅方式的提示词。无人值守的编码自动化（如修复 lint 错误或审查 diff 的 CI 任务）仍适合预设，因为工作本身就是预设针对的场景。
* **不同身份**：agent 不应以 Claude Code 自居。支持机器人、数据分析助手或任何领域特定 agent 需要自己的名称、范围和人格。
* **不同权限模型**：agent 无人值守自主运行，或只操作有限资源集。Claude Code 的提示词假设有人在环路中且有完整工具集的访问权。
* **非编码任务**：Claude Code 提示词的大部分是编码指导。对于研究、内容或运维 agent，这些指导会与你实际需要的指令竞争。

[四种方案对比](#四种方案对比)表展示每种定制方法保留了什么。

## 定制 agent 行为

**输出风格、`append` 和自定义提示词字符串直接修改系统提示词。** CLAUDE.md 走不同的路径：SDK 读取它并将内容作为项目上下文注入对话，而不是注入系统提示词，所以它在你选择的任何系统提示词旁塑造行为。[Skills](https://code.claude.com/docs/en/agent-sdk/skills)、[hooks](https://code.claude.com/docs/en/agent-sdk/hooks) 和 [permissions](https://code.claude.com/docs/en/agent-sdk/permissions) 也在系统提示词之外塑造行为，各自有专属页面。

### CLAUDE.md 文件：项目级指令

**CLAUDE.md 文件为 Claude 提供持久的项目上下文和指令。** SDK 将其内容注入对话而非系统提示词，因此它可以与任何系统提示词配置配合使用。关于在 CLAUDE.md 中放什么内容、放在哪里、如何编写有效指令，参见 [How Claude remembers your project](https://code.claude.com/docs/en/memory)。本节涵盖 SDK 特有的内容：CLAUDE.md 如何加载。

SDK 在对应的设置源启用时读取 CLAUDE.md：`'project'` 加载工作目录中的 `CLAUDE.md` 或 `.claude/CLAUDE.md`，`'user'` 加载 `~/.claude/CLAUDE.md`。默认 `query()` 选项启用两个源，所以 CLAUDE.md 自动加载。如果显式设置 `settingSources`（TS）或 `setting_sources`（Python），需包含你需要的源。CLAUDE.md 加载由设置源控制，而非 `claude_code` 预设。

#### 用 SDK 加载 CLAUDE.md

设置 `settingSources` 包含 CLAUDE.md 所在的级别。以下示例加载项目级 CLAUDE.md 并配合 `claude_code` 预设，让 Claude 同时拥有完整的编码 agent 提示词和项目规范：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

const messages = [];

for await (const message of query({
  prompt: "Add a new React component for user profiles",
  options: {
    systemPrompt: {
      type: "preset",
      preset: "claude_code" // 使用 Claude Code 的系统提示词
    },
    settingSources: ["project"] // 从项目加载 CLAUDE.md
  }
})) {
  messages.push(message);
}

// Claude 现在可以访问 CLAUDE.md 中的项目指南
```

```python
from claude_agent_sdk import query, ClaudeAgentOptions

messages = []

async for message in query(
    prompt="Add a new React component for user profiles",
    options=ClaudeAgentOptions(
        system_prompt={
            "type": "preset",
            "preset": "claude_code",  # 使用 Claude Code 的系统提示词
        },
        setting_sources=["project"],  # 从项目加载 CLAUDE.md
    ),
):
    messages.append(message)

# Claude 现在可以访问 CLAUDE.md 中的项目指南
```

CLAUDE.md 跨项目中所有会话持久存在，通过 git 与团队共享，无需代码修改即可自动发现。传入空 `settingSources` 数组时不加载。

### 输出风格：持久配置

**输出风格是保存的配置，用于修改 Claude 的系统提示词。** 它们存储为 markdown 文件，可跨会话和项目复用。

#### 创建输出风格

输出风格是带 [frontmatter](https://code.claude.com/docs/en/output-styles#frontmatter) 元数据的 markdown 文件，后跟提示词内容。保存到 `~/.claude/output-styles/` 作为用户级风格（每个项目可用），或保存到仓库中的 `.claude/output-styles/` 作为项目级风格（可提交并与团队共享）。

默认情况下，自定义输出风格会用你的内容**替换** `claude_code` 预设的软件工程指令。要保留它们并在上面叠加你的指令，在 frontmatter 中设置 `keep-coding-instructions: true`。当 agent 仍在做软件工程工作时保留它们。当你完全替换角色时省略它们。

以下示例定义一个代码审查人格，保留编码指令——因为审查代码仍然受益于 Claude Code 的安全和代码质量指导。保存为 `~/.claude/output-styles/code-reviewer.md` 使其跨项目可用：

```markdown
---
name: Code Reviewer
description: Thorough code review assistant
keep-coding-instructions: true
---

You are an expert code reviewer.

For every code submission:
1. Check for bugs and security issues
2. Evaluate performance
3. Suggest improvements
4. Rate code quality (1-10)
```

#### 激活输出风格

创建后，通过以下方式激活输出风格：

* **CLI**：运行 `/config` 并选择输出风格
* **设置**：在 `.claude/settings.local.json` 中设置 `outputStyle`
* **TypeScript SDK**：在传给 `query()` 的内联 `settings` 对象中设置 `outputStyle`，或将 `settings` 指向设置了它的设置文件。`outputStyle` 不是顶层 `Options` 字段：

  ```typescript
  const options = { settings: { outputStyle: "Explanatory" } };
  ```

Python SDK 没有以编程方式选择输出风格的选项。对于无法写入 `.claude/settings.local.json` 的纯代码部署，改用 `append` 或自定义提示词字符串。

**SDK 用户注意：** 当选项中包含 `settingSources: ['user']` 或 `settingSources: ['project']`（TS）/ `setting_sources=["user"]` 或 `setting_sources=["project"]`（Python）时加载输出风格。

### 追加到 `claude_code` 预设

**你可以在 Claude Code 预设上使用 `append` 属性添加自定义指令，同时保留所有内置功能。**

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

const messages = [];

for await (const message of query({
  prompt: "Help me write a Python function to calculate fibonacci numbers",
  options: {
    systemPrompt: {
      type: "preset",
      preset: "claude_code",
      append: "Always include detailed docstrings and type hints in Python code."
    }
  }
})) {
  messages.push(message);
  if (message.type === "assistant") {
    console.log(message.message.content);
  }
}
```

```python
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage

messages = []

async for message in query(
    prompt="Help me write a Python function to calculate fibonacci numbers",
    options=ClaudeAgentOptions(
        system_prompt={
            "type": "preset",
            "preset": "claude_code",
            "append": "Always include detailed docstrings and type hints in Python code.",
        }
    ),
):
    messages.append(message)
    if isinstance(message, AssistantMessage):
        print(message.content)
```

#### 跨用户和机器优化 prompt 缓存

**默认情况下，使用相同 `claude_code` 预设和 `append` 文本的两个会话，如果从不同工作目录运行，仍无法共享 prompt 缓存条目。** 这是因为预设在系统提示词中嵌入了每会话上下文（在 `append` 文本之前）：工作目录、是否是 git 仓库、平台、活跃的 shell、OS 版本和自动记忆路径。这些上下文的任何差异都会产生不同的系统提示词和缓存未命中。CLAUDE.md 内容不影响系统提示词缓存，因为 SDK 将其注入对话而非系统提示词。

要使系统提示词跨会话相同，设置 `excludeDynamicSections: true`（TS）或 `"exclude_dynamic_sections": True`（Python）。每会话上下文移入第一条用户消息，只留静态预设和 `append` 文本在系统提示词中，这样相同配置可跨用户和机器共享缓存条目。

> **注意：** `excludeDynamicSections` 需要 `@anthropic-ai/claude-agent-sdk` v0.2.98 或更高版本，Python 需要 `claude-agent-sdk` v0.1.58 或更高版本。仅适用于预设对象形式，当 `systemPrompt` 是字符串时无效。

以下示例将共享的 `append` 块与 `excludeDynamicSections` 配对，让一组从不同目录运行的 agent 可以复用同一个缓存的系统提示词：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Triage the open issues in this repo",
  options: {
    systemPrompt: {
      type: "preset",
      preset: "claude_code",
      append: "You operate Acme's internal triage workflow. Label issues by component and severity.",
      excludeDynamicSections: true
    }
  }
})) {
  // ...
}
```

```python
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt="Triage the open issues in this repo",
    options=ClaudeAgentOptions(
        system_prompt={
            "type": "preset",
            "preset": "claude_code",
            "append": "You operate Acme's internal triage workflow. Label issues by component and severity.",
            "exclude_dynamic_sections": True,
        },
    ),
):
    ...
```

**权衡：** 工作目录、git 仓库标志、平台、活跃 shell、OS 版本和自动记忆路径仍然到达 Claude，但作为第一条用户消息的一部分而非系统提示词。用户消息中的指令比系统提示词中的同等文本权重略低，所以 Claude 在推理当前目录或自动记忆路径时可能对它们的依赖稍弱。当跨会话缓存复用比最大化权威的环境上下文更重要时启用此选项。

非交互式 CLI 模式中的等价标志，参见 [`--exclude-dynamic-system-prompt-sections`](https://code.claude.com/docs/en/cli-reference)。

### 自定义系统提示词

**你可以提供自定义字符串作为 `systemPrompt` 来完全替换默认提示词。**

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

const customPrompt = `You are a Python coding specialist.
Follow these guidelines:
- Write clean, well-documented code
- Use type hints for all functions
- Include comprehensive docstrings
- Prefer functional programming patterns when appropriate
- Always explain your code choices`;

const messages = [];

for await (const message of query({
  prompt: "Create a data processing pipeline",
  options: {
    systemPrompt: customPrompt
  }
})) {
  messages.push(message);
  if (message.type === "assistant") {
    console.log(message.message.content);
  }
}
```

```python
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage

custom_prompt = """You are a Python coding specialist.
Follow these guidelines:
- Write clean, well-documented code
- Use type hints for all functions
- Include comprehensive docstrings
- Prefer functional programming patterns when appropriate
- Always explain your code choices"""

messages = []

async for message in query(
    prompt="Create a data processing pipeline",
    options=ClaudeAgentOptions(system_prompt=custom_prompt),
):
    messages.append(message)
    if isinstance(message, AssistantMessage):
        print(message.content)
```

## 四种方案对比

**四种定制方法在存放位置、共享方式和从 `claude_code` 预设保留的内容方面各不相同。**

| 特性 | CLAUDE.md | 输出风格 | `systemPrompt` + append | 自定义 `systemPrompt` |
|:---|:---|:---|:---|:---|
| **持久性** | 项目文件 | 保存为文件 | 仅会话 | 仅会话 |
| **可复用性** | 项目级 | 跨项目 | 代码复制 | 代码复制 |
| **管理方式** | 文件系统 | CLI + 文件 | 代码中 | 代码中 |
| **默认工具** | 保留 | 保留 | 保留 | 丢失（除非自行包含） |
| **内置安全** | 保持 | 保持 | 保持 | 需自行添加 |
| **环境上下文** | 自动 | 自动 | 自动 | 需自行提供 |
| **定制程度** | 仅添加 | 替换或扩展默认 | 仅添加 | 完全控制 |
| **版本控制** | 随项目 | 是 | 随代码 | 随代码 |
| **作用域** | 项目特定 | 用户或项目 | 代码会话 | 代码会话 |

"+ append" 指使用 `systemPrompt: { type: "preset", preset: "claude_code", append: "..." }`（TS）或 `system_prompt={"type": "preset", "preset": "claude_code", "append": "..."}`（Python）。CLAUDE.md 不改变系统提示词本身：SDK 将其内容作为项目上下文注入对话。

## 使用场景与最佳实践

### 何时使用 CLAUDE.md

**用于应该应用到项目中每个会话的指令**——无论会话使用哪种系统提示词：编码标准、常用命令、架构上下文和团队规范。CLAUDE.md 提交到仓库，与它描述的代码保持同步。详细指导参见 [When to add to CLAUDE.md](https://code.claude.com/docs/en/memory#when-to-add-to-claude-md)。

当 `project` 设置源启用时加载 CLAUDE.md 文件——默认 `query()` 选项默认启用。如果显式设置 `settingSources`（TS）或 `setting_sources`（Python），包含 `'project'` 以继续加载项目级 CLAUDE.md。

### 何时使用输出风格

**输出风格适合想在 CLI 和 SDK 之间复用而无需修改应用代码的人格。** 因为它们作为文件存在于 `.claude/output-styles`，同一人格可从 CLI 的 `/config` 和任何加载匹配设置源的 SDK 会话中使用。

**最适合：**

* 跨会话的持久行为变更
* 团队共享配置
* 专业助手如代码审查员、数据科学家或 DevOps 助手
* 需要版本控制的复杂提示词修改

**示例：**

* 创建专门的 SQL 优化助手
* 构建专注安全的代码审查员
* 开发带特定教学法的教学助手

### 何时使用 `systemPrompt` + append

**当 `claude_code` 预设已经适合你的产品、只需要叠加额外指令时使用 `append`。** 你保留预设的工具指导、安全规则和编码规范而无需重新实现。

**最适合：**

* 添加特定编码标准或偏好
* 自定义输出格式
* 添加领域特定知识
* 修改响应详细程度
* 增强 Claude Code 默认行为而不丢失工具指令

### 何时使用自定义 `systemPrompt`

**当 agent 的界面、身份或权限模型不同于 Claude Code 时使用自定义提示词**（如[选择起点](#选择起点)中所述）。你定义完整的指令集，包括 agent 需要的任何工具指导和安全规则。

**最适合：**

* 完全控制 Claude 的行为
* 专门的单会话任务
* 测试新的提示词策略
* 不需要默认工具的场景
* 构建具有独特行为的专业 agent

## 组合使用

**这些方法可以组合。** 持久的输出风格或 CLAUDE.md 设置长期行为，`append` 在上面叠加会话特定指令而不触及保存的配置。

### 组合输出风格与会话特定补充

以下示例假设 Code Reviewer 输出风格已激活。`append` 块在人格之上叠加会话特定的关注领域，让一次审查会话可以优先关注 OAuth 和 token 存储而无需修改保存的输出风格：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

// 假设 "Code Reviewer" 输出风格已激活（通过 /config 或设置）
// 添加会话特定的关注领域
const messages = [];

for await (const message of query({
  prompt: "Review this authentication module",
  options: {
    systemPrompt: {
      type: "preset",
      preset: "claude_code",
      append: `
        For this review, prioritize:
        - OAuth 2.0 compliance
        - Token storage security
        - Session management
      `
    }
  }
})) {
  messages.push(message);
}
```

```python
from claude_agent_sdk import query, ClaudeAgentOptions

# 假设 "Code Reviewer" 输出风格已激活（通过 /config 或设置）
# 添加会话特定的关注领域
messages = []

async for message in query(
    prompt="Review this authentication module",
    options=ClaudeAgentOptions(
        system_prompt={
            "type": "preset",
            "preset": "claude_code",
            "append": """
            For this review, prioritize:
            - OAuth 2.0 compliance
            - Token storage security
            - Session management
            """,
        }
    ),
):
    messages.append(message)
```

## 另见

* [输出风格](https://code.claude.com/docs/en/output-styles)：为 CLI 创建、管理和共享输出风格，包括文件格式和存储位置
* [Claude 如何记住你的项目](https://code.claude.com/docs/en/memory)：CLAUDE.md 中放什么内容、放在哪里、如何编写有效的项目指令
* [TypeScript SDK 参考](https://code.claude.com/docs/en/agent-sdk/typescript)：完整 `Options` 类型，包括 `systemPrompt`、`settingSources` 和 `settings`
* [Python SDK 参考](https://code.claude.com/docs/en/agent-sdk/python)：完整 `ClaudeAgentOptions` 类型，包括 `system_prompt` 和 `setting_sources`
* [设置](https://code.claude.com/docs/en/settings)：`settings.json` 参考，包括输出风格和其他配置的存储位置
