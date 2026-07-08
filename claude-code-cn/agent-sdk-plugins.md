---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Agent SDK - 插件
description: 通过 Agent SDK 加载自定义插件，为 Claude Code 扩展 Skills、Agents、Hooks 和 MCP 服务器。涵盖插件加载、命名空间使用、目录结构和常见问题排查。
category: translation
tags: [claude-code, agent-sdk, plugins, translation]
refs:
  - https://code.claude.com/docs/en/agent-sdk/plugins
  - en-source/agent-sdk/plugins.md
---

# SDK 中的插件

> 通过 Agent SDK 加载自定义插件，为 Claude Code 扩展 Skills、Agents、Hooks 和 MCP 服务器

**插件可以为 Claude Code 添加自定义功能，方便跨项目共享。** 通过 Agent SDK，你可以从本地目录以编程方式加载插件，为 Agent 会话添加 Skills、Agents、Hooks 和 MCP 服务器。

## 什么是插件？

**插件是 Claude Code 扩展的打包形式，可以包含以下组件：**

* **Skills**：模型自主调用的能力（也可通过 `/skill-name` 手动调用）
* **Agents**：面向特定任务的专用子代理
* **Hooks**：响应工具调用和其他事件的事件处理器
* **MCP 服务器**：通过 Model Context Protocol 集成的外部工具

> **注意：** `commands/` 目录是旧格式，新插件请使用 `skills/`。Claude Code 继续支持两种格式以保持向后兼容。

关于插件结构和创建方式的完整信息，参见 [插件](https://code.claude.com/docs/en/plugins)。

## 加载插件

**在选项配置中提供插件的本地文件系统路径即可加载。** `type` 字段必须为 `"local"`，这是 SDK 接受的唯一值。如果要使用通过[市场](https://code.claude.com/docs/en/plugin-marketplaces)或远程仓库分发的插件，需先下载到本地再提供路径。SDK 支持同时从不同位置加载多个插件。

TypeScript：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Hello",
  options: {
    plugins: [
      { type: "local", path: "./my-plugin" },
      { type: "local", path: "/absolute/path/to/another-plugin" }
    ]
  }
})) {
  // 插件的命令、代理等功能现已可用
}
```

Python：

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    async for message in query(
        prompt="Hello",
        options=ClaudeAgentOptions(
            plugins=[
                {"type": "local", "path": "./my-plugin"},
                {"type": "local", "path": "/absolute/path/to/another-plugin"},
            ]
        ),
    ):
        # 插件的命令、代理等功能现已可用
        pass


asyncio.run(main())
```

### 路径规范

**插件路径支持两种形式：**

| 路径类型 | 说明 | 示例 |
|:---|:---|:---|
| 相对路径 | 相对于当前工作目录解析 | `"./plugins/my-plugin"` |
| 绝对路径 | 完整文件系统路径 | `"/home/user/plugins/my-plugin"` |

> **注意：** 路径应指向插件的根目录——即 `skills/`、`agents/`、`hooks/`、`commands/`（旧版）或 `.claude-plugin/` 的父目录，而非子目录。

## 验证插件安装

**插件成功加载后会出现在系统初始化消息中。** 可以这样验证插件是否可用：

TypeScript：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Hello",
  options: {
    plugins: [{ type: "local", path: "./my-plugin" }]
  }
})) {
  if (message.type === "system" && message.subtype === "init") {
    // 检查已加载的插件
    console.log("Plugins:", message.plugins);
    // 示例: [{ name: "my-plugin", path: "./my-plugin" }]

    // 插件 Skills 带有插件名前缀
    console.log("Skills:", message.skills);
    // 示例: ["my-plugin:greet"]

    // 插件命令使用相同前缀，Skills 也会出现在这里
    console.log("Commands:", message.slash_commands);
    // 示例: ["compact", "context", "my-plugin:custom-command", "my-plugin:greet"]
  }
}
```

Python：

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, SystemMessage


async def main():
    async for message in query(
        prompt="Hello",
        options=ClaudeAgentOptions(
            plugins=[{"type": "local", "path": "./my-plugin"}]
        ),
    ):
        if isinstance(message, SystemMessage) and message.subtype == "init":
            # 检查已加载的插件
            print("Plugins:", message.data.get("plugins"))
            # 示例: [{"name": "my-plugin", "path": "./my-plugin"}]

            # 插件 Skills 带有插件名前缀
            print("Skills:", message.data.get("skills"))
            # 示例: ["my-plugin:greet"]

            # 插件命令使用相同前缀，Skills 也会出现在这里
            print("Commands:", message.data.get("slash_commands"))
            # 示例: ["compact", "context", "my-plugin:custom-command", "my-plugin:greet"]


asyncio.run(main())
```

## 使用插件 Skills

**插件中的 Skills 会自动以插件名作为命名空间，避免冲突。** 要直接调用某个 Skill，发送 `/plugin-name:skill-name` 作为 prompt。

TypeScript：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

// 加载含有自定义 /greet skill 的插件
for await (const message of query({
  prompt: "/my-plugin:greet", // 使用命名空间调用插件 skill
  options: {
    plugins: [{ type: "local", path: "./my-plugin" }]
  }
})) {
  // Claude 执行插件中的自定义问候 skill
  if (message.type === "assistant") {
    console.log(message.message.content);
  }
}
```

Python：

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock


async def main():
    # 加载含有自定义 /greet skill 的插件
    async for message in query(
        prompt="/demo-plugin:greet",  # 使用命名空间调用插件 skill
        options=ClaudeAgentOptions(
            plugins=[{"type": "local", "path": "./plugins/demo-plugin"}]
        ),
    ):
        # Claude 执行插件中的自定义问候 skill
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")


asyncio.run(main())
```

