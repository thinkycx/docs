---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Agent SDK - Todo 追踪
description: 通过 Claude Agent SDK 追踪和展示 Todo 任务进度。涵盖 Todo 生命周期、TodoWrite 工具监控、实时进度展示，以及迁移到新的 Task 工具的方法。
category: translation
tags: [claude-code, agent-sdk, todo, translation]
refs:
  - https://code.claude.com/docs/en/agent-sdk/todo-tracking
  - en-source/agent-sdk/todo-tracking.md
---

# Todo 列表

> 通过 Claude Agent SDK 追踪和展示 Todo 任务，实现有序的任务管理

**Todo 追踪提供了一种结构化的方式来管理任务并向用户展示进度。** Claude Agent SDK 内置 Todo 功能，帮助组织复杂工作流并让用户了解任务进展。

> **注意：** 自 TypeScript Agent SDK 0.3.142 和 Claude Code v2.1.142 起，会话使用结构化的 Task 工具（`TaskCreate`、`TaskUpdate`、`TaskGet`、`TaskList`）取代 `TodoWrite`。Python SDK 的变更来自其启动的 Claude Code CLI，而非 Python 包版本：当该 CLI（pip 包内捆绑的副本，或通过 `cli_path` 指定的）为 v2.1.142 或更高版本时切换生效。参见[迁移到 Task 工具](#迁移到-task-工具)了解监控代码的变化。本页示例设置 `CLAUDE_CODE_ENABLE_TASKS=0` 以继续展示尚未迁移的会话中的 `TodoWrite`。

### Todo 生命周期

**Todo 遵循可预测的生命周期：**

| 阶段 | 状态 | 说明 |
|:---|:---|:---|
| 创建 | `pending` | 任务被识别时 |
| 激活 | `in_progress` | 开始执行时 |
| 完成 | `completed` | 任务成功完成时 |
| 移除 | — | 组内所有任务完成时 |

### 何时使用 Todo

**SDK 会为大多数多步骤工作创建 Todo：**

* 需要 3 个或更多不同动作的复杂多步任务
* 用户提供的任务列表（提到多个项目时）
* 受益于进度追踪的非平凡操作
* 用户明确请求 Todo 组织

对于非常短或单步骤的请求可能会跳过 Todo。

## 示例

运行这些示例前，请按照[快速入门](https://code.claude.com/docs/en/agent-sdk/quickstart)安装 Claude Agent SDK。

每个示例运行直到 Agent 完成并产出最终结果消息。如果会话先达到轮次限制，结果消息的 subtype 为 `error_max_turns`。检查 `subtype` 来检测这种结束。

这些示例使用单次 `query()` 调用。产出 `error_max_turns` 结果后，`query()` 会抛出包含 `Reached maximum number of turns` 的错误。每个示例用 try 块包裹循环以在发生时优雅退出。

参见[处理结果](https://code.claude.com/docs/en/agent-sdk/agent-loop#handle-the-result)了解结果子类型。

### 监控 Todo 变更

TypeScript：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

try {
  for await (const message of query({
    prompt: "Optimize my React app performance and track progress with todos",
    // 重新启用 TodoWrite（本示例监控的对象）。不启用时 SDK 使用
    // Task 工具，这些 tool_use 块永远不会出现。
    options: { maxTurns: 15, env: { ...process.env, CLAUDE_CODE_ENABLE_TASKS: "0" } }
  })) {
    // Todo 更新反映在消息流中
    if (message.type === "assistant") {
      for (const block of message.message.content) {
        if (block.type === "tool_use" && block.name === "TodoWrite") {
          const todos = block.input.todos;

          console.log("Todo Status Update:");
          todos.forEach((todo, index) => {
            const status =
              todo.status === "completed" ? "✅" : todo.status === "in_progress" ? "🔧" : "❌";
            console.log(`${index + 1}. ${status} ${todo.content}`);
          });
        }
      }
    }
  }
} catch (error) {
  // 单次 query() 在产出错误结果后抛出异常，
  // 例如达到 maxTurns 限制时。
  console.log(`Session ended with an error: ${error}`);
}
```

Python：

```python
import asyncio

from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ToolUseBlock


async def main():
    try:
        async for message in query(
            prompt="Optimize my React app performance and track progress with todos",
            # 重新启用 TodoWrite（本示例监控的对象）。不启用时 SDK 使用
            # Task 工具，这些 tool_use 块永远不会出现。
            options=ClaudeAgentOptions(max_turns=15, env={"CLAUDE_CODE_ENABLE_TASKS": "0"}),
        ):
            # Todo 更新反映在消息流中
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, ToolUseBlock) and block.name == "TodoWrite":
                        todos = block.input["todos"]

                        print("Todo Status Update:")
                        for i, todo in enumerate(todos):
                            status = (
                                "✅"
                                if todo["status"] == "completed"
                                else "🔧"
                                if todo["status"] == "in_progress"
                                else "❌"
                            )
                            print(f"{i + 1}. {status} {todo['content']}")
    except Exception as error:
        # 单次 query() 在产出错误结果后抛出异常，
        # 例如达到 max_turns 限制时。
        print(f"Session ended with an error: {error}")


asyncio.run(main())
```

### 实时进度展示

TypeScript：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

class TodoTracker {
  private todos: any[] = [];

  displayProgress() {
    if (this.todos.length === 0) return;

    const completed = this.todos.filter((t) => t.status === "completed").length;
    const inProgress = this.todos.filter((t) => t.status === "in_progress").length;
    const total = this.todos.length;

    console.log(`\nProgress: ${completed}/${total} completed`);
    console.log(`Currently working on: ${inProgress} task(s)\n`);

    this.todos.forEach((todo, index) => {
      const icon =
        todo.status === "completed" ? "✅" : todo.status === "in_progress" ? "🔧" : "❌";
      const text = todo.status === "in_progress" ? todo.activeForm : todo.content;
      console.log(`${index + 1}. ${icon} ${text}`);
    });
  }

  async trackQuery(prompt: string) {
    try {
      for await (const message of query({
        prompt,
        // 重新启用 TodoWrite（tracker 监听的对象）。
        options: { maxTurns: 20, env: { ...process.env, CLAUDE_CODE_ENABLE_TASKS: "0" } }
      })) {
        if (message.type === "assistant") {
          for (const block of message.message.content) {
            if (block.type === "tool_use" && block.name === "TodoWrite") {
              this.todos = block.input.todos;
              this.displayProgress();
            }
          }
        }
      }
    } catch (error) {
      console.log(`Session ended with an error: ${error}`);
    }
  }
}

// 使用
const tracker = new TodoTracker();
await tracker.trackQuery("Build a complete authentication system with todos");
```

Python：

```python
import asyncio

from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ToolUseBlock
from typing import List, Dict


class TodoTracker:
    def __init__(self):
        self.todos: List[Dict] = []

    def display_progress(self):
        if not self.todos:
            return

        completed = len([t for t in self.todos if t["status"] == "completed"])
        in_progress = len([t for t in self.todos if t["status"] == "in_progress"])
        total = len(self.todos)

        print(f"\nProgress: {completed}/{total} completed")
        print(f"Currently working on: {in_progress} task(s)\n")

        for i, todo in enumerate(self.todos):
            icon = (
                "✅"
                if todo["status"] == "completed"
                else "🔧"
                if todo["status"] == "in_progress"
                else "❌"
            )
            text = (
                todo["activeForm"]
                if todo["status"] == "in_progress"
                else todo["content"]
            )
            print(f"{i + 1}. {icon} {text}")

    async def track_query(self, prompt: str):
        try:
            async for message in query(
                prompt=prompt,
                # 重新启用 TodoWrite（tracker 监听的对象）。
                options=ClaudeAgentOptions(max_turns=20, env={"CLAUDE_CODE_ENABLE_TASKS": "0"}),
            ):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, ToolUseBlock) and block.name == "TodoWrite":
                            self.todos = block.input["todos"]
                            self.display_progress()
        except Exception as error:
            print(f"Session ended with an error: {error}")


# 使用
async def main():
    tracker = TodoTracker()
    await tracker.track_query("Build a complete authentication system with todos")


asyncio.run(main())
```

## 迁移到 Task 工具

**Task 工具将单一的 `TodoWrite` 调用拆分为 `TaskCreate`（创建每个新项）和 `TaskUpdate`（更新每个状态变化），`TaskList` 和 `TaskGet` 可供模型读取当前列表。** 监控代码仍然检查 assistant 流中的 `tool_use` 块，但维护一个以 task ID 为键的 map，而非每次调用时替换整个列表。自 TypeScript Agent SDK 0.3.142 和 Claude Code v2.1.142 起，Task 工具是默认值，无需设置 `options.env`。

### TodoWrite vs Task 工具对比

| `TodoWrite` | Task 工具 |
|:---|:---|
| 一次工具调用重写整个 `todos` 数组 | `TaskCreate` 添加一项，`TaskUpdate` 按 `taskId` 修改一项 |
| 匹配 `block.name === "TodoWrite"` | 匹配 `block.name === "TaskCreate"` 或 `"TaskUpdate"` |
| 项结构：`{ content, status, activeForm }` | `TaskCreate` 输入：`{ subject, description, activeForm?, metadata? }`。`TaskUpdate` 输入：`{ taskId, status?, subject?, description?, activeForm?, addBlocks?, addBlockedBy?, owner?, metadata? }`。`status` 为 `"pending"`、`"in_progress"` 或 `"completed"`；设为 `"deleted"` 可删除 |
| 直接渲染 `block.input.todos` | 跨调用累积项，或从 `TaskList` 工具结果中读取快照 |

**已分配的 task ID 不在 `TaskCreate` 输入中。** 它在匹配的 `tool_result` 中以 `{ task: { id, subject } }` 返回，因此从结果块中捕获它来建立 map 的键。以下示例展示对[监控 Todo 变更](#监控-todo-变更)循环的最小改动。它只读取 `tool_use` 输入，跳过从 `tool_result` 块捕获 ID。要渲染完整列表，请观察流中的 `TaskList` 工具结果，或累积 `TaskCreate` 结果和 `TaskUpdate` 输入到 map 中。

流中的 `tool_use` 输入是模型发出的原始形状。Claude Code 在执行前会修复一些接近但不正确的键名（将 `id` 或 `task_id` 映射为 `taskId`，`active_form` 映射为 `activeForm`），但该修复不反映在流中。请防御性地读取 `TaskUpdate` 输入字段（如下面的示例所示），不要假设始终使用规范名称。

TypeScript：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

try {
  for await (const message of query({
    prompt: "Optimize my React app performance and track progress with todos",
    options: { maxTurns: 15 },
  })) {
    if (message.type !== "assistant") continue;
    for (const block of message.message.content) {
      if (block.type !== "tool_use") continue;
      if (block.name === "TaskCreate") {
        const input = block.input as { subject: string };
        console.log(`+ ${input.subject}`);
      } else if (block.name === "TaskUpdate") {
        const input = block.input as {
          taskId?: string;
          id?: string;
          task_id?: string;
          status?: string;
        };
        const taskId = input.taskId ?? input.id ?? input.task_id;
        if (taskId && input.status) console.log(`  ${taskId} -> ${input.status}`);
      }
    }
  }
} catch (error) {
  // 单次 query() 在产出错误结果后抛出异常。
  console.log(`Session ended with an error: ${error}`);
}
```

Python：

```python
import asyncio

from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ToolUseBlock

async def main():
    try:
        async for message in query(
            prompt="Optimize my React app performance and track progress with todos",
            options=ClaudeAgentOptions(max_turns=15),
        ):
            if not isinstance(message, AssistantMessage):
                continue
            for block in message.content:
                if not isinstance(block, ToolUseBlock):
                    continue
                if block.name == "TaskCreate":
                    print(f"+ {block.input['subject']}")
                elif block.name == "TaskUpdate" and block.input.get("status"):
                    task_id = (
                        block.input.get("taskId")
                        or block.input.get("id")
                        or block.input.get("task_id")
                    )
                    if task_id:
                        print(f"  {task_id} -> {block.input['status']}")
    except Exception as error:
        # 单次 query() 在产出错误结果后抛出异常。
        print(f"Session ended with an error: {error}")


asyncio.run(main())
```

## 相关文档

* [TypeScript SDK 参考](https://code.claude.com/docs/en/agent-sdk/typescript)
* [Python SDK 参考](https://code.claude.com/docs/en/agent-sdk/python)
* [流式 vs 单次模式](https://code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode)
* [自定义工具](https://code.claude.com/docs/en/agent-sdk/custom-tools)
