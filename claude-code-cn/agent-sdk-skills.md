---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Agent SDK - Skills
description: 在 Claude Agent SDK 中使用 Agent Skills 扩展 Claude 的专业能力。涵盖 Skills 的工作原理、配置方式、文件位置、工具限制和故障排查。
category: translation
tags: [claude-code, agent-sdk, skills, translation]
refs:
  - https://code.claude.com/docs/en/agent-sdk/skills
  - en-source/agent-sdk/skills.md
---

# SDK 中的 Agent Skills

> 在 Claude Agent SDK 中使用 Agent Skills 扩展 Claude 的专业能力

## 概述

**Agent Skills 为 Claude 添加专业能力，Claude 在相关场景下会自主调用。** Skills 打包为 `SKILL.md` 文件，包含指令、描述和可选的辅助资源。

关于 Skills 的详细信息（包括优势、架构和编写指南），参见 [Agent Skills 概览](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)。

## Skills 在 SDK 中的工作方式

**在 Claude Agent SDK 中，Skills 的运作流程如下：**

| 步骤 | 说明 |
|:---|:---|
| 定义为文件系统产物 | 以 `SKILL.md` 文件形式创建在特定目录（`.claude/skills/`） |
| 从文件系统加载 | 根据 `settingSources`（TS）或 `setting_sources`（Python）加载 |
| 自动发现 | 文件系统设置加载后，启动时从用户和项目目录发现 Skill 元数据；触发时才加载完整内容 |
| 模型自主调用 | Claude 根据上下文自主决定何时使用 |
| 通过 `skills` 选项过滤 | 发现的 Skills 默认启用。传入 Skill 名称列表、`"all"` 或 `[]` 来控制可用范围 |

与子代理（可以编程式定义）不同，Skills 必须作为文件系统产物创建。SDK 不提供编程式注册 Skills 的 API。

