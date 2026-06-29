---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】JetBrains IDE
description: Claude Code 通过专用插件与 JetBrains IDE 集成，支持 IntelliJ、PyCharm、WebStorm 等主流 IDE，提供交互式 diff 查看、选中代码上下文共享、快捷键引用文件等功能。
category: translation
tags: [claude-code, jetbrains, ide, translation]
refs: [https://code.claude.com/docs/en/jetbrains.md]
---

# JetBrains IDE 集成

> 在 IntelliJ、PyCharm、WebStorm 等 JetBrains IDE 中使用 Claude Code

**Claude Code 通过专用插件与 JetBrains IDE 深度集成，支持交互式 diff 查看、选中代码上下文共享等功能。**

## 支持的 IDE

**Claude Code 插件兼容大多数 JetBrains IDE。**

| IDE | 说明 |
|-----|------|
| IntelliJ IDEA | Java/Kotlin 开发 |
| PyCharm | Python 开发 |
| Android Studio | Android 开发 |
| WebStorm | 前端/Node.js 开发 |
| PhpStorm | PHP 开发 |
| GoLand | Go 开发 |

## 功能特性

**插件提供五大核心能力，覆盖从启动到编码的完整流程。**

| 功能 | 说明 |
|------|------|
| 快速启动 | 使用 `Cmd+Esc`（Mac）或 `Ctrl+Esc`（Windows/Linux）直接从编辑器打开 Claude Code，也可点击 UI 中的 Claude Code 按钮 |
| Diff 查看 | 代码变更可直接在 IDE 的 diff 查看器中展示，无需在终端中查看 |
| 选中上下文 | IDE 中当前选中的内容或打开的标签页会自动共享给 Claude Code。[`Read` 拒绝规则](https://code.claude.com/docs/en/permissions#read-and-edit)会阻止匹配文件的共享 |
| 文件引用快捷键 | 使用 `Cmd+Option+K`（Mac）或 `Alt+Ctrl+K`（Linux/Windows）插入文件引用，如 `@src/auth.ts#L1-99` |
| 诊断信息共享 | IDE 中的诊断错误（如 lint 错误、语法错误）会在你工作时自动共享给 Claude |

## 安装

**插件依赖 `claude` CLI 命令，需要分别安装 CLI 和插件两部分。**

插件在 IDE 内置终端中运行 `claude` 命令并与之连接。它不会自带 CLI，因此两部分都需要安装：

### 第一步：安装 Claude Code CLI

按照[快速入门指南](https://code.claude.com/docs/en/quickstart)安装 CLI（如果还未安装）。如果 `claude` 不在你的 PATH 中，插件会弹出 "Cannot launch Claude Code" 的通知。

### 第二步：安装 JetBrains 插件

从 JetBrains Marketplace 安装 [Claude Code 插件](https://plugins.jetbrains.com/plugin/27310-claude-code-beta-)，然后重启 IDE。

如果 `claude` 安装在 IDE 无法找到的位置，可以在插件的 [Claude command 设置](#通用设置)中指定完整路径。

Claude Code 支持所有付费 Claude 订阅（Pro、Max、Team 或 Enterprise）或 Claude Console 账户，无需 API 密钥。首次运行 `claude` 时会提示你[登录](https://code.claude.com/docs/en/authentication#log-in-to-claude-code)。

> **注意**：安装插件后，可能需要完全重启 IDE 才能生效。

## 使用方式

### 从 IDE 内部使用

**在 IDE 内置终端中运行 `claude`，所有集成功能即自动激活。**

### 从外部终端使用

**在任意外部终端中使用 `/ide` 命令，可将 Claude Code 连接到 JetBrains IDE 并激活所有功能。**

```bash
claude
```

```text
/ide
```

如果希望 Claude 能访问与 IDE 相同的文件，请从 IDE 项目根目录启动 Claude Code。

## 配置

### Claude Code 设置

**通过 Claude Code 内部的设置配置 IDE 集成。**

1. 运行 `claude`
2. 输入 `/config` 命令
3. 将 diff 工具设置为 `auto`（在 IDE 中显示 diff）或 `terminal`（保留在终端中）

### 插件设置

**通过 Settings → Tools → Claude Code [Beta] 配置插件。**

#### 通用设置

| 设置项 | 说明 |
|--------|------|
| Claude command | 指定运行 Claude 的自定义命令，例如 `claude`、`/usr/local/bin/claude` 或 `npx @anthropic-ai/claude-code` |
| Suppress notification for Claude command not found | 跳过找不到 Claude 命令时的通知 |
| Enable using Option+Enter for multi-line prompts | 仅限 macOS。启用后，Option+Enter 可在 Claude Code 提示中插入换行。如果 Option 键被意外捕获，可禁用此选项。需要重启终端。 |
| Enable automatic updates | 自动检查并安装插件更新，重启后生效 |

> **提示**：WSL 用户可将 Claude command 设置为 `wsl -d Ubuntu -- bash -lic "claude"`（将 `Ubuntu` 替换为你的 WSL 发行版名称）。

#### ESC 键配置

**如果 ESC 键无法在 JetBrains 终端中中断 Claude Code 操作，需要调整终端设置。**

1. 前往 **Settings → Tools → Terminal**
2. 以下二选一：
   - 取消勾选 "Move focus to the editor with Escape"
   - 点击 "Configure terminal keybindings" 并删除 "Switch focus to Editor" 快捷键
3. 应用更改

这样 ESC 键就能正常中断 Claude Code 操作了。

## 特殊配置

### 远程开发

**使用 JetBrains 远程开发时，必须将插件安装在远程主机上（通过 Settings → Plugin (Host)）。**

插件必须安装在远程主机上，而非本地客户端机器。

### WSL 配置

**如果在 WSL2 + JetBrains IDE 中看到 "No available IDEs detected"，通常是 WSL2 的 NAT 网络或 Windows 防火墙阻止了连接。**

WSL1 直接使用主机网络，不受此问题影响。

#### 方案一：允许 WSL2 流量通过 Windows 防火墙（推荐）

这是推荐方案，因为它保留了现有的 WSL2 网络模式。

**第一步：查找 WSL2 IP 地址**

在 WSL shell 中运行：

```bash
hostname -I
```

记下子网，例如 `172.21.123.45` 属于 `172.21.0.0/16`。

**第二步：创建防火墙规则**

以管理员身份打开 PowerShell，运行以下命令（将 IP 范围调整为你的子网）：

```powershell
New-NetFirewallRule -DisplayName "Allow WSL2 Internal Traffic" -Direction Inbound -Protocol TCP -Action Allow -RemoteAddress 172.21.0.0/16 -LocalAddress 172.21.0.0/16
```

**第三步：重启 IDE 和 Claude Code**

关闭并重新打开两者，使新规则生效。

#### 方案二：将 WSL2 切换为镜像网络模式

镜像网络模式要求 Windows 11 22H2 或更高版本。如果你使用的是 Windows 10，请使用上面的防火墙规则方案。

在 Windows 用户目录下的 `.wslconfig` 中添加：

```ini
[wsl2]
networkingMode=mirrored
```

然后在 PowerShell 中运行 `wsl --shutdown` 重启 WSL。

## 故障排查

### 插件不工作

**如果插件已安装但 Claude Code 功能未出现在 IDE 中：**

- 确保从项目根目录运行 Claude Code
- 检查 JetBrains 插件是否在 IDE 设置中启用
- 完全重启 IDE（可能需要多次重启）
- 远程开发场景下，确保插件安装在远程主机上

### IDE 未检测到

**如果运行 `claude` 后显示 "No available IDEs detected"：**

- 确认插件已安装并启用
- 完全重启 IDE
- 确认从内置终端运行 Claude Code
- WSL 用户请参考上文的 [WSL 配置](#wsl-配置)

### 命令找不到

**如果点击 Claude 图标后显示 "command not found"：**

1. 在终端中运行 `claude --version` 确认 Claude Code 已安装
2. 在插件设置中配置 Claude command 路径
3. WSL 用户请使用配置部分提到的 WSL 命令格式

## 安全注意事项

**当 Claude Code 在启用自动编辑权限的 JetBrains IDE 中运行时，它可能修改 IDE 配置文件，而这些文件可能被 IDE 自动执行。**

这可能增加在自动编辑模式下运行 Claude Code 的风险，并可能绕过 Claude Code 对 bash 执行的权限提示。

在 JetBrains IDE 中运行时，建议：

- 对编辑操作使用手动审批模式
- 格外注意只在可信的提示下使用 Claude
- 了解 Claude Code 有权修改哪些文件

如果遇到 IDE 之外的 Claude Code 安装或登录问题，请参阅[安装和登录故障排查](https://code.claude.com/docs/en/troubleshoot-install)。
