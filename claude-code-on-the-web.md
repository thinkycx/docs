---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】Web 端使用
description: 本文介绍如何在 Web 端使用 Claude Code，包括云环境配置、Setup 脚本、网络访问控制、Docker 使用，以及通过 --remote 和 --teleport 在 Web 和终端之间切换会话。
category: translation
tags: [claude-code, web, translation]
refs: [https://code.claude.com/docs/en/claude-code-on-the-web.md]
---

# 在 Web 端使用 Claude Code

> 配置云环境、Setup 脚本、网络访问和 Docker。通过 `--remote` 和 `--teleport` 在 Web 与终端之间无缝切换会话。

> [!NOTE]
> Claude Code Web 端目前为研究预览版，面向 Pro、Max 和 Team 用户开放，Enterprise 用户需要拥有 premium 席位或 Chat + Claude Code 席位。

**Claude Code Web 端在 Anthropic 托管的云基础设施上运行任务。** 访问 [claude.ai/code](https://claude.ai/code) 即可使用。即使关闭浏览器，会话依然保持运行，你还可以通过 Claude 移动端 App 随时监控进度。

> [!TIP]
> 第一次使用？建议先阅读 [快速入门](https://code.claude.com/docs/en/web-quickstart) 连接 GitHub 账号并提交你的第一个任务。

本文涵盖以下内容：

- [GitHub 认证方式](#github-认证方式)：两种连接 GitHub 的方法
- [云环境](#云环境)：哪些配置会生效、预装了哪些工具、如何自定义环境
- [Setup 脚本](#setup-脚本)与依赖管理
- [网络访问](#网络访问)：访问级别、代理和默认白名单
- [在 Web 和终端之间切换任务](#在-web-和终端之间切换任务)：使用 `--remote` 和 `--teleport`
- [管理会话](#管理会话)：查看、分享、归档、删除
- [自动修复 Pull Request](#自动修复-pull-request)：自动响应 CI 失败和评审评论
- [安全与隔离](#安全与隔离)：会话如何被隔离
- [限制](#限制)：速率限制与平台约束

## GitHub 认证方式

**云端会话需要访问你的 GitHub 仓库来克隆代码和推送分支。** 你可以通过两种方式授权：

| 方式 | 工作原理 | 适用场景 |
| :--- | :--- | :--- |
| **GitHub App** | 在 [Web 引导流程](https://code.claude.com/docs/en/web-quickstart) 中授权 Claude GitHub App | 浏览器引导；需要[自动修复](#自动修复-pull-request)的团队 |
| **`/web-setup`** | 在终端运行 `/web-setup`，将本地 `gh` CLI token 同步到你的 Claude 账号 | 已经使用 `gh` 的独立开发者 |

> [!NOTE]
> 无论哪种方式，云端会话都能访问连接的 GitHub 账号所能看到的所有仓库，而不仅仅是安装了 Claude GitHub App 的仓库。App 安装仅用于启用 PR Webhook 以支持[自动修复](#自动修复-pull-request)，它并非会话级别的访问控制。要限制团队从云端会话能访问哪些仓库，请在 GitHub 本身进行限制，例如限制连接的 GitHub 账号的团队或仓库成员资格。

两种方式都可以。[`/schedule`](https://code.claude.com/docs/en/routines) 会检查是否有任一形式的访问权限，如果都没有则提示你运行 `/web-setup`。详见 [从终端连接](https://code.claude.com/docs/en/web-quickstart#connect-from-your-terminal) 中的 `/web-setup` 流程说明。

GitHub App 是[自动修复](#自动修复-pull-request)的必要条件，因为它使用 App 来接收 PR Webhook。如果你先通过 `/web-setup` 连接，之后又想用自动修复，需要在对应仓库上安装 App。

Team 和 Enterprise 管理员可以在 [claude.ai/admin-settings/claude-code](https://claude.ai/admin-settings/claude-code) 通过 Quick web setup 开关禁用 `/web-setup`。

> [!NOTE]
> 启用了[零数据保留](https://code.claude.com/docs/en/zero-data-retention)的组织无法使用 `/web-setup` 或其他云端会话功能。

## 云环境

**每个会话都在全新的 Anthropic 托管虚拟机中运行，你的仓库已预先克隆好。** 本节介绍会话启动时有哪些资源可用以及如何自定义。

### 云端会话中可用的内容

**云端会话从仓库的全新克隆开始。** 仓库中已提交的内容都可以使用，而只在你本地机器上安装或配置的内容不可用。组织策略通过 [服务端托管设置](https://code.claude.com/docs/en/server-managed-settings) 单独下发。

| 项目 | 是否在云端可用 | 原因 |
| :--- | :--- | :--- |
| 仓库中的 `CLAUDE.md` | 是 | 属于克隆内容 |
| 仓库中的 `.claude/settings.json` hooks | 是 | 属于克隆内容 |
| 仓库中的 `.mcp.json` MCP servers | 是 | 属于克隆内容 |
| 仓库中的 `.claude/rules/` | 是 | 属于克隆内容 |
| 仓库中的 `.claude/skills/`、`.claude/agents/`、`.claude/commands/` | 是 | 属于克隆内容 |
| 在 `.claude/settings.json` 中声明的 Plugins | 是 | 会话启动时从你声明的 [marketplace](https://code.claude.com/docs/en/plugin-marketplaces) 安装，需要网络访问 |
| 组织的[服务端托管设置](https://code.claude.com/docs/en/server-managed-settings) | 是 | 会话启动时从 Anthropic 服务器获取。通过 MDM 或托管设置文件部署到你设备的设置不适用，因为会话运行在 Anthropic 托管的 VM 上 |
| 用户目录 `~/.claude/CLAUDE.md` | 否 | 存在于你的机器上，不在仓库中 |
| 用户目录 `~/.claude/skills/`、`~/.claude/agents/`、`~/.claude/commands/` | 否 | 存在于你的机器上。应提交到仓库的 `.claude/` 目录。在 claude.ai 启用的 Skills 会自动加载到云端会话 |
| 仅在用户设置中启用的 Plugins | 否 | 用户级 `enabledPlugins` 在 `~/.claude/settings.json` 中，应改为在仓库的 `.claude/settings.json` 中声明 |
| 通过 `claude mcp add` 添加的 MCP servers | 否 | 这些写入的是本地用户配置，而非仓库。应在 [`.mcp.json`](https://code.claude.com/docs/en/mcp#project-scope) 中声明 |
| 静态 API token 和凭证 | 否 | 目前还没有专用的密钥存储 |
| 交互式认证（如 AWS SSO） | 否 | 不支持。SSO 需要浏览器登录，无法在云端会话中运行 |

要让你自己的配置在云端会话中可用，请将其提交到仓库；组织策略通过[服务端托管设置](https://code.claude.com/docs/en/server-managed-settings)单独下发。

**目前还没有专用的密钥存储。** 环境变量和 Setup 脚本都存储在环境配置中，对任何能编辑该环境的人可见。如果你需要在云端会话中使用密钥，可以将其作为环境变量添加，但要注意可见性。

### 预装工具

**云端会话预装了常见的语言运行时、构建工具和数据库。** 下表按类别列出了包含的内容：

| 类别 | 包含内容 |
| :--- | :--- |
| **Python** | Python 3.x，含 pip、poetry、uv、black、mypy、pytest、ruff |
| **Node.js** | 20、21、22（通过 nvm），含 npm、yarn、pnpm、bun¹、eslint、prettier、chromedriver |
| **Ruby** | 3.1、3.2、3.3，含 gem、bundler、rbenv |
| **PHP** | 8.4，含 Composer |
| **Java** | OpenJDK 21，含 Maven 和 Gradle |
| **Go** | 最新稳定版，支持 module |
| **Rust** | rustc 和 cargo |
| **C/C++** | GCC、Clang、cmake、ninja、conan |
| **Docker** | docker、dockerd、docker compose |
| **数据库** | PostgreSQL 16、Redis 7.0 |
| **实用工具** | git、jq、yq、ripgrep、tmux、vim、nano |

¹ Bun 已安装但存在已知的[代理兼容性问题](#通过-sessionstart-hook-安装依赖)，包获取可能受影响。

要查看确切版本号，可以在云端会话中让 Claude 运行 `check-tools` 命令。该命令仅在云端会话中可用。

### 操作 GitHub Issues 和 Pull Requests

**云端会话内置了 GitHub 工具，无需额外配置即可让 Claude 读取 Issues、列出 PR、获取 diff 和发表评论。** 这些工具通过 [GitHub 代理](#github-代理)进行认证，使用你在 [GitHub 认证方式](#github-认证方式)中配置的方法，token 不会进入容器。

`gh` CLI 并未预装。如果你需要内置工具未覆盖的 `gh` 命令（如 `gh release` 或 `gh workflow run`），需自行安装和认证：

1. **在 Setup 脚本中安装 gh**：在你的 [Setup 脚本](#setup-脚本)中添加 `apt update && apt install -y gh`
2. **提供 token**：在[环境设置](#配置你的环境)中添加 `GH_TOKEN` 环境变量，使用 GitHub 个人访问令牌。`gh` 会自动读取 `GH_TOKEN`，无需执行 `gh auth login`

### 在输出中链接回会话

**每个云端会话在 claude.ai 上都有一个 transcript URL，会话可通过 `CLAUDE_CODE_REMOTE_SESSION_ID` 环境变量读取自己的 ID。** 你可以利用这个链接放在 PR body、commit message、Slack 消息或生成的报告中，方便审阅者打开产生这些内容的运行记录。

从 v2.1.179 起，Claude 在 Web 会话中创建的 commit 会包含 `Claude-Session: <url>` git trailer，PR body 中也会包含会话 URL。从 v2.1.182 起，设置 [`attribution.sessionUrl`](https://code.claude.com/docs/en/settings#attribution-settings) 为 `false` 可以省略 trailer 和 PR body 中的链接。

如果要在 commit 或 PR 之外的地方使用会话链接（例如 Claude 发的 Slack 消息或写的报告文件），可以让 Claude 运行以下命令：

```bash
echo "https://claude.ai/code/${CLAUDE_CODE_REMOTE_SESSION_ID/#cse_/session_}"
```

### 运行测试、启动服务和添加包

**Claude 会在工作过程中运行测试。** 在提示中要求即可，比如"修复 `tests/` 中失败的测试"或"每次修改后运行 pytest"。pytest、jest、cargo test 等测试运行器已预装，无需额外配置。

PostgreSQL 和 Redis 已预装但默认未启动。可以让 Claude 在会话中启动：

```bash
service postgresql start
```

```bash
service redis-server start
```

**Docker 可用于运行容器化服务。** 让 Claude 运行 `docker compose up` 来启动项目服务。拉取镜像的网络访问遵循你的环境[访问级别](#访问级别)，[Trusted 默认白名单](#默认允许的域名)包含 Docker Hub 和其他常用注册中心。

如果镜像较大或拉取较慢，可在 [Setup 脚本](#setup-脚本)中添加 `docker compose pull` 或 `docker compose build`。拉取的镜像会保存在[缓存环境](#环境缓存)中，每个新会话都能直接使用。缓存只存储文件而非运行中的进程，所以 Claude 每次会话仍需启动容器。

要添加未预装的包，使用 [Setup 脚本](#setup-脚本)。脚本的输出会被[缓存](#环境缓存)，这样你安装的包在每次新会话开始时都可用，无需重复安装。也可以让 Claude 在会话中临时安装包，但这些安装不会保留到其他会话。

### 资源限制

**云端会话的大致资源上限如下（可能随时间调整）：**

- 4 vCPU
- 16 GB 内存
- 30 GB 磁盘

需要显著更多内存的任务（如大型构建任务或内存密集型测试）可能失败或被终止。如果工作负载超出这些限制，可使用 [Remote Control](https://code.claude.com/docs/en/remote-control) 在你自己的硬件上运行 Claude Code。

### 配置你的环境

**环境控制[网络访问](#网络访问)、环境变量和会话启动前运行的 [Setup 脚本](#setup-脚本)。** 参见[预装工具](#预装工具)了解无需配置即可使用的内容。你可以从 Web 界面或终端管理环境：

| 操作 | 方式 |
| :--- | :--- |
| 添加环境 | 选择当前环境打开选择器，然后选择 **Add environment**。对话框包含名称、网络访问级别、环境变量和 Setup 脚本 |
| 编辑环境 | 点击显示当前环境名称的云图标打开选择器，鼠标悬停在环境上，点击右侧出现的设置图标 |
| 归档环境 | 打开环境编辑界面并选择 **Archive**。已归档的环境在选择器中隐藏，但现有会话继续运行 |
| 设置 `--remote` 默认环境 | 在终端运行 `/remote-env`。如果只有一个环境，此命令显示当前配置。`/remote-env` 仅选择默认值；添加、编辑和归档环境请在 Web 界面操作 |

环境变量使用 `.env` 格式，每行一个 `KEY=value` 对。不要给值加引号，因为引号会作为值的一部分存储。示例：

```text
NODE_ENV=development
LOG_LEVEL=debug
DATABASE_URL=postgres://localhost:5432/myapp
```

## Setup 脚本

**Setup 脚本是一段在新云端会话启动时、Claude Code 启动前运行的 Bash 脚本。** 用于安装依赖、配置工具或获取会话所需的未预装内容。

脚本以 root 身份在 Ubuntu 24.04 上运行，因此 `apt install` 和大多数语言包管理器都可以使用。

要添加 Setup 脚本，打开环境设置对话框，在 **Setup script** 字段中输入脚本。

示例——安装未预装的 `gh` CLI：

```bash
#!/bin/bash
apt update && apt install -y gh
```

如果脚本以非零状态退出，会话将无法启动。对非关键命令追加 `|| true` 可避免因偶发的安装失败而阻塞会话。

**控制脚本总运行时间在大约五分钟以内**，这样[环境缓存](#环境缓存)才能正常构建。可以用 `&` 和 `wait` 并行运行独立的安装任务。如果某个下载无法在五分钟内完成，将其移到后台启动的 [SessionStart hook](#setup-脚本-vs-sessionstart-hook) 中。

> [!NOTE]
> 安装包的 Setup 脚本需要网络访问来连接注册中心。默认的 **Trusted** 网络访问允许连接[常见包注册中心](#默认允许的域名)，包括 npm、PyPI、RubyGems 和 crates.io。如果你的环境使用 **None** 网络访问，脚本将无法安装包。

### 环境缓存

**Setup 脚本在你首次在某环境中启动会话时运行。** 完成后，Anthropic 会快照文件系统，并将该快照作为后续会话的起点复用。新会话启动时依赖、工具和 Docker 镜像已在磁盘上就绪，Setup 脚本步骤被跳过。即使脚本安装了大型工具链或拉取了容器镜像，启动速度依然很快。

**缓存捕获的是文件而非运行中的进程。** Setup 脚本写入磁盘的内容会保留，但它启动的服务或容器不会。需要每个会话都启动的服务，请让 Claude 启动或使用 [SessionStart hook](#setup-脚本-vs-sessionstart-hook)。

以下情况会重新运行 Setup 脚本来重建缓存：修改了环境的 Setup 脚本或允许的网络主机，以及缓存到期（大约七天）。恢复现有会话永远不会重新运行 Setup 脚本。

你无需手动启用缓存或管理快照。

### Setup 脚本 vs. SessionStart Hook

**用 Setup 脚本安装云端需要但你笔记本已有的东西**（如语言运行时或 CLI 工具）。**用 [SessionStart hook](https://code.claude.com/docs/en/hooks#sessionstart) 做到处都该运行的项目设置**（如 `npm install`），包括云端和本地。

两者都在会话开始时运行，但归属不同：

| | Setup 脚本 | SessionStart Hook |
| :--- | :--- | :--- |
| 关联到 | 云环境 | 你的仓库 |
| 配置位置 | 云环境 UI | 仓库中的 `.claude/settings.json` |
| 运行时机 | Claude Code 启动前，仅在没有[缓存环境](#环境缓存)时运行 | Claude Code 启动后，每次会话（包括恢复的）都运行 |
| 作用范围 | 仅云环境 | 本地和云端都生效 |

SessionStart hook 也可以在本地的 `~/.claude/settings.json` 中定义，但用户级设置不会带到云端会话。在云端，hook 来源于仓库和组织的[服务端托管设置](https://code.claude.com/docs/en/server-managed-settings)。

### 通过 SessionStart Hook 安装依赖

要仅在云端会话中安装依赖，在仓库的 `.claude/settings.json` 中添加 SessionStart hook：

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/scripts/install_pkgs.sh"
          }
        ]
      }
    ]
  }
}
```

创建脚本 `scripts/install_pkgs.sh` 并用 `chmod +x` 使其可执行。云端会话中 `CLAUDE_CODE_REMOTE` 环境变量设置为 `true`，可据此跳过本地执行：

```bash
#!/bin/bash

if [ "$CLAUDE_CODE_REMOTE" != "true" ]; then
  exit 0
fi

npm install
pip install -r requirements.txt
exit 0
```

**SessionStart hook 在云端会话中的一些限制：**

- **无法仅限云端**：hook 在本地和云端会话中都会运行。要跳过本地执行，检查 `CLAUDE_CODE_REMOTE` 环境变量（如上所示）
- **需要网络访问**：安装命令需要连接包注册中心。如果环境使用 **None** 网络访问，hook 会失败。**Trusted** 下的[默认白名单](#默认允许的域名)覆盖了 npm、PyPI、RubyGems 和 crates.io
- **代理兼容性**：所有出站流量通过[安全代理](#安全代理)。某些包管理器与此代理不兼容，Bun 是一个已知的例子
- **增加启动延迟**：hook 每次会话启动或恢复时都会运行，不像 Setup 脚本有[环境缓存](#环境缓存)。保持安装脚本快速，先检查依赖是否已存在再安装

要为后续 Bash 命令持久化环境变量，请写入 `$CLAUDE_ENV_FILE` 文件。详见 [SessionStart hooks](https://code.claude.com/docs/en/hooks#sessionstart)。

目前不支持用自己的 Docker 镜像替换基础镜像。使用 Setup 脚本在[提供的镜像](#预装工具)基础上安装所需内容，或用 `docker compose` 在 Claude 旁边运行你的镜像作为容器。

## 网络访问

**网络访问控制云环境的出站连接。** 每个环境指定一个访问级别，你可以通过自定义允许的域名来扩展。默认为 **Trusted**，允许包注册中心和其他[白名单域名](#默认允许的域名)。

要更改环境的网络访问，[打开编辑界面](#配置你的环境)并在对话框中使用 **Network access** 选择器。没有单独的 Environments 页面——云图标会出现在你启动云端会话或配置 [routine](https://code.claude.com/docs/en/routines#environments-and-network-access) 的地方。

> [!NOTE]
> MCP connector 流量通过 Anthropic 服务器路由，因此你在会话或 routine 上启用的 connector 无需将其主机添加到 **Allowed domains** 就能工作。Connector 按会话或按 routine 配置；移除不需要的 connector 可以限制 Claude 能触达的工具。

### 访问级别

创建或编辑环境时选择一个访问级别：

| 级别 | 出站连接 |
| :--- | :--- |
| **None** | 无出站网络访问 |
| **Trusted** | 仅[白名单域名](#默认允许的域名)：包注册中心、GitHub、云 SDK |
| **Full** | 任何域名 |
| **Custom** | 你自己的白名单，可选择性包含默认白名单 |

GitHub 操作使用[独立的代理](#github-代理)，不受此设置影响。

### 允许特定域名

要允许不在 Trusted 列表中的域名，在环境网络访问设置中选择 **Custom**。会出现 **Allowed domains** 字段，每行输入一个域名：

```text
api.example.com
*.internal.example.com
registry.example.com
```

使用 `*.` 进行通配符子域匹配。勾选 **Also include default list of common package managers** 可以在自定义条目旁保留 [Trusted 域名](#默认允许的域名)，取消勾选则只允许你列出的域名。

### GitHub 代理

**出于安全考虑，所有 GitHub 操作通过专用代理服务，透明处理所有 git 交互。** 在沙盒内部，git 客户端使用自定义构建的范围凭证进行认证。此代理：

- 安全管理 GitHub 认证：沙盒内的 git 客户端使用范围凭证，代理验证并将其转换为你的实际 GitHub 认证 token
- 限制 git push 操作只能推送到当前工作分支
- 在维护安全边界的同时支持 clone、fetch 和 PR 操作

### 安全代理

**环境运行在 HTTP/HTTPS 网络代理后面，用于安全和防滥用。** 所有出站互联网流量都通过此代理，提供：

- 防御恶意请求
- 速率限制和防滥用
- 内容过滤增强安全
- 请求主机名的 DNS 级别审计追踪

### 默认允许的域名

使用 **Trusted** 网络访问时，以下域名默认允许。标记 `*` 的表示通配符子域匹配，例如 `*.gcr.io` 允许 `gcr.io` 的任何子域。

<details>
<summary>Anthropic 服务</summary>

- api.anthropic.com
- statsig.anthropic.com
- docs.claude.com
- platform.claude.com
- code.claude.com
- claude.ai
</details>

<details>
<summary>版本控制</summary>

- github.com
- www.github.com
- api.github.com
- npm.pkg.github.com
- raw.githubusercontent.com
- pkg-npm.githubusercontent.com
- objects.githubusercontent.com
- release-assets.githubusercontent.com
- codeload.github.com
- avatars.githubusercontent.com
- camo.githubusercontent.com
- gist.github.com
- gitlab.com
- www.gitlab.com
- registry.gitlab.com
- bitbucket.org
- www.bitbucket.org
- api.bitbucket.org
</details>

<details>
<summary>容器注册中心</summary>

- registry-1.docker.io
- auth.docker.io
- index.docker.io
- hub.docker.com
- www.docker.com
- production.cloudflare.docker.com
- download.docker.com
- gcr.io
- *.gcr.io
- ghcr.io
- mcr.microsoft.com
- *.data.mcr.microsoft.com
- public.ecr.aws
</details>

<details>
<summary>云平台</summary>

- cloud.google.com
- accounts.google.com
- gcloud.google.com
- *.googleapis.com
- storage.googleapis.com
- compute.googleapis.com
- container.googleapis.com
- azure.com
- portal.azure.com
- microsoft.com
- www.microsoft.com
- *.microsoftonline.com
- packages.microsoft.com
- dotnet.microsoft.com
- dot.net
- visualstudio.com
- dev.azure.com
- *.amazonaws.com
- *.api.aws
- oracle.com
- www.oracle.com
- java.com
- www.java.com
- java.net
- www.java.net
- download.oracle.com
- yum.oracle.com
</details>

<details>
<summary>JavaScript 和 Node 包管理器</summary>

- registry.npmjs.org
- www.npmjs.com
- www.npmjs.org
- npmjs.com
- npmjs.org
- yarnpkg.com
- registry.yarnpkg.com
</details>

<details>
<summary>Python 包管理器</summary>

- pypi.org
- www.pypi.org
- files.pythonhosted.org
- pythonhosted.org
- test.pypi.org
- pypi.python.org
- pypa.io
- www.pypa.io
</details>

<details>
<summary>Ruby 包管理器</summary>

- rubygems.org
- www.rubygems.org
- api.rubygems.org
- index.rubygems.org
- ruby-lang.org
- www.ruby-lang.org
- rubyforge.org
- www.rubyforge.org
- rubyonrails.org
- www.rubyonrails.org
- rvm.io
- get.rvm.io
</details>

<details>
<summary>Rust 包管理器</summary>

- crates.io
- www.crates.io
- index.crates.io
- static.crates.io
- rustup.rs
- static.rust-lang.org
- www.rust-lang.org
</details>

<details>
<summary>Go 包管理器</summary>

- proxy.golang.org
- sum.golang.org
- index.golang.org
- golang.org
- www.golang.org
- goproxy.io
- pkg.go.dev
</details>

<details>
<summary>JVM 包管理器</summary>

- maven.org
- repo.maven.org
- central.maven.org
- repo1.maven.org
- repo.maven.apache.org
- jcenter.bintray.com
- gradle.org
- www.gradle.org
- services.gradle.org
- plugins.gradle.org
- kotlinlang.org
- www.kotlinlang.org
- spring.io
- repo.spring.io
</details>

<details>
<summary>其他包管理器</summary>

- packagist.org (PHP Composer)
- www.packagist.org
- repo.packagist.org
- nuget.org (.NET NuGet)
- www.nuget.org
- api.nuget.org
- pub.dev (Dart/Flutter)
- api.pub.dev
- hex.pm (Elixir/Erlang)
- www.hex.pm
- cpan.org (Perl CPAN)
- www.cpan.org
- metacpan.org
- www.metacpan.org
- api.metacpan.org
- cocoapods.org (iOS/macOS)
- www.cocoapods.org
- cdn.cocoapods.org
- haskell.org
- www.haskell.org
- hackage.haskell.org
- swift.org
- www.swift.org
</details>

<details>
<summary>Linux 发行版</summary>

- archive.ubuntu.com
- security.ubuntu.com
- ubuntu.com
- www.ubuntu.com
- *.ubuntu.com
- ppa.launchpad.net
- launchpad.net
- www.launchpad.net
- *.nixos.org
</details>

<details>
<summary>开发工具与平台</summary>

- dl.k8s.io (Kubernetes)
- pkgs.k8s.io
- k8s.io
- www.k8s.io
- releases.hashicorp.com (HashiCorp)
- apt.releases.hashicorp.com
- rpm.releases.hashicorp.com
- archive.releases.hashicorp.com
- hashicorp.com
- www.hashicorp.com
- repo.anaconda.com (Anaconda/Conda)
- conda.anaconda.org
- anaconda.org
- www.anaconda.com
- anaconda.com
- continuum.io
- apache.org (Apache)
- www.apache.org
- archive.apache.org
- downloads.apache.org
- eclipse.org (Eclipse)
- www.eclipse.org
- download.eclipse.org
- nodejs.org (Node.js)
- www.nodejs.org
- developer.apple.com
- developer.android.com
- pkg.stainless.com
- binaries.prisma.sh
</details>

<details>
<summary>云服务与监控</summary>

- statsig.com
- www.statsig.com
- api.statsig.com
- sentry.io
- *.sentry.io
- downloads.sentry-cdn.com
- http-intake.logs.datadoghq.com
- *.datadoghq.com
- *.datadoghq.eu
- api.honeycomb.io
</details>

<details>
<summary>内容分发与镜像</summary>

- sourceforge.net
- *.sourceforge.net
- packagecloud.io
- *.packagecloud.io
- fonts.googleapis.com
- fonts.gstatic.com
</details>

<details>
<summary>Schema 和配置</summary>

- json-schema.org
- www.json-schema.org
- json.schemastore.org
- www.schemastore.org
</details>

<details>
<summary>Model Context Protocol</summary>

- *.modelcontextprotocol.io
</details>

## 在 Web 和终端之间切换任务

**以下工作流要求 [Claude Code CLI](https://code.claude.com/docs/en/quickstart) 已登录同一个 claude.ai 账号。** 你可以从终端启动新的云端会话，也可以将云端会话拉到终端继续本地工作。云端会话即使关闭笔记本也会持续运行，你可以从任何地方监控，包括 Claude 移动端 App。

> [!NOTE]
> 从 CLI 看，会话传递是单向的：你可以通过 `--teleport` 将云端会话拉到终端，但不能将现有的终端会话推到 Web 端。`--remote` 标志为当前仓库创建新的云端会话。[桌面应用](https://code.claude.com/docs/en/desktop#continue-in-another-surface)提供了"Continue in"菜单，可以将本地会话发送到 Web 端。

### 从终端到 Web

使用 `--remote` 标志从命令行启动云端会话：

```bash
claude --remote "Fix the authentication bug in src/auth/login.ts"
```

这会在 claude.ai 上创建一个新的云端会话。会话会克隆你当前目录的 GitHub remote 和当前分支，因此如果有本地提交请先 push——VM 从 GitHub 克隆而非你的机器。`--remote` 一次只能处理一个仓库。任务在云端运行，你可以继续本地工作。

> [!NOTE]
> `--remote` 创建云端会话。`--remote-control` 是另一个不相关的功能：它将本地 CLI 会话暴露给 Web 端监控。详见 [Remote Control](https://code.claude.com/docs/en/remote-control)。

使用 Claude Code CLI 中的 `/tasks` 查看进度，或在 claude.ai 或 Claude 移动端 App 上打开会话直接交互。在那里你可以引导 Claude、提供反馈或回答问题，就像任何其他对话一样。

#### 云端任务技巧

**本地规划，远程执行**：对于复杂任务，先用 plan mode 协作确定方案，再发送到云端执行：

```bash
claude --permission-mode plan
```

在 plan mode 中，Claude 读取文件、运行命令探索，并提出计划但不编辑源代码。满意后，将计划保存到仓库，commit 并 push，这样云端 VM 才能克隆到。然后启动云端会话进行自主执行：

```bash
claude --remote "Execute the migration plan in docs/migration-plan.md"
```

这种模式让你掌控策略，同时让 Claude 在云端自主执行。

**在云端用 ultraplan 做规划**：要在 Web 会话中起草和评审计划，使用 [ultraplan](https://code.claude.com/docs/en/ultraplan)。Claude 在 Web 端生成计划，你继续工作，然后在浏览器中对各部分评论，选择远程执行或将计划发回终端。

**并行运行任务**：每个 `--remote` 命令创建独立的云端会话。你可以启动多个任务，它们会在不同会话中同时运行：

```bash
claude --remote "Fix the flaky test in auth.spec.ts"
claude --remote "Update the API documentation"
claude --remote "Refactor the logger to use structured output"
```

用 Claude Code CLI 中的 `/tasks` 监控所有会话。会话完成后，可以从 Web 界面创建 PR，或 [teleport](#从-web-到终端) 会话到终端继续工作。

#### 发送本地仓库（无 GitHub）

**当你从未连接 GitHub 的仓库运行 `claude --remote` 时，Claude Code 会打包本地仓库并直接上传到云端会话。** 打包内容包含所有分支的完整仓库历史，以及已跟踪文件的未提交更改。

当 GitHub 访问不可用时自动启用此回退。要强制使用（即使已连接 GitHub），设置 `CCR_FORCE_BUNDLE=1`：

```bash
CCR_FORCE_BUNDLE=1 claude --remote "Run the test suite and fix any failures"
```

打包仓库必须满足以下限制：

- 目录必须是一个有至少一次 commit 的 git 仓库
- 打包后大小须低于 100 MB。超过时会依次回退为只打包当前分支、单个压缩的工作树快照，只有快照仍然过大时才会失败
- 未跟踪的文件不包含在内；对需要云端会话看到的文件运行 `git add`
- 从打包创建的会话不能推送回 remote，除非你也配置了 [GitHub 认证](#github-认证方式)

### 从 Web 到终端

使用以下任一方式将云端会话拉到终端：

- **使用 `--teleport`**：命令行运行 `claude --teleport` 打开交互式会话选择器，或 `claude --teleport <session-id>` 直接恢复特定会话。如有未提交更改，会提示你先 stash
- **使用 `/teleport`**：在已有的 CLI 会话中运行 `/teleport` 或 `/tp` 打开相同的会话选择器，无需重启 Claude Code
- **从 `/tasks`**：运行 `/tasks` 查看后台会话，然后按 `t` teleport 进入
- **从 Web 界面**：选择 **Open in CLI** 复制一条可粘贴到终端的命令

Teleport 会话时，Claude 会验证你在正确的仓库中，从云端会话获取并切换到对应分支，将完整对话历史加载到终端。

`--teleport` 和 `--resume` 不同。`--resume` 重新打开本机本地历史中的对话，不列出云端会话；`--teleport` 拉取云端会话及其分支。

#### Teleport 要求

Teleport 在恢复会话前检查以下要求。如不满足，会看到错误提示或被引导解决：

| 要求 | 详情 |
| :--- | :--- |
| 干净的 git 状态 | 工作目录不能有未提交的更改。Teleport 会提示你 stash 更改 |
| 正确的仓库 | 必须从同一仓库的 checkout 运行 `--teleport`，不能是 fork |
| 分支可用 | 云端会话的分支必须已推送到 remote。Teleport 会自动 fetch 并 checkout |
| 同一账号 | 必须认证到云端会话使用的同一 claude.ai 账号 |

#### `--teleport` 不可用的情况

Teleport 需要 claude.ai 订阅认证。如果你通过 API key、Bedrock、Vertex AI 或 Microsoft Foundry 认证，运行 `/login` 改用你的 claude.ai 账号登录。如果已通过 claude.ai 登录但 `--teleport` 仍不可用，可能是你的组织禁用了云端会话。

## 管理会话

**会话显示在 claude.ai/code 的侧边栏中。** 你可以在那里查看变更、与队友分享、归档已完成的工作，或永久删除会话。

### 管理上下文

云端会话支持产生文本输出的[内置命令](https://code.claude.com/docs/en/commands)。打开交互式终端选择器的命令（如 `/model` 或 `/config`）不可用。

上下文管理方面：

| 命令 | 云端会话中可用 | 说明 |
| :--- | :--- | :--- |
| `/compact` | 是 | 总结对话以释放上下文空间。接受可选的聚焦指令，如 `/compact keep the test output` |
| `/context` | 是 | 显示当前上下文窗口中的内容 |
| `/clear` | 否 | 改为从侧边栏启动新会话 |

上下文窗口接近容量时会自动触发 auto-compaction。要提前触发，在[环境变量](#配置你的环境)中设置 [`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`](https://code.claude.com/docs/en/env-vars)。例如 `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=70` 会在 70% 容量时压缩，而不是等窗口接近满。要更改压缩计算使用的有效窗口大小，使用 [`CLAUDE_CODE_AUTO_COMPACT_WINDOW`](https://code.claude.com/docs/en/env-vars)。

[Subagents](https://code.claude.com/docs/en/sub-agents) 的工作方式与本地相同。Claude 可通过 Task 工具生成 subagent，将研究或并行工作卸载到独立的上下文窗口，保持主对话轻量。仓库 `.claude/agents/` 中定义的 agent 会自动识别。

[Agent teams](https://code.claude.com/docs/en/agent-teams) 默认关闭，可通过在[环境变量](#配置你的环境)中添加 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 启用。

### 查看变更

**每个会话显示一个 diff 指示器，标注添加和删除的行数**（如 `+42 -18`）。点击它打开 diff 视图，在特定行留下内联评论，并在下条消息中发送给 Claude。详见 [查看和迭代](https://code.claude.com/docs/en/web-quickstart#review-and-iterate) 的完整流程（包括 PR 创建）。要让 Claude 自动监控 PR 的 CI 失败和评审评论，详见[自动修复 Pull Request](#自动修复-pull-request)。

### 分享会话

**要分享会话，根据下面的账号类型切换其可见性。** 之后直接分享会话链接即可。接收者打开链接时看到最新状态，但其视图不会实时更新。

#### 从 Enterprise 或 Team 账号分享

Enterprise 和 Team 账号有两个可见性选项：**Private** 和 **Team**。Team 可见性使会话对 claude.ai 组织的其他成员可见。[Claude in Slack](https://code.claude.com/docs/en/slack) 会话会自动以 Team 可见性分享。

默认启用仓库访问验证，基于接收者账号连接的 GitHub 账号。你的账号显示名称对所有有权限的接收者可见。

#### 从 Max 或 Pro 账号分享

Max 和 Pro 账号有两个可见性选项：**Private** 和 **Public**。Public 可见性使会话对任何登录 claude.ai 的用户可见。

分享前检查会话中是否有敏感内容。会话可能包含私有 GitHub 仓库的代码和凭证。默认不启用仓库访问验证。

要求接收者拥有仓库访问权限，或在分享会话时隐藏你的姓名，请前往 Settings > Claude Code > Sharing settings。

### 归档会话

**你可以归档会话来保持会话列表整洁。** 已归档的会话从默认列表中隐藏，但可以通过筛选归档会话来查看。

要归档会话，将鼠标悬停在侧边栏中的会话上，点击归档图标。

### 删除会话

**删除会话会永久移除会话及其数据，此操作不可撤销。** 可通过两种方式删除：

- **从侧边栏**：筛选归档会话，将鼠标悬停在要删除的会话上，点击删除图标
- **从会话菜单**：打开会话，点击会话标题旁的下拉菜单，选择 **Delete**

删除前会要求确认。

## 自动修复 Pull Request

**Claude 可以监控 Pull Request，自动响应 CI 失败和评审评论。** Claude 订阅 PR 上的 GitHub 活动，当检查失败或审阅者留下评论时，Claude 会调查并在情况明确时推送修复。

> [!NOTE]
> 自动修复需要在你的仓库上安装 Claude GitHub App。如果还没有安装，可以从 [GitHub App 页面](https://github.com/apps/claude) 或在[设置流程](https://code.claude.com/docs/en/web-quickstart#connect-github-and-create-an-environment)中安装。

根据 PR 的来源和你使用的设备，有几种方式开启自动修复：

- **在 Claude Code Web 端创建的 PR**：打开 CI 状态栏并选择 **Auto-fix**
- **从终端**：在 PR 所在分支运行 [`/autofix-pr`](https://code.claude.com/docs/en/commands)。Claude Code 通过 `gh` 检测开放的 PR，生成一个 Web 会话并一步开启自动修复
- **从移动端 App**：告诉 Claude 自动修复该 PR，例如"watch this PR and fix any CI failures or review comments"
- **任何现有 PR**：将 PR URL 粘贴到会话中并告诉 Claude 自动修复

自动修复是逐 PR 的开关。要停止监控，打开 Web 会话中的 CI 状态栏并清除 **Auto-fix** 开关，或告诉 Claude 停止监控 PR。

### Claude 如何响应 PR 活动

**自动修复激活后，Claude 接收 PR 的 GitHub 事件**，包括新的评审评论和 CI 检查失败。对于每个事件，Claude 会调查并决定如何处理：

- **明确的修复**：如果 Claude 对修复有信心且不与先前指令冲突，会直接修改、推送并在会话中解释
- **模糊的请求**：如果评审者的评论有多种解读方式或涉及架构重要事项，Claude 会先问你再行动
- **重复或无需操作的事件**：如果事件是重复的或不需要修改，Claude 在会话中记录并继续

GitHub 不会在 base 分支前进导致合并冲突时发出 webhook，因此自动修复无法自行处理冲突。要解决冲突，打开会话让 Claude rebase。

Claude 可能会回复 GitHub 评审评论来表示已解决。这些回复使用你的 GitHub 账号发布，因此显示在你的用户名下，但每条回复都标记为来自 Claude Code，方便审阅者知道是 agent 而非你本人直接撰写的。

> [!WARNING]
> 如果你的仓库使用评论触发的自动化（如 Atlantis、Terraform Cloud 或基于 `issue_comment` 事件的自定义 GitHub Actions），请注意 Claude 可以代表你回复评论，这可能触发这些工作流。启用自动修复前请审查仓库的自动化配置，对于 PR 评论可以部署基础设施或运行特权操作的仓库，考虑禁用自动修复。

## 安全与隔离

**每个云端会话通过多个层面与你的机器及其他会话隔离：**

- **隔离的虚拟机**：每个会话运行在独立的 Anthropic 托管 VM 中
- **网络访问控制**：默认限制网络访问，可以禁用。禁用网络访问时，Claude Code 仍可与 Anthropic API 通信，这意味着数据可能离开 VM
- **凭证保护**：敏感凭证（如 git 凭证或签名密钥）不会进入 Claude Code 所在的沙盒。认证通过范围凭证的安全代理处理
- **安全分析**：代码在隔离 VM 中被分析和修改，然后才创建 PR

## 故障排除

对于对话中出现的运行时 API 错误（如 `API Error: 500`、`529 Overloaded`、`429` 或 `Prompt is too long`），参见[错误参考](https://code.claude.com/docs/en/errors)。这些错误及修复方法与 CLI 和桌面应用共享。以下部分涵盖云端会话特有的问题。

### 会话创建失败

**如果新会话启动时出现 `Session creation failed` 或卡在 provisioning 阶段，说明 Claude Code 无法分配云环境。**

- 检查 [status.claude.com](https://status.claude.com) 是否有云端会话故障
- 等一分钟后重试，因为容量是按需配置的
- 确认你的仓库可达。连接的 GitHub 账号必须能在 GitHub 上访问该仓库（通过 Claude GitHub App 授权或通过 `/web-setup` 同步的 `gh` token）。在仓库上安装 App 不是必需的。参见 [GitHub 认证方式](#github-认证方式)

### Remote Control 会话过期或访问被拒绝

**`--teleport` 使用与云端会话相同的 Remote Control 会话基础设施连接**，因此认证和会话过期错误会以 Remote Control 相关的措辞显示。你可能看到 `Remote Control session expired` 或 `Access denied`。连接 token 是短期的且绑定到你的账号。

- 在本地运行 `/login` 刷新凭证，然后重新连接
- 确认你登录的是拥有该会话的同一账号
- 如果看到 `Remote Control may not be available for this organization`，说明管理员未为你的组织启用云端会话

### 环境过期

**云端会话在一段时间不活跃后停止，底层环境被回收。** 从本地终端看，这表现为 `Could not resume session ... its environment has expired. Creating a fresh session instead.`。在 Web 端，会话在列表中标记为 expired。

在 [claude.ai/code](https://claude.ai/code) 重新打开会话可配置新环境并恢复你的对话历史。

## 限制

**在依赖云端会话处理工作流之前，请考虑以下约束：**

- **速率限制**：Claude Code Web 端与账号内所有其他 Claude 和 Claude Code 使用共享速率限制。并行运行多个任务会成比例消耗更多配额。云端 VM 没有单独的计算费用
- **仓库认证**：只有认证到同一账号时才能将会话从 Web 转移到本地
- **平台限制**：仓库克隆和 PR 创建需要 GitHub。自托管的 [GitHub Enterprise Server](https://code.claude.com/docs/en/github-enterprise-server) 实例支持 Team 和 Enterprise 计划。GitLab、Bitbucket 和其他非 GitHub 仓库可以作为[本地打包](#发送本地仓库无-github)发送到云端会话，但会话无法将结果推回 remote
- **组织 IP 白名单**：云端会话从 Anthropic 托管的基础设施调用 Anthropic API，而非你的网络。如果你的组织启用了 [IP 白名单](https://support.claude.com/en/articles/13200993-restrict-access-to-claude-with-ip-allowlisting)，每个云端会话都会因认证错误而失败。[Code Review](https://code.claude.com/docs/en/code-review) 和 [Routines](https://code.claude.com/docs/en/routines) 同理。联系 [Anthropic 支持](https://support.claude.com/)将 Anthropic 托管的服务从组织的 IP 白名单中豁免

## 相关资源

- [Ultraplan](https://code.claude.com/docs/en/ultraplan)：在云端会话中起草计划并在浏览器中审阅
- [Ultrareview](https://code.claude.com/docs/en/ultrareview)：在云端沙盒中运行深度多 agent 代码审查
- [Routines](https://code.claude.com/docs/en/routines)：按计划、通过 API 调用或响应 GitHub 事件自动化工作
- [Hooks 配置](https://code.claude.com/docs/en/hooks)：在会话生命周期事件时运行脚本
- [Settings 参考](https://code.claude.com/docs/en/settings)：所有配置选项
- [安全](https://code.claude.com/docs/en/security)：隔离保证和数据处理
- [数据使用](https://code.claude.com/docs/en/data-usage)：Anthropic 从云端会话保留哪些数据
- [Claude Tag](https://claude.com/docs/claude-tag/overview)：运行在相同云环境上的组织管理的 @Claude in Slack
