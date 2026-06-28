---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】Skills 扩展
description: Skills 是 Claude Code 的可复用能力扩展机制。通过编写 SKILL.md 文件定义指令，Claude 会在相关场景自动加载或由用户手动触发，支持动态上下文注入、子 Agent 运行、参数传递等高级模式。
category: translation
tags: [claude-code, skills, translation]
refs:
  - https://code.claude.com/docs/en/skills.md
---

# 用 Skills 扩展 Claude 的能力

> 在 Claude Code 中创建、管理和分享 Skill，扩展 Claude 的能力边界。包括自定义命令和内置 Skill。

**Skill 是 Claude 的可复用能力模块，写一个 `SKILL.md` 文件就能让 Claude 多一项技能。** Claude 会在相关场景自动调用 Skill，你也可以通过 `/skill-name` 手动触发。

什么时候该创建 Skill？当你反复粘贴同一段指令、清单或多步流程到对话中时；或者当 CLAUDE.md 里某段内容已经从"事实描述"膨胀成"操作流程"时。与 CLAUDE.md 不同，Skill 的内容只在被使用时才加载到上下文，因此长篇参考材料在用到之前几乎不消耗 Token。

> [!NOTE]
> 内置命令（如 `/help`、`/compact`）和内置 Skill（如 `/debug`、`/code-review`）的详细列表参见 [命令参考](https://code.claude.com/docs/en/commands)。
>
> **自定义命令已合并进 Skills 体系。** `.claude/commands/deploy.md` 和 `.claude/skills/deploy/SKILL.md` 都会创建 `/deploy`，功能完全一致。已有的 `.claude/commands/` 文件继续生效。Skills 额外支持：目录内放辅助文件、用 frontmatter [控制谁来触发](#控制谁来触发-skill)、以及 Claude 自动按需加载。

Claude Code Skills 遵循 [Agent Skills](https://agentskills.io) 开放标准，可跨多种 AI 工具使用。Claude Code 在此标准上扩展了[调用控制](#控制谁来触发-skill)、[子 Agent 执行](#在子-agent-中运行-skill)和[动态上下文注入](#注入动态上下文)等能力。

## 内置 Skills

**Claude Code 自带一组内置 Skill，每个会话默认可用（可通过 [`disableBundledSkills`](https://code.claude.com/docs/en/settings#available-settings) 设置禁用）。** 包括 `/code-review`、`/batch`、`/debug`、`/loop`、`/claude-api` 等。与大多数执行固定逻辑的内置命令不同，内置 Skill 是基于 Prompt 的：它们给 Claude 详细指令，由 Claude 自主调度完成工作。调用方式和普通 Skill 一样，输入 `/` 加 Skill 名即可。

内置 Skill 与内置命令一同列在 [命令参考](https://code.claude.com/docs/en/commands) 中，Purpose 列标注 **Skill**。

### 运行和验证你的应用

**三个内置 Skill 协同工作，启动应用并直接在运行中的应用上验证变更，而非仅靠测试。**

| Skill | 用途 |
| :--- | :--- |
| `/run` | 启动并驱动应用，查看变更是否生效 |
| `/verify` | 构建并运行应用，确认代码变更符合预期，不退回到测试或类型检查 |
| `/run-skill-generator` | 教会 `/run` 和 `/verify` 如何构建和启动你的项目 |

以上三个 Skill 需要 Claude Code v2.1.145 或更高版本。

`/run` 和 `/verify` 开箱即用，会根据项目类型（CLI、服务器、TUI、浏览器驱动）和 README、`package.json`、`Makefile` 等自动推断启动方式。但对于需要数据库、env 文件、图形界面或多步构建的项目，这种推断不可靠。

`/run-skill-generator` 用于记录完整的启动方案。它从干净环境启动你的应用，捕获成功的步骤（安装命令、环境变量、启动脚本），并提交为项目级 Skill `.claude/skills/run-<name>/`。之后 `/run`、`/verify` 以及仓库中的其他 Agent 都会按照记录的方案执行，无需重新探索。每个项目运行一次即可，构建或启动流程变更时再次运行。

## 快速开始

### 创建你的第一个 Skill

**以下示例创建一个 Skill，总结 Git 仓库中未提交的变更并标记风险项。** 它在 Claude 读取内容之前就把实时 diff 拉进 Prompt，因此响应基于真实的工作区状态，而非 Claude 从打开文件中的猜测。Claude 会在你问到变更时自动加载该 Skill，也可以用 `/summarize-changes` 直接调用。

**第一步：创建 Skill 目录**

在个人 Skills 文件夹中创建目录。个人 Skill 在你所有项目中可用。

```bash
mkdir -p ~/.claude/skills/summarize-changes
```

**第二步：编写 SKILL.md**

每个 Skill 需要一个 `SKILL.md` 文件，包含两部分：`---` 标记之间的 YAML frontmatter（告诉 Claude 何时使用该 Skill），以及 Markdown 内容（Claude 执行 Skill 时遵循的指令）。目录名即为你输入的命令名，`description` 帮助 Claude 判断何时自动加载。

保存到 `~/.claude/skills/summarize-changes/SKILL.md`：

```yaml
---
description: Summarizes uncommitted changes and flags anything risky. Use when the user asks what changed, wants a commit message, or asks to review their diff.
---

## Current changes

!`git diff HEAD`

## Instructions

Summarize the changes above in two or three bullet points, then list any risks you notice such as missing error handling, hardcoded values, or tests that need updating. If the diff is empty, say there are no uncommitted changes.
```

`` !`git diff HEAD` `` 这行使用了[动态上下文注入](#注入动态上下文)：Claude Code 先执行命令，把输出替换到该位置，Claude 看到的 Skill 内容中已经内联了当前 diff。

**第三步：测试 Skill**

打开一个 Git 项目，随意编辑一个文件，运行 `claude` 启动 Claude Code。两种方式测试：

**让 Claude 自动调用**——说一句匹配 description 的话：

```text
What did I change?
```

**或直接调用**：

```text
/summarize-changes
```

两种方式下 Claude 都会返回一段简短的变更总结和风险列表。

### Skill 的存放位置

**存放位置决定了 Skill 的可见范围。**

| 层级 | 路径 | 作用范围 |
| :--- | :--- | :--- |
| 企业级 | 参见 [受管设置](https://code.claude.com/docs/en/settings#settings-files) | 组织内所有用户 |
| 个人级 | `~/.claude/skills/<skill-name>/SKILL.md` | 你的所有项目 |
| 项目级 | `.claude/skills/<skill-name>/SKILL.md` | 仅当前项目 |
| 插件级 | `<plugin>/skills/<skill-name>/SKILL.md` | 启用了该插件的地方 |

**同名 Skill 的优先级：企业级 > 个人级 > 项目级。** 任何层级的 Skill 也会覆盖同名的内置 Skill。例如项目 `.claude/skills/` 中的 `code-review` 会替换内置的 `/code-review`。插件 Skill 使用 `plugin-name:skill-name` 命名空间，不会与其他层级冲突。如果 `.claude/commands/` 中有同名文件，Skill 优先。

**嵌套目录中的 Skill 也会被发现。** 当 Claude 读取或编辑子目录中的文件时，该子目录的 `.claude/skills/` 下的 Skill 变为可用。这让 Monorepo 中的子包可以提供自己的 Skill。

如果嵌套 Skill 与其他 Skill 同名，两者都保留可用。例如项目根目录和 `apps/web/.claude/skills/` 下都有 `deploy` Skill：

* 嵌套的那个显示为目录限定名 `apps/web:deploy`
* 其描述说明适用于哪个目录
* Claude 自动选择与当前操作文件匹配的变体

输入 `/deploy` 运行项目根目录的 Skill，输入 `/apps/web:deploy` 显式运行嵌套变体。

> [!NOTE]
> 在 Skill 文件夹中添加 `.claude-plugin/plugin.json`，它会作为名为 `<name>@skills-dir` 的[插件](https://code.claude.com/docs/en/plugins-reference#skills-directory-plugins)加载，可以打包 Agent、Hook 和 MCP Server。在项目 `.claude/skills/` 中，需要先接受工作区信任对话框。

#### 实时变更检测

**Claude Code 会监视 Skill 目录的文件变化。** 在 `~/.claude/skills/`、项目 `.claude/skills/`、或 `--add-dir` 目录的 `.claude/skills/` 下添加、编辑或删除 Skill，会在当前会话中即时生效，无需重启。如果在会话启动后才创建了一个顶层 Skills 目录，则需要重启 Claude Code 才能监视新目录。

> [!NOTE]
> 实时变更检测仅覆盖 `SKILL.md` 文本。对于同时作为[插件](https://code.claude.com/docs/en/plugins-reference#skills-directory-plugins)的 Skill 文件夹，`hooks/`、`.mcp.json`、`agents/`、`output-styles/` 的变更需要 `/reload-plugins` 才能生效。

#### 父目录和嵌套目录的自动发现

**项目 Skill 从启动目录的 `.claude/skills/` 以及向上到仓库根目录的每个父目录加载。** 在子目录启动 Claude 仍能获取根目录定义的 Skill。当你操作子目录的文件时，Claude Code 也会按需发现嵌套的 `.claude/skills/` 目录中的 Skill。例如编辑 `packages/frontend/` 中的文件时，也会查找 `packages/frontend/.claude/skills/`。这支持子包有自己 Skill 的 Monorepo 场景。

每个 Skill 是一个以 `SKILL.md` 为入口的目录：

```text
my-skill/
├── SKILL.md           # 主指令文件（必需）
├── template.md        # 模板供 Claude 填充
├── examples/
│   └── sample.md      # 示例输出展示预期格式
└── scripts/
    └── validate.sh    # Claude 可执行的脚本
```

`SKILL.md` 是必需的主指令文件。其他文件可选，用于构建更强大的 Skill：供 Claude 填充的模板、展示预期格式的示例输出、Claude 可执行的脚本、或详细参考文档。在 `SKILL.md` 中引用这些文件，让 Claude 知道它们的内容和何时加载。详见[添加辅助文件](#添加辅助文件)。

> [!NOTE]
> `.claude/commands/` 中的文件仍然有效，支持相同的 [frontmatter](#frontmatter-参考)。推荐使用 Skills，因为它们支持辅助文件等额外功能。

#### 来自附加目录的 Skills

**`--add-dir` 标志和 `/add-dir` 命令[授予文件访问权限](https://code.claude.com/docs/en/permissions#additional-directories-grant-file-access-not-configuration)而非配置发现，但 Skills 是例外：** 附加目录中的 `.claude/skills/` 会自动加载。此例外仅适用于 `--add-dir` 和 `/add-dir`。`settings.json` 中的 `permissions.additionalDirectories` 设置仅授予文件访问权限，不加载 Skills。关于会话中编辑如何生效，见[实时变更检测](#实时变更检测)。

其他 `.claude/` 配置（如 commands 和 output styles）不会从附加目录加载。完整列表见 [exceptions 表](https://code.claude.com/docs/en/permissions#additional-directories-grant-file-access-not-configuration)。

> [!NOTE]
> `--add-dir` 目录的 CLAUDE.md 文件默认不加载。要加载它们，设置 `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`。参见[从附加目录加载](https://code.claude.com/docs/en/memory#load-from-additional-directories)。

## 配置 Skills

**Skills 通过 `SKILL.md` 顶部的 YAML frontmatter 和后续的 Markdown 内容进行配置。**

### Skill 内容的类型

Skill 文件可以包含任何指令，但思考调用方式有助于确定内容方向：

**参考型内容**——为 Claude 当前工作添加知识。包括规范、模式、风格指南、领域知识。这类内容内联运行，Claude 可以结合对话上下文使用。

```yaml
---
name: api-conventions
description: API design patterns for this codebase
---

When writing API endpoints:
- Use RESTful naming conventions
- Return consistent error formats
- Include request validation
```

**任务型内容**——给 Claude 针对特定操作的分步指令，如部署、提交或代码生成。通常希望通过 `/skill-name` 手动触发而非让 Claude 自动决定。添加 `disable-model-invocation: true` 可防止 Claude 自动触发。

```yaml
---
name: deploy
description: Deploy the application to production
context: fork
disable-model-invocation: true
---

Deploy the application:
1. Run the test suite
2. Build the application
3. Push to the deployment target
```

**保持 Skill 正文简洁。** 一旦 Skill 加载，其内容会[在整个会话中持续存在](#skill-内容生命周期)，每一行都是持续的 Token 开销。描述"做什么"而非解释"怎么做"或"为什么"，与 [CLAUDE.md 的精简原则](https://code.claude.com/docs/en/best-practices#write-an-effective-claude-md)一致。

### Frontmatter 参考

**通过 `SKILL.md` 文件顶部 `---` 标记之间的 YAML frontmatter 字段配置 Skill 行为：**

```yaml
---
name: my-skill
description: What this skill does
disable-model-invocation: true
allowed-tools: Read Grep
---

Your skill instructions here...
```

所有字段均为可选。仅 `description` 被推荐，以便 Claude 知道何时使用该 Skill。

| 字段 | 是否必需 | 说明 |
| :--- | :--- | :--- |
| `name` | 否 | 在 Skill 列表中显示的名称，默认为目录名。与输入的命令名不同，详见[命令名的来源](#skill-的命令名来源) |
| `description` | 推荐 | Skill 的功能和使用场景。Claude 据此决定何时应用。未设时使用 Markdown 内容的第一段。关键用例放最前面：`description` + `when_to_use` 合并文本在 Skill 列表中截断为 1,536 字符 |
| `when_to_use` | 否 | Claude 应触发此 Skill 的额外上下文（如触发短语、示例请求）。追加到 `description` 后，计入 1,536 字符上限 |
| `argument-hint` | 否 | 自动补全时显示的参数提示。例如 `[issue-number]` 或 `[filename] [format]` |
| `arguments` | 否 | 用于 [`$name` 替换](#可用字符串替换)的命名位置参数。接受空格分隔字符串或 YAML 列表，名称按顺序映射到参数位置 |
| `disable-model-invocation` | 否 | 设为 `true` 阻止 Claude 自动加载该 Skill。用于仅手动 `/name` 触发的工作流。也阻止 Skill 被[预加载到子 Agent](https://code.claude.com/docs/en/sub-agents#preload-skills-into-subagents)。默认 `false` |
| `user-invocable` | 否 | 设为 `false` 从 `/` 菜单隐藏。用于用户不应直接调用的背景知识。默认 `true` |
| `allowed-tools` | 否 | Skill 激活时 Claude 可免授权使用的工具。接受空格/逗号分隔字符串或 YAML 列表 |
| `disallowed-tools` | 否 | Skill 激活时从 Claude 可用工具池中移除的工具。用于不应调用某些工具的自主 Skill（如后台循环禁用 `AskUserQuestion`）。你发下一条消息时限制解除 |
| `model` | 否 | Skill 激活时使用的模型。覆盖仅在当前 turn 有效，不保存到设置；下一条 Prompt 恢复会话模型。接受与 [`/model`](https://code.claude.com/docs/en/model-config) 相同的值，或 `inherit` 保持当前模型 |
| `effort` | 否 | Skill 激活时的[努力等级](https://code.claude.com/docs/en/model-config#adjust-effort-level)。覆盖会话努力等级。选项：`low`、`medium`、`high`、`xhigh`、`max` |
| `context` | 否 | 设为 `fork` 在分叉的子 Agent 上下文中运行 |
| `agent` | 否 | 当 `context: fork` 时使用哪种子 Agent 类型 |
| `hooks` | 否 | 作用于此 Skill 生命周期的 Hook。配置格式见 [Skills 和 Agents 中的 Hooks](https://code.claude.com/docs/en/hooks#hooks-in-skills-and-agents) |
| `paths` | 否 | 限制 Skill 激活时机的 Glob 模式。仅当操作匹配模式的文件时 Claude 自动加载该 Skill。格式与[路径规则](https://code.claude.com/docs/en/memory#path-specific-rules)相同 |
| `shell` | 否 | 此 Skill 中 `` !`command` `` 和 ` ```! ` 代码块使用的 Shell。接受 `bash`（默认）或 `powershell` |

#### Skill 的命令名来源

**你输入 `/` 后面的命令名取决于 Skill 文件的存放位置。** frontmatter 中的 `name` 字段设置的是列表中的显示名称，除了插件根 `SKILL.md` 的情况外，不会改变你输入的命令。

| Skill 位置 | 命令名来源 | 示例 |
| :--- | :--- | :--- |
| `~/.claude/skills/` 或 `.claude/skills/` 下的 Skill 目录 | 目录名 | `.claude/skills/deploy-staging/SKILL.md` → `/deploy-staging` |
| 嵌套 `.claude/skills/` 目录（与其他 Skill 同名时） | 相对工作目录的子目录路径 + Skill 目录名 | `apps/web/.claude/skills/deploy/SKILL.md` → `/apps/web:deploy` |
| `.claude/commands/` 下的文件 | 文件名去掉扩展名 | `.claude/commands/deploy.md` → `/deploy` |
| 插件 `skills/` 子目录 | 目录名，按插件命名空间 | `my-plugin/skills/review/SKILL.md` → `/my-plugin:review` |
| 插件根 `SKILL.md` | frontmatter `name`，回退到插件目录名 | `my-plugin/SKILL.md` with `name: review` → `/my-plugin:review` |

插件根是唯一一个 `name` 会决定命令名的场景，因为没有 Skill 目录可以从中取名。如果未设 `name`，则使用插件的目录名。

#### 可用字符串替换

**Skills 支持动态值的字符串替换：**

| 变量 | 说明 |
| :--- | :--- |
| `$ARGUMENTS` | 调用 Skill 时传入的所有参数。如果内容中不存在 `$ARGUMENTS`，参数以 `ARGUMENTS: <value>` 追加到末尾 |
| `$ARGUMENTS[N]` | 按 0 起始索引访问特定参数，如 `$ARGUMENTS[0]` 是第一个参数 |
| `$N` | `$ARGUMENTS[N]` 的简写，如 `$0` 是第一个参数 |
| `$name` | 在 [`arguments`](#frontmatter-参考) frontmatter 列表中声明的命名参数。名称按顺序映射到位置 |
| `${CLAUDE_SESSION_ID}` | 当前会话 ID。用于日志记录、创建会话专属文件或关联 Skill 输出与会话 |
| `${CLAUDE_EFFORT}` | 当前努力等级：`low`、`medium`、`high`、`xhigh` 或 `max` |
| `${CLAUDE_SKILL_DIR}` | 包含 Skill `SKILL.md` 文件的目录。用于在 bash 注入命令中引用随 Skill 打包的脚本或文件，不受当前工作目录影响 |

索引参数使用 shell 风格引号——多词值用引号包裹作为单个参数传递。例如 `/my-skill "hello world" second` 使得 `$0` 展开为 `hello world`，`$1` 为 `second`。`$ARGUMENTS` 始终展开为输入的完整参数字符串。

要在数字、`ARGUMENTS` 或声明的参数名前插入字面 `$`（如 `$1.00`），用反斜杠转义：`\$1.00`。

**使用替换的示例：**

```yaml
---
name: session-logger
description: Log activity for this session
---

Log the following to logs/${CLAUDE_SESSION_ID}.log:

$ARGUMENTS
```

### 添加辅助文件

**Skill 目录中可以包含多个文件，使 `SKILL.md` 保持精简，详细参考材料仅在需要时按需加载。**

```text
my-skill/
├── SKILL.md (必需 - 概述和导航)
├── reference.md (详细 API 文档 - 按需加载)
├── examples.md (使用示例 - 按需加载)
└── scripts/
    └── helper.py (工具脚本 - 执行而非加载)
```

在 `SKILL.md` 中引用辅助文件，让 Claude 知道它们的内容和加载时机：

```markdown
## Additional resources

- For complete API details, see [reference.md](reference.md)
- For usage examples, see [examples.md](examples.md)
```

> [!TIP]
> `SKILL.md` 控制在 500 行以内。详细参考材料移到独立文件中。

### 控制谁来触发 Skill

**默认情况下，你和 Claude 都能触发任何 Skill。** 你可以输入 `/skill-name` 直接调用，Claude 也可以在相关场景自动加载。两个 frontmatter 字段可以限制这一点：

* **`disable-model-invocation: true`**：仅你能触发。用于有副作用或需要你控制时机的工作流，如 `/commit`、`/deploy`、`/send-slack-message`——你不希望 Claude 仅仅因为代码看起来"准备好了"就自动部署。

* **`user-invocable: false`**：仅 Claude 能触发。用于不适合作为命令的背景知识。比如 `legacy-system-context` 解释旧系统的工作方式，Claude 在相关时应知道这些，但 `/legacy-system-context` 对用户而言不是有意义的操作。

示例——仅你能触发的部署 Skill：

```yaml
---
name: deploy
description: Deploy the application to production
disable-model-invocation: true
---

Deploy $ARGUMENTS to production:

1. Run the test suite
2. Build the application
3. Push to the deployment target
4. Verify the deployment succeeded
```

**两个字段对调用和上下文加载的影响：**

| Frontmatter | 你能调用 | Claude 能调用 | 何时加载到上下文 |
| :--- | :--- | :--- | :--- |
| （默认） | 是 | 是 | 描述始终在上下文中，完整 Skill 在被调用时加载 |
| `disable-model-invocation: true` | 是 | 否 | 描述不在上下文中，完整 Skill 在你调用时加载 |
| `user-invocable: false` | 否 | 是 | 描述始终在上下文中，完整 Skill 在被调用时加载 |

> [!NOTE]
> 常规会话中，Skill 描述加载到上下文让 Claude 知道可用选项，但完整内容仅在被调用时加载。[预加载 Skills 的子 Agent](https://code.claude.com/docs/en/sub-agents#preload-skills-into-subagents) 则不同：完整 Skill 内容在启动时注入。

### Skill 内容生命周期

**Skill 被调用后，渲染的 `SKILL.md` 内容作为一条消息进入对话并在整个会话中保留。** Claude Code 不会在后续 turn 重新读取 Skill 文件，因此请把应在整个任务中持续生效的指导写成常驻指令，而非一次性步骤。

[自动压缩](https://code.claude.com/docs/en/how-claude-code-works#when-context-fills-up)会在 Token 预算内保留已调用的 Skill。当对话被摘要以释放上下文时，Claude Code 在摘要后重新附加每个 Skill 最近一次调用的内容（保留前 5,000 Token）。重新附加的 Skill 共享 25,000 Token 的合并预算，从最近调用的 Skill 开始填充，因此同一会话中调用了许多 Skill 时，较早的可能在压缩后被完全丢弃。

如果 Skill 在第一次响应后似乎不再影响行为，通常内容仍在，只是模型选择了其他工具或方式。强化 Skill 的 `description` 和指令让模型持续偏好它，或使用 [Hooks](https://code.claude.com/docs/en/hooks) 确定性地强制行为。如果 Skill 很大或之后又调用了多个其他 Skill，压缩后重新调用它以恢复完整内容。

### 为 Skill 预授权工具

**`allowed-tools` 字段在 Skill 激活时授予列出工具的免确认权限。** 它不限制可用工具——所有工具仍可调用，[权限设置](https://code.claude.com/docs/en/permissions)仍管控未列出的工具。

对于提交到项目 `.claude/skills/` 目录中的 Skill，`allowed-tools` 在你接受该文件夹的工作区信任对话框后生效，与 `.claude/settings.json` 中的权限规则相同。信任仓库前请审查项目 Skill，因为 Skill 可以为自身授予广泛的工具访问权限。

示例——让 Claude 在调用时无需逐次确认即可运行 git 命令：

```yaml
---
name: commit
description: Stage and commit the current changes
disable-model-invocation: true
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *)
---
```

要在 Skill 激活时从 Claude 可用工具池移除工具，在 frontmatter 中用 `disallowed-tools` 列出。限制在你发下一条消息时解除。要在所有 Skill 和 Prompt 中阻止工具，在[权限设置](https://code.claude.com/docs/en/permissions)中添加 deny 规则。

### 向 Skill 传递参数

**你和 Claude 都可以在调用 Skill 时传递参数，通过 `$ARGUMENTS` 占位符获取。**

此 Skill 按编号修复 GitHub Issue，`$ARGUMENTS` 被替换为 Skill 名称后面的内容：

```yaml
---
name: fix-issue
description: Fix a GitHub issue
disable-model-invocation: true
---

Fix GitHub issue $ARGUMENTS following our coding standards.

1. Read the issue description
2. Understand the requirements
3. Implement the fix
4. Write tests
5. Create a commit
```

运行 `/fix-issue 123` 时，Claude 收到 "Fix GitHub issue 123 following our coding standards..."

如果 Skill 内容中没有 `$ARGUMENTS`，Claude Code 会在末尾追加 `ARGUMENTS: <your input>`，Claude 仍能看到你输入的内容。

按位置访问单个参数，使用 `$ARGUMENTS[N]` 或简写 `$N`：

```yaml
---
name: migrate-component
description: Migrate a component from one framework to another
---

Migrate the $ARGUMENTS[0] component from $ARGUMENTS[1] to $ARGUMENTS[2].
Preserve all existing behavior and tests.
```

运行 `/migrate-component SearchBar React Vue` 将 `$ARGUMENTS[0]` 替换为 `SearchBar`，`$ARGUMENTS[1]` 替换为 `React`，`$ARGUMENTS[2]` 替换为 `Vue`。用 `$N` 简写形式：

```yaml
---
name: migrate-component
description: Migrate a component from one framework to another
---

Migrate the $0 component from $1 to $2.
Preserve all existing behavior and tests.
```

## 高级模式

### 注入动态上下文

**`` !`<command>` `` 语法在 Skill 内容发送给 Claude 之前执行 Shell 命令，命令输出替换占位符，Claude 收到的是实际数据而非命令本身。**

此 Skill 通过 GitHub CLI 获取实时 PR 数据来总结 Pull Request：

```yaml
---
name: pr-summary
description: Summarize changes in a pull request
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Pull request context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

## Your task
Summarize this pull request...
```

运行此 Skill 时：

1. 每个 `` !`<command>` `` 立即执行（在 Claude 看到内容之前）
2. 输出替换 Skill 内容中的占位符
3. Claude 收到包含实际 PR 数据的完整渲染 Prompt

这是预处理，不是 Claude 执行的内容。Claude 只看到最终结果。

替换对原始文件只运行一次。命令输出作为纯文本插入，不会被再次扫描以展开进一步的 `` !`<command>` `` 占位符。

内联形式仅在 `!` 出现在行首或紧跟空白符之后时才被识别。如果 `!` 跟在其他字符后面（如 `` KEY=!`cmd` ``），占位符保留为字面文本，命令不会运行。

对于多行命令，使用 ` ```! ` 开启的围栏代码块：

````markdown
## Environment
```!
node --version
npm --version
git status --short
```
````

要禁用来自用户、项目、插件或[附加目录](#来自附加目录的-skills)来源的 Skills 和自定义命令的此行为，在[设置](https://code.claude.com/docs/en/settings)中设置 `"disableSkillShellExecution": true`。每个命令将被替换为 `[shell command execution disabled by policy]`。内置和受管 Skill 不受影响。

> [!TIP]
> 要在 Skill 运行时请求更深层推理，在内容中任意位置包含 `ultrathink`。参见[使用 ultrathink 进行一次性深度推理](https://code.claude.com/docs/en/model-config#use-ultrathink-for-one-off-deep-reasoning)。

### 在子 Agent 中运行 Skill

**在 frontmatter 中添加 `context: fork`，Skill 将在隔离环境中运行。** Skill 内容成为驱动子 Agent 的 Prompt，它无法访问你的对话历史。

> [!WARNING]
> `context: fork` 仅对有明确指令的 Skill 有意义。如果 Skill 包含"使用这些 API 规范"之类的指导而没有任务，子 Agent 收到指导但没有可执行的 Prompt，将不会返回有意义的输出。

**Skills 和[子 Agent](https://code.claude.com/docs/en/sub-agents) 的两个方向：**

| 方式 | System Prompt | 任务 | 额外加载 |
| :--- | :--- | :--- | :--- |
| 带 `context: fork` 的 Skill | 来自 Agent 类型 | SKILL.md 内容 | CLAUDE.md（Agent 为 Explore 或 Plan 时除外） |
| 带 `skills` 字段的子 Agent | 子 Agent 的 Markdown 正文 | Claude 的委派消息 | 预加载的 Skills + CLAUDE.md |

使用 `context: fork` 时，你在 Skill 中编写任务并选择 Agent 类型来执行。内置的 Explore 和 Plan Agent [跳过 CLAUDE.md 和 git status](https://code.claude.com/docs/en/sub-agents#what-loads-at-startup) 以保持上下文精简，因此使用 `agent: Explore` 的 forked Skill 只看到 SKILL.md 内容和 Agent 自身的 System Prompt。

#### 示例：使用 Explore Agent 的研究 Skill

此 Skill 在 forked Explore Agent 中运行研究。Skill 内容成为任务，Agent 提供优化用于代码库探索的只读工具：

```yaml
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly:

1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Summarize findings with specific file references
```

运行此 Skill 时：

1. 创建新的隔离上下文
2. 子 Agent 收到 Skill 内容作为其 Prompt（"Research $ARGUMENTS thoroughly..."）
3. `agent` 字段决定执行环境（模型、工具和权限）
4. 结果被摘要后返回主对话

`agent` 字段指定使用哪个子 Agent 配置。选项包括内置 Agent（`Explore`、`Plan`、`general-purpose`）或 `.claude/agents/` 中的任何自定义子 Agent。省略时使用 `general-purpose`。

### 限制 Claude 的 Skill 访问

**默认情况下，Claude 可以调用任何未设 `disable-model-invocation: true` 的 Skill。** 定义了 `allowed-tools` 的 Skill 在激活时授予 Claude 免确认的工具访问。[权限设置](https://code.claude.com/docs/en/permissions)仍管控所有其他工具的基线审批行为。少数内置命令也通过 Skill 工具可用，包括 `/init`、`/review` 和 `/security-review`。

三种方式控制 Claude 可以调用哪些 Skill：

**禁用所有 Skill**——在 `/permissions` 中拒绝 Skill 工具：

```text
# Add to deny rules:
Skill
```

**允许或拒绝特定 Skill**——使用[权限规则](https://code.claude.com/docs/en/permissions)：

```text
# Allow only specific skills
Skill(commit)
Skill(review-pr *)

# Deny specific skills
Skill(deploy *)
```

权限语法：`Skill(name)` 精确匹配，`Skill(name *)` 前缀匹配任意参数。

**隐藏单个 Skill**——在其 frontmatter 中添加 `disable-model-invocation: true`，将 Skill 从 Claude 上下文中完全移除。

> [!NOTE]
> `user-invocable` 字段仅控制菜单可见性，不影响 Skill 工具访问。用 `disable-model-invocation: true` 阻止程序化调用。

### 从设置覆盖 Skill 可见性

**`skillOverrides` 设置从[设置](https://code.claude.com/docs/en/settings)中控制 Skill 可见性，而非修改 Skill 自身的 frontmatter。** 用于不想编辑 SKILL.md 的场景，如提交到共享项目仓库或由 MCP Server 提供的 Skill。`/skills` 菜单可直接操作：高亮 Skill 按 `Space` 切换状态，按 `Enter` 保存到 `.claude/settings.local.json`。

每个键是 Skill 名称，值为四种状态之一：

| 值 | 是否列出给 Claude | 是否在 `/` 菜单 |
| :--- | :--- | :--- |
| `"on"` | 名称和描述 | 是 |
| `"name-only"` | 仅名称 | 是 |
| `"user-invocable-only"` | 隐藏 | 是 |
| `"off"` | 隐藏 | 隐藏 |

未出现在 `skillOverrides` 中的 Skill 视为 `"on"`。示例：

```json
{
  "skillOverrides": {
    "legacy-context": "name-only",
    "deploy": "off"
  }
}
```

插件 Skill 不受 `skillOverrides` 影响，通过 `/plugin` 管理。

## 评估和迭代 Skill

**看到 Skill 被触发说明 Claude 找到了它，不代表它按你的意图工作。** 要确认 Skill 有效，需分别衡量两件事：Claude 是否在应触发的 Prompt 上调用了它，以及触发时输出是否符合预期。

两者的验证方式都是基线对比。收集几个真实的 Prompt，分别在有 Skill 和[禁用 Skill](#从设置覆盖-skill-可见性)的新会话中运行，比较结果。必须在新会话中测试，因为编写 Skill 时残留的上下文会掩盖指令中的缺陷。

### 使用 skill-creator 运行评估

**[`skill-creator` 插件](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator)在 Claude Code 内自动化对比循环。** 从官方市场安装：

```text
/plugin install skill-creator@claude-plugins-official
```

如果 Claude Code 报告找不到插件，你的市场可能缺失或过期。运行 `/plugin marketplace update claude-plugins-official` 刷新，或 `/plugin marketplace add anthropics/claude-plugins-official` 首次添加。然后重试安装。

安装后运行 `/reload-plugins` 使插件 Skill 在当前会话可用。然后让 Claude 评估现有 Skill，例如 `evaluate my summarize-changes skill with skill-creator`。插件引导你编写测试用例并运行循环：

* **测试用例**：将 Prompt、输入文件和预期行为存储在 Skill 目录的 `evals/evals.json` 中
* **隔离运行**：每个测试用例生成一个[子 Agent](https://code.claude.com/docs/en/sub-agents)，从干净上下文启动，记录 Token 数和耗时
* **评分**：对照每个断言检查输出，将通过/失败及证据写入 `grading.json`
* **基准测试**：聚合有/无 Skill 的通过率、时间和 Token 到 `benchmark.json`，对比通过率提升与 Token/时间开销
* **版本对比**：在 Skill 的两个版本间运行盲 A/B 测试，确认编辑是改进后再提交
* **描述调优**：生成应触发和不应触发的 Prompt，衡量命中率，在 Skill 被错误请求激活时提议描述修改
* **审查查看器**：打开 HTML 报告，检查每个输出并记录定性反馈供下次迭代读取

评估文件格式和完整迭代工作流参见 agentskills.io 上的 [Evaluating skill output quality](https://agentskills.io/skill-creation/evaluating-skills)。基准测试和对比模式的背景参见 [skill-creator 公告](https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills)。

## 分享 Skills

**Skills 可以按不同范围分发：**

* **项目 Skills**：将 `.claude/skills/` 提交到版本控制
* **插件**：在你的[插件](https://code.claude.com/docs/en/plugins)中创建 `skills/` 目录
* **受管**：通过[受管设置](https://code.claude.com/docs/en/settings#settings-files)在组织范围部署

### 生成可视化输出

**Skills 可以打包和运行任何语言的脚本，赋予 Claude 超越单一 Prompt 的能力。** 一种强大的模式是生成可视化输出：交互式 HTML 文件在浏览器中打开，用于探索数据、调试或创建报告。

以下示例创建一个代码库浏览器——交互式树形视图，可展开/折叠目录、一目了然地查看文件大小、按颜色识别文件类型。

创建 Skill 目录：

```bash
mkdir -p ~/.claude/skills/codebase-visualizer/scripts
```

保存到 `~/.claude/skills/codebase-visualizer/SKILL.md`。描述告诉 Claude 何时激活此 Skill，指令告诉 Claude 运行打包的脚本。脚本路径使用 [`${CLAUDE_SKILL_DIR}`](#可用字符串替换)，无论 Skill 安装在个人、项目还是插件级别都能正确解析：

````yaml
---
name: codebase-visualizer
description: Generate an interactive collapsible tree visualization of your codebase. Use when exploring a new repo, understanding project structure, or identifying large files.
allowed-tools: Bash(python3 *)
---

# Codebase Visualizer

Generate an interactive HTML tree view that shows your project's file structure with collapsible directories.

## Usage

Run the visualization script from your project root:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/visualize.py .
```

This creates `codebase-map.html` in the current directory and opens it in your default browser.

## What the visualization shows

- **Collapsible directories**: Click folders to expand/collapse
- **File sizes**: Displayed next to each file
- **Colors**: Different colors for different file types
- **Directory totals**: Shows aggregate size of each folder
````

保存到 `~/.claude/skills/codebase-visualizer/scripts/visualize.py`。此脚本扫描目录树并生成自包含的 HTML 文件，包含：

* **摘要侧边栏**：显示文件数、目录数、总大小和文件类型数
* **柱状图**：按文件类型分解代码库（按大小排前 8）
* **可折叠树**：可展开/折叠目录，带颜色编码的文件类型指示器

脚本需要 Python 3，仅使用内置库，无需安装包：

```python
#!/usr/bin/env python3
"""Generate an interactive collapsible tree visualization of a codebase."""

import json
import sys
import webbrowser
from html import escape
from pathlib import Path
from collections import Counter

IGNORE = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build'}

def scan(path: Path, stats: dict) -> dict:
    result = {"name": path.name, "children": [], "size": 0}
    try:
        for item in sorted(path.iterdir()):
            if item.name in IGNORE or item.name.startswith('.'):
                continue
            if item.is_file():
                size = item.stat().st_size
                ext = item.suffix.lower() or '(no ext)'
                result["children"].append({"name": item.name, "size": size, "ext": ext})
                result["size"] += size
                stats["files"] += 1
                stats["extensions"][ext] += 1
                stats["ext_sizes"][ext] += size
            elif item.is_dir():
                stats["dirs"] += 1
                child = scan(item, stats)
                if child["children"]:
                    result["children"].append(child)
                    result["size"] += child["size"]
    except PermissionError:
        pass
    return result

def generate_html(data: dict, stats: dict, output: Path) -> None:
    # ... (HTML generation logic)
    pass

if __name__ == '__main__':
    target = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
    stats = {"files": 0, "dirs": 0, "extensions": Counter(), "ext_sizes": Counter()}
    data = scan(target, stats)
    out = Path('codebase-map.html')
    generate_html(data, stats, out)
    print(f'Generated {out.absolute()}')
    webbrowser.open(f'file://{out.absolute()}')
```

测试时，在任意项目中打开 Claude Code 问 "Visualize this codebase."。Claude 运行脚本，生成 `codebase-map.html` 并在浏览器中打开。

这种模式适用于任何可视化输出：依赖图、测试覆盖率报告、API 文档或数据库 Schema 可视化。打包的脚本完成实际工作，Claude 负责编排。

## 故障排除

### Skill 未触发

如果 Claude 在预期场景下未使用你的 Skill：

1. 检查 description 是否包含用户自然会说的关键词
2. 验证 Skill 出现在 `What skills are available?` 的回复中
3. 尝试改述请求以更接近 description
4. 如果 Skill 是 user-invocable 的，直接用 `/skill-name` 调用

如果 frontmatter YAML 格式错误，Claude Code 会以空元数据加载 Skill 正文——`/skill-name` 仍可用，但 Claude 没有 `description` 可以匹配。使用 `--debug` 查看解析错误。

### Skill 触发过于频繁

如果 Claude 在不需要时使用了你的 Skill：

1. 让 description 更具体
2. 如果只想手动触发，添加 `disable-model-invocation: true`

### Skill 描述被截断

**Skill 描述被加载到上下文让 Claude 知道可用选项。** 所有 Skill 名称始终包含，但如果你有大量 Skill，描述会被缩短以适应字符预算，这可能去掉 Claude 匹配请求所需的关键词。预算按模型上下文窗口的 1% 缩放。溢出时，你最少调用的 Skill 的描述优先被丢弃，常用 Skill 保留完整文本。运行 `/doctor` 查看多少 Skill 描述被缩短或丢弃以及受影响的 Skill。

提高预算：设置 [`skillListingBudgetFraction`](https://code.claude.com/docs/en/settings#available-settings)（如 `0.02` = 2%）或设环境变量 `SLASH_COMMAND_TOOL_CHAR_BUDGET` 为固定字符数。为其他 Skill 释放预算：在 [`skillOverrides`](#从设置覆盖-skill-可见性) 中将低优先级条目设为 `"name-only"` 使其仅列名不含描述。也可以从源头精简 `description` 和 `when_to_use` 文本：关键用例放最前面，每个条目合并文本上限 1,536 字符。上限可通过 [`maxSkillDescriptionChars`](https://code.claude.com/docs/en/settings#available-settings) 配置。

## 相关资源

* [调试你的配置](https://code.claude.com/docs/en/debug-your-config) - 诊断 Skill 为何未出现或未触发
* [评估 Skill 输出质量](https://agentskills.io/skill-creation/evaluating-skills) - agentskills.io 上的评估文件格式和迭代工作流
* [Skill 编写最佳实践](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) - 适用于所有 Claude 产品的编写指导
* [子 Agent](https://code.claude.com/docs/en/sub-agents) - 将任务委派给专门的 Agent
* [插件](https://code.claude.com/docs/en/plugins) - 打包和分发 Skills 及其他扩展
* [Hooks](https://code.claude.com/docs/en/hooks) - 围绕工具事件自动化工作流
* [Memory](https://code.claude.com/docs/en/memory) - 管理 CLAUDE.md 文件作为持久上下文
* [命令](https://code.claude.com/docs/en/commands) - 内置命令和内置 Skill 参考
* [权限](https://code.claude.com/docs/en/permissions) - 控制工具和 Skill 访问
* [Claude Tag Skills](https://claude.com/docs/claude-tag/admins/skills-repo) - 提交到仓库的项目 Skill 也会在该仓库用于 Claude Tag 频道时加载
