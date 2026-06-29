---
title: 【译】沙箱机制
tags:
  - claude-code
  - sandboxing
  - security
  - translation
create: 2026-06-28
update: 2026-06-28
author: thinkycx
category: translation
description: 介绍 Claude Code 沙箱化 Bash 工具的工作原理，包括文件系统隔离、网络隔离、OS 级别强制执行机制，以及如何为组织配置和强制沙箱策略。
refs: https://code.claude.com/docs/en/sandboxing.md
---

# 配置沙箱化的 Bash 工具

> 了解 Claude Code 的沙箱化 Bash 工具如何通过文件系统和网络隔离，实现更安全、更自主的 agent 执行。

**沙箱让 Claude 无需逐条审批即可执行大多数 shell 命令。** 你只需定义命令可以访问哪些文件和网络域名，操作系统会为每个 Bash 命令及其子进程强制执行该边界。

> [!NOTE]
> 要比较其他隔离方案（如 dev container、自定义容器、虚拟机），参见 [Sandbox environments](https://code.claude.com/docs/en/sandbox-environments)。要减少 Bash 以外工具的权限提示，参见 [Permission modes](https://code.claude.com/docs/en/permission-modes)。

## 快速开始

**沙箱内置于 Claude Code，支持 macOS、Linux 和 WSL2。** 原生 Windows 不支持，需在 WSL2 中运行。

在 macOS 上无需安装额外组件：沙箱使用内置的 Seatbelt 框架。在 Linux 和 WSL2 上，沙箱依赖两个包，详见 [设置 Linux 和 WSL2](#设置-linux-和-wsl2)。即使尚未安装，你也可以先运行 `/sandbox`，因为面板会显示是否缺少依赖。

### 步骤一：运行 /sandbox

启动 Claude Code 会话并运行 `/sandbox` 命令：

```text
/sandbox
```

这会打开沙箱面板，包含三个标签页：

- **Mode**：选择沙箱命令的审批方式（见下一步）
- **Overrides**：选择在沙箱下失败的命令是否可以回退到非沙箱执行（即 [`allowUnsandboxedCommands`](https://code.claude.com/docs/en/settings#sandbox-settings) 设置）
- **Config**：查看最终生效的沙箱配置

如果面板只显示 Dependencies 标签页，说明缺少必要的包。按照 [设置 Linux 和 WSL2](#设置-linux-和-wsl2) 安装后重启 Claude Code，再次运行 `/sandbox`。

### 步骤二：选择模式

在 Mode 标签页，选择 auto-allow 或 regular permissions。Auto-allow 运行沙箱命令时不提示，regular permissions 即使命令在沙箱中也保持常规权限提示。详见 [沙箱模式](#沙箱模式)。

### 步骤三：运行 Bash 命令

让 Claude 运行一个命令，如构建或测试套件。默认情况下，沙箱内的命令只能写入工作目录和会话临时目录。命令首次需要访问新的网络域名时，Claude Code 会提示审批。

无法在沙箱中运行的命令会回退到常规权限流程。要扩大或缩小这些边界，参见 [配置沙箱](#配置沙箱)。

---

**在面板中选择模式会写入项目本地设置** `.claude/settings.local.json`，仅适用于当前项目且不会提交到 git。要在所有项目中启用沙箱，在用户设置 `~/.claude/settings.json` 中将 [`sandbox.enabled`](https://code.claude.com/docs/en/settings#sandbox-settings) 设为 `true`。要为组织中的所有开发者强制启用沙箱，使用 [managed settings](#用-managed-settings-强制沙箱)。

> [!WARNING]
> 默认情况下，如果沙箱因缺少依赖或平台不支持而无法启动，Claude Code 会显示警告并以非沙箱方式运行命令。要将其改为硬失败，将 [`sandbox.failIfUnavailable`](https://code.claude.com/docs/en/settings#sandbox-settings) 设为 `true`。此设置适用于将沙箱作为安全门控的托管部署。

### 设置 Linux 和 WSL2

**Linux 和 WSL2 上沙箱依赖两个包：**

| 包 | 用途 |
| :--- | :--- |
| [`bubblewrap`](https://github.com/containers/bubblewrap) | 无特权沙箱工具，强制文件系统隔离 |
| [`socat`](http://www.dest-unreach.org/socat/) | 中继工具，用于将网络流量路由到沙箱代理 |

Ubuntu/Debian 安装：

```bash
sudo apt-get install bubblewrap socat
```

Fedora 安装：

```bash
sudo dnf install bubblewrap socat
```

安装后，`/sandbox` 中的 Dependencies 标签页会显示 `ripgrep`、`bubblewrap`、`socat` 和 seccomp 过滤器是否可用。Ripgrep 捆绑在原生 Claude Code 二进制文件中。seccomp 过滤器可选，用于阻止 Unix 域套接字。如果缺失，用 `npm install -g @anthropic-ai/sandbox-runtime` 安装。

**Ubuntu 24.04 及更高版本：允许 bubblewrap 创建用户命名空间**

在 Ubuntu 24.04 及更高版本上，默认 AppArmor 策略阻止 bubblewrap 创建隔离所需的用户命名空间。

检查是否存在此限制（包括 WSL2 内）：运行 `sysctl kernel.apparmor_restrict_unprivileged_userns`。如果键不存在或返回 `0`，跳过此步骤。如果返回 `1`，添加一个 AppArmor 配置文件：

```bash
sudo tee /etc/apparmor.d/bwrap > /dev/null <<'EOF'
abi <abi/4.0>,
include <tunables/global>

profile bwrap /usr/bin/bwrap flags=(unconfined) {
  userns,
  include if exists <local/bwrap>
}
EOF
```

重新加载 AppArmor：

```bash
sudo systemctl reload apparmor
```

**WSL2 注意事项**

用 PowerShell 中的 `wsl -l -v` 检查 WSL 版本。如果看到 `Sandboxing requires WSL2`，你的发行版运行的是 WSL1，需升级到 WSL2。

在 WSL2 上，沙箱命令无法启动 Windows 二进制文件（如 `cmd.exe`、`powershell.exe` 或 `/mnt/c/` 下的任何内容）。如果命令需要调用 Windows 二进制文件，将其添加到 [`excludedCommands`](https://code.claude.com/docs/en/settings#sandbox-settings) 使其在沙箱外运行。

### 沙箱模式

**Claude Code 提供两种沙箱模式：**

| 模式 | 行为 |
| :--- | :--- |
| **Auto-allow 模式** | Bash 命令尝试在沙箱内运行并自动允许，无需权限提示。无法沙箱化的命令回退到常规权限流程。 |
| **Regular permissions 模式** | 所有 Bash 命令都走常规权限流程，即使已沙箱化。提供更多控制但需要更多审批。 |

**即使在 auto-allow 模式下，以下规则仍然适用：**

- 显式 [deny 规则](https://code.claude.com/docs/en/permissions) 始终被尊重
- 针对 `/`、home 目录或其他关键系统路径的 `rm` 或 `rmdir` 命令仍会触发权限提示
- 有内容范围的 [ask 规则](https://code.claude.com/docs/en/permissions)（如 `Bash(git push *)`）仍会强制提示
- 裸 `Bash` ask 规则或等效的 `Bash(*)` 形式，对沙箱命令会被跳过；但对回退到常规权限流程的命令仍然适用

**在两种模式下，沙箱强制执行相同的文件系统和网络限制。** 区别仅在于沙箱命令是自动批准还是需要显式权限。

**关于临时目录：** 会话临时目录在沙箱内默认可写。Claude Code 为沙箱命令设置 `$TMPDIR` 指向此目录。非沙箱命令继承 shell 的 `$TMPDIR`，这意味着沙箱和非沙箱命令的 `$TMPDIR` 解析到不同目录。要在两者间传递临时文件，请写入工作目录。

**关于逃逸机制：** 某些命令完全无法在沙箱内运行。当命令因沙箱限制失败时，Claude 会分析失败原因并可能用 `dangerouslyDisableSandbox` 参数重试。重试的命令在沙箱外运行，需经过常规权限流程。

你可以通过在 [沙箱设置](https://code.claude.com/docs/en/settings#sandbox-settings) 中设置 `"allowUnsandboxedCommands": false` 来禁用此逃逸机制（即 `/sandbox` Overrides 标签页显示的 **严格沙箱模式**）。

> [!NOTE]
> Auto-allow 模式独立于你的 permission mode 设置。即使你不在 "accept edits" 模式下，当 auto-allow 启用时，沙箱化的 Bash 命令仍会自动运行。这意味着修改沙箱边界内文件的 Bash 命令会无提示执行，即使文件编辑工具通常需要审批。

## 配置沙箱

**通过 `settings.json` 文件自定义沙箱行为。** 参见 [Settings](https://code.claude.com/docs/en/settings#sandbox-settings) 获取完整配置参考。

默认情况下，沙箱命令只能写入当前工作目录和会话临时目录。如果子进程命令（如 `kubectl`、`terraform`、`npm`）需要写入这些目录之外的位置，使用 `sandbox.filesystem.allowWrite` 授权：

```json
{
  "sandbox": {
    "enabled": true,
    "filesystem": {
      "allowWrite": ["~/.kube", "/tmp/build"]
    }
  }
}
```

这些路径在 OS 级别强制执行，沙箱内运行的所有命令（包括子进程）都遵守。这是推荐做法——当工具需要写入特定位置时，优先使用此方式而非用 `excludedCommands` 将工具排除出沙箱。

**当多个设置范围中定义了相同的 filesystem 数组时，数组会合并：各范围的路径被组合而非替换。**

**路径前缀规则：**

| 前缀 | 含义 | 示例 |
| :--- | :--- | :--- |
| `/` | 从文件系统根目录的绝对路径 | `/tmp/build` 保持 `/tmp/build` |
| `~/` | 相对于 home 目录 | `~/.kube` 变为 `$HOME/.kube` |
| `./` 或无前缀 | 对项目设置相对于项目根目录，对用户设置相对于 `~/.claude` | `.claude/settings.json` 中的 `./output` 解析为 `<project-root>/output` |

此语法不同于 [Read 和 Edit 权限规则](https://code.claude.com/docs/en/permissions#read-and-edit)（使用 `//path` 表示绝对路径，`/path` 表示项目相对路径）。沙箱文件系统路径使用标准约定：`/tmp/build` 是绝对路径。

**你还可以使用 `sandbox.filesystem.denyWrite` 和 `sandbox.filesystem.denyRead` 拒绝写入或读取访问，用 `sandbox.filesystem.allowRead` 在被拒绝区域内重新允许特定路径。**

以下示例阻止读取整个 home 目录，同时仍允许读取当前项目。将其放在项目的 `.claude/settings.json` 中，因为相对路径 `.` 只有在配置位于项目设置中时才解析为项目根目录：

```json
{
  "sandbox": {
    "enabled": true,
    "filesystem": {
      "denyRead": ["~/"],
      "allowRead": ["."]
    }
  }
}
```

### 保护凭证

**`sandbox.credentials` 设置声明沙箱命令不可访问的凭证文件和环境变量。** 列出的文件路径在沙箱内被拒绝读取（与 `filesystem.denyRead` 相同），列出的环境变量在每个沙箱命令运行前被清除。需要 Claude Code v2.1.187 或更高版本。

以下示例阻止读取 AWS 凭证文件和 SSH 目录，并从沙箱命令环境中移除 `GITHUB_TOKEN` 和 `NPM_TOKEN`：

```json
{
  "sandbox": {
    "enabled": true,
    "credentials": {
      "files": [
        { "path": "~/.aws/credentials", "mode": "deny" },
        { "path": "~/.ssh", "mode": "deny" }
      ],
      "envVars": [
        { "name": "GITHUB_TOKEN", "mode": "deny" },
        { "name": "NPM_TOKEN", "mode": "deny" }
      ]
    }
  }
}
```

每个条目带有 `"mode": "deny"`（目前唯一支持的值）。文件路径遵循与 `sandbox.filesystem.*` 设置相同的 [前缀规则](https://code.claude.com/docs/en/settings#sandbox-path-prefixes)，各 [设置范围](https://code.claude.com/docs/en/settings#settings-precedence) 的条目会合并。因为唯一的 mode 是 `deny`，任何范围都只能添加限制而不能移除。

没有内置的凭证拒绝列表，只有你列出的文件和变量会被限制。此设置仅影响沙箱 Bash 命令。要从所有子进程中剥离 Anthropic 和云提供商凭证（无论是否沙箱化），设置 [`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`](https://code.claude.com/docs/en/env-vars)。

## 沙箱工作原理

### 文件系统隔离

**沙箱化的 Bash 工具将文件系统访问限制在特定目录：**

| 类型 | 行为 |
| :--- | :--- |
| 默认写入 | 对当前工作目录及其子目录、会话临时目录（`$TMPDIR`）有读写权限 |
| 默认读取 | 对整台电脑有读取权限，但某些被拒绝的目录除外。注意默认仍允许读取凭证文件（如 `~/.aws/credentials`、`~/.ssh/`）。使用 [`sandbox.credentials`](#保护凭证) 来阻止 |
| 被阻止的访问 | 未经显式许可，不能修改工作目录和会话临时目录之外的文件，包括 shell 配置文件（如 `~/.bashrc`）和系统二进制文件（`/bin/`） |
| Git worktrees | 当工作目录是 [链接的 git worktree](https://code.claude.com/docs/en/worktrees) 时，沙箱还允许写入主仓库共享的 `.git` 目录（以便 `git commit` 更新 refs 和索引）。该目录内 `hooks/` 和 `config` 的写入仍被拒绝 |
| 可配置 | 通过设置定义自定义的允许和拒绝路径 |

### 网络隔离

**网络访问通过运行在沙箱外的代理服务器控制：**

- **域名限制**：没有预先允许的域名。命令首次需要新域名时，Claude Code 提示审批。从 v2.1.191 起，选择 Yes 允许该主机在当前会话剩余时间内使用。用 [`allowedDomains`](https://code.claude.com/docs/en/settings#sandbox-settings) 预先允许域名以避免提示。
- **托管锁定**：如果 managed settings 中设置了 [`allowManagedDomainsOnly`](https://code.claude.com/docs/en/settings#sandbox-settings)，非允许域名会被自动阻止而非提示，且仅 managed settings 中的 `allowedDomains` 生效。
- **自定义代理支持**：高级用户可对出站流量实现自定义规则。
- **全面覆盖**：限制适用于命令派生的所有脚本、程序和子进程。

> [!NOTE]
> 内置代理基于请求的主机名执行允许列表，不终止或检查 TLS 流量。参见 [安全限制](#安全限制) 了解此设计的影响，如果你的威胁模型需要 TLS 检查，参见 [自定义代理配置](#自定义代理配置)。

### OS 级别强制执行

**沙箱化 Bash 工具利用操作系统安全原语：**

| 平台 | 机制 |
| :--- | :--- |
| macOS | 使用 Seatbelt 进行沙箱强制执行 |
| Linux | 使用 [bubblewrap](https://github.com/containers/bubblewrap) 进行隔离 |
| WSL2 | 使用 bubblewrap，与 Linux 相同 |

WSL1 不支持，因为 bubblewrap 需要仅 WSL2 提供的内核特性。OS 级别限制确保 Claude Code 命令产生的所有子进程继承相同的安全边界。

这些原语也作为独立的 [`@anthropic-ai/sandbox-runtime`](https://github.com/anthropic-experimental/sandbox-runtime) 包提供，[Sandbox environments](https://code.claude.com/docs/en/sandbox-environments#sandbox-runtime) 页面将其作为包装整个 Claude Code 进程的独立方案介绍。

## 沙箱与权限及权限模式的关系

**沙箱、[权限规则](https://code.claude.com/docs/en/permissions) 和 [权限模式](https://code.claude.com/docs/en/permission-modes) 是互补的层次。**

### 权限规则

权限规则和沙箱控制不同的事物：

- **权限规则** 控制 Claude Code 可以使用哪些工具，在任何工具运行之前评估。适用于所有工具：Bash、Read、Edit、WebFetch、MCP 等。
- **沙箱** 提供 OS 级别的强制执行，限制 Bash 命令可以在文件系统和网络层面访问什么。仅适用于 Bash 命令及其子进程。

两者的执行方式也不同。Claude Code 在命令运行前做权限判断（基于命令字符串，在 auto mode 下还基于分类器判断）。操作系统在运行中的进程上强制沙箱边界——无论模型选择运行什么命令，即使被允许的命令做了超出其名称暗示的事情。

**文件系统和网络限制通过沙箱设置和权限规则共同配置：**

| 设置或规则 | 作用 |
| :--- | :--- |
| `sandbox.filesystem.allowWrite` | 授权子进程写入工作目录之外的路径 |
| `sandbox.filesystem.denyWrite` 和 `sandbox.filesystem.denyRead` | 阻止子进程访问特定路径 |
| `sandbox.filesystem.allowRead` | 在 `denyRead` 区域内重新允许读取特定路径 |
| `Edit` allow 规则 | 授权写入特定路径（方式与 `sandbox.filesystem.allowWrite` 相同） |
| `Read` 和 `Edit` deny 规则 | 阻止访问特定文件或目录 |
| `WebFetch` allow 和 deny 规则 | 控制域名访问 |
| 沙箱 `allowedDomains` | 控制 Bash 命令可以访问哪些域名 |
| 沙箱 `deniedDomains` | 阻止特定域名（即使更宽泛的 `allowedDomains` 通配符本应允许） |

来自 `sandbox.filesystem` 设置和权限规则的路径会合并到最终沙箱配置中。

[claude-code 仓库的 examples 目录](https://github.com/anthropics/claude-code/tree/main/examples/settings) 包含常见部署场景的起始设置配置，包括沙箱相关示例。

### 权限模式

**`/sandbox` 不是 [权限模式](https://code.claude.com/docs/en/permission-modes)。** 权限模式决定工具调用是否运行以及是否需要提示，沙箱限制 Bash 命令运行后可以访问什么。

| | 控制什么 | 什么替代了提示 |
| :--- | :--- | :--- |
| `/sandbox` | Bash 命令运行后可以访问什么 | 沙箱边界本身（在 [auto-allow 模式](#沙箱模式) 下） |
| [Auto mode](https://code.claude.com/docs/en/permission-modes#eliminate-prompts-with-auto-mode) | 每个工具调用是否运行 | 审查操作的分类器 |
| `--dangerously-skip-permissions` | 每个工具调用是否运行 | 无。[受保护路径](https://code.claude.com/docs/en/permission-modes#protected-paths) 检查也被跳过 |

沙箱的 [auto-allow 模式](#沙箱模式) 与 [auto mode](https://code.claude.com/docs/en/permission-modes#eliminate-prompts-with-auto-mode) 是分开的：auto-allow 批准 Bash 命令是因为沙箱边界包含了它们，而 auto mode 使用分类器审查操作。两者独立工作并可组合。要为无人值守运行选择隔离边界，参见 [Sandbox environments](https://code.claude.com/docs/en/sandbox-environments#how-isolation-relates-to-permission-modes)。

## 为组织配置沙箱

**管理员可以为每个用户强制沙箱，防止开发者放宽策略，并将沙箱流量路由到企业代理。**

### 用 Managed Settings 强制沙箱

要为每个开发者强制沙箱，通过 [managed settings](https://code.claude.com/docs/en/settings#settings-files) 分发 `sandbox` 键（通过 MDM 管理的文件或 Claude.ai 上的 [server-managed settings](https://code.claude.com/docs/en/server-managed-settings)）。

以下 managed settings 配置启用沙箱、沙箱无法初始化时拒绝启动 Claude Code、并防止模型在沙箱外重试命令：

```json
{
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true,
    "allowUnsandboxedCommands": false
  }
}
```

`enabled` 之外的两个键控制沙箱无法运行命令时的行为：

- **`failIfUnavailable`**：Linux 上缺少 bubblewrap 等依赖时阻止 Claude Code 启动，而不是显示警告并回退到非沙箱执行
- **`allowUnsandboxedCommands: false`**：`dangerouslyDisableSandbox` 逃逸机制被忽略，沙箱下失败的命令不能在沙箱外重试

建议同时添加 `excludedCommands`（用于必须在无隔离下运行的组织批准工具）和 [`sandbox.credentials`](#保护凭证) 条目（用于凭证目录和敏感环境变量）。

### 防止开发者放宽策略

对于布尔键（如 `enabled` 和 `failIfUnavailable`），Claude Code 使用 managed 值并忽略开发者本地设置。对于数组键（如 `excludedCommands` 和 `allowRead`），Claude Code 合并所有范围的条目，因此开发者可以追加放宽策略的条目。

在 managed settings 中设置 `allowManagedReadPathsOnly` 为 `true`，这样只有 managed settings 中的 `allowRead` 条目生效。用户、项目和本地的 `allowRead` 条目被忽略。要以相同方式锁定网络域名到 managed 值，设置 [`allowManagedDomainsOnly`](https://code.claude.com/docs/en/settings#sandbox-settings)。

`excludedCommands` 没有等效的 managed-only 锁定，因此开发者始终可以追加在沙箱外运行额外命令的条目。保持 managed 列表精简。

### 自定义代理配置

**对于需要高级网络安全的组织，你可以实现自定义代理来：**

- 解密和检查 HTTPS 流量
- 应用自定义过滤规则
- 记录所有网络请求
- 与现有安全基础设施集成

将 Claude Code 指向你的代理：

```json
{
  "sandbox": {
    "network": {
      "httpProxyPort": 8080,
      "socksProxyPort": 8081
    }
  }
}
```

## 故障排除

**某些命令在沙箱内失败但在外部正常工作。** 以下是最常见情况的修复方法：

| 问题 | 解决方案 |
| :--- | :--- |
| 命令因 host-not-allowed 错误失败 | 在提示时授权该主机。许多 CLI 工具需要访问特定主机。 |
| `jest` 挂起或失败 | `watchman` 与沙箱不兼容。改用 `jest --no-watchman` |
| macOS 上 Go CLI 工具 TLS 验证失败 | `gh`、`gcloud`、`terraform` 等工具可能在 Seatbelt 下 TLS 验证失败。将这些工具列入 `excludedCommands` |
| macOS 上 `open`、`osascript` 或浏览器认证流程因错误 `-600` 失败 | 沙箱默认阻止 Apple Events。在用户、managed 或 CLI 设置中将 [`allowAppleEvents`](https://code.claude.com/docs/en/settings#sandbox-settings) 设为 `true`。注意：启用它会移除代码执行隔离 |
| `docker` 命令失败 | `docker` 与沙箱不兼容。添加 `docker *` 到 `excludedCommands` |
| bubblewrap 在容器内启动失败 | 在无特权容器中，bubblewrap 无法挂载新的 `/proc`。设置 [`enableWeakerNestedSandbox`](https://code.claude.com/docs/en/settings#sandbox-settings) 为 `true`。仅在外层容器已提供所需隔离边界时使用 |
| Linux 上缺少 seccomp 过滤器 | 运行 `npm install -g @anthropic-ai/sandbox-runtime` 安装 |
| 以 root 身份运行时 `--dangerously-skip-permissions` 失败 | 此标志在以 root 或 sudo 运行时被阻止。在容器中使用 [dev container](https://code.claude.com/docs/en/devcontainer) 配置（以非 root 用户运行） |

## 限制

**沙箱降低风险但不是完整的隔离边界。** 在将其作为硬安全控制依赖之前，请审查以下限制。

### 安全限制

- **网络过滤**：内置代理不终止或执行 TLS 检查。你有责任确保策略中只允许受信任的域名。

> [!WARNING]
> 允许宽泛域名（如 `github.com`）可能创建数据外泄路径。因为代理从客户端提供的主机名做允许决定而不检查 TLS，沙箱内运行的代码可能使用 [domain fronting](https://en.wikipedia.org/wiki/Domain_fronting) 等技术访问允许列表之外的主机。如果你的威胁模型需要更强保证，配置终止 TLS 并检查流量的 [自定义代理](#自定义代理配置)。

- **通过 Unix 套接字提权**：`allowUnixSockets` 配置可能无意中授予对强大系统服务的访问。例如，允许访问 `/var/run/docker.sock` 实际上通过 Docker 套接字授予了对主机系统的访问。
- **文件系统权限提权**：过宽的文件系统写权限可能启用提权攻击。允许写入 `$PATH` 中的可执行文件目录、系统配置目录或 shell 配置文件可能导致不同安全上下文中的代码执行。
- **Linux 沙箱强度**：Linux 实现提供强大的文件系统和网络隔离，但包含 `enableWeakerNestedSandbox` 模式。此选项显著削弱安全性，仅在额外隔离已由其他方式提供时使用。
- **macOS 上的 Apple Events**：macOS 沙箱默认阻止 Apple Events。`allowAppleEvents` 设置解除此限制，但移除了代码执行隔离。它仅从用户、managed 或 CLI 设置中生效，项目设置无法启用它。
- **设置文件受保护**：沙箱自动拒绝对 Claude Code 各范围 `settings.json` 文件和 managed settings 目录的写访问。

### 平台和工具兼容性

- **平台支持**：支持 macOS、Linux 和 WSL2。WSL1 和原生 Windows 不支持。
- **性能开销**：极小，但某些文件系统操作可能略慢。
- **工具兼容性**：某些需要特定系统访问模式的工具可能需要配置调整，或需要在沙箱外运行。

### 作用范围

**沙箱隔离 Bash 子进程。其他工具在不同边界下运行：**

- **内置文件工具**：Read、Edit 和 Write 直接使用权限系统而非通过沙箱运行。参见 [Permissions](https://code.claude.com/docs/en/permissions)。
- **Computer use**：当 Claude 打开应用并控制你的屏幕时，它在你的实际桌面上运行而非隔离环境中。
- **环境变量**：沙箱 Bash 命令默认继承父进程环境（包括凭证）。使用 [`sandbox.credentials`](#保护凭证) 清除特定变量，或设置 [`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`](https://code.claude.com/docs/en/env-vars) 从所有子进程剥离凭证。
- **Subagents**：[Subagents](https://code.claude.com/docs/en/sub-agents) 在与父会话相同的进程中运行，使用相同的沙箱配置。

> [!WARNING]
> 有效的沙箱需要文件系统和网络隔离同时存在。没有网络隔离，被入侵的 agent 可以外泄 SSH 密钥等敏感文件。没有文件系统隔离，被入侵的 agent 可以后门化系统资源以获取网络访问。当你放宽默认设置时，检查 `allowWrite` 路径、宽泛的 `allowedDomains` 条目或 `excludedCommands` 例外是否取消了另一侧的限制。

## 另请参阅

- [Sandbox environments](https://code.claude.com/docs/en/sandbox-environments)：比较内置沙箱与 dev container、容器和 VM
- [Security](https://code.claude.com/docs/en/security)：全面的安全特性和最佳实践
- [Permissions](https://code.claude.com/docs/en/permissions)：权限配置和访问控制
- [Settings](https://code.claude.com/docs/en/settings)：完整配置参考
- [CLI reference](https://code.claude.com/docs/en/cli-reference)：命令行选项
