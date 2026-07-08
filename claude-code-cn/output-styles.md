---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】输出风格
description: 输出风格改变 Claude 的响应方式（角色、语气、格式），通过修改系统 prompt 实现。支持内置预设和自定义 Markdown 文件定义，适用于将 Claude Code 用于软件工程之外的场景。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/output-styles.md
  - en-source/output-styles.md
---

# 输出风格

> 让 Claude Code 适应软件工程之外的用途

**输出风格改变 Claude 的响应方式，而非 Claude 知道什么。** 它们修改系统 prompt 来设定角色、语气和输出格式。当你反复对每轮对话重新提示相同的表达方式或格式，或想让 Claude 扮演软件工程师之外的角色时使用。

自定义输出风格将你的指令添加到系统 prompt，并让你选择是否保留 Claude Code 内置的软件工程指令。做代码工作但改变沟通方式时保留它们（比如总是用图表回答）。Claude 完全不做软件工程时去掉它们（比如写作助手或数据分析师）。

对于关于项目、规范或代码库的指令，使用 [CLAUDE.md](https://code.claude.com/docs/en/memory) 替代。

## 内置输出风格

Claude Code 的 **Default** 输出风格是现有系统 prompt，设计用于高效完成软件工程任务。

还有三个额外的内置输出风格：

| 风格 | 说明 |
|------|------|
| **Proactive** | Claude 立即执行，对常规决策做合理假设而非暂停，偏好行动而非规划。这比 [auto mode](https://code.claude.com/docs/en/permission-modes#eliminate-prompts-with-auto-mode) 更强的自主执行引导，且不改变权限模式 |
| **Explanatory** | 在帮你完成软件工程任务之间提供教育性 "Insights"。帮你理解实现选择和代码库模式 |
| **Learning** | 协作式边做边学模式。Claude 不仅在编码时分享 "Insights"，还会要求你自己贡献小的战略性代码片段。Claude Code 会在代码中添加 `TODO(human)` 标记让你实现 |

## 更改输出风格

运行 `/config` 选择 **Output style** 从菜单中选取。选择保存到 `.claude/settings.local.json`（[本地项目级别](https://code.claude.com/docs/en/settings)）。

要不通过菜单设置风格，直接在 settings 文件中编辑 `outputStyle` 字段：

```json
{
  "outputStyle": "Explanatory"
}
```

输出风格是系统 prompt 的一部分，Claude Code 在会话开始时读取一次。更改在 `/clear` 或新会话后生效。参见 [prompt caching 对输出风格的影响](https://code.claude.com/docs/en/prompt-caching#changing-output-style)。

## 创建自定义输出风格

**自定义输出风格是一个 Markdown 文件：** frontmatter 存放元数据，正文是添加到系统 prompt 的指令。

### 步骤 1：创建 Markdown 文件

保存到三个级别之一。文件名成为风格名称（除非在 frontmatter 中设置了 `name`）：

| 级别 | 路径 |
|------|------|
| 用户 | `~/.claude/output-styles` |
| 项目 | `.claude/output-styles` |
| 管理策略 | `.claude/output-styles`（在 [managed settings 目录](https://code.claude.com/docs/en/settings#settings-files)中） |

### 步骤 2：添加 frontmatter 和指令

决定是否保留 Claude Code 的软件工程指令。设置 `keep-coding-instructions: true` 如果你改变的是沟通方式但仍在编码。

示例——每次解释都以图表开头，同时保留 Claude 的编码行为：

```markdown
---
name: Diagrams first
description: Lead every explanation with a diagram
keep-coding-instructions: true
---

When explaining code, architecture, or data flow, start with a Mermaid diagram showing the structure, then explain in prose.

## Diagram conventions

Use `flowchart TD` for control flow and `sequenceDiagram` for request paths. Keep diagrams under 15 nodes.
```

### 步骤 3：切换到你的风格

运行 `/config` 在 **Output style** 下选择你的风格。在 `/clear` 或下次启动会话后生效。

[Plugins](https://code.claude.com/docs/en/plugins-reference) 也可以在 `output-styles/` 目录中提供输出风格。

### Frontmatter 字段

| 字段 | 用途 | 默认值 |
|------|------|--------|
| `name` | 输出风格名称（如果不用文件名） | 继承自文件名 |
| `description` | 输出风格描述，显示在 `/config` 选择器中 | 无 |
| `keep-coding-instructions` | 保留 Claude Code 内置的软件工程指令 | `false` |
| `force-for-plugin` | 仅插件输出风格：启用插件时自动应用此风格，无需用户选择 | `false` |

## 输出风格工作原理

**输出风格直接修改 Claude Code 的系统 prompt：**

- 所有输出风格的自定义指令添加到系统 prompt 末尾
- 所有输出风格在对话中触发提醒 Claude 遵循输出风格指令
- 自定义输出风格去掉 Claude Code 内置的软件工程指令（如何确定变更范围、写注释、验证工作），除非 `keep-coding-instructions` 设为 `true`

Token 使用取决于风格。将指令添加到系统 prompt 增加输入 token，但 prompt caching 在会话第一次请求后降低成本。内置 Explanatory 和 Learning 风格设计上产生比 Default 更长的响应，增加输出 token。

## 与相关功能的对比

| 功能 | 工作方式 | 使用场景 |
|------|---------|---------|
| 输出风格 | 修改系统 prompt | 每轮都要不同的角色、语气或默认响应格式 |
| [CLAUDE.md](https://code.claude.com/docs/en/memory) | 在系统 prompt 后添加用户消息 | Claude 应始终知道你的项目规范和代码库上下文 |
| `--append-system-prompt` | 追加到系统 prompt 而不移除内容 | 单次调用的一次性补充 |
| [Agents](https://code.claude.com/docs/en/sub-agents) | 用自己的系统 prompt、模型和工具运行子 Agent | 需要独立范围的辅助完成聚焦任务 |
| [Skills](https://code.claude.com/docs/en/skills) | 调用或相关时加载任务特定指令 | 有可复用的工作流 |

## 相关资源

- [Settings](https://code.claude.com/docs/en/settings)：`outputStyle` 字段的位置和设置优先级
- [Permission modes](https://code.claude.com/docs/en/permission-modes)：Proactive 风格与 auto mode 的对比
- [Plugins](https://code.claude.com/docs/en/plugins)：打包和分发输出风格
- [Debug your configuration](https://code.claude.com/docs/en/debug-your-config)：诊断输出风格未生效的原因
