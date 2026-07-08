---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】故障排除
description: 修复 Claude Code 运行时的高 CPU/内存占用、挂起、自动压缩抖动和搜索问题，以及问题分流到正确的排错页面。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/troubleshooting.md
  - en-source/troubleshooting.md
---

# 故障排除

> 修复 Claude Code 中的高 CPU 或内存占用、挂起、自动压缩抖动和搜索问题。

**本页涵盖 Claude Code 运行后的性能、稳定性和搜索问题。** 其他问题请从对应的页面开始：

| 症状 | 前往 |
| :--- | :--- |
| `command not found`、安装失败、PATH 问题、`EACCES`、TLS 错误 | [安装排错](https://code.claude.com/docs/en/troubleshoot-install) |
| 更新下载失败（`The connection dropped while downloading the update` 或 `aborted`） | [错误参考](https://code.claude.com/docs/en/errors#the-connection-dropped-while-downloading-the-update) |
| 登录循环、OAuth 错误、`403 Forbidden`、"organization disabled"、Bedrock/Agent Platform/Foundry 凭据 | [安装排错](https://code.claude.com/docs/en/troubleshoot-install#login-and-authentication) |
| 设置未生效、hooks 未触发、MCP 服务器未加载 | [调试配置](https://code.claude.com/docs/en/debug-your-config) |
| `API Error: 5xx`、`529 Overloaded`、`429`、请求验证错误 | [错误参考](https://code.claude.com/docs/en/errors) |
| `model not found` 或 `you may not have access to it` | [错误参考](https://code.claude.com/docs/en/errors#there%E2%80%99s-an-issue-with-the-selected-model) |
| VS Code 扩展未连接或检测 Claude | [VS Code 集成](https://code.claude.com/docs/en/vs-code#fix-common-issues) |
| JetBrains 插件或 IDE 未检测到 | [JetBrains 集成](https://code.claude.com/docs/en/jetbrains#troubleshooting) |
| 高 CPU/内存、响应慢、挂起、搜索找不到文件 | [性能与稳定性](#性能与稳定性)（下文） |

如果不确定适用哪个，在 Claude Code 内运行 `/doctor` 自动检查安装、设置、MCP 配置和上下文使用。如果 `claude` 根本无法启动，从 shell 运行 `claude doctor`。

## 性能与稳定性

### 高 CPU 或内存占用

**Claude Code 可以处理大多数开发环境，但处理大型代码库时可能消耗大量资源。** 如果遇到性能问题：

1. 定期使用 `/compact` 减少上下文大小
2. 在主要任务之间关闭并重启 Claude Code
3. 考虑将大型构建目录添加到 `.gitignore`
4. 用 [`claude --safe-mode`](https://code.claude.com/docs/en/cli-reference#cli-flags) 重启，检查是否是插件、MCP 服务器或 hook 导致。它为会话禁用所有自定义项；如果占用下降，参见[调试配置](https://code.claude.com/docs/en/debug-your-config#test-against-a-clean-configuration)找出是哪个

如果这些步骤后内存占用仍然很高，运行 `/heapdump` 将 JavaScript 堆快照和内存分析写入 `~/Desktop`。Linux 上无 Desktop 文件夹时写入 home 目录。

分析显示常驻集大小、JS 堆、数组缓冲区和未计入的原生内存，帮助识别增长是在 JavaScript 对象还是原生代码中。要检查保留者，在 Chrome DevTools 的 Memory → Load 中打开 `.heapsnapshot` 文件。在 [GitHub](https://github.com/anthropics/claude-code/issues) 报告内存问题时附上两个文件。

### 自动压缩抖动停止

**如果看到 `Autocompact is thrashing: the context refilled to the limit...`**，说明自动压缩成功但文件或工具输出立即重新填满上下文窗口，连续多次。Claude Code 停止重试以避免在没有进展的循环上浪费 API 调用。

恢复方法：

1. 要求 Claude 分块读取大文件（如特定行范围或函数），而非整个文件
2. 用聚焦的 `/compact` 丢弃大输出，例如 `/compact keep only the plan and the diff`
3. 将大文件工作移到[子代理](https://code.claude.com/docs/en/sub-agents)中运行在独立上下文窗口
4. 如果早期对话不再需要，运行 `/clear`

### 命令挂起或冻结

如果 Claude Code 无响应：

1. 按 Ctrl+C 尝试取消当前操作
2. 如果仍无响应，可能需要关闭终端并重启

重启不会丢失对话。在同一目录运行 `claude --resume` 即可恢复会话。

### 编辑器集成终端中文字乱码或损坏

**如果在 VS Code、Cursor 或 Devin Desktop 集成终端中字符显示为方块、涂抹或错误字形**，终端的 GPU 渲染器通常是原因。在 Claude Code 内运行 `/terminal-setup` 将 `terminal.integrated.gpuAcceleration` 设为 `"off"`，或在编辑器设置中手动设置并重载窗口。参见[终端配置](https://code.claude.com/docs/en/terminal-config)了解 `/terminal-setup` 写入的其他设置。

### 搜索和发现问题

**如果 Search 工具、`@file` 提及、自定义代理或自定义 skills 找不到文件**，内置的 `ripgrep` 二进制可能无法在你的系统上运行。安装平台的 `ripgrep` 包并告诉 Claude Code 使用它：

macOS：
```bash
brew install ripgrep
```

Ubuntu/Debian：
```bash
sudo apt install ripgrep
```

Alpine：
```bash
apk add ripgrep
```

Arch：
```bash
pacman -S ripgrep
```

Windows：
```powershell
winget install BurntSushi.ripgrep.MSVC
```

然后在[环境](https://code.claude.com/docs/en/env-vars)中设置 `USE_BUILTIN_RIPGREP=0`。

### WSL 上搜索慢或结果不完整

**在 WSL 上[跨文件系统工作](https://learn.microsoft.com/en-us/windows/wsl/filesystems)时的磁盘读取性能损失**可能导致搜索返回比预期更少的结果。搜索仍然有效，但结果少于原生文件系统。

`/doctor` 在这种情况下会显示 Search 为 OK。

解决方案：

1. **提交更具体的搜索**：通过指定目录或文件类型减少搜索文件数："Search for JWT validation logic in the auth-service package"
2. **将项目移到 Linux 文件系统**：确保项目在 Linux 文件系统（`/home/`）而非 Windows 文件系统（`/mnt/c/`）
3. **使用原生 Windows**：考虑在 Windows 上原生运行 Claude Code 而非通过 WSL

## 获取更多帮助

如果遇到本页未涵盖的问题：

1. 运行 `/doctor` 一次性检查安装健康、设置有效性、MCP 配置和上下文使用
2. 在 Claude Code 内使用 `/feedback` 命令直接向 Anthropic 报告问题
3. 查看 [GitHub 仓库](https://github.com/anthropics/claude-code) 的已知问题
4. 直接询问 Claude 其功能和特性。Claude 内置了文档访问能力。
