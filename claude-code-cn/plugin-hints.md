---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】插件提示
description: 介绍如何从你的 CLI 工具发出标记，让 Claude Code 提示用户安装你在官方市场的插件。覆盖 hint 协议格式、发射时机和用户体验。
category: translation
tags: [claude-code, plugin-hints, translation]
refs:
  - https://code.claude.com/docs/en/plugin-hints.md
  - en-source/plugin-hints.md
---

# 从 CLI 推荐你的插件

**如果你维护一个 CLI/SDK 且在官方 Anthropic 市场有插件，你的工具可以提示 Claude Code 用户安装该插件。**

你的 CLI 在检测到自己运行在 Claude Code 内部时，向 stderr 写一行标记。Claude Code 读取标记、从输出中去除它、并向用户展示一次性安装提示。

Claude Code 在发送给模型前会去除 hint 行，所以标记不会出现在对话中、也不计入 token 用量。协议不需要额外命令，也不改变你的 CLI 对非 Claude Code 用户的输出。

## 工作原理

**Claude Code 为通过 Bash/PowerShell 工具运行的每个命令设置 `CLAUDECODE` 环境变量为 `1`。** 从 v2.1.172 起还设置 `CLAUDE_CODE_CHILD_SESSION` 为 `1`。当你的 CLI 看到这些变量时，向 stderr 写一个自闭合 `<claude-code-hint />` 标签。

Claude Code 收到命令输出后：

1. 扫描 hint 行并在输出到达模型前移除
2. 检查 hint 指向的插件在官方 Anthropic 市场
3. 检查该插件未安装且之前未被提示过
4. 向用户展示安装提示，标明是哪个命令发出的 hint

Claude Code 永远不会自动安装插件。用户始终确认。

## 发射 hint

**用环境变量门控发射，然后向 stderr 写标签。**

选择检查哪个变量：

| 变量 | 特点 |
|------|------|
| `CLAUDECODE` | 每个 Claude Code 版本都设置，覆盖最多会话。IDE 集成终端也设置它 |
| `CLAUDE_CODE_CHILD_SESSION` | 仅在 Claude Code 自己启动的子进程中设置（工具调用、hook 命令等）。需要 v2.1.172+ |

代码示例（门控 `CLAUDECODE` 以最大覆盖）：

```javascript
// Node.js
if (process.env.CLAUDECODE) {
  process.stderr.write(
    '<claude-code-hint v="1" type="plugin" value="example-cli@claude-plugins-official" />\n',
  )
}
```

```python
# Python
import os, sys

if os.environ.get("CLAUDECODE"):
    print(
        '<claude-code-hint v="1" type="plugin" value="example-cli@claude-plugins-official" />',
        file=sys.stderr,
    )
```

```go
// Go
if os.Getenv("CLAUDECODE") != "" {
    fmt.Fprintln(os.Stderr,
        `<claude-code-hint v="1" type="plugin" value="example-cli@claude-plugins-official" />`)
}
```

```shell
# Shell
[ -n "$CLAUDECODE" ] &&
  printf '%s\n' '<claude-code-hint v="1" type="plugin" value="example-cli@claude-plugins-official" />' >&2
```

## 发射位置选择

| 放置位置 | 为什么有效 |
|---------|-----------|
| `--help` 输出 | Claude 探索不熟悉的 CLI 时常运行 help |
| 未知子命令错误 | 在 Claude 对你的接口困惑的时刻触达 |
| 登录/认证成功 | 用户已在设置心态中 |
| 首次运行欢迎消息 | 自然的入门时机 |

## 用户看到什么

当 hint 通过所有检查时，Claude Code 展示类似提示：

```text
─────────────────────────────────────────────────────────────
  Plugin recommendation

    The example-cli command suggests installing a plugin.

    Plugin: example-cli
    Marketplace: claude-plugins-official
    Official integration for example-cli deployments

    Would you like to install it?
    > 1. Yes, install example-cli
      2. No
      3. No, and don't show plugin installation hints again

─────────────────────────────────────────────────────────────
```

提示频率限制：

- **每个插件一次**：提示展示后记录，不再为该插件重复提示
- **每个会话一次**：所有 CLI 合计，每个 Claude Code 会话最多一次 hint 提示

选择 "Yes" 安装到用户作用域。选择 "No, and don't show..." 禁用所有未来 hint 提示。

## Hint 格式

```text
<claude-code-hint v="1" type="plugin" value="example-cli@claude-plugins-official" />
```

| 属性 | 必填 | 描述 |
|------|------|------|
| `v` | 是 | 协议版本。`1` 是唯一支持值 |
| `type` | 是 | Hint 类型。`plugin` 是唯一支持值 |
| `value` | 是 | 插件标识符，`name@marketplace` 格式 |

## 要求

Claude Code 在处理 hint 前强制两个条件：

- **独占一行**：标签必须独占一行。嵌在行中间的标签被忽略
- **官方市场**：`value` 必须引用 Anthropic 控制的市场（如 `claude-plugins-official`）中的插件。指向其他市场的 hint 被静默丢弃

推荐但非强制的指导：

- **写到 stderr**：保持标签不进入 shell 管道
- **用环境变量门控**：仅在 `CLAUDECODE` 或 `CLAUDE_CODE_CHILD_SESSION` 设置时发射

## 将插件加入官方市场

**Hint 协议仅对官方 Anthropic 市场 `claude-plugins-official` 中的插件生效。** 应用内提交表单将插件添加到社区市场，hint 协议不检查社区市场。如果你与 Anthropic 合作伙伴联系人合作，联系他们协调官方市场上架。

## 另见

- [Create plugins](https://code.claude.com/docs/en/plugins) — 构建你的 CLI 推荐的插件
- [Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces) — 在官方市场之外托管插件
- [Environment variables](https://code.claude.com/docs/en/env-vars) — `CLAUDECODE` 及相关变量完整参考
