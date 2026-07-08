---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】沟通工具包
description: 面向管理员和工程 lead 的 Claude Code 组织级 rollout 沟通套件，包含发布公告模板、功能激活滴水邮件和高频 FAQ 一行回复。
category: translation
tags: [claude-code, communications-kit, translation]
refs:
  - https://code.claude.com/docs/en/communications-kit.md
  - en-source/communications-kit.md
---

# 沟通工具包

**本页面面向向团队推出 Claude Code 的管理员和工程 lead。** 提供可直接复制的发布公告、功能激活 Tips 滴水推送、以及高频问题的一行回复。

> 将这里的所有内容视为草稿而非成品。用你组织的声音重写，把示例任务换成你自己代码库的真实 bug 和模块，发送前替换 `[括号占位符]`。

## 发布沟通

### 发布前清单

| 项目 | 为什么重要 |
|------|-----------|
| `#claude-code` 频道已创建并链接在消息中 | 让问题有统一去处 |
| 安装命令已在你的环境至少一台机器测试 | 在所有人同时碰到前捕获代理/防火墙问题 |
| 安全和数据处理链接就绪 | "我的代码去哪了？" 会是第一个回复 |
| 选好一个具体首任务（你代码库中真实 bug 或文件） | 通用示例不转化；"修复 `auth_test.go` 中的 flaky 测试" 才行 |
| 前 48 小时有人负责频道 | 发布日未回答的问题会杀死动量 |
| C-suite sponsor 准备发送或联署公告 | 高管发出的 launch 首周采用率始终高于管理员发出的 |

### 标准公告（邮件版）

```text
Subject: Claude Code is live for [Engineering / your team]

Team,

As of today you have access to Claude Code, an AI coding agent that runs in
your terminal, reads your actual codebase, and works through real tasks end
to end: debugging, refactors, tests, PRs. It is not autocomplete and it is
not a chat window. It edits files, runs your commands, and asks permission
before anything risky.

Get running in two minutes:

    curl -fsSL https://claude.ai/install.sh | bash
    cd <your-repo>
    claude

Then run /init once. Claude reads your project and writes a CLAUDE.md with
your build commands and conventions, so you stop re-explaining the basics.

Then try one of these on the repo you are already in:

  - "The test in [file] is flaky. Figure out why and fix it"
  - "Walk me through how [module] handles [X]"
  - "Look at my working diff and tell me what's risky before I push"

Where your code goes: Claude Code runs in your terminal and talks directly
to Anthropic's API, with no third-party servers in the loop. It asks before
editing files or running commands. Under our Enterprise agreement, Anthropic
does not use your code or prompts to train its models.
Details: https://code.claude.com/docs/en/data-usage
         https://code.claude.com/docs/en/security

Where to go with questions: #claude-code. [Owner name] is watching it
this week.

- [Name]
```

### 标准公告（Slack/Teams 版）

```markdown
🚀 *Claude Code is live for [team]*

AI coding agent, runs in your terminal, reads your repo, does real work:
bugs, refactors, tests, PRs. Asks before it touches anything.

`curl -fsSL https://claude.ai/install.sh | bash` → `cd your-repo` → `claude`

*First thing to try* → run `/init`, then: "the test in [file] is flaky,
figure out why and fix it."

🔒 Runs in your terminal, talks only to Anthropic's API. Under our
Enterprise plan your code and prompts are not used to train models.
Data usage → https://code.claude.com/docs/en/data-usage

📚 Quickstart · VS Code · Free 1-hr course
   https://code.claude.com/docs/en/quickstart
   https://code.claude.com/docs/en/vs-code
   https://anthropic.skilljar.com/claude-code-in-action

Questions → this thread. [Owner] is on point.
```

### 高管 sponsor 变体

从 CTO/CIO/SVP Engineering 名义发出。刻意精简到一个要求：安装并在一个真实任务上运行。

```text
Subject: One thing I'd like every engineer to try this week

Team,

We have turned on Claude Code for all of engineering. It is an AI agent
that works directly in your terminal, on your actual codebase, and the
early results from teams already using it are strong enough that I want
everyone on it this week.

I am asking for ten minutes:

    curl -fsSL https://claude.ai/install.sh | bash
    cd <your-repo>
    claude

Then hand it one real task: the bug you have been putting off, or "walk me
through how [module] works."

That is the whole ask. [Owner name] and team are in #claude-code for
anything you hit along the way.

- [Exec Name]
  [Title]
```

### 试点组变体

```text
Subject: You're in the Claude Code pilot

[Name / team],

You are in the first wave of Claude Code at [company]. We picked this group
because you will put it on real problems and tell us the truth about it.

The ask: use it on at least one real task this week, then drop a note in
#claude-code-pilot covering what worked, what was annoying, and what
surprised you. That feedback decides how we roll it out to everyone else.

One extra thing for pilots: on your first multi-file change, press Shift+Tab
until you see "plan". Claude will lay out exactly what it intends to do
before it touches a file. It is the fastest way to calibrate how much to
trust it.
```

### 推广者招募 DM

发布后，DM 在 `#claude-code` 最活跃的两三人：

```text
Hey [name], your #claude-code posts are doing more for adoption than my
announcement did. A couple of people told me your [thread / screenshot]
was why they actually tried it.

Want to make that semi-official? Low lift: mostly keep posting what you
are posting, plus first crack at new features and a direct line to the
Anthropic team. I can share a short playbook if you're in.
```

