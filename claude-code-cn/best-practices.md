---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】Claude Code 最佳实践
description: Anthropic 内部验证的 Claude Code 高效模式：管理上下文窗口、提供验证手段、探索→规划→编码流程、精确 Prompt 技巧、CLAUDE.md/权限/MCP/Hooks/Skills 环境配置、会话管理策略。
category: translation
tags: [claude-code, best-practices, translation]
refs:
  - https://code.claude.com/docs/en/best-practices.md
---

# Claude Code 最佳实践

> Claude Code 是一个自主式编程环境。它不是等你提问的聊天机器人，而是能读文件、跑命令、改代码、自主解决问题的 Agent。

这改变了你的工作方式：你描述目标，Claude 自己探索、规划、实现。但自主性带来学习曲线——Claude 有自己的约束，你需要理解它。

本指南覆盖 Anthropic 内部团队和外部工程师验证有效的模式。关于 Agent 循环的底层机制，参见 [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works)（[中文](how-claude-code-works.md)）。

---

## 核心约束：上下文窗口

**所有最佳实践都围绕一个核心约束：上下文窗口会快速填满，填满后性能下降。**

上下文窗口装着整个对话——你的消息、Claude 读的文件、命令输出。一次调试或代码探索就可能消耗数万 token。窗口接近满载时，Claude 会"遗忘"早期指令或犯更多错误。

