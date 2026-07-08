---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】开发容器
description: 在开发容器（Dev Container）中运行 Claude Code，为团队提供一致的隔离环境。涵盖安装、认证持久化、组织策略、网络限制和无提示运行。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/devcontainer.md
  - en-source/devcontainer.md
---

# 开发容器

> 在 dev container 中运行 Claude Code，获得一致的隔离环境。

**[开发容器](https://containers.dev/)让你定义一个所有团队成员都能运行的相同隔离环境。** 在容器中安装 Claude Code 后，Claude 执行的命令在容器内运行而非宿主机上，同时对项目文件的编辑会在你的本地仓库中显示。

本页介绍[在 dev container 中安装 Claude Code](#在-dev-container-中添加-claude-code)，然后是一组独立的配置主题：跨重建持久化认证、执行组织策略、限制网络出口、无权限提示运行。按需阅读匹配你场景的部分。

> **警告**：虽然 dev container 提供了实质性保护，但没有任何系统完全免疫所有攻击。使用 `--dangerously-skip-permissions` 时，dev container 不会阻止恶意项目窃取容器内可访问的任何内容，包括 [`~/.claude`](https://code.claude.com/docs/en/claude-directory) 中存储的 Claude Code 凭据。仅在可信仓库中使用 dev container，并监控 Claude 的活动。避免将 `~/.ssh` 或云凭据文件等宿主机密钥挂载到容器中；优先使用仓库级或短期令牌。

## 在 Dev Container 中添加 Claude Code

**Claude Code 通过 [Claude Code Dev Container Feature](https://github.com/anthropics/devcontainer-features/tree/main/src/claude-code) 安装到任何 dev container 中。**

这些设置适用于任何支持 Dev Containers 规范的工具，如 VS Code、GitHub Codespaces 或 JetBrains IDE。以下步骤以 VS Code 为例。

在 VS Code 或 Codespaces 中打开容器时，Feature 还会添加 Claude Code VS Code 扩展；其他编辑器忽略此部分。

> 如果刚接触 dev containers，[VS Code Dev Containers 教程](https://code.visualstudio.com/docs/devcontainers/tutorial)介绍了 Docker 安装、扩展和首次打开容器。完整的强化示例参见[试用参考容器](#试用参考容器)。

**步骤 1：创建或更新 devcontainer.json**

将以下内容保存为仓库中的 `.devcontainer/devcontainer.json`，或将 `features` 块添加到现有文件。

末尾的版本标签（如 `:1.0`）固定的是 Feature 的安装脚本而非 Claude Code 版本。Feature 安装最新 Claude Code，且 Claude Code 默认在容器内自动更新。

```json
{
  "image": "mcr.microsoft.com/devcontainers/base:ubuntu",
  "features": {
    "ghcr.io/anthropics/devcontainer-features/claude-code:1.0": {}
  }
}
```

用你项目的基础镜像替换 `image` 行，或者如果现有文件使用 Dockerfile 则删除它。

**步骤 2：重建容器**

在 VS Code 中用 `Cmd+Shift+P`（Mac）或 `Ctrl+Shift+P`（Windows/Linux）打开命令面板，运行 **Dev Containers: Rebuild Container**。

其他工具请按各自的重建操作执行。

**步骤 3：登录 Claude Code**

在重建后的容器中打开终端运行 `claude`，按认证提示操作。

认证提示取决于你的提供商：

- **Anthropic**：通过浏览器用 Claude 或 Anthropic Console 账户登录
- **[Amazon Bedrock、Google Cloud Agent Platform 或 Microsoft Foundry](https://code.claude.com/docs/en/third-party-integrations)**：Claude Code 使用你的云提供商凭据，无浏览器提示

对于云提供商，通过 `containerEnv`、Codespaces secret 或云工作负载身份将凭据传入容器，而非从宿主机挂载凭据文件。

如果浏览器登录完成但回调未到达容器，复制浏览器中显示的代码并粘贴到终端的 `Paste code here if prompted` 提示处。这在编辑器的端口转发未路由 localhost 回调时可能发生。

## 跨重建持久化认证和设置

**默认情况下，容器的 home 目录在重建时被丢弃，工程师每次都需要重新登录。** Claude Code 将认证令牌、用户设置和会话历史存储在 [`~/.claude`](https://code.claude.com/docs/en/claude-directory) 下。在该路径挂载命名卷可跨重建保持状态。

以下示例在 `node` 用户的 home 目录挂载卷：

```json
"mounts": [
  "source=claude-code-config,target=/home/node/.claude,type=volume"
]
```

将 `/home/node` 替换为容器 `remoteUser` 的 home 目录。如果将卷挂载到 `~/.claude` 以外的位置，设置 [`CLAUDE_CONFIG_DIR`](https://code.claude.com/docs/en/env-vars) 为挂载路径。

要按项目隔离状态而非跨仓库共享一个卷，在 source 名称中包含 `${devcontainerId}` 变量。[参考配置](https://github.com/anthropics/claude-code/blob/main/.devcontainer/devcontainer.json)使用 `source=claude-code-config-${devcontainerId}`。

在 GitHub Codespaces 中，`~/.claude` 在停止和启动 codespace 时持久化，但重建容器时仍被清除，所以上面的卷挂载同样适用。要跨 codespace 携带认证，将 `ANTHROPIC_API_KEY` 或来自 [`claude setup-token`](https://code.claude.com/docs/en/authentication#generate-a-long-lived-token) 的 `CLAUDE_CODE_OAUTH_TOKEN` 存储为 [Codespaces secret](https://docs.github.com/en/codespaces/managing-your-codespaces/managing-your-account-specific-secrets-for-github-codespaces)。

## 执行组织策略

**Dev container 是应用组织策略的便捷场所，因为相同的镜像和配置运行在每个工程师的机器上。**

Claude Code 读取 Linux 上的 `/etc/claude-code/managed-settings.json` 并在[设置层级](https://code.claude.com/docs/en/settings#how-scopes-interact)中以最高优先级应用，覆盖工程师在 `~/.claude` 或项目 `.claude/` 目录中设置的任何内容。从 Dockerfile 中复制文件到位：

```dockerfile
RUN mkdir -p /etc/claude-code
COPY managed-settings.json /etc/claude-code/managed-settings.json
```

因为 Dockerfile 在仓库中，任何有写权限的人都可以更改或删除此步骤。对于工程师不能通过编辑仓库文件绕过的策略，通过[服务器托管设置](https://code.claude.com/docs/en/server-managed-settings)或 MDM 交付。

要设置适用于容器中每个 Claude Code 会话的[环境变量](https://code.claude.com/docs/en/env-vars)，在 `devcontainer.json` 中添加 `containerEnv`。以下示例退出遥测和错误报告，并阻止 Claude Code 在安装后自动更新：

```json
"containerEnv": {
  "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
  "DISABLE_AUTOUPDATER": "1"
}
```

Dev Container Feature 始终安装最新 Claude Code 版本。要固定特定版本以获得可重现构建，从 Dockerfile 中用 `npm install -g @anthropic-ai/claude-code@X.Y.Z` 安装而非使用 Feature，并如上设置 `DISABLE_AUTOUPDATER`。

完整的策略控制（包括权限规则、工具限制和 MCP 服务器白名单）参见[为组织设置 Claude Code](https://code.claude.com/docs/en/admin-setup)。

要在容器内提供 [MCP 服务器](https://code.claude.com/docs/en/mcp)，在仓库根目录的 `.mcp.json` 文件中以[项目级](https://code.claude.com/docs/en/mcp#mcp-installation-scopes)定义它们。在 Dockerfile 中安装本地 stdio 服务器依赖的所有二进制文件，并将远程服务器域名添加到网络白名单。

## 限制网络出口

**你可以将容器的出站流量限制为 Claude Code 需要的域名。** 参见[网络访问要求](https://code.claude.com/docs/en/network-config#network-access-requirements)了解推理和认证域名，[遥测服务](https://code.claude.com/docs/en/data-usage#telemetry-services)了解可选遥测连接及禁用方式。

参考容器包含一个 [`init-firewall.sh`](https://github.com/anthropics/claude-code/blob/main/.devcontainer/init-firewall.sh) 脚本，阻止除 Claude Code 和开发工具需要的域名以外的所有出站流量。在容器内运行防火墙需要额外权限，所以参考配置通过 `runArgs` 添加了 `NET_ADMIN` 和 `NET_RAW` 能力。防火墙脚本和这些能力不是 Claude Code 本身所需的：你可以省略它们而依赖自己的网络控制。

## 无权限提示运行

**因为容器以非 root 用户运行 Claude Code 并将命令执行限制在容器内，你可以传递 `--dangerously-skip-permissions` 进行无人值守操作。** CLI 在以 root 启动时拒绝此标志，所以确认 `remoteUser` 设置为非 root 账户。

跳过权限提示移除了你在工具调用运行前审查的机会。Claude 仍可修改绑定挂载工作区中的任何文件（直接出现在宿主机上），并访问容器网络策略允许的任何内容。将此标志与上面的[网络出口限制](#限制网络出口)配合使用以限制绕过会话的可达范围。

如果想减少提示但不完全禁用安全检查，考虑使用 [auto mode](https://code.claude.com/docs/en/permission-modes#eliminate-prompts-with-auto-mode)，它有分类器在操作运行前审查。要禁止工程师使用 `--dangerously-skip-permissions`，在[托管设置](https://code.claude.com/docs/en/settings#permission-settings)中将 `permissions.disableBypassPermissionsMode` 设置为 `"disable"`。

## 试用参考容器

**[`anthropics/claude-code`](https://github.com/anthropics/claude-code/tree/main/.devcontainer) 仓库包含一个示例 dev container**，组合了 CLI、出口防火墙、持久化卷和基于 Zsh 的 shell。它作为工作示例而非维护的基础镜像提供；用它了解各部分如何配合，然后应用到你自己的配置。

**步骤 1**：安装 VS Code 和 [Dev Containers 扩展](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)。

**步骤 2**：克隆 [Claude Code 仓库](https://github.com/anthropics/claude-code) 并在 VS Code 中打开。

**步骤 3**：收到提示时点击 **Reopen in Container**，或从命令面板运行 **Dev Containers: Reopen in Container**。

**步骤 4**：容器构建完成后，用 `Ctrl+`` 打开终端并运行 `claude` 登录开始第一个会话。

参考配置由三个文件组成。使用 Feature 向你自己的 dev container 添加 Claude Code 时它们都不是必需的，但展示了一种组合方式：

| 文件 | 用途 |
| :--- | :--- |
| [`devcontainer.json`](https://github.com/anthropics/claude-code/blob/main/.devcontainer/devcontainer.json) | 卷挂载、`runArgs` 能力、VS Code 扩展和 `containerEnv` |
| [`Dockerfile`](https://github.com/anthropics/claude-code/blob/main/.devcontainer/Dockerfile) | 基础镜像、开发工具和 Claude Code 安装 |
| [`init-firewall.sh`](https://github.com/anthropics/claude-code/blob/main/.devcontainer/init-firewall.sh) | 阻止除允许域名外的所有出站网络流量 |

## 后续步骤

Claude Code 在 dev container 中运行后，以下页面涵盖组织部署的其余部分：

- [为组织设置 Claude Code](https://code.claude.com/docs/en/admin-setup)：选择认证提供商、决定策略如何到达设备、规划部署
- [服务器托管设置](https://code.claude.com/docs/en/server-managed-settings)：从 Claude.ai 管理控制台交付托管策略
- [监控使用和审计活动](https://code.claude.com/docs/en/monitoring-usage)：导出 OpenTelemetry 指标并审查团队运行内容
- [网络访问要求](https://code.claude.com/docs/en/network-config#network-access-requirements)：代理和防火墙的完整域名白名单
- [遥测服务与退出](https://code.claude.com/docs/en/data-usage#telemetry-services)：Claude Code 默认发送什么及禁用的环境变量
- [探索 `.claude` 目录](https://code.claude.com/docs/en/claude-directory)：卷挂载包含什么，包括凭据、设置和会话历史
- [沙箱环境](https://code.claude.com/docs/en/sandbox-environments)：对比 dev container 与内置 Bash 沙箱、自定义容器和虚拟机
- [安全模型](https://code.claude.com/docs/en/security)：Claude Code 的权限系统、沙箱和 prompt 注入保护如何协同
- [权限模式](https://code.claude.com/docs/en/permission-modes)：从 plan mode 到 auto mode 到 bypass 的全范围