> **提示：** 如果你通过 CLI 安装了插件（例如 `/plugin install my-plugin@marketplace`），仍可在 SDK 中通过提供安装路径来使用它。CLI 安装的插件路径在 `~/.claude/plugins/`。

## 完整示例

**以下是演示插件加载和使用的完整示例：**

TypeScript：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";
import * as path from "path";

async function runWithPlugin() {
  const pluginPath = path.join(__dirname, "plugins", "my-plugin");

  console.log("Loading plugin from:", pluginPath);

  for await (const message of query({
    prompt: "What custom commands do you have available?",
    options: {
      plugins: [{ type: "local", path: pluginPath }],
      maxTurns: 3
    }
  })) {
    if (message.type === "system" && message.subtype === "init") {
      console.log("Loaded plugins:", message.plugins);
      console.log("Available skills:", message.skills);
      console.log("Available commands:", message.slash_commands);
    }

    if (message.type === "assistant") {
      console.log("Assistant:", message.message.content);
    }
  }
}

runWithPlugin().catch(console.error);
```

Python：

```python
#!/usr/bin/env python3
"""演示如何在 Agent SDK 中使用插件。"""

from pathlib import Path
import anyio
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    SystemMessage,
    TextBlock,
    query,
)


async def run_with_plugin():
    """使用自定义插件的示例。"""
    plugin_path = Path(__file__).parent / "plugins" / "demo-plugin"

    print(f"Loading plugin from: {plugin_path}")

    options = ClaudeAgentOptions(
        plugins=[{"type": "local", "path": str(plugin_path)}],
        max_turns=3,
    )

    async for message in query(
        prompt="What custom commands do you have available?", options=options
    ):
        if isinstance(message, SystemMessage) and message.subtype == "init":
            print(f"Loaded plugins: {message.data.get('plugins')}")
            print(f"Available skills: {message.data.get('skills')}")
            print(f"Available commands: {message.data.get('slash_commands')}")

        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Assistant: {block.text}")


if __name__ == "__main__":
    anyio.run(run_with_plugin)
```

## 插件目录结构参考

**插件目录通常包含 `.claude-plugin/plugin.json` 清单文件。** 清单是可选的——省略时 Claude Code 会从目录布局自动发现组件。目录可以包含：

```text
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # 插件清单（可选，省略时自动发现组件）
├── skills/                   # Agent Skills（自主调用或通过 /skill-name）
│   └── my-skill/
│       └── SKILL.md
├── commands/                 # 旧版：请改用 skills/
│   └── custom-cmd.md
├── agents/                   # 自定义代理
│   └── specialist.md
├── hooks/                    # 事件处理器
│   └── hooks.json
└── .mcp.json                # MCP 服务器定义
```

关于创建插件的详细信息，参见：

* [插件](https://code.claude.com/docs/en/plugins) - 完整的插件开发指南
* [插件参考](https://code.claude.com/docs/en/plugins-reference) - 技术规范和 Schema

## 常见用例

### 开发和测试

**在开发期间加载插件，无需全局安装：**

```typescript
plugins: [{ type: "local", path: "./dev-plugins/my-plugin" }];
```

### 项目专属扩展

**将插件包含在项目仓库中，确保团队一致性：**

```typescript
plugins: [{ type: "local", path: "./project-plugins/team-workflows" }];
```

### 多插件来源

**从不同位置组合加载插件：**

```typescript
plugins: [
  { type: "local", path: "./local-plugin" },
  { type: "local", path: "~/.claude/custom-plugins/shared-plugin" }
];
```

## 故障排查

### 插件未加载

**如果插件没有出现在 init 消息中：**

1. **检查路径**：确保路径指向插件根目录——即 `skills/`、`agents/`、`hooks/`、`commands/`（旧版）或 `.claude-plugin/` 的父目录
2. **验证 plugin.json**：如果插件包含清单，确保 JSON 语法有效
3. **检查文件权限**：确保插件目录可读

### Skills 未出现

**如果插件 Skills 不起作用：**

1. **使用命名空间**：以 `/plugin-name:skill-name` 形式调用插件 Skills
2. **检查 init 消息**：确认 Skill 出现在 `skills` 列表中且命名空间正确
3. **验证 Skill 文件**：确保每个 Skill 在 `skills/` 下有自己的子目录并包含 `SKILL.md`，例如 `skills/my-skill/SKILL.md`

### 路径解析问题

**如果相对路径不起作用：**

1. **检查工作目录**：相对路径从当前工作目录解析
2. **使用绝对路径**：为确保可靠性，考虑使用绝对路径
3. **规范化路径**：使用路径工具库正确构造路径

## 相关文档

* [插件](https://code.claude.com/docs/en/plugins) - 完整插件开发指南
* [插件参考](https://code.claude.com/docs/en/plugins-reference) - 技术规范
* [斜杠命令](https://code.claude.com/docs/en/agent-sdk/slash-commands) - 在 SDK 中使用命令
* [子代理](https://code.claude.com/docs/en/agent-sdk/subagents) - 使用专用代理
* [Skills](https://code.claude.com/docs/en/agent-sdk/skills) - 使用 Agent Skills
