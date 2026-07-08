---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Agent SDK - 用户输入处理
description: Claude Agent SDK 用户输入处理指南，涵盖工具审批回调、澄清问题处理、AskUserQuestion 工具、响应格式与多种审批模式。
category: translation
tags: [claude-code, agent-sdk, translation]
refs:
  - https://code.claude.com/docs/en/agent-sdk/user-input
  - en-source/agent-sdk/user-input.md
---

# 处理审批与用户输入

> 将 Claude 的审批请求和澄清问题展示给用户，然后将用户决策返回给 SDK。

**Claude 在执行任务时有时需要与用户确认。** 它可能需要在删除文件前请求权限，或需要询问新项目该使用哪个数据库。应用需要将这些请求展示给用户，以便 Claude 能在获得用户输入后继续工作。

Claude 在两种情况下请求用户输入：需要**使用工具的权限**（如删除文件或运行命令），以及有**澄清问题**（通过 `AskUserQuestion` 工具）。两者都会触发 `canUseTool` 回调，暂停执行直到你返回响应。这不同于 Claude 完成回复后等待下一条消息的普通对话轮次。

对于澄清问题，Claude 生成问题和选项。你的职责是将它们展示给用户并返回选择结果。你不能在这个流程中添加自己的问题；如果需要自行向用户提问，请在应用逻辑中单独处理。

