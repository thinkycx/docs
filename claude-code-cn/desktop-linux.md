---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Linux 桌面版
description: Claude 桌面应用 Linux 版的安装、更新和卸载指南。支持 Ubuntu 22.04+ 和 Debian 12+，通过 apt 仓库获取更新。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/desktop-linux.md
  - en-source/desktop-linux.md
---

# Claude Desktop Linux 版（beta）

> 在 Ubuntu 和 Debian 上安装和更新 Claude 桌面应用

**Linux 桌面应用目前为 beta 阶段。** Chat、Cowork 和 Code 标签页均可用。

**Linux 桌面应用提供与 macOS 和 Windows 相同的体验：** 并行会话、可视化 diff 审查、内置终端和编辑器、实时应用预览。完整功能参见 [Use Claude Code Desktop](https://code.claude.com/docs/en/desktop)。

## 系统要求

| 要求 | 说明 |
| --- | --- |
| 系统 | Ubuntu 22.04 或更高，或 Debian 12 或更高 |
| 架构 | x86_64 或 arm64 |

其他满足条件的 Debian 系发行版可能可用，但未经官方测试。

## 安装

**推荐通过 Anthropic 的 apt 仓库安装，以便通过系统包管理器获取更新。**

### 步骤 1：添加 Anthropic apt 仓库

如果 `curl` 未安装，先安装：

```bash
sudo apt install curl
```

下载 Anthropic 签名密钥：

```bash
sudo curl -fsSLo /usr/share/keyrings/claude-desktop-archive-keyring.asc https://downloads.claude.ai/claude-desktop/key.asc
```

注册仓库：

```bash
echo "deb [arch=amd64,arm64 signed-by=/usr/share/keyrings/claude-desktop-archive-keyring.asc] https://downloads.claude.ai/claude-desktop/apt/stable stable main" | sudo tee /etc/apt/sources.list.d/claude-desktop.list
```

### 步骤 2：安装

```bash
sudo apt update && sudo apt install claude-desktop
```

### 步骤 3：启动并登录

从应用启动器打开 **Claude**，或在终端运行 `claude-desktop`，然后用 Anthropic 账号登录。

Linux 应用的登录方式与 macOS 和 Windows 相同：使用 claude.ai 订阅或组织的 SSO。桌面版不直接接受 Claude Console API key；API key 认证请使用 [CLI](https://code.claude.com/docs/en/quickstart)。企业部署路由至 Google Cloud Agent Platform 或 LLM gateway 的配置，参见[企业配置指南](https://support.claude.com/en/articles/12622667-enterprise-configuration)和[网络配置](https://code.claude.com/docs/en/network-config)。

### 验证签名密钥

可确认下载的签名密钥属于 Anthropic：

```bash
gpg --show-keys /usr/share/keyrings/claude-desktop-archive-keyring.asc
```

指纹应为 `31DD DE24 DDFA B679 F42D 7BD2 BAA9 29FF 1A7E CACE`。

### 从下载文件安装

如果无法使用 apt 仓库，先从 [claude.com/download](https://claude.com/download) 下载对应架构（x64 或 arm64）的 `.deb` 包，然后用软件安装器打开，或通过 apt 安装：

```bash
sudo apt install ./claude-desktop_*.deb
```

如果 apt 报 `E: Unsupported file ./claude-desktop_*.deb given on commandline`，说明当前目录下没有匹配的 `.deb` 文件。确认下载完成后，在包所在目录重新执行命令。

**通过此方式安装的 `.deb` 不会自动更新。** 要通过 apt 获取更新，请添加仓库（如上），或取消注释包写入 `/etc/apt/sources.list.d/claude-desktop.list` 的 `deb` 行。

## 更新

**桌面应用在 Linux 上不会自动更新。** 更新随系统常规包更新到达：

```bash
sudo apt update && sudo apt upgrade
```

发行版的图形软件更新器也会提示新版本。

## 卸载

```bash
sudo apt remove claude-desktop
```

这会同时移除签名密钥。如果安装时添加了仓库条目，也需删除：

```bash
sudo rm /etc/apt/sources.list.d/claude-desktop.list
```

## Linux beta 尚未支持的功能

| 功能 | 状态 |
| --- | --- |
| Computer Use | [应用和屏幕控制](https://code.claude.com/docs/en/desktop#let-claude-use-your-computer)在 Linux 上不可用 |
| 语音输入 | Linux 桌面应用不支持。可在 CLI 中使用[语音听写](https://code.claude.com/docs/en/voice-dictation) |
| Quick Entry 全局快捷键 | X11 下正常工作。原生 Wayland 需要桌面环境的 GlobalShortcuts portal |
| Fedora 和 RHEL | 目前仅支持 Debian 系发行版。未来会增加更多发行版支持 |

对于桌面应用尚未提供的功能，[CLI](https://code.claude.com/docs/en/quickstart) 运行相同的 Claude Code 引擎且支持更多 Linux 发行版；详见[系统要求](https://code.claude.com/docs/en/setup#system-requirements)。
