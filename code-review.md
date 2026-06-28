---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】Code Review
description: Claude Code Review 是一项自动化 PR 审查服务，通过多智能体并行分析代码变更，捕获逻辑错误、安全漏洞和隐性回归。本文介绍其工作原理、配置方式、触发方法和定价模型。
category: translation
tags: [claude-code, code-review, translation]
refs: [https://code.claude.com/docs/en/code-review.md]
---

# Code Review

> **一句话概括：** 配置自动化 PR 审查，通过多智能体对完整代码库的分析来捕获逻辑错误、安全漏洞和隐性回归。

> [!NOTE]
> Code Review 目前处于研究预览阶段，仅对 [Team 和 Enterprise](https://claude.ai/admin-settings/claude-code) 订阅开放，不支持启用了 [Zero Data Retention](https://code.claude.com/docs/en/zero-data-retention) 的组织。

**Code Review 会分析你的 GitHub Pull Request，并以行内评论的形式标注问题所在。** 一组专业化的智能体在你完整代码库的上下文中检查代码变更，寻找逻辑错误、安全漏洞、边界用例缺陷和隐性回归。

**审查结果按严重程度标注，不会批准或阻止你的 PR，现有审查工作流完全不受影响。** 你可以通过在仓库中添加 `CLAUDE.md` 或 `REVIEW.md` 文件来调整 Claude 标记的内容。

如果你希望在自己的 CI 基础设施上运行 Claude（而不是使用这个托管服务），请参考 [GitHub Actions](https://code.claude.com/docs/en/github-actions) 或 [GitLab CI/CD](https://code.claude.com/docs/en/gitlab-ci-cd)。对于自托管 GitHub 实例上的仓库，参见 [GitHub Enterprise Server](https://code.claude.com/docs/en/github-enterprise-server)。

本文涵盖：

* [工作原理](#工作原理)
* [配置](#配置-code-review)
* [手动触发审查](#手动触发审查) — `@claude review` 和 `@claude review once`
* [自定义审查](#自定义审查) — `CLAUDE.md` 和 `REVIEW.md`
* [定价](#定价)
* [故障排除](#故障排除) — 运行失败和评论缺失
* [本地审查 diff](#本地审查-diff) — `/code-review` 命令

> [!TIP]
> 如果只想在终端本地审查 diff，无需安装 GitHub App，直接在任何 Claude Code 会话中运行 `/code-review` 即可。参见 [本地审查 diff](#本地审查-diff)。

---

## 工作原理

**组织 Owner 启用 Code Review 后，审查会根据仓库配置在 PR 打开、每次 push 或手动请求时触发。** 在任何模式下，评论 `@claude review` 都可以[启动审查](#手动触发审查)。

**审查过程：** 多个智能体在 Anthropic 基础设施上并行分析 diff 及其周围代码。每个智能体针对不同类别的问题进行检测，随后验证步骤会对照实际代码行为过滤误报。最终结果去重、按严重程度排序，以行内评论的形式标注在具体代码行上，并在审查正文中提供汇总。如果没有发现问题，Code Review 会更新 GitHub check run 显示未检测到问题，Claude 也可能在 PR 上发一条简短确认评论。

**审查时间和费用随 PR 大小和复杂度线性增长，平均完成时间约 20 分钟。** Owner 可以通过[分析看板](#查看用量)监控审查活动和费用。

### 严重程度分级

| 标记 | 严重程度 | 含义 |
| :--- | :------- | :--- |
| 🔴 | Important（重要） | 合并前应修复的 bug |
| 🟡 | Nit（小问题） | 值得修复但不阻塞合并的小问题 |
| 🟣 | Pre-existing（已有问题） | 代码库中已存在的 bug，非本次 PR 引入 |

**每条发现都包含一个可展开的推理详情，** 你可以查看 Claude 为什么标记该问题以及它如何验证问题的存在。

### 对发现进行评价和回复

**每条审查评论自带 👍 和 👎 反应按钮，支持一键评价。** 👍 表示发现有用，👎 表示错误或噪音。Anthropic 在 PR 合并后收集反应计数用于调优审查器。反应不会触发重新审查或改变 PR 上的任何内容。

**回复行内评论不会触发 Claude 响应或更新 PR。** 要处理某条发现，直接修改代码并 push。如果 PR 订阅了 push 触发的审查，下次运行会在问题修复后自动关闭该讨论线程。要在不 push 的情况下请求一次全新审查，请作为[顶层 PR 评论](#手动触发审查)发送 `@claude review once`。

### Check Run 输出

**除了行内评论外，每次审查还会填充 CI 检查旁边显示的 "Claude Code Review" check run。** 展开其 **Details** 链接可以在一处看到所有发现的汇总，按严重程度排序：

| 严重程度 | 文件:行 | 问题 |
| -------- | ------- | ---- |
| 🔴 Important | `src/auth/session.ts:142` | Token 刷新与登出竞争，导致过期会话残留 |
| 🟡 Nit | `src/auth/session.ts:88` | `parseExpiry` 在输入格式错误时静默返回 0 |

**每条发现还会作为注解出现在 "Files changed" 标签页中，** 直接标注在相关 diff 行上。Important 使用红色标记，Nit 使用黄色警告，Pre-existing 使用灰色提示。注解和严重程度表独立于行内评论写入 check run，因此即使 GitHub 拒绝了某条行内评论（因为代码行已移动），注解仍然可用。

**Check run 始终以 neutral 结论完成，永远不会通过分支保护规则阻止合并。** 如果你希望根据 Code Review 发现来门控合并，可以在自己的 CI 中读取 check run 输出中的严重程度分布。Details 文本的最后一行是机器可读的注释，可以用 `gh` 和 jq 解析：

```bash
gh api repos/OWNER/REPO/check-runs/CHECK_RUN_ID \
  --jq '.output.text | split("bughunter-severity: ")[1] | split(" -->")[0] | fromjson'
```

返回一个按严重程度计数的 JSON 对象，例如 `{"normal": 2, "nit": 1, "pre_existing": 0}`。`normal` 键对应 Important 发现的数量；非零值表示 Claude 发现了至少一个建议在合并前修复的 bug。

### Code Review 检查什么

**默认情况下，Code Review 聚焦于正确性：会导致线上故障的 bug，而非格式偏好或测试覆盖率缺失。** 你可以通过[添加指导文件](#自定义审查)来扩展检查范围。

---

## 配置 Code Review

**组织 Owner 为组织启用 Code Review 一次，并选择要包含的仓库。**

### 步骤

1. **打开 Claude Code 管理设置**
   前往 [claude.ai/admin-settings/claude-code](https://claude.ai/admin-settings/claude-code)，找到 Code Review 部分。你需要在 Claude 组织中拥有 Owner 或 Primary Owner 角色，并且在 GitHub 组织中拥有安装 GitHub App 的权限。

2. **开始配置**
   点击 **Setup**，进入 GitHub App 安装流程。

3. **安装 Claude GitHub App**
   按照提示将 Claude GitHub App 安装到你的 GitHub 组织。该 App 请求以下仓库权限：
   * **Contents**：读写
   * **Issues**：读写
   * **Pull requests**：读写

   Code Review 使用内容的读权限和 Pull Request 的写权限。更广泛的权限集也支持 [GitHub Actions](https://code.claude.com/docs/en/github-actions)（如果你后续启用）。

4. **选择仓库**
   选择要启用 Code Review 的仓库。如果看不到某个仓库，请确认安装时已授予 Claude GitHub App 对该仓库的访问权限。后续可以随时添加更多仓库。

5. **为每个仓库设置审查触发方式**
   配置完成后，Code Review 部分会以表格形式显示你的仓库。对每个仓库，使用 **Review Behavior** 下拉菜单选择审查运行时机：
   * **Once after PR creation**：PR 打开或标记为 ready for review 时运行一次
   * **After every push**：每次 push 到 PR 分支时运行，随 PR 演进捕获新问题，修复后自动关闭讨论线程
   * **Manual**：仅在有人[评论 `@claude review` 或 `@claude review once`](#手动触发审查) 时启动；`@claude review` 还会订阅后续 push 的审查

   每次 push 都审查会产生最多的审查次数和费用。Manual 模式适合高流量仓库（只希望对特定 PR 启用审查）或希望 PR 准备好后再开始审查的场景。

**仓库表格还显示每个仓库基于近期活动的平均审查费用。** 使用行操作菜单可以为每个仓库开关 Code Review 或完全移除仓库。

**验证配置：** 打开一个测试 PR。如果选择了自动触发，几分钟内会出现名为 **Claude Code Review** 的 check run。如果选择了 Manual，在 PR 上评论 `@claude review` 启动第一次审查。如果没有 check run 出现，确认仓库已列在管理设置中且 Claude GitHub App 有权访问。

---

## 手动触发审查

**两个评论命令可以按需启动审查，** 无论仓库配置了哪种触发方式都有效。在 Manual 模式下可以用它们将特定 PR 纳入审查，在其他模式下可以获得即时重新审查。

| 命令 | 作用 |
| :--- | :--- |
| `@claude review` | 启动审查，并订阅该 PR 后续 push 触发的审查 |
| `@claude review once` | 启动一次性审查，不订阅后续 push |

**`@claude review once` 适合只想获取当前状态反馈、不想后续每次 push 都产生审查的场景。** 对于 push 频繁的长周期 PR 或只需要一次性第二意见的情况特别有用。

**使用这两个命令的前提：**

* 作为顶层 PR 评论发布（不是 diff 行上的行内评论）
* 命令放在评论开头，如果使用一次性形式则 `once` 在同一行
* 你必须对仓库拥有 owner、member 或 collaborator 权限
* PR 必须处于 open 状态

**与自动触发不同，手动触发会在 draft PR 上运行，** 因为明确请求表明你现在就需要审查，不管 draft 状态。

如果该 PR 上已有审查正在运行，请求会排队等待进行中的审查完成。你可以通过 PR 上的 check run 监控进度。

---

## 自定义审查

**Code Review 读取仓库中的两个文件来指导标记内容，** 它们的影响力度不同：

* **`CLAUDE.md`**：Claude Code 所有任务共享的项目指令，不仅限于审查。Code Review 将其作为项目上下文读取，新引入的违规标记为 Nit。
* **`REVIEW.md`**：仅审查专用的指令，作为最高优先级直接注入审查流水线中的每个智能体。用它来改变标记内容、标记严重程度和报告方式。

### CLAUDE.md

**Code Review 会读取仓库的 `CLAUDE.md` 文件，将新引入的违规标记为 [Nit 级别](#严重程度分级)的发现。** 这是双向的：如果你的 PR 修改了代码导致 `CLAUDE.md` 中的描述过时，Claude 也会标记文档需要更新。

Claude 会读取目录层级中每一级的 `CLAUDE.md` 文件，所以子目录中的规则只适用于该路径下的文件。更多信息参见 [memory 文档](https://code.claude.com/docs/en/memory)。

对于不希望应用到常规 Claude Code 会话、仅审查相关的指导，请使用 [`REVIEW.md`](#reviewmd)。

### REVIEW.md

**`REVIEW.md` 是放在仓库根目录的文件，用于覆盖 Code Review 在你仓库上的行为。** 其内容以最高优先级指令块的形式注入审查流水线中每个智能体的 system prompt，优先于默认审查指导。

**由于它是原样粘贴的，`REVIEW.md` 是纯指令文本：** [`@` 导入语法](https://code.claude.com/docs/en/memory#import-additional-files)不会被展开，引用的文件不会被读入 prompt。你需要把希望执行的规则直接写在文件中。

#### 可调节的内容

`REVIEW.md` 是自由格式的 markdown，任何你能表达为审查指令的内容都可以放入。以下模式在实践中影响最大：

**严重程度重新定义：** 为你的仓库重新定义 🔴 Important 的含义。默认校准针对生产代码；文档仓库、配置仓库或原型可能需要更窄的定义。明确说明哪些类别的发现是 Important，哪些最多是 Nit。也可以反向升级，例如将所有 `CLAUDE.md` 违规视为 Important 而非默认的 Nit。

**Nit 数量上限：** 限制单次审查发布的 🟡 Nit 评论数量。散文和配置文件永远有打磨空间。设定上限如"最多报告五条 Nit，其余在汇总中以计数形式提及"可以保持审查的可操作性。

**跳过规则：** 列出 Claude 不应发布发现的路径、分支模式和发现类别。常见候选项包括生成代码、lock 文件、vendored 依赖和机器生成的分支，以及 CI 已强制执行的内容（如 lint 或拼写检查）。对于需要部分审查但不需要全面检查的路径，设置更高的门槛而非完全跳过："在 `scripts/` 中，仅在几乎确定且严重时才报告。"

**仓库特定检查：** 添加你希望在每个 PR 上都检查的规则，例如"新增 API 路由必须有集成测试。"由于 `REVIEW.md` 以最高优先级注入，这些规则比放在长 `CLAUDE.md` 中更可靠地生效。

**验证门槛：** 要求在发布某类发现前提供证据。例如，"行为声明需要引用源代码中的 `file:line`，而不是从命名推断"可以减少让作者白费功夫的误报。

**再次审查收敛：** 告诉 Claude 在 PR 已被审查过的情况下如何表现。规则如"第一次审查后，压制新的 Nit，只发布 Important 发现"可以防止一行修复在风格上被反复审查。

**汇总格式：** 要求审查正文以一行统计开头，如 `2 factual, 4 style`，如果没有实质性问题则以"no factual issues"开头。作者希望在看到细节之前了解工作的全貌。

#### 示例

这个 `REVIEW.md` 为后端服务重新校准严重程度、设置 Nit 上限、跳过生成文件，并添加仓库特定检查。

```markdown
# Review instructions

## What Important means here

Reserve Important for findings that would break behavior, leak data,
or block a rollback: incorrect logic, unscoped database queries, PII
in logs or error messages, and migrations that aren't backward
compatible. Style, naming, and refactoring suggestions are Nit at
most.

## Cap the nits

Report at most five Nits per review. If you found more, say "plus N
similar items" in the summary instead of posting them inline. If
everything you found is a Nit, lead the summary with "No blocking
issues."

## Do not report

- Anything CI already enforces: lint, formatting, type errors
- Generated files under `src/gen/` and any `*.lock` file
- Test-only code that intentionally violates production rules

## Always check

- New API routes have an integration test
- Log lines don't include email addresses, user IDs, or request bodies
- Database queries are scoped to the caller's tenant
```

#### 保持简洁

**长度有代价：冗长的 `REVIEW.md` 会稀释最重要的规则。** 只放改变审查行为的指令，通用项目上下文留给 `CLAUDE.md`。

---

## 查看用量

前往 [claude.ai/analytics/code-review](https://claude.ai/analytics/code-review) 查看组织范围内的 Code Review 活动。看板显示：

| 板块 | 内容 |
| :--- | :--- |
| PRs reviewed | 所选时间范围内每日审查的 PR 数量 |
| Cost weekly | Code Review 每周花费 |
| Feedback | 因开发者修复问题而自动关闭的审查评论数量 |
| Repository breakdown | 每个仓库的审查 PR 数和已关闭评论数 |

管理设置中的仓库表格也显示每个仓库的平均审查费用。看板费用数字是用于监控活动的估算值；精确账单金额以 Anthropic 发票为准。

---

## 定价

**Code Review 按 token 用量计费。** 每次审查平均费用 $15-25，随 PR 大小、代码库复杂度和需要验证的问题数量而变化。Code Review 通过 [usage credits](https://support.claude.com/en/articles/12429409-extra-usage-for-paid-claude-plans) 单独计费，不计入你的计划包含的用量。

**审查触发方式影响总费用：**

* **Once after PR creation**：每个 PR 运行一次
* **After every push**：每次 push 都运行，费用乘以 push 次数
* **Manual**：在有人评论 `@claude review` 之前不产生审查

在任何模式下，评论 `@claude review` 会[将 PR 订阅到 push 触发的审查](#手动触发审查)，之后每次 push 都会产生额外费用。如果只想运行一次审查而不订阅后续 push，请评论 `@claude review once`。

**费用出现在 Anthropic 账单上，无论你的组织是否为其他 Claude Code 功能使用 Amazon Bedrock 或 Google Vertex AI。** 要设置 Code Review 的月度花费上限，前往 [claude.ai/admin-settings/usage](https://claude.ai/admin-settings/usage) 配置 Claude Code Review 服务的限额。

通过[分析看板](#查看用量)中的每周费用图表或管理设置中的每仓库平均费用列来监控花费。

---

## 故障排除

**审查运行是尽力而为的。运行失败永远不会阻止你的 PR，但也不会自动重试。** 本节介绍如何从失败中恢复以及在哪里查找 check run 报告但找不到的问题。

### 重新触发失败或超时的审查

**当审查基础设施遇到内部错误或超出时间限制时，** check run 以 **Code review encountered an error** 或 **Code review timed out** 为标题完成。结论仍然是 neutral，不会阻止合并，但不会发布任何发现。

要重新运行审查，在 PR 上评论 `@claude review once`。这会启动一次全新审查而不订阅后续 push。如果 PR 已订阅 push 触发的审查，推送新提交也会启动新审查。

**GitHub Checks 标签页中的 Re-run 按钮不会重新触发 Code Review。** 请使用评论命令或新 push。

### 审查未运行且 PR 显示费用上限消息

**当组织的月度花费上限已达到时，** Code Review 会在 PR 上发一条评论解释审查被跳过。审查在下一个计费周期开始时自动恢复，或在管理员在 [claude.ai/admin-settings/usage](https://claude.ai/admin-settings/usage) 提高上限后立即恢复。

### 找到未显示为行内评论的问题

**如果 check run 标题显示发现了问题但你在 diff 上看不到行内评论，** 请查看以下位置：

* **Check run Details**：点击 Checks 标签页中 Claude Code Review 检查旁边的 **Details**。严重程度表列出所有发现及其文件、行号和摘要，不管行内评论是否被接受。
* **Files changed 注解**：打开 PR 的 **Files changed** 标签页。发现以直接附加在 diff 行上的注解形式呈现，独立于审查评论。
* **审查正文**：如果你在审查运行期间 push 到 PR，某些发现可能引用了当前 diff 中已不存在的行。这些发现出现在审查正文中 **Additional findings** 标题下，而非行内评论。

---

## 本地审查 diff

**[`/code-review` 命令](https://code.claude.com/docs/en/commands)在终端中审查 diff，无需安装 GitHub App。** 在任何 Claude Code 会话中运行即可：它报告正确性 bug 以及复用、简化和效率方面的改进建议。默认情况下，本地审查覆盖你分支超前于上游的提交加上工作区中未提交的变更。传入 `--comment` 将发现作为行内 PR 评论发布，或传入 `--fix` 在审查后将修复应用到你的工作区。

**较低的 [effort 级别](https://code.claude.com/docs/en/model-config#adjust-effort-level)返回更少但置信度更高的发现，** 而 `high` 到 `max` 提供更广的覆盖范围，可能包含不确定的发现。不带 effort 参数时，审查使用会话当前的 effort 设置。要审查默认 diff 以外的内容，传入目标：文件路径、PR 编号、分支名，或 ref 范围如 `main...my-feature`。ref 范围形式审查从 `my-feature` 合入 `main` 的 PR 所包含的已提交 diff，不受分支上游配置影响。

**`/code-review ultra --fix` 在云端运行更深入的 [ultrareview](https://code.claude.com/docs/en/ultrareview)，** 然后在结果返回你的会话时将修复应用到工作区。Ultrareview 使用自己的范围：当前分支对比仓库默认分支，加上工作区中未提交和已暂存的变更。

该命令在 v2.1.147 之前名为 `/simplify`，当时默认应用修复。从 v2.1.154 起，`/simplify` 运行一个仅清理的审查并应用修复，不查找 bug。如果你之前用 `/simplify` 脚本化 bug 查找，请切换到 `/code-review --fix`，其行为不变。

---

## 相关资源

Code Review 设计为与 Claude Code 其余部分协同工作。如果你想在开 PR 前本地运行审查、需要自托管方案，或想深入了解 `CLAUDE.md` 如何在各工具间影响 Claude 的行为，以下页面是好的起点：

* [Commands](https://code.claude.com/docs/en/commands)：在本地 Claude Code 会话中运行 `/code-review` 检查 diff
* [GitHub Actions](https://code.claude.com/docs/en/github-actions)：在自己的 GitHub Actions 工作流中运行 Claude 实现代码审查之外的自定义自动化
* [GitLab CI/CD](https://code.claude.com/docs/en/gitlab-ci-cd)：GitLab 流水线的自托管 Claude 集成
* [Memory](https://code.claude.com/docs/en/memory)：`CLAUDE.md` 文件在 Claude Code 中的工作方式
* [Analytics](https://code.claude.com/docs/en/analytics)：跟踪代码审查之外的 Claude Code 使用情况
