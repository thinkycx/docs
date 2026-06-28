---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】桌面应用
description: Claude Code 桌面应用完整指南，涵盖会话管理、代码编写、工作区布局、Computer Use、扩展功能（MCP/Skills/Plugins）、环境配置、企业部署，以及从 CLI 迁移的对照说明。
category: translation
tags: [claude-code, desktop, translation]
refs:
  - https://code.claude.com/docs/en/desktop.md
---

# 桌面应用

> 充分利用 Claude Code 桌面版：并行会话与 Git 隔离、拖拽式面板布局、内置终端与文件编辑器、侧聊、计算机控制、通过手机发起 Dispatch 会话、可视化 diff 审查、应用预览、PR 监控、连接器，以及企业级配置。

Claude 桌面应用有三个标签页：**Chat** 用于对话，**Cowork** 用于 [Dispatch 和更长时间的代理工作](https://claude.com/product/cowork)，**Code** 用于软件开发。本文档是 Code 标签页的完整参考。

<CardGroup cols={2}>
  <Card title="下载 macOS 版" icon="apple" href="https://claude.ai/api/desktop/darwin/universal/dmg/latest/redirect?utm_source=claude_code&utm_medium=docs">
    Intel 与 Apple Silicon 通用版本
  </Card>

  <Card title="下载 Windows 版" icon="windows" href="https://claude.ai/api/desktop/win32/x64/setup/latest/redirect?utm_source=claude_code&utm_medium=docs">
    适用于 x64 处理器
  </Card>
</CardGroup>

**Windows ARM64 用户**请下载 [ARM64 安装包](https://claude.ai/api/desktop/win32/arm64/setup/latest/redirect?utm_source=claude_code\&utm_medium=docs)。Linux 暂无桌面版，请使用 [CLI](https://code.claude.com/docs/en/quickstart)。

**安装后**，启动 Claude，登录账号，点击 **Code** 标签页。Windows 首次打开时需要安装 [Git for Windows](https://git-scm.com/downloads/win)，安装完成后重启应用。首次使用的完整引导请参考[快速上手指南](https://code.claude.com/docs/en/desktop-quickstart)。

**会话是核心概念。** 在 Code 标签页中，每个对话就是一个**会话**：拥有独立的聊天历史、项目目录和代码变更，与其他会话互不影响。侧边栏列出所有会话，支持并行运行多个。在一个会话中，你可以：

* [审查和评论 diff](#review-changes-with-diff-view)，然后[跟踪 PR 的 CI 状态](#monitor-pull-request-status)
* 在内嵌浏览器中[预览运行中的应用](#preview-your-app)，Claude 会自动验证自己的修改
* [自由排列面板](#arrange-your-workspace)：聊天、diff、预览、终端、文件编辑器并排显示
* 提出[侧聊问题](#ask-a-side-question-without-derailing-the-session)，利用当前上下文但不干扰主线
* [连接外部工具](#connect-external-tools)，如 GitHub、Slack、Linear
* 让 Claude [打开应用并控制屏幕](#let-claude-use-your-computer)
* 在本地运行，或在[云端](#run-long-running-tasks-remotely)运行，或通过 [SSH](#ssh-sessions) 运行

**更多功能**：[定时周期性任务](https://code.claude.com/docs/en/desktop-scheduled-tasks)、[快捷键](#keyboard-shortcuts)、[手机发送任务](#sessions-from-dispatch)，请参见对应章节。如果你之前使用终端版 CLI，请参见 [CLI 对比](#coming-from-the-cli)了解哪些功能可以延续。

## 开始一个会话

**发送第一条消息前**，在输入区域配置四项内容：

| 配置项 | 说明 |
| --- | --- |
| **环境** | 选择 Claude 的运行位置。**Local** 表示本机，**Remote** 表示 Anthropic 云端，或选择 [**SSH 连接**](#ssh-sessions) 连接你自己管理的远程机器。详见[环境配置](#environment-configuration)。 |
| **项目目录** | 选择 Claude 工作的文件夹或仓库。云端会话支持添加[多个仓库](#run-long-running-tasks-remotely)。 |
| **模型** | 在发送按钮旁的下拉菜单中选择[模型](https://code.claude.com/docs/en/model-config#available-models)。会话中途可随时切换。 |
| **权限模式** | 通过[模式选择器](#choose-a-permission-mode)决定 Claude 的自主程度。会话中途可随时切换。 |

输入任务描述，按 **Enter** 发送即可开始。每个会话独立跟踪各自的上下文和变更。

## 编写代码

**核心流程**：给 Claude 提供正确的上下文，控制它的自主程度，审查它做出的修改。

### 使用输入框

**输入指令并发送即可。** 输入你想让 Claude 做的事，按 **Enter** 发送。Claude 会读取项目文件、修改代码、执行命令，具体取决于你的[权限模式](#choose-a-permission-mode)。你可以随时调整方向：点击停止按钮立即中断，或直接输入纠正内容并按 **Enter** 发送（不会中断正在运行的操作）。Claude 会在当前操作完成后立刻读取你的纠正，并在下一步前做出调整。

**附加功能**：输入框旁的 **+** 按钮可以访问文件附件、[技能](#use-skills)、[连接器](#connect-external-tools)和[插件](#install-plugins)。

### 为提示添加文件和上下文

输入框支持两种方式引入外部上下文：

| 方式 | 说明 |
| --- | --- |
| **@提及文件** | 输入 `@` 后跟文件名，将文件添加到对话上下文。Claude 随后可以读取和引用该文件。云端会话不支持 @提及。 |
| **附加文件** | 通过附件按钮或拖拽方式将图片、PDF 及其他文件添加到提示中。适合分享 bug 截图、设计稿或参考文档。 |

### 选择权限模式

**权限模式决定 Claude 的自主程度**：是否在编辑文件或执行命令前征求许可。你可以随时通过发送按钮旁的模式选择器切换。建议新用户从 Ask permissions 开始，熟悉后再切换到 Auto accept edits 或 Plan mode。

| 模式 | 配置键 | 行为 |
| --- | --- | --- |
| **Ask permissions** | `default` | Claude 在编辑文件或执行命令前都会请求许可。你可以看到 diff 并逐个接受或拒绝。推荐新用户使用。 |
| **Auto accept edits** | `acceptEdits` | Claude 自动接受文件编辑和常见文件系统命令（如 `mkdir`、`touch`、`mv`），但其他终端命令仍需确认。适合信任文件变更、希望加快迭代速度的场景。 |
| **Plan mode** | `plan` | Claude 读取文件和执行命令来探索项目，然后提出计划，但不修改源代码。适合需要先审查方案的复杂任务。 |
| **Auto** | `auto` | Claude 执行所有操作，后台安全检查会验证是否与你的请求一致。减少权限提示的同时保持监督。在 Settings → Claude Code 中启用。详见下方[可用性要求](#auto-mode-availability)。 |
| **Bypass permissions** | `bypassPermissions` | Claude 无需权限提示即可运行，除非被显式的 [ask 规则](https://code.claude.com/docs/en/permissions#manage-permissions)强制要求；等同于 CLI 中的 `--dangerously-skip-permissions`。在 Settings → Claude Code 的 "Allow bypass permissions mode" 中启用。仅在沙箱容器或虚拟机中使用。企业管理员可禁用此选项。 |

`dontAsk` 权限模式仅在 [CLI](https://code.claude.com/docs/en/permission-modes#allow-only-pre-approved-tools-with-dontask-mode) 中可用。

<span id="auto-mode-availability" />

**Auto 模式的可用性**：Auto 模式为研究预览版，所有 Anthropic API 用户均可使用，要求 Claude Opus 4.6 或更高版本，或 Sonnet 4.6。在通过 Google Cloud Vertex AI 路由的企业部署中，Auto 模式默认关闭，需[设置 `CLAUDE_CODE_ENABLE_AUTO_MODE`](https://code.claude.com/docs/en/permission-modes#enable-auto-mode-on-bedrock-vertex-ai-or-foundry) 启用，且仅支持 Claude Opus 4.7 和 Opus 4.8。

<Tip title="最佳实践">
  复杂任务建议先用 Plan mode 让 Claude 制定方案，再切换到 Auto accept edits 或 Ask permissions 执行。详见[先探索、再规划、再编码](https://code.claude.com/docs/en/best-practices#explore-first-then-plan-then-code)。
</Tip>

**云端会话**支持 Accept edits、Plan mode 和 Auto mode。Accept edits 对应 `default` 模式：云端会话预先批准文件编辑，因此选择器显示 Accept edits 而非 Ask permissions。Bypass permissions 不可用，因为云端环境本身已经是沙箱化的。

企业管理员可以限制可用的权限模式。详见[企业配置](#enterprise-configuration)。

### 预览应用

**Claude 可以启动开发服务器并打开内嵌浏览器来验证修改。** 这对前端 Web 应用和后端服务器都适用：Claude 可以测试 API 端点、查看服务器日志，并自动修复发现的问题。大多数情况下，Claude 在编辑项目文件后会自动启动服务器。你也可以随时让 Claude 预览。默认情况下，Claude 每次编辑后都会[自动验证](#auto-verify-changes)修改。

预览面板也可以打开项目中的静态 HTML 文件、PDF、图片和视频。在聊天中点击 HTML、PDF、图片或视频路径即可在预览面板中打开。

**预览面板操作：**

* 直接在内嵌浏览器中与运行中的应用交互
* 观察 Claude 自动验证修改：它会截图、检查 DOM、点击元素、填写表单，并修复发现的问题
* 通过会话工具栏中的 **Preview** 下拉菜单启动或停止服务器
* 在下拉菜单中选择 **Persist sessions** 可以在服务器重启后保留 Cookie 和本地存储，避免开发中反复登录
* 编辑服务器配置或一次性停止所有服务器

Claude 会根据你的项目创建初始服务器配置。如果应用使用自定义的开发命令，请编辑 `.claude/launch.json` 来匹配你的配置。详见[配置预览服务器](#configure-preview-servers)。

要清除已保存的会话数据，在 Settings → Claude Code 中关闭 **Persist preview sessions**。要完全禁用预览，关闭 Settings → Claude Code 中的 **Preview**。

### 通过 diff 视图审查变更

**Claude 修改代码后，diff 视图让你逐文件审查修改。**

当 Claude 修改文件时，会出现一个 diff 统计指示器，显示新增和删除的行数，例如 `+12 -1`。点击该指示器打开 diff 查看器，左侧是文件列表，右侧是每个文件的变更内容。

**评论代码行**：在 diff 中点击任意行打开评论框。输入反馈后按 **Enter** 添加评论。给多行添加评论后，一次性提交所有评论：

* **macOS**：按 **Cmd+Enter**
* **Windows**：按 **Ctrl+Enter**

Claude 会读取你的评论并做出相应修改，新的 diff 会再次呈现供你审查。

### 审查代码质量

**在 diff 视图中**，点击右上角工具栏的 **Review code**，让 Claude 在提交前评估变更。Claude 会检查当前 diff 并直接在 diff 视图中留下评论。你可以回复任何评论或要求 Claude 修改。

审查聚焦于高价值问题：编译错误、明确的逻辑错误、安全漏洞和明显的 bug。不会标记代码风格、格式、已有问题或 linter 能捕获的内容。

### 监控 Pull Request 状态

**PR 创建后**，会话中会出现 CI 状态栏。Claude Code 使用 GitHub CLI 轮询检查结果并展示失败信息。

| 功能 | 说明 |
| --- | --- |
| **Auto-fix** | 启用后，Claude 自动尝试修复失败的 CI 检查：读取失败输出并迭代修复。 |
| **Auto-merge** | 启用后，所有检查通过时 Claude 自动合并 PR。合并方式为 squash。需要在 [GitHub 仓库设置中启用 auto-merge](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-auto-merge-for-pull-requests-in-your-repository)。 |

使用 CI 状态栏中的 **Auto-fix** 和 **Auto-merge** 开关来启用。Claude Code 在 CI 完成时还会发送桌面通知。要在 PR 合并或关闭后自动归档会话，请在 Settings → Claude Code 中开启 [auto-archive](#work-in-parallel-with-sessions)。

<Note>
  PR 监控需要安装并认证 [GitHub CLI (`gh`)](https://cli.github.com/)。如果未安装 `gh`，桌面版会在你首次创建 PR 时提示安装。
</Note>

## 排列工作区

**Code 标签页围绕面板构建**，支持任意布局：聊天、diff、预览、终端、文件、计划、任务和子代理。拖拽面板标题来重新定位，拖拽面板边缘来调整大小。按 **Cmd+\\**（macOS）或 **Ctrl+\\**（Windows）关闭当前聚焦的面板。通过会话工具栏中的 **Views** 菜单打开更多面板。

<Note>
  本节中的面板布局、终端、文件编辑器和视图模式需要 Claude Desktop v1.2581.0 或更高版本。在 macOS 中打开 **Claude → Check for Updates**，在 Windows 中打开 **Help → Check for Updates** 来更新。
</Note>

### 在终端中运行命令

**内置终端让你无需切换应用即可运行命令。** 通过 **Views** 菜单打开，或按 **Ctrl+\`**（macOS/Windows）。终端在会话工作目录下打开，与 Claude 共享相同环境，因此 `npm test` 或 `git status` 等命令看到的文件和 Claude 编辑的一致。点击终端面板标题中的 **+** 可以打开第二个终端标签页，或在聊天中右键点击文件夹选择 **Open in terminal**。终端仅在本地会话中可用。

### 打开和编辑文件

**点击聊天或 diff 查看器中的文件路径**即可在文件面板中打开。HTML、PDF、图片和视频路径会在[预览面板](#preview-your-app)中打开。进行局部编辑后点击 **Save** 保存。如果文件在打开后被磁盘上的其他操作修改，面板会提示你选择覆盖或放弃。点击 **Discard** 撤销编辑，点击面板标题中的路径可复制绝对路径。

文件面板在本地和 SSH 会话中可用。云端会话请让 Claude 来修改。

### 在其他应用中打开文件

**右键点击**聊天、diff 查看器或文件面板中的任何文件路径，打开上下文菜单：

| 选项 | 说明 |
| --- | --- |
| **Attach as context** | 将文件添加到下一条提示的上下文中 |
| **Open in** | 在已安装的编辑器（如 VS Code、Cursor 或 Zed）中打开 |
| **Show in Finder**（macOS）/ **Show in Explorer**（Windows） | 打开所在文件夹 |
| **Copy path** | 复制绝对路径到剪贴板 |

### 切换视图模式

**视图模式控制聊天记录中显示的详细程度。** 通过发送按钮旁的 **Transcript view** 下拉菜单切换，或按 **Ctrl+O**（macOS/Windows）循环切换。

| 模式 | 显示内容 |
| --- | --- |
| **Normal** | 工具调用折叠为摘要，文本回复完整显示 |
| **Verbose** | 显示 Claude 的每个工具调用、文件读取和中间步骤 |
| **Summary** | 仅显示 Claude 的最终回复和所做的修改 |

**使用建议**：调试 Claude 为何采取某个操作时用 Verbose；同时运行多个会话想快速浏览结果时用 Summary。

### 快捷键

按 **Cmd+/**（macOS）或 **Ctrl+/**（Windows）查看 Code 标签页中所有可用快捷键。在 Windows 上，以下快捷键中的 **Cmd** 替换为 **Ctrl**。会话切换、终端开关和视图模式切换在所有平台上都使用 **Ctrl**。

| 快捷键 | 操作 |
| --- | --- |
| `Cmd` `/` | 显示快捷键列表 |
| `Cmd` `N` | 新建会话 |
| `Cmd` `W` | 关闭会话 |
| `Ctrl` `Tab` / `Ctrl` `Shift` `Tab` | 下一个/上一个会话 |
| `Cmd` `Shift` `]` / `Cmd` `Shift` `[` | 下一个/上一个会话 |
| `Esc` | 停止 Claude 的回复 |
| `Cmd` `Shift` `D` | 切换 diff 面板 |
| `Cmd` `Shift` `P` | 切换预览面板 |
| `Cmd` `Shift` `S` | 在预览中选择元素 |
| `Ctrl` `` ` `` | 切换终端面板 |
| `Cmd` `\` | 关闭当前聚焦面板 |
| `Cmd` `;` | 打开侧聊 |
| `Ctrl` `O` | 循环视图模式 |
| `Cmd` `Shift` `M` | 打开权限模式菜单 |
| `Cmd` `Shift` `I` | 打开模型菜单 |
| `Cmd` `Shift` `E` | 打开 effort 菜单 |
| `1`–`9` | 选择已打开菜单中的项目 |

这些快捷键仅适用于 Code 标签页。终端版[交互模式快捷键](https://code.claude.com/docs/en/interactive-mode#keyboard-shortcuts)（如 `Shift+Tab` 循环模式）在桌面版中不适用。

### 查看用量

**点击模型选择器旁的用量环**，查看当前会话的上下文窗口使用情况和本周期的计划用量。上下文用量按会话计算；计划用量在所有 Claude Code 界面间共享。

## 让 Claude 控制你的电脑

**计算机控制让 Claude 像你一样操作桌面**：打开应用、控制屏幕、直接在你的机器上工作。可以让 Claude 在移动模拟器中测试原生应用、操作没有 CLI 的桌面工具，或自动化只能通过 GUI 完成的操作。

<Note>
  计算机控制是 macOS 和 Windows 上的研究预览功能，需要 Pro 或 Max 计划。Team 和 Enterprise 计划暂不可用。Claude 桌面应用必须在运行中。
</Note>

**默认关闭。** 需要先在[设置中启用](#enable-computer-use)，Claude 才能控制屏幕。macOS 上还需要授予辅助功能和屏幕录制权限。

<Warning>
  与[沙箱化的 Bash 工具](https://code.claude.com/docs/en/sandboxing)不同，计算机控制在你的真实桌面上运行，可以访问你批准的任何内容。Claude 会检查每个操作并标记来自屏幕内容的潜在注入攻击，但信任边界不同。请参阅[计算机控制安全指南](https://support.claude.com/en/articles/14128542)了解最佳实践。
</Warning>

### 何时使用计算机控制

**Claude 有多种与应用或服务交互的方式**，计算机控制是最广泛但也最慢的。Claude 会优先使用最精确的工具：

* 如果你有某服务的[连接器](#connect-external-tools)，Claude 使用连接器。
* 如果任务是 shell 命令，Claude 使用 Bash。
* 如果任务是浏览器操作且你配置了 [Claude in Chrome](https://code.claude.com/docs/en/chrome)，Claude 使用浏览器扩展。
* 如果以上都不适用，Claude 使用计算机控制。

[应用级别的访问层级](#app-permissions)强化了这一逻辑：浏览器限制为仅查看，终端和 IDE 限制为仅点击，引导 Claude 即使在计算机控制激活时也优先使用专用工具。屏幕控制保留给其他方式无法触及的场景，如原生应用、硬件控制面板、移动模拟器或没有 API 的专有工具。

### 启用计算机控制

**默认关闭。** 如果你要求 Claude 做需要计算机控制的事而该功能处于关闭状态，Claude 会告诉你可以在设置中启用。

<Steps>
  <Step title="更新桌面应用">
    确保你使用的是最新版 Claude Desktop。在 [claude.com/download](https://claude.com/download) 下载或更新，然后重启应用。
  </Step>

  <Step title="开启开关">
    在桌面应用中，前往 **Settings > General**（Desktop app 下方）。找到 **Computer use** 开关并开启。Windows 上开关立即生效，设置完成。macOS 上请继续下一步。

    如果看不到该开关，请确认你使用的是 macOS 或 Windows 且拥有 Pro 或 Max 计划，然后更新并重启应用。
  </Step>

  <Step title="授予 macOS 权限">
    macOS 上需要授予两项系统权限，开关才能生效：

    * **辅助功能（Accessibility）**：允许 Claude 点击、输入和滚动
    * **屏幕录制（Screen Recording）**：允许 Claude 看到屏幕内容

    设置页面会显示每项权限的当前状态。如果任一权限被拒绝，点击徽标跳转到对应的系统设置面板。
  </Step>
</Steps>

### 应用权限

**首次 Claude 需要使用某个应用时**，会话中会弹出提示。点击 **Allow for this session** 或 **Deny**。许可在当前会话内有效，[Dispatch 生成的会话](#sessions-from-dispatch)中为 30 分钟。

提示还会显示 Claude 对该应用获得的控制级别。这些层级由应用类别决定，不可更改：

| 层级 | Claude 可以做什么 | 适用于 |
| :--- | :--- | :--- |
| View only | 在截图中查看应用 | 浏览器、交易平台 |
| Click only | 点击和滚动，但不能输入或使用快捷键 | 终端、IDE |
| Full control | 点击、输入、拖拽和使用快捷键 | 其他所有应用 |

**权限较广的应用**（如终端、Finder / 文件资源管理器、系统设置）会在提示中显示额外警告，让你知道批准后会授予什么权限。

你可以在 **Settings > General**（Desktop app 下方）配置两个设置：

| 设置 | 说明 |
| --- | --- |
| **Denied apps** | 在此添加应用，无需提示直接拒绝。Claude 仍可能通过允许的应用间接影响被拒绝的应用，但不能直接与其交互。 |
| **Unhide apps when Claude finishes** | Claude 工作时会隐藏其他窗口，确保只与批准的应用交互。Claude 完成后恢复隐藏的窗口（除非关闭此设置）。 |

## 管理会话

**每个会话都是独立的对话**，拥有自己的上下文和变更。你可以并行运行多个会话、发起侧聊、将任务发送到云端，或让 Dispatch 从手机为你创建会话。

### 并行多会话

**点击侧边栏的 + New session**，或按 **Cmd+N**（macOS）/ **Ctrl+N**（Windows），即可并行处理多个任务。按 **Ctrl+Tab** 和 **Ctrl+Shift+Tab** 在侧边栏中循环切换会话。对于 Git 仓库，每个会话通过 [Git worktrees](https://code.claude.com/docs/en/worktrees) 获得项目的独立副本，因此一个会话的修改在提交前不会影响其他会话。

**分屏查看**：按住 **Cmd**（macOS）或 **Ctrl**（Windows）点击侧边栏中的会话，即可将其在第二个面板中打开。分屏激活时，点击侧边栏其他会话会替换当前聚焦的面板。按 **Cmd+\\**（macOS）或 **Ctrl+\\**（Windows）关闭聚焦面板，回到单会话视图。

**Worktree 配置**：默认存储在 `<project-root>/.claude/worktrees/`。可在 Settings → Claude Code 的 "Worktree location" 中更改为自定义目录。还可以设置分支前缀，添加到每个 worktree 分支名前面，方便组织 Claude 创建的分支。要删除 worktree，在侧边栏悬停会话并点击归档图标。要在 PR 合并或关闭后自动归档会话，在 Settings → Claude Code 中开启 **Auto-archive after PR merge or close**。自动归档仅适用于已完成运行的本地会话。

要在新 worktree 中包含 `.env` 等被 gitignore 的文件，请在项目根目录创建 [`.worktreeinclude` 文件](https://code.claude.com/docs/en/worktrees#copy-gitignored-files-into-worktrees)。

<Note>
  会话隔离需要安装 [Git](https://git-scm.com/downloads)。大多数 Mac 自带 Git。在终端运行 `git --version` 检查。Windows 上 Code 标签页必须有 Git：[下载 Git for Windows](https://git-scm.com/downloads/win)，安装后重启应用。遇到 Git 错误时，可以在 [Cowork 标签页](https://claude.com/product/cowork)中让 Claude 帮你排查。
</Note>

**会话管理功能**：使用侧边栏顶部的控件按状态、项目或环境筛选会话，按项目分组会话。点击活跃会话顶部工具栏中的会话标题可重命名。查看上下文用量请参见[查看用量](#check-usage)。上下文满时，Claude 会自动总结对话并继续工作。也可以输入 `/compact` 手动触发总结，释放上下文空间。详见[上下文窗口](https://code.claude.com/docs/en/how-claude-code-works#the-context-window)了解压缩机制。

桌面应用会在 Code 会话完成任务且你未在查看该会话时发送系统通知。

### 在不偏离主线的情况下提出侧聊问题

**侧聊让你利用会话上下文提问，但不会向主对话添加任何内容。** 适合理解某段代码、验证假设或探索想法，而不让会话偏离方向。

按 **Cmd+;**（macOS）或 **Ctrl+;**（Windows）打开侧聊，或在输入框中输入 `/btw`。侧聊可以读取主线程中截至当前的所有内容。完成后关闭侧聊，主会话从中断处继续。侧聊在本地和 SSH 会话中可用。

### 查看后台任务

**任务面板显示当前会话中正在运行的后台工作**：子代理、后台 shell 命令和[动态工作流](https://code.claude.com/docs/en/workflows)。通过 **Views** 菜单打开或拖拽到布局中。

点击任一条目可查看其输出或停止它。要查看其他会话的运行状态，使用[侧边栏](#work-in-parallel-with-sessions)。

### 远程运行长时间任务

**大型重构、测试套件、迁移或其他长时间任务**，启动会话时选择 **Remote** 而非 **Local**。云端会话运行在 Anthropic 的云基础设施上，即使关闭应用或关机也会继续运行。随时回来查看进度或调整方向。也可以从 [claude.ai/code](https://claude.ai/code) 或 Claude iOS 应用监控云端会话。

**多仓库支持**：选择云端环境后，点击仓库标签旁的 **+** 按钮添加更多仓库。每个仓库有独立的分支选择器。适合跨多个代码库的任务，如同时更新共享库及其消费者。

详见 [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web) 了解云端会话的工作方式。

### 在其他界面继续

**Continue in** 菜单（位于会话工具栏右下角的 VS Code 图标处）可以将会话转移到其他界面：

| 目标 | 说明 |
| --- | --- |
| **Claude Code on the Web** | 将本地会话发送到云端继续运行。桌面版推送分支、生成对话摘要，并创建包含完整上下文的新云端会话。然后你可以选择归档或保留本地会话。需要干净的工作树，SSH 会话不支持。 |
| **Your IDE** | 在支持的 IDE 中打开当前工作目录下的项目。 |

### 来自 Dispatch 的会话

**[Dispatch](https://support.claude.com/en/articles/13947068)** 是 [Cowork](https://claude.com/product/cowork#dispatch-and-computer-use) 标签页中的持续对话。你给 Dispatch 发送任务，它决定如何处理。

**任务变成 Code 会话有两种方式**：你直接要求（如"打开一个 Claude Code 会话修复登录 bug"），或 Dispatch 判断这是开发工作自动创建。通常路由到 Code 的任务包括：修复 bug、更新依赖、运行测试、创建 Pull Request。研究、文档编辑和电子表格工作留在 Cowork 中。

无论哪种方式，Code 会话都会出现在 Code 标签页侧边栏中，带有 **Dispatch** 徽标。任务完成或需要你批准时，手机会收到推送通知。

如果你启用了[计算机控制](#let-claude-use-your-computer)，Dispatch 生成的 Code 会话也可以使用。这些会话中的应用许可 30 分钟后过期并重新提示，而非像普通 Code 会话那样持续整个会话。

设置、配对和 Dispatch 相关配置请参见 [Dispatch 帮助文档](https://support.claude.com/en/articles/13947068)。Dispatch 需要 Pro 或 Max 计划，Team 和 Enterprise 计划暂不可用。

**Dispatch 是离开终端后与 Claude 协作的方式之一。** 要比较 Remote Control、Channels、Slack 和定时任务的异同，请参见[平台与集成](https://code.claude.com/docs/en/platforms#work-when-you-are-away-from-your-terminal)。
## 扩展 Claude Code

连接外部服务、添加可复用工作流、自定义 Claude 行为、配置预览服务器。要统一管理连接器、技能和插件，点击侧边栏中的 **Customize**。

### 连接外部工具

**通过连接器快速集成第三方服务。** 在本地和 [SSH](#ssh-sessions) 会话中，点击输入框旁的 **+** 按钮，选择 **Connectors** 即可添加 Google Calendar、Slack、GitHub、Linear、Notion 等集成。连接器可以在会话开始前或进行中添加。云端会话中 **+** 按钮不可用，但 [routines](https://code.claude.com/docs/en/routines) 可在创建时配置连接器。

**管理或断开连接器：** 进入 Settings → Connectors，或从输入框的 Connectors 菜单中选择 **Manage connectors**。

**连接后 Claude 能做什么：** 读取日历、发送消息、创建 Issue、直接与你的工具交互。你可以询问 Claude 当前会话配置了哪些连接器。

**连接器本质上是带图形化设置界面的 [MCP 服务器](https://code.claude.com/docs/en/mcp)。** 适合快速接入已支持的服务。对于未列出的集成，可通过[配置文件](https://code.claude.com/docs/en/mcp#installing-mcp-servers)手动添加 MCP 服务器。你也可以[创建自定义连接器](https://support.claude.com/en/articles/11175166-getting-started-with-custom-connectors-using-remote-mcp)。

### 使用技能

**技能扩展 Claude 的能力范围。** [技能](https://code.claude.com/docs/en/skills)会在相关时自动加载，也可以直接调用：在输入框中输入 `/`，或点击 **+** 按钮选择 **Slash commands** 浏览可用技能。包括[内置命令](https://code.claude.com/docs/en/commands)、[自定义技能](https://code.claude.com/docs/en/skills#create-your-first-skill)、代码库中的项目技能，以及[已安装插件](https://code.claude.com/docs/en/plugins)提供的技能。选中后会高亮显示在输入框中，在其后输入任务描述即可发送。

### 安装插件

**插件是可复用的扩展包，能为 Claude Code 添加技能、Agent、Hook、MCP 服务器和 LSP 配置。** [插件](https://code.claude.com/docs/en/plugins)可直接在桌面应用中安装，无需使用终端。

在本地和 [SSH](#ssh-sessions) 会话中，点击输入框旁的 **+** 按钮选择 **Plugins**，查看已安装的插件及其技能。选择 **Add plugin** 打开插件浏览器，显示来自已配置[市场](https://code.claude.com/docs/en/plugin-marketplaces)（包括 Anthropic 官方市场）的可用插件。选择 **Manage plugins** 可启用、禁用或卸载插件。

**插件作用域：** 可限定为用户账号级别、特定项目级别或仅本地。如果组织集中管理插件，这些插件在桌面会话中的使用方式与 CLI 相同。云端会话不支持插件。完整的插件参考（包括创建自定义插件），请参阅[插件文档](https://code.claude.com/docs/en/plugins)。

### 配置预览服务器

**Claude 自动检测开发服务器配置并存储在 `.claude/launch.json` 中。** 该文件位于启动会话时所选文件夹的根目录。预览以该文件夹为工作目录，因此如果选择了父文件夹，子文件夹中的开发服务器不会被自动检测。要使用子文件夹的服务器，可以直接在该子文件夹中启动会话，或手动添加配置。

**自定义服务器启动方式（如用 `yarn dev` 替代 `npm run dev` 或更改端口）：** 直接编辑文件，或在 Preview 下拉菜单中点击 **Edit configuration** 用代码编辑器打开。该文件支持带注释的 JSON。

```json theme={null}
{
  "version": "0.0.1",
  "configurations": [
    {
      "name": "my-app",
      "runtimeExecutable": "npm",
      "runtimeArgs": ["run", "dev"],
      "port": 3000
    }
  ]
}
```

你可以定义多个配置来运行同一项目中的不同服务器，例如前端和 API。参见下方[示例](#examples)。

#### 自动验证变更

**启用 `autoVerify` 后，Claude 会在编辑文件后自动验证代码变更。** 它会截屏、检查错误，并确认变更正常工作后再完成响应。

自动验证默认开启。可通过在 `.claude/launch.json` 中添加 `"autoVerify": false` 来为单个项目禁用，或从 **Preview** 下拉菜单切换。

```json theme={null}
{
  "version": "0.0.1",
  "autoVerify": false,
  "configurations": [...]
}
```

禁用后，预览工具仍然可用，你可以随时要求 Claude 验证。自动验证只是让每次编辑后的验证变为自动执行。

#### 配置字段

`configurations` 数组中每个条目支持以下字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `name` | string | 服务器的唯一标识符 |
| `runtimeExecutable` | string | 要运行的命令，如 `npm`、`yarn` 或 `node` |
| `runtimeArgs` | string[] | 传递给 `runtimeExecutable` 的参数，如 `["run", "dev"]` |
| `port` | number | 服务器监听的端口，默认为 3000 |
| `cwd` | string | 相对于项目根目录的工作目录。默认为项目根目录。使用 `${workspaceFolder}` 显式引用项目根目录 |
| `env` | object | 附加环境变量（键值对），如 `{ "NODE_ENV": "development" }`。不要在此存放敏感信息（此文件会提交到仓库）。要向开发服务器传递密钥，请在[本地环境编辑器](#local-sessions)中设置 |
| `autoPort` | boolean | 端口冲突时的处理方式。详见下文 |
| `program` | string | 用 `node` 运行的脚本。参见 [`program` 与 `runtimeExecutable` 的选择](#when-to-use-program-vs-runtimeexecutable) |
| `args` | string[] | 传递给 `program` 的参数。仅在设置了 `program` 时使用 |

<a id="when-to-use-program-vs-runtimeexecutable" />

##### `program` 与 `runtimeExecutable` 的选择

**通过包管理器启动开发服务器用 `runtimeExecutable` + `runtimeArgs`。** 例如 `"runtimeExecutable": "npm"` 配合 `"runtimeArgs": ["run", "dev"]` 相当于运行 `npm run dev`。

**直接用 `node` 运行独立脚本用 `program`。** 例如 `"program": "server.js"` 相当于运行 `node server.js`。通过 `args` 传递额外参数。

#### 端口冲突

`autoPort` 字段控制首选端口被占用时的行为：

* **`true`**：Claude 自动找到并使用空闲端口。适用于大多数开发服务器。
* **`false`**：Claude 报错并停止。适用于服务器必须使用特定端口的场景，如 OAuth 回调或 CORS 白名单。
* **未设置（默认）**：Claude 会询问服务器是否必须使用该端口，然后保存你的回答。

当 Claude 选择不同端口时，会通过 `PORT` 环境变量将分配的端口传递给服务器。

#### 示例

以下配置展示了不同项目类型的常见设置：

<Tabs>
  <Tab title="Next.js">
    此配置使用 Yarn 在端口 3000 运行 Next.js 应用：

    ```json theme={null}
    {
      "version": "0.0.1",
      "configurations": [
        {
          "name": "web",
          "runtimeExecutable": "yarn",
          "runtimeArgs": ["dev"],
          "port": 3000
        }
      ]
    }
    ```
  </Tab>

  <Tab title="Multiple servers">
    对于包含前端和 API 服务器的 monorepo，定义多个配置。前端使用 `autoPort: true`，在 3000 端口被占用时自动选择空闲端口；API 服务器则严格要求端口 8080：

    ```json theme={null}
    {
      "version": "0.0.1",
      "configurations": [
        {
          "name": "frontend",
          "runtimeExecutable": "npm",
          "runtimeArgs": ["run", "dev"],
          "cwd": "apps/web",
          "port": 3000,
          "autoPort": true
        },
        {
          "name": "api",
          "runtimeExecutable": "npm",
          "runtimeArgs": ["run", "start"],
          "cwd": "server",
          "port": 8080,
          "env": { "NODE_ENV": "development" },
          "autoPort": false
        }
      ]
    }
    ```
  </Tab>

  <Tab title="Node.js script">
    要直接运行 Node.js 脚本而非通过包管理器命令，使用 `program` 字段：

    ```json theme={null}
    {
      "version": "0.0.1",
      "configurations": [
        {
          "name": "server",
          "program": "server.js",
          "args": ["--verbose"],
          "port": 4000
        }
      ]
    }
    ```
  </Tab>
</Tabs>

## 环境配置

[启动会话](#start-a-session)时选择的环境决定了 Claude 在哪里执行以及如何连接：

* **本地（Local）**：在你的机器上运行，直接访问本地文件
* **远程（Remote）**：在 Anthropic 的云基础设施上运行。关闭应用后会话仍继续执行。
* **SSH**：在你通过 SSH 连接的远程机器上运行，如自有服务器、云 VM 或开发容器

### 本地会话

**桌面应用不一定会继承完整的 Shell 环境。** 在 macOS 上，从 Dock 或 Finder 启动应用时，它会读取 Shell 配置文件（如 `~/.zshrc` 或 `~/.bashrc`）以提取 `PATH` 和一组固定的 Claude Code 变量，但你在这些文件中 export 的其他变量不会被加载。在 Windows 上，应用继承用户和系统环境变量，但不读取 PowerShell 配置文件。

**设置本地会话和开发服务器的环境变量（跨平台）：** 打开输入框中的环境下拉菜单，悬停在 **Local** 上，点击齿轮图标打开本地环境编辑器。在此保存的变量会加密存储在你的机器上，并应用于每个本地会话和预览服务器。你也可以将变量添加到 `~/.claude/settings.json` 的 `env` 键中，但这些变量只能到达 Claude 会话，不会传递给开发服务器。完整的支持变量列表请参阅[环境变量](https://code.claude.com/docs/en/env-vars)。

**[扩展思考](https://code.claude.com/docs/en/model-config#extended-thinking)默认开启，** 能提升复杂推理任务的表现，但会消耗更多 token。要禁用思考，在本地环境编辑器中将 `MAX_THINKING_TOKENS` 设为 `0`；这对 Fable 5 无效（它始终使用扩展思考）。在[第三方提供商](https://code.claude.com/docs/en/third-party-integrations)上，设为 `0` 会省略 `thinking` 参数，但自适应推理模型可能仍会思考。在支持[自适应推理](https://code.claude.com/docs/en/model-config#adjust-effort-level)的模型上，其他 `MAX_THINKING_TOKENS` 值会被忽略，因为自适应推理会自行控制思考深度。在 Opus 4.6 和 Sonnet 4.6 上，将 `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING` 设为 `1` 可使用固定思考预算；Opus 4.7 及更高版本始终使用自适应推理，没有固定预算模式。

### 云端会话

**云端会话在后台持续运行，即使关闭应用也不中断。** 用量计入你的[订阅计划额度](https://code.claude.com/docs/en/costs)，不额外收取计算费用。

你可以创建自定义云端环境，配置不同的网络访问级别和环境变量。启动云端会话时选择环境下拉菜单，选择 **Add environment**。详见[云端环境](https://code.claude.com/docs/en/claude-code-on-the-web#the-cloud-environment)中的网络访问和环境变量配置说明。

### SSH 会话

**SSH 会话让你在远程机器上运行 Claude Code，同时使用桌面应用作为界面。** 适用于代码库位于云 VM、开发容器或具有特定硬件/依赖的服务器上的场景。

**添加 SSH 连接：** 在启动会话前点击环境下拉菜单，选择 **+ Add SSH connection**。对话框要求填写：

* **Name**：此连接的友好名称
* **SSH Host**：`user@hostname` 或 `~/.ssh/config` 中定义的主机名
* **SSH Port**：留空默认为 22，或使用 SSH 配置中的端口
* **Identity File**：私钥路径，如 `~/.ssh/id_rsa`。留空则使用默认密钥或 SSH 配置

添加后，连接会出现在环境下拉菜单中。选择它即可在该机器上启动会话。Claude 在远程机器上运行，可访问其文件和工具。

**远程机器必须运行 Linux 或 macOS。** 桌面应用会在首次连接时自动在远程机器上安装 Claude Code。连接后，SSH 会话支持权限模式、连接器、插件和 MCP 服务器。

#### 为团队预配置 SSH 连接

**管理员可通过托管配置文件向团队成员分发 SSH 连接。** 在[托管设置](https://code.claude.com/docs/en/settings#settings-precedence)文件中添加 `sshConfigs`，定义的连接会自动出现在每个用户的环境下拉菜单中，标记为"managed"，用户可以选择但不能编辑或删除。

以下示例预配置了一个连接，打开后进入远程主机的 `~/projects` 目录：

```json theme={null}
{
  "sshConfigs": [
    {
      "id": "shared-dev-vm",
      "name": "Shared Dev VM",
      "sshHost": "user@dev.example.com",
      "sshPort": 22,
      "sshIdentityFile": "~/.ssh/id_ed25519",
      "startDirectory": "~/projects"
    }
  ]
}
```

每个条目必须包含 `id`、`name` 和 `sshHost`。`sshPort`、`sshIdentityFile` 和 `startDirectory` 为可选字段。用户也可以在自己的 `~/.claude/settings.json` 中添加 `sshConfigs`（通过对话框添加的连接就存储在此）。

#### 限制用户可连接的 SSH 主机

**管理员可通过 `sshHostAllowlist` 将桌面应用的 SSH 会话限制在已批准的主机范围内。** 在[托管设置](https://code.claude.com/docs/en/settings#settings-precedence)文件中添加此配置。设置后，用户只能连接到解析后主机名匹配某个模式的主机。设为空数组可完全禁用 SSH 会话。

以下示例允许连接 `devboxes.example.com` 下的所有主机以及一台指定的堡垒机：

```json theme={null}
{
  "sshHostAllowlist": ["*.devboxes.example.com", "bastion.example.com"]
}
```

**匹配规则：** 模式不区分大小写。`*` 匹配任何主机，`*.example.com` 匹配 `example.com` 及其所有子域名，其他为精确匹配。检查针对的是经 `~/.ssh/config` 解析后的主机名（通过 `ssh -G`），因此 `Host` 别名和 `ProxyCommand`/`ProxyJump` 条目只要解析后的 `HostName` 匹配即可。

**重要限制：** `sshHostAllowlist` 仅从托管设置读取；用户或项目设置中的值会被忽略。仅 Claude Desktop 应用遵循此设置；Claude Code CLI 和 IDE 扩展不读取它，它也不限制通过 Bash 工具运行的 `ssh` 命令。它控制的是桌面应用连接的目标主机，而非网络出口。如果需要硬边界，请配合组织的网络或零信任策略使用。

## 企业配置

Team 或 Enterprise 计划的组织可通过管理控制台、托管设置文件和设备管理策略来管理桌面应用行为。

### 管理控制台

以下设置通过[管理设置控制台](https://claude.ai/admin-settings/claude-code)配置：

* **Code in the desktop**：控制组织中的用户是否可以在桌面应用中使用 Claude Code
* **Code in the web**：为组织启用或禁用 [Web 会话](https://code.claude.com/docs/en/claude-code-on-the-web)
* **Remote Control**：为组织启用或禁用[远程控制](https://code.claude.com/docs/en/remote-control)
* **Disable Bypass permissions mode**：禁止组织中的用户启用绕过权限模式

### 托管设置

**托管设置覆盖项目和用户设置，应用于桌面应用中的 Claude Code 会话。** 你可以在组织的[托管设置](https://code.claude.com/docs/en/settings#settings-precedence)文件中设置这些键，或通过管理控制台远程推送。

| 键 | 说明 |
| --- | --- |
| `permissions.disableBypassPermissionsMode` | 设为 `"disable"` 以禁止用户启用绕过权限模式 |
| `disableAutoMode` | 设为 `"disable"` 以禁止用户启用 [Auto](https://code.claude.com/docs/en/permission-modes#eliminate-prompts-with-auto-mode) 模式。从模式选择器中移除 Auto。也可放在 `permissions` 下 |
| `autoMode` | 自定义组织范围内 Auto 模式分类器信任和阻止的内容。详见[配置 Auto 模式](https://code.claude.com/docs/en/auto-mode-config) |
| `sshConfigs` | 预配置出现在环境下拉菜单中的 [SSH 连接](#pre-configure-ssh-connections-for-your-team)。用户不能编辑或删除托管连接 |
| `sshHostAllowlist` | 将 [SSH 会话](#restrict-which-ssh-hosts-users-can-connect-to)限制在解析后主机名匹配这些模式的主机范围内。空数组禁用 SSH 会话。仅从托管设置读取 |
| `managedMcpServers` | 向第三方部署中的所有用户推送 MCP 服务器配置。每个条目指定传输协议（`"http"`、`"sse"` 或 `"stdio"`）、连接详情，以及可选的 `toolPolicy` 映射（限制用户可调用该服务器中的哪些工具）。仅适用于第三方 (3P) Desktop 部署。通过托管设置文件或 MDM 分发此键（第三方部署不接收管理控制台设置） |

**哪些托管设置会到达桌面会话取决于会话运行的位置。** 模型限制如 [`availableModels`](https://code.claude.com/docs/en/model-config#restrict-model-selection) 在桌面 Claude Code 会话中的执行方式与终端 CLI 相同；详见[覆盖范围](https://code.claude.com/docs/en/model-config#surface-coverage)。

* **本机上的本地会话**：部署到磁盘的托管设置文件生效。通过管理控制台远程推送的托管设置也能到达这些会话（在 Anthropic API 上，当会话使用组织登录或直接配置的 API 密钥进行身份验证时），遵循与终端 CLI 相同的[设置优先级](https://code.claude.com/docs/en/settings#settings-precedence)。
* **[云端会话](#cloud-sessions)**：在 Anthropic 托管的 VM 上运行，仅接收[服务器托管设置](https://code.claude.com/docs/en/server-managed-settings)。
* **[SSH 会话](#ssh-sessions)**：会话从远程主机读取托管设置文件。桌面应用本身在创建连接时从本机的托管设置中读取 `sshConfigs` 和 `sshHostAllowlist`。

**设置生效说明：** `permissions.disableBypassPermissionsMode` 和 `disableAutoMode` 也可在用户和项目设置中使用，但放在托管设置中可防止用户覆盖。`autoMode` 从用户设置、`.claude/settings.local.json` 和托管设置中读取，但不从已提交的 `.claude/settings.json` 中读取：克隆的仓库不能注入自己的分类器规则。完整的仅托管设置列表（包括 `allowManagedPermissionRulesOnly` 和 `allowManagedHooksOnly`），请参阅[仅托管设置](https://code.claude.com/docs/en/permissions#managed-only-settings)。

### 设备管理策略

**IT 团队可通过 macOS 上的 MDM 或 Windows 上的组策略管理桌面应用。** 可用策略包括启用或禁用 Claude Code 功能、控制自动更新、设置自定义部署 URL。

* **macOS**：通过 `com.anthropic.claudefordesktop` 偏好设置域配置，使用 Jamf 或 Kandji 等工具
* **Windows**：通过注册表 `SOFTWARE\Policies\Claude` 配置

### 身份认证与 SSO

Enterprise 组织可要求所有用户使用 SSO。详见[身份认证](https://code.claude.com/docs/en/authentication)了解计划级别详情，以及[设置 SSO](https://support.claude.com/en/articles/13132885-setting-up-single-sign-on-sso) 了解 SAML 和 OIDC 配置。

### 数据处理

**Claude Code 在本地会话中于你的机器上处理代码，在云端会话中于 Anthropic 的云基础设施上处理。** 对话和代码上下文会发送到 Anthropic 的 API 进行处理。详见[数据处理](https://code.claude.com/docs/en/data-usage)了解数据保留、隐私和合规信息。

### 部署

桌面应用可通过企业部署工具分发：

* **macOS**：通过 MDM（如 Jamf 或 Kandji）使用 `.dmg` 安装包分发
* **Windows**：通过 MSIX 包或 `.exe` 安装程序部署。详见[部署 Claude Desktop for Windows](https://support.claude.com/en/articles/12622703-deploy-claude-desktop-for-windows) 了解企业部署选项（包括静默安装）

网络配置（如代理设置、防火墙白名单和 LLM 网关），请参阅[网络配置](https://code.claude.com/docs/en/network-config)。

完整的企业配置参考，请参阅[企业配置指南](https://support.claude.com/en/articles/12622667-enterprise-configuration)。

## 从 CLI 迁移？

**如果你已经在使用 Claude Code CLI，桌面应用运行的是同一底层引擎，只是加了图形界面。** 可以在同一台机器上、甚至同一个项目上同时运行两者。各自维护独立的会话历史，但通过 CLAUDE.md 文件共享配置和项目记忆。

**将 CLI 会话移入桌面应用：** 在终端中运行 `/desktop`。Claude 会保存你的会话并在桌面应用中打开，然后退出 CLI。此命令在已登录 Claude 订阅的 macOS 和 Windows 上可用。API 密钥认证或 Bedrock、Vertex、Foundry 上不可用。

<Tip>
  何时用桌面应用 vs CLI：当你想在一个窗口中管理多个并行会话、并排排列面板或可视化审查变更时，使用桌面应用。当你需要脚本化、自动化或偏好终端工作流时，使用 CLI。
</Tip>

### CLI 参数对照表

下表展示了常用 CLI 参数在桌面应用中的对应操作。未列出的参数没有桌面端对应，因为它们是为脚本化或自动化设计的。

| CLI | 桌面端对应 |
| --- | --- |
| `--model sonnet` | 发送按钮旁的模型下拉菜单 |
| `--resume`, `--continue` | 点击侧边栏中的会话 |
| `--permission-mode` | 发送按钮旁的模式选择器 |
| `--dangerously-skip-permissions` | 绕过权限模式。在 Settings → Claude Code → "Allow bypass permissions mode" 中启用。企业管理员可禁用此设置 |
| `--add-dir` | 在云端会话中使用 **+** 按钮添加多个仓库 |
| `--allowedTools`, `--disallowedTools` | 无单次会话对应。[设置文件](https://code.claude.com/docs/en/settings)中的权限规则仍然生效 |
| `--verbose` | Transcript 视图下拉菜单中的[详细视图模式](#switch-view-modes) |
| `--print`, `--output-format` | 不可用。桌面应用仅支持交互模式 |
| `ANTHROPIC_MODEL` 环境变量 | 发送按钮旁的模型下拉菜单 |
| `MAX_THINKING_TOKENS` 环境变量 | 在本地环境编辑器中设置。详见[环境配置](#environment-configuration) |

### 共享配置

**桌面应用和 CLI 读取相同的配置文件，因此你的设置可以无缝沿用：**

* **[CLAUDE.md](https://code.claude.com/docs/en/memory)** 和 `CLAUDE.local.md` 文件在项目中对两者都生效
* **[MCP 服务器](https://code.claude.com/docs/en/mcp)** 在 `~/.claude.json` 或 `.mcp.json` 中的配置对两者都生效
* **[Hook](https://code.claude.com/docs/en/hooks)** 和 **[技能](https://code.claude.com/docs/en/skills)** 在设置中定义后对两者都生效
* **[设置](https://code.claude.com/docs/en/settings)** 在 `~/.claude.json` 和 `~/.claude/settings.json` 中共享。`settings.json` 中的权限规则、允许的工具和其他设置应用于桌面会话
* **模型**：两者可用的[模型](https://code.claude.com/docs/en/model-config#available-models)相同。在桌面应用中，从发送按钮旁的下拉菜单选择模型。可以在会话中途从同一下拉菜单切换模型

<Note>
  **来自 Claude Desktop 聊天应用的 MCP 服务器**：桌面应用会将 `claude_desktop_config.json` 中的 MCP 服务器加载到 Code 标签页会话中，与 `~/.claude.json` 和 `.mcp.json` 中的服务器并存。在 `claude_desktop_config.json` 中定义的服务器在桌面聊天界面和 Code 标签页中都可用。

  独立 CLI 不读取 `claude_desktop_config.json`。在 macOS 和 WSL 上，运行 `claude mcp add-from-claude-desktop` 可将这些服务器复制到 `~/.claude.json` 中。详见[从 Claude Desktop 导入 MCP 服务器](https://code.claude.com/docs/en/mcp#import-mcp-servers-from-claude-desktop)了解导入流程和作用域选项。
</Note>

### 功能对比

下表对比了 CLI 和桌面应用的核心功能。完整的 CLI 参数列表请参阅 [CLI 参考](https://code.claude.com/docs/en/cli-reference)。

| 功能 | CLI | 桌面应用 |
| --- | --- | --- |
| 权限模式 | 所有模式（包括 `dontAsk`） | Ask permissions、Auto accept edits、Plan mode、Auto 以及通过 Settings 启用的 Bypass permissions |
| `--dangerously-skip-permissions` | CLI 参数 | 绕过权限模式。在 Settings → Claude Code → "Allow bypass permissions mode" 中启用 |
| [第三方提供商](https://code.claude.com/docs/en/third-party-integrations) | Bedrock、Vertex AI、Foundry | 默认连接 Anthropic API。企业部署可配置 Vertex AI 和网关提供商。详见[企业配置指南](https://support.claude.com/en/articles/12622667-enterprise-configuration)。要在 Code 标签页使用 Bedrock、Vertex AI、Foundry 或自托管 LLM 网关，详见 [Cowork on 3P 研究预览](https://claude.com/docs/cowork/3p/overview) |
| [MCP 服务器](https://code.claude.com/docs/en/mcp) | 在设置文件中配置 | 本地和 SSH 会话使用 Connectors UI，或使用设置文件 |
| [插件](https://code.claude.com/docs/en/plugins) | `/plugin` 命令 | 插件管理器 UI |
| @mention 文件 | 文本方式 | 带自动补全；仅限本地和 SSH 会话 |
| 文件附件 | 不可用 | 图片、PDF |
| 会话隔离 | [`--worktree`](https://code.claude.com/docs/en/cli-reference) 参数 | 自动 worktree |
| 多会话 | 多个终端 | 侧边栏标签页 |
| 定期任务 | Cron 任务、CI 流水线 | [定时任务](https://code.claude.com/docs/en/desktop-scheduled-tasks) |
| 计算机使用 | 在 macOS 上[通过 `/mcp` 启用](https://code.claude.com/docs/en/computer-use) | macOS 和 Windows 上的[应用和屏幕控制](#let-claude-use-your-computer) |
| Dispatch 集成 | 不可用 | 侧边栏中的 [Dispatch 会话](#sessions-from-dispatch) |
| 脚本化和自动化 | [`--print`](https://code.claude.com/docs/en/cli-reference)、[Agent SDK](https://code.claude.com/docs/en/headless) | 不可用 |

### 桌面应用中不可用的功能

以下功能仅在 CLI 或 VS Code 扩展中可用（除非特别说明）：

* **第三方提供商**：桌面应用默认连接 Anthropic API。企业部署可通过[托管设置](https://support.claude.com/en/articles/12622667-enterprise-configuration)配置 Vertex AI 和网关提供商。CLI 中使用 Bedrock 或 Foundry 请参阅[快速开始](https://code.claude.com/docs/en/quickstart)。特殊情况：[Cowork on 3P 研究预览](https://claude.com/docs/cowork/3p/overview)可在 Code 标签页上运行 Bedrock、Vertex AI、Foundry 或自托管 LLM 网关。
* **Linux**：桌面应用仅支持 macOS 和 Windows。Linux 上请使用 [CLI](https://code.claude.com/docs/en/quickstart)。
* **内联代码建议**：桌面应用不提供自动补全式建议。它通过对话提示和显式代码变更工作。
* **Agent 团队**：相互通信的并行 Claude Code 会话仅在 [CLI](https://code.claude.com/docs/en/agent-teams) 中可用，桌面应用不支持。单会话内的多 Agent 协作可使用[动态工作流](https://code.claude.com/docs/en/workflows)，它在桌面应用中可运行。
* **终端交互命令**：在终端中打开交互面板的内置命令（如 `/permissions`、`/config`、`/agents`、`/doctor`）在 Code 标签页中不可用，会回复 `isn't available in this environment`。请直接编辑[设置文件](https://code.claude.com/docs/en/settings)来管理权限规则和配置，或从独立 CLI 中运行这些命令。

## 故障排除

以下章节涵盖桌面应用特有的问题。对于聊天中出现的运行时 API 错误（如 `API Error: 500`、`529 Overloaded`、`429` 或 `Prompt is too long`），请参阅[错误参考](https://code.claude.com/docs/en/errors)。这些错误及其修复方法在 CLI、桌面应用和 Web 端完全相同。

### 检查版本

查看桌面应用版本：

* **macOS**：点击菜单栏中的 **Claude**，然后选择 **About Claude**
* **Windows**：点击 **Help**，然后选择 **About**

点击版本号可将其复制到剪贴板。

### Code 标签页中的 403 或身份认证错误

**如果你看到 `Error 403: Forbidden` 或其他身份认证失败：**

1. 从应用菜单登出再重新登录。这是最常见的修复方法。
2. 确认你有活跃的付费订阅：Pro、Max、Team 或 Enterprise。
3. 如果 CLI 正常但桌面应用不行，完全退出桌面应用（不只是关闭窗口），然后重新打开并登录。
4. 检查网络连接和代理设置。

### 启动时白屏或卡住

**如果应用打开但显示空白或无响应的屏幕：**

1. 重启应用。
2. 检查是否有待处理的更新。应用在启动时自动更新。
3. 在 Windows 上，检查事件查看器中 **Windows Logs → Application** 下的崩溃日志。

### "Failed to load session"

**如果你看到 `Failed to load session`，** 可能是所选文件夹不再存在、Git 仓库需要未安装的 Git LFS、或文件权限阻止了访问。尝试选择其他文件夹或重启应用。

### 会话找不到已安装的工具

**如果 Claude 找不到 `npm`、`node` 或其他 CLI 命令：** 确认这些工具在常规终端中可正常使用，检查 Shell 配置文件是否正确设置了 PATH，然后重启桌面应用以重新加载环境变量。

### Git 和 Git LFS 错误

**在 Windows 上，Code 标签页启动本地会话需要 Git。** 如果看到"Git is required"，请安装 [Git for Windows](https://git-scm.com/downloads/win) 并重启应用。

如果看到"Git LFS is required by this repository but is not installed"，请从 [git-lfs.com](https://git-lfs.com/) 安装 Git LFS，运行 `git lfs install`，然后重启应用。

### Windows 上 MCP 服务器不工作

**如果 MCP 服务器开关无响应或服务器连接失败：** 检查服务器是否在设置中正确配置，重启应用，在任务管理器中确认服务器进程正在运行，并查看服务器日志中的连接错误。

### 应用无法退出

* **macOS**：按 Cmd+Q。如果应用无响应，使用 Cmd+Option+Esc 强制退出，选择 Claude 并点击 Force Quit。
* **Windows**：使用 Ctrl+Shift+Esc 打开任务管理器，结束 Claude 进程。

### Windows 特有问题

* **安装后 PATH 未更新**：打开新的终端窗口。PATH 更新仅对新终端会话生效。
* **并发安装错误**：如果看到关于另一个安装正在进行的错误，但实际并没有，尝试以管理员身份运行安装程序。

### 云端会话中"Branch doesn't exist yet"

**云端会话可能创建了本地机器上不存在的分支。** 点击会话工具栏中的分支名复制它，然后在本地拉取：

```bash theme={null}
git fetch origin <branch-name>
git checkout <branch-name>
```

### 仍然遇到问题？

* 在桌面应用中打开 Help → Get Support，或直接访问 [Claude 支持中心](https://support.claude.com/)
* 对于在独立 `claude` CLI 中也能复现的问题，在 [GitHub Issues](https://github.com/anthropics/claude-code/issues) 上搜索或提交 Bug

**报告问题时请附上：** 桌面应用版本、操作系统、确切的错误信息和相关日志。macOS 上检查 Console.app，Windows 上检查事件查看器 → Windows Logs → Application。
