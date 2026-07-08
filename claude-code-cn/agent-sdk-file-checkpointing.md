---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Agent SDK - 文件检查点
description: Claude Agent SDK 文件检查点机制，追踪 Write/Edit/NotebookEdit 工具的文件修改，支持回退到任意历史状态，涵盖启用方式、UUID 捕获、回退操作和常见故障排除。
category: translation
tags: [claude-code, agent-sdk, translation]
refs:
  - https://code.claude.com/docs/en/agent-sdk/file-checkpointing
  - en-source/agent-sdk/file-checkpointing.md
---

# 文件检查点：回退文件变更

> 在 agent 会话中追踪文件修改并将文件恢复到任意历史状态。

**文件检查点追踪通过 Write、Edit 和 NotebookEdit 工具进行的文件修改，允许你将文件回退到任意历史状态。** 想快速体验？跳转到[交互式示例](#交互式体验)。

通过检查点，你可以：

* **撤销不想要的更改**——将文件恢复到已知的正确状态
* **探索替代方案**——恢复到检查点后尝试不同方案
* **从错误中恢复**——当 agent 做出错误修改时

> **注意：只有通过 Write、Edit 和 NotebookEdit 工具进行的更改会被追踪。通过 Bash 命令（如 `echo > file.txt` 或 `sed -i`）进行的更改不会被检查点系统捕获。**

## 检查点工作原理

**启用文件检查点后，SDK 在通过 Write、Edit 或 NotebookEdit 工具修改文件前创建备份。** 响应流中的用户消息包含一个检查点 UUID，可用作恢复点。

检查点配合以下 agent 修改文件的内置工具使用：

| 工具 | 说明 |
|:---|:---|
| Write | 创建新文件或用新内容覆盖已有文件 |
| Edit | 对已有文件的特定部分做定向编辑 |
| NotebookEdit | 修改 Jupyter notebook（`.ipynb` 文件）中的 cell |

> **文件回退恢复磁盘上的文件到之前的状态。** 它不会回退对话本身。调用 `rewindFiles()`（TypeScript）或 `rewind_files()`（Python）后，对话历史和上下文保持不变。

检查点系统追踪：

* 会话期间创建的文件
* 会话期间修改的文件
* 被修改文件的原始内容

回退到某个检查点时，创建的文件被删除，修改的文件恢复到该时间点的内容。

## 实现检查点

**要使用文件检查点，在选项中启用它，从响应流捕获检查点 UUID，然后在需要恢复时调用 `rewindFiles()`（TypeScript）或 `rewind_files()`（Python）。**

以下示例展示完整流程：启用检查点、从响应流捕获检查点 UUID 和 session ID，然后稍后恢复会话以回退文件。每步在下方详细说明。示例使用提示"Refactor the authentication module"。在包含认证模块的项目中运行它们，或更改提示以指定项目中存在的文件，这样你可以观察文件变化并看到回退恢复它们。

```python
import asyncio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    UserMessage,
    ResultMessage,
)


async def main():
    # 步骤 1：启用检查点
    options = ClaudeAgentOptions(
        enable_file_checkpointing=True,
        permission_mode="acceptEdits",  # 自动接受文件编辑无需提示
        extra_args={
            "replay-user-messages": None
        },  # 必需：在响应流中接收检查点 UUID
    )

    checkpoint_id = None
    session_id = None

    # 运行查询并捕获检查点 UUID 和 session ID
    async with ClaudeSDKClient(options) as client:
        await client.query("Refactor the authentication module")

        # 步骤 2：从第一条用户消息捕获检查点 UUID
        async for message in client.receive_response():
            if isinstance(message, UserMessage) and message.uuid and not checkpoint_id:
                checkpoint_id = message.uuid
            if isinstance(message, ResultMessage) and not session_id:
                session_id = message.session_id

    # 步骤 3：稍后，通过恢复会话并发送空提示来回退
    if checkpoint_id and session_id:
        async with ClaudeSDKClient(
            ClaudeAgentOptions(enable_file_checkpointing=True, resume=session_id)
        ) as client:
            await client.query("")  # 空提示打开连接
            async for message in client.receive_response():
                await client.rewind_files(checkpoint_id)
                break
        print(f"Rewound to checkpoint: {checkpoint_id}")


asyncio.run(main())
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

async function main() {
  // 步骤 1：启用检查点
  const opts = {
    enableFileCheckpointing: true,
    permissionMode: "acceptEdits" as const, // 自动接受文件编辑无需提示
    extraArgs: { "replay-user-messages": null } // 必需：在响应流中接收检查点 UUID
  };

  const response = query({
    prompt: "Refactor the authentication module",
    options: opts
  });

  let checkpointId: string | undefined;
  let sessionId: string | undefined;

  // 步骤 2：从第一条用户消息捕获检查点 UUID
  for await (const message of response) {
    if (message.type === "user" && message.uuid && !checkpointId) {
      checkpointId = message.uuid;
    }
    if ("session_id" in message && !sessionId) {
      sessionId = message.session_id;
    }
  }

  // 步骤 3：稍后，通过恢复会话并发送空提示来回退
  if (checkpointId && sessionId) {
    const rewindQuery = query({
      prompt: "", // 空提示打开连接
      options: { ...opts, resume: sessionId }
    });

    for await (const msg of rewindQuery) {
      await rewindQuery.rewindFiles(checkpointId);
      break;
    }
    console.log(`Rewound to checkpoint: ${checkpointId}`);
  }
}

main();
```

### 步骤详解

#### 步骤 1：启用检查点

**配置 SDK 选项以启用检查点并接收检查点 UUID：**

| 选项 | Python | TypeScript | 说明 |
|:---|:---|:---|:---|
| 启用检查点 | `enable_file_checkpointing=True` | `enableFileCheckpointing: true` | 追踪文件变更以支持回退 |
| 接收检查点 UUID | `extra_args={"replay-user-messages": None}` | `extraArgs: { 'replay-user-messages': null }` | 必需：在流中获取用户消息 UUID |

```python
options = ClaudeAgentOptions(
    enable_file_checkpointing=True,
    permission_mode="acceptEdits",
    extra_args={"replay-user-messages": None},
)

async with ClaudeSDKClient(options) as client:
    await client.query("Refactor the authentication module")
```

```typescript
const response = query({
  prompt: "Refactor the authentication module",
  options: {
    enableFileCheckpointing: true,
    permissionMode: "acceptEdits" as const,
    extraArgs: { "replay-user-messages": null }
  }
});
```

#### 步骤 2：捕获检查点 UUID 和 session ID

**设置 `replay-user-messages` 选项后（如上），响应流中的每条用户消息都有一个作为检查点的 UUID。**

大多数场景下，捕获第一条用户消息的 UUID（`message.uuid`）即可；回退到它会将所有文件恢复到原始状态。要存储多个检查点并回退到中间状态，参见[多恢复点](#多恢复点)。

捕获 session ID（`message.session_id`）是可选的；只有在流完成后想稍后回退时才需要。如果在处理消息期间立即调用 `rewindFiles()`（如[危险操作前建立检查点](#危险操作前建立检查点)中的示例），可以跳过捕获 session ID。

```python
checkpoint_id = None
session_id = None

async for message in client.receive_response():
    # 捕获第一条用户消息 UUID 作为检查点
    if isinstance(message, UserMessage) and message.uuid and checkpoint_id is None:
        checkpoint_id = message.uuid
    # 从 result 消息捕获 session ID
    if isinstance(message, ResultMessage):
        session_id = message.session_id
```

```typescript
let checkpointId: string | undefined;
let sessionId: string | undefined;

for await (const message of response) {
  // 捕获第一条用户消息 UUID 作为检查点
  if (message.type === "user" && message.uuid && !checkpointId) {
    checkpointId = message.uuid;
  }
  // 从任何包含 session_id 的消息中捕获
  if ("session_id" in message) {
    sessionId = message.session_id;
  }
}
```

#### 步骤 3：回退文件

**流完成后要回退，用空提示恢复会话并调用 `rewind_files()`（Python）或 `rewindFiles()`（TypeScript）传入检查点 UUID。** 也可以在流处理期间回退；参见[危险操作前建立检查点](#危险操作前建立检查点)了解该模式。

```python
async with ClaudeSDKClient(
    ClaudeAgentOptions(enable_file_checkpointing=True, resume=session_id)
) as client:
    await client.query("")  # 空提示打开连接
    async for message in client.receive_response():
        await client.rewind_files(checkpoint_id)
        break
```

```typescript
const rewindQuery = query({
  prompt: "", // 空提示打开连接
  options: { ...opts, resume: sessionId }
});

for await (const msg of rewindQuery) {
  await rewindQuery.rewindFiles(checkpointId);
  break;
}
```

如果捕获了 session ID 和检查点 ID，也可以从 CLI 回退。此命令需要 `claude` 可执行文件，来自[安装 Claude Code](https://code.claude.com/docs/en/setup)，SDK 包不安装它。SDK 会自动为你启用检查点，但直接运行 `claude -p` 时必须设置 `CLAUDE_CODE_ENABLE_SDK_FILE_CHECKPOINTING` 环境变量：

```bash
CLAUDE_CODE_ENABLE_SDK_FILE_CHECKPOINTING=true claude -p --resume <session-id> --rewind-files <checkpoint-uuid>
```

`--rewind-files` 标志不出现在 `claude --help` 输出中，但 CLI 按如上方式接受它。

## 常见模式

以下模式展示根据不同场景捕获和使用检查点 UUID 的方式。

### 危险操作前建立检查点

**此模式只保留最新的检查点 UUID，在每个 agent 轮次前更新。** 如果处理期间出现问题，可以立即回退到最后安全状态并跳出循环。

运行此示例前，将 `your_revert_condition`（Python）或 `yourRevertCondition`（TypeScript）替换为你自己的检查逻辑，如错误检测或验证失败；示例中未定义占位符。

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, UserMessage


async def main():
    options = ClaudeAgentOptions(
        enable_file_checkpointing=True,
        permission_mode="acceptEdits",
        extra_args={"replay-user-messages": None},
    )

    safe_checkpoint = None

    async with ClaudeSDKClient(options) as client:
        await client.query("Refactor the authentication module")

        async for message in client.receive_response():
            # 在每个 agent 轮次开始前更新检查点
            # 覆盖前一个检查点。只保留最新的
            if isinstance(message, UserMessage) and message.uuid:
                safe_checkpoint = message.uuid

            # 根据你自己的逻辑决定何时回退
            # 例如：错误检测、验证失败或用户输入
            if your_revert_condition and safe_checkpoint:
                await client.rewind_files(safe_checkpoint)
                # 回退后退出循环，文件已恢复
                break


asyncio.run(main())
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

async function main() {
  const response = query({
    prompt: "Refactor the authentication module",
    options: {
      enableFileCheckpointing: true,
      permissionMode: "acceptEdits" as const,
      extraArgs: { "replay-user-messages": null }
    }
  });

  let safeCheckpoint: string | undefined;

  for await (const message of response) {
    // 在每个 agent 轮次开始前更新检查点
    // 覆盖前一个检查点。只保留最新的
    if (message.type === "user" && message.uuid) {
      safeCheckpoint = message.uuid;
    }

    // 根据你自己的逻辑决定何时回退
    // 例如：错误检测、验证失败或用户输入
    if (yourRevertCondition && safeCheckpoint) {
      await response.rewindFiles(safeCheckpoint);
      // 回退后退出循环，文件已恢复
      break;
    }
  }
}

main();
```

### 多恢复点

**如果 Claude 跨多个轮次做了修改，你可能想回退到特定点而不是最开始。** 例如，Claude 在第一轮重构文件、第二轮添加测试，你可能想保留重构但撤销测试。

此模式将所有检查点 UUID 存储在带元数据的数组中。会话完成后，可以回退到任意历史检查点：

```python
import asyncio
from dataclasses import dataclass
from datetime import datetime
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    UserMessage,
    ResultMessage,
)


# 存储检查点元数据以便追踪
@dataclass
class Checkpoint:
    id: str
    description: str
    timestamp: datetime


async def main():
    options = ClaudeAgentOptions(
        enable_file_checkpointing=True,
        permission_mode="acceptEdits",
        extra_args={"replay-user-messages": None},
    )

    checkpoints = []
    session_id = None

    async with ClaudeSDKClient(options) as client:
        await client.query("Refactor the authentication module")

        async for message in client.receive_response():
            if isinstance(message, UserMessage) and message.uuid:
                checkpoints.append(
                    Checkpoint(
                        id=message.uuid,
                        description=f"After turn {len(checkpoints) + 1}",
                        timestamp=datetime.now(),
                    )
                )
            if isinstance(message, ResultMessage) and not session_id:
                session_id = message.session_id

    # 稍后：通过恢复会话回退到任意检查点
    if checkpoints and session_id:
        target = checkpoints[0]  # 选择任意检查点
        async with ClaudeSDKClient(
            ClaudeAgentOptions(enable_file_checkpointing=True, resume=session_id)
        ) as client:
            await client.query("")  # 空提示打开连接
            async for message in client.receive_response():
                await client.rewind_files(target.id)
                break
        print(f"Rewound to: {target.description}")


asyncio.run(main())
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

// 存储检查点元数据以便追踪
interface Checkpoint {
  id: string;
  description: string;
  timestamp: Date;
}

async function main() {
  const opts = {
    enableFileCheckpointing: true,
    permissionMode: "acceptEdits" as const,
    extraArgs: { "replay-user-messages": null }
  };

  const response = query({
    prompt: "Refactor the authentication module",
    options: opts
  });

  const checkpoints: Checkpoint[] = [];
  let sessionId: string | undefined;

  for await (const message of response) {
    if (message.type === "user" && message.uuid) {
      checkpoints.push({
        id: message.uuid,
        description: `After turn ${checkpoints.length + 1}`,
        timestamp: new Date()
      });
    }
    if ("session_id" in message && !sessionId) {
      sessionId = message.session_id;
    }
  }

  // 稍后：通过恢复会话回退到任意检查点
  if (checkpoints.length > 0 && sessionId) {
    const target = checkpoints[0]; // 选择任意检查点
    const rewindQuery = query({
      prompt: "", // 空提示打开连接
      options: { ...opts, resume: sessionId }
    });

    for await (const msg of rewindQuery) {
      await rewindQuery.rewindFiles(target.id);
      break;
    }
    console.log(`Rewound to: ${target.description}`);
  }
}

main();
```

## 交互式体验

**这个完整示例创建一个小工具文件，让 agent 添加文档注释，展示变更，然后询问你是否要回退。**

开始前，确保已[安装 Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/quickstart)。

### 步骤 1：创建测试文件

创建一个名为 `utils.py`（Python）或 `utils.ts`（TypeScript）的新文件并粘贴以下代码：

```python
# utils.py
def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

```typescript
// utils.ts
export function add(a: number, b: number): number {
  return a + b;
}

export function subtract(a: number, b: number): number {
  return a - b;
}

export function multiply(a: number, b: number): number {
  return a * b;
}

export function divide(a: number, b: number): number {
  if (b === 0) {
    throw new Error("Cannot divide by zero");
  }
  return a / b;
}
```

### 步骤 2：运行交互式示例

在与工具文件相同的目录下创建 `try_checkpointing.py`（Python）或 `try_checkpointing.ts`（TypeScript），粘贴以下代码。

此脚本要求 Claude 给你的工具文件添加文档注释，然后让你选择是否回退恢复原始文件。

```python
# try_checkpointing.py
import asyncio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    UserMessage,
    ResultMessage,
)


async def main():
    # 配置 SDK 并启用检查点
    # - enable_file_checkpointing：追踪文件变更以支持回退
    # - permission_mode：自动接受文件编辑无需提示
    # - extra_args：必需，在流中接收用户消息 UUID
    options = ClaudeAgentOptions(
        enable_file_checkpointing=True,
        permission_mode="acceptEdits",
        extra_args={"replay-user-messages": None},
    )

    checkpoint_id = None  # 存储用户消息 UUID 用于回退
    session_id = None  # 存储 session ID 用于恢复

    print("Running agent to add doc comments to utils.py...\n")

    # 运行 agent 并从响应流捕获检查点数据
    async with ClaudeSDKClient(options) as client:
        await client.query("Add doc comments to utils.py")

        async for message in client.receive_response():
            # 捕获第一条用户消息 UUID——这是我们的恢复点
            if isinstance(message, UserMessage) and message.uuid and not checkpoint_id:
                checkpoint_id = message.uuid
            # 捕获 session ID 以便稍后恢复
            if isinstance(message, ResultMessage):
                session_id = message.session_id

    print("Done! Open utils.py to see the added doc comments.\n")

    # 询问用户是否要回退变更
    if checkpoint_id and session_id:
        response = input("Rewind to remove the doc comments? (y/n): ")

        if response.lower() == "y":
            # 用空提示恢复会话，然后回退
            async with ClaudeSDKClient(
                ClaudeAgentOptions(enable_file_checkpointing=True, resume=session_id)
            ) as client:
                await client.query("")  # 空提示打开连接
                async for message in client.receive_response():
                    await client.rewind_files(checkpoint_id)  # 恢复文件
                    break

            print("\nFile restored! Open utils.py to verify the doc comments are gone.")
        else:
            print("\nKept the modified file.")


asyncio.run(main())
```

```typescript
// try_checkpointing.ts
import { query } from "@anthropic-ai/claude-agent-sdk";
import * as readline from "readline";

async function main() {
  // 配置 SDK 并启用检查点
  // - enableFileCheckpointing：追踪文件变更以支持回退
  // - permissionMode：自动接受文件编辑无需提示
  // - extraArgs：必需，在流中接收用户消息 UUID
  const opts = {
    enableFileCheckpointing: true,
    permissionMode: "acceptEdits" as const,
    extraArgs: { "replay-user-messages": null }
  };

  let sessionId: string | undefined; // 存储 session ID 用于恢复
  let checkpointId: string | undefined; // 存储用户消息 UUID 用于回退

  console.log("Running agent to add doc comments to utils.ts...\n");

  // 运行 agent 并从响应流捕获检查点数据
  const response = query({
    prompt: "Add doc comments to utils.ts",
    options: opts
  });

  for await (const message of response) {
    // 捕获第一条用户消息 UUID——这是我们的恢复点
    if (message.type === "user" && message.uuid && !checkpointId) {
      checkpointId = message.uuid;
    }
    // 捕获 session ID 以便稍后恢复
    if ("session_id" in message) {
      sessionId = message.session_id;
    }
  }

  console.log("Done! Open utils.ts to see the added doc comments.\n");

  // 询问用户是否要回退变更
  if (checkpointId && sessionId) {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    const answer = await new Promise<string>((resolve) => {
      rl.question("Rewind to remove the doc comments? (y/n): ", resolve);
    });
    rl.close();

    if (answer.toLowerCase() === "y") {
      // 用空提示恢复会话，然后回退
      const rewindQuery = query({
        prompt: "", // 空提示打开连接
        options: { ...opts, resume: sessionId }
      });

      for await (const msg of rewindQuery) {
        await rewindQuery.rewindFiles(checkpointId); // 恢复文件
        break;
      }

      console.log("\nFile restored! Open utils.ts to verify the doc comments are gone.");
    } else {
      console.log("\nKept the modified file.");
    }
  }
}

main();
```

此示例演示完整的检查点工作流：

1. **启用检查点**：配置 SDK，设置 `enable_file_checkpointing=True` 和 `permission_mode="acceptEdits"` 自动批准文件编辑
2. **捕获检查点数据**：agent 运行时，存储第一条用户消息 UUID（恢复点）和 session ID
3. **提示回退**：agent 完成后，检查工具文件看文档注释，然后决定是否撤销更改
4. **恢复并回退**：如果是，用空提示恢复会话并调用 `rewind_files()` 恢复原始文件

### 步骤 3：运行示例

在与工具文件相同的目录下运行脚本。

> **提示：** 运行脚本前在 IDE 或编辑器中打开工具文件（`utils.py` 或 `utils.ts`）。你会看到文件在 agent 添加文档注释时实时更新，然后在选择回退时恢复原样。

```bash
# Python
python try_checkpointing.py

# TypeScript
npx tsx try_checkpointing.ts
```

你会看到 agent 添加文档注释，然后一个提示询问是否回退。选择"是"则文件恢复到原始状态。

## 限制

| 限制 | 说明 |
|:---|:---|
| 仅 Write/Edit/NotebookEdit 工具 | 通过 Bash 命令进行的更改不被追踪 |
| 同一会话 | 检查点绑定到创建它们的会话 |
| 仅文件内容 | 创建、移动或删除目录不会被回退撤销 |
| 本地文件 | 远程或网络文件不被追踪 |

## 故障排除

### 检查点选项不被识别

如果 `enableFileCheckpointing` 或 `rewindFiles()` 不可用，可能使用了旧版 SDK。

**解决方案**：更新到最新 SDK 版本：

* **Python**：`pip install --upgrade claude-agent-sdk`
* **TypeScript**：`npm install @anthropic-ai/claude-agent-sdk@latest`

### 用户消息没有 UUID

如果 `message.uuid` 是 `undefined` 或缺失，说明没有接收到检查点 UUID。

**原因**：`replay-user-messages` 选项未设置。

**解决方案**：在选项中添加 `extra_args={"replay-user-messages": None}`（Python）或 `extraArgs: { 'replay-user-messages': null }`（TypeScript）。

### "No file checkpoint found for message" 错误

此错误在指定的用户消息 UUID 没有对应的检查点数据时发生。

**常见原因**：

* 原始会话未启用文件检查点（`enable_file_checkpointing` 或 `enableFileCheckpointing` 未设为 `true`）
* 尝试恢复和回退之前，会话未正确完成

**解决方案**：确保原始会话设置了 `enable_file_checkpointing=True`（Python）或 `enableFileCheckpointing: true`（TypeScript），然后使用示例中展示的模式：捕获第一条用户消息 UUID，完整完成会话，然后用空提示恢复并调用一次 `rewindFiles()`。

### "File rewinding is not enabled" 错误

**此错误在未启用检查点的情况下尝试非交互式回退时发生：** 裸运行 `claude -p` 加 `--rewind-files`，或运行一个选项中未启用检查点的 SDK 会话（包括恢复的会话）。SDK 仅在 `enable_file_checkpointing`（Python）或 `enableFileCheckpointing`（TypeScript）在执行回退的会话上启用时才内部设置 `CLAUDE_CODE_ENABLE_SDK_FILE_CHECKPOINTING` 环境变量；裸 CLI 从不设置它。

**解决方案**：对于裸 CLI，在运行命令时设置环境变量：

```bash
CLAUDE_CODE_ENABLE_SDK_FILE_CHECKPOINTING=true claude -p --resume <session-id> --rewind-files <checkpoint-uuid>
```

对于 SDK，在恢复的会话上设置 `enable_file_checkpointing=True`（Python）或 `enableFileCheckpointing: true`（TypeScript），如本页示例所示。

### "ProcessTransport is not ready for writing" 错误

此错误在遍历完响应后调用 `rewindFiles()` 或 `rewind_files()` 时发生。循环完成后与 CLI 进程的连接关闭。

**解决方案**：用空提示恢复会话，然后在新 query 上调用 rewind：

```python
# 用空提示恢复会话，然后回退
async with ClaudeSDKClient(
    ClaudeAgentOptions(enable_file_checkpointing=True, resume=session_id)
) as client:
    await client.query("")
    async for message in client.receive_response():
        await client.rewind_files(checkpoint_id)
        break
```

```typescript
// 用空提示恢复会话，然后回退
const rewindQuery = query({
  prompt: "",
  options: { ...opts, resume: sessionId }
});

for await (const msg of rewindQuery) {
  await rewindQuery.rewindFiles(checkpointId);
  break;
}
```

## 下一步

* **[会话](https://code.claude.com/docs/en/agent-sdk/sessions)**：了解如何恢复会话（流完成后回退的前提）。涵盖 session ID、恢复对话和会话分叉。
* **[权限](https://code.claude.com/docs/en/agent-sdk/permissions)**：配置 Claude 可以使用哪些工具以及文件修改如何被审批。适用于想更精细控制编辑时机的场景。
* **[TypeScript SDK 参考](https://code.claude.com/docs/en/agent-sdk/typescript)**：完整 API 参考，包括 `query()` 的所有选项和 `rewindFiles()` 方法。
* **[Python SDK 参考](https://code.claude.com/docs/en/agent-sdk/python)**：完整 API 参考，包括 `ClaudeAgentOptions` 的所有选项和 `rewind_files()` 方法。
