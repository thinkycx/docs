---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Agent SDK - 迁移指南
description: 从 Claude Code SDK 迁移到 Claude Agent SDK 的完整指南，涵盖 TypeScript 和 Python 项目的迁移步骤、破坏性变更（系统提示默认值、设置源配置等），以及改名原因。
category: translation
tags: [claude-code, agent-sdk, migration, translation]
refs:
  - https://code.claude.com/docs/en/agent-sdk/migration-guide
  - en-source/agent-sdk/migration-guide.md
---

# 迁移到 Claude Agent SDK

> 从 Claude Code TypeScript/Python SDK 迁移到 Claude Agent SDK 的指南

## 概述

**Claude Code SDK 已更名为 Claude Agent SDK，文档结构也做了重组。** 新名称反映了 SDK 的更广泛能力——不只是编码任务，而是构建各类 AI Agent。

## 变更一览

| 方面 | 旧版 | 新版 |
|:---|:---|:---|
| **包名（TS/JS）** | `@anthropic-ai/claude-code` | `@anthropic-ai/claude-agent-sdk` |
| **Python 包名** | `claude-code-sdk` | `claude-agent-sdk` |
| **文档位置** | Claude Code 文档 | API 指南 → Agent SDK 专区 |

> **文档变更说明：** Agent SDK 文档已从 Claude Code 文档站迁移到 API 指南中的独立 [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) 章节。Claude Code 文档现在专注于 CLI 工具和自动化特性。

## 迁移步骤

### TypeScript/JavaScript 项目

**1. 卸载旧包：**

```bash
npm uninstall @anthropic-ai/claude-code
```

**2. 安装新包：**

```bash
npm install @anthropic-ai/claude-agent-sdk
```

**3. 更新 import 语句：**

将所有 `@anthropic-ai/claude-code` 改为 `@anthropic-ai/claude-agent-sdk`：

```typescript
// 旧版
import { query, tool, createSdkMcpServer } from "@anthropic-ai/claude-code";

// 新版
import { query, tool, createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";
```

**4. 更新 package.json 依赖：**

旧版：

```json
{
  "dependencies": {
    "@anthropic-ai/claude-code": "^0.0.42"
  }
}
```

新版：

```json
{
  "dependencies": {
    "@anthropic-ai/claude-agent-sdk": "^0.2.0"
  }
}
```

