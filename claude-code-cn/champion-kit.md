---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】推广工具包
description: 面向已在使用 Claude Code 并希望帮助团队采用的工程师的行动指南，包括分享什么、如何回答问题、三十天推广计划以及应对常见顾虑的方法。
category: translation
tags: [claude-code, champion-kit, translation]
refs:
  - https://code.claude.com/docs/en/champion-kit.md
  - en-source/champion-kit.md
---

# 推广工具包

**本页面面向已经在使用 Claude Code、并希望帮助团队采用的工程师。** 涵盖分享什么、如何回答问题、三十天推广计划、以及应对常见顾虑的方法。

开发者工具的采用很少因为一次发布公告就成功。它的发生往往是因为团队中有人把工具用好了、公开谈论它、并让其他人容易跟进。作为推广者，你的每一个案例都缩短了后来者的学习曲线，每一个公开回答都将个人经验变成团队共同的资产。你是团队的乘数效应，而非帮助台。本指南的结构旨在让这个角色可持续。

## 推广者角色

**三种相互强化的行为构成了推广者角色。**

| 行为 | 具体表现 | 为什么重要 |
|------|---------|-----------|
| 分享发现 | 在团队常看的地方（工程频道、站会帖子、PR 描述）发布你的 prompt、截图和小胜利 | 来自自己代码库的案例比任何外部文档都有说服力 |
| 成为别人问的人 | 当同事问你怎么做到的，直接回复你用的 prompt | 具体可运行的示例消除了"好奇"到"第一次成功使用"之间的鸿沟 |
| 扩大圈子 | 建立少量轻量级的循环习惯（专属频道、每周帖子） | 依赖单人的采用是脆弱的，由共同习惯承载的采用会自行复利 |

### 时间投入预期

