---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】Claude Code 记忆系统
description: Claude Code 通过 CLAUDE.md 文件和自动记忆两套机制实现跨会话的持久化上下文。本文详解如何编写、组织 CLAUDE.md 文件，配置自动记忆，以及排查指令未生效的问题。
category: translation
tags: [claude-code, memory, claude-md, translation]
refs:
  - https://code.claude.com/docs/en/memory.md
---

# Claude Code 记忆系统

> 用 CLAUDE.md 给 Claude 写持久化指令，用自动记忆让 Claude 自己积累经验。

**Claude Code 每次启动都是空白上下文，跨会话的知识靠两套机制传递。** 一是你亲手写的 CLAUDE.md 文件，二是 Claude 在使用过程中自己记录的自动记忆（Auto Memory）。

本文涵盖：

- [编写和组织 CLAUDE.md 文件](#claudemd-文件)
- [用 `.claude/rules/` 按路径限定规则作用范围](#用-clauderules-组织规则)
- [配置自动记忆](#自动记忆)
- [排查指令不生效的问题](#排查记忆问题)

## CLAUDE.md 与自动记忆的区别

**两套记忆系统互补，都在每次会话开始时加载到上下文中。** Claude 把它们当参考上下文，而非强制执行的配置。如果想无论 Claude 怎么判断都阻止某个操作，应使用 [PreToolUse Hook](https://code.claude.com/docs/en/hooks-guide)。指令越具体、越简洁，Claude 遵从得越一致。

| | CLAUDE.md 文件 | 自动记忆 |
|:--|:--|:--|
| **谁来写** | 你 | Claude |
| **写什么** | 指令和规则 | 经验和模式 |
| **作用域** | 项目 / 用户 / 组织 | 按仓库，跨 worktree 共享 |
| **加载方式** | 每次会话 | 每次会话（前 200 行或 25KB） |
| **适用场景** | 编码规范、工作流、项目架构 | 构建命令、调试经验、Claude 发现的偏好 |

CLAUDE.md 用于主动引导 Claude 行为；自动记忆让 Claude 从你的纠正中学习，无需手动维护。

子代理也可以维护自己的自动记忆，详见 [子代理配置](https://code.claude.com/docs/en/sub-agents#enable-persistent-memory)。

## CLAUDE.md 文件

**CLAUDE.md 是纯文本 Markdown 文件，用来给 Claude 下达项目级、个人级或组织级的持久化指令。** 你写好文件，Claude 在每次会话开头读取。

### 何时添加内容

把 CLAUDE.md 当作"不想反复解释的事情"的存放处。以下场景适合写入：

- Claude 第二次犯同样的错误
- Code Review 发现 Claude 本应了解的仓库约定
- 你连续两次在聊天里输入相同的纠正或说明
- 新同事也需要同样的上下文才能上手

内容限于每次会话都需要的事实：构建命令、约定、项目布局、"永远做 X"类规则。如果是多步骤流程或只跟代码库某个部分相关，应改用 [Skill](https://code.claude.com/docs/en/skills) 或[按路径限定的规则](#按路径限定规则)。各扩展机制的选用时机参见[功能概览](https://code.claude.com/docs/en/features-overview#build-your-setup-over-time)。

### 文件放在哪

**CLAUDE.md 可以放在多个位置，作用域各不相同。** 下表按加载顺序排列，从最宽到最窄——项目级指令在用户级之后进入上下文。

| 作用域 | 路径 | 用途 | 示例 | 共享范围 |
|:--|:--|:--|:--|:--|
| **受管策略** | macOS: `/Library/Application Support/ClaudeCode/CLAUDE.md`<br/>Linux/WSL: `/etc/claude-code/CLAUDE.md`<br/>Windows: `C:\Program Files\ClaudeCode\CLAUDE.md` | IT/DevOps 管理的组织级指令 | 公司编码标准、安全策略、合规要求 | 组织内所有用户 |
| **用户级** | `~/.claude/CLAUDE.md` | 所有项目通用的个人偏好 | 代码风格偏好、个人工具快捷方式 | 仅自己（全部项目） |
| **项目级** | `./CLAUDE.md` 或 `./.claude/CLAUDE.md` | 团队共享的项目指令 | 项目架构、编码规范、常见工作流 | 团队成员（通过版本控制） |
| **本地级** | `./CLAUDE.local.md` | 个人的项目特定偏好；加入 `.gitignore` | 你的沙箱 URL、偏好测试数据 | 仅自己（当前项目） |

工作目录上方的 CLAUDE.md 和 CLAUDE.local.md 在启动时完整加载；子目录中的文件在 Claude 读取该子目录文件时按需加载，详见[加载机制](#加载机制)。

大型项目可使用[项目规则](#用-clauderules-组织规则)把指令拆分到多个按主题划分的文件中。

### 初始化项目 CLAUDE.md

**项目 CLAUDE.md 存放在 `./CLAUDE.md` 或 `./.claude/CLAUDE.md`。** 写入适用于所有项目参与者的内容：构建和测试命令、编码规范、架构决策、命名约定、常见工作流。这些通过版本控制共享，应关注项目级标准而非个人偏好。

> **提示**：运行 `/init` 可自动生成初始 CLAUDE.md。Claude 会分析代码库并创建包含构建命令、测试指令和发现的项目约定的文件。如果 CLAUDE.md 已存在，`/init` 会建议改进而非覆盖。之后再补充 Claude 无法自动发现的指令即可。
>
> 设置 `CLAUDE_CODE_NEW_INIT=1` 可启用交互式多阶段流程。`/init` 会询问要设置哪些产物（CLAUDE.md、skills、hooks），然后用子代理探索代码库，通过追问补充信息，最后展示可审阅的方案再写入文件。

### 编写有效指令

**CLAUDE.md 在每次会话开始时加载到上下文窗口，和对话内容一起消耗 token。** [上下文窗口可视化](https://code.claude.com/docs/en/context-window)展示了 CLAUDE.md 相对于其他启动上下文的加载位置。因为它是上下文而非强制配置，写法直接影响 Claude 遵循的可靠程度。具体、简洁、结构化的指令效果最好。

**篇幅**：每个 CLAUDE.md 控制在 200 行以内。过长会消耗更多上下文并降低遵循度。如果指令越来越多，用[按路径限定规则](#按路径限定规则)让指令只在 Claude 处理匹配文件时加载。也可以用 [import](#导入其他文件) 拆分组织，但导入文件仍在启动时加载进上下文。

**结构**：用 Markdown 标题和列表分组相关指令。Claude 像读者一样扫描结构，组织清晰的段落比密集文本更容易遵循。

**具体性**：写能验证的具体指令，例如：

- "使用 2 空格缩进" 而不是 "正确格式化代码"
- "提交前运行 `npm test`" 而不是 "测试你的改动"
- "API handler 放在 `src/api/handlers/`" 而不是 "保持文件有序"

**一致性**：两条规则互相矛盾时，Claude 可能随机选一条。定期审查 CLAUDE.md、子目录中的嵌套 CLAUDE.md 和 `.claude/rules/`，移除过时或冲突的指令。在 monorepo 中，用 [`claudeMdExcludes`](#排除特定-claudemd-文件) 跳过其他团队的无关文件。

### 导入其他文件

**CLAUDE.md 可以用 `@path/to/import` 语法导入其他文件。** 导入的文件在启动时展开并与引用它的 CLAUDE.md 一起加载到上下文中。

支持相对路径和绝对路径。相对路径相对于包含 import 的文件解析，而非工作目录。导入文件可递归导入其他文件，最大深度四层。

解析时会跳过 Markdown 行内代码和围栏代码块。在 CLAUDE.md 中提到路径但不想导入时，用反引号包裹：`` `@README` `` 保持字面文本，而 `@README` 裸写则触发导入。

示例——引入 README、package.json 和工作流指南：

```text
See @README for project overview and @package.json for available npm commands for this project.

# Additional Instructions
- git workflow @docs/git-instructions.md
```

对于不应提交到版本控制的个人项目偏好，在项目根目录创建 `CLAUDE.local.md`，它与 `CLAUDE.md` 一同加载且处理方式相同。将 `CLAUDE.local.md` 加入 `.gitignore`；运行 `/init` 选择 personal 选项会自动完成。

如果在同一仓库的多个 git worktree 中工作，被 gitignore 的 `CLAUDE.local.md` 只存在于创建它的 worktree。要跨 worktree 共享个人指令，改为从主目录导入文件：

```text
# Individual Preferences
- @~/.claude/my-project-instructions.md
```

> **注意**：Claude Code 首次在项目中遇到外部导入时，会显示审批对话框列出相关文件。如果你拒绝，导入保持禁用且对话框不再出现。

更结构化的指令组织方式参见 [`.claude/rules/`](#用-clauderules-组织规则)。

### AGENTS.md

**Claude Code 读取 CLAUDE.md 而非 AGENTS.md。** 如果仓库已有 `AGENTS.md` 供其他编码代理使用，创建 CLAUDE.md 并导入它即可让两个工具读取相同指令而不重复维护。还可以在导入下方添加 Claude 专属指令：

```markdown
@AGENTS.md

## Claude Code

Use plan mode for changes under `src/billing/`.
```

如果不需要 Claude 专属内容，也可以用符号链接：

```bash
ln -s AGENTS.md CLAUDE.md
```

Windows 上创建符号链接需要管理员权限或开发者模式，建议用 `@AGENTS.md` 导入方式。

在已有 `AGENTS.md` 的仓库运行 [`/init`](https://code.claude.com/docs/en/commands) 时，它会读取并把相关部分整合进生成的 CLAUDE.md，同时也会读取 `.cursorrules`、`.devin/rules/`、`.windsurfrules` 等其他工具配置。

### 加载机制

**Claude Code 从当前工作目录向上遍历目录树，逐级查找 `CLAUDE.md` 和 `CLAUDE.local.md`。** 如果在 `foo/bar/` 启动，则加载 `foo/bar/CLAUDE.md`、`foo/CLAUDE.md` 以及同级的 `CLAUDE.local.md`。

所有找到的文件拼接进上下文而非互相覆盖。跨目录的排序从文件系统根目录到工作目录——对上例而言，`foo/CLAUDE.md` 在 `foo/bar/CLAUDE.md` 之前出现，距启动位置更近的指令最后被读取。同一目录内，`CLAUDE.local.md` 附加在 `CLAUDE.md` 之后，所以你的个人笔记在该层级最后被读取。

Claude 也会发现工作目录子目录中的 CLAUDE.md 和 CLAUDE.local.md，但不在启动时加载，而是在 Claude 读取这些子目录中的文件时按需加入。

在大型 monorepo 中如果其他团队的 CLAUDE.md 被误加载，用 [`claudeMdExcludes`](#排除特定-claudemd-文件) 跳过。根目录和子目录 CLAUDE.md 及 rules 的完整布局参见 [Monorepo 和大型仓库](https://code.claude.com/docs/en/large-codebases)。

CLAUDE.md 文件中的块级 HTML 注释（`<!-- maintainer notes -->`）在注入上下文前会被剥离，可用来给人类维护者留笔记而不消耗 token。代码块内的注释保留。用 Read 工具直接打开 CLAUDE.md 时注释可见。

#### 从额外目录加载

`--add-dir` 标志让 Claude 访问主工作目录之外的目录，但默认不加载其中的 CLAUDE.md。

要同时加载额外目录的记忆文件，设置环境变量：

```bash
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1 claude --add-dir ../shared-config
```

这会从额外目录加载 `CLAUDE.md`、`.claude/CLAUDE.md`、`.claude/rules/*.md` 和 `CLAUDE.local.md`。如果在 [`--setting-sources`](https://code.claude.com/docs/en/cli-reference) 中排除了 `local`，则跳过 `CLAUDE.local.md`。

### 用 `.claude/rules/` 组织规则

**对大型项目，可以用 `.claude/rules/` 目录把指令拆分到多个文件中。** 这让指令模块化、团队更容易维护。规则还可[按路径限定](#按路径限定规则)，仅在 Claude 处理匹配文件时加载，减少噪声并节省上下文空间。

> **注意**：规则在每次会话或打开匹配文件时加载。对于不需要常驻上下文的任务型指令，用 [Skills](https://code.claude.com/docs/en/skills) 替代——它只在你调用或 Claude 判断与当前 prompt 相关时加载。

#### 设置规则

在项目的 `.claude/rules/` 目录放置 Markdown 文件。每个文件覆盖一个主题，用描述性文件名如 `testing.md` 或 `api-design.md`。所有 `.md` 文件被递归发现，所以可以按子目录组织如 `frontend/` 或 `backend/`：

```text
your-project/
├── .claude/
│   ├── CLAUDE.md           # 项目主指令
│   └── rules/
│       ├── code-style.md   # 代码风格
│       ├── testing.md      # 测试约定
│       └── security.md     # 安全要求
```

没有 [`paths` frontmatter](#按路径限定规则) 的规则在启动时加载，优先级与 `.claude/CLAUDE.md` 相同。

#### 按路径限定规则

**规则可以通过 YAML frontmatter 中的 `paths` 字段限定到特定文件。** 这些条件规则仅在 Claude 处理匹配文件时生效。

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API Development Rules

- All API endpoints must include input validation
- Use the standard error response format
- Include OpenAPI documentation comments
```

没有 `paths` 字段的规则无条件加载，适用于所有文件。按路径限定的规则在 Claude 读取匹配文件时触发，而非每次工具调用时。

`paths` 字段使用 glob 模式匹配文件：

| 模式 | 匹配范围 |
|:--|:--|
| `**/*.ts` | 任意目录下的所有 TypeScript 文件 |
| `src/**/*` | `src/` 目录下的所有文件 |
| `*.md` | 项目根目录的 Markdown 文件 |
| `src/components/*.tsx` | 指定目录下的 React 组件 |

支持多个模式和花括号展开：

```markdown
---
paths:
  - "src/**/*.{ts,tsx}"
  - "lib/**/*.ts"
  - "tests/**/*.test.ts"
---
```

#### 用符号链接跨项目共享规则

`.claude/rules/` 目录支持符号链接，可以维护一套共享规则并链接到多个项目。符号链接正常解析和加载，循环链接会被检测并优雅处理。

示例——链接共享目录和单个文件：

```bash
ln -s ~/shared-claude-rules .claude/rules/shared
ln -s ~/company-standards/security.md .claude/rules/security.md
```

#### 用户级规则

`~/.claude/rules/` 中的个人规则适用于机器上所有项目，用于非项目特定的偏好：

```text
~/.claude/rules/
├── preferences.md    # 个人编码偏好
└── workflows.md      # 偏好工作流
```

用户级规则在项目规则之前加载，项目规则优先级更高。

### 大型团队的 CLAUDE.md 管理

**面向跨团队部署 Claude Code 的组织，可以集中管理指令并控制 CLAUDE.md 的加载行为。**

#### 部署组织级 CLAUDE.md

组织可以部署一个集中管理的 CLAUDE.md 应用到机器上的所有用户。此文件不能被个人设置排除。

步骤：

1. **在受管策略路径创建文件**
   - macOS: `/Library/Application Support/ClaudeCode/CLAUDE.md`
   - Linux/WSL: `/etc/claude-code/CLAUDE.md`
   - Windows: `C:\Program Files\ClaudeCode\CLAUDE.md`

2. **用配置管理系统分发**：使用 MDM、Group Policy、Ansible 等工具部署到开发者机器。其他组织级配置选项参见[受管设置](https://code.claude.com/docs/en/permissions#managed-settings)。

`managed-settings.json` 中的 `claudeMd` 键可以直接内嵌 CLAUDE.md 内容，无需部署单独文件：

```json
{
  "claudeMd": "Always run `make lint` before committing.\nNever push directly to main."
}
```

**作用域**：机器上每个仓库的每次会话。仓库特定指令应提交项目 CLAUDE.md。

**优先级**：与受管 CLAUDE.md 文件相同，在用户和项目 CLAUDE.md 之前加载。

**生效位置**：仅受管和策略设置。在 user、project 或 local settings 中设置 `claudeMd` 无效。

受管 CLAUDE.md 和[受管设置](https://code.claude.com/docs/en/settings#settings-files)用途不同——settings 用于技术强制，CLAUDE.md 用于行为引导：

| 关注点 | 配置位置 |
|:--|:--|
| 阻止特定工具、命令或文件路径 | 受管设置：`permissions.deny` |
| 强制沙箱隔离 | 受管设置：`sandbox.enabled` |
| 环境变量和 API 路由 | 受管设置：`env` |
| 认证方式和组织锁定 | 受管设置：`forceLoginMethod`、`forceLoginOrgUUID` |
| 代码风格和质量指南 | 受管 CLAUDE.md |
| 数据处理和合规提醒 | 受管 CLAUDE.md |
| 对 Claude 的行为指令 | 受管 CLAUDE.md |

Settings 规则由客户端强制执行，不管 Claude 怎么决定。CLAUDE.md 指令塑造 Claude 行为，但不是硬性执行层。

#### 排除特定 CLAUDE.md 文件

**在大型 monorepo 中，祖先目录的 CLAUDE.md 可能包含与你无关的指令。** `claudeMdExcludes` 设置可按路径或 glob 模式跳过指定文件。

示例——排除顶层 CLAUDE.md 和父文件夹的规则目录，添加到 `.claude/settings.local.json` 保持本地生效：

```json
{
  "claudeMdExcludes": [
    "**/monorepo/CLAUDE.md",
    "/home/user/monorepo/other-team/.claude/rules/**"
  ]
}
```

模式使用 glob 语法匹配绝对路径。`claudeMdExcludes` 可在任意[设置层级](https://code.claude.com/docs/en/settings#settings-files)配置：user、project、local 或 managed policy，数组跨层级合并。

受管策略 CLAUDE.md 不能被排除，确保组织级指令始终生效。

## 自动记忆

**自动记忆让 Claude 在无需你手动编写的情况下跨会话积累知识。** Claude 边工作边给自己做笔记：构建命令、调试经验、架构笔记、代码风格偏好、工作流习惯。并非每次会话都会保存——Claude 根据信息在未来对话中是否有用来判断是否值得记录。

> **注意**：自动记忆需要 Claude Code v2.1.59 或更高版本。用 `claude --version` 检查。

### 启用或禁用

自动记忆默认开启。切换方式：在会话中打开 `/memory` 使用开关，或在项目设置中配置：

```json
{
  "autoMemoryEnabled": false
}
```

也可通过环境变量禁用：`CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`。

### 存储位置

**每个项目有自己的记忆目录 `~/.claude/projects/<project>/memory/`。** `<project>` 路径来源于 git 仓库，同一仓库的所有 worktree 和子目录共享一个自动记忆目录。不在 git 仓库中时使用项目根目录。

要自定义存储位置，在 `settings.json` 中设置 `autoMemoryDirectory`，支持任意[设置作用域](https://code.claude.com/docs/en/settings#settings-precedence)：user、project、local、policy 或 `--settings`。

```json
{
  "autoMemoryDirectory": "~/my-custom-memory-dir"
}
```

值必须是绝对路径或以 `~/` 开头。在项目的 `.claude/settings.json` 或 `.claude/settings.local.json` 中设置时，只有接受该文件夹的工作区信任对话框后才生效（与 hooks 同一机制）。

目录包含一个 `MEMORY.md` 入口文件和可选的主题文件：

```text
~/.claude/projects/<project>/memory/
├── MEMORY.md          # 简明索引，每次会话加载
├── debugging.md       # 调试模式详细笔记
├── api-conventions.md # API 设计决策
└── ...                # Claude 创建的其他主题文件
```

`MEMORY.md` 充当记忆目录的索引。Claude 在会话中读写此目录文件，通过 `MEMORY.md` 追踪存了什么、在哪。

自动记忆是机器本地的。同一 git 仓库的所有 worktree 和子目录共享一个目录，但不跨机器或云环境共享。

### 工作原理

**每次会话开始时加载 `MEMORY.md` 的前 200 行或前 25KB（取较先到者）。** 超出阈值的内容不在会话开始时加载。Claude 通过将详细笔记移到独立主题文件来保持 `MEMORY.md` 简洁。

此限制仅适用于 `MEMORY.md`。CLAUDE.md 文件无论长度如何都完整加载，虽然更短的文件遵循度更好。

`debugging.md` 或 `patterns.md` 等主题文件不在启动时加载，Claude 在需要时用标准文件工具按需读取。

Claude 在会话中读写记忆文件。当你在 Claude Code 界面看到 "Writing memory" 或 "Recalled memory" 时，Claude 正在更新或读取 `~/.claude/projects/<project>/memory/` 中的内容。

### 审计和编辑记忆

自动记忆文件是纯 Markdown，可随时编辑或删除。运行 [`/memory`](#用-memory-查看和编辑) 可在会话内浏览并打开记忆文件。

## 用 `/memory` 查看和编辑

**`/memory` 命令列出当前会话加载的所有 CLAUDE.md、CLAUDE.local.md 和 rules 文件**，可切换自动记忆开关，并提供打开自动记忆文件夹的链接。选择任意文件可在编辑器中打开。

当你要求 Claude 记住某事（如 "always use pnpm, not npm" 或 "remember that the API tests require a local Redis instance"），Claude 会保存到自动记忆。如果想写入 CLAUDE.md，需明确说明如 "add this to CLAUDE.md"，或通过 `/memory` 自己编辑。

## 排查记忆问题

以下是 CLAUDE.md 和自动记忆最常见的问题及调试步骤。

### Claude 不遵循我的 CLAUDE.md

**CLAUDE.md 内容以用户消息形式注入系统提示之后，而非系统提示本身的一部分。** Claude 读取并尝试遵循，但不保证严格合规，尤其是模糊或冲突的指令。

调试方法：

- 运行 `/memory` 确认 CLAUDE.md 和 CLAUDE.local.md 已加载。如果文件未列出，Claude 看不到它。
- 检查相关 CLAUDE.md 是否在会话能加载的位置（参见[文件放在哪](#文件放在哪)）。
- 让指令更具体。"使用 2 空格缩进"比"好好格式化代码"有效得多。
- 检查多个 CLAUDE.md 文件间是否有冲突指令。同一行为有不同指导时，Claude 可能随机选择。

如果指令必须在特定时间点执行（如每次提交前或每次文件编辑后），应写成 [Hook](https://code.claude.com/docs/en/hooks-guide)。Hook 以 shell 命令形式在固定生命周期事件执行，不受 Claude 决策影响。

对于想放到系统提示级别的指令，用 [`--append-system-prompt`](https://code.claude.com/docs/en/cli-reference#system-prompt-flags)。它需要每次调用都传入，更适合脚本和自动化而非交互使用。

> **提示**：使用 [`InstructionsLoaded` Hook](https://code.claude.com/docs/en/hooks#instructionsloaded) 可记录哪些指令文件被加载、何时加载、为何加载。这对调试按路径限定规则或子目录延迟加载文件特别有用。

### 不知道自动记忆保存了什么

运行 `/memory` 选择自动记忆文件夹浏览 Claude 的保存内容。全部是纯 Markdown，可读可编辑可删除。

### CLAUDE.md 太大了

超过 200 行的文件消耗更多上下文且可能降低遵循度。用[按路径限定规则](#按路径限定规则)让指令只在处理匹配文件时加载，或精简非每次会话都需要的内容。拆分为 [`@path` 导入](#导入其他文件)有助于组织但不减少上下文，因为导入文件启动时即加载。

### `/compact` 后指令似乎丢失

**项目根目录的 CLAUDE.md 在 compact 后存活：** Claude 从磁盘重新读取并重新注入会话。子目录中的嵌套 CLAUDE.md 不会自动重新注入，要等 Claude 下次读取该子目录文件时才重新加载。

如果某条指令在 compact 后消失，它要么只在对话中给出过，要么在尚未重新加载的嵌套 CLAUDE.md 中。将仅对话中的指令添加到 CLAUDE.md 使其持久化。完整说明参见 [compact 后哪些内容保留](https://code.claude.com/docs/en/context-window#what-survives-compaction)。

编写有效指令的指导参见[编写有效指令](#编写有效指令)。

## 相关资源

- [调试配置](https://code.claude.com/docs/en/debug-your-config)：诊断 CLAUDE.md 或设置不生效的原因
- [Skills](https://code.claude.com/docs/en/skills)：打包按需加载的可复用工作流
- [Settings](https://code.claude.com/docs/en/settings)：用设置文件配置 Claude Code 行为
- [子代理记忆](https://code.claude.com/docs/en/sub-agents#enable-persistent-memory)：让子代理维护自己的自动记忆