回调可以无限期挂起。执行保持暂停直到回调返回，SDK 只在 query 本身被取消时才取消等待。如果用户可能需要比进程合理运行时间更长的响应时间，返回 [`defer` hook 决策](https://code.claude.com/docs/en/hooks#defer-a-tool-call-for-later)，让进程退出并稍后从持久化的会话中恢复。

## 检测 Claude 何时需要输入

**在查询选项中传入 `canUseTool` 回调。** 回调在 Claude 需要用户输入时触发，接收工具名称和输入作为参数：

```python
async def handle_tool_request(tool_name, input_data, context):
    # 提示用户并返回 allow 或 deny
    ...


options = ClaudeAgentOptions(can_use_tool=handle_tool_request)
```

```typescript
async function handleToolRequest(toolName, input, options) {
  // options 包含 { signal: AbortSignal, suggestions?: PermissionUpdate[] }
  // 提示用户并返回 allow 或 deny
}

const options = { canUseTool: handleToolRequest };
```

回调在两种情况下触发：

1. **工具需要审批**：Claude 想使用一个未被[权限规则](https://code.claude.com/docs/en/agent-sdk/permissions)或权限模式自动批准的工具。检查 `tool_name` 获取工具名（如 `"Bash"`、`"Write"`）。
2. **Claude 提出问题**：Claude 调用 `AskUserQuestion` 工具。检查 `tool_name == "AskUserQuestion"` 以差异化处理。如果指定了 `tools` 数组，需包含 `AskUserQuestion` 才能生效。详见[处理澄清问题](#处理澄清问题)。

> **回调不会为自动批准的工具触发。** [权限评估流程](https://code.claude.com/docs/en/agent-sdk/permissions#how-permissions-are-evaluated)中更早期的任何批准——allow 规则或 `acceptEdits`、`bypassPermissions` 等模式——会在咨询 `canUseTool` 之前解决调用。如果在 `allowed_tools` 中直接列出工具，该工具的 `canUseTool` 检查不会运行，除非 ask 规则或 `plan` 模式将调用路由回提示。对于必须应用于每次工具调用的逻辑，使用 [`PreToolUse` hook](https://code.claude.com/docs/en/agent-sdk/hooks)——它在流程其余部分之前执行，可以允许、拒绝或修改请求。

你也可以使用 [`PermissionRequest` hook](https://code.claude.com/docs/en/agent-sdk/hooks#available-hooks) 在 Claude 等待审批时发送外部通知（Slack、邮件、推送）。

## 处理工具审批请求

**在查询选项中传入 `canUseTool` 回调后，当 Claude 想使用权限流程中未被更早批准的工具时，回调会触发。** 回调接收三个参数：

| 参数 | 说明 |
|:---|:---|
| `toolName` | Claude 想使用的工具名称（如 `"Bash"`、`"Write"`、`"Edit"`） |
| `input` | Claude 传给工具的参数。内容因工具而异。 |
| `options`（TS）/ `context`（Python） | 额外上下文，包括可选的 `suggestions`（建议的 `PermissionUpdate` 条目以避免重复提示）和取消信号。TypeScript 中 `signal` 是 `AbortSignal`；Python 中信号字段预留给未来使用。参见 [`ToolPermissionContext`](https://code.claude.com/docs/en/agent-sdk/python#toolpermissioncontext)。 |

`input` 对象包含工具特定的参数。常见示例：

| 工具 | 输入字段 |
|:---|:---|
| `Bash` | `command`、`description`、`timeout` |
| `Write` | `file_path`、`content` |
| `Edit` | `file_path`、`old_string`、`new_string` |
| `Read` | `file_path`、`offset`、`limit` |

完整输入 schema 参见 SDK 参考：[Python](https://code.claude.com/docs/en/agent-sdk/python#tool-input%2Foutput-types) | [TypeScript](https://code.claude.com/docs/en/agent-sdk/typescript#tool-input-types)。

你可以将这些信息展示给用户，让他们决定允许还是拒绝操作，然后返回对应的响应。

以下示例要求 Claude 创建并删除一个测试文件。当 Claude 尝试每个操作时，回调将工具请求打印到终端并提示用户 y/n 审批。

```python
import asyncio

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query
from claude_agent_sdk.types import (
    HookMatcher,
    PermissionResultAllow,
    PermissionResultDeny,
    ToolPermissionContext,
)


async def can_use_tool(
    tool_name: str, input_data: dict, context: ToolPermissionContext
) -> PermissionResultAllow | PermissionResultDeny:
    # 展示工具请求
    print(f"\nTool: {tool_name}")
    if tool_name == "Bash":
        print(f"Command: {input_data.get('command')}")
        if input_data.get("description"):
            print(f"Description: {input_data.get('description')}")
    else:
        print(f"Input: {input_data}")

    # 获取用户审批
    response = input("Allow this action? (y/n): ")

    # 根据用户响应返回 allow 或 deny
    if response.lower() == "y":
        # Allow：工具使用原始（或修改后的）输入执行
        return PermissionResultAllow(updated_input=input_data)
    else:
        # Deny：工具不执行，Claude 看到消息
        return PermissionResultDeny(message="User denied this action")


# 必要的变通：dummy hook 保持流打开以支持 can_use_tool
async def dummy_hook(input_data, tool_use_id, context):
    return {"continue_": True}


async def prompt_stream():
    yield {
        "type": "user",
        "message": {
            "role": "user",
            "content": "Create a test file in /tmp and then delete it",
        },
    }


async def main():
    async for message in query(
        prompt=prompt_stream(),
        options=ClaudeAgentOptions(
            can_use_tool=can_use_tool,
            hooks={"PreToolUse": [HookMatcher(matcher=None, hooks=[dummy_hook])]},
        ),
    ):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(message.result)


asyncio.run(main())
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";
import * as readline from "readline";

// 辅助函数：在终端提示用户输入
function prompt(question: string): Promise<string> {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  return new Promise((resolve) =>
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer);
    })
  );
}

for await (const message of query({
  prompt: "Create a test file in /tmp and then delete it",
  options: {
    canUseTool: async (toolName, input) => {
      // 展示工具请求
      console.log(`\nTool: ${toolName}`);
      if (toolName === "Bash") {
        console.log(`Command: ${input.command}`);
        if (input.description) console.log(`Description: ${input.description}`);
      } else {
        console.log(`Input: ${JSON.stringify(input, null, 2)}`);
      }

      // 获取用户审批
      const response = await prompt("Allow this action? (y/n): ");

      // 根据用户响应返回 allow 或 deny
      if (response.toLowerCase() === "y") {
        // Allow：工具使用原始（或修改后的）输入执行
        return { behavior: "allow", updatedInput: input };
      } else {
        // Deny：工具不执行，Claude 看到消息
        return { behavior: "deny", message: "User denied this action" };
      }
    }
  }
})) {
  if ("result" in message) console.log(message.result);
}
```

> **Python 注意：** `can_use_tool` 需要[流式模式](https://code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode)。当通过 `query(prompt=generator)` 或 `ClaudeSDKClient.connect(prompt=async_iterable)` 传入有限消息流时，SDK 在最后一条消息后关闭输入流——此时权限回调还未被调用——除非有注册的 hook 或进程内 MCP server 保持流打开。上面的示例使用返回 `{"continue_": True}` 的 `PreToolUse` hook 保持流打开。通过不带 prompt 连接并通过 `ClaudeSDKClient.query()` 发送消息的方式会自行保持流打开，不需要 hook。

此示例使用 `y/n` 流程，非 `y` 的任何输入都被视为拒绝。实际中你可能构建更丰富的 UI，让用户修改请求、提供反馈或完全重定向 Claude。参见[响应工具请求](#响应工具请求)了解所有响应方式。

### 响应工具请求

**回调返回两种响应类型之一：**

| 响应 | Python | TypeScript |
|:---|:---|:---|
| **允许** | `PermissionResultAllow(updated_input=...)` | `{ behavior: "allow", updatedInput }` |
| **拒绝** | `PermissionResultDeny(message=...)` | `{ behavior: "deny", message }` |

允许时，传入工具输入（原始或修改后的）。拒绝时，提供说明原因的消息。Claude 看到此消息后可能调整方案。

```python
from claude_agent_sdk.types import PermissionResultAllow, PermissionResultDeny

# 允许工具执行
return PermissionResultAllow(updated_input=input_data)

# 阻止工具
return PermissionResultDeny(message="User rejected this action")
```

```typescript
// 允许工具执行
return { behavior: "allow", updatedInput: input };

// 阻止工具
return { behavior: "deny", message: "User rejected this action" };
```

**除了简单的允许或拒绝，你还可以修改工具输入或提供帮助 Claude 调整方案的上下文：**

* **批准**：让工具按 Claude 的请求执行
* **批准并修改**：执行前修改输入（如清理路径、添加约束）
* **批准并记住**：回传一条建议的权限规则，使匹配的后续调用跳过提示
* **拒绝**：阻止工具并告诉 Claude 原因
* **建议替代方案**：阻止但引导 Claude 朝用户想要的方向
* **完全重定向**：使用[流式输入](https://code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode)给 Claude 发送全新指令

#### 批准

**用户原样批准操作。** 将回调中的 `input` 不变传回，工具按 Claude 请求的方式精确执行。

```python
async def can_use_tool(tool_name, input_data, context):
    print(f"Claude wants to use {tool_name}")
    approved = await ask_user("Allow this action?")

    if approved:
        return PermissionResultAllow(updated_input=input_data)
    return PermissionResultDeny(message="User declined")
```

```typescript
canUseTool: async (toolName, input) => {
  console.log(`Claude wants to use ${toolName}`);
  const approved = await askUser("Allow this action?");

  if (approved) {
    return { behavior: "allow", updatedInput: input };
  }
  return { behavior: "deny", message: "User declined" };
};
```

#### 批准并修改

**用户批准但想先修改请求。** 你可以在工具执行前更改输入。Claude 看到结果但不会被告知你修改了什么。适用于清理参数、添加约束或限定访问范围。

```python
async def can_use_tool(tool_name, input_data, context):
    if tool_name == "Bash":
        # 用户批准，但将所有命令限定在沙箱中
        sandboxed_input = {**input_data}
        sandboxed_input["command"] = input_data["command"].replace(
            "/tmp", "/tmp/sandbox"
        )
        return PermissionResultAllow(updated_input=sandboxed_input)
    return PermissionResultAllow(updated_input=input_data)
```

```typescript
canUseTool: async (toolName, input) => {
  if (toolName === "Bash") {
    // 用户批准，但将所有命令限定在沙箱中
    const sandboxedInput = {
      ...input,
      command: input.command.replace("/tmp", "/tmp/sandbox")
    };
    return { behavior: "allow", updatedInput: sandboxedInput };
  }
  return { behavior: "allow", updatedInput: input };
};
```

#### 批准并记住

**用户批准且不想再次被询问同类调用。** 回调的第三个参数携带 `suggestions`——现成的 [`PermissionUpdate`](https://code.claude.com/docs/en/agent-sdk/typescript#permissionupdate) 条目数组。回传其中一个到 `updatedPermissions` 以应用它。`localSettings` 目标的 suggestion 将规则写入 `.claude/settings.local.json`，后续会话中匹配的调用跳过提示。

Python 示例需要 `claude-agent-sdk` 0.1.80 或更高版本。

```python
async def can_use_tool(tool_name, input_data, context):
    choice = await ask_user(f"Allow {tool_name}?", ["once", "always", "no"])

    if choice == "always":
        persist = [
            s for s in context.suggestions if s.destination == "localSettings"
        ]
        return PermissionResultAllow(
            updated_input=input_data, updated_permissions=persist
        )
    if choice == "once":
        return PermissionResultAllow(updated_input=input_data)
    return PermissionResultDeny(message="User declined")
```

```typescript
canUseTool: async (toolName, input, { suggestions = [] }) => {
  const choice = await askUser(`Allow ${toolName}?`, ["once", "always", "no"]);

  if (choice === "always") {
    const persist = suggestions.filter(
      (s) => s.destination === "localSettings"
    );
    return {
      behavior: "allow",
      updatedInput: input,
      updatedPermissions: persist
    };
  }
  if (choice === "once") {
    return { behavior: "allow", updatedInput: input };
  }
  return { behavior: "deny", message: "User declined" };
};
```

#### 拒绝

**用户不希望执行此操作。** 阻止工具并提供解释原因的消息。Claude 看到此消息后可能尝试不同的方案。

```python
async def can_use_tool(tool_name, input_data, context):
    approved = await ask_user(f"Allow {tool_name}?")

    if not approved:
        return PermissionResultDeny(message="User rejected this action")
    return PermissionResultAllow(updated_input=input_data)
```

```typescript
canUseTool: async (toolName, input) => {
  const approved = await askUser(`Allow ${toolName}?`);

  if (!approved) {
    return {
      behavior: "deny",
      message: "User rejected this action"
    };
  }
  return { behavior: "allow", updatedInput: input };
};
```

#### 建议替代方案

**用户不想要这个特定操作，但有不同的想法。** 阻止工具并在消息中包含引导。Claude 会阅读并根据反馈决定如何继续。

```python
async def can_use_tool(tool_name, input_data, context):
    if tool_name == "Bash" and "rm" in input_data.get("command", ""):
        # 用户不想删除，建议改为归档
        return PermissionResultDeny(
            message="User doesn't want to delete files. They asked if you could compress them into an archive instead."
        )
    return PermissionResultAllow(updated_input=input_data)
```

```typescript
canUseTool: async (toolName, input) => {
  if (toolName === "Bash" && input.command.includes("rm")) {
    // 用户不想删除，建议改为归档
    return {
      behavior: "deny",
      message:
        "User doesn't want to delete files. They asked if you could compress them into an archive instead."
    };
  }
  return { behavior: "allow", updatedInput: input };
};
```

#### 完全重定向

**需要完全改变方向时（不只是微调），使用[流式输入](https://code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode)给 Claude 发送新指令。** 这绕过当前工具请求，给 Claude 全新的指令去遵循。

## 处理澄清问题

**当 Claude 在有多种有效方案的任务中需要更多方向时，它调用 `AskUserQuestion` 工具。** 这会触发你的 `canUseTool` 回调，`toolName` 设为 `AskUserQuestion`。输入包含 Claude 的问题作为多选选项，你展示给用户并返回他们的选择。

> **提示：** 澄清问题在 [`plan` 模式](https://code.claude.com/docs/en/agent-sdk/permissions#plan-mode-plan)中尤其常见，Claude 会先探索代码库并提问，然后再提出计划。这使 plan 模式非常适合交互式工作流，让 Claude 在修改前先收集需求。

### 处理步骤

#### 1. 传入 `canUseTool` 回调

在查询选项中传入 `canUseTool` 回调。默认情况下 `AskUserQuestion` 可用。如果指定了 `tools` 数组来限制 Claude 的能力（例如只有 `Read`、`Glob`、`Grep` 的只读 agent），需在该数组中包含 `AskUserQuestion`。否则 Claude 无法提出澄清问题：

```python
async for message in query(
    prompt="Analyze this codebase",
    options=ClaudeAgentOptions(
        # 在 tools 列表中包含 AskUserQuestion
        tools=["Read", "Glob", "Grep", "AskUserQuestion"],
        can_use_tool=can_use_tool,
    ),
):
    print(message)
```

```typescript
for await (const message of query({
  prompt: "Analyze this codebase",
  options: {
    // 在 tools 列表中包含 AskUserQuestion
    tools: ["Read", "Glob", "Grep", "AskUserQuestion"],
    canUseTool: async (toolName, input) => {
      // 在此处理澄清问题
    }
  }
})) {
  console.log(message);
}
```

#### 2. 检测 AskUserQuestion

在回调中，检查 `toolName` 是否等于 `AskUserQuestion` 以差异化处理：

```python
async def can_use_tool(tool_name: str, input_data: dict, context):
    if tool_name == "AskUserQuestion":
        # 你的实现：从用户收集答案
        return await handle_clarifying_questions(input_data)
    # 正常处理其他工具
    return await prompt_for_approval(tool_name, input_data)
```

```typescript
canUseTool: async (toolName, input) => {
  if (toolName === "AskUserQuestion") {
    // 你的实现：从用户收集答案
    return handleClarifyingQuestions(input);
  }
  // 正常处理其他工具
  return promptForApproval(toolName, input);
};
```

#### 3. 解析问题输入

输入包含 Claude 的问题，位于 `questions` 数组中。每个问题有 `question`（要展示的文本）、`options`（选项）和 `multiSelect`（是否允许多选）：

```json
{
  "questions": [
    {
      "question": "How should I format the output?",
      "header": "Format",
      "options": [
        { "label": "Summary", "description": "Brief overview" },
        { "label": "Detailed", "description": "Full explanation" }
      ],
      "multiSelect": false
    },
    {
      "question": "Which sections should I include?",
      "header": "Sections",
      "options": [
        { "label": "Introduction", "description": "Opening context" },
        { "label": "Conclusion", "description": "Final summary" }
      ],
      "multiSelect": true
    }
  ]
}
```

#### 4. 从用户收集答案

将问题展示给用户并收集选择。具体方式取决于应用形态：终端提示、Web 表单、移动对话框等。

#### 5. 将答案返回给 Claude

构建 `answers` 对象，键为问题的 `question` 文本，值为所选选项的 `label`：

| 来源 | 用途 |
|:---|:---|
| `question` 字段（如 `"How should I format the output?"`） | 键 |
| 所选选项的 `label` 字段（如 `"Summary"`） | 值 |

对于多选问题，传入 label 数组或用 `", "` 连接。如果支持自由文本输入，使用用户的自定义文本作为值。

```python
return PermissionResultAllow(
    updated_input={
        "questions": input_data.get("questions", []),
        "answers": {
            "How should I format the output?": "Summary",
            "Which sections should I include?": ["Introduction", "Conclusion"],
        },
    }
)
```

```typescript
return {
  behavior: "allow",
  updatedInput: {
    questions: input.questions,
    answers: {
      "How should I format the output?": "Summary",
      "Which sections should I include?": "Introduction, Conclusion"
    }
  }
};
```

### 问题格式

**输入包含 Claude 生成的问题，位于 `questions` 数组中。** 每个问题有以下字段：

| 字段 | 说明 |
|:---|:---|
| `question` | 要展示的完整问题文本 |
| `header` | 问题的短标签（最多 12 个字符） |
| `options` | 2-4 个选项的数组，每个包含 `label` 和 `description`。TypeScript 中可选 `preview`（见下文） |
| `multiSelect` | 为 `true` 时用户可选择多个选项 |

回调接收的结构：

```json
{
  "questions": [
    {
      "question": "How should I format the output?",
      "header": "Format",
      "options": [
        { "label": "Summary", "description": "Brief overview of key points" },
        { "label": "Detailed", "description": "Full explanation with examples" }
      ],
      "multiSelect": false
    }
  ]
}
```

#### 选项预览（仅 TypeScript）

**`toolConfig.askUserQuestion.previewFormat` 为每个选项添加 `preview` 字段。** 这样应用可以在标签旁展示可视化预览。未设置时，Claude 不生成预览，该字段不存在。

| `previewFormat` | `preview` 内容 |
|:---|:---|
| 未设置（默认） | 字段不存在。Claude 不生成预览。 |
| `"markdown"` | ASCII art 和代码块 |
| `"html"` | 带样式的 `<div>` 片段（SDK 在回调运行前拒绝 `<script>`、`<style>` 和 `<!DOCTYPE>`） |

该格式应用于会话中的所有问题。Claude 在视觉比较有帮助的选项（布局选择、配色方案）上包含 `preview`，在不需要的选项（是/否确认、纯文本选择）上省略。渲染前检查 `undefined`。

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Help me choose a card layout",
  options: {
    toolConfig: {
      askUserQuestion: { previewFormat: "html" }
    },
    canUseTool: async (toolName, input) => {
      // input.questions[].options[].preview 是 HTML 字符串或 undefined
      return { behavior: "allow", updatedInput: input };
    }
  }
})) {
  // ...
}
```

带 HTML 预览的选项示例：

```json
{
  "label": "Compact",
  "description": "Title and metric value only",
  "preview": "<div style=\"padding:12px;border:1px solid #ddd;border-radius:8px\"><div style=\"font-size:12px;color:#666\">Active users</div><div style=\"font-size:28px;font-weight:600\">1,284</div></div>"
}
```

### 响应格式

**返回一个 `answers` 对象，将每个问题的 `question` 字段映射到所选选项的 `label`：**

| 字段 | 说明 |
|:---|:---|
| `questions` | 传回原始 questions 数组（工具处理必需） |
| `answers` | 键为问题文本、值为所选标签的对象 |
| `response` | 可选的自由文本回复——用户跳过结构化问题直接输入的通用回复 |

对于多选问题，传入 label 数组或用 `", "` 连接。对于每个问题的自由文本（如"其他"选项），将用户文本放在 `answers[question]` 中。仅当 UI 允许用户忽略问题卡片并输入通用回复（不针对任何特定问题）时才设置 `response`。设置 `response` 时，Claude 收到的是"The user responded: ..."而不是逐题答案列表。

```json
{
  "questions": [
    // ...
  ],
  "answers": {
    "How should I format the output?": "Summary",
    "Which sections should I include?": ["Introduction", "Conclusion"]
  }
}
```

#### 支持自由文本输入

**Claude 的预定义选项不总能覆盖用户需求。** 要让用户输入自己的答案：

* 在 Claude 的选项后显示一个接受文本输入的额外"其他"选项
* 使用用户的自定义文本作为答案值（不是"Other"这个词）

完整实现参见下方完整示例。

### 完整示例

**Claude 在需要用户输入才能继续时会提出澄清问题。** 例如，被要求帮助决定移动应用的技术栈时，Claude 可能会问关于跨平台还是原生、后端偏好或目标平台的问题。这些问题帮助 Claude 做出符合用户偏好的决策，而不是猜测。

此示例在终端应用中处理这些问题。每步的处理逻辑：

1. **路由请求**：`canUseTool` 回调检查工具名是否为 `"AskUserQuestion"` 并路由到专用处理器
2. **展示问题**：处理器遍历 `questions` 数组，打印每个问题及编号选项
3. **收集输入**：用户可以输入数字选择选项，或直接输入自由文本（如 "jquery"、"i don't know"）
4. **映射答案**：代码检查输入是数字（使用选项的 label）还是自由文本（直接使用文本）
5. **返回给 Claude**：响应包含原始 `questions` 数组和 `answers` 映射

将 TypeScript 版本保存为 `ask.ts` 并用 `npx tsx ask.ts` 运行，或将 Python 版本保存为 `ask.py` 并用 `python ask.py` 运行。

```python
import asyncio

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query
from claude_agent_sdk.types import HookMatcher, PermissionResultAllow


def parse_response(response: str, options: list) -> str:
    """将用户输入解析为选项编号或自由文本。"""
    try:
        indices = [int(s.strip()) - 1 for s in response.split(",")]
        labels = [options[i]["label"] for i in indices if 0 <= i < len(options)]
        return ", ".join(labels) if labels else response
    except ValueError:
        return response


async def handle_ask_user_question(input_data: dict) -> PermissionResultAllow:
    """展示 Claude 的问题并收集用户答案。"""
    answers = {}

    for q in input_data.get("questions", []):
        print(f"\n{q['header']}: {q['question']}")

        options = q["options"]
        for i, opt in enumerate(options):
            print(f"  {i + 1}. {opt['label']} - {opt['description']}")
        if q.get("multiSelect"):
            print("  (Enter numbers separated by commas, or type your own answer)")
        else:
            print("  (Enter a number, or type your own answer)")

        response = input("Your choice: ").strip()
        answers[q["question"]] = parse_response(response, options)

    return PermissionResultAllow(
        updated_input={
            "questions": input_data.get("questions", []),
            "answers": answers,
        }
    )


async def can_use_tool(
    tool_name: str, input_data: dict, context
) -> PermissionResultAllow:
    # 将 AskUserQuestion 路由到问题处理器
    if tool_name == "AskUserQuestion":
        return await handle_ask_user_question(input_data)
    # 本示例自动批准其他工具
    return PermissionResultAllow(updated_input=input_data)


async def prompt_stream():
    yield {
        "type": "user",
        "message": {
            "role": "user",
            "content": "Help me decide on the tech stack for a new mobile app",
        },
    }


# 必要的变通：dummy hook 保持流打开以支持 can_use_tool
async def dummy_hook(input_data, tool_use_id, context):
    return {"continue_": True}


async def main():
    async for message in query(
        prompt=prompt_stream(),
        options=ClaudeAgentOptions(
            can_use_tool=can_use_tool,
            hooks={"PreToolUse": [HookMatcher(matcher=None, hooks=[dummy_hook])]},
        ),
    ):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(message.result)


asyncio.run(main())
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";
import * as readline from "readline/promises";

// 辅助函数：在终端提示用户输入
async function prompt(question: string): Promise<string> {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const answer = await rl.question(question);
  rl.close();
  return answer;
}

// 将用户输入解析为选项编号或自由文本
function parseResponse(response: string, options: any[]): string {
  const indices = response.split(",").map((s) => parseInt(s.trim()) - 1);
  const labels = indices
    .filter((i) => !isNaN(i) && i >= 0 && i < options.length)
    .map((i) => options[i].label);
  return labels.length > 0 ? labels.join(", ") : response;
}

// 展示 Claude 的问题并收集用户答案
async function handleAskUserQuestion(input: any) {
  const answers: Record<string, string> = {};

  for (const q of input.questions) {
    console.log(`\n${q.header}: ${q.question}`);

    const options = q.options;
    options.forEach((opt: any, i: number) => {
      console.log(`  ${i + 1}. ${opt.label} - ${opt.description}`);
    });
    if (q.multiSelect) {
      console.log("  (Enter numbers separated by commas, or type your own answer)");
    } else {
      console.log("  (Enter a number, or type your own answer)");
    }

    const response = (await prompt("Your choice: ")).trim();
    answers[q.question] = parseResponse(response, options);
  }

  // 将答案返回给 Claude（必须包含原始 questions）
  return {
    behavior: "allow",
    updatedInput: { questions: input.questions, answers }
  };
}

async function main() {
  for await (const message of query({
    prompt: "Help me decide on the tech stack for a new mobile app",
    options: {
      canUseTool: async (toolName, input) => {
        // 将 AskUserQuestion 路由到问题处理器
        if (toolName === "AskUserQuestion") {
          return handleAskUserQuestion(input);
        }
        // 本示例自动批准其他工具
        return { behavior: "allow", updatedInput: input };
      }
    }
  })) {
    if ("result" in message) console.log(message.result);
  }
}

main();
```

## 限制

* **子代理**：`AskUserQuestion` 目前不可用于通过 Agent 工具生成的子代理
* **问题数量限制**：每次 `AskUserQuestion` 调用支持 1-4 个问题，每个问题 2-4 个选项

## 获取用户输入的其他方式

`canUseTool` 回调和 `AskUserQuestion` 工具覆盖了大多数审批和澄清场景，但 SDK 还提供其他获取用户输入的方式：

### 流式输入

**当需要以下场景时使用[流式输入](https://code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode)：**

* **中途打断 agent**：在 Claude 工作时发送取消信号或改变方向
* **提供额外上下文**：添加 Claude 需要的信息而无需等它主动询问
* **构建聊天界面**：让用户在长时间运行的操作期间发送后续消息

流式输入适合对话式 UI，用户在整个执行过程中与 agent 交互，而不仅仅是在审批检查点。

### 自定义工具

**当需要以下场景时使用[自定义工具](https://code.claude.com/docs/en/agent-sdk/custom-tools)：**

* **收集结构化输入**：构建表单、向导或多步工作流，超出 `AskUserQuestion` 的多选格式
* **集成外部审批系统**：连接已有的工单、工作流或审批平台
* **实现特定领域的交互**：创建适合应用需求的定制工具，如代码审查界面或部署清单

自定义工具给你完全的交互控制，但比使用内置 `canUseTool` 回调需要更多实现工作。

## 相关资源

* [配置权限](https://code.claude.com/docs/en/agent-sdk/permissions)：设置权限模式和规则
* [用 hooks 控制执行](https://code.claude.com/docs/en/agent-sdk/hooks)：在 agent 生命周期的关键点运行自定义代码
* [TypeScript SDK 参考](https://code.claude.com/docs/en/agent-sdk/typescript#canusetool)：完整 canUseTool API 文档
