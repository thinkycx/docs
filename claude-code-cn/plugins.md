---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】插件
description: Claude Code 插件系统完整开发指南。涵盖从零创建插件、添加 Skill/Agent/Hook/MCP/LSP、本地测试调试、发布到社区市场的全流程，以及将现有 .claude/ 配置迁移为可复用插件的方法。
category: translation
tags: [claude-code, plugins, translation]
refs:
  - https://code.claude.com/docs/en/plugins.md
---

# 创建插件

> 创建自定义插件来扩展 Claude Code，可包含 Skill、Agent、Hook 和 MCP 服务器。

**插件让你把自定义功能打包成可分享、可复用的扩展单元。** 本文档覆盖从零创建插件、开发 Skill/Agent/Hook/MCP/LSP、本地测试到分发的完整流程。

想安装现有插件？参见 [发现并安装插件](https://code.claude.com/docs/en/discover-plugins)。完整技术规格参见 [插件参考](https://code.claude.com/docs/en/plugins-reference)。

## 插件 vs 独立配置：何时选用哪种

**Claude Code 提供两种方式来添加自定义 Skill、Agent 和 Hook。**

| 方式 | Skill 命名 | 最适合场景 |
| :--- | :--- | :--- |
| **独立配置**（`.claude/` 目录） | `/hello` | 个人工作流、项目专属定制、快速实验 |
| **插件**（自包含目录，含 Skill/Agent/Hook 或 `.claude-plugin/plugin.json` 清单） | `/plugin-name:hello` | 团队共享、社区分发、版本化发布、跨项目复用 |

**适合用独立配置的场景：**

* 只在单个项目中使用
* 属于个人定制，不需要共享
* 正在做 Skill 或 Hook 的早期实验
* 想用简短的命名，如 `/hello` 或 `/deploy`

**适合用插件的场景：**

* 想把功能分享给团队或社区
* 需要在多个项目间复用同一套 Skill/Agent
* 需要版本控制和便捷的更新机制
* 通过市场进行分发
* 可以接受命名空间前缀（如 `/my-plugin:hello`），这种机制避免了多个插件之间的命名冲突

> [!TIP]
> 建议先在 `.claude/` 中快速迭代，准备好共享时再[转换为插件](#将现有配置转换为插件)。

## 快速上手

**通过创建一个含自定义 Skill 的插件来学习基本流程。** 你将创建清单文件（定义插件元数据的配置文件）、添加一个 Skill，然后用 `--plugin-dir` 标志本地测试。

### 前置条件

* 已[安装并认证 Claude Code](https://code.claude.com/docs/en/quickstart#step-1-install-claude-code)

> [!NOTE]
> 如果看不到 `/plugin` 命令，请将 Claude Code 更新到最新版本。升级方法见 [故障排除](https://code.claude.com/docs/en/troubleshooting)。

### 创建你的第一个插件

#### 第一步：创建插件目录

**每个插件都有自己独立的目录。** 目录内包含你的 Skill、Agent 或 Hook，以及可选的 `.claude-plugin/plugin.json` 清单文件。

```bash
mkdir my-first-plugin
```

#### 第二步：创建插件清单

**清单文件定义了插件的身份信息：名称、描述和版本。** Claude Code 用这些元数据在插件管理器中展示你的插件。

在插件目录中创建 `.claude-plugin` 子目录：

```bash
mkdir my-first-plugin/.claude-plugin
```

然后创建 `my-first-plugin/.claude-plugin/plugin.json`：

```json
{
  "name": "my-first-plugin",
  "description": "A greeting plugin to learn the basics",
  "version": "1.0.0",
  "author": {
    "name": "Your Name"
  }
}
```

| 字段 | 说明 |
| :--- | :--- |
| `name` | 唯一标识符，也作为 Skill 的命名空间前缀（如 `/my-first-plugin:hello`） |
| `description` | 在插件管理器浏览/安装时显示 |
| `version` | 可选。设置后，只有手动 bump 此字段时用户才会收到更新。省略时若通过 git 分发，则使用 commit SHA，每次 commit 都算一个新版本。详见 [版本管理](https://code.claude.com/docs/en/plugins-reference#version-management) |
| `author` | 可选。用于署名 |

更多字段如 `homepage`、`repository`、`license` 等，参见[完整清单 Schema](https://code.claude.com/docs/en/plugins-reference#plugin-manifest-schema)。

#### 第三步：添加 Skill

**Skill 存放在 `skills/` 目录中。** 每个 Skill 是一个包含 `SKILL.md` 文件的子目录。子目录名即 Skill 名，加上插件命名空间前缀（例如 `hello/` 在名为 `my-first-plugin` 的插件中会变成 `/my-first-plugin:hello`）。

```bash
mkdir -p my-first-plugin/skills/hello
```

创建 `my-first-plugin/skills/hello/SKILL.md`：

```markdown
---
description: Greet the user with a friendly message
disable-model-invocation: true
---

Greet the user warmly and ask how you can help them today.
```

#### 第四步：测试插件

**用 `--plugin-dir` 标志加载插件进行测试：**

```bash
claude --plugin-dir ./my-first-plugin
```

启动后，试用你的新 Skill：

```shell
/my-first-plugin:hello
```

Claude 会用友好的问候回应。运行 `/help` 可以看到你的 Skill 列在插件命名空间下。

> [!NOTE]
> **为什么要命名空间？** 插件 Skill 始终带命名空间前缀（如 `/my-first-plugin:hello`），这样即使多个插件有同名 Skill 也不会冲突。想更改前缀，修改 `plugin.json` 中的 `name` 字段即可。

#### 第五步：添加 Skill 参数

**通过 `$ARGUMENTS` 占位符让 Skill 接受用户输入。** 它会捕获用户在 Skill 名后面输入的所有文本。

更新 `SKILL.md`：

```markdown
---
description: Greet the user with a personalized message
---

# Hello Skill

Greet the user named "$ARGUMENTS" warmly and ask how you can help them today. Make the greeting personal and encouraging.
```

运行 `/reload-plugins` 加载变更，然后试一下带参数的调用：

```shell
/my-first-plugin:hello Alex
```

Claude 会用你的名字来打招呼。参数传递的更多用法见 [Skills](https://code.claude.com/docs/en/skills#pass-arguments-to-skills)。

---

**至此你已经成功创建并测试了一个插件，包含以下关键组件：**

* **插件清单**（`.claude-plugin/plugin.json`）：描述插件元数据
* **Skills 目录**（`skills/`）：存放自定义 Skill
* **Skill 参数**（`$ARGUMENTS`）：捕获用户输入实现动态行为

> [!TIP]
> `--plugin-dir` 适合开发和测试阶段。准备好分享给他人时，参见 [创建和分发插件市场](https://code.claude.com/docs/en/plugin-marketplaces)。

## 在 Skills 目录中开发插件

**不想每次启动都传 `--plugin-dir`，可以把插件放在 Skills 目录中让 Claude Code 自动加载。** `claude plugin init` 可以快速搭建脚手架：

```bash
claude plugin init my-tool
```

这会在 `~/.claude/skills/my-tool/` 创建一个带 `.claude-plugin/plugin.json` 清单和初始 `SKILL.md` 的结构。下次启动会话时，它会以 `my-tool@skills-dir` 的身份自动加载，不需要市场安装步骤。

关于自动加载规则、个人 vs 项目作用域、工作区信任要求，以及更新或移除方式，参见 [Skills 目录插件](https://code.claude.com/docs/en/plugins-reference#skills-directory-plugins)。

## 插件结构总览

**你已经创建了一个带 Skill 的插件，但插件还可以包含更多组件：自定义 Agent、Hook、MCP 服务器、LSP 服务器和后台监控器。**

> [!WARNING]
> **常见错误**：不要把 `commands/`、`agents/`、`skills/` 或 `hooks/` 放到 `.claude-plugin/` 目录里面。只有 `plugin.json` 放在 `.claude-plugin/` 内，其余目录都必须在插件根目录下。

| 目录 | 位置 | 用途 |
| :--- | :--- | :--- |
| `.claude-plugin/` | 插件根目录 | 存放 `plugin.json` 清单（如果各组件都使用默认位置则可省略） |
| `skills/` | 插件根目录 | Skill，格式为 `<name>/SKILL.md` 子目录 |
| `commands/` | 插件根目录 | Skill 的扁平 Markdown 文件形式。新插件建议用 `skills/` |
| `agents/` | 插件根目录 | 自定义 Agent 定义 |
| `hooks/` | 插件根目录 | 事件处理器，配置在 `hooks.json` 中 |
| `.mcp.json` | 插件根目录 | MCP 服务器配置 |
| `.lsp.json` | 插件根目录 | LSP 服务器配置，提供代码智能 |
| `monitors/` | 插件根目录 | 后台监控器配置，配置在 `monitors.json` 中 |
| `bin/` | 插件根目录 | 可执行文件，插件启用时会加入 Bash 工具的 `PATH` |
| `settings.json` | 插件根目录 | 插件启用时应用的默认[设置](https://code.claude.com/docs/en/settings) |

**如果插件只有一个 Skill，可以把 `SKILL.md` 直接放在插件根目录**，不需要创建 `skills/` 子目录。Claude Code 会将其作为单个 Skill 加载，并用 frontmatter 中的 `name` 字段作为调用名。如果后续可能增加更多 Skill，建议一开始就用 `skills/` 目录结构。

> [!NOTE]
> **下一步**：想添加更多功能？跳转到[开发更复杂的插件](#开发更复杂的插件)，了解如何添加 Agent、Hook、MCP 和 LSP 服务器。完整技术规格参见 [插件参考](https://code.claude.com/docs/en/plugins-reference)。

## 开发更复杂的插件

**掌握基础插件开发后，你可以创建更复杂的扩展。**

### 为插件添加 Skill

**插件可以包含 [Agent Skill](https://code.claude.com/docs/en/skills) 来扩展 Claude 的能力。** Skill 是模型驱动的：Claude 会根据任务上下文自动调用它们。

在插件根目录下添加 `skills/` 目录，其中每个 Skill 是一个包含 `SKILL.md` 的子目录：

```text
my-plugin/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── code-review/
        └── SKILL.md
```

每个 `SKILL.md` 包含 YAML frontmatter 和指令。务必写好 `description`，让 Claude 知道何时该使用这个 Skill：

```yaml
---
description: Reviews code for best practices and potential issues. Use when reviewing code, checking PRs, or analyzing code quality.
---

When reviewing code, check for:
1. Code organization and structure
2. Error handling
3. Security concerns
4. Test coverage
```

安装插件后，运行 `/reload-plugins` 加载 Skill。完整的 Skill 编写指南（包括渐进式展开和工具限制）参见 [Agent Skills](https://code.claude.com/docs/en/skills)。

### 为插件添加 LSP 服务器

> [!TIP]
> TypeScript、Python、Rust 等常见语言，直接从官方市场安装预构建的 LSP 插件即可。只有当你需要支持尚未覆盖的语言时，才需要自定义 LSP 插件。

**LSP（语言服务器协议）插件为 Claude 提供实时的代码智能能力。** 如果你需要支持没有官方 LSP 插件的语言，可以在插件中添加 `.lsp.json` 文件：

```json
{
  "go": {
    "command": "gopls",
    "args": ["serve"],
    "extensionToLanguage": {
      ".go": "go"
    }
  }
}
```

安装该插件的用户需要在本地预装对应的语言服务器二进制文件。

完整 LSP 配置选项参见 [LSP 服务器](https://code.claude.com/docs/en/plugins-reference#lsp-servers)。

### 为插件添加后台监控器

**后台监控器让插件在后台持续监听日志、文件或外部状态变化，并在事件到达时通知 Claude。** 插件激活时 Claude Code 自动启动每个监控器，无需你手动指示 Claude 开始监听。

在插件根目录添加 `monitors/monitors.json` 文件，内容为监控器条目的数组：

```json
[
  {
    "name": "error-log",
    "command": "tail -F ./logs/error.log",
    "description": "Application error log"
  }
]
```

`command` 的每行 stdout 输出都会在会话中作为通知传递给 Claude。完整 schema（包括 `when` 触发器和变量替换）参见 [Monitors](https://code.claude.com/docs/en/plugins-reference#monitors)。

### 随插件附带默认设置

**插件可以在根目录包含 `settings.json` 文件，在插件启用时应用默认配置。** 当前仅支持 `agent` 和 `subagentStatusLine` 字段。

设置 `agent` 会将插件中某个[自定义 Agent](https://code.claude.com/docs/en/sub-agents) 激活为主线程 Agent，应用其系统 Prompt、工具限制和模型配置。这样插件在启用时就能改变 Claude Code 的默认行为。

```json
{
  "agent": "security-reviewer"
}
```

上面的示例会激活插件 `agents/` 目录中定义的 `security-reviewer` Agent。`settings.json` 中的设置优先级高于 `plugin.json` 中声明的 `settings`。未知的 key 会被静默忽略。

### 组织复杂插件

**对于包含众多组件的插件，按功能模块组织目录结构。** 完整的目录布局和组织模式参见 [插件目录结构](https://code.claude.com/docs/en/plugins-reference#plugin-directory-structure)。

### 本地测试插件

**用 `--plugin-dir` 标志在开发阶段测试插件。** 它直接加载插件，不需要走安装流程。

```bash
claude --plugin-dir ./my-plugin
```

该标志也接受插件目录的 `.zip` 压缩包（需 Claude Code v2.1.128+）：

```bash
claude --plugin-dir ./my-plugin.zip
```

**当 `--plugin-dir` 加载的插件与已安装的市场插件同名时，本地版本优先。** 这让你可以在不卸载已安装插件的情况下测试修改。例外情况是被 Managed Settings 强制启用/禁用的插件，`--plugin-dir` 无法覆盖这些。

开发过程中修改了插件内容后，运行 `/reload-plugins` 即可热加载更新，不需要重启。它会重新加载插件、Skill、Agent、Hook、插件 MCP 服务器和插件 LSP 服务器。逐项测试你的组件：

* 用 `/plugin-name:skill-name` 试用 Skill
* 在 `/agents` 中确认 Agent 出现
* 验证 Hook 按预期触发

> [!TIP]
> 可以多次指定 `--plugin-dir` 来同时加载多个插件：
>
> ```bash
> claude --plugin-dir ./plugin-one --plugin-dir ./plugin-two
> ```

**如果插件已打包为 `.zip` 并托管在 URL（如 CI 构建产物），用 `--plugin-url` 加载。** Claude Code 在启动时下载压缩包并仅在当前会话中加载。如果下载失败或压缩包无效，Claude Code 会报告插件加载错误并在无该插件的情况下启动。安全注意事项与其他插件来源相同：只指向你控制或信任的压缩包。

加载多个插件时，对每个 URL 重复该标志：

```bash
claude --plugin-url https://example.com/my-plugin.zip --plugin-url https://example.com/other.zip
```

或将多个空格分隔的 URL 作为一个引号参数传入：

```bash
claude --plugin-url "https://example.com/my-plugin.zip https://example.com/other.zip"
```

### 调试插件问题

**插件没按预期工作时的排查步骤：**

1. **检查目录结构**：确保各目录在插件根目录下，而非 `.claude-plugin/` 里面
2. **逐项测试组件**：分别检查每个 Skill、Agent 和 Hook
3. **使用验证和调试工具**：参见[调试和开发工具](https://code.claude.com/docs/en/plugins-reference#debugging-and-development-tools)了解 CLI 命令和排查技巧

### 分享你的插件

**插件准备好分享时的步骤：**

1. **添加文档**：写一个 `README.md`，说明安装和使用方法
2. **选择版本策略**：决定是设置显式的 `version` 字段还是依赖 git commit SHA。参见 [版本管理](https://code.claude.com/docs/en/plugins-reference#version-management)
3. **创建或使用市场**：通过[插件市场](https://code.claude.com/docs/en/plugin-marketplaces)分发安装
4. **让他人测试**：在更大范围发布前，让团队成员先行测试

插件上架市场后，其他人可以按照 [发现并安装插件](https://code.claude.com/docs/en/discover-plugins) 中的说明安装。如果想把插件限制在团队内部，将市场托管在[私有仓库](https://code.claude.com/docs/en/plugin-marketplaces#private-repositories)中即可。

### 提交插件到社区市场

**Anthropic 维护两个公开的 Claude Code 插件市场：**

* **`claude-plugins-official`**：由 Anthropic 维护的精选插件集。首次以交互模式启动 Claude Code 时自动注册。在首次启动前运行的非交互脚本需要手动添加：`claude plugin marketplace add anthropics/claude-plugins-official`。
* **`claude-community`**：公开的社区市场，第三方提交经审核后上架。用户通过 `/plugin marketplace add anthropics/claude-plugins-community` 添加后，可从 `@claude-community` 安装。

**提交插件进行社区市场审核，使用以下入口之一：**

* **claude.ai**：[claude.ai/admin-settings/directory/submissions/plugins/new](https://claude.ai/admin-settings/directory/submissions/plugins/new)
* **Console**：[platform.claude.com/plugins/submit](https://platform.claude.com/plugins/submit)

claude.ai 入口要求 Team 或 Enterprise 组织并具有目录管理权限；组织 Owner 默认拥有此权限。不属于 Team 或 Enterprise 组织的个人开发者可以使用 Console 入口。

**提交前请在本地运行 `claude plugin validate`。** 审核流水线会执行相同检查，并附加自动化安全扫描。

审核通过的插件会被固定到 [`anthropics/claude-plugins-community`](https://github.com/anthropics/claude-plugins-community) 目录中的特定 commit SHA，CI 会在你向仓库推送新 commit 时自动更新这个固定值。公开目录从审核流水线每夜同步，因此审核通过到插件实际可见之间可能有延迟。要确认插件是否已可安装，在[社区目录](https://github.com/anthropics/claude-plugins-community/blob/main/.claude-plugin/marketplace.json)中搜索其名称。

官方市场 `claude-plugins-official` 有独立的遴选流程。Anthropic 自行决定收录哪些插件，没有申请通道，提交表单不会将插件添加到官方市场。

如果 Anthropic 将你的插件收录到官方市场，你的 CLI 可以向 Claude Code 用户推荐安装它。参见 [从 CLI 推荐你的插件](https://code.claude.com/docs/en/plugin-hints)。

> [!NOTE]
> 完整技术规格、调试技巧和分发策略参见 [插件参考](https://code.claude.com/docs/en/plugins-reference)。

## 将现有配置转换为插件

**如果你已经在 `.claude/` 目录中有 Skill 或 Hook，可以把它们转换为插件以便共享和分发。**

### 迁移步骤

#### 第一步：创建插件结构

创建新的插件目录：

```bash
mkdir -p my-plugin/.claude-plugin
```

创建清单文件 `my-plugin/.claude-plugin/plugin.json`：

```json
{
  "name": "my-plugin",
  "description": "Migrated from standalone configuration",
  "version": "1.0.0"
}
```

#### 第二步：复制现有文件

把现有配置复制到插件目录：

```bash
# 复制 commands
cp -r .claude/commands my-plugin/

# 复制 agents（如果有）
cp -r .claude/agents my-plugin/

# 复制 skills（如果有）
cp -r .claude/skills my-plugin/
```

#### 第三步：迁移 Hook

如果你在 settings 中配置了 Hook，创建 hooks 目录：

```bash
mkdir my-plugin/hooks
```

创建 `my-plugin/hooks/hooks.json`，把 `.claude/settings.json` 或 `settings.local.json` 中的 `hooks` 对象复制过来，格式相同。命令通过 stdin 接收 JSON 格式的 hook 输入，用 `jq` 提取文件路径：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{ "type": "command", "command": "jq -r '.tool_input.file_path' | xargs npm run lint:fix" }]
      }
    ]
  }
}
```

#### 第四步：测试迁移后的插件

加载插件确认一切正常：

```bash
claude --plugin-dir ./my-plugin
```

逐项测试：运行你的命令、在 `/agents` 中确认 Agent 出现、验证 Hook 正确触发。

### 迁移前后对比

| 独立配置（`.claude/`） | 插件 |
| :--- | :--- |
| 仅在单个项目中可用 | 可通过市场共享 |
| 文件在 `.claude/commands/` | 文件在 `plugin-name/commands/` |
| Hook 在 `settings.json` 中 | Hook 在 `hooks/hooks.json` 中 |
| 共享需要手动复制 | 通过 `/plugin install` 安装 |

> [!NOTE]
> 迁移完成后，删除 `.claude/` 中的原始文件以避免重复。项目和用户级 `.claude/agents/` 定义会覆盖同名的插件 Agent，只有移除原始文件后插件版本才会生效。

## 后续学习

**根据你的角色选择不同的深入方向。**

### 插件使用者

* [发现并安装插件](https://code.claude.com/docs/en/discover-plugins)：浏览市场和安装插件
* [配置团队市场](https://code.claude.com/docs/en/discover-plugins#configure-team-marketplaces)：为团队设置仓库级插件

### 插件开发者

* [创建和分发市场](https://code.claude.com/docs/en/plugin-marketplaces)：打包和分享你的插件
* [插件参考](https://code.claude.com/docs/en/plugins-reference)：完整技术规格
* 深入各组件的专题文档：
  * [Skills](https://code.claude.com/docs/en/skills)：Skill 开发细节
  * [子 Agent](https://code.claude.com/docs/en/sub-agents)：Agent 配置与能力
  * [Hooks](https://code.claude.com/docs/en/hooks)：事件处理与自动化
  * [MCP](https://code.claude.com/docs/en/mcp)：外部工具集成
