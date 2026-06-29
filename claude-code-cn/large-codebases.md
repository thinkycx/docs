---
title: 【译】大型代码库
tags:
  - claude-code
  - large-codebases
  - translation
create: 2026-06-28
update: 2026-06-28
author: thinkycx
category: translation
description: 介绍如何在 monorepo 或大型代码库中配置 Claude Code，通过分层 CLAUDE.md、稀疏 worktree、代码智能插件等手段，让 Claude 聚焦于当前任务涉及的代码，降低 token 消耗并提升输出质量。
refs: https://code.claude.com/docs/en/large-codebases.md
---

# 在 monorepo 或大型代码库中配置 Claude Code

> 通过分层 CLAUDE.md 文件、稀疏 worktree、代码智能插件以及按目录划分的 skill，为 monorepo 和大型单仓代码库配置 Claude Code，让 Claude 始终聚焦在你正在修改的代码上。

**大型代码库可以是拥有数百万行代码的单一仓库，也可以是包含多个 package 的 monorepo。** Claude Code 在任何规模下都能正常工作，但随着代码量增长，为小型项目调优的默认配置会把大量无关指令和文件读入上下文窗口，浪费 token 并降低 Claude 的表现。

本指南面向个人开发者和工程团队，展示如何将 Claude 的作用范围限定在当前任务涉及的那部分代码上。每一节都会注明该设置是仅保存在你本地还是提交到仓库。

## 本指南涵盖的内容

**下方表格列出了本页涉及的每项设置及其用途。** 表格后面的文件树是本页所有代码示例参照的示例 monorepo。

### 本页涉及的设置