| 活动 | 每周时间 | 指导 |
|------|---------|------|
| 发布胜利和 prompt | 约 15 分钟 | 截图加一两句话，不要写成正式报告 |
| 在共享频道回答问题 | 约 20 分钟 | 公开回答一次，再次出现时贴链接 |
| 主持每周 show-and-tell | 约 5 分钟 | 你发起话题，团队提供内容 |
| 可选的配对或演示 | 0-30 分钟 | 留给真正卡住的同事，先给 [Quickstart](https://code.claude.com/docs/en/quickstart) 链接 |

## 分享发现

**你自己的经验是同事能遇到的最有说服力的材料，因为它针对你们共享的代码库和问题。**

### 值得分享什么

最有用的帖子描述的是同事明天就能复用的技巧，而非已完成的结果。技巧在团队中传播时会复利；状态更新不会。

可复用技巧示例：

- "我发现 @-引用目录有效。指向 `@src/components/` 并问哪些缺测试，发现了两个我遗漏的。"
- "Plan 模式（`Shift+Tab`）在编辑前精确展示将修改哪些文件，这就是我在共享代码上放心使用它的原因。"
- "我配置了 Stop hook，长任务完成时收到桌面通知。配置在帖子里。"
- "运行 `/init` 会从仓库生成 `CLAUDE.md`，让助手不再反复问我们的规范。"

### 在哪里分享

在团队已经在看的地方发布。目标是把示例放在正常工作路径上，而非创建一个目的地。

| 位置 | 适合什么 | 推荐格式 |
|------|---------|---------|
| `#claude-code` 或通用工程频道 | 发现、prompt、"今天学到" | 截图配一两句上下文 |
| PR 描述 | 在 reviewer 已经在看的真实代码上展示方法 | 一行如"Claude 和我做了这个重构，乐意演示方法" |
| 站会或周报 | 向 lead 正常化使用 | 一句话描述一个具体产出 |
| 团队 wiki | 持久模式、自定义技能、`CLAUDE.md` 示例 | 短页面，从频道置顶链接过来 |

### 有效的格式

截图配一行上下文，或简短的前后对比，通常就是合适的详细程度。保持每条帖子短到滚动路过也能吸收要点。

示例帖子：

```text
Learned today that @-mentioning a directory works. I pointed it at
@src/components/ and asked which components were missing tests, and it
surfaced two I had forgotten about.
```

```text
I configured a Stop hook so I receive a desktop notification when a long
task completes. I started a refactor, stepped away, and was notified when
it finished. Configuration is in the thread.
```

```text
Plan mode is the reason I am comfortable using this on code that matters.
Press Shift+Tab until you see "plan"; it lays out exactly which files it
intends to touch before changing anything.
```

## 成为别人问的人

**分享几个示例后问题自然会来。这是推广者角色杠杆最大的地方，因为回答一个人往往同时解锁了几个旁观者。**

### 用 prompt 回答而非解释

当同事问你怎么做到的，最有用的回复是你实际用的 prompt。他们从在自己问题上运行那个 prompt 学到的，比你能写的任何描述都多。

```text
同事：你怎么找到那个竞态条件的？

推广者：我问"@tests/scheduler.test.ts 中的测试是 flaky 的，找出原因"，
它追踪到 scheduler 中两个未 join 的 promise。试试同样的措辞。
```

### 指向功能而非文档

"试试 plan 模式，按 `Shift+Tab` 直到看到它"比文档链接更有用。如果对方后来需要更多深度，他们自己会找到。

### 常见问题

| 问题 | 建议回复 | 后续资源 |
|------|---------|---------|
| "我应该先试什么？" | 推荐一个真实但可控的任务——最好是对方一直在推迟的枯燥 bug | [Common workflows](https://code.claude.com/docs/en/common-workflows) |
| "怎么信任它动我的代码？" | 介绍 plan 模式：`Shift+Tab` 切入，Claude 展示打算改什么，你批准后才执行 | [Permissions](https://code.claude.com/docs/en/permissions) |
| "设置值得花时间吗？" | 安装约两分钟，在终端运行，不需要 IDE 扩展。运行一次 `/init` 即可开始 | [Quickstart](https://code.claude.com/docs/en/quickstart) |
| "它产生了错误结果" | 鼓励把错误反馈给 Claude。粘贴错误信息或失败测试比重新措辞有效得多 | [Common workflows](https://code.claude.com/docs/en/common-workflows) |
| "它不理解我们的代码规范" | 建议运行 `/init` 生成 `CLAUDE.md`，然后添加团队规范和测试命令 | [Memory](https://code.claude.com/docs/en/memory) |
| "这只是自动补全吗？" | 做个简短演示：Claude 解释陌生文件、追踪跨服务 bug、或起草迁移计划 | 两分钟现场演示 |
| "安全和数据处理呢？" | 将此问题转给管理员。你的组织的部署和数据处理策略已配置好 | [Security](https://code.claude.com/docs/en/security) · [Data usage](https://code.claude.com/docs/en/data-usage) |

## 扩大圈子

**目标不是建立一个项目或拥有一个 rollout。而是建立少量轻量级习惯，让动量在你不再主动推动后继续。** 当频道里的问题被你以外的人回答时，角色就完成了它的使命。

### 有效的模式

| 模式 | 怎么运行 | 所需精力 |
|------|---------|---------|
| 专属频道 | 创建 `#claude-code` 频道，置顶 [Quickstart](https://code.claude.com/docs/en/quickstart) 和一个好示例，公开回答问题 | 约五分钟设置，之后是环境噪音 |
| 每周 show-and-tell | 每周五发"这周 Claude 帮你做了什么？"不需要准备、幻灯片或会议 | 每周约两分钟 |
| 分享自定义技能 | 发布你最有用的 `.claude/skills/<name>/SKILL.md` 文件，附一行描述 | 每个技能约五分钟 |
| 从使用中生成设置指南 | 在你花过真正时间的项目中运行 `/team-onboarding` | 约两分钟 |
| 配对首次任务 | 为入门者提供一次十五分钟的配对 | 每人约十五分钟 |
| 找到下一个推广者 | 问你最多问题的同事通常准备好了 | 忽略不计 |

### 三十天计划

| 阶段 | 内容 | 信号 |
|------|------|------|
| 第一周：种子频道 | 创建频道，置顶 Quickstart，发两三个你的示例（含 prompt） | 几个同事互动或提问 |
| 第二周：开始节奏 | 开始每周 show-and-tell，公开回答每个问题，分享一个自定义技能或 `CLAUDE.md` 片段 | 你以外的人发布了自己的示例 |
| 第三周：配对和整合 | 提供两三次短配对，将常见问答整理成置顶 FAQ | 看到重复使用——同样的同事回来而非试一次就停 |
| 第四周：交接 | 找到第二个推广者，与 lead 分享什么有效什么无效 | 频道里的问题被你以外的人回答 |

### 当有人想深入

你是热情的引介，而非入门培训。当同事从"我该不该试"进入"我怎么变得高效"时，指向 [Quickstart](https://code.claude.com/docs/en/quickstart) 和 [Common workflows](https://code.claude.com/docs/en/common-workflows) 页面。

## 应对常见顾虑

**健康的怀疑是正常的。最有效的回应是承认顾虑、提供简短重构、并提出在对方自己的代码上做一次具体演示。**

| 顾虑 | 建议回复 | 可提供的证据 |
|------|---------|------------|
| "没有它我更快" | 对于常写的代码可能是对的。建议试试他们倾向于回避的工作：遗留文件、不熟悉的服务、测试脚手架 | 用两种方式计时一个枯燥任务并比较 |
| "我不信任 AI 碰生产代码" | 同意不应有未审阅的变更。Plan 模式加正常 diff review 意味着没什么是工程师没检查过的 | 在真实文件上演示 plan 模式 |
| "会让初级工程师变弱" | 用得好是有效的讲解者。鼓励初级先让 Claude 解释文件再让它改 | 一起运行"Explain @file and where it is called from" |
| "我试过一次，它产生幻觉" | 通常是上下文问题而非模型问题。@-引用相关文件、运行 `/init`、提供实际错误输出通常能解决 | 用正确 @-context 重跑原始 prompt |
| "没时间学另一个工具" | Claude Code 是终端命令而非平台。如果第一次会话没返回价值，搁置是合理的 | 两分钟安装加一个真实 bug |

## 快速参考表

**以下技巧最可靠地将人从首次试用推向日常使用。** 在频道置顶或单独分享此表。

| 技巧 | 如何应用 |
|------|---------|
| 提供正确上下文 | 使用 `@file` 或 `@directory/` 引用，或直接粘贴错误/日志输出 |
| 编辑前审查计划 | 按 `Shift+Tab` 进入 plan 模式。Claude 描述打算的变更供你批准后再执行 |
| 教它你的仓库 | 运行 `/init` 生成 `CLAUDE.md`，然后添加规范和测试命令。见 [Memory](https://code.claude.com/docs/en/memory) |
| 复用工作流 | 在 `.claude/skills/<name>/` 保存 `SKILL.md` 文件创建 `/name` 技能。见 [Skills](https://code.claude.com/docs/en/skills) |
| 长任务保持知情 | 配置 Stop hook 在长任务完成时收桌面通知。见 [Hooks](https://code.claude.com/docs/en/hooks-guide) |
| 从错误结果恢复 | 不要重新措辞请求，粘贴失败的测试或堆栈跟踪并要求 Claude 针对该特定失败处理 |
| 保持编辑精准 | 要求 diff，或指定"只改 X"。指定范围时 Claude 尊重范围 |

> Claude Code 更新频繁。在内部分发此材料前，请对照 [文档首页](https://code.claude.com/docs/en/overview) 验证版本特定细节。
