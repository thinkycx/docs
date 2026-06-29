---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】Checkpointing 检查点
description: Claude Code 的检查点机制会自动追踪代码编辑状态，支持回退到任意历史节点、恢复代码或对话、以及压缩对话释放上下文空间。本文介绍检查点的工作原理、常见用法和局限性。
category: translation
tags: [claude-code, checkpointing, translation]
refs: [https://code.claude.com/docs/en/checkpointing.md]
---

# Checkpointing 检查点

> 追踪、回退、总结 Claude 的编辑和对话，管理会话状态。

**Claude Code 会自动追踪你工作过程中的文件编辑**，方便你在出问题时快速撤销更改、回退到之前的状态。

## 检查点的工作原理

**每次编辑前自动捕获代码快照**，你可以放心大胆地进行大规模修改——因为随时能回到之前的代码状态。

### 自动追踪

Claude Code 会追踪所有通过文件编辑工具做出的改动：

| 特性 | 说明 |
|------|------|
| 创建时机 | 每次用户发送 prompt 时自动创建一个新检查点 |
| 跨会话持久化 | 检查点在恢复的对话中依然可用 |
| 自动清理 | 随会话一起在 30 天后清理（可配置） |

### 回退与总结

**运行 `/rewind`，或在输入框为空时连按两次 `Esc`**，即可打开回退菜单。

> 注意：如果输入框中有文字，双击 `Esc` 会清空文字而非打开菜单。被清空的文字会保存到输入历史，按 `Up` 键可找回。

回退菜单列出了本次会话中你发送的每条 prompt。选中要操作的节点后，可以执行以下动作：

| 动作 | 效果 |
|------|------|
| **Restore code and conversation** | 将代码和对话都恢复到该节点 |
| **Restore conversation** | 回退对话到该节点，但保留当前代码 |
| **Restore code** | 恢复文件改动，但保留对话 |
| **Summarize from here** | 将该节点之后的对话压缩为摘要，释放上下文空间 |
| **Summarize up to here** | 将该节点之前的对话压缩为摘要，保留之后的消息 |
| **Never mind** | 返回消息列表，不做任何更改 |

选择恢复对话或 Summarize from here 后，所选节点的原始 prompt 会被还原到输入框中，方便你重新发送或修改。

选择 Summarize up to here 后，光标会留在对话末尾，输入框为空。

#### 回退到 /clear 之前

**如果之前执行过 `/clear`**，回退菜单顶部会多出一个条目：`/resume <session-id> (previous session)`。选中它即可恢复 `/clear` 之前的对话。此条目在退出 Claude Code 或恢复其他会话前一直可用，需要 Claude Code v2.1.191 或更高版本。低版本可以通过 `/resume` 手动选择之前的会话。

#### Restore 与 Summarize 的区别

**Restore 是回退状态，Summarize 是压缩内容。**

Restore 选项会撤销代码改动、对话历史或两者。Summarize 选项则将部分对话压缩为 AI 生成的摘要，不改变磁盘上的文件：

| 操作 | 行为 |
|------|------|
| **Summarize from here** | 所选节点之前的消息保持不变，该节点及之后的内容被替换为摘要。适合丢弃一段跑偏的讨论，同时保留前面的上下文细节。 |
| **Summarize up to here** | 所选节点之前的消息被替换为摘要，该节点及之后的内容保持不变，光标留在对话末尾。适合压缩前期的配置讨论，保留最近的工作细节。 |

两种情况下，原始消息都保留在会话记录中，Claude 需要时仍可引用其中的细节。你可以输入可选的指引文字来控制摘要的侧重方向。这类似于 `/compact`，但更有针对性——你可以选择压缩所选节点的哪一侧，而非整段对话。

> 注意：Summarize 是在当前会话内压缩上下文。如果你想分支出一个新方向同时保留原会话完好，请使用 [fork](https://code.claude.com/docs/en/sessions#branch-a-session)（`claude --continue --fork-session`）。

## 常见使用场景

检查点在以下场景特别有用：

| 场景 | 说明 |
|------|------|
| **探索不同方案** | 尝试不同的实现方式，不用担心丢失起点 |
| **从错误中恢复** | 快速撤销引入 bug 或破坏功能的改动 |
| **迭代功能开发** | 放心尝试各种变体，随时回退到可用状态 |
| **释放上下文空间** | 从中间节点开始总结冗长的调试过程，保留开头的指令不变 |

## 局限性

### Bash 命令的改动不被追踪

**检查点不会追踪通过 bash 命令修改的文件。** 例如：

```bash
rm file.txt
mv old.txt new.txt
cp source.txt dest.txt
```

这些文件改动无法通过回退撤销。只有通过 Claude 文件编辑工具做出的直接编辑才会被追踪。

### 外部更改不被追踪

**检查点只追踪当前会话中被编辑过的文件。** 你在 Claude Code 之外手动做的更改，以及其他并发会话的编辑，通常不会被捕获——除非它们恰好修改了与当前会话相同的文件。

### 不能替代版本控制

**检查点是会话级别的快速恢复工具，不是版本控制系统。**

| 定位 | 工具 |
|------|------|
| 本地撤销 | 检查点 |
| 永久历史 | Git |

对于永久的版本历史和协作，继续使用版本控制系统（如 Git）管理 commit、分支和长期历史。检查点是 Git 的补充而非替代。

## 相关文档

- [Interactive mode](https://code.claude.com/docs/en/interactive-mode) - 键盘快捷键与会话控制
- [Commands](https://code.claude.com/docs/en/commands) - 通过 `/rewind` 访问检查点
- [CLI reference](https://code.claude.com/docs/en/cli-reference) - 命令行选项