> **注意：** Skills 通过文件系统设置源发现。使用默认 `query()` 选项时，SDK 加载用户和项目源，因此 `~/.claude/skills/`、`<cwd>/.claude/skills/` 和从 `<cwd>` 到仓库根的任何父目录中的 `.claude/skills/` 都可用。如果显式设置了 `settingSources`，需包含 `'user'` 或 `'project'` 以保持 Skill 发现，或使用 [`plugins` 选项](https://code.claude.com/docs/en/agent-sdk/plugins)从特定路径加载 Skills。

## 在 SDK 中使用 Skills

**在 `query()` 上设置 `skills` 选项来控制会话中哪些 Skills 可用。** 省略时，已发现的 Skills 默认启用且 Skill 工具可用（与 CLI 行为一致）。传入 `"all"` 启用所有已发现的 Skill，传入名称列表只启用指定的，传入 `[]` 禁用全部。设置 `skills` 时，SDK 自动将 Skill 工具添加到 `allowedTools`。如果同时传入了显式 `tools` 列表，需在其中包含 `"Skill"` 以便 Claude 能调用 Skills。

配置完成后，Claude 自动从文件系统发现 Skills 并在与请求相关时调用它们。

Python：

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    options = ClaudeAgentOptions(
        cwd="/path/to/project",  # 包含 .claude/skills/ 的项目
        setting_sources=["user", "project"],  # 从文件系统加载 Skills
        skills="all",  # 启用所有已发现的 Skill
        allowed_tools=["Read", "Write", "Bash"],
    )

    async for message in query(
        prompt="Help me process this PDF document", options=options
    ):
        print(message)


asyncio.run(main())
```

TypeScript：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Help me process this PDF document",
  options: {
    cwd: "/path/to/project", // 包含 .claude/skills/ 的项目
    settingSources: ["user", "project"], // 从文件系统加载 Skills
    skills: "all", // 启用所有已发现的 Skill
    allowedTools: ["Read", "Write", "Bash"]
  }
})) {
  console.log(message);
}
```

**只启用特定 Skills 时，传入名称列表。** 名称匹配 `SKILL.md` 中的 `name` 字段或 Skill 的目录名。插件提供的 Skills 使用 `plugin:skill` 格式。

Python：

```python
options = ClaudeAgentOptions(skills=["pdf", "docx"])
```

TypeScript：

```typescript
const options = { skills: ["pdf", "docx"] };
```

`skills` 选项是上下文过滤器，不是沙箱。未列出的 Skills 对模型不可见且 Skill 工具会拒绝调用，但其文件仍在磁盘上，可通过 Read 和 Bash 访问。

## Skill 位置

**Skills 根据 `settingSources`/`setting_sources` 配置从文件系统目录加载：**

| 位置类型 | 路径 | 说明 |
|:---|:---|:---|
| 项目 Skills | `.claude/skills/` | 通过 git 与团队共享——`setting_sources` 包含 `"project"` 时加载 |
| 用户 Skills | `~/.claude/skills/` | 跨所有项目的个人 Skills——`setting_sources` 包含 `"user"` 时加载 |
| 插件 Skills | — | 随已安装的 Claude Code 插件捆绑 |

## 创建 Skills

**Skills 定义为包含 `SKILL.md` 文件的目录，文件有 YAML frontmatter 和 Markdown 内容。** `description` 字段决定 Claude 何时调用你的 Skill。

示例目录结构：

```bash
.claude/skills/processing-pdfs/
└── SKILL.md
```

关于创建 Skills 的完整指南（包括 SKILL.md 结构、多文件 Skills 和示例），参见：

* [Claude Code 中的 Agent Skills](https://code.claude.com/docs/en/skills)：完整指南含示例
* [Agent Skills 最佳实践](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)：编写指南和命名规范

## 工具限制

> **注意：** SKILL.md 中的 `allowed-tools` frontmatter 字段仅在直接使用 Claude Code CLI 时有效。**通过 SDK 使用 Skills 时不适用。**
>
> 在 SDK 中通过 query 配置的 `allowedTools` 选项控制工具访问。

**在 SDK 应用中控制 Skills 的工具访问时，使用 `allowedTools` 预批准特定工具。** 没有 `canUseTool` 回调的情况下，不在列表中的工具一律拒绝：

Python：

```python
options = ClaudeAgentOptions(
    setting_sources=["user", "project"],  # 从文件系统加载 Skills
    skills="all",
    allowed_tools=["Read", "Grep", "Glob"],
)

async for message in query(prompt="Analyze the codebase structure", options=options):
    print(message)
```

TypeScript：

```typescript
for await (const message of query({
  prompt: "Analyze the codebase structure",
  options: {
    settingSources: ["user", "project"], // 从文件系统加载 Skills
    skills: "all",
    allowedTools: ["Read", "Grep", "Glob"],
    permissionMode: "dontAsk" // 拒绝不在 allowedTools 中的工具
  }
})) {
  console.log(message);
}
```

## 发现可用 Skills

**直接询问 Claude 即可查看 SDK 应用中有哪些 Skills 可用：**

Python：

```python
options = ClaudeAgentOptions(
    setting_sources=["user", "project"],  # 从文件系统加载 Skills
    skills="all",
)

async for message in query(prompt="What Skills are available?", options=options):
    print(message)
```

TypeScript：

```typescript
for await (const message of query({
  prompt: "What Skills are available?",
  options: {
    settingSources: ["user", "project"], // 从文件系统加载 Skills
    skills: "all"
  }
})) {
  console.log(message);
}
```

Claude 会根据当前工作目录和已安装插件列出可用的 Skills。

## 测试 Skills

**通过提出与 Skill 描述匹配的问题来测试 Skills：**

Python：

```python
options = ClaudeAgentOptions(
    cwd="/path/to/project",
    setting_sources=["user", "project"],  # 从文件系统加载 Skills
    skills="all",
    allowed_tools=["Read", "Bash"],
)

async for message in query(prompt="Extract text from invoice.pdf", options=options):
    print(message)
```

TypeScript：

```typescript
for await (const message of query({
  prompt: "Extract text from invoice.pdf",
  options: {
    cwd: "/path/to/project",
    settingSources: ["user", "project"], // 从文件系统加载 Skills
    skills: "all",
    allowedTools: ["Read", "Bash"]
  }
})) {
  console.log(message);
}
```

如果描述匹配你的请求，Claude 会自动调用相关 Skill。

## 故障排查

### Skills 未找到

**检查 settingSources 配置：** Skills 通过 `user` 和 `project` 设置源发现。如果显式设置了 `settingSources`/`setting_sources` 但省略了这些源，Skills 不会被加载：

Python：

```python
# Skills 未加载：setting_sources 排除了 user 和 project
options = ClaudeAgentOptions(setting_sources=[], skills="all")

# Skills 已加载：包含 user 和 project 源
options = ClaudeAgentOptions(
    setting_sources=["user", "project"],
    skills="all",
)
```

TypeScript：

```typescript
// Skills 未加载：settingSources 排除了 user 和 project
const options = {
  settingSources: [],
  skills: "all"
};

// Skills 已加载：包含 user 和 project 源
const options = {
  settingSources: ["user", "project"],
  skills: "all"
};
```

关于 `settingSources`/`setting_sources` 的详情，参见 [TypeScript SDK 参考](https://code.claude.com/docs/en/agent-sdk/typescript#settingsource)或 [Python SDK 参考](https://code.claude.com/docs/en/agent-sdk/python#settingsource)。

**检查工作目录：** SDK 从 `cwd` 选项指定的目录及向上到仓库根的每个父目录中的 `.claude/skills/` 加载 Skills。确保 `cwd` 指向包含 `.claude/skills/` 的目录或其下级（在同一仓库内）：

Python：

```python
# 确保 cwd 指向包含 .claude/skills/ 的目录
options = ClaudeAgentOptions(
    cwd="/path/to/project",  # .claude/skills/ 在此目录或父目录中
    setting_sources=["user", "project"],  # 从这些源加载 skills
    skills="all",
)
```

TypeScript：

```typescript
// 确保 cwd 指向包含 .claude/skills/ 的目录
const options = {
  cwd: "/path/to/project", // .claude/skills/ 在此目录或父目录中
  settingSources: ["user", "project"], // 从这些源加载 skills
  skills: "all"
};
```

**验证文件系统位置：**

```bash
# 检查项目 Skills
ls .claude/skills/*/SKILL.md

# 检查个人 Skills
ls ~/.claude/skills/*/SKILL.md
```

### Skill 未被使用

**检查 `skills` 选项：** 如果传入了 `skills` 列表，确认 Skill 名称包含在内。传入 `[]` 会禁用所有 Skills。

**检查描述：** 确保描述具体且包含相关关键词。参见 [Agent Skills 最佳实践](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#writing-effective-descriptions)了解如何编写有效描述。

### 其他排查

关于通用 Skills 故障排查（YAML 语法、调试等），参见 [Claude Code Skills 故障排查](https://code.claude.com/docs/en/skills#troubleshooting)。

## 相关文档

### Skills 指南

* [Claude Code 中的 Agent Skills](https://code.claude.com/docs/en/skills)：完整 Skills 指南（创建、示例和排查）
* [Agent Skills 概览](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)：概念概览、优势和架构
* [Agent Skills 最佳实践](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)：编写有效 Skills 的指南
* [Agent Skills Cookbook](https://platform.claude.com/cookbook/skills-notebooks-01-skills-introduction)：示例 Skills 和模板

### SDK 资源

* [SDK 中的子代理](https://code.claude.com/docs/en/agent-sdk/subagents)：类似的基于文件系统的代理，带编程选项
* [SDK 中的斜杠命令](https://code.claude.com/docs/en/agent-sdk/slash-commands)：用户调用的命令
* [SDK 概览](https://code.claude.com/docs/en/agent-sdk/overview)：通用 SDK 概念
* [TypeScript SDK 参考](https://code.claude.com/docs/en/agent-sdk/typescript)：完整 API 文档
* [Python SDK 参考](https://code.claude.com/docs/en/agent-sdk/python)：完整 API 文档
