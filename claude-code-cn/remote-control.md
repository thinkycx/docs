---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】Remote Control 远程控制
description: Claude Code Remote Control 功能指南。让你从手机、平板或任何浏览器继续本地 Claude Code 会话，Claude 始终在本地机器上运行，web 和移动端只是本地会话的一个窗口。支持多设备同步、网络中断自动重连、服务器模式多并发会话。
category: translation
tags: [claude-code, remote-control, translation]
refs: [https://code.claude.com/docs/en/remote-control.md]
---

# 用 Remote Control 从任何设备继续本地会话

**Remote Control 将 claude.ai/code 或 Claude 移动应用连接到你机器上运行的 Claude Code 会话。在桌前启动任务，然后在沙发上用手机或另一台电脑的浏览器继续操作。Claude 始终在本地运行，不会迁移到云端。**

> [!NOTE]
> Remote Control 处于研究预览阶段，所有计划均可使用。在 Team 和 Enterprise 上默认关闭，需要 Owner 在 [Claude Code 管理设置](https://claude.ai/admin-settings/claude-code) 中启用 Remote Control 开关。

Remote Control 将 [claude.ai/code](https://claude.ai/code) 或 Claude [iOS](https://apps.apple.com/us/app/claude-by-anthropic/id6473753684) / [Android](https://play.google.com/store/apps/details?id=com.anthropic.claude) 应用连接到你机器上运行的 Claude Code 会话。在桌前启动任务，然后在沙发上用手机或另一台电脑的浏览器接手。

**启动 Remote Control 会话后，Claude 始终在本地运行，不会迁移到云端。** 你可以：

- **远程使用完整的本地环境**：文件系统、[MCP 服务器](https://code.claude.com/docs/en/mcp)、工具和项目配置全部可用，输入 `@` 可自动补全本地项目的文件路径
- **同时在多个界面操作**：对话跨所有连接设备保持同步，你可以在终端、浏览器和手机间交替发消息
- **经受中断**：如果笔记本休眠或网络断开，机器重新上线后会话会自动重连

不同于 [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web)（运行在云端基础设施上），Remote Control 会话直接在你的机器上运行并与本地文件系统交互。Web 和移动端界面只是本地会话的一个窗口。

> [!NOTE]
> Remote Control 需要 Claude Code v2.1.51 或更高版本。使用 `claude --version` 检查版本。

## 前置条件

| 条件 | 说明 |
| :--- | :--- |
| 订阅 | Pro、Max、Team 和 Enterprise 计划可用。不支持 API Key。Team 和 Enterprise 需要 Owner 先在 [管理设置](https://claude.ai/admin-settings/claude-code) 中启用 Remote Control 开关 |
| 认证 | 运行 `claude` 并使用 `/login` 通过 claude.ai 登录（如果尚未登录） |
| 工作区信任 | 至少在项目目录中运行过一次 `claude` 以接受工作区信任对话框 |

## 启动 Remote Control 会话

**你可以从 CLI 或 VS Code 扩展启动 Remote Control 会话。** CLI 提供三种调用模式；VS Code 使用 `/remote-control` 命令。

### 服务器模式

导航到你的项目目录并运行：

```bash
claude remote-control
```

进程在终端中以服务器模式持续运行，等待远程连接。它会显示一个会话 URL 供你 [从另一台设备连接](#从另一台设备连接)，按空格键可以显示 QR 码快速从手机访问。远程会话活跃时，终端显示连接状态和工具活动。

**可用 flag：**

| Flag | 说明 |
| :--- | :--- |
| `--name "My Project"` | 设置自定义会话标题，在 claude.ai/code 的会话列表中可见 |
| `--remote-control-session-name-prefix <prefix>` | 未设置显式名称时自动生成会话名的前缀。默认为机器的主机名，生成如 `myhost-graceful-unicorn` 的名称。也可用环境变量 `CLAUDE_REMOTE_CONTROL_SESSION_NAME_PREFIX` |
| `--spawn <mode>` | 服务器如何创建会话：<br/>- `same-dir`（默认）：所有会话共享当前工作目录，编辑同一文件时可能冲突<br/>- `worktree`：每个按需会话获得自己的 [git worktree](https://code.claude.com/docs/en/worktrees)，需要 git 仓库<br/>- `session`：单会话模式，仅服务一个会话并拒绝额外连接。仅在启动时设置<br/>运行时按 `w` 可在 `same-dir` 和 `worktree` 间切换 |
| `--capacity <N>` | 最大并发会话数。默认 32。不能与 `--spawn=session` 一起使用 |
| `--verbose` | 显示详细的连接和会话日志 |
| `--sandbox` / `--no-sandbox` | 启用或禁用 [沙箱](https://code.claude.com/docs/en/sandboxing) 以实现文件系统和网络隔离。默认关闭 |

### 交互式会话

**要启动启用了 Remote Control 的正常交互式 Claude Code 会话，使用 `--remote-control` flag（或 `--rc`）：**

```bash
claude --remote-control
```

可选地传入会话名称：

```bash
claude --remote-control "My Project"
```

这给你一个完整的终端交互式会话，同时也可以从 claude.ai 或 Claude 应用远程控制。与 `claude remote-control`（服务器模式）不同，你可以在会话也远程可用时在本地输入消息。

### 从已有会话中启用

如果你已经在 Claude Code 会话中，想从远程继续，使用 `/remote-control`（或 `/rc`）命令：

```text
/remote-control
```

传入名称作为参数可设置自定义会话标题：

```text
/remote-control My Project
```

这会启动一个 Remote Control 会话，保留当前对话历史。

`--verbose`、`--sandbox` 和 `--no-sandbox` flag 在此命令中不可用。

### VS Code

在 [Claude Code VS Code 扩展](https://code.claude.com/docs/en/vs-code) 中，在提示框中输入 `/remote-control` 或 `/rc`，或使用 `/` 打开命令菜单并选择它。需要 Claude Code v2.1.79 或更高版本。

```text
/remote-control
```

提示框上方出现横幅显示连接状态。连接后，点击横幅中的 **Open in browser** 直接跳转到会话，或在 [claude.ai/code](https://claude.ai/code) 的会话列表中找到它。会话 URL 也会发布在对话中。

要断开连接，点击横幅上的关闭图标或再次运行 `/remote-control`。

与 CLI 不同，VS Code 命令不接受名称参数或显示 QR 码。会话标题由对话历史或第一条 prompt 生成。

### 检查连接状态

在交互式终端会话中，连接正常时输入框下方的页脚会显示 `/rc active` 指示器（终端太窄时隐藏）。指示器文本是指向 claude.ai 上会话的链接。用向下箭头键选中它并按回车，或再次运行 `/remote-control`，可打开状态面板显示会话 URL 和 QR 码。

如果连接失败，会出现通知显示失败原因，指示器从页脚消失。再次运行 `/remote-control` 重试。

### 从另一台设备连接

**Remote Control 会话活跃后，你有几种方式从另一台设备连接：**

- **打开会话 URL**：在任何浏览器中打开，直接跳转到 [claude.ai/code](https://claude.ai/code) 上的会话
- **扫描 QR 码**：扫描会话 URL 旁边显示的 QR 码，直接在 Claude 应用中打开。使用 `claude remote-control` 时按空格键切换 QR 码显示
- **打开 claude.ai/code 或 Claude 应用**：在会话列表中按名称找到会话。在 Claude 移动应用中，点击导航中的 **Code** 进入会话列表。Remote Control 会话在线时显示带绿色状态点的电脑图标

**远程会话标题按以下顺序选择：**

1. 你传给 `--name`、`--remote-control` 或 `/remote-control` 的名称
2. 你用 `/rename` 设置的标题
3. 现有对话历史中最后一条有意义的消息
4. 自动生成的名称如 `myhost-graceful-unicorn`，其中 `myhost` 是机器主机名或你用 `--remote-control-session-name-prefix` 设置的前缀

如果没有设置显式名称，发送 prompt 后标题会更新以反映你的提问。自 Claude Code v2.1.176 起，自动生成的标题匹配你的对话语言，或已配置的 [`language`](https://code.claude.com/docs/en/settings#available-settings) 设置。从 claude.ai 或 Claude 应用重命名会话也会更新 `claude --resume` 中显示的本地标题。

如果环境中已有活跃会话，会询问你是继续还是启动新会话。

如果你还没有 Claude 应用，在 Claude Code 中使用 `/mobile` 命令显示 [iOS](https://apps.apple.com/us/app/claude-by-anthropic/id6473753684) 或 [Android](https://play.google.com/store/apps/details?id=com.anthropic.claude) 的下载 QR 码。

### 为所有会话启用 Remote Control

**默认情况下，Remote Control 仅在显式运行 `claude remote-control`、`claude --remote-control` 或 `/remote-control` 时激活。** 要为每个交互式会话自动启用，在 Claude Code 中运行 `/config` 并将 **Enable Remote Control for all sessions** 设置为 `true`。设回 `false` 可禁用。在 Desktop 应用中，也可从 **Settings → Claude Code → Enable remote control by default** 切换。

启用此设置后，每个交互式 Claude Code 进程注册一个远程会话。如果运行多个实例，每个实例获得自己的环境和会话。要从单个进程运行多个并发会话，使用 [服务器模式](#服务器模式)。

## 连接与安全

**你的本地 Claude Code 会话仅发出 HTTPS 出站请求，从不在机器上打开入站端口。** 启动 Remote Control 时，它向 Anthropic API 注册并轮询工作。从另一台设备连接时，服务器通过流式连接在 web/移动客户端和你的本地会话之间路由消息。

所有流量通过 Anthropic API over TLS 传输，与任何 Claude Code 会话使用相同的传输安全。连接使用多个短期凭据，每个凭据限定于单一用途并独立过期。

## Trusted Devices（可信设备）

> [!NOTE]
> Trusted Devices 目前处于 beta 阶段，功能可能会随迭代变化。
>
> Trusted Devices 在 Team 和 Enterprise 计划上可用，默认关闭直到管理员启用。

**Trusted Devices 是一个组织级设置，要求成员在从 claude.ai、Claude 移动应用或 Claude Desktop 查看或操控 Remote Control 会话之前验证其设备。** 它将 Remote Control 访问绑定到已知设备和近期认证，而不仅仅是已登录的账户。

启用此设置后，与 Remote Control 会话交互需要同时满足：

- **已注册设备**：每个用于 Remote Control 的浏览器、手机或桌面应用注册自己的凭据。注册仅在完整登录后不久提供，因此设备作为真实认证的一部分加入可信列表
- **近期登录**：成员的登录不超过 18 小时。无需每天重新登录，成员通过 Face ID、Touch ID、Windows Hello 或 passkey 确认在场。此生物识别验证立即刷新会话

生物识别检查通过操作系统或浏览器在设备上运行，与 passkey 登录使用相同的机制。Anthropic 从不接收或存储指纹、面部数据或任何其他生物识别信息。仅存储设备的公钥和基本元数据（如显示名称、平台和注册时间）。

该设置仅适用于 Remote Control。常规 Claude 聊天、终端中的 Claude Code 和 API 使用不受影响。

### 为组织启用 Trusted Devices

管理员从 Claude Code 管理控制台启用设置。

**第 1 步：打开 Claude Code 管理设置**

前往 [claude.ai/admin-settings/claude-code](https://claude.ai/admin-settings/claude-code)。**Require trusted devices** 开关出现在 Remote Control 设置下方。

**第 2 步：打开 Require trusted devices**

该设置适用于组织的每个成员，并适用于启用后启动的 Remote Control 会话。启用前已运行的会话不会被追溯保护，它们在结束前继续无设备要求。不支持按团队或按项目范围限定。

**第 3 步：通知成员**

启用设置后，成员首次从浏览器、手机或桌面应用查看或操控新的 Remote Control 会话时，会被提示注册该设备。提前告知他们可以避免困惑。

### 成员看到什么

**注册是每台设备一次性的步骤。** 之后唯一可见的变化是偶尔的生物识别提示。

| 场景 | 体验 |
| :--- | :--- |
| 每台设备首次使用 | 要求注册。如果登录不是近期的，先通过正常流程（包括已配置的 SSO）登录，然后确认注册 |
| 日常使用 | 有已注册设备和近期登录的成员不会看到提示。登录超过 18 小时后，下次 Remote Control 交互显示一次生物识别提示 |
| 未注册设备 | 无法查看或操控 Remote Control 会话直到设备注册。该设备上的常规 Claude 聊天不受影响 |
| 无平台认证器 | 没有 Face ID、Touch ID 或 Windows Hello 的机器上的成员可以使用硬件安全密钥，或重新登录代替生物识别验证 |
| 在终端中 | 运行 Claude Code 的机器在开发者登录 CLI 时自动获得凭据。终端中没有单独的注册步骤 |

### 管理已注册设备

**成员可以从账户设置查看和撤销自己的设备。**

打开 [claude.ai/settings/account](https://claude.ai/settings/account#trusted-devices) 找到 **Trusted devices** 部分，查看每个已注册设备的名称、平台和注册日期。移除设备会立即撤销其凭据，设备之后可在重新登录后再次注册。凭据如果不续期也会自动过期，未使用的设备会自动从可信列表中移除。

对于丢失或被盗的设备，成员从此页面移除它。如果成员无法登录，管理员可以在管理控制台中使用 **Sign out everywhere** 撤销该成员的所有会话和已注册设备，之后成员重新注册仍持有的设备。

## Remote Control vs Claude Code on the web

**Remote Control 和 [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web) 都使用 claude.ai/code 界面。关键区别在于会话运行的位置：** Remote Control 在你的机器上执行，因此本地 MCP 服务器、工具和项目配置保持可用。Claude Code on the web 在 Anthropic 管理的云基础设施上执行。

当你正在进行本地工作并想从另一台设备继续时使用 Remote Control。当你想在没有本地设置的情况下启动任务、处理未克隆的仓库或并行运行多个任务时使用 Claude Code on the web。

## 移动推送通知

**Remote Control 活跃时，Claude 可以向你的手机发送推送通知。**

Claude 自行决定何时推送。通常在长时间运行的任务完成或需要你做决定时发送。你也可以在 prompt 中请求推送，例如 `notify me when the tests finish`。除了下面两个开/关切换外，没有逐事件配置。

> [!NOTE]
> 移动推送通知需要 Claude Code v2.1.110 或更高版本。

**设置移动推送通知的步骤：**

1. **安装 Claude 移动应用**：下载 [iOS](https://apps.apple.com/us/app/claude-by-anthropic/id6473753684) 或 [Android](https://play.google.com/store/apps/details?id=com.anthropic.claude) 版 Claude 应用
2. **使用你的 Claude Code 账户登录**：使用与终端中 Claude Code 相同的账户和组织
3. **允许通知**：接受操作系统的通知权限提示
4. **在 Claude Code 中启用推送**：在终端中运行 `/config`，启用 **Push when Claude decides**（主动通知）和/或 **Push when actions required**（权限提示和问题）

**如果通知未到达：**

- 如果 `/config` 显示 **No mobile registered**，在手机上打开 Claude 应用让它刷新推送 token。下次 Remote Control 连接时警告会消失
- 在 iOS 上，Focus 模式和通知摘要可能抑制或延迟推送。检查 Settings → Notifications → Claude
- 在 Android 上，激进的电池优化可能延迟送达。在系统设置中将 Claude 应用排除在电池优化之外

当你在已连接的终端中输入或聚焦时，Claude Code 会跳过移动推送通知。自 v2.1.181 起，你可以设置 [`CLAUDE_CLIENT_PRESENCE_FILE`](https://code.claude.com/docs/en/env-vars) 为标记文件路径，将此扩展到你在机器前的任何时候（即使在另一个窗口中）：文件存在时跳过通知。配置屏幕锁定监听器或类似工具，在屏幕解锁时创建文件，锁定时删除文件。

## 限制

- **每个交互进程一个远程会话**：服务器模式外，每个 Claude Code 实例同时支持一个远程会话。使用 [服务器模式](#服务器模式) 从单个进程运行多个并发会话
- **本地进程必须保持运行**：Remote Control 作为本地进程运行。如果关闭终端、退出 VS Code 或停止 `claude` 进程，会话结束
- **长时间网络中断**：如果机器清醒但无法连接网络超过约 10 分钟，会话超时并退出。再次运行 `claude remote-control` 启动新会话
- **Ultraplan 断开 Remote Control**：启动 [ultraplan](https://code.claude.com/docs/en/ultraplan) 会话会断开任何活跃的 Remote Control 会话，因为两者都占用 claude.ai/code 界面且一次只能连接一个
- **部分命令仅限本地**：在终端中打开交互式选择器的命令（如 `/plugin` 或 `/resume`）仅从本地 CLI 工作。以下命令从移动端和 web 可用：
  - 文本输出命令：`/compact`、`/clear`、`/context`、`/usage`、`/exit`、`/usage-credits`、`/recap`、`/reload-plugins`
  - `/mcp`（v2.1.166 起）：返回服务器状态的文本摘要而非打开选择器，接受 `reconnect`、`enable` 和 `disable` 子命令。与本地 CLI 不同，不带服务器名的 `/mcp reconnect` 会重连所有失败或需要认证的服务器
  - `/config`（v2.1.181 起）：传 `key=value` 设置值，不带参数运行列出可设置的键

## 故障排除

### "Remote Control requires a claude.ai subscription"

你没有使用 claude.ai 账户认证。运行 `claude auth login` 并选择 claude.ai 选项。如果环境中设置了 `ANTHROPIC_API_KEY`，先取消设置。

### "Remote Control requires a full-scope login token"

你使用了 `claude setup-token` 或 `CLAUDE_CODE_OAUTH_TOKEN` 环境变量的长期 token 认证。这些 token 限于推理，无法建立 Remote Control 会话。运行 `claude auth login` 使用全范围会话 token 认证。

### "Unable to determine your organization for Remote Control eligibility"

缓存的账户信息过时或不完整。运行 `claude auth login` 刷新。

### "Remote Control is not yet enabled for your account"

Remote Control 的推出尚未到达你的账户，或缓存的权限信息过时。如果你最近更改了计划，运行 `claude auth logout` 然后 `claude auth login` 刷新。运行 `claude doctor` 查看哪个具体的资格检查失败了。

### "Couldn't verify Remote Control eligibility"

Claude Code 无法访问 feature-flag 服务检查 Remote Control 是否为你的账户启用，通常因为离线或代理阻止了请求。有网络访问后重试，或运行 `claude doctor` 获取详情。

### "Remote Control is disabled by your organization's policy"

**此错误有四种不同原因。** 先运行 `/status` 查看使用的登录方式和订阅。

| 原因 | 修复方法 |
| :--- | :--- |
| 使用 API Key 或 Console 账户认证 | Remote Control 需要 claude.ai OAuth。运行 `/login` 选择 claude.ai 选项。如果设置了 `ANTHROPIC_API_KEY`，取消设置 |
| Owner 未为组织启用 | Team 和 Enterprise 计划默认关闭。Owner 可在 [管理设置](https://claude.ai/admin-settings/claude-code) 启用 **Remote Control** 开关 |
| 管理开关灰化 | 你的组织有与 Remote Control 不兼容的数据保留或合规配置。无法从管理面板更改。联系 Anthropic 支持讨论选项 |
| 错误提到 `disableRemoteControl` | IT 管理员通过 [托管设置](https://code.claude.com/docs/en/settings#settings-files) 在此设备上禁用了 Remote Control，独立于组织级开关 |

### "Remote credentials fetch failed"

Claude Code 无法从 Anthropic API 获取短期凭据建立连接。使用 `--verbose` 重新运行查看完整错误：

```bash
claude remote-control --verbose
```

常见原因：

- 未登录：运行 `claude` 并使用 `/login` 用 claude.ai 账户认证。Remote Control 不支持 API Key 认证
- 网络或代理问题：防火墙或代理可能阻止了出站 HTTPS 请求。Remote Control 需要访问端口 443 上的 Anthropic API
- 会话创建失败：如果还看到 `Session creation failed — see debug log`，失败发生在设置的早期阶段。检查订阅是否活跃

### "Your organization requires Trusted Devices for Remote Control, but this device is not enrolled"

你的组织启用了 [Trusted Devices](#trusted-devices可信设备) 且此机器尚未注册。在 Claude Code 中运行 `/login`。注册作为登录的一部分发生，没有单独的注册命令。

### "session expired for trusted-device check"

你的登录超过 18 小时。在 Claude Code 中运行 `/login`，或在 claude.ai 或移动应用提示时通过 Face ID、Touch ID、Windows Hello 或 passkey 确认。

## 选择合适的方式

**Claude Code 提供多种不在终端前工作的方式，区别在于触发方式、Claude 运行位置和所需设置量。**

| 方式 | 触发方式 | Claude 运行位置 | 设置 | 最适合 |
| :--- | :--- | :--- | :--- | :--- |
| [Dispatch](https://code.claude.com/docs/en/desktop#sessions-from-dispatch) | 从 Claude 移动应用发送任务 | 你的机器（Desktop） | [将移动应用与 Desktop 配对](https://support.claude.com/en/articles/13947068) | 不在时委派工作，最少设置 |
| [Remote Control](https://code.claude.com/docs/en/remote-control) | 从 claude.ai/code 或 Claude 移动应用驱动运行中的会话 | 你的机器（CLI 或 VS Code） | 运行 `claude remote-control` | 从另一台设备操控进行中的工作 |
| [Channels](https://code.claude.com/docs/en/channels) | 来自 Telegram、Discord 等聊天应用或你自己服务器的推送事件 | 你的机器（CLI） | [安装 channel 插件](https://code.claude.com/docs/en/channels#quickstart) 或 [构建自己的](https://code.claude.com/docs/en/channels-reference) | 响应 CI 失败或聊天消息等外部事件 |
| [Slack](https://code.claude.com/docs/en/slack) | 在团队频道中 @Claude | Anthropic 云 | [安装 Slack 应用](https://code.claude.com/docs/en/slack#setting-up-claude-code-in-slack)，启用 [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web) | 从团队聊天发起 PR 和审查 |
| [定时任务](https://code.claude.com/docs/en/scheduled-tasks) | 设置调度 | [CLI](https://code.claude.com/docs/en/scheduled-tasks)、[Desktop](https://code.claude.com/docs/en/desktop-scheduled-tasks) 或 [云](https://code.claude.com/docs/en/routines) | 选择频率 | 重复性自动化如每日审查 |

## 相关资源

- [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web) - 在 Anthropic 管理的云环境中运行会话
- [Ultraplan](https://code.claude.com/docs/en/ultraplan) - 从终端启动云端规划会话并在浏览器中审查计划
- [Channels](https://code.claude.com/docs/en/channels) - 将 Telegram、Discord 或 iMessage 转发到会话中
- [Dispatch](https://code.claude.com/docs/en/desktop#sessions-from-dispatch) - 从手机发送任务，可生成 Desktop 会话处理
- [认证](https://code.claude.com/docs/en/authentication) - 设置 `/login` 和管理 claude.ai 凭据
- [CLI 参考](https://code.claude.com/docs/en/cli-reference) - 完整的 flag 和命令列表，包括 `claude remote-control`
- [安全](https://code.claude.com/docs/en/security) - Remote Control 会话如何融入 Claude Code 安全模型
- [数据使用](https://code.claude.com/docs/en/data-usage) - 本地和远程会话中哪些数据通过 Anthropic API 流转
