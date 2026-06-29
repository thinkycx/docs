---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】Chrome 浏览器集成
description: Claude Code 与 Chrome 浏览器的集成指南（beta）。通过 Claude in Chrome 扩展将浏览器自动化能力引入 CLI，实现实时调试、设计验证、Web 应用测试、表单填写、数据提取等工作流，支持在单一工作流中串联编码任务与浏览器操作。
category: translation
tags: [claude-code, chrome, translation]
refs: [https://code.claude.com/docs/en/chrome.md]
---

# 在 Claude Code 中使用 Chrome（beta）

**将 Claude Code 连接到 Chrome 浏览器，实现 Web 应用测试、控制台日志调试、表单自动填写和网页数据提取。在 CLI 或 VS Code 扩展中即可操控浏览器，无需切换上下文。**

Claude Code 与 [Claude in Chrome 浏览器扩展](https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn) 集成，为你在 CLI 或 [VS Code 扩展](https://code.claude.com/docs/en/vs-code#automate-browser-tasks-with-chrome) 中提供浏览器自动化能力。先编写代码，再在浏览器中测试和调试，全程不用切换上下文。

Claude 会为浏览器任务打开新标签页，并共享你浏览器的登录状态，因此可以访问你已登录的任何站点。浏览器操作在可见的 Chrome 窗口中实时运行。当 Claude 遇到登录页面或验证码时，会暂停并请你手动处理。

> [!NOTE]
> Chrome 集成目前处于 beta 阶段，支持 Google Chrome 和 Microsoft Edge。暂不支持 Brave、Arc 或其他基于 Chromium 的浏览器，也不支持 WSL（Windows Subsystem for Linux）。

## 能力

**连接 Chrome 后，你可以在单一工作流中串联浏览器操作与编码任务：**

| 能力 | 说明 |
| :--- | :--- |
| 实时调试 | 直接读取控制台错误和 DOM 状态，然后修复导致问题的代码 |
| 设计验证 | 根据 Figma 稿构建 UI，然后在浏览器中打开验证是否匹配 |
| Web 应用测试 | 测试表单验证、检查视觉回退、验证用户流程 |
| 认证 Web 应用 | 与 Google Docs、Gmail、Notion 等你已登录的应用交互，无需 API 连接器 |
| 数据提取 | 从网页中提取结构化信息并保存到本地 |
| 任务自动化 | 自动化重复的浏览器任务，如数据录入、表单填写或跨站工作流 |
| 会话录制 | 将浏览器交互录制为 GIF 用于文档记录或分享 |

## 前置条件

| 条件 | 说明 |
| :--- | :--- |
| 浏览器 | [Google Chrome](https://www.google.com/chrome/) 或 [Microsoft Edge](https://www.microsoft.com/edge) |
| Chrome 扩展 | [Claude in Chrome 扩展](https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn) 1.0.36 或更高版本（Chrome Web Store 中两种浏览器均可用） |
| Claude Code | [Claude Code](https://code.claude.com/docs/en/quickstart#step-1-install-claude-code) 2.0.73 或更高版本 |
| 订阅计划 | Anthropic 直接计划（Pro、Max、Team 或 Enterprise） |

> [!NOTE]
> Chrome 集成不支持通过第三方提供商（如 Amazon Bedrock、Google Cloud Vertex AI 或 Microsoft Foundry）使用。如果你仅通过第三方提供商访问 Claude，需要一个单独的 claude.ai 账户才能使用此功能。

## 在 CLI 中开始使用

### 第 1 步：启动带 Chrome 的 Claude Code

使用 `--chrome` flag 启动 Claude Code：

```bash
claude --chrome
```

你也可以在已有会话中运行 `/chrome` 来启用 Chrome。

### 第 2 步：让 Claude 使用浏览器

以下示例导航到页面、与之交互并报告发现，全部在终端或编辑器中完成：

```text
Go to code.claude.com/docs, click on the search box,
type "hooks", and tell me what results appear
```

随时运行 `/chrome` 可以检查连接状态、管理权限、重新连接扩展，或选择使用哪个已连接的浏览器。如果浏览器操作开始时有多个浏览器连接，Claude 会提示你选择一个。

关于 VS Code 中的使用，请参阅 [VS Code 中的浏览器自动化](https://code.claude.com/docs/en/vs-code#automate-browser-tasks-with-chrome)。

### 默认启用 Chrome

**如果不想每次都传 `--chrome`，运行 `/chrome` 并选择 "Enabled by default"。**

在 [VS Code 扩展](https://code.claude.com/docs/en/vs-code#automate-browser-tasks-with-chrome) 中，只要安装了 Chrome 扩展，Chrome 就可用，不需要额外 flag。

> [!NOTE]
> 在 CLI 中默认启用 Chrome 会增加上下文使用量，因为浏览器工具始终被加载。如果你发现上下文消耗增加，可以禁用此设置，仅在需要时使用 `--chrome`。

### 管理站点权限

站点级权限继承自 Chrome 扩展。在 Chrome 扩展设置中管理权限，控制 Claude 可以在哪些站点上浏览、点击和输入。

## 工作流示例

**运行 `/mcp` 并选择 `claude-in-chrome` 可查看完整的浏览器工具列表。** 以下示例展示将浏览器操作与编码任务结合的常见方式。

### 测试本地 Web 应用

开发 Web 应用时，让 Claude 验证你的变更是否正常工作：

```text
I just updated the login form validation. Can you open localhost:3000,
try submitting the form with invalid data, and check if the error
messages appear correctly?
```

Claude 导航到你的本地服务器，与表单交互，并报告观察结果。

### 使用控制台日志调试

**Claude 可以读取控制台输出来帮助诊断问题。** 告诉 Claude 要查找什么模式，而不是要求所有控制台输出（日志可能很冗长）：

```text
Open the dashboard page and check the console for any errors when
the page loads.
```

Claude 读取控制台消息并可以过滤特定模式或错误类型。

### 自动化表单填写

加速重复的数据录入任务：

```text
I have a spreadsheet of customer contacts in contacts.csv. For each row,
go to the CRM at crm.example.com, click "Add Contact", and fill in the
name, email, and phone fields.
```

Claude 读取你的本地文件，导航 Web 界面，为每条记录输入数据。

### 在 Google Docs 中起草内容

使用 Claude 直接在你的文档中编写内容，无需 API 设置：

```text
Draft a project update based on the recent commits and add it to my
Google Doc at docs.google.com/document/d/abc123
```

Claude 打开文档，点击编辑器，输入内容。这适用于你已登录的任何 Web 应用：Gmail、Notion、Sheets 等。

### 从网页提取数据

从网站提取结构化信息：

```text
Go to the product listings page and extract the name, price, and
availability for each item. Save the results as a CSV file.
```

Claude 导航到页面，读取内容，将数据编译成结构化格式。

### 运行跨站工作流

协调跨多个网站的任务：

```text
Check my calendar for meetings tomorrow, then for each meeting with
an external attendee, look up their company website and add a note
about what they do.
```

Claude 跨标签页工作，收集信息并完成工作流。

### 录制演示 GIF

创建可分享的浏览器交互录制：

```text
Record a GIF showing how to complete the checkout flow, from adding
an item to the cart through to the confirmation page.
```

Claude 录制交互序列并保存为 GIF 文件。

## 故障排除

### 扩展未检测到

**如果 Claude Code 无法检测到 Chrome 扩展：**

1. 在 `chrome://extensions` 中验证 Chrome 扩展已安装并启用
2. 运行 `claude --version` 验证 Claude Code 已更新
3. 检查 Chrome 正在运行
4. 运行 `/chrome` 并选择 "Reconnect extension" 重新建立连接
5. 如果问题持续，重启 Claude Code 和 Chrome

首次启用 Chrome 集成时，Claude Code 会安装一个 native messaging host 配置文件。Chrome 在启动时读取该文件，所以如果首次尝试未检测到扩展，重启 Chrome 以加载新配置。

如果连接仍然失败，验证 host 配置文件是否存在：

**Chrome：**

| 平台 | 路径 |
| :--- | :--- |
| macOS | `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json` |
| Linux | `~/.config/google-chrome/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json` |
| Windows | 在 Windows Registry 中检查 `HKCU\Software\Google\Chrome\NativeMessagingHosts\` |

**Edge：**

| 平台 | 路径 |
| :--- | :--- |
| macOS | `~/Library/Application Support/Microsoft Edge/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json` |
| Linux | `~/.config/microsoft-edge/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json` |
| Windows | 在 Windows Registry 中检查 `HKCU\Software\Microsoft\Edge\NativeMessagingHosts\` |

### 浏览器无响应

**如果 Claude 的浏览器命令停止工作：**

1. 检查是否有模态对话框（alert、confirm、prompt）阻塞了页面。JavaScript 对话框会阻止浏览器事件，使 Claude 无法接收命令。手动关闭对话框，然后告诉 Claude 继续。
2. 让 Claude 创建新标签页并重试
3. 在 `chrome://extensions` 中禁用再启用 Chrome 扩展来重启它

### 长时间会话中连接断开

Chrome 扩展的 Service Worker 在长时间会话中可能进入空闲状态，导致连接中断。如果浏览器工具在一段时间不活动后停止工作，运行 `/chrome` 并选择 "Reconnect extension"。

### Windows 特有问题

在 Windows 上你可能遇到：

- **Named pipe 冲突（EADDRINUSE）**：如果另一个进程正在使用同一 named pipe，重启 Claude Code。关闭其他可能正在使用 Chrome 的 Claude Code 会话。
- **Native messaging host 错误**：如果 native messaging host 在启动时崩溃，尝试重新安装 Claude Code 以重新生成 host 配置。

### 常见错误消息

| 错误 | 原因 | 修复方法 |
| :--- | :--- | :--- |
| "Browser extension is not connected" | Native messaging host 无法到达扩展 | 重启 Chrome 和 Claude Code，然后运行 `/chrome` 重新连接 |
| "Extension not detected" | Chrome 扩展未安装或已禁用 | 在 `chrome://extensions` 中安装或启用扩展 |
| "No tab available" | Claude 在标签页准备好之前尝试操作 | 让 Claude 创建新标签页并重试 |
| "Receiving end does not exist" | 扩展 Service Worker 进入空闲 | 运行 `/chrome` 并选择 "Reconnect extension" |

## 相关文档

- [Computer use](https://code.claude.com/docs/en/computer-use) - 当任务无法在浏览器中完成时控制原生 macOS 应用
- [在 VS Code 中使用 Claude Code](https://code.claude.com/docs/en/vs-code#automate-browser-tasks-with-chrome) - VS Code 扩展中的浏览器自动化
- [CLI 参考](https://code.claude.com/docs/en/cli-reference) - 命令行 flag 包括 `--chrome`
- [常见工作流](https://code.claude.com/docs/en/common-workflows) - Claude Code 的更多使用方式
- [数据与隐私](https://code.claude.com/docs/en/data-usage) - Claude Code 如何处理你的数据
- [Chrome 扩展入门指南](https://support.claude.com/en/articles/12012173-getting-started-with-claude-in-chrome) - Chrome 扩展的完整文档，包括快捷键、定时任务和权限
