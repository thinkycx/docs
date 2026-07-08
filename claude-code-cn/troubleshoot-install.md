---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】安装排错
description: 修复安装或登录 Claude Code 时的 command not found、PATH、权限、网络和认证错误。包含各平台的诊断步骤和常见问题解决方案。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/troubleshoot-install.md
  - en-source/troubleshoot-install.md
---

# 安装和登录排错

> 修复安装或登录 Claude Code 时的 command not found、PATH、权限、网络和认证错误。

**安装失败或无法登录时，在下面找到你的错误。** 运行时问题参见[故障排除](https://code.claude.com/docs/en/troubleshooting)。配置问题参见[调试配置](https://code.claude.com/docs/en/debug-your-config)。

## 错误速查表

| 你看到的 | 解决方案 |
| :--- | :--- |
| `command not found: claude` 或 `'claude' is not recognized` | [修复 PATH](#command-not-found-claude) |
| `syntax error near unexpected token '<'` | [安装脚本返回 HTML](#安装脚本返回-html) |
| `curl: (22) The requested URL returned error: 403` | [安装脚本返回 403](#安装脚本返回-html) |
| `Killed` / 退出码 137 | [释放内存或添加 swap](#低内存-linux-服务器安装被终止) |
| `TLS connect error` / `SSL/TLS secure channel` | [更新 CA 证书](#tls-或-ssl-连接错误) |
| `irm is not recognized` / `&& is not valid` | [使用正确的安装命令](#windows-上使用错误安装命令) |
| `Error loading shared library` | [二进制变体不匹配](#linux-musl-或-glibc-二进制不匹配) |
| `Illegal instruction` | [架构或 CPU 指令集不匹配](#illegal-instruction) |
| `OAuth error` / `403 Forbidden` | [修复认证](#登录和认证) |

如果你的问题不在列表中，按下面的诊断步骤缩小范围。

> 如果想跳过终端，[Claude Code Desktop 应用](https://code.claude.com/docs/en/desktop-quickstart)提供图形界面安装和使用。

## 运行诊断检查

### 检查网络连通性

安装程序从 `downloads.claude.ai` 下载。验证是否可达：

```bash
curl -sI https://downloads.claude.ai/claude-code-releases/latest
```

PowerShell 中用 `curl.exe -sI`。`HTTP/2 200` 表示到达服务器。无输出或超时表示网络阻止连接。

如果在企业代理后面，在安装前设置 `HTTPS_PROXY` 和 `HTTP_PROXY`：

macOS/Linux：
```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
curl -fsSL https://claude.ai/install.sh | bash
```

Windows PowerShell：
```powershell
$env:HTTP_PROXY = 'http://proxy.example.com:8080'
$env:HTTPS_PROXY = 'http://proxy.example.com:8080'
irm https://claude.ai/install.ps1 | iex
```

### 验证 PATH

**安装成功但运行 `claude` 报 `command not found` 时，安装目录不在 PATH 中。** 安装器将 `claude` 放在 macOS/Linux 的 `~/.local/bin/claude` 或 Windows 的 `%USERPROFILE%\.local\bin\claude.exe`。

检查安装目录是否在 PATH 中：

macOS/Linux：
```bash
echo $PATH | tr ':' '\n' | grep -Fx "$HOME/.local/bin"
```

如果无输出，添加到 shell 配置：

Zsh（macOS 默认）：
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Bash（大多数 Linux 默认）：
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Windows PowerShell：
```powershell
$currentPath = [Environment]::GetEnvironmentVariable('PATH', 'User')
[Environment]::SetEnvironmentVariable('PATH', "$currentPath;$env:USERPROFILE\.local\bin", 'User')
```

### 检查冲突安装

多个 Claude Code 安装可能导致版本不匹配。检查已安装的：

```bash
which -a claude
ls -la ~/.local/bin/claude
ls -la ~/.claude/local/
npm -g ls @anthropic-ai/claude-code 2>/dev/null
```

保留一个（推荐 `~/.local/bin/claude` 原生安装），移除其他：

```bash
npm uninstall -g @anthropic-ai/claude-code   # 移除 npm 全局安装
rm -rf ~/.claude/local                         # 移除旧版本地安装
brew uninstall --cask claude-code              # 移除 Homebrew 安装
```

### 检查目录权限

安装器需要 `~/.local/bin/` 和 `~/.claude/` 的写权限：

```bash
test -w ~/.local/bin && echo "writable" || echo "not writable"
test -w ~/.claude && echo "writable" || echo "not writable"
```

如果不可写：

```bash
sudo mkdir -p ~/.local/bin
sudo chown -R $(whoami) ~/.local
```

## 常见安装问题

### 安装脚本返回 HTML

运行安装命令时看到 `syntax error near unexpected token '<'` 或 PowerShell 的 `Missing argument in parameter list`。这表示 URL 返回了 HTML 页面而非安装脚本。如果 HTML 页面说 "App unavailable in region"，Claude Code 在你的国家/地区不可用。

**解决：** 使用替代安装方式。macOS 用 `brew install --cask claude-code`；Windows 用 `winget install Anthropic.ClaudeCode`。

### command not found: claude

安装完成但 `claude` 不工作。参见[验证 PATH](#验证-path)。

### 低内存 Linux 服务器安装被终止

安装期间的 `Killed` 消息通常表示 OOM killer 终止了进程。安装需要约 512 MB 空闲内存。

**解决：** 添加 swap 空间：

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
curl -fsSL https://claude.ai/install.sh | bash
```

### TLS 或 SSL 连接错误

`curl: (35) TLS connect error` 或 PowerShell 的 `Could not establish trust relationship` 表示 TLS 握手失败。

**解决：**

1. 更新系统 CA 证书：`sudo apt-get update && sudo apt-get install ca-certificates`
2. Windows 上启用 TLS 1.2：`[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12`
3. 企业代理做 TLS 检查时，用 `--cacert` 指向企业 CA 包：`curl --cacert /path/to/corporate-ca.pem -fsSL https://claude.ai/install.sh | bash`
4. 安装后设置 `NODE_EXTRA_CA_CERTS=/path/to/corporate-ca.pem`

### Windows 上使用错误安装命令

- `irm` not recognized → 你在 CMD 而非 PowerShell。打开 PowerShell 运行 `irm https://claude.ai/install.ps1 | iex`
- `&&` not valid → 你在 PowerShell 但用了 CMD 命令。用 PowerShell 安装器
- `-fsSL` 参数错误 → 你在 Windows PowerShell 中用了 macOS/Linux 命令。用 PowerShell 安装器

### Docker 中安装挂起

以 root 在 `/` 安装时可能挂起。

**解决：** 设置工作目录：

```dockerfile
WORKDIR /tmp
RUN curl -fsSL https://claude.ai/install.sh | bash
```

### Linux musl 或 glibc 二进制不匹配

安装后看到 `Error loading shared library libstdc++.so.6` 等错误。

**解决：** 用 `ldd --version` 检查系统使用哪个 libc。如果是 musl（如 Alpine），安装依赖：`apk add libgcc libstdc++ ripgrep`。

### Illegal instruction

原生二进制使用你的处理器不支持的 CPU 指令。可能是架构不匹配（x86 on ARM），或缺少 AVX 指令集（约 2013 年前的 CPU）。

用 `uname -m` 检查架构；在虚拟机中运行 `grep -m1 -ow avx /proc/cpuinfo` 检查 AVX。

### WSL1 上的 Exec format error

WSL1 的加载器无法处理二进制的程序头。最干净的修复是转为 WSL2：

```powershell
wsl --set-version <DistroName> 2
```

## 登录和认证

### 重置登录

登录失败时，干净的重新认证可解决大多数情况：

1. 运行 `/logout`
2. 关闭 Claude Code
3. 用 `claude` 重启并完成认证

如果浏览器不自动打开，按 `c` 复制 OAuth URL 到剪贴板。

### OAuth error: Invalid code

登录码过期或复制粘贴时被截断。

**解决：** 按 Enter 重试并在浏览器打开后尽快完成；输入 `c` 复制完整 URL。

### 403 Forbidden after login

- Claude Pro/Max 用户：在 [claude.ai/settings](https://claude.ai/settings) 验证订阅有效
- Anthropic Console 用户：确认账户有 "Claude Code" 或 "Developer" 角色
- 代理后面：参见[网络配置](https://code.claude.com/docs/en/network-config)

### This organization has been disabled

尽管有活跃订阅但看到此错误，一个 `ANTHROPIC_API_KEY` 环境变量覆盖了你的订阅。

**解决：** 取消设置环境变量：

```bash
unset ANTHROPIC_API_KEY
claude
```

检查 `~/.zshrc`、`~/.bashrc` 中的 `export ANTHROPIC_API_KEY=...` 行并移除。运行 `/status` 确认认证方式。

### WSL2/SSH/容器中 OAuth 登录失败

浏览器在不同主机打开，重定向无法到达 Claude Code 的本地回调服务器。登录后浏览器显示登录码。将该码粘贴到终端的 `Paste code here if prompted` 提示处。

如果浏览器不从 WSL2 打开，设置 `BROWSER` 环境变量：

```bash
export BROWSER="/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"
```

或用 `claude auth login` 替代，从标准输入读取粘贴的码。

### Not logged in or token expired

OAuth token 可能已过期。运行 `/login` 重新认证。

频繁发生时，检查系统时钟准确性。macOS 上可能是 Keychain 锁定；运行 `claude doctor` 检查。

### Bedrock/Agent Platform/Foundry 凭据未加载

云提供商 CLI 可能未在当前 shell 中认证。

Amazon Bedrock：`aws sts get-caller-identity`

Google Cloud：确认 `ANTHROPIC_VERTEX_PROJECT_ID` 和 `CLOUD_ML_REGION` 已设置，然后 `gcloud auth application-default login`

Microsoft Foundry：确认 `ANTHROPIC_FOUNDRY_API_KEY` 已设置，或 `az login`

如果凭据在终端有效但 VS Code/JetBrains 扩展中无效，IDE 进程可能未继承你的 shell 环境。在 IDE 设置中设置提供商环境变量。

## 仍然卡住

1. 检查 [GitHub 仓库](https://github.com/anthropics/claude-code/issues)的已知问题
2. 如果 `claude --version` 有效但有其他问题，运行 `claude doctor`
3. 如果能启动会话，使用 `/feedback` 报告问题
