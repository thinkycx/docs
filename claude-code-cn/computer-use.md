---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Computer Use
description: Claude Code CLI 中的 Computer Use 功能让 Claude 能打开应用、点击、打字并查看屏幕。支持原生应用测试、可视化问题调试和 GUI 工具自动化。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/computer-use.md
  - en-source/computer-use.md
---

# 从 CLI 让 Claude 使用你的电脑

> 在 Claude Code CLI 中启用 computer use，让 Claude 可以打开应用、点击、打字并查看 macOS 屏幕。测试原生应用、调试可视化问题、自动化纯 GUI 工具，全在终端完成。

**Computer use 是 macOS 上的研究预览功能，需要 Pro 或 Max 计划。** Team 或 Enterprise 计划不可用。需要 Claude Code v2.1.85 或更高版本和交互式会话，非交互模式（`-p` 标志）下不可用。

**Computer use 让 Claude 能打开应用、控制屏幕，像你一样操作你的电脑。** 在 CLI 中，Claude 可以编译 Swift 应用、启动它、点击每个按钮、截取结果——全在写代码的同一对话中完成。

本页介绍 CLI 中的 computer use 工作方式。Desktop 应用（macOS 或 Windows）参见 [computer use in Desktop](https://code.claude.com/docs/en/desktop#let-claude-use-your-computer)。

## 能做什么

**Computer use 处理需要 GUI 的任务——任何你通常需要离开终端手动完成的操作。**

- **构建和验证原生应用**：让 Claude 构建 macOS 菜单栏应用，编写 Swift、编译、启动并点击每个控件验证
- **端到端 UI 测试**：指向本地 Electron 应用说"测试注册流程"。Claude 打开应用、点击注册、截取每一步。无需 Playwright 配置
- **调试视觉和布局问题**：告诉 Claude"弹窗在小窗口中被裁剪"。Claude 调整窗口大小、复现 bug、截图、修复 CSS 并验证
- **驱动纯 GUI 工具**：与设计工具、硬件控制面板、iOS 模拟器或没有 CLI/API 的专有应用交互

## 何时触发 computer use

**Claude 有多种与应用交互的方式。Computer use 范围最广但最慢，Claude 优先使用最精确的工具：**

| 优先级 | 工具 |
| --- | --- |
| 1 | 如果有对应服务的 [MCP server](https://code.claude.com/docs/en/mcp)，使用 MCP |
| 2 | 如果任务是 shell 命令，使用 Bash |
| 3 | 如果是浏览器工作且设置了 [Claude in Chrome](https://code.claude.com/docs/en/chrome)，使用 Chrome |
| 4 | 以上都不适用时，使用 computer use |

屏幕控制保留给其他工具无法触及的场景：原生应用、模拟器和没有 API 的工具。

## 启用 computer use

**Computer use 作为名为 `computer-use` 的内置 MCP server 提供，默认关闭。**

### 步骤 1：打开 MCP 菜单

在交互式会话中运行：

```text
/mcp
```

找到 `computer-use`，状态显示为 disabled。

### 步骤 2：启用服务器

选择 `computer-use` 并选择 **Enable**。设置按项目持久化，每个需要 computer use 的项目只需做一次。

### 步骤 3：授予 macOS 权限

Claude 首次使用你的电脑时，会提示授予两项 macOS 权限：

- **辅助功能（Accessibility）**：让 Claude 点击、打字和滚动
- **屏幕录制（Screen Recording）**：让 Claude 看到屏幕内容

提示中包含打开相应系统设置面板的链接。授予两者后，在提示中选择 **Try again**。macOS 可能要求在授予屏幕录制后重启 Claude Code。

设置完成后，请求需要 GUI 的操作即可：

```text
Build the app target, launch it, and click through each tab to make
sure nothing crashes. Screenshot any error states you find.
```

## 逐会话批准应用

**启用 `computer-use` server 不会授予 Claude 访问所有应用的权限。** 每次会话中 Claude 首次需要某个应用时，终端会显示提示：

- Claude 想要控制哪些应用
- 请求的额外权限（如剪贴板访问）
- Claude 工作时将隐藏多少其他应用

选择 **Allow for this session** 或 **Deny**。批准仅持续当前会话。

**具有广泛权限的应用会显示额外警告：**

| 警告 | 适用于 |
| --- | --- |
| 等同于 shell 访问 | Terminal、iTerm、VS Code、Warp 等终端和 IDE |
| 可读写任何文件 | Finder |
| 可更改系统设置 | System Settings |

这些应用不会被阻止。警告让你判断任务是否需要该级别的访问。

Claude 的控制级别因应用类别而异：浏览器和交易平台为只读，终端和 IDE 为仅点击，其他应用为完全控制。完整层级参见 [app permissions in Desktop](https://code.claude.com/docs/en/desktop#app-permissions)。

## Claude 如何操作你的屏幕

### 一次一个会话

**Computer use 从首次操作到会话退出期间持有全机锁。** 从 v2.1.195 起，完成任务不释放锁，只有退出会话才释放。如果另一个 Claude Code 会话正在使用你的电脑，新尝试会失败并提示哪个会话持有锁。先退出那个会话。

### 工作时隐藏其他应用

Claude 开始控制屏幕时，其他可见应用被隐藏，确保 Claude 只与已批准的应用交互。终端窗口保持可见且被排除在截图之外，你可以观察会话，Claude 永远看不到自己的输出。

Claude 完成当前 turn 后，隐藏的应用自动恢复。

### 截图自动缩放

**Claude Code 在发送到模型前会自动缩小每张截图。** 在 Retina 或其他高分辨率显示器上无需降低分辨率或调整窗口。16 英寸 MacBook Pro 原生 Retina 分辨率下，从 3456x2234 缩放到约 1372x887，保持宽高比。

没有设置可更改目标大小。如果缩放后屏幕文字或控件太小无法识别，在应用中放大而非更改显示分辨率。

### 随时停止

**Claude 获取锁时，macOS 通知出现："Claude is using your computer - press Esc to stop。"** 随时按 `Esc` 立即中止当前操作，或在终端按 `Ctrl+C`。无论哪种方式，Claude 停止、恢复应用并将控制权还给你。会话保持 [computer use 锁](#一次一个会话)直到退出。

完成后会显示第二个通知。

## 安全与信任边界

**与[沙箱化 Bash 工具](https://code.claude.com/docs/en/sandboxing)不同，computer use 在你的真实桌面上运行，可访问你批准的应用。** Claude 检查每个操作并标记来自屏幕内容的潜在提示注入，但信任边界不同。最佳实践参见 [computer use safety guide](https://support.claude.com/en/articles/14128542)。

内置安全措施无需配置即可降低风险：

| 措施 | 说明 |
| --- | --- |
| 逐应用批准 | Claude 只能控制当前会话中你已批准的应用 |
| 哨兵警告 | 授予 shell、文件系统或系统设置访问的应用在批准前会被标记 |
| 终端排除截图 | Claude 永远看不到你的终端窗口 |
| 全局 Esc 键 | 随时中止 computer use，且按键被消耗防止提示注入利用 |
| 锁文件 | 同时只有一个会话可控制你的机器 |

## 示例工作流

### 验证原生构建

修改 macOS 或 iOS 应用后，让 Claude 一次性编译和验证：

```text
Build the MenuBarStats target, launch it, open the preferences window,
and verify the interval slider updates the label. Screenshot the
preferences window when you're done.
```

Claude 运行 `xcodebuild`、启动应用、与 UI 交互并报告发现。

### 复现布局 bug

当视觉 bug 只在特定窗口尺寸下出现时：

```text
The settings modal clips its footer on narrow windows. Resize the app
window down until you can reproduce it, screenshot the clipped state,
then check the CSS for the modal container.
```

Claude 调整窗口大小、截取问题状态并读取相关样式表。

### 测试模拟器流程

无需编写 XCTest 即可驱动 iOS 模拟器：

```text
Open the iOS Simulator, launch the app, tap through the onboarding
screens, and tell me if any screen takes more than a second to load.
```

Claude 像你用鼠标一样控制模拟器。

## 与 Desktop 应用的区别

| 特性 | Desktop | CLI |
| --- | --- | --- |
| 平台 | macOS 和 Windows | 仅 macOS |
| 启用 | Settings > General 中的开关 | 在 `/mcp` 中启用 `computer-use` |
| 拒绝应用列表 | 可在 Settings 中配置 | 尚不可用 |
| 自动恢复隐藏 | 可选 | 始终开启 |
| Dispatch 集成 | Dispatch 生成的会话可使用 computer use | 不适用 |

## 故障排除

### "Computer use is in use by another Claude session"

另一个 Claude Code 会话持有锁，锁在会话退出前不会释放。退出那个会话。如果另一个会话崩溃，检测到进程不再运行时锁会自动释放。

### macOS 权限提示反复出现

macOS 有时在授予屏幕录制后需要重启请求进程。完全退出 Claude Code 并开始新会话。如果提示持续出现，打开 **System Settings > Privacy & Security > Screen Recording** 确认你的终端应用已列出并启用。

### `computer-use` 不出现在 `/mcp` 中

该 server 仅在符合条件的环境中出现。检查：

- macOS 系统（CLI 中的 computer use 不支持 Linux 或 Windows。Windows 请使用 [Desktop 版 computer use](https://code.claude.com/docs/en/desktop#let-claude-use-your-computer)）
- Claude Code v2.1.85 或更高（运行 `claude --version` 检查）
- Pro 或 Max 计划（运行 `/status` 确认）
- 通过 claude.ai 认证（第三方服务商如 Bedrock、Google Cloud Agent Platform 或 Microsoft Foundry 不可用。需要单独的 claude.ai 账号使用此功能）
- 交互式会话（非交互模式 `-p` 标志下不可用）

## 相关阅读

- [Desktop 版 Computer use](https://code.claude.com/docs/en/desktop#let-claude-use-your-computer)：图形设置页面的同一功能
- [Claude in Chrome](https://code.claude.com/docs/en/chrome)：网页任务的浏览器自动化
- [MCP](https://code.claude.com/docs/en/mcp)：连接 Claude 到结构化工具和 API
- [沙箱](https://code.claude.com/docs/en/sandboxing)：Claude 的 Bash 工具如何隔离文件系统和网络访问
- [Computer use safety guide](https://support.claude.com/en/articles/14128542)：安全使用最佳实践
