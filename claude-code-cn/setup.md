---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】高级安装
description: Claude Code 的系统要求、平台特定安装、版本管理和卸载的完整参考。涵盖原生安装、Homebrew、WinGet、Linux 包管理器、npm 安装以及二进制完整性验证。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/setup.md
  - en-source/setup.md
---

# 高级安装

> Claude Code 的系统要求、平台特定安装、版本管理和卸载。

本页涵盖系统要求、平台特定安装细节、更新和卸载。首次会话的引导流程参见[快速开始](https://code.claude.com/docs/en/quickstart)。

## 系统要求

Claude Code 运行在以下平台和配置上：

| 类别 | 要求 |
|------|------|
| **操作系统** | macOS 13.0+、Windows 10 1809+ / Windows Server 2019+、Ubuntu 20.04+、Debian 10+、Alpine Linux 3.19+ |
| **硬件** | 4 GB+ RAM，x64 或 ARM64 处理器 |
| **网络** | 需要互联网连接。参见[网络配置](https://code.claude.com/docs/en/network-config#network-access-requirements) |
| **Shell** | Bash、Zsh、PowerShell 或 CMD |
| **位置** | [Anthropic 支持的国家/地区](https://www.anthropic.com/supported-countries) |

额外依赖：**ripgrep** 通常随 Claude Code 包含。

## 安装 Claude Code

> [!TIP]
> 偏好图形界面？[桌面应用](https://code.claude.com/docs/en/desktop-quickstart)让你无需终端使用 Claude Code。

### 原生安装（推荐）

**macOS / Linux / WSL：**

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows PowerShell：**

```powershell
irm https://claude.ai/install.ps1 | iex
```

**Windows CMD：**

```batch
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

如果看到 `The token '&&' is not a valid statement separator` 说明你在 PowerShell 而非 CMD。如果看到 `'irm' is not recognized` 说明你在 CMD 而非 PowerShell。

原生安装会在后台自动更新以保持最新版本。

### Homebrew

```bash
brew install --cask claude-code
```

Homebrew 提供两个 cask：`claude-code` 跟踪稳定发布频道（通常落后约一周），`claude-code@latest` 跟踪 latest 频道。Homebrew 安装不自动更新，需运行 `brew upgrade claude-code` 手动更新。

### WinGet

```powershell
winget install Anthropic.ClaudeCode
```

WinGet 安装不自动更新，需定期运行 `winget upgrade Anthropic.ClaudeCode`。

安装完成后，在项目目录打开终端启动 Claude Code：

```bash
claude
```

### Windows 设置

可以在原生 Windows 或 WSL 中运行 Claude Code：

| 选项 | 要求 | [沙箱](https://code.claude.com/docs/en/sandboxing) | 适用场景 |
|------|------|------|---------|
| 原生 Windows | 无；[Git for Windows](https://git-scm.com/downloads/win) 可选 | 不支持 | Windows 原生项目和工具 |
| WSL 2 | 启用 WSL 2 | 支持 | Linux 工具链或沙箱命令执行 |
| WSL 1 | 启用 WSL 1 | 不支持 | WSL 2 不可用时 |

**原生 Windows**：从 PowerShell 或 CMD 运行安装命令，不需要管理员权限。安装 [Git for Windows](https://git-scm.com/downloads/win) 可选但推荐（启用 Bash 工具）。

**WSL**：打开 WSL 发行版，运行 Linux 安装命令。在 WSL 终端内安装和启动 `claude`。

### Alpine Linux 和基于 musl 的发行版

需要 `libgcc`、`libstdc++` 和 `ripgrep`：

```bash
apk add libgcc libstdc++ ripgrep
```

然后在 `settings.json` 中设置：

```json
{
  "env": {
    "USE_BUILTIN_RIPGREP": "0"
  }
}
```

## 验证安装

```bash
claude --version
```

更详细的检查：

```bash
claude doctor
```

## 认证

Claude Code 需要 Pro、Max、Team、Enterprise 或 Console 账号。免费 Claude.ai 计划不包含 Claude Code 访问。也支持第三方 API 提供商如 [Amazon Bedrock](https://code.claude.com/docs/en/amazon-bedrock)、[Google Cloud Agent Platform](https://code.claude.com/docs/en/google-vertex-ai) 或 [Microsoft Foundry](https://code.claude.com/docs/en/microsoft-foundry)。

## 更新 Claude Code

原生安装在后台自动更新。可以[配置发布频道](#配置发布频道)或[禁用自动更新](#禁用自动更新)。

### 自动更新

Claude Code 在启动时和运行期间定期检查更新。更新在后台下载安装，下次启动 Claude Code 时生效。

### 配置发布频道

用 `autoUpdatesChannel` 设置控制发布频道：

| 频道 | 说明 |
|------|------|
| `"latest"`（默认） | 发布后立即接收新功能 |
| `"stable"` | 使用通常约一周前的版本，跳过有重大回归的发布 |

```json
{
  "autoUpdatesChannel": "stable"
}
```

### 锁定最低版本

`minimumVersion` 设置建立最低版本。后台自动更新和 `claude update` 拒绝安装低于此值的任何版本：

```json
{
  "autoUpdatesChannel": "stable",
  "minimumVersion": "2.1.100"
}
```

### 禁用自动更新

在 `settings.json` 的 `env` 键中设置：

```json
{
  "env": {
    "DISABLE_AUTOUPDATER": "1"
  }
}
```

`DISABLE_AUTOUPDATER` 只停止后台检查；`claude update` 和 `claude install` 仍可用。要阻止所有更新路径（包括手动），设置 `DISABLE_UPDATES`。

### 手动更新

```bash
claude update
```

## 高级安装选项

### 安装特定版本

原生安装支持特定版本号或发布频道（`latest` 或 `stable`）。

**安装 stable 版本：**

```bash
curl -fsSL https://claude.ai/install.sh | bash -s stable
```

**安装特定版本：**

```bash
curl -fsSL https://claude.ai/install.sh | bash -s 2.1.89
```

### Linux 包管理器安装

Claude Code 发布签名的 apt、dnf 和 apk 仓库。

**apt（Debian/Ubuntu）：**

```bash
sudo install -d -m 0755 /etc/apt/keyrings
sudo curl -fsSL https://downloads.claude.ai/keys/claude-code.asc \
  -o /etc/apt/keyrings/claude-code.asc
echo "deb [signed-by=/etc/apt/keyrings/claude-code.asc] https://downloads.claude.ai/claude-code/apt/stable stable main" \
  | sudo tee /etc/apt/sources.list.d/claude-code.list
sudo apt update
sudo apt install claude-code
```

升级：`sudo apt update && sudo apt upgrade claude-code`

**dnf（Fedora/RHEL）：**

```bash
sudo tee /etc/yum.repos.d/claude-code.repo <<'EOF'
[claude-code]
name=Claude Code
baseurl=https://downloads.claude.ai/claude-code/rpm/stable
enabled=1
gpgcheck=1
gpgkey=https://downloads.claude.ai/keys/claude-code.asc
EOF
sudo dnf install claude-code
```

升级：`sudo dnf upgrade claude-code`

**apk（Alpine）：**

```sh
wget -O /etc/apk/keys/claude-code.rsa.pub \
  https://downloads.claude.ai/keys/claude-code.rsa.pub
echo "https://downloads.claude.ai/claude-code/apk/stable" >> /etc/apk/repositories
apk add claude-code
```

升级：`apk update && apk upgrade claude-code`

GPG 密钥指纹验证：`31DD DE24 DDFA B679 F42D 7BD2 BAA9 29FF 1A7E CACE`

### npm 安装

npm 包从 v2.1.198 起需要 [Node.js 22 或更高版本](https://nodejs.org/en/download)：

```bash
npm install -g @anthropic-ai/claude-code
```

npm 包安装与独立安装器相同的原生二进制文件。安装的 `claude` 二进制不调用 Node。

升级 npm 安装：`npm install -g @anthropic-ai/claude-code@latest`（避免使用 `npm update -g`）。

> [!WARNING]
> 不要使用 `sudo npm install -g`，这会导致权限问题和安全风险。

### 二进制完整性和代码签名

每个发布都发布包含每个平台二进制 SHA256 校验和的 `manifest.json`。manifest 用 Anthropic GPG 密钥签名。

**验证步骤：**

1. 下载并导入公钥：`curl -fsSL https://downloads.claude.ai/keys/claude-code.asc | gpg --import`
2. 确认指纹：`31DD DE24 DDFA B679 F42D 7BD2 BAA9 29FF 1A7E CACE`
3. 下载 manifest 和签名，验证：`gpg --verify manifest.json.sig manifest.json`
4. 对比二进制 SHA256 校验和

**平台代码签名：**
- **macOS**：由 "Anthropic PBC" 签名并经 Apple 公证。验证：`codesign --verify --verbose ./claude`
- **Windows**：由 "Anthropic, PBC" 签名。验证：`Get-AuthenticodeSignature .\claude.exe`
- **Linux**：二进制不单独签名，使用上述 manifest 签名验证

## 卸载 Claude Code

### 原生安装

```bash
rm -f ~/.local/bin/claude
rm -rf ~/.local/share/claude
```

Windows PowerShell：

```powershell
Remove-Item -Path "$env:USERPROFILE\.local\bin\claude.exe" -Force
Remove-Item -Path "$env:USERPROFILE\.local\share\claude" -Recurse -Force
```

### Homebrew

```bash
brew uninstall --cask claude-code
```

### WinGet

```powershell
winget uninstall Anthropic.ClaudeCode
```

### apt / dnf / apk

**apt：**
```bash
sudo apt remove claude-code
sudo rm /etc/apt/sources.list.d/claude-code.list /etc/apt/keyrings/claude-code.asc
```

**dnf：**
```bash
sudo dnf remove claude-code
sudo rm /etc/yum.repos.d/claude-code.repo
```

**apk：**
```sh
apk del claude-code
sed -i '\|downloads.claude.ai/claude-code/apk|d' /etc/apk/repositories
rm /etc/apk/keys/claude-code.rsa.pub
```

### npm

```bash
npm uninstall -g @anthropic-ai/claude-code
```

### 删除配置文件

> [!WARNING]
> 删除配置文件会移除所有设置、允许的工具、MCP 服务器配置和会话历史。

```bash
# 删除用户设置和状态
rm -rf ~/.claude
rm ~/.claude.json

# 删除项目特定设置（在项目目录中运行）
rm -rf .claude
rm -f .mcp.json
```
