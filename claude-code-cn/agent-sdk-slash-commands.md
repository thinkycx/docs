---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Agent SDK - 斜杠命令
description: 在 SDK 中使用斜杠命令控制 Claude Code 会话。涵盖内置命令（/compact、/clear）的使用、自定义命令的创建（参数占位、Bash 执行、文件引用），以及命名空间组织。
category: translation
tags: [claude-code, agent-sdk, slash-commands, translation]
refs:
  - https://code.claude.com/docs/en/agent-sdk/slash-commands
  - en-source/agent-sdk/slash-commands.md
---

# SDK 中的斜杠命令

> 通过 SDK 使用斜杠命令控制 Claude Code 会话

**斜杠命令以 `/` 开头，是控制 Claude Code 会话的特殊指令。** 可通过 SDK 发送这些命令执行操作，如压缩上下文、列出上下文使用量或调用自定义命令。只有不需要交互终端的命令才能通过 SDK 分发；`system/init` 消息列出了当前会话中可用的命令。

## 发现可用斜杠命令

**Agent SDK 在系统初始化消息中提供可用斜杠命令的信息。** 会话启动时可访问：

TypeScript：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Hello Claude",
  options: { maxTurns: 1 }
})) {
  if (message.type === "system" && message.subtype === "init") {
    console.log("Available slash commands:", message.slash_commands);
    // 包括内置命令加捆绑的 Skills，例如：
    // ["clear", "compact", "context", "usage", "code-review", "verify", ...]
  }
}
```

Python：

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, SystemMessage


async def main():
    async for message in query(prompt="Hello Claude", options=ClaudeAgentOptions(max_turns=1)):
        if isinstance(message, SystemMessage) and message.subtype == "init":
            print("Available slash commands:", message.data["slash_commands"])
            # 包括内置命令加捆绑的 Skills，例如：
            # ["clear", "compact", "context", "usage", "code-review", "verify", ...]


asyncio.run(main())
```

## 发送斜杠命令

**像普通文本一样在 prompt 字符串中包含斜杠命令即可发送。** 操作对话历史的命令（如 `/compact`）需要有先前消息才能工作，因此下面的示例先提问，然后将命令作为同一对话的后续发送：

TypeScript：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

// 先建立对话历史
try {
  for await (const message of query({
    prompt: "What does the README in this directory cover?",
    options: { maxTurns: 2 }
  })) {
    if (message.type === "result" && message.subtype === "success") {
      console.log(message.result);
    }
  }
} catch (error) {
  // 单次 query() 在产出错误结果后会抛出异常，
  // 因此下面的后续查询仍会运行。
  console.error(`Session ended with an error: ${error}`);
}

// 在同一对话中发送斜杠命令作为后续
for await (const message of query({
  prompt: "/compact",
  options: { continue: true, maxTurns: 1 }
})) {
  if (message.type === "result") {
    console.log("Command executed, result subtype:", message.subtype);
    // 输出示例: Command executed, result subtype: success
  }
}
```

Python：

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


async def main():
    # 先建立对话历史
    try:
        async for message in query(
            prompt="What does the README in this directory cover?",
            options=ClaudeAgentOptions(max_turns=2),
        ):
            if isinstance(message, ResultMessage) and message.subtype == "success":
                print(message.result)
    except Exception as error:
        # 单次 query() 在产出错误结果后会抛出异常，
        # 因此下面的后续查询仍会运行。
        print(f"Session ended with an error: {error}")

    # 在同一对话中发送斜杠命令作为后续
    async for message in query(
        prompt="/compact",
        options=ClaudeAgentOptions(continue_conversation=True, max_turns=1),
    ):
        if isinstance(message, ResultMessage):
            print("Command executed, result subtype:", message.subtype)
            # 输出示例: Command executed, result subtype: success


asyncio.run(main())
```

