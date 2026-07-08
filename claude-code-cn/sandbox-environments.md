---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】沙箱环境
description: 比较 Claude Code 的各种沙箱隔离方案（内置 Bash 沙箱、沙箱运行时、Dev Container、Docker 容器、虚拟机、Web 版），帮助你根据威胁模型选择合适的隔离级别。
category: translation
tags: [claude-code, sandbox-environments, translation]
refs:
  - https://code.claude.com/docs/en/sandbox-environments.md
  - en-source/sandbox-environments.md
---

# 选择沙箱环境

**隔离 Claude Code 限制了会话可以读写和访问网络的范围。** 当你让 Claude 以更少权限提示运行、无人值守运行、或指向不完全信任的代码时，这尤其重要。

Claude Code 可以运行在从轻量级逐命令沙箱到完全独立虚拟机的多种隔离环境中。本页比较各方案的隔离范围和要求，帮助你根据威胁模型选择。

## 方案对比

| 方案 | 隔离什么 | 需要 Docker | 设置成本 |
|------|---------|------------|---------|
| [内置 Bash 沙箱](#内置-bash-沙箱) | Bash 命令及其子进程 | 否 | macOS 最低；Linux/WSL2 低 |
| [沙箱运行时](#沙箱运行时) | 整个 Claude Code 进程（含文件工具、MCP、hooks） | 否 | 低 |
| [Dev Container](#dev-container) | 完整开发环境 | 是 | 中 |
| [自定义容器](#自定义容器) | 完整开发环境 | 是 | 中到高 |
| [虚拟机](#虚拟机) | 完整操作系统 | 否 | 高 |
| [Claude Code Web 版](#claude-code-web-版) | 完整操作系统（Anthropic 托管） | 否 | 无；需 Claude 订阅和 GitHub |

**内置 Bash 沙箱仅限制 Bash 命令。** 内置文件工具、MCP 服务器和 hooks 仍直接在宿主上运行。表中其他所有方案将整个 Claude Code 进程放在隔离边界内。

> 沙箱隔离降低漏洞影响，但不消除风险。任何允许网络出站的方案仍可泄露 agent 能读到的数据；任何以可写方式挂载项目目录的方案仍可修改代码。隔离也不改变发送给模型的内容。见 [Data usage](https://code.claude.com/docs/en/data-usage)。

## 选择方案

| 你想要 | 建议从这里开始 |
|-------|-------------|
| 日常工作中减少权限提示 | 内置 [Bash 沙箱](https://code.claude.com/docs/en/sandboxing)，用 `/sandbox` 启用 |
| 用 `--dangerously-skip-permissions` 或 auto 模式无人值守运行 | 预配置 [Dev Container](https://code.claude.com/docs/en/devcontainer)、容器/VM、或沙箱运行时 |
| 隔离 MCP 和 hooks（不用 Docker） | 沙箱运行时 |
| 在不信任的仓库上工作 | 专用虚拟机，或 [Claude Code Web 版](https://code.claude.com/docs/en/claude-code-on-the-web) |
| 跨团队标准化沙箱环境 | 预配置 Dev Container，复制到仓库 |
| 无本地设置的设备使用 Claude Code | Claude Code Web 版 |
| 为组织每个开发者强制隔离 | 见下方"跨组织强制隔离" |
| 原生 Windows 主机 | 容器/VM，或在 WSL2 内运行 Bash 沙箱 |

### 隔离与权限模式的关系

**权限模式决定工具调用是否运行及是否提示。隔离限制命令运行后能访问什么。** 两者协同工作。

- `--dangerously-skip-permissions` 移除逐操作审查，隔离边界是唯一限制。务必在容器、VM 或沙箱运行时内运行
- [Auto 模式](https://code.claude.com/docs/en/permission-modes#eliminate-prompts-with-auto-mode) 用分类器替代提示审查操作，隔离边界仍增加纵深防御，但非必需

## 内置 Bash 沙箱

**内置于 Claude Code 中，使用操作系统原语限制每个 Bash 命令的文件系统和网络访问。** macOS 用 Seatbelt，Linux/WSL2 用 [bubblewrap](https://github.com/containers/bubblewrap)。

用 `/sandbox` 命令启用。默认允许写入工作目录，命令首次需要新网络域时提示。

不覆盖的部分：
- Read、Edit、WebFetch 等内置工具在 Claude Code 进程内运行，不启动任意代码
- MCP 服务器和 hooks 是独立进程，在宿主上无约束运行

> 不支持原生 Windows。Windows 主机请用 WSL2 或容器/VM。

## 沙箱运行时

**[`@anthropic-ai/sandbox-runtime`](https://github.com/anthropic-experimental/sandbox-runtime) 包将整个进程包裹在与内置 Bash 沙箱相同的 Seatbelt/bubblewrap 隔离中。**

运行时默认拒绝所有写入和网络访问，需在 `~/.srt-settings.json` 中配置至少允许项目目录和 `~/.claude` 的写访问，以及 `api.anthropic.com` 的网络访问。

```bash
npx @anthropic-ai/sandbox-runtime claude
```

## Dev Container

**在 Docker 容器内运行 Claude Code，VS Code 或兼容编辑器管理，项目挂载在内。**

Claude Code 仓库发布了一个[示例 Dev Container](https://code.claude.com/docs/en/devcontainer)，带默认拒绝的 iptables 防火墙。复制到仓库并调整防火墙白名单、基础镜像和 Claude Code 版本。

## 自定义容器

**在任何 Docker/OCI 容器镜像中运行 Claude Code，使用你自己的网络策略、挂载卷和 seccomp 配置。**

可以在容器内叠加内置 Bash 沙箱做逐命令限制。非特权容器需要嵌套沙箱设置，见 [Sandboxing troubleshooting](https://code.claude.com/docs/en/sandboxing#troubleshooting)。

## 虚拟机

**专用虚拟机提供最强隔离：独立内核，在云/microVM 部署中有独立虚拟化硬件。**

适用场景：评估不信任的代码、安全策略要求内核级别隔离、或无主机级方案满足合规要求时。Docker Desktop 的 sandboxes 功能提供带自己 Docker daemon 和工作区同步的 microVM。

## Claude Code Web 版

**[Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web) 在隔离的 Anthropic 管理虚拟机中运行每个会话。** 网络代理强制默认白名单，独立代理在沙箱外持有 GitHub token 并在内部签发作用域凭据。

需要 Claude 订阅和连接的 GitHub 账户。会话从 GitHub 克隆仓库。

## 跨组织强制隔离

| 方案 | 强制机制 |
|------|---------|
| 内置 Bash 沙箱 | Claude Code 自身强制。通过管理设置 ([managed settings](https://code.claude.com/docs/en/settings#settings-files)) 下发 `sandbox` 设置键 |
| Dev Container | 将示例 Dev Container 提交到仓库以标准化。这是约定而非强制边界 |
| 自定义容器/VM | 通过批准镜像分发 Claude Code，用设备管理工具阻止在外部安装 |

## 另见

- [Sandboxing](https://code.claude.com/docs/en/sandboxing) — 配置内置 Bash 沙箱
- [Dev container](https://code.claude.com/docs/en/devcontainer) — 预配置 Docker 开发容器
- [Security](https://code.claude.com/docs/en/security) — 完整 Claude Code 安全模型
- [Secure deployment](https://code.claude.com/docs/en/agent-sdk/secure-deployment) — Agent SDK 应用隔离指南
- [Settings](https://code.claude.com/docs/en/settings#sandbox-settings) — 所有沙箱配置键