**5. 检查[破坏性变更](#破坏性变更)**

根据需要调整代码完成迁移。

### Python 项目

**1. 卸载旧包：**

```bash
pip uninstall claude-code-sdk
```

**2. 安装新包：**

```bash
pip install claude-agent-sdk
```

**3. 更新 import 语句：**

将所有 `claude_code_sdk` 改为 `claude_agent_sdk`：

```python
# 旧版
from claude_code_sdk import query, ClaudeCodeOptions

# 新版
from claude_agent_sdk import query, ClaudeAgentOptions
```

**4. 更新类型名称：**

将 `ClaudeCodeOptions` 改为 `ClaudeAgentOptions`：

```python
# 旧版
from claude_code_sdk import query, ClaudeCodeOptions

options = ClaudeCodeOptions(model="claude-opus-4-7")

# 新版
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(model="claude-opus-4-7")
```

**5. 检查[破坏性变更](#破坏性变更)**

根据需要调整代码完成迁移。

## 破坏性变更

> **注意：** 为了改进隔离性和显式配置，Claude Agent SDK v0.1.0 引入了破坏性变更。迁移前请仔细阅读本节。

### Python：ClaudeCodeOptions 重命名为 ClaudeAgentOptions

**变更内容：** Python SDK 类型 `ClaudeCodeOptions` 已重命名为 `ClaudeAgentOptions`。

**迁移方式：**

```python
# 旧版 (claude-code-sdk)
from claude_code_sdk import query, ClaudeCodeOptions

options = ClaudeCodeOptions(model="claude-opus-4-7", permission_mode="acceptEdits")

# 新版 (claude-agent-sdk)
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(model="claude-opus-4-7", permission_mode="acceptEdits")
```

**变更原因：** 类型名称现在与 "Claude Agent SDK" 品牌一致，保持 SDK 命名规范的统一性。

### 系统提示不再默认使用

**变更内容：** SDK 不再默认使用 Claude Code 的系统提示。

**迁移方式：**

TypeScript：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

// 旧版 (v0.0.x) - 默认使用 Claude Code 系统提示
const before = query({ prompt: "Hello" });

// 新版 (v0.1.0) - 默认使用最小系统提示
// 如需恢复旧行为，显式请求 Claude Code 预设：
const presetResult = query({
  prompt: "Hello",
  options: {
    systemPrompt: { type: "preset", preset: "claude_code" }
  }
});

// 或使用自定义系统提示：
const customResult = query({
  prompt: "Hello",
  options: {
    systemPrompt: "You are a helpful coding assistant"
  }
});
```

Python：

```python
# 旧版 (v0.0.x) - 默认使用 Claude Code 系统提示
async for message in query(prompt="Hello"):
    print(message)

# 新版 (v0.1.0) - 默认使用最小系统提示
# 如需恢复旧行为，显式请求 Claude Code 预设：
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt="Hello",
    options=ClaudeAgentOptions(
        system_prompt={"type": "preset", "preset": "claude_code"}  # 使用预设
    ),
):
    print(message)

# 或使用自定义系统提示：
async for message in query(
    prompt="Hello",
    options=ClaudeAgentOptions(system_prompt="You are a helpful coding assistant"),
):
    print(message)
```

**变更原因：** 为 SDK 应用提供更好的控制和隔离性。现在可以构建具有自定义行为的 Agent，无需继承 Claude Code CLI 专用的指令。

### 设置源默认值

**此默认值在 v0.1.0 中曾短暂修改，随后被恢复，无需迁移操作。**

**当前行为：** 在 `query()` 中省略 `settingSources` 会加载用户、项目和本地文件系统设置，与 CLI 行为一致。包括 `~/.claude/settings.json`、`.claude/settings.json`、`.claude/settings.local.json`、CLAUDE.md 文件和自定义命令。

如需完全隔离运行（不加载文件系统设置），传入空数组：

TypeScript：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

const isolatedResult = query({
  prompt: "Hello",
  options: {
    settingSources: [] // 不加载文件系统设置
  }
});

// 或只加载特定来源：
const projectOnlyResult = query({
  prompt: "Hello",
  options: {
    settingSources: ["project"] // 仅加载项目设置
  }
});
```

Python：

```python
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt="Hello",
    options=ClaudeAgentOptions(setting_sources=[]),  # 不加载文件系统设置
):
    print(message)

# 或只加载特定来源：
async for message in query(
    prompt="Hello",
    options=ClaudeAgentOptions(
        setting_sources=["project"]  # 仅加载项目设置
    ),
):
    print(message)
```

**隔离性在以下场景尤为重要：** CI/CD 流水线、已部署应用、测试环境、多租户系统——这些场景中本地自定义配置不应泄漏进来。

> **注意：** SDK v0.1.0 曾短暂默认不加载任何设置，后续版本已恢复。Python SDK 0.1.59 及更早版本中，空列表与省略选项等效，因此请先升级再依赖 `setting_sources=[]`。关于 `settingSources` 无法控制的输入，参见 [settingSources 不控制的内容](https://code.claude.com/docs/en/agent-sdk/claude-code-features#what-settingsources-does-not-control)。

## 为什么改名？

**Claude Code SDK 最初为编码任务设计，但已演变为构建各类 AI Agent 的强大框架。** 新名称 "Claude Agent SDK" 更准确地反映其能力：

* 构建业务 Agent（法律助手、金融顾问、客户支持）
* 创建专业编码 Agent（SRE 机器人、安全审查员、代码审查 Agent）
* 开发任意领域的自定义 Agent，支持工具调用、MCP 集成等

## 常见问题排查

**TypeScript/JavaScript：**

1. 确保所有 import 已更新为 `@anthropic-ai/claude-agent-sdk`
2. 确认 package.json 中使用了新包名
3. 运行 `npm install` 确保依赖已更新

**Python：**

1. 确保所有 import 已更新为 `claude_agent_sdk`
2. 确认 requirements.txt 或 pyproject.toml 中使用了新包名
3. 运行 `pip install claude-agent-sdk` 确保包已安装

## 后续步骤

* 浏览 [Agent SDK 概览](https://code.claude.com/docs/en/agent-sdk/overview) 了解可用功能
* 查看 [TypeScript SDK 参考](https://code.claude.com/docs/en/agent-sdk/typescript) 获取详细 API 文档
* 查看 [Python SDK 参考](https://code.claude.com/docs/en/agent-sdk/python) 获取 Python 专属文档
* 了解[自定义工具](https://code.claude.com/docs/en/agent-sdk/custom-tools)和 [MCP 集成](https://code.claude.com/docs/en/agent-sdk/mcp)
