---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
category: translation
tags: [claude-code, agent-sdk, translation]
description: Claude Agent SDK 的会话管理指南，介绍会话如何持久化对话历史，以及何时使用 continue、resume 和 fork 回到先前的运行。
refs:
  - https://code.claude.com/docs/en/agent-sdk/sessions
  - en-source/agent-sdk/sessions.md
title: 【译】Agent SDK - 会话管理
---

# 【译】SDK 会话管理

> 会话如何持久化 Agent 对话历史，以及何时使用 continue、resume 和 fork 回到先前的运行

**会话是 SDK 在 Agent 工作过程中累积的对话历史。** 它包含你的提示、Agent 进行的每次工具调用、每个工具结果和每个响应。SDK 自动将其写入磁盘，以便你稍后回到它。

回到一个会话意味着 Agent 拥有之前的完整上下文：它已经读过的文件、已经执行的分析、已经做出的决策。你可以提问后续问题、从中断中恢复，或分叉尝试不同的方案。

> 会话持久化的是**对话**，不是文件系统。要快照和回滚 Agent 所做的文件更改，使用[文件检查点](https://code.claude.com/docs/en/agent-sdk/file-checkpointing)。

本文涵盖如何为你的应用选择正确的方式、自动跟踪会话的 SDK 接口、如何捕获会话 ID 并手动使用 `resume` 和 `fork`，以及跨主机恢复会话的注意事项。

## 选择方式

**你需要多少会话处理取决于应用的形态。** 当你发送多个需要共享上下文的提示时，会话管理才会发挥作用。在单个 `query()` 调用内，Agent 已经根据需要执行多个轮次，权限提示和 `AskUserQuestion` 在[循环内处理](https://code.claude.com/docs/en/agent-sdk/user-input)（它们不会结束调用）。

| 你在构建什么 | 应该使用 |
| :--- | :--- |
| 一次性任务：单个提示，无后续 | 不需要额外操作。一次 `query()` 调用搞定。 |
| 单进程内的多轮对话 | [`ClaudeSDKClient`（Python）或 `continue: true`（TypeScript）](#自动会话管理)。SDK 自动跟踪会话，无需处理 ID。 |
| 进程重启后继续上次 | `continue_conversation=True`（Python）/ `continue: true`（TypeScript）。恢复目录中最近的会话，不需要 ID。 |
| 恢复特定的历史会话（非最近的） | 捕获会话 ID 并传给 `resume`。 |
| 尝试替代方案而不丢失原始内容 | Fork 会话。 |
| 无状态任务，不想写入磁盘（仅 TypeScript） | 设置 [`persistSession: false`](https://code.claude.com/docs/en/agent-sdk/typescript#options)。会话仅在调用期间存在于内存中。Python 始终持久化到磁盘。 |

### Continue、Resume 和 Fork

**Continue、resume 和 fork 是设置在 `query()` 上的选项字段**（Python 中为 [`ClaudeAgentOptions`](https://code.claude.com/docs/en/agent-sdk/python#claudeagentoptions)，TypeScript 中为 [`Options`](https://code.claude.com/docs/en/agent-sdk/typescript#options)）。

**Continue** 和 **resume** 都是接续一个已有会话并在其上追加。区别在于如何找到那个会话：

* **Continue** — 查找当前目录中最近的会话。你不需要跟踪任何东西。适合应用一次只运行一个对话的场景。
* **Resume** — 接受特定的会话 ID。你需要跟踪 ID。在有多个会话时需要（例如多用户应用中每个用户一个会话），或想返回非最近的会话时。

**Fork** 不同：它创建一个新会话，以原始会话历史的副本开始。原始会话保持不变。用 fork 尝试不同方向，同时保留回退选项。

## 自动会话管理

**两个 SDK 都提供跨调用自动跟踪会话状态的接口，无需手动传递 ID。** 用于单进程内的多轮对话。

### Python: `ClaudeSDKClient`

**[`ClaudeSDKClient`](https://code.claude.com/docs/en/agent-sdk/python#claudesdkclient) 在内部处理会话 ID。** 每次调用 `client.query()` 自动延续同一个会话。调用 [`client.receive_response()`](https://code.claude.com/docs/en/agent-sdk/python#claudesdkclient) 来迭代当前查询的消息。使用 client 作为异步上下文管理器以自动处理连接设置和清理，或手动调用 `connect()` 和 `disconnect()`。

此示例对同一个 `client` 运行两个查询。第一个让 Agent 分析一个模块；第二个让它重构该模块。因为两次调用都通过同一个 client 实例，第二个查询拥有第一个的完整上下文，无需显式 `resume` 或会话 ID：

```python
import asyncio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
)


def print_response(message):
    """只打印消息中人类可读的部分。"""
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(block.text)
    elif isinstance(message, ResultMessage):
        cost = (
            f"${message.total_cost_usd:.4f}"
            if message.total_cost_usd is not None
            else "N/A"
        )
        print(f"[done: {message.subtype}, cost: {cost}]")


async def main():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Edit", "Glob", "Grep"],
    )

    async with ClaudeSDKClient(options=options) as client:
        # 第一个查询：client 内部捕获会话 ID
        await client.query("Analyze the auth module")
        async for message in client.receive_response():
            print_response(message)

        # 第二个查询：自动延续同一个会话
        await client.query("Now refactor it to use JWT")
        async for message in client.receive_response():
            print_response(message)


asyncio.run(main())
```

何时使用 `ClaudeSDKClient` vs 独立 `query()` 函数的详情见 [Python SDK 参考](https://code.claude.com/docs/en/agent-sdk/python#choosing-between-query-and-claudesdkclient)。

### TypeScript: `continue: true`

**TypeScript SDK 没有像 Python 的 `ClaudeSDKClient` 那样的会话保持对象。** 相反，在每次后续 `query()` 调用时传入 `continue: true`，SDK 会拾取当前目录中最近的会话。不需要跟踪 ID。

此示例进行两次单独的 `query()` 调用。第一次创建新会话；第二次设置 `continue: true`，告诉 SDK 查找并恢复磁盘上最近的会话。Agent 拥有第一次调用的完整上下文：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

// 第一个查询：创建新会话
for await (const message of query({
  prompt: "Analyze the auth module",
  options: { allowedTools: ["Read", "Glob", "Grep"] }
})) {
  if (message.type === "result" && message.subtype === "success") {
    console.log(message.result);
  }
}

// 第二个查询：continue: true 恢复最近的会话
for await (const message of query({
  prompt: "Now refactor it to use JWT",
  options: {
    continue: true,
    allowedTools: ["Read", "Edit", "Write", "Glob", "Grep"]
  }
})) {
  if (message.type === "result" && message.subtype === "success") {
    console.log(message.result);
  }
}
```

> 实验性的 [V2 会话 API](https://code.claude.com/docs/en/agent-sdk/typescript-v2-preview)（提供带 `send` / `stream` 模式的 `createSession()`）已在 TypeScript Agent SDK 0.3.142 中移除。请使用 `query()` 函数和本页描述的会话选项。

## 通过 `query()` 使用会话选项

### 捕获会话 ID

**Resume 和 fork 需要会话 ID。** 从结果消息的 `session_id` 字段读取（Python 中为 [`ResultMessage`](https://code.claude.com/docs/en/agent-sdk/python#resultmessage)，TypeScript 中为 [`SDKResultMessage`](https://code.claude.com/docs/en/agent-sdk/typescript#sdkresultmessage)），无论成功或错误每个结果都带有此字段。在 TypeScript 中，ID 也可以更早地作为 init `SystemMessage` 的直接字段获取；在 Python 中它嵌套在 `SystemMessage.data` 内。

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


async def main():
    session_id = None

    async for message in query(
        prompt="Analyze the auth module and suggest improvements",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Glob", "Grep"],
        ),
    ):
        if isinstance(message, ResultMessage):
            session_id = message.session_id
            if message.subtype == "success":
                print(message.result)

    print(f"Session ID: {session_id}")
    return session_id


session_id = asyncio.run(main())
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

let sessionId: string | undefined;

for await (const message of query({
  prompt: "Analyze the auth module and suggest improvements",
  options: { allowedTools: ["Read", "Glob", "Grep"] }
})) {
  if (message.type === "result") {
    sessionId = message.session_id;
    if (message.subtype === "success") {
      console.log(message.result);
    }
  }
}

console.log(`Session ID: ${sessionId}`);
```

### 通过 ID 恢复

**传递会话 ID 到 `resume` 以返回该特定会话。** Agent 带着完整的上下文从会话离开的地方接续。恢复的常见原因：

* **跟进已完成的任务** — Agent 已经分析了某些内容；现在你希望它基于该分析采取行动，无需重新读取文件。
* **从限制中恢复** — 首次运行以 `error_max_turns` 或 `error_max_budget_usd` 结束（见[处理结果](https://code.claude.com/docs/en/agent-sdk/agent-loop#handle-the-result)）；使用更高限制恢复。
* **重启进程** — 你在关闭前捕获了 ID，想恢复对话。

此示例从[捕获会话 ID](#捕获会话-id) 中恢复会话并发送后续提示。因为是恢复，Agent 已经在上下文中有了先前的分析：

```python
# 先前的会话分析了代码；现在基于该分析继续
async for message in query(
    prompt="Now implement the refactoring you suggested",
    options=ClaudeAgentOptions(
        resume=session_id,
        allowed_tools=["Read", "Edit", "Write", "Glob", "Grep"],
    ),
):
    if isinstance(message, ResultMessage) and message.subtype == "success":
        print(message.result)
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

const sessionId = "..."; // 前面示例中捕获的 ID

// 先前的会话分析了代码；现在基于该分析继续
for await (const message of query({
  prompt: "Now implement the refactoring you suggested",
  options: {
    resume: sessionId,
    allowedTools: ["Read", "Edit", "Write", "Glob", "Grep"]
  }
})) {
  if (message.type === "result" && message.subtype === "success") {
    console.log(message.result);
  }
}
```

你应该看到基于先前分析构建的响应，而不是从头开始。这确认了 Agent 以其先前上下文恢复了会话。

> 如果 `resume` 调用返回全新会话而非预期历史，最常见的原因是 `cwd` 不匹配。会话存储在 `~/.claude/projects/<encoded-cwd>/*.jsonl` 下，或在设置了 `CLAUDE_CONFIG_DIR` 环境变量时存储在 `$CLAUDE_CONFIG_DIR/projects/<encoded-cwd>/*.jsonl` 下，其中 `<encoded-cwd>` 是绝对工作目录，每个非字母数字字符替换为 `-`（如 `/Users/me/proj` 变为 `-Users-me-proj`）。如果你的 resume 调用从不同目录运行，SDK 会查找错误的位置。会话文件也需要存在于当前机器上。

要跨机器或在无服务器环境中恢复会话，使用 [`SessionStore` 适配器](https://code.claude.com/docs/en/agent-sdk/session-storage)将记录镜像到共享存储。

### Fork 探索替代方案

**Fork 创建一个新会话，以原始会话历史的副本开始但从该点分叉。** Fork 获得自己的会话 ID；原始的 ID 和历史保持不变。你最终得到两个可以分别恢复的独立会话。

> Fork 分叉的是对话历史，不是文件系统。如果 fork 出的 Agent 编辑了文件，这些更改是真实的，对在同一目录工作的任何会话都可见。要分叉和回滚文件更改，使用[文件检查点](https://code.claude.com/docs/en/agent-sdk/file-checkpointing)。

此示例基于[捕获会话 ID](#捕获会话-id)：你已在 `session_id` 中分析了一个 auth 模块，想在不丢失 JWT 主线的情况下探索 OAuth2。第一个代码块 fork 会话并捕获 fork 的 ID（`forked_id`）；第二个代码块恢复原始 `session_id` 以继续 JWT 路线。你现在有两个会话 ID 指向两段独立的历史：

```python
# Fork：从 session_id 分叉出一个新会话
forked_id = None
async for message in query(
    prompt="Instead of JWT, outline how OAuth2 would work for the auth module",
    options=ClaudeAgentOptions(
        resume=session_id,
        fork_session=True,
        max_turns=5,
    ),
):
    if isinstance(message, ResultMessage):
        forked_id = message.session_id  # Fork 的 ID，与 session_id 不同
        if message.subtype == "success":
            print(message.result)

print(f"Forked session: {forked_id}")

# 原始会话未受影响；恢复它继续 JWT 主线
async for message in query(
    prompt="Continue with the JWT approach",
    options=ClaudeAgentOptions(resume=session_id),
):
    if isinstance(message, ResultMessage) and message.subtype == "success":
        print(message.result)
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

const sessionId = "..."; // 前面示例中捕获的 ID

// Fork：从 sessionId 分叉出一个新会话
let forkedId: string | undefined;

for await (const message of query({
  prompt: "Instead of JWT, outline how OAuth2 would work for the auth module",
  options: {
    resume: sessionId,
    forkSession: true,
    maxTurns: 5
  }
})) {
  if (message.type === "system" && message.subtype === "init") {
    forkedId = message.session_id; // Fork 的 ID，与 sessionId 不同
  }
  if (message.type === "result" && message.subtype === "success") {
    console.log(message.result);
  }
}

console.log(`Forked session: ${forkedId}`);

// 原始会话未受影响；恢复它继续 JWT 主线
for await (const message of query({
  prompt: "Continue with the JWT approach",
  options: { resume: sessionId }
})) {
  if (message.type === "result" && message.subtype === "success") {
    console.log(message.result);
  }
}
```

你应该看到 `forkedId` 与原始会话 ID 不同。恢复原始会话仍然延续 JWT 主线，这确认了 fork 没有修改原始历史。

## 跨主机恢复

**会话文件位于创建它们的机器本地。** 要在不同主机上恢复会话（CI worker、临时容器、无服务器环境），有两个选择：

* **移动会话文件** — 从首次运行中持久化 `~/.claude/projects/<encoded-cwd>/<session-id>.jsonl`，在新主机上恢复到相同路径后再调用 `resume`。`cwd` 必须匹配。
* **不依赖会话恢复** — 将你需要的结果（分析输出、决策、文件 diff）捕获为应用状态，传入新会话的提示中。这通常比搬运记录文件更可靠。

两个 SDK 都暴露了枚举磁盘上会话和读取其消息的函数：TypeScript 中的 [`listSessions()`](https://code.claude.com/docs/en/agent-sdk/typescript#listsessions) 和 [`getSessionMessages()`](https://code.claude.com/docs/en/agent-sdk/typescript#getsessionmessages)，Python 中的 [`list_sessions()`](https://code.claude.com/docs/en/agent-sdk/python#list_sessions) 和 [`get_session_messages()`](https://code.claude.com/docs/en/agent-sdk/python#get_session_messages)。用它们构建自定义会话选择器、清理逻辑或记录查看器。

两个 SDK 也暴露了查找和修改单个会话的函数：Python 中的 [`get_session_info()`](https://code.claude.com/docs/en/agent-sdk/python#get_session_info)、[`rename_session()`](https://code.claude.com/docs/en/agent-sdk/python#rename_session) 和 [`tag_session()`](https://code.claude.com/docs/en/agent-sdk/python#tag_session)，TypeScript 中的 [`getSessionInfo()`](https://code.claude.com/docs/en/agent-sdk/typescript#getsessioninfo)、[`renameSession()`](https://code.claude.com/docs/en/agent-sdk/typescript#renamesession) 和 [`tagSession()`](https://code.claude.com/docs/en/agent-sdk/typescript#tagsession)。用它们按标签组织会话或给予人类可读的标题。

## 相关资源

* [Agent 循环工作原理](https://code.claude.com/docs/en/agent-sdk/agent-loop)：了解会话内的轮次、消息和上下文累积
* [文件检查点](https://code.claude.com/docs/en/agent-sdk/file-checkpointing)：快照和回滚 Agent 在会话中所做的文件更改
* [Python `ClaudeAgentOptions`](https://code.claude.com/docs/en/agent-sdk/python#claudeagentoptions)：Python 完整会话选项参考
* [TypeScript `Options`](https://code.claude.com/docs/en/agent-sdk/typescript#options)：TypeScript 完整会话选项参考
