---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】深度链接
description: 深度链接是 claude-cli:// URL，用于从链接直接打开 Claude Code 终端会话。可嵌入运维手册、告警面板和文档中，一键打开正确的仓库和预填充 prompt。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/deep-links.md
  - en-source/deep-links.md
---

# 从链接启动会话

> 从 URL 打开 Claude Code 终端会话。将 `claude-cli://` 链接嵌入运维手册、告警和面板中，一键打开 Claude Code 并带上正确的仓库和 prompt。

**深度链接是一个 `claude-cli://` URL，在新终端窗口中打开 Claude Code。** URL 可以携带工作目录和预填充的 prompt。

这让你可以分享一键启动任务的起点：任何安装了 Claude Code 的人点击链接就会看到会话打开，prompt 已经输入好。prompt 会被填充但不会自动发送，直到你按 Enter。

因为深度链接是 URL，你可以放在任何能放链接的地方：

- 事件运维手册中打开受影响服务仓库的诊断 prompt
- 监控告警或面板中链接到特定指标的调查 prompt
- README 或 wiki 页面中打开项目的引导 prompt
- CI 失败通知中预填充失败 job 名称

本页介绍如何[构建链接](#构建链接)、[嵌入到运维手册或从 shell 触发](#示例)，以及在各平台上[管理或禁用处理器注册](#注册和支持的平台)。

> [!NOTE]
> 深度链接需要 Claude Code v2.1.91 及以上版本。

## 工作原理

**`claude-cli://` 前缀是一个自定义 URL scheme，Claude Code 向操作系统注册。** 类似于 `mailto:` 链接打开邮件客户端。链接可以存在于网页、wiki、Slack 消息或任何渲染链接的应用中。当你点击时：

1. 浏览器或应用将 URL 传给操作系统
2. 操作系统识别 `claude-cli://` 前缀并启动 Claude Code
3. 新终端窗口打开，Claude Code 运行在链接指定的目录中，链接的 prompt 文本已在输入框中
4. 你阅读 prompt，需要的话编辑它，然后按 Enter 发送

链接本身可以托管在任何地方，但会话始终在你点击的电脑上本地打开。

> [!NOTE]
> 显示链接的平台必须允许自定义 URL scheme。GitHub 渲染的 Markdown 允许 `http` 和 `https` 但会剥离 `claude-cli://` 等 scheme。参见[故障排除](#链接显示为纯文本而非可点击)了解解决方案。

### 启动的会话显示什么

**深度链接本身不执行任何操作。** 链接只选择目录和填充 prompt 框。如果你从不信任的页面点击链接，prompt 仍然是惰性的：在你阅读填充内容并按 Enter 之前，不会有任何内容到达模型。

会话打开时，输入框下方显示警告行 `Prompt from an external link`，在你发送或清除 prompt 之前一直可见。超过 1,000 字符的 prompt 会包含字符数并提示你在按 Enter 前滚动查看全文。

## 构建链接

**每个深度链接以 `claude-cli://open` 开头**，这是处理器接受的唯一路径，后跟可选查询参数。最简形式在 home 目录打开 Claude Code 并带空 prompt：

```text
claude-cli://open
```

添加参数控制会话启动位置和 prompt 框内容：

| 参数 | 说明 |
|------|------|
| `q` | 预填充到 prompt 框的文本。需要 [URL 编码](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/encodeURIComponent)。用 `%0A` 表示多行 prompt 中的换行。最大 5,000 字符 |
| `cwd` | 用作工作目录的绝对路径。拒绝网络/UNC 路径和包含不可见/双向控制字符的路径 |
| `repo` | GitHub `owner/name` slug。Claude Code 解析为之前见过的本地克隆并在那里启动。如果没有匹配的克隆，会话在 home 目录打开 |

`cwd` 和 `repo` 是[设置工作目录的两种方式](#选择-cwd-还是-repo)。如果同时传递两者，`cwd` 优先，`repo` 被忽略。

示例——指向名为 `acme/payments` 的仓库并带两行诊断 prompt：

```text
claude-cli://open?repo=acme/payments&q=Investigate%20the%20failed%20deploy%20of%20payments-api.%0ACheck%20recent%20commits%20to%20main%20and%20the%20last%20successful%20build.
```

点击后在 `acme/payments` 的本地克隆中打开新终端窗口，prompt 框中填入：

```text
Investigate the failed deploy of payments-api.
Check recent commits to main and the last successful build.
```

### 选择 cwd 还是 repo

**用 `cwd`：** 当所有点击链接的人项目在相同绝对路径时，如标准化的 devcontainer 或 VM 镜像。

**用 `repo`：** 当链接被共享且每人克隆到不同位置时。Claude Code 按以下方式解析 slug 到本地路径：

- 每次在 Git 仓库中运行 `claude` 时，该目录路径会被记录并关联到仓库的 GitHub `owner/name` slug
- 深度链接到达时，`repo` 打开你最近使用的匹配路径
- 查找只能找到你已经运行过 Claude Code 至少一次的路径
- 链接不会改变检出的分支

## 示例

### 在运维手册中嵌入链接

运维手册中的深度链接给分诊人员一键在正确仓库中开始调查的方式。

```markdown
## High 5xx rate on web-gateway

1. Acknowledge the page in PagerDuty.
2. [Open Claude Code in the gateway repo](claude-cli://open?repo=acme/web-gateway&q=5xx%20rate%20is%20elevated%20on%20web-gateway.%20Check%20recent%20deploys%2C%20error%20logs%20from%20the%20last%2030%20minutes%2C%20and%20open%20incidents%20in%20Linear.)
3. Post initial findings in #incident.
```

### 从 shell 打开链接

也可以从 shell 脚本、别名或自动化中打开深度链接。

**macOS：**

```bash
open "claude-cli://open?repo=acme/payments&q=review%20open%20PRs"
```

**Linux：**

```bash
xdg-open "claude-cli://open?repo=acme/payments&q=review%20open%20PRs"
```

**Windows PowerShell：**

```powershell
Start-Process "claude-cli://open?repo=acme/payments&q=review%20open%20PRs"
```

**Windows cmd.exe：**

```cmd
start "" "claude-cli://open?repo=acme/payments&q=review%20open%20PRs"
```

## 注册和支持的平台

**Claude Code 在 macOS、Linux 和 Windows 上首次启动交互式会话时向操作系统注册 `claude-cli://` 处理器。** 无需运行单独的安装命令。注册只写入用户级位置：

| 平台 | 处理器位置 |
|------|-----------|
| macOS | `~/Applications/Claude Code URL Handler.app` |
| Linux | `claude-code-url-handler.desktop` 位于 `$XDG_DATA_HOME/applications`（默认 `~/.local/share/applications`） |
| Windows | `HKEY_CURRENT_USER\Software\Classes\claude-cli` |

**处理器在检测到的终端模拟器中启动 Claude Code。** macOS 上记住你最近交互式会话的终端并复用，支持 iTerm2、Ghostty、kitty、Alacritty、WezTerm 和 Terminal.app。Linux 上尊重 `$TERMINAL` 环境变量。Windows 上优先 Windows Terminal，然后 PowerShell，然后 cmd.exe。

要完全阻止注册，在 `settings.json` 中设置 `disableDeepLinkRegistration` 为 `"disable"`。要在组织范围强制执行，在 [managed settings](https://code.claude.com/docs/en/server-managed-settings) 中设置。

## 打开 VS Code 标签而非终端

VS Code 扩展注册了自己的处理器 `vscode://anthropic.claude-code/open`，打开 Claude Code 编辑器标签而非终端窗口。参见 [Launch a VS Code tab from other tools](https://code.claude.com/docs/en/vs-code#launch-a-vs-code-tab-from-other-tools)。

## 故障排除

### 点击链接没反应

处理器可能尚未注册。在该机器上启动一次交互式 `claude` 会话，退出，然后重试链接。

### 链接显示为纯文本而非可点击

某些 Markdown 渲染器只允许 `http` 和 `https` 链接并剥离其他 URL scheme。GitHub 在 README、issues、PR 和 wiki 中就是这样。在这些平台上，将深度链接放在代码块中让读者能看到 URL 并粘贴到浏览器地址栏。

### 会话在 home 目录打开而非仓库

`repo` 参数只能解析到 Claude Code 已经见过的克隆。在克隆中运行一次 `claude` 让其路径被记录，或将链接改为使用 `cwd` 加绝对路径。

### 链接打开了错误的终端

macOS 上在你偏好的终端启动一次 `claude`，下次深度链接就会使用它。Linux 上设置 `$TERMINAL` 环境变量。Windows 上顺序固定：安装 Windows Terminal 让链接在那里打开。

## 了解更多

- [Skills](https://code.claude.com/docs/en/skills)：将长运维 prompt 存为 `/skill`，这样深度链接的 `q` 参数只需要命名它
- [非交互模式](https://code.claude.com/docs/en/headless)：从脚本运行 Claude 并捕获输出，不打开终端