## Tips 滴水推送

**发布后逐功能激活的即贴 Slack/Teams 消息。** 每条遵循相同模式：Hook → 收益 → "现在试" prompt → 文档链接。每周滴一两条到 `#claude-code`。

### 选择模型

```markdown
🎯 *Tip: Match the model to the moment*

Using Opus to fix a typo burns compute. Using Haiku for a 12-file refactor
is asking for a re-do.

*Try it now:* type `/model` and pick Sonnet if you haven't already.

📖 Model configuration → https://code.claude.com/docs/en/model-config
```

| 模型 | 适用场景 |
|------|---------|
| Fable 5 | 最难、最长运行的任务。需主动选择：`/model fable` |
| Opus | 大规模重构、复杂调试、架构决策 |
| Sonnet | 日常功能、bug 修复、测试、文档。推荐默认 |
| Haiku | 快速问题、格式化、机械编辑 |

### /init 和 CLAUDE.md

```markdown
📁 *Tip: Stop re-explaining your repo every session*

Run `/init` once per repo. Claude reads your project structure and writes a
CLAUDE.md file with your build commands, architecture, and conventions.

*Try it now:* open your main repo, run `claude`, type `/init`.

📖 CLAUDE.md and project memory → https://code.claude.com/docs/en/memory
```

### 权限模式

```markdown
🛡️ *Tip: One keystroke between "look but don't touch" and "just do it"*

*Shift+Tab* cycles through how much Claude can do without asking.

*Try it now:* on your next refactor, hit Shift+Tab until you see "plan".

📖 Permission modes → https://code.claude.com/docs/en/permissions
```

### Skills

```markdown
⚡ *Tip: Turn that prompt you keep retyping into a command*

A SKILL.md file in `.claude/skills/<name>/` becomes a reusable prompt.

*Try it now:* type "make me a /standup skill that summarizes what I worked
on today from git log", then run `/standup` tomorrow morning.

📖 Skills → https://code.claude.com/docs/en/skills
```

### Hooks

```markdown
🔔 *Tip: Get pinged when your refactor finishes*

Hooks are shell commands that fire on Claude Code events.

*Try it now:* ask Claude "add a Stop hook that sends a desktop notification
when you finish".

📖 Hooks guide → https://code.claude.com/docs/en/hooks-guide
```

### Git 工作流

```markdown
🌿 *Tip: Hand off the whole git ceremony*

Claude handles the full git flow: commits, branches, PRs with proper summaries.

*Try it now:* after your next fix, just type "commit this with a good message
and open a PR".

📖 Creating pull requests → https://code.claude.com/docs/en/common-workflows
```

### 安全架构

```markdown
🔐 *Tip: The answer to "is this safe?" for the next time you're asked*

Permission-first by design. Every file edit, shell command, and external
call is gated by your approval. The CLI runs in your terminal and talks
directly to Anthropic's API.

📖 https://code.claude.com/docs/en/security
📖 https://code.claude.com/docs/en/data-usage
```

## 快速参考

### FAQ 一行回复

| 问题 | 回复 |
|------|------|
| "在 VS Code 能用吗？" | 可以。有 VS Code 扩展和 JetBrains 插件。[VS Code →](https://code.claude.com/docs/en/vs-code) |
| "需要先配置什么吗？" | 不需要。安装后 `claude` 在任何仓库运行。`/init` 一次即可。[Quickstart →](https://code.claude.com/docs/en/quickstart) |
| "我的代码去哪了？" | CLI 在你终端运行，向 Anthropic API 发送上下文做推理，无第三方服务器。Enterprise 计划下代码和 prompt 不用于训练。[Data usage →](https://code.claude.com/docs/en/data-usage) |
| "它能看到整个仓库吗？" | 读取你给它访问的内容。工作目录内的文件读取不提示；编辑、shell 命令需权限。[Permissions →](https://code.claude.com/docs/en/permissions) |
| "和 Copilot 有什么不同？" | Copilot 自动补全行。Claude Code 是 agent——读文件、运行命令、做多文件编辑。[Overview →](https://code.claude.com/docs/en/overview) |
| "应该先试什么？" | 你一直推迟的枯燥 bug。"[file] 中的测试是 flaky 的，找出原因。" [Quickstart →](https://code.claude.com/docs/en/quickstart) |

### Prompt 模板

| 任务 | Prompt |
|------|--------|
| 修 bug | "the tests in [file] are failing, figure out why and fix it" |
| 理解代码 | "walk me through how [module] works, then tell me where the entry point is" |
| 安全重构 | "refactor [module] to [goal], use plan mode so I can review first" |
| 写测试 | "write tests for [file] that cover the edge cases around [scenario]" |
| 提交前审查 | "look at my working diff and tell me what looks risky" |
| 开 PR | "fix [issue], write a conventional commit, and open a PR with a summary" |
| 做技能 | "make me a /ship skill that runs tests and lint before commit" |
| 调试堆栈 | "here's the stack trace, find the root cause, don't just paper over it" |

> Claude Code 频繁更新。在内部分发前请对照 [文档首页](https://code.claude.com/docs/en/overview) 验证版本特定细节。