> **注意：** 查询可能以错误结果结束，例如在工作完成前达到 `maxTurns`/`max_turns` 限制。最终结果消息的 `is_error` 为 `true`，subtype 为 `error_max_turns` 而非 `success`。
>
> 产出该最终结果消息后，SDK 会抛出错误（因为 CLI 进程以非零代码退出）。
>
> 如果命令可能达到限制，在 TypeScript 中用 `try`/`catch`、Python 中用 `try`/`except` 包裹循环（如[单消息输入](https://code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode#single-message-input)所示），或将 `maxTurns` 设置得足够高。在 Python 中捕获 `Exception`：SDK 将错误结果表示为普通 `Exception`。

## 常用斜杠命令

### `/compact` - 压缩对话历史

**`/compact` 命令通过总结旧消息来减小对话历史大小，同时保留重要上下文。** 压缩需要有至少两轮先前交换的现有对话。以下示例先进行对话，然后压缩它并读取报告结果的 `compact_boundary` 系统消息：

TypeScript：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

// 压缩需要现有历史，先进行一次对话
try {
  for await (const message of query({
    prompt: "Explain what this project does",
    options: { maxTurns: 2 }
  })) {
    if (message.type === "result" && message.subtype === "success") {
      console.log(message.result);
    }
  }
} catch (error) {
  console.error(`Session ended with an error: ${error}`);
}

// 压缩同一对话
for await (const message of query({
  prompt: "/compact",
  options: { continue: true, maxTurns: 1 }
})) {
  if (message.type === "system" && message.subtype === "compact_boundary") {
    console.log("Compaction completed");
    console.log("Pre-compaction tokens:", message.compact_metadata.pre_tokens);
    console.log("Trigger:", message.compact_metadata.trigger);
    // 输出示例:
    // Compaction completed
    // Pre-compaction tokens: 1842
    // Trigger: manual
  }
}
```

Python：

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage, SystemMessage


async def main():
    # 压缩需要现有历史，先进行一次对话
    try:
        async for message in query(
            prompt="Explain what this project does",
            options=ClaudeAgentOptions(max_turns=2),
        ):
            if isinstance(message, ResultMessage) and message.subtype == "success":
                print(message.result)
    except Exception as error:
        print(f"Session ended with an error: {error}")

    # 压缩同一对话
    async for message in query(
        prompt="/compact",
        options=ClaudeAgentOptions(continue_conversation=True, max_turns=1),
    ):
        if isinstance(message, SystemMessage) and message.subtype == "compact_boundary":
            print("Compaction completed")
            print("Pre-compaction tokens:", message.data["compact_metadata"]["pre_tokens"])
            print("Trigger:", message.data["compact_metadata"]["trigger"])
            # 输出示例:
            # Compaction completed
            # Pre-compaction tokens: 1842
            # Trigger: manual


asyncio.run(main())
```

> **注意：** `compact_boundary` 消息仅在压缩实际执行时才会到达。如果没有内容可总结，`/compact` 会报告原因而非抛出异常：运行仍以 `success` 结果结束，不会发出 `compact_boundary` 消息，结果文本中包含消息（例如 `Not enough messages to compact.`）。全新的一次性 `query()` 调用从空上下文开始，所以请在有先前轮次的会话中使用此模式（例如[流式输入模式](https://code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode)或恢复会话时）。

### `/clear` - 重置对话上下文

**`/clear` 命令将对话重置为空上下文，后续 prompt 从无先前对话历史的状态开始。** 之前的对话保留在磁盘上，可通过将其 session ID 传给 [`resume` 选项](https://code.claude.com/docs/en/agent-sdk/sessions#resume-by-id)来恢复。

适用于[流式输入模式](https://code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode)——在单个连接上发送多个 prompt 的场景。对于一次性 `query()` 调用，每次调用本身就从空上下文开始，所以发送 `/clear` 没有实际效果；直接开始新的 `query()` 即可。

> **注意：** SDK 中的 `/clear` 需要 Claude Code v2.1.117 或更高版本。更早版本中它不会出现在 `slash_commands` 中。

## 创建自定义斜杠命令

**除了使用内置斜杠命令，还可以创建自己的自定义命令。** 自定义命令定义为 markdown 文件，放在特定目录中，类似子代理的配置方式。

> **注意：** `.claude/commands/` 目录是旧格式。推荐格式是 `.claude/skills/<name>/SKILL.md`，它既支持相同的斜杠命令调用（`/name`），又支持 Claude 自主调用。参见 [Skills](https://code.claude.com/docs/en/agent-sdk/skills) 了解当前格式。CLI 继续支持两种格式。

### 文件位置

**自定义斜杠命令存储在指定目录中，根据作用域划分：**

| 作用域 | 路径 | 说明 |
|:---|:---|:---|
| 项目命令 | `.claude/commands/` | 仅在当前项目可用（旧版；推荐用 `.claude/skills/`） |
| 个人命令 | `~/.claude/commands/` | 跨所有项目可用（旧版；推荐用 `~/.claude/skills/`） |

### 文件格式

**每个自定义命令是一个 markdown 文件：**

* 文件名（去掉 `.md` 扩展名）成为命令名
* 文件内容定义命令功能
* 可选的 YAML frontmatter 提供配置

#### 基本示例

在项目中创建 `.claude/commands` 目录（如果不存在），然后创建 `.claude/commands/refactor.md`：

```markdown
Refactor the selected code to improve readability and maintainability.
Focus on clean code principles and best practices.
```

这会创建 `/refactor` 命令，可通过 SDK 使用。

#### 带 Frontmatter

创建 `.claude/commands/security-check.md`：

```markdown
---
allowed-tools: Read, Grep, Glob
description: Run security vulnerability scan
model: claude-opus-4-8
---

Analyze the codebase for security vulnerabilities including:
- SQL injection risks
- XSS vulnerabilities
- Exposed credentials
- Insecure configurations
```

### 在 SDK 中使用自定义命令

**定义在文件系统后，自定义命令自动通过 SDK 可用：**

TypeScript：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

// 使用自定义命令
try {
  for await (const message of query({
    prompt: "/refactor src/auth/login.ts",
    options: { maxTurns: 3 }
  })) {
    if (message.type === "assistant") {
      console.log("Refactoring suggestions:", message.message);
    }
  }
} catch (error) {
  console.error(`Session ended with an error: ${error}`);
}

// 自定义命令出现在 slash_commands 列表中
for await (const message of query({
  prompt: "Hello",
  options: { maxTurns: 1 }
})) {
  if (message.type === "system" && message.subtype === "init") {
    console.log("Available commands:", message.slash_commands);
    // 包含内置命令、捆绑 Skills 和你的自定义命令，例如：
    // ["clear", "compact", "context", "usage", "code-review", "verify", "refactor", "security-check", ...]
  }
}
```

Python：

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, SystemMessage


async def main():
    # 使用自定义命令
    try:
        async for message in query(
            prompt="/refactor src/auth/login.py", options=ClaudeAgentOptions(max_turns=3)
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if hasattr(block, "text"):
                        print("Refactoring suggestions:", block.text)
    except Exception as error:
        print(f"Session ended with an error: {error}")

    # 自定义命令出现在 slash_commands 列表中
    async for message in query(prompt="Hello", options=ClaudeAgentOptions(max_turns=1)):
        if isinstance(message, SystemMessage) and message.subtype == "init":
            print("Available commands:", message.data["slash_commands"])
            # 包含内置命令、捆绑 Skills 和你的自定义命令，例如：
            # ["clear", "compact", "context", "usage", "code-review", "verify", "refactor", "security-check", ...]


asyncio.run(main())
```

### 高级功能

#### 参数和占位符

**自定义命令支持使用占位符实现动态参数：**

创建 `.claude/commands/fix-issue.md`：

```markdown
---
argument-hint: [issue-number] [priority]
description: Fix a GitHub issue
---

Fix issue #$0 with priority $1.
Check the issue description and implement the necessary changes.
```

在 SDK 中使用：

TypeScript：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

// 向自定义命令传递参数
for await (const message of query({
  prompt: "/fix-issue 123 high",
  options: { maxTurns: 5 }
})) {
  // 命令将以 $0="123" 和 $1="high" 处理
  if (message.type === "result" && message.subtype === "success") {
    console.log("Issue fixed:", message.result);
  }
}
```

Python：

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


async def main():
    # 向自定义命令传递参数
    async for message in query(prompt="/fix-issue 123 high", options=ClaudeAgentOptions(max_turns=5)):
        # 命令将以 $0="123" 和 $1="high" 处理
        if isinstance(message, ResultMessage):
            print("Issue fixed:", message.result)


asyncio.run(main())
```

#### Bash 命令执行

**自定义命令可以执行 bash 命令并包含其输出：**

创建 `.claude/commands/git-commit.md`：

```markdown
---
allowed-tools: Bash(git add *), Bash(git status *), Bash(git commit *)
description: Create a git commit
---

## Context

- Current status: !`git status`
- Current diff: !`git diff HEAD`

## Task

Create a git commit with appropriate message based on the changes.
```

#### 文件引用

**使用 `@` 前缀包含文件内容：**

创建 `.claude/commands/review-config.md`：

```markdown
---
description: Review configuration files
---

Review the following configuration files for issues:
- Package config: @package.json
- TypeScript config: @tsconfig.json
- Environment config: @.env

Check for security issues, outdated dependencies, and misconfigurations.
```

### 命名空间组织

**使用子目录组织命令以获得更好的结构：**

```bash
.claude/commands/
├── frontend/
│   ├── component.md      # 创建 /component (project:frontend)
│   └── style-check.md     # 创建 /style-check (project:frontend)
├── backend/
│   ├── api-test.md        # 创建 /api-test (project:backend)
│   └── db-migrate.md      # 创建 /db-migrate (project:backend)
└── review.md              # 创建 /review (project)
```

子目录出现在命令描述中，但不影响命令名称本身。

### 实用示例

#### Pull Request 审查命令

创建 `.claude/commands/review-pr.md`：

```markdown
---
allowed-tools: Read, Grep, Glob, Bash(git diff *)
description: Comprehensive code review
---

## Changed Files
!`git diff --name-only HEAD~1`

## Detailed Changes
!`git diff HEAD~1`

## Review Checklist

Review the above changes for:
1. Code quality and readability
2. Security vulnerabilities
3. Performance implications
4. Test coverage
5. Documentation completeness

Provide specific, actionable feedback organized by priority.
```

> **注意：** Claude Code 包含内置的 `code-review` 和 `verify` Skills。如果你以相同名称创建自定义命令（例如 `.claude/commands/code-review.md`），你的命令会覆盖内置 Skill，`slash_commands` 中只列出一次。

#### 测试运行命令

创建 `.claude/commands/test.md`：

```markdown
---
allowed-tools: Bash, Read, Edit
argument-hint: [test-pattern]
description: Run tests with optional pattern
---

Run tests matching pattern: $ARGUMENTS

1. Detect the test framework (Jest, pytest, etc.)
2. Run tests with the provided pattern
3. If tests fail, analyze and fix them
4. Re-run to verify fixes
```

通过 SDK 使用这些命令：

TypeScript：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

// 运行代码审查
try {
  for await (const message of query({
    prompt: "/review-pr",
    options: { maxTurns: 3 }
  })) {
    // 处理审查反馈
  }
} catch (error) {
  console.error(`Session ended with an error: ${error}`);
}

// 运行特定测试
for await (const message of query({
  prompt: "/test auth",
  options: { maxTurns: 5 }
})) {
  // 处理测试结果
}
```

Python：

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    # 运行代码审查
    try:
        async for message in query(prompt="/review-pr", options=ClaudeAgentOptions(max_turns=3)):
            # 处理审查反馈
            pass
    except Exception as error:
        print(f"Session ended with an error: {error}")

    # 运行特定测试
    async for message in query(prompt="/test auth", options=ClaudeAgentOptions(max_turns=5)):
        # 处理测试结果
        pass


asyncio.run(main())
```

## 相关文档

* [斜杠命令](https://code.claude.com/docs/en/skills) - 完整斜杠命令文档
* [SDK 中的子代理](https://code.claude.com/docs/en/agent-sdk/subagents) - 类似的基于文件系统的子代理配置
* [TypeScript SDK 参考](https://code.claude.com/docs/en/agent-sdk/typescript) - 完整 API 文档
* [SDK 概览](https://code.claude.com/docs/en/agent-sdk/overview) - 通用 SDK 概念
* [CLI 参考](https://code.claude.com/docs/en/cli-reference) - 命令行接口