上下文窗口是你最需要管理的资源。用 [custom status line](https://code.claude.com/docs/en/statusline) 持续追踪用量，参见 [Reduce token usage](https://code.claude.com/docs/en/costs#reduce-token-usage) 了解节省策略。

---

## 给 Claude 提供验证手段

**让 Claude 自己验证工作是否完成，是"能放手不管"和"必须盯着看"的分水岭。**

Claude 在工作"看起来完成"时停止。没有验证手段，"看起来完成"就是唯一信号，你变成了人工验证环。给它一个能产生通过/失败结果的检查，循环就自动闭合：Claude 做事、跑检查、读结果、迭代直到通过。

检查可以是：测试套件、构建退出码、Linter、对比输出的脚本、[浏览器截图](https://code.claude.com/docs/en/chrome) 与设计稿的比对。

| 策略 | 反面示例 | 正面示例 |
| --- | --- | --- |
| **提供验证标准** | *"implement a function that validates email addresses"* | *"write a validateEmail function. example test cases: user@example.com is true, invalid is false, user@.com is false. run the tests after implementing"* |
| **视觉验证 UI 变更** | *"make the dashboard look better"* | *"[paste screenshot] implement this design. take a screenshot of the result and compare it to the original. list differences and fix them"* |
| **定位根因而非症状** | *"the build is failing"* | *"the build fails with this error: [paste error]. fix it and verify the build succeeds. address the root cause, don't suppress the error"* |

### 验证的四个层级

有了检查之后，决定它在多大程度上"卡住"停止：

| 层级 | 做法 | 适用场景 |
| --- | --- | --- |
| **单条 Prompt** | 在同一消息中让 Claude 跑检查并迭代 | 任何任务，立即可用 |
| **跨会话 `/goal`** | 设为 [`/goal` 条件](https://code.claude.com/docs/en/goal)，独立评估器每轮检查，Claude 持续工作直到满足 | 无人值守运行 |
| **确定性门控** | [Stop hook](https://code.claude.com/docs/en/hooks#stop) 以脚本运行检查，阻止结束直到通过（连续 8 次阻止后强制结束） | 必须通过才能停止 |
| **第二意见** | [验证子 Agent](https://code.claude.com/docs/en/sub-agents) 或 [动态工作流](https://code.claude.com/docs/en/workflows) 让新模型尝试反驳结果 | 做事的不该自己打分 |

让 Claude 展示证据（测试输出、命令结果、截图），而不是断言"已完成"。审查证据比自己重跑验证快得多。

---

## 先探索、再规划、后编码

**把研究规划和实现分开，避免解决错误的问题。**

让 Claude 直接写代码可能写出解决错误问题的代码。用 [plan mode](https://code.claude.com/docs/en/permission-modes#analyze-before-you-edit-with-plan-mode) 把探索和执行分离。

### 推荐的四阶段工作流

| 阶段 | 操作 | 示例 |
| --- | --- | --- |
| 1. 探索 | 进入 plan mode，Claude 读文件、回答问题、不修改 | `read /src/auth and understand how we handle sessions and login. also look at how we manage environment variables for secrets.` |
| 2. 规划 | 让 Claude 生成详细实现计划；`Ctrl+G` 可在编辑器中直接修改计划 | `I want to add Google OAuth. What files need to change? What's the session flow? Create a plan.` |
| 3. 实现 | 退出 plan mode，让 Claude 编码并对照计划验证 | `implement the OAuth flow from your plan. write tests for the callback handler, run the test suite and fix any failures.` |
| 4. 提交 | 让 Claude 提交并创建 PR | `commit with a descriptive message and open a PR` |

> **何时跳过规划：** 范围清晰且修改小（修 typo、加 log、改变量名）时直接做。规划最有价值的场景是——你不确定方案、变更涉及多文件、或你不熟悉被修改的代码。如果能一句话描述 diff，就跳过规划。

---

## 在 Prompt 中提供精确上下文

**指令越精确，需要的修正就越少。**

Claude 能推理意图，但不能读你的心。引用具体文件、提及约束、指向示例模式。

| 策略 | 反面示例 | 正面示例 |
| --- | --- | --- |
| **限定范围** — 指定文件、场景、测试偏好 | *"add tests for foo.py"* | *"write a test for foo.py covering the edge case where the user is logged out. avoid mocks."* |
| **指向信息源** — 引导 Claude 到能回答问题的地方 | *"why does ExecutionFactory have such a weird api?"* | *"look through ExecutionFactory's git history and summarize how its api came to be"* |
| **引用现有模式** — 指向代码库中的模式 | *"add a calendar widget"* | *"look at how existing widgets are implemented on the home page to understand the patterns. HotDogWidget.php is a good example. follow the pattern to implement a new calendar widget..."* |
| **描述症状** — 提供症状、可能位置、"修好"的定义 | *"fix the login bug"* | *"users report that login fails after session timeout. check the auth flow in src/auth/, especially token refresh. write a failing test that reproduces the issue, then fix it"* |

模糊提示在探索阶段反而有用。比如 `"what would you improve in this file?"` 能发现你想不到的问题。

### 提供丰富内容

**用 `@` 引用文件、粘贴截图、管道输入数据——越丰富越好。**

| 方式 | 说明 |
| --- | --- |
| `@` 引用文件 | Claude 回答前先读文件 |
| 粘贴图片 | 拖拽或 copy/paste 图片到 prompt |
| 给 URL | 文档和 API 参考；用 `/permissions` 白名单常用域名 |
| 管道输入 | `cat error.log | claude` 直接送入文件内容 |
| 让 Claude 自己获取 | 告诉 Claude 用 Bash 命令、MCP 工具或读文件来拉取上下文 |

---

## 配置你的环境

**几步配置让 Claude Code 在所有会话中都显著更高效。**

完整的扩展功能概览参见 [Extend Claude Code](https://code.claude.com/docs/en/features-overview)。

### 写好 CLAUDE.md

**`/init` 生成起始文件，之后持续精简。**

CLAUDE.md 是 Claude 每次对话开始时读取的特殊文件。放入 Bash 命令、代码风格、工作流规则——给 Claude 无法从代码推断的持久上下文。

```markdown
# Code style
- Use ES modules (import/export) syntax, not CommonJS (require)
- Destructure imports when possible (eg. import { foo } from 'bar')

# Workflow
- Be sure to typecheck when you're done making a series of code changes
- Prefer running single tests, and not the whole test suite, for performance
```

| 应该包含 | 不应该包含 |
| --- | --- |
| Claude 猜不到的 Bash 命令 | Claude 读代码就能推断的东西 |
| 不同于默认的代码风格规则 | Claude 已知的语言标准约定 |
| 测试指令和偏好的测试运行器 | 详细的 API 文档（链接即可） |
| 仓库礼仪（分支命名、PR 约定） | 经常变化的信息 |
| 项目特有的架构决策 | 长篇解释或教程 |
| 开发环境的坑（必需的环境变量） | 逐文件的代码库描述 |
| 常见陷阱或非显而易见的行为 | 不言自明的实践（如"写干净代码"） |

关键原则：
- 如果 Claude 反复违反规则但 CLAUDE.md 里有，文件可能太长、规则被淹没了
- 如果 Claude 问了 CLAUDE.md 已回答的问题，措辞可能有歧义
- 像代码一样对待 CLAUDE.md：出问题时审查、定期精简、观察行为变化
- 加强调（如 "IMPORTANT" 或 "YOU MUST"）可提高遵守度
- 提交到 git，让团队共同维护

CLAUDE.md 支持用 `@path/to/import` 语法导入其他文件：

```markdown
See @README.md for project overview and @package.json for available npm commands.

# Additional Instructions
- Git workflow: @docs/git-instructions.md
- Personal overrides: @~/.claude/my-project-instructions.md
```

CLAUDE.md 可放置的位置：

| 位置 | 作用域 |
| --- | --- |
| `~/.claude/CLAUDE.md` | 所有 Claude 会话 |
| `./CLAUDE.md`（项目根目录） | 提交到 git，团队共享 |
| `./CLAUDE.local.md`（项目根目录） | 个人项目笔记，加入 `.gitignore` |
| 父目录 | Monorepo 中 `root/CLAUDE.md` 和 `root/foo/CLAUDE.md` 自动加载 |
| 子目录 | Claude 读取该目录文件时按需加载 |

### 配置权限

**用 auto mode 让分类器处理审批，`/permissions` 白名单特定命令，`/sandbox` 启用 OS 级隔离。三种方式各自减少中断。**

默认情况下，Claude Code 对可能修改系统的操作请求权限。安全但繁琐。三种减少中断的方式：

| 方式 | 说明 |
| --- | --- |
| **Auto mode** | 独立分类器模型审查命令，只阻止有风险的：权限提升、未知基础设施、恶意内容驱动的操作 |
| **权限白名单** | 允许已知安全的特定工具，如 `npm run lint` 或 `git commit` |
| **沙箱** | OS 级隔离，限制文件系统和网络访问，Claude 在受限边界内自由工作 |

详见 [permission modes](https://code.claude.com/docs/en/permission-modes)、[permission rules](https://code.claude.com/docs/en/permissions)、[sandboxing](https://code.claude.com/docs/en/sandboxing)。

### 使用 CLI 工具

**告诉 Claude 用 `gh`、`aws`、`gcloud`、`sentry-cli` 等 CLI 与外部服务交互——这是最省上下文的方式。**

如果用 GitHub，装 `gh` CLI。Claude 知道怎么用它创建 issue、开 PR、读评论。没有 `gh` 时 Claude 仍能用 GitHub API，但未认证请求容易触发限流。

Claude 也擅长学习它不认识的 CLI 工具。试试：`Use 'foo-cli-tool --help' to learn about foo tool, then use it to solve A, B, C.`

### 连接 MCP 服务器

**`claude mcp add` 连接 Notion、Figma、数据库等外部工具。**

通过 [MCP servers](https://code.claude.com/docs/en/mcp)，你可以让 Claude 从 issue tracker 实现功能、查数据库、分析监控数据、集成 Figma 设计、自动化工作流。

### 设置 Hooks

**Hooks 用于"必须每次发生、零例外"的动作。**

[Hooks](https://code.claude.com/docs/en/hooks-guide) 在 Claude 工作流的特定时点自动运行脚本。与 CLAUDE.md 的建议性指令不同，Hooks 是确定性的，保证动作发生。

Claude 能帮你写 Hook。试试：*"Write a hook that runs eslint after every file edit"* 或 *"Write a hook that blocks writes to the migrations folder."*

编辑 `.claude/settings.json` 手动配置，运行 `/hooks` 浏览已配置的 Hook。

### 创建 Skills

**在 `.claude/skills/` 创建 `SKILL.md` 文件，给 Claude 领域知识和可复用工作流。**

[Skills](https://code.claude.com/docs/en/skills) 用项目/团队/领域特定信息扩展 Claude 的知识。Claude 在相关时自动应用，或用 `/skill-name` 直接调用。

```markdown
# .claude/skills/api-conventions/SKILL.md
---
name: api-conventions
description: REST API design conventions for our services
---
# API Conventions
- Use kebab-case for URL paths
- Use camelCase for JSON properties
- Always include pagination for list endpoints
- Version APIs in the URL path (/v1/, /v2/)
```

Skills 也可定义可重复调用的工作流：

```markdown
# .claude/skills/fix-issue/SKILL.md
---
name: fix-issue
description: Fix a GitHub issue
disable-model-invocation: true
---
Analyze and fix the GitHub issue: $ARGUMENTS.

1. Use `gh issue view` to get the issue details
2. Understand the problem described in the issue
3. Search the codebase for relevant files
4. Implement the necessary changes to fix the issue
5. Write and run tests to verify the fix
6. Ensure code passes linting and type checking
7. Create a descriptive commit message
8. Push and create a PR
```

运行 `/fix-issue 1234` 调用。`disable-model-invocation: true` 用于有副作用、需要手动触发的工作流。

### 创建自定义子 Agent

**在 `.claude/agents/` 定义专用助手，Claude 可将隔离任务委托给它们。**

[子 Agent](https://code.claude.com/docs/en/sub-agents) 在自己的上下文中运行，有自己的工具集。适用于读很多文件或需要专注而不污染主对话的任务。

```markdown
# .claude/agents/security-reviewer.md
---
name: security-reviewer
description: Reviews code for security vulnerabilities
tools: Read, Grep, Glob, Bash
model: opus
---
You are a senior security engineer. Review code for:
- Injection vulnerabilities (SQL, XSS, command injection)
- Authentication and authorization flaws
- Secrets or credentials in code
- Insecure data handling

Provide specific line references and suggested fixes.
```

显式告诉 Claude 使用子 Agent：*"Use a subagent to review this code for security issues."*

### 安装插件

**`/plugin` 浏览市场。插件将 skills、tools、集成打包为一键安装单元。**

[Plugins](https://code.claude.com/docs/en/plugins) 将 skills、hooks、subagents 和 MCP servers 打包为来自社区和 Anthropic 的可安装单元。如果用类型化语言，安装 [code intelligence plugin](https://code.claude.com/docs/en/discover-plugins#code-intelligence) 给 Claude 精确的符号导航和编辑后自动错误检测。

如何在 skills、subagents、hooks 和 MCP 之间选择，参见 [Extend Claude Code](https://code.claude.com/docs/en/features-overview#match-features-to-your-goal)。

---

## 有效沟通

**沟通方式显著影响输出质量。**

### 问代码库相关问题

**像问高级工程师一样问 Claude 问题。**

入职新代码库时，用 Claude Code 学习和探索。问你会问其他工程师的问题：

- 日志系统是怎么工作的？
- 如何新建一个 API endpoint？
- `foo.rs` 第 134 行的 `async move { ... }` 做了什么？
- `CustomerOnboardingFlowImpl` 处理了哪些边界情况？
- 第 333 行为什么调 `foo()` 而不是 `bar()`？

这种用法有效缩短入职时间、减少其他工程师的负担。无需特殊提示技巧，直接问。

### 让 Claude 面试你

**对于较大功能，先让 Claude 面试你。用最少的 prompt 开始，让 Claude 通过 `AskUserQuestion` 工具追问。**

Claude 会问你可能没考虑到的事——技术实现、UI/UX、边界情况、权衡。

```text
I want to build [brief description]. Interview me in detail using the AskUserQuestion tool.

Ask about technical implementation, UI/UX, edge cases, concerns, and tradeoffs. Don't ask obvious questions, dig into the hard parts I might not have considered.

Keep interviewing until we've covered everything, then write a complete spec to SPEC.md.
```

Spec 完成后，开一个新会话执行。新会话的上下文干净，完全聚焦于实现；你有书面 Spec 可随时参考。

最有用的 Spec 是自包含的：列出涉及的文件和接口、说明范围外的内容、以端到端验证步骤结尾来证明功能可用。花在精确 Spec 上的时间比花在看实现过程上的时间回报更高。

---

## 管理你的会话

**对话是持久化和可逆的。利用这一点。**

### 尽早纠偏

**发现 Claude 偏离方向时立即纠正。**

最好的结果来自紧密的反馈循环。虽然 Claude 偶尔一次完美解决问题，但快速纠正通常更快产出更好的方案。

| 操作 | 说明 |
| --- | --- |
| `Esc` | 中途停止 Claude，上下文保留，可重新引导 |
| `Esc + Esc` 或 `/rewind` | 打开回退菜单，恢复之前的对话和代码状态，或从选定消息总结 |
| `"Undo that"` | 让 Claude 回退更改 |
| `/clear` | 不相关任务之间重置上下文 |

如果同一会话中纠正了 Claude 两次以上同一问题，上下文已被失败方案塞满。运行 `/clear`，用更精确的 prompt 重新开始——融入你学到的东西。干净会话 + 更好 prompt 几乎总是优于长会话 + 累积修正。

### 积极管理上下文

**不相关任务之间用 `/clear` 重置上下文。**

Claude Code 在接近上下文限制时自动压缩对话历史，保留重要代码和决策并释放空间。

长会话中，上下文窗口可能充满无关对话、文件内容和命令，降低性能甚至让 Claude 分心。

| 操作 | 效果 |
| --- | --- |
| `/clear` | 完全重置上下文窗口 |
| 自动压缩 | Claude 总结最重要的内容——代码模式、文件状态、关键决策 |
| `/compact <instructions>` | 手动压缩，如 `/compact Focus on the API changes` |
| `Esc + Esc` 或 `/rewind` → 选择检查点 | **Summarize from here**：压缩该点之后的消息，保留之前上下文；**Summarize up to here**：压缩之前消息，保留最近的完整内容 |
| CLAUDE.md 中定制压缩行为 | 如 `"When compacting, always preserve the full list of modified files and any test commands"` |
| `/btw` | 快速问题，答案在浮层显示，不进入对话历史，不增长上下文 |

### 用子 Agent 做调查

**用 `"use subagents to investigate X"` 委托研究。子 Agent 在独立上下文中探索，主对话保持干净。**

上下文是根本约束，子 Agent 是最强大的工具之一。Claude 研究代码库时会读大量文件，全部消耗上下文。子 Agent 在独立上下文窗口中运行，只返回摘要：

```text
Use subagents to investigate how our authentication system handles token
refresh, and whether we have any existing OAuth utilities I should reuse.
```

子 Agent 探索代码库、读相关文件、返回发现——不污染主对话。

也可在 Claude 实现完成后用子 Agent 验证：

```text
use a subagent to review this code for edge cases
```

### 用检查点回退

**每次发送 prompt 都创建检查点。你可以将对话、代码或两者恢复到任何之前的检查点。**

Claude 在每次修改前自动快照文件。双击 `Escape` 或运行 `/rewind` 打开回退菜单。可以只恢复对话、只恢复代码、两者都恢复，或从选定消息总结。参见 [Checkpointing](https://code.claude.com/docs/en/checkpointing)。

你可以让 Claude 放手尝试有风险的事。不行就回退，换个方案。检查点跨会话持久化——关掉终端之后仍可回退。

> 注意：检查点只追踪 Claude 做的更改，不追踪外部进程。这不是 git 的替代品。

### 恢复对话

**用 `/rename` 命名会话，把它们当作分支：每个工作流有自己的持久上下文。**

Claude Code 在本地保存对话。跨多次坐下工作时不需要重新解释上下文。`claude --continue` 继续最近会话，`claude --resume` 从列表中选择。给会话起描述性名称如 `oauth-migration` 以便之后找到。参见 [Manage sessions](https://code.claude.com/docs/en/sessions)。

---

## 自动化与扩展

**一个 Claude 用好了，用并行会话、非交互模式、扇出模式倍增产出。**

以上内容假设一人一 Claude 一对话。但 Claude Code 能水平扩展。本节展示如何做更多。

### 运行非交互模式

**`claude -p "prompt"` 用于 CI、pre-commit hooks 或脚本。加 `--output-format stream-json --verbose` 获取流式 JSON 输出。**

`claude -p "your prompt"` 以非交互方式运行 Claude，没有会话。[非交互模式](https://code.claude.com/docs/en/headless) 是将 Claude 集成到 CI 流水线、pre-commit hooks 或任何自动化工作流的方式。

```bash
# 一次性查询
claude -p "Explain what this project does"

# 脚本用结构化输出
claude -p "List all API endpoints" --output-format json

# 实时处理用流式
claude -p "Analyze this log file" --output-format stream-json --verbose
```

### 运行多个 Claude 会话

**并行运行多个 Claude 会话：加速开发、运行隔离实验、启动复杂工作流。**

根据你想做多少协调，选择并行方式：

| 方式 | 说明 |
| --- | --- |
| [Worktrees](https://code.claude.com/docs/en/worktrees) | 在隔离的 git checkout 中运行独立 CLI 会话，编辑不冲突 |
| [Desktop app](https://code.claude.com/docs/en/desktop#work-in-parallel-with-sessions) | 可视化管理多个本地会话，各自有自己的 worktree |
| [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web) | 在 Anthropic 管理的云基础设施上以隔离 VM 运行会话 |
| [Agent teams](https://code.claude.com/docs/en/agent-teams) | 自动协调多会话，含共享任务、消息传递和团队负责人 |

并行之外，多会话也能提升质量。新上下文改善代码审查——Claude 不会对自己刚写的代码有偏见。

Writer/Reviewer 模式示例：

| Session A（写代码） | Session B（审查） |
| --- | --- |
| `Implement a rate limiter for our API endpoints` | |
| | `Review the rate limiter implementation in @src/middleware/rateLimiter.ts. Look for edge cases, race conditions, and consistency with our existing middleware patterns.` |
| `Here's the review feedback: [Session B output]. Address these issues.` | |

类似地：一个 Claude 写测试，另一个写代码让测试通过。

### 跨文件扇出

**循环调用 `claude -p` 处理每个任务。用 `--allowedTools` 限定批量操作的权限。**

对大规模迁移或分析，将工作分发到多个并行 Claude 调用：

1. **生成任务列表**：让 Claude 列出需要迁移的所有文件
2. **写脚本循环处理**：

```bash
for file in $(cat files.txt); do
  claude -p "Migrate $file from React to Vue. Return OK or FAIL." \
    --allowedTools "Edit,Bash(git commit *)"
done
```

3. **先在几个文件上测试，再大规模运行**：根据前 2-3 个文件的问题优化 prompt，然后跑全集。`--allowedTools` 限制 Claude 可做的事——无人值守时很重要。

也可将 Claude 集成到现有数据/处理管道中：

```bash
claude -p "<your prompt>" --output-format json | your_command
```

开发时用 `--verbose` 调试，生产中关掉。

### 以 Auto Mode 自主运行

**对无中断执行配后台安全检查，用 [auto mode](https://code.claude.com/docs/en/permission-modes#eliminate-prompts-with-auto-mode)。**

分类器模型在命令运行前审查，阻止权限提升、未知基础设施和恶意内容驱动的操作，同时让常规工作无提示推进。

```bash
claude --permission-mode auto -p "fix all lint errors"
```

对 `-p` 非交互运行，如果分类器反复阻止操作，auto mode 会中止——因为没有用户可回退。参见 [when auto mode falls back](https://code.claude.com/docs/en/permission-modes#when-auto-mode-falls-back)。

### 添加对抗性审查步骤

**在视为完成之前，让子 Agent 在新上下文中审查 diff 并报告遗漏。**

Claude 无人值守工作越久，独立检查在结束前就越重要。在新 [子 Agent](https://code.claude.com/docs/en/sub-agents) 上下文中运行的审查者只看到 diff 和你给的标准，而不是产生变更的推理过程——它用自己的判断评估结果。

正确性检查可运行内置 [`/code-review` skill](https://code.claude.com/docs/en/commands)，在新子 Agent 中审查当前 diff 并返回发现。要对照计划检查，自己写审查 prompt：

```text
Use a subagent to review the rate limiter diff against PLAN.md. Check that
every requirement is implemented, the listed edge cases have tests, and
nothing outside the task's scope changed. Report gaps, not style preferences.
```

因为审查者作为子 Agent 运行，实现会话直接收到遗漏并可修复和重新审查，无需你在窗口间复制。对更长的自主运行，[agent team](https://code.claude.com/docs/en/agent-teams) 可在多任务间持续此循环，你只需抽查记录的发现。

> 注意：被 prompt 要求"找遗漏"的审查者通常会报告一些，即使工作完善——因为那是它被要求做的。追逐每个发现导致过度工程：多余的抽象层、防御性代码、为不可能发生的情况写测试。告诉审查者只标记影响正确性或明确需求的遗漏，其余视为可选。

---

## 避免常见失败模式

**识别这些模式可节省大量时间。**

| 模式 | 问题 | 解法 |
| --- | --- | --- |
| **厨房水槽会话** | 从一个任务开始，问无关的事，再回到第一个任务。上下文充满无关信息 | 不相关任务之间 `/clear` |
| **反复纠正** | Claude 做错，你纠正，还是错，再纠正。上下文被失败方案污染 | 两次纠正失败后，`/clear` 并写更好的初始 prompt |
| **过度填充的 CLAUDE.md** | 太长，Claude 忽略一半——重要规则淹没在噪音中 | 无情精简。如果 Claude 没有指令也做对了，删掉或转为 Hook |
| **信任-验证缺口** | Claude 产出看似可信但不处理边界情况的实现 | 始终提供验证（测试、脚本、截图）。不能验证就不发布 |
| **无限探索** | 让 Claude "investigate" 但不限定范围。Claude 读几百个文件，填满上下文 | 窄范围调查，或用子 Agent 让探索不消耗主上下文 |

---

## 培养你的直觉

**本指南的模式不是铁律。它们是通用有效的起点，但未必对每种情况都最优。**

有时你应该让上下文累积——因为你深陷一个复杂问题、历史记录有价值。有时应该跳过规划——因为任务是探索性的。有时模糊 prompt 恰恰正确——因为你想看 Claude 如何解读问题再加以约束。

注意什么有效。当 Claude 产出优秀输出时，留意你做了什么：prompt 结构、提供的上下文、所在的模式。当 Claude 挣扎时，问为什么。上下文太嘈杂？prompt 太模糊？任务对一次通过来说太大？

随着时间推移，你会培养出任何指南都无法捕捉的直觉。你会知道何时精确、何时开放，何时规划、何时探索，何时清上下文、何时让它累积。

---

## 相关资源

- [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works)（[中文](how-claude-code-works.md)） — Agent 循环、工具和上下文管理
- [Extend Claude Code](https://code.claude.com/docs/en/features-overview) — skills、hooks、MCP、subagents 和 plugins
- [Common workflows](https://code.claude.com/docs/en/common-workflows) — 调试、测试、PR 等逐步指南
- [CLAUDE.md](https://code.claude.com/docs/en/memory) — 存储项目约定和持久上下文
