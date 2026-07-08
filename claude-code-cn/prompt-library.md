---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Prompt 库
description: Claude Code 的 Prompt 库收录了按任务和角色分类的可复制 prompt，涵盖理解代码、规划、构建、测试、审查、调试、自动化等阶段的实用模板。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/prompt-library.md
  - en-source/prompt-library.md
---

# Prompt 库

> 按任务和角色分类的 Claude Code 可复制 prompt。

**这是一个可以直接复制到 Claude Code 中使用的 Prompt 库。** 用它探索你还没尝试过的工作方式，或在不确定从哪里开始时参考。

这些 prompt 收集自 Anthropic 的各种指南，包括 [Common workflows](https://code.claude.com/docs/en/common-workflows)、[Best practices](https://code.claude.com/docs/en/best-practices) 和 [How Anthropic teams use Claude Code](https://claude.com/blog/how-anthropic-teams-use-claude-code)。它们是起点而非脚本。

> [!NOTE]
> 原文页面包含一个交互式 React 组件，支持搜索、过滤标签、填充变量并复制 prompt。以下为所有 prompt 的文本版本，按开发生命周期阶段分组。

## 发现阶段

### 入门

**在新仓库中定位方向**

```
give me an overview of this codebase: architecture, key directories, and how the pieces connect
```

为什么有效：描述你想知道什么，而不是要读哪些文件。Claude 自己探索项目并返回结构摘要。

### 理解

**解释不熟悉的代码**

```
explain what {path} does and how data flows through it. write it up as {format}
```

示例变量：`path` = `src/scheduler/queue.ts`，`format` = `an HTML page with a diagram, then open it in my browser`

**找到某个行为发生的位置**

```
where do we {behavior}?
```

示例：`behavior` = `validate uploaded file types`

**检查删除前会破坏什么**

```
what would break if I deleted {target}?
```

**追溯代码演变**

```
look through the commit history of {path} and summarize how it evolved and why
```

**评估变更范围**

```
which files would I need to touch to {change}?
```

**向代码库提产品问题**

```
I am a {role}. walk me through what happens when a user {action}, from the UI down to the result
```

## 设计阶段

### 规划

**规划多文件变更**

```
plan how to refactor the {target} to {goal}. list the files you would change, but don't edit anything yet
```

为什么有效：添加 "don't edit yet" 将探索和变更分开，先看方案再动代码。

**通过访谈起草 spec**

```
I want to build {feature}. interview me about implementation, UX, edge cases, and tradeoffs until we have covered everything, then write the spec to SPEC.md
```

**将会议转为工单**

```
read {input} and write up the action items, then create a {tracker} ticket for each with acceptance criteria
```

**在构建前映射边界情况**

```
list the error states, empty states, and edge cases for {feature} that the design needs to cover
```

### 原型

**将 mockup 变为可工作的原型**

```
here is a mockup. build a working prototype I can click through, matching the layout and states shown
```

（粘贴、拖拽或 @-mention 你的 mockup 图片）

**从截图实现并自检**

```
implement this design, then take a screenshot of the result, compare it to the original, and fix any differences
```

## 构建阶段

### 实现

**遵循现有模式**

```
look at how {example} is implemented to understand the pattern, then build {new} the same way
```

**为代码生成文档**

```
find {scope} without {format} comments and add them, matching the style already used in the file
```

**添加小而明确的功能**

```
add a {endpoint} endpoint that returns {payload}
```

**从零构建小工具**

```
create a {tool} using HTML, CSS, and vanilla JavaScript, then open it in my browser
```

**端到端处理 issue**

```
read issue #{issue}, implement the fix, and run the tests
```

（需要 `gh` CLI 认证）

**查找并更新文案**

```
find every place we say "{copy}" or a close variant, show me each one in context, then update them all to "{new}". leave tests and the changelog alone
```

**从过去的示例起草文档**

```
read the {examples} in {folder} to learn the structure and voice, then draft a new one for {topic}
```

### 测试

**写测试、运行、修复失败**

```
write tests for {path}, run them, and fix any failures
```

**从测试驱动实现**

```
write tests for {feature} first, then implement it until they pass
```

**从覆盖率报告填补空白**

```
read {report} and add tests for the lowest-covered files until each is above {target}%
```

### 重构

**跨代码库迁移模式**

```
migrate everything from {from} to {to}: identify every place that needs to change, then make the changes
```

**在语言间移植代码**

```
port {source} to {target}, keeping the same {keep}
```

**针对可度量目标优化**

```
optimize {target} to bring {metric} from {current} down to under {goal}
```

**修复精确的视觉 Bug**

```
the {element} extends {amount} beyond the {container} on {viewport}. fix it.
```

### 审查

**提交前审查变更**

```
review my uncommitted changes and flag anything that looks risky before I commit
```

**审查 PR**

```
review PR #{pr} and summarize what changed, then list any concerns
```

**审查基础设施变更**

```
here is my Terraform plan output. what is this going to do, and is anything here going to cause problems?
```

（先粘贴 plan 输出）

**用子 Agent 运行安全审查**

```
use a subagent to review {path} for security issues and report what it finds
```

### 引导

**纠正错误方向**

```
that is not right: {feedback}. try a different approach
```

**缩小变更范围**

```
that is too much. keep only the changes to {scope} and undo your other edits
```

**将纠正变为规则**

```
you keep {mistake}. add a rule to CLAUDE.md so this stops happening
```

## 发布阶段

### Git

**解决合并冲突**

```
resolve the merge conflicts in this branch and explain what you kept from each side
```

**生成 commit 消息**

```
commit these changes with a message that summarizes what I did
```

**从工单开 PR**

```
find the {tracker} ticket about {topic} and open a PR that implements it
```

### 发布

**从 git 历史起草 release notes**

```
compare {from} to {to} and draft release notes grouped by feature, fix, and breaking change
```

**写 CI workflow**

```
write a GitHub Actions workflow that {steps} on every push to {branch}
```

## 运维阶段

### 调试

**找到并修复失败的测试**

```
the {test} test is failing, find out why and fix it
```

**调查报告的错误**

```
users are seeing {symptom} on {where}. investigate and tell me what is going on
```

**修复构建错误的根本原因**

```
here is a build error. fix the root cause and verify the build succeeds
```

（先粘贴错误输出）

### 事件响应

**调查生产事件**

```
{symptom}. check the logs, recent deploys, and config changes, then tell me the most likely cause
```

**从控制台截图诊断**

```
here is a screenshot of {console}. walk me through why {resource} is failing and give me the exact commands to fix it
```

（粘贴截图）

**用自然语言查询日志**

```
show me all {events} for {scope} over {timeframe}. write the query, run it, and tell me what stands out
```

### 数据

**分析数据文件**

```
read {file}, summarize the key patterns, and write the results to {output}
```

**从性能数据生成变体**

```
read {file}, find the underperforming {items}, and generate {n} new variations that stay under {limit} characters
```

### 自动化

**将重复任务变为 skill**

```
create a /{name} skill for this project that {steps}
```

**为重复行为添加 hook**

```
write a hook that {action} after every {event}
```

**用 MCP 连接工具**

```
set up the {server} MCP server so you can read my {data} directly
```

**记录下次要记住的内容**

```
summarize what we did this session and suggest what to add to CLAUDE.md
```

## 什么让这些 Prompt 有效

这些 prompt 共享几个模式。认识它们有助于将任何 prompt 调整为你自己的任务。

**描述结果，不是步骤。** 说你想要什么，让 Claude 找文件：

```
add rate limiting to the public API and make sure existing tests still pass
```

**给它自检的方法。** 在同一个 prompt 中要求 run、test、compare 或 verify，这样 Claude 会迭代而不是一次就停：

```
write the migration, run it against the dev database, and confirm the schema matches
```

**指向参考。** 命名一个现有文件、测试或模式来匹配，使新代码与已有代码一致：

```
add a settings page that follows the same layout as the profile page
```

**说明可度量目标。** 当目标是性能或覆盖率时，给出指标和阈值使完成条件明确：

```
get the bundle size under 200KB and show me what you removed
```

**给它原始素材。** 直接在 prompt 中粘贴错误、日志、截图和 plan 输出，或输入 `@` 引用文件：

```
why is the build failing? @build.log
```

**说明你想要的答案格式。** 命名格式、长度或受众：

```
explain how the payment retry logic works as an HTML page with a diagram, then open it in my browser
```

更多模式详见 [best practices](https://code.claude.com/docs/en/best-practices)。

## 来源

这些 prompt 基于已发布的 Anthropic 资源中的模式：

- [Common workflows](https://code.claude.com/docs/en/common-workflows)：核心任务的分步指南
- [Best practices](https://code.claude.com/docs/en/best-practices)：prompt 模式和项目设置
- [How Anthropic teams use Claude Code](https://claude.com/blog/how-anthropic-teams-use-claude-code)：工程、产品、设计和数据团队的真实工作流
- [Scaling agentic coding guide](https://resources.anthropic.com/hubfs/Scaling%20agentic%20coding%20across%20your%20organization.pdf)：企业采用指南

视频演练参见 Anthropic Academy 上的免费 [Claude Code in Action](https://anthropic.skilljar.com/claude-code-in-action) 课程。

## 相关资源

本页的 prompt 是起点。一旦某个 prompt 对你的项目有效，下一步是使其可重复：保存为 [skill](https://code.claude.com/docs/en/skills) 让团队任何人可以作为 `/command` 运行，并在 [CLAUDE.md](https://code.claude.com/docs/en/memory) 中记录 Claude 学到的规范使每个会话都从该上下文开始。对于更大或更有风险的变更，[plan mode](https://code.claude.com/docs/en/permission-modes#analyze-before-you-edit-with-plan-mode) 在任何编辑发生前显示文件列表。