以下设置彼此独立，可以叠加使用而非互相替代。建议先阅读[选择 Claude 的启动位置](#选择-claude-的启动位置)，因为它决定了配置文件的存放路径。[完整示例](#完整示例)展示了所有设置的组合效果。

| 我想...                                          | 使用                                                                |
| :----------------------------------------------- | :------------------------------------------------------------------ |
| 只加载当前修改的代码所需的约定，而非一个涵盖所有子系统的根文件 | 按目录分层的 [CLAUDE.md 文件](#按目录分层-claudemd-文件)            |
| 排除从不涉及的 package 的 CLAUDE.md 文件           | [`claudeMdExcludes`](#排除无关的-claudemd-文件)                     |
| 阻止 Claude 读取构建产物、生成代码和 vendor 依赖    | `permissions.deny` 中的 [`Read` 拒绝规则](#阻止读取生成和-vendor-代码) |
| 通过语言服务器查找符号定义或调用方而不是扫描文件     | [代码智能插件](#通过代码智能减少文件读取)                             |
| 让 Claude 创建 worktree 时只检出任务需要的目录     | [`worktree.sparsePaths`](#只检出需要的目录)                          |
| 在同一会话中读写兄弟 package 或另一个仓库          | [`--add-dir`](#跨-package-或跨仓库授予访问权限) 或 `additionalDirectories` |
| 为 Claude 提供只在相关时加载的特定领域流程          | 按目录划分的 [skill](#添加按目录划分的-skill)                        |
| 用一套所有人统一安装的约定替代大量分散的 CLAUDE.md   | 内部市场中的[插件](#当分层不再可扩展时集中管理约定)                    |

> **提示：** 关于在任何仓库中保持上下文精简的工作流技巧（例如[在 subagent 中执行探索](https://code.claude.com/docs/en/best-practices#use-subagents-for-investigation)以免文件读取污染主对话），参见 [Claude Code 最佳实践](https://code.claude.com/docs/en/best-practices)。要在组织中为每位开发者推送基线配置，参见[为组织设置 Claude Code](https://code.claude.com/docs/en/admin-setup)。

### 示例 monorepo

本页的示例均基于一个包含三个 package 的 monorepo。同样的模式也适用于大型单仓代码库：将示例中的 `packages/api/` 替换为你自己的子系统目录即可，例如 `src/backend/` 或 `lib/core/`。

```text
monorepo/
  CLAUDE.md                     # 根指令
  packages/
    api/
      CLAUDE.md                 # API 特定指令
      .claude/skills/
      src/
    web/
      CLAUDE.md                 # 前端特定指令
      .claude/skills/
      src/
    shared/
      CLAUDE.md                 # 共享库指令
      src/
```

## 选择 Claude 的启动位置

**你在哪里启动 `claude` 决定了 Claude 能读写哪些文件、启动时加载哪些 CLAUDE.md 文件以及应用哪些项目设置。**

| 启动位置      | 文件访问范围                   | 启动时加载的 CLAUDE.md                                               | 适用场景                         |
| :------------ | :---------------------------- | :------------------------------------------------------------------- | :------------------------------- |
| 仓库根目录     | 所有文件                      | 仅根文件；子目录文件在 Claude 读取到该目录时按需加载                    | 任务跨多个 package 或子系统       |
| 某个子目录     | 仅该子树，直到你授予更多权限    | 该目录及其所有祖先目录的 CLAUDE.md                                    | 工作范围限定在单个 package 或子系统 |

`.claude/settings.json` 中的项目设置只从你的启动目录加载，不会像 CLAUDE.md 那样从父目录继承：仓库根目录下的 `.claude/settings.json` 只在你从根目录启动时生效。

下面各节会注明其配置文件应放在仓库根目录还是你的启动子目录中，以及是否需要提交到版本控制。

## 按目录分层 CLAUDE.md 文件

**在大型代码库中，单一根目录 CLAUDE.md 往往要么膨胀到涵盖所有子系统约定（浪费上下文在无关指令上），要么太过笼统而缺乏实用性。** 将指令拆分到按目录分布的文件中，意味着 Claude 只加载全仓库通用规则以及你当前修改的代码的约定。

Claude Code 在启动时加载工作目录及所有父目录中的每个 [CLAUDE.md](https://code.claude.com/docs/en/memory) 文件，然后在读取子目录中的文件时按需加载该子目录的 CLAUDE.md。根文件设定全仓通用规则，子目录文件补充各自的规则。

常见的分层方式是两级：

* **根 `CLAUDE.md`**：全仓库通用的指令，例如代码规范、提交约定和仓库结构说明
* **子目录 `CLAUDE.md`**：特定于该区域技术栈的约定。在 monorepo 中每个 package 一个，在大型单仓中每个子系统一个（如 `src/db/` 或 `src/api/`）

将这些文件提交到仓库，让团队成员自动继承。每个目录的负责人通常维护对应文件。

根 `CLAUDE.md` 向 Claude 介绍仓库结构：

```markdown
# CLAUDE.md
This is a monorepo with three packages under packages/:

- packages/api: Node.js REST API with Express, TypeScript, and PostgreSQL
- packages/web: React frontend with Vite, TypeScript, and TailwindCSS
- packages/shared: shared TypeScript utilities used by both api and web

Run commands from the package directory, not the monorepo root.
Each package has its own tsconfig.json, package.json, and test suite.
```

子目录的 `CLAUDE.md`（以 `packages/api/CLAUDE.md` 为例）补充该区域技术栈的上下文：

```markdown
# packages/api/CLAUDE.md
This package is the REST API server.

- Run tests: `npm test` (uses Vitest)
- Run dev server: `npm run dev` (port 3001)
- Database migrations: `npm run migrate`
- Environment variables: copy `.env.example` to `.env`

API routes are in src/routes/. Each route file exports an Express router.
Database queries use Knex in src/db/. Never write raw SQL strings in route handlers.
```

当你从 `packages/api/` 启动 Claude 时，它会同时加载 `packages/api/CLAUDE.md` 和根 `CLAUDE.md`。Claude 看到本地指令和全仓规则，但不会在上下文中包含 `packages/web/` 的任何指令。

保持文件随代码和模型演进而更新的几种方式：

* **在 PR 中审查**：像对待其他文档变更一样 review CLAUDE.md 的修改，确保约定跟上代码
* **主要模型版本发布后重新审视**：为绕过旧模型局限而添加的指令，在新模型已能自动处理时就成了累赘。例如强制单文件重构的规则，在模型能力提升后可以删除
* **添加 Stop hook 来自动建议更新**：[`Stop` hook](https://code.claude.com/docs/en/hooks#stop) 在 Claude 完成响应时接收会话记录路径，脚本可以审查该会话并在暴露的问题还新鲜时建议 CLAUDE.md 更新

更多关于 CLAUDE.md 文件如何加载和交互的信息，参见[记忆与项目指令](https://code.claude.com/docs/en/memory)。

### 按目录 CLAUDE.md 与路径作用域规则的选择

按目录的 `CLAUDE.md` 文件和 `.claude/rules/` 下的[路径作用域规则](https://code.claude.com/docs/en/memory#path-specific-rules)都能将指令定向到代码树的特定部分。它们的区别在于文件位置和加载时机。

| 方式                           | 文件位置                     | 加载时机                                          | 适用场景                                          |
| :----------------------------- | :--------------------------- | :----------------------------------------------- | :----------------------------------------------- |
| 按目录 `CLAUDE.md`             | 在目录内部，紧邻代码          | 从该目录启动时立即加载，或 Claude 读取该目录文件时按需加载 | 目录负责人维护各自约定；指令与代码一同版本控制       |
| `.claude/rules/` 中的路径作用域规则 | 集中在仓库根目录的 `.claude/` | Claude 处理匹配规则 `paths:` glob 的文件时加载     | 想将所有约定集中管理，或同一规则适用于多个分散路径   |

关于包含 skill 在内的完整对比，参见[对比相似功能](https://code.claude.com/docs/en/features-overview#compare-similar-features)。

### 排除无关的 CLAUDE.md 文件

**当你从仓库根目录启动 Claude 时，每个子目录的 CLAUDE.md 会在 Claude 读取该目录中的文件时自动加载。** `claudeMdExcludes` 设置通过路径或 glob 模式跳过特定文件，使其永远不会被加载。

适用于你从不涉及的目录，例如其他团队的 package、遗留代码或 vendor 子树。排除列表是静态的，不是按任务切换的开关。如果今天想关注一个 package 明天关注另一个，应该改为[从该 package 目录启动 Claude](#选择-claude-的启动位置)。

如果只想为你自己设置排除，将配置放在 `.claude/settings.local.json` 中。模式使用 glob 语法匹配绝对路径，因此相对风格的模式需要以 `**/` 开头以匹配树中任意位置：

```json
// .claude/settings.local.json
{
  "claudeMdExcludes": [
    "**/packages/admin-dashboard/**",
    "**/packages/legacy-*/**"
  ]
}
```

这会跳过这些 package 下的所有 CLAUDE.md 和规则文件。根 CLAUDE.md 和你实际工作的 package 仍正常加载。

其他常见模式：

* `"**/packages/*/CLAUDE.md"`：排除每个 package 的 CLAUDE.md，保留根文件
* `"**/packages/web/**"`：排除 web package 下的所有内容，包括规则
* `"/home/user/monorepo/legacy/CLAUDE.md"`：按绝对路径排除某个特定文件

托管策略 CLAUDE.md 文件不可被排除，组织级指令始终生效。`claudeMdExcludes` 可在任何[设置范围](https://code.claude.com/docs/en/settings#configuration-scopes)设定：用户、项目、本地或托管。数组在各范围间合并，因此团队可以设置项目级默认值，个人可以添加本地覆盖。

完整的排除文档参见[排除特定 CLAUDE.md 文件](https://code.claude.com/docs/en/memory#exclude-specific-claude-md-files)。

## 减少 Claude 的读取量

**指令只是上下文中的一部分。文件读取是随代码库增长而增加的另一项开销。** 以下设置阻止读取无关路径，并用语言服务器查找替代穷举式文件扫描。

### 阻止读取生成和 vendor 代码

Claude 的内容搜索默认遵守 `.gitignore`，因此已经列在其中的路径（如 `node_modules/`、`dist/`、`build/`）无需额外配置即会被排除。

对于已提交到版本控制的路径（如 vendor SDK 或已提交的生成代码），在 `permissions.deny` 中添加 `Read` 拒绝规则，即使搜索结果列出了这些文件也阻止 Claude 打开。

要对仓库中所有人生效，将规则提交到 `.claude/settings.json`。要仅个人使用，放在 `.claude/settings.local.json` 中：

```json
// .claude/settings.json
{
  "permissions": {
    "deny": [
      "Read(./**/dist/**)",
      "Read(./**/build/**)",
      "Read(./**/*.generated.*)",
      "Read(./vendor/**)"
    ]
  }
}
```

拒绝规则覆盖 Claude 的内置文件工具和识别的 Bash 文件命令（包括 `cat`、`head`、`grep`、`find`），当传入被拒绝的路径时生效。它们不会从递归搜索输出中过滤被拒绝的路径，也不覆盖自行打开文件的任意子进程。完整的模式语法参见[Read 和 Edit 权限规则](https://code.claude.com/docs/en/permissions#read-and-edit)。

### 通过代码智能减少文件读取

**在大型代码库中，查找符号的定义或使用位置可能需要大量文件读取和 grep 调用。** [代码智能插件](https://code.claude.com/docs/en/discover-plugins#code-intelligence)将 Claude 连接到语言服务器，使其能直接跳转到定义、查找引用和显示类型错误，而不是扫描整棵树。

官方市场提供 TypeScript、Python、Go、Rust 等常见语言的插件。以下示例安装 TypeScript 插件：

```shell
/plugin install typescript-lsp@claude-plugins-official
```

要为仓库中所有人启用插件（而非仅自己安装），将其添加到 [`enabledPlugins` 项目设置](https://code.claude.com/docs/en/settings#plugin-settings)。

代码智能插件要求每台开发者机器上安装对应语言的语言服务器二进制文件。参见[各语言所需的二进制文件](https://code.claude.com/docs/en/discover-plugins#code-intelligence)。从官方市场安装需要访问 GitHub（市场的托管地）。在受限网络环境中，可以[从内部 Git 主机或本地路径添加市场](https://code.claude.com/docs/en/discover-plugins#add-from-other-git-hosts)。

代码智能与上文的 `claudeMdExcludes` 和 `Read` 拒绝规则搭配使用效果更佳：后者将无关内容排除出上下文，代码智能则防止 Claude 为定位定义而逐文件阅读剩余内容。

## 限定 worktree 和文件访问范围

**以下设置控制 worktree 中磁盘上的内容以及 Claude 可以读写哪些超出启动点的目录。**

### 只检出需要的目录

`--worktree` 标志在新的 git worktree 中启动会话，使变更与主检出隔离。默认情况下会检出整个仓库。在大型仓库中，`worktree.sparsePaths` 设置使用 git sparse-checkout 只将列出的目录和根级文件写入磁盘，使 worktree 启动更快、占用更少空间。

如果此目录中的所有人都需要相同路径，将设置提交到 `.claude/settings.json`。要添加个人路径，使用 `.claude/settings.local.json`：列表在各范围间合并，本地文件可以添加路径但不能移除：

```json
// .claude/settings.json
{
  "worktree": {
    "sparsePaths": [
      ".claude",
      "packages/api",
      "packages/shared"
    ]
  }
}
```

当 Claude 创建 worktree 时，只检出 `.claude/`、`packages/api/` 和 `packages/shared/`，而非完整代码树。`sparsePaths` 中的路径相对于仓库根目录，无论你从哪个子目录启动 Claude。

这对 [subagent worktree 隔离](https://code.claude.com/docs/en/worktrees#isolate-subagents-with-worktrees)特别有用。Subagent 是为子任务生成的并行 Claude 实例，每个在 worktree 中运行的实例都获得轻量级检出而非完整代码树。一个会话中的所有 worktree 共享相同的 `sparsePaths`，因此如果一个 subagent 需要 `packages/api/` 而另一个需要 `packages/web/`，将两者都列出。

在 `sparsePaths` 中列出目录而非单独文件。根级文件（如 `package.json`、`tsconfig.base.json` 和 lock 文件）始终与你列出的目录一起检出。根级目录不会自动检出，因此如果需要在 worktree 中使用仓库根目录的 `.claude/settings.json`、`.claude/rules/` 或 `.claude/skills/`，需要在列表中包含 `.claude`。

要避免在多个 worktree 间重复大目录（如 `node_modules`），将 `sparsePaths` 与同一 `.claude/settings.json` 中的 `symlinkDirectories` 搭配使用：

```json
// .claude/settings.json
{
  "worktree": {
    "sparsePaths": [
      ".claude",
      "packages/api",
      "packages/shared"
    ],
    "symlinkDirectories": [
      "node_modules"
    ]
  }
}
```

这会从每个 worktree 的 `node_modules/` 创建一个指向主仓库副本的符号链接，而非在磁盘上复制。

> **注意：** `sparsePaths` 和 `symlinkDirectories` 设置在创建 worktree 之前从你的启动目录读取。创建后，会话的工作目录是 worktree 根目录而非你的启动子目录。因此 worktree 内部的项目设置从 worktree 根目录的 `.claude/settings.json` 加载（即仓库根目录文件的检出副本）。将需要在 worktree 中生效的其他设置（如权限规则或 hook）放在仓库根目录的 `.claude/settings.json` 中。

完整的 worktree 设置参考见 [Worktree 设置](https://code.claude.com/docs/en/settings#worktree-settings)。

### 跨 package 或跨仓库授予访问权限

**本节适用于从子目录启动 Claude，或任务跨多个检出的场景。** 如果你从仓库根目录启动单一大型代码树，Claude 已经可以访问所有文件，可以跳过此节。

当你从 `packages/api/` 启动 Claude 时，它只能读写该目录中的文件。如果任务需要跨 package 修改（例如更新 `api` 和 `web` 都导入的 shared 类型），你需要授予对兄弟目录的访问权限。同样的机制也适用于单独检出的仓库。

`.claude/settings.json` 中的 `additionalDirectories` 设置授予 Claude 对工作目录之外目录的访问权限：

```json
// .claude/settings.json
{
  "permissions": {
    "additionalDirectories": [
      "../shared",
      "../web"
    ]
  }
}
```

相对路径基于你启动 Claude 的目录解析。使用此配置，Claude 可以在从 `packages/api/` 工作时读写 `packages/shared/` 和 `packages/web/` 中的文件。

也可以在启动时传入 `--add-dir` 而无需编辑设置：

```bash
claude --add-dir ../shared
```

无论如何添加目录，Claude 都可以读写其中的文件。该目录的 CLAUDE.md、`.claude/rules/` 文件和 skill 是否也会加载取决于添加方式：

| 添加方式                            | 是否加载 CLAUDE.md 和规则       | 是否加载 skill |
| :--------------------------------- | :----------------------------- | :------------ |
| `additionalDirectories` 设置        | 不加载                          | 不加载        |
| `--add-dir` 标志或 `/add-dir` 命令  | 仅在设置下方环境变量时加载       | 加载          |

要从通过 `--add-dir` 或 `/add-dir` 添加的目录加载 CLAUDE.md 和规则文件，设置 `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` 环境变量：

```bash
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1 claude --add-dir ../shared
```

该环境变量对 `additionalDirectories` 设置中列出的目录无效。详见[从额外目录加载](https://code.claude.com/docs/en/memory#load-from-additional-directories)。

## 添加按目录划分的 skill

**任何子目录都可以定义限定于其技术栈的 [skill](https://code.claude.com/docs/en/skills)。** Skill 在 Claude 判断相关时按需加载，因此 API 特定的工具不会在前端工作时占用上下文。

Skill 位于目录内的 `.claude/skills/` 下。将它们与该区域的代码一起提交，让所有克隆仓库的人都能使用。在 monorepo 中可以是每个 package 一组 skill，在大型单仓中可以是每个子系统一组（如 `src/db/.claude/skills/`）。

在子目录内创建 skill 目录：

```bash
mkdir -p packages/api/.claude/skills/api-testing
```

然后在该目录中编写 `SKILL.md`，以 `packages/api/.claude/skills/api-testing/SKILL.md` 为例。这个示例教 Claude API package 的测试模式：

```markdown
---
name: api-testing
description: Testing patterns for the API package. Use when writing or modifying tests in packages/api/.
---

## Test structure

Tests are in `src/__tests__/` mirroring the `src/` directory structure.
Each route file has a corresponding `.test.ts` file.

## Running tests

- All tests: `npm test`
- Single file: `npm test -- src/__tests__/routes/users.test.ts`
- Watch mode: `npm test -- --watch`

## Test utilities

- `src/__tests__/helpers/db.ts`: provides `setupTestDb()` and `teardownTestDb()` for database tests
- `src/__tests__/helpers/auth.ts`: provides `createTestUser()` and `getAuthToken()` for authenticated endpoints

## Patterns

- Use `supertest` for HTTP assertions, not raw fetch
- Always wrap database tests in a transaction that rolls back
- Mock external services in `src/__tests__/mocks/`
```

不同子目录以同样方式持有不同 skill：`packages/web/.claude/skills/component-patterns/` 描述前端组件约定。当 Claude 处理 `packages/api/` 中的文件时加载 api-testing skill，处理 `packages/web/` 时加载 component-patterns。两个目录的 skill 不会在对方任务中加载。

也可以通过文件模式而非放置位置来限定 skill 范围。[`paths` frontmatter 字段](https://code.claude.com/docs/en/skills#frontmatter-reference)接受 glob 模式，Claude 只在处理匹配文件时自动加载该 skill。适用于放在仓库根目录 `.claude/skills/` 但只适用于特定文件的 skill，例如限定为 `**/migrations/**` 的数据库迁移 skill。

更多关于创建和组织 skill 的信息，参见 [Skills](https://code.claude.com/docs/en/skills)。

### 保持 skill 的可发现性

**skill 分散在多个目录时，Claude 可选列表可能会变大。** Claude 通过读取所有已发现 skill 的名称和描述来选择 skill，只有被选中 skill 的完整内容才会加载到上下文。

哪些 skill 在范围内取决于你的启动位置：

* **从子目录启动（如 `packages/api/`）**：该目录、到仓库根的每个父目录、以及用户和企业级的 skill
* **从仓库根启动**：会话期间 Claude 接触的每个子目录的 skill，可能累积到数百个
* **添加兄弟目录后（使用 [`--add-dir`](#跨-package-或跨仓库授予访问权限)）**：该兄弟的 skill 也会加载。`additionalDirectories` 设置只授予文件访问权限，不加载 skill

名称始终加载，但[当 skill 很多时描述会被截短](https://code.claude.com/docs/en/skills#skill-descriptions-are-cut-short)，这可能去掉 Claude 判断 skill 是否适用的关键词。保持描述简短，以请求中可能包含的词开头，例如 "writing or modifying tests in `packages/api/`"。

对于多个目录共享的 skill（如 PR 约定或部署检查清单），放在仓库根的 `.claude/skills/` 中，这样从任何启动目录都能加载。当共享 skill 需要独立版本历史或必须跨仓库工作时，将其打包为[插件](https://code.claude.com/docs/en/plugins)。插件 skill 使用 `plugin-name:skill-name` 命名空间，不会与按目录的 skill 冲突。

要查找哪些 skill 未被使用，启用 OpenTelemetry [日志导出器](https://code.claude.com/docs/en/monitoring-usage)并设置 `OTEL_LOG_TOOL_DETAILS=1`，使 skill 名称原样记录。[`skill_activated` 事件](https://code.claude.com/docs/en/monitoring-usage#skill-activated-event)在 `skill.name` 属性中记录每次调用，`invocation_trigger` 记录是命令、Claude 还是嵌套 skill 触发的调用，帮你判断哪些可以合并或淘汰。

## 当分层不再可扩展时集中管理约定

**随着代码库增长，按目录的 CLAUDE.md 文件可能变得难以治理。** 约定发生漂移、文件变得过时、没人负责根文件。解决这个问题通常是维护仓库 Claude Code 配置的团队的责任，而非每位开发者。

将约定和参考内容从始终加载的 CLAUDE.md 移到按需加载的机制中：

* [Skills](https://code.claude.com/docs/en/skills)：Claude 仅在与任务相关时加载的参考材料
* [Plugins](https://code.claude.com/docs/en/plugins)：平台团队集中拥有的版本化 skill、hook 和命令包
* [MCP servers](https://code.claude.com/docs/en/mcp)：如果组织已运行代码搜索或 RAG 索引，将其暴露为 MCP 工具让 Claude 查询，而不是直接读取文件

参见[服务器管理或端点管理设置](https://code.claude.com/docs/en/server-managed-settings#choose-between-server-managed-and-endpoint-managed-settings)了解平台团队如何集中执行这些设置。

### 在会话启动时推荐正确的插件

一旦约定存在于插件中，在代码树不熟悉的部分启动 Claude 的团队成员就没有信号知道该区域的负责人维护哪个插件。[`SessionStart` hook](https://code.claude.com/docs/en/hooks#sessionstart) 可以弥补这个差距——hook 输出到 stdout 的内容会在第一个提示之前添加到 Claude 的上下文中。

例如，你可以编写一个脚本从 [hook 输入](https://code.claude.com/docs/en/hooks#common-input-fields)中读取启动目录，在提交到仓库的路径-插件映射中查找，并打印推荐内容让 Claude 在第一次回复中转达。参见[使用 hook 自动化操作](https://code.claude.com/docs/en/hooks-guide)编写和注册 hook。

## 完整示例

**以下组合配置使用 monorepo 布局。** 相同的文件适用于大型单仓中的任何子目录。项目设置只从你启动 Claude 的目录加载，因此每个子目录的 `.claude/settings.json` 必须是自包含的，而非在根文件上分层。

以下示例将 `worktree`、`additionalDirectories` 和 `Read` 拒绝规则提交到 `.claude/settings.json`，使 `packages/api/` 中的每位开发者获得相同的兄弟访问、稀疏路径和排除。以下是 `packages/api/` 的已提交设置：

```json
// packages/api/.claude/settings.json
{
  "worktree": {
    "sparsePaths": [
      ".claude",
      "packages/api",
      "packages/shared"
    ],
    "symlinkDirectories": [
      "node_modules"
    ]
  },
  "permissions": {
    "additionalDirectories": [
      "../shared"
    ],
    "deny": [
      "Read(./**/dist/**)",
      "Read(./**/build/**)"
    ]
  }
}
```

由于此会话从 `packages/api/` 启动，兄弟 package 的 CLAUDE.md 文件已在范围之外，这里不需要 `claudeMdExcludes`。如果你也从根目录启动会话，将其添加到仓库根目录的 `.claude/settings.local.json`。

`additionalDirectories` 条目在你直接从 `packages/api/` 启动 Claude 时生效。在从此会话创建的 worktree 内部，工作目录是 worktree 根目录，因此此设置文件不会加载。兄弟 package 在 worktree 中已经可达无需此设置，但拒绝规则需要在仓库根目录的 `.claude/settings.json` 中有第二个副本以便 worktree 会话能使用：

```json
// .claude/settings.json
{
  "permissions": {
    "deny": [
      "Read(./**/dist/**)",
      "Read(./**/build/**)"
    ]
  }
}
```

设置完成后，仓库的布局如下：

```text
monorepo/
  CLAUDE.md
  .claude/settings.json                           # worktree 会话的拒绝规则
  packages/
    api/
      CLAUDE.md
      .claude/settings.json                       # worktree、additionalDirectories、拒绝规则
      .claude/skills/api-testing/SKILL.md
    web/
      CLAUDE.md
      .claude/skills/component-patterns/SKILL.md
    shared/
      CLAUDE.md
```

使用此配置，从 `packages/api/` 启动 Claude：

* 加载根 CLAUDE.md 和 `packages/api/CLAUDE.md`，跳过 `packages/web/CLAUDE.md`
* 可读写 `packages/api/` 和 `packages/shared/` 中的文件
* 跳过 `packages/api/` 下 `dist/` 和 `build/` 中的构建产物
* 按需提供 api-testing skill
* 创建包含 `.claude/`、`packages/api/`、`packages/shared/` 和根级文件的 worktree，并从根设置文件应用拒绝规则

## 规划跨 package 的变更范围和顺序

**上述配置控制 Claude 看到什么。当单个变更涉及多个 package 时（如更新共享类型及其所有调用方），你如何规划和排序任务也影响结果。**

两种技巧有助于保持跨 package 变更的一致性：

* **在一个会话中给 Claude 完整的变更**：将共享编辑及其调用方一起交给 Claude，保持每处编辑背后的决策一致，而不是逐 package 重新推导
* **编辑前将计划保存到文件**：先[规划](https://code.claude.com/docs/en/best-practices#explore-first-then-plan-then-code)，让 Claude 将计划写入仓库中的 markdown 文件。长时间的跨 package 会话会在过程中[压缩上下文](https://code.claude.com/docs/en/context-window#what-survives-compaction)，保存的计划能在对话历史可能丢失时存活

## 下一步

配置就位后，你可以进一步优化：

* 使用 [hooks](https://code.claude.com/docs/en/hooks-guide) 在 Claude 编辑文件后运行按目录的 linter 或类型检查
* 查阅[管理成本](https://code.claude.com/docs/en/costs)了解代码库规模如何影响 token 使用，以及如何在更大范围推广前设置花费限制
* 阅读 Claude 博客上的[Claude Code 如何在大型代码库中工作](https://claude.com/blog/how-claude-code-works-in-large-codebases-best-practices-and-where-to-start)，了解高于本页逐仓库配置的组织级推广模式和所有权模型
