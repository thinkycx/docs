---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】发现和安装插件
description: 介绍如何通过插件市场发现和安装预构建的 Claude Code 插件，涵盖官方市场、社区市场的使用方法，以及插件管理的完整操作流程。
category: translation
tags: [claude-code, plugins, marketplace, translation]
refs: [https://code.claude.com/docs/en/discover-plugins.md]
---

# 通过市场发现和安装预构建插件

> **核心能力**: 从插件市场中查找和安装插件，为 Claude Code 扩展新的技能、Agent 和功能。

**插件是 Claude Code 的扩展机制。** 插件可以为 Claude Code 添加技能（skills）、Agent、钩子（hooks）和 MCP 服务器。插件市场（marketplace）是一个目录，帮助你发现和安装这些扩展，而无需自己从零构建。

想创建和分发自己的插件市场？参见 [创建和分发插件市场](https://code.claude.com/docs/en/plugin-marketplaces)。

## 市场的工作原理

**市场本质上是一个插件目录。** 使用市场分两步：

| 步骤 | 操作 | 说明 |
|:-----|:-----|:-----|
| 1 | 添加市场 | 将目录注册到 Claude Code，此时不会安装任何插件 |
| 2 | 安装插件 | 浏览目录，选择需要的插件进行安装 |

可以类比应用商店：添加商店只是让你能浏览它的内容，具体下载哪些应用仍由你自己决定。

## 官方 Anthropic 市场

**官方市场自动可用。** 官方 Anthropic 市场（`claude-plugins-official`）在启动 Claude Code 时自动加载。运行 `/plugin` 并进入 **Discover** 标签页即可浏览，也可以在 [claude.com/plugins](https://claude.com/plugins) 查看目录。

从官方市场安装插件的命令格式：

```shell
/plugin install <name>@claude-plugins-official
```

例如安装 GitHub 集成：

```shell
/plugin install github@claude-plugins-official
```

如果 Claude Code 提示找不到插件，可能是市场缺失或过期。运行 `/plugin marketplace update claude-plugins-official` 刷新，或者用 `/plugin marketplace add anthropics/claude-plugins-official` 重新添加，然后重试安装。

> **注意**: 官方市场由 Anthropic 策划，是否收录由 Anthropic 决定。应用内的提交表单会将插件添加到[社区市场](#社区市场)而非官方市场。如需独立分发插件，请[创建自己的市场](https://code.claude.com/docs/en/plugin-marketplaces)并分享给用户。

官方市场包含以下几类插件：

### 代码智能（Code Intelligence）

**通过 LSP 赋予 Claude 精确代码导航能力。** 代码智能插件启用 Claude Code 内置的 LSP 工具，让 Claude 能够跳转定义、查找引用、在编辑后立即看到类型错误。这些插件配置的是 [Language Server Protocol](https://microsoft.github.io/language-server-protocol/) 连接——与 VS Code 代码智能背后的技术相同。

这些插件需要你的系统上已安装对应的语言服务器二进制文件。如果你已安装了某个语言服务器，Claude 可能会在你打开项目时提示安装对应插件。

| 语言 | 插件 | 需要的二进制文件 |
|:-----|:-----|:-----------------|
| C/C++ | `clangd-lsp` | `clangd` |
| C# | `csharp-lsp` | `csharp-ls` |
| Go | `gopls-lsp` | `gopls` |
| Java | `jdtls-lsp` | `jdtls` |
| Kotlin | `kotlin-lsp` | `kotlin-language-server` |
| Lua | `lua-lsp` | `lua-language-server` |
| PHP | `php-lsp` | `intelephense` |
| Python | `pyright-lsp` | `pyright-langserver` |
| Rust | `rust-analyzer-lsp` | `rust-analyzer` |
| Swift | `swift-lsp` | `sourcekit-lsp` |
| TypeScript | `typescript-lsp` | `typescript-language-server` |

你也可以为其他语言[创建自己的 LSP 插件](https://code.claude.com/docs/en/plugins-reference#lsp-servers)。

> **提示**: 如果在 `/plugin` 的 Errors 标签页中看到 `Executable not found in $PATH`，说明需要安装上表中对应的二进制文件。

#### 代码智能插件带来的能力

**安装后 Claude 获得自动诊断和精确导航两大能力。** 一旦代码智能插件安装完成且语言服务器二进制文件可用，Claude 将获得：

- **自动诊断**: Claude 每次编辑文件后，语言服务器会自动分析变更并报告错误和警告。Claude 无需运行编译器或 lint 工具即可看到类型错误、缺失导入和语法问题。如果 Claude 引入了错误，它会在同一轮对话中发现并修复。按 **Ctrl+O** 可在出现"diagnostics found"指示时查看内联诊断。
- **代码导航**: Claude 可以使用语言服务器跳转定义、查找引用、悬停获取类型信息、列出符号、查找实现和追踪调用层级。这些操作比基于 grep 的搜索更精确，但可用性因语言和环境而异。

遇到问题请参见[代码智能问题排查](#代码智能问题)。

### 外部集成

**预配置的 MCP 服务器，开箱即用连接外部服务。** 这些插件打包了预配置的 [MCP 服务器](https://code.claude.com/docs/en/mcp)，让你无需手动配置即可连接 Claude 到外部服务：

| 类别 | 插件 |
|:-----|:-----|
| 代码管理 | `github`、`gitlab` |
| 项目管理 | `atlassian`（Jira/Confluence）、`asana`、`linear`、`notion` |
| 设计 | `figma` |
| 基础设施 | `vercel`、`firebase`、`supabase` |
| 通信 | `slack` |
| 监控 | `sentry` |

### 自动安全审查

**`security-guidance` 插件在 Claude 每次变更后自动审查常见漏洞。** 它会审查 Claude 所做的每处修改，检测常见安全漏洞，并指导 Claude 在同一会话中修复发现的问题。详见 [在 Claude 编码时捕获安全问题](https://code.claude.com/docs/en/security-guidance)。

### 开发工作流

**为常见开发任务提供技能和 Agent 的插件：**

| 插件 | 用途 |
|:-----|:-----|
| `commit-commands` | Git 提交工作流，包括 commit、push 和创建 PR |
| `pr-review-toolkit` | 专门用于审查 PR 的 Agent |
| `agent-sdk-dev` | 使用 Claude Agent SDK 进行开发的工具 |
| `plugin-dev` | 创建自定义插件的工具包 |

### 输出风格

**自定义 Claude 的回复风格：**

| 插件 | 效果 |
|:-----|:-----|
| `explanatory-output-style` | 提供关于实现选择的教学性解释 |
| `learning-output-style` | 交互式学习模式，帮助技能提升 |

## 社区市场

**社区市场托管经过 Anthropic 自动验证和安全筛查的第三方插件。** 社区市场位于 [`anthropics/claude-plugins-community`](https://github.com/anthropics/claude-plugins-community)，每个插件在目录中锁定到特定的 commit SHA。与官方市场不同，需要手动添加：

```shell
/plugin marketplace add anthropics/claude-plugins-community
```

然后使用 `claude-community` 市场名安装插件：

```shell
/plugin install <plugin-name>@claude-community
```

要将自己的插件提交到社区市场，请参见[提交插件到社区市场](https://code.claude.com/docs/en/plugins#submit-your-plugin-to-the-community-marketplace)。

## 实践：添加演示市场

**Anthropic 维护了一个演示市场展示插件系统的可能性。** 演示插件市场位于 [anthropics/claude-code](https://github.com/anthropics/claude-code/tree/main/plugins)（`claude-code-plugins`），包含展示插件系统能力的示例插件。与官方市场不同，需要手动添加。

### 第一步：添加市场

在 Claude Code 中运行：

```shell
/plugin marketplace add anthropics/claude-code
```

这会下载市场目录并使其中的插件可供你使用。

### 第二步：浏览可用插件

运行 `/plugin` 打开插件管理器。会出现一个标签页界面，按 **Tab** 切换（**Shift+Tab** 反向切换）：

| 标签页 | 功能 |
|:-------|:-----|
| **Discover** | 浏览所有已添加市场的可用插件 |
| **Installed** | 查看和管理已安装的插件 |
| **Marketplaces** | 添加、删除或更新市场 |
| **Errors** | 查看插件加载错误 |

进入 **Discover** 标签页查看你刚添加的市场中的插件。当管理员通过 [`pluginSuggestionMarketplaces`](https://code.claude.com/docs/en/settings#available-settings) 托管设置将市场加入白名单时，与当前工作目录相关的插件会置顶显示 **suggested for this directory** 标签。

### 第三步：安装插件

选中一个插件查看详情。详情面板展示插件包含的内容和开销：

- **Context cost** 估算：显示插件每轮对话会增加多少 token 到你的[上下文窗口](https://code.claude.com/docs/en/features-overview#understand-context-costs)
- **Last updated** 日期
- **Will install** 部分：列出插件的命令、Agent、技能、钩子、MCP 服务器和 LSP 服务器，安装前可全面预览

选择安装范围：

| 范围 | 说明 |
|:-----|:-----|
| **User scope** | 为自己安装，跨所有项目生效 |
| **Project scope** | 为本仓库所有协作者安装 |
| **Local scope** | 仅为自己在本仓库安装 |

例如选择 **commit-commands**（一个添加 git 工作流技能的插件），安装到用户范围。

也可以从命令行直接安装：

```shell
/plugin install commit-commands@claude-code-plugins
```

关于范围的更多信息，参见[配置范围](https://code.claude.com/docs/en/settings#configuration-scopes)。

### 第四步：使用新插件

安装后运行 `/reload-plugins` 激活插件。插件技能以插件名作为命名空间，所以 **commit-commands** 提供的技能类似 `/commit-commands:commit`。

试试看——修改一个文件然后运行：

```shell
/commit-commands:commit
```

这会暂存你的更改、生成提交信息并创建提交。

每个插件的工作方式不同。查看 **Discover** 标签页中插件的详情了解它提供的命令和技能，或访问其主页获取使用指南。

---

以下内容涵盖添加市场、安装插件和管理配置的所有方式。

## 添加市场

**使用 `/plugin marketplace add` 命令从不同来源添加市场。**

> **快捷方式**: 可以用 `/plugin market` 代替 `/plugin marketplace`，用 `rm` 代替 `remove`。

支持的来源类型：

| 来源类型 | 格式 |
|:---------|:-----|
| GitHub 仓库 | `owner/repo` 格式 |
| Git URL | 任意 git 仓库 URL（含 GitLab、Bitbucket、自托管） |
| 本地路径 | 目录或 `marketplace.json` 文件的直接路径 |
| 远程 URL | 托管的 `marketplace.json` 文件的直接 URL |

### 从 GitHub 添加

添加包含 `.claude-plugin/marketplace.json` 文件的 GitHub 仓库，使用 `owner/repo` 格式：

```shell
/plugin marketplace add anthropics/claude-code
```

### 从其他 Git 托管平台添加

**提供完整 URL 即可添加任何 Git 仓库。** 适用于 GitLab、Bitbucket 和自托管服务器。加上 `.git` 后缀，让 Claude Code 将其识别为需要克隆的仓库而非 `marketplace.json` 的直接链接。

使用 HTTPS：

```shell
/plugin marketplace add https://gitlab.com/company/plugins.git
```

使用 SSH：

```shell
/plugin marketplace add git@gitlab.com:company/plugins.git
```

指定特定分支或标签，追加 `#` 加引用名：

```shell
/plugin marketplace add https://gitlab.com/company/plugins.git#v1.0.0
```

### 从本地路径添加

添加包含 `.claude-plugin/marketplace.json` 文件的本地目录：

```shell
/plugin marketplace add ./my-marketplace
```

也可以直接指定 `marketplace.json` 文件路径：

```shell
/plugin marketplace add ./path/to/marketplace.json
```

### 从远程 URL 添加

通过 URL 添加远程 `marketplace.json` 文件：

```shell
/plugin marketplace add https://example.com/marketplace.json
```

> **注意**: 基于 URL 的市场相比基于 Git 的市场有一些限制。如果安装插件时遇到"path not found"错误，参见[故障排查](https://code.claude.com/docs/en/plugin-marketplaces#plugins-with-relative-paths-fail-in-url-based-marketplaces)。

## 安装插件

**添加市场后即可直接安装插件。** 命令默认安装到用户范围：

```shell
/plugin install plugin-name@marketplace-name
```

要选择不同的[安装范围](https://code.claude.com/docs/en/settings#configuration-scopes)，使用交互式 UI：运行 `/plugin`，进入 **Discover** 标签页，对某个插件按 **Enter**。你会看到以下选项：

| 范围 | 说明 |
|:-----|:-----|
| **User scope**（默认） | 为自己安装，跨所有项目 |
| **Project scope** | 为本仓库所有协作者安装，添加到 `.claude/settings.json` |
| **Local scope** | 仅为自己在本仓库安装，不与协作者共享 |

你可能还会看到 **managed** 范围的插件。这些由管理员通过[托管设置](https://code.claude.com/docs/en/settings#settings-files)安装，不可修改。

> **警告**: 安装前请确保你信任该插件。Anthropic 不控制插件包含的 MCP 服务器、文件或其他软件，也无法验证它们是否按预期工作。请查看每个插件的主页获取更多信息。

## 管理已安装的插件

**运行 `/plugin` 进入 Installed 标签页查看、启用、禁用或卸载插件。** 列表按范围分组，问题优先展示：有加载错误或未解决依赖的插件排在最前，其次是收藏的插件，禁用的插件折叠在底部。

可用操作：

| 快捷键/操作 | 功能 |
|:------------|:-----|
| `f` | 收藏/取消收藏选中的插件 |
| 输入文字 | 按插件名或描述筛选 |
| Enter | 打开详情视图，可启用、禁用或卸载 |

详情视图展示插件贡献的组件：命令、技能、Agent、钩子、MCP 服务器和 LSP 服务器。同样的信息也可通过命令行 `claude plugin details` 获取。

**"Not used recently"分组帮助你发现不再使用的插件。** 在 Claude Code v2.1.187 及之后版本，Installed 标签页会对至少两周（跨越至少 10 个会话）未调用的市场插件显示 **Not used recently** 分组，详情视图也会显示 **Last used** 行。用这些信息找到已不使用但仍增加启动和上下文开销的插件，然后禁用或卸载。

组织托管的插件、通过 `--plugin-dir` 加载的插件永远不会被列为未使用。贡献 LSP 服务器、主题、输出风格、监控或工作流的插件也不会被列为未使用，因为它们无需调用即可产生价值。当组织通过 [`strictKnownMarketplaces`](https://code.claude.com/docs/en/settings#strictknownmarketplaces) 限制市场时，该分组和 **Last used** 行都会隐藏。

安装声明了依赖的插件时，安装输出会列出随之自动安装的依赖项。

### 命令行管理

列出已安装的插件（不打开菜单）：

```shell
/plugin list
```

传入 `--enabled` 或 `--disabled` 仅显示对应状态的插件。

禁用插件（不卸载）：

```shell
/plugin disable plugin-name@marketplace-name
```

重新启用已禁用的插件：

```shell
/plugin enable plugin-name@marketplace-name
```

完全移除插件：

```shell
/plugin uninstall plugin-name@marketplace-name
```

`--scope` 选项可指定目标范围：

```shell
claude plugin install formatter@your-org --scope project
claude plugin uninstall formatter@your-org --scope project
```

### 不重启应用即生效插件变更

**安装、启用或禁用插件后，运行 `/reload-plugins` 无需重启即可激活。**

```shell
/reload-plugins
```

Claude Code 会重新加载所有活动插件，并显示插件、技能、Agent、钩子、MCP 服务器和 LSP 服务器的计数。

重新加载对下次请求有 token 开销：新加载的组件会在对话追加内容中声明自身，而已有历史仍从 prompt 缓存中读取。提供 MCP 服务器且其工具未通过 [tool search](https://code.claude.com/docs/en/mcp#scale-with-mcp-tool-search) 延迟加载的插件开销更大：变更会使缓存失效，下次请求需要重新读取整个对话。此时 `/reload-plugins` 会显示警告且不应用重载；传入 `--force` 可强制应用。详见[启用或禁用插件](https://code.claude.com/docs/en/prompt-caching#enabling-or-disabling-a-plugin)。

## 管理市场

**通过交互式 `/plugin` 界面或 CLI 命令管理市场。**

### 使用交互式界面

运行 `/plugin` 进入 **Marketplaces** 标签页可以：

- 查看所有已添加的市场及其来源和状态
- 添加新市场
- 更新市场列表以获取最新插件
- 移除不再需要的市场

### 使用 CLI 命令

列出所有已配置的市场：

```shell
/plugin marketplace list
```

刷新市场的插件列表：

```shell
/plugin marketplace update marketplace-name
```

移除市场：

```shell
/plugin marketplace remove marketplace-name
```

> **警告**: 移除市场会卸载你从该市场安装的所有插件。

### 配置自动更新

**Claude Code 可以在启动时自动更新市场及其已安装的插件。** 当市场启用了自动更新，Claude Code 会刷新市场数据并将已安装的插件更新到最新版本。如果有插件被更新，你会看到运行 `/reload-plugins` 的提示通知。

通过 UI 为单个市场切换自动更新：

1. 运行 `/plugin` 打开插件管理器
2. 选择 **Marketplaces**
3. 选择一个市场
4. 选择 **Enable auto-update** 或 **Disable auto-update**

官方 Anthropic 市场默认启用自动更新。第三方和本地开发市场默认禁用自动更新。

管理员也可以在托管设置的 [`extraKnownMarketplaces`](https://code.claude.com/docs/en/settings#extraknownmarketplaces) 条目中设置 `"autoUpdate": true`，为组织市场启用自动更新，无需每个用户手动切换。

要完全禁用所有自动更新（Claude Code 和所有插件），设置 `DISABLE_AUTOUPDATER` 环境变量。详见[自动更新](https://code.claude.com/docs/en/setup#auto-updates)。

要保留插件自动更新但禁用 Claude Code 自身的自动更新，将 `FORCE_AUTOUPDATE_PLUGINS=1` 与 `DISABLE_AUTOUPDATER` 一起设置：

```bash
export DISABLE_AUTOUPDATER=1
export FORCE_AUTOUPDATE_PLUGINS=1
```

当你想手动管理 Claude Code 更新但仍接收自动插件更新时，这很有用。

## 配置团队市场

**团队管理员可以在项目中设置市场自动安装。** 将市场配置添加到 `.claude/settings.json`，当团队成员信任该仓库文件夹时，Claude Code 会提示他们安装这些市场和插件。

在项目的 `.claude/settings.json` 中添加 `extraKnownMarketplaces`：

```json
{
  "extraKnownMarketplaces": {
    "my-team-tools": {
      "source": {
        "source": "github",
        "repo": "your-org/claude-plugins"
      }
    }
  }
}
```

完整配置选项（包括 `extraKnownMarketplaces` 和 `enabledPlugins`）参见[插件设置](https://code.claude.com/docs/en/settings#plugin-settings)。

## 安全性

**插件和市场是高度受信任的组件，可以在你的机器上以你的用户权限执行任意代码。** 只安装来自你信任来源的插件和市场。组织可以使用[托管市场限制](https://code.claude.com/docs/en/plugin-marketplaces#managed-marketplace-restrictions)来约束用户允许添加的市场。

## 故障排查

### /plugin 命令无法识别

如果出现"unknown command"或 `/plugin` 命令不显示：

1. **检查版本**: 运行 `claude --version` 查看当前安装版本
2. **更新 Claude Code**:
   - **Homebrew**: `brew upgrade claude-code`，或 `brew upgrade claude-code@latest`（如果安装的是该 cask）
   - **npm**: `npm install -g @anthropic-ai/claude-code@latest`
   - **原生安装器**: 按照[安装指南](https://code.claude.com/docs/en/setup)重新运行安装命令
3. **重启 Claude Code**: 更新后重启终端并重新运行 `claude`

### 常见问题

| 问题 | 解决方案 |
|:-----|:---------|
| 市场无法加载 | 确认 URL 可访问且 `.claude-plugin/marketplace.json` 存在于该路径 |
| 插件安装失败 | 检查插件源 URL 可访问且仓库为公开（或你有访问权限） |
| 安装后找不到文件 | 插件会被复制到缓存，引用插件目录外文件的路径将失效 |
| 插件技能不显示 | 清除缓存 `rm -rf ~/.claude/plugins/cache`，重启 Claude Code 并重新安装插件 |

详细排查方案参见市场指南中的[故障排查](https://code.claude.com/docs/en/plugin-marketplaces#troubleshooting)。调试工具参见[调试和开发工具](https://code.claude.com/docs/en/plugins-reference#debugging-and-development-tools)。

### 代码智能问题

| 问题 | 解决方案 |
|:-----|:---------|
| 语言服务器不启动 | 确认二进制文件已安装且在 `$PATH` 中可用。查看 `/plugin` 的 Errors 标签页了解详情 |
| 内存占用高 | `rust-analyzer` 和 `pyright` 等语言服务器在大项目上可能消耗大量内存。如遇内存问题，用 `/plugin disable <plugin-name>` 禁用该插件，改用 Claude 内置搜索工具 |
| 单一仓库中的误报诊断 | 如果工作区配置不正确，语言服务器可能会报告内部包的未解析导入错误。这不影响 Claude 编辑代码的能力 |

## 下一步

- **构建自己的插件**: 参见[插件](https://code.claude.com/docs/en/plugins)了解如何创建技能、Agent 和钩子
- **创建市场**: 参见[创建插件市场](https://code.claude.com/docs/en/plugin-marketplaces)将插件分发给团队或社区
- **技术参考**: 参见[插件参考](https://code.claude.com/docs/en/plugins-reference)获取完整规范
