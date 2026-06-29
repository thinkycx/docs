---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】Channels 事件推送
description: Channels 是 Claude Code 的事件推送机制，允许 MCP 服务器将消息、告警和 Webhook 推送到正在运行的会话中。支持 Telegram、Discord、iMessage 等双向通道，让 Claude 在你离开终端时也能响应外部事件。
category: translation
tags: [claude-code, channels, translation]
refs: [https://code.claude.com/docs/en/channels.md]
---

# 用 Channels 向运行中的会话推送事件

**通过 Channels，MCP 服务器可以将消息、告警和 Webhook 推送到你的 Claude Code 会话中。你可以转发 CI 结果、聊天消息和监控事件，让 Claude 在你离开时也能自动响应。**

> [!NOTE]
> Channels 目前处于 [研究预览阶段](#研究预览)，需要 Claude Code v2.1.80 或更高版本。需要通过 claude.ai 或 Console API key 进行 Anthropic 认证，不支持 Amazon Bedrock、Google Vertex AI 或 Microsoft Foundry。Team 和 Enterprise 组织必须 [显式启用](#企业管控)。

**Channel 本质上是一个能向你的 Claude Code 会话推送事件的 MCP 服务器。** Claude 可以在你不在终端前时对外部事件做出响应。Channel 支持双向通信：Claude 读取事件后，可以通过同一通道回复，就像一个聊天桥接器。事件只在会话打开期间才能到达，因此如果要 24 小时不间断运行，需要将 Claude 放在后台进程或持久终端中运行。

**Channel 与集成方式的区别：** 不同于创建全新云端会话或等待轮询的集成方式，事件直接到达你已经打开的会话。具体对比见 [Channels 与其他方式的比较](#channels-与其他方式的比较)。

**你可以将 Channel 作为插件安装，并配置自己的凭据。** 研究预览阶段内置支持 Telegram、Discord 和 iMessage。

**关于回复的显示方式：** 当 Claude 通过 Channel 回复时，你会在终端中看到入站消息，但看不到回复正文。终端只显示工具调用和确认信息（如 "sent"），实际回复内容出现在对应的平台上。

如果你管理 Team、Enterprise 或 Console 组织，请参阅 [为组织启用 Channels](#为组织启用-channels)。要构建自定义 Channel，请参阅 [Channels 参考文档](https://code.claude.com/docs/en/channels-reference)。

## 支持的 Channels

**每个支持的 Channel 都是一个插件，需要安装 [Bun](https://bun.sh)。** 如果想在连接真实平台之前先体验插件流程，可以尝试 [fakechat 快速入门](#快速入门)。

### Telegram

查看完整的 [Telegram 插件源码](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/telegram)。

**第 1 步：创建 Telegram 机器人**

在 Telegram 中打开 [BotFather](https://t.me/BotFather)，发送 `/newbot`。给它一个显示名称和以 `bot` 结尾的唯一用户名。复制 BotFather 返回的 token。

**第 2 步：安装插件**

在 Claude Code 中运行：

```
/plugin install telegram@claude-plugins-official
```

如果 Claude Code 提示找不到插件，说明你的 marketplace 缺失或过期。运行 `/plugin marketplace update claude-plugins-official` 刷新，或者 `/plugin marketplace add anthropics/claude-plugins-official` 首次添加。然后重试安装。

安装完成后，运行 `/reload-plugins` 以激活插件的配置命令。

**第 3 步：配置 token**

用 BotFather 给你的 token 运行配置命令：

```
/telegram:configure <token>
```

Token 会保存到 `~/.claude/channels/telegram/.env`。你也可以在启动 Claude Code 前在 shell 环境中设置 `TELEGRAM_BOT_TOKEN`。

**第 4 步：启用 Channels 重启**

退出 Claude Code，然后带 channel 标志重启。这将启动 Telegram 插件，开始轮询你的机器人消息：

```bash
claude --channels plugin:telegram@claude-plugins-official
```

**第 5 步：配对账号**

打开 Telegram，向你的机器人发送任意消息。机器人会回复一个配对码。

> [!NOTE]
> 如果机器人没有回复，确保 Claude Code 正在用上一步的 `--channels` 参数运行。机器人只在 Channel 激活时才能回复。

回到 Claude Code 中运行：

```
/telegram:access pair <code>
```

然后锁定访问权限，只允许你的账号发送消息：

```
/telegram:access policy allowlist
```

### Discord

查看完整的 [Discord 插件源码](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/discord)。

**第 1 步：创建 Discord 机器人**

进入 [Discord 开发者门户](https://discord.com/developers/applications)，点击 **New Application** 并命名。在 **Bot** 部分创建用户名，然后点击 **Reset Token** 并复制 token。

**第 2 步：启用 Message Content Intent**

在机器人设置中，滚动到 **Privileged Gateway Intents**，启用 **Message Content Intent**。

**第 3 步：邀请机器人到你的服务器**

进入 **OAuth2 > URL Generator**。选择 `bot` 范围，启用以下权限：

- View Channels
- Send Messages
- Send Messages in Threads
- Read Message History
- Attach Files
- Add Reactions

打开生成的 URL 将机器人添加到你的服务器。

**第 4 步：安装插件**

在 Claude Code 中运行：

```
/plugin install discord@claude-plugins-official
```

如果 Claude Code 提示找不到插件，运行 `/plugin marketplace update claude-plugins-official` 刷新，或 `/plugin marketplace add anthropics/claude-plugins-official` 首次添加。然后重试安装。

安装完成后，运行 `/reload-plugins` 以激活插件的配置命令。

**第 5 步：配置 token**

用你复制的机器人 token 运行配置命令：

```
/discord:configure <token>
```

Token 会保存到 `~/.claude/channels/discord/.env`。你也可以在 shell 环境中设置 `DISCORD_BOT_TOKEN`。

**第 6 步：启用 Channels 重启**

退出 Claude Code，然后带 channel 标志重启。这将连接 Discord 插件，使机器人能接收和响应消息：

```bash
claude --channels plugin:discord@claude-plugins-official
```

**第 7 步：配对账号**

在 Discord 上私信你的机器人。机器人会回复一个配对码。

> [!NOTE]
> 如果机器人没有回复，确保 Claude Code 正在用上一步的 `--channels` 参数运行。机器人只在 Channel 激活时才能回复。

回到 Claude Code 中运行：

```
/discord:access pair <code>
```

然后锁定访问权限：

```
/discord:access policy allowlist
```

### iMessage

查看完整的 [iMessage 插件源码](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/imessage)。

**iMessage Channel 直接读取你的 Messages 数据库，通过 AppleScript 发送回复。** 它只需要 macOS，不需要机器人 token 或外部服务。

**第 1 步：授予完全磁盘访问权限**

Messages 数据库位于 `~/Library/Messages/chat.db`，受 macOS 保护。服务器首次读取时，macOS 会弹出权限提示：点击 **Allow**。提示会显示启动 Bun 的应用名称，如 Terminal、iTerm 或你的 IDE。

如果提示没有出现或你点了"拒绝"，需要在 **系统设置 > 隐私与安全 > 完全磁盘访问** 中手动添加你的终端。没有此权限，服务器会立即以 `authorization denied` 退出。

**第 2 步：安装插件**

在 Claude Code 中运行：

```
/plugin install imessage@claude-plugins-official
```

如果 Claude Code 提示找不到插件，运行 `/plugin marketplace update claude-plugins-official` 刷新，或 `/plugin marketplace add anthropics/claude-plugins-official` 首次添加。然后重试安装。

**第 3 步：启用 Channels 重启**

退出 Claude Code，然后带 channel 标志重启：

```bash
claude --channels plugin:imessage@claude-plugins-official
```

**第 4 步：给自己发消息**

在任何登录了你 Apple ID 的设备上打开 Messages，给自己发送一条消息。消息会立即到达 Claude：自聊天模式无需任何访问控制设置即可使用。

> [!NOTE]
> Claude 发送的第一条回复会触发 macOS 自动化权限提示，询问你的终端是否可以控制 Messages。点击 **OK**。

**第 5 步：允许其他发送者**

默认情况下只有你自己的消息能通过。要让其他联系人联系 Claude，添加他们的标识：

```
/imessage:access allow +15551234567
```

标识格式为 `+国家代码` 格式的电话号码，或 Apple ID 邮箱如 `user@example.com`。

---

你也可以为尚未有插件的系统 [构建自定义 Channel](https://code.claude.com/docs/en/channels-reference)。

## 快速入门

**Fakechat 是一个官方提供的演示 Channel，在 localhost 运行聊天界面，无需认证、无需配置外部服务。**

安装并启用 fakechat 后，你可以在浏览器中输入消息，消息会到达你的 Claude Code 会话。Claude 回复后，回复会显示在浏览器中。体验完 fakechat 后，可以尝试 [Telegram](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/telegram)、[Discord](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/discord) 或 [iMessage](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/imessage)。

**前提条件：**

- Claude Code [已安装并认证](https://code.claude.com/docs/en/quickstart#step-1-install-claude-code)（使用 claude.ai 账号或 Claude Console API key）
- [Bun](https://bun.sh) 已安装。预构建的 Channel 插件是 Bun 脚本。用 `bun --version` 检查；如果命令不存在，[安装 Bun](https://bun.sh/docs/installation)
- **Team、Enterprise 或托管的 Console 组织**：管理员必须在托管设置中 [启用 Channels](#企业管控)

**第 1 步：安装 fakechat Channel 插件**

启动 Claude Code 会话并运行安装命令：

```
/plugin install fakechat@claude-plugins-official
```

如果 Claude Code 提示找不到插件，运行 `/plugin marketplace update claude-plugins-official` 刷新，或 `/plugin marketplace add anthropics/claude-plugins-official` 首次添加。然后重试安装。

**第 2 步：启用 Channel 重启**

退出 Claude Code，然后带 `--channels` 参数重启，传入你安装的 fakechat 插件：

```bash
claude --channels plugin:fakechat@claude-plugins-official
```

fakechat 服务器会自动启动。

> [!TIP]
> 你可以在 `--channels` 后传入多个插件，用空格分隔。

**第 3 步：推送消息**

在浏览器中打开 fakechat 界面 [http://localhost:8787](http://localhost:8787)，输入一条消息：

```
hey, what's in my working directory?
```

消息以 `<channel source="fakechat">` 事件的形式到达你的 Claude Code 会话。Claude 读取后执行工作，然后调用 fakechat 的 `reply` 工具。回答会显示在聊天界面中。

---

**关于权限提示：** 如果 Claude 在你离开终端时遇到权限提示，会话会暂停直到你响应。声明了 [权限转发能力](https://code.claude.com/docs/en/channels-reference#relay-permission-prompts) 的 Channel 服务器可以将这些提示转发给你，让你远程批准或拒绝。对于无人值守场景，[`--dangerously-skip-permissions`](https://code.claude.com/docs/en/permission-modes#skip-all-checks-with-bypasspermissions-mode) 可以跳过除显式 ask 规则之外的所有提示，但只在你信任的环境中使用。

**关于非交互模式：** 在用 `-p` 运行 Channels 的非交互模式下，需要终端输入的工具（如多选题和计划模式审批）会被禁用，确保会话不会因等待输入而卡住。

## 安全性

**每个已批准的 Channel 插件都维护一个发送者允许列表：只有你添加的 ID 才能推送消息，其他人的消息会被静默丢弃。**

Telegram 和 Discord 通过配对机制建立允许列表：

1. 在 Telegram 或 Discord 中找到你的机器人，发送任意消息
2. 机器人回复一个配对码
3. 在你的 Claude Code 会话中，确认配对码
4. 你的发送者 ID 被添加到允许列表

iMessage 的机制不同：给自己发消息会自动绕过访问控制，你可以用 `/imessage:access allow` 命令添加其他联系人。

**在此之上，你还有两层控制：**

- 通过 `--channels` 控制每个会话启用哪些服务器
- 组织通过 [`channelsEnabled`](#企业管控) 控制可用性（适用于 claude.ai Team/Enterprise 计划和部署了托管设置的 Console 组织）

**仅在 `.mcp.json` 中配置不足以推送消息：** 服务器还必须在 `--channels` 中被指定。

**允许列表同样控制 [权限转发](https://code.claude.com/docs/en/channels-reference#relay-permission-prompts)。** 任何能通过 Channel 回复的人都可以批准或拒绝你会话中的工具使用，因此只将你信任的发送者加入允许列表。

## 企业管控

**管理员通过两个 [托管设置](https://code.claude.com/docs/en/settings) 控制可用性，用户无法覆盖这些设置。** 默认值取决于认证方式：

- **claude.ai Team 和 Enterprise**：Channels 默认禁用，直到 Owner 启用
- **Anthropic Console（API key 认证）**：Channels 默认允许。只有在组织部署了托管设置时才需要此配置

无论哪种情况，Channel 都不会自动运行，用户必须通过 `--channels` 在每个会话中手动启用。

| 设置 | 用途 | 未配置时 |
| :--- | :--- | :--- |
| `channelsEnabled` | 主开关。必须为 `true` 才能让任何 Channel 推送消息。通过 [claude.ai 管理控制台](https://claude.ai/admin-settings/claude-code) 开关或直接在托管设置中设置。关闭时会阻止所有 Channel，包括开发标志。 | claude.ai Team/Enterprise：Channels 被阻止。Console：除非组织部署了托管设置（此时 Channels 被阻止直到设置此 key），否则允许 |
| `allowedChannelPlugins` | Channels 启用后，控制哪些插件可以注册。设置后替代 Anthropic 维护的列表。仅在 `channelsEnabled` 为 `true` 时有效。 | 使用 Anthropic 默认列表 |

Pro 和 Max 用户如果没有组织，完全跳过这些检查：Channels 可用，用户通过 `--channels` 按会话启用。

### 为组织启用 Channels

**从 [claude.ai → Admin settings → Claude Code → Channels](https://claude.ai/admin-settings/claude-code) 启用（需要 Owner 角色），或在托管设置中将 `channelsEnabled` 设为 `true`。**

启用后，组织中的用户可以用 `--channels` 将 Channel 服务器接入单个会话。如果设置被禁用或未设置，MCP 服务器仍然可以连接且其工具正常工作，但 Channel 消息不会到达。启动时会有警告提示用户联系管理员启用此设置。

### 限制允许运行的 Channel 插件

**默认情况下，Anthropic 维护的允许列表上的任何插件都可以注册为 Channel。** Team 和 Enterprise 计划的管理员可以通过在托管设置中设置 `allowedChannelPlugins` 来用自己的列表替代。你可以用它来限制允许的官方插件、批准来自内部 marketplace 的 Channel，或两者兼顾。每个条目指定一个插件及其来源 marketplace：

```json
{
  "channelsEnabled": true,
  "allowedChannelPlugins": [
    { "marketplace": "claude-plugins-official", "plugin": "telegram" },
    { "marketplace": "claude-plugins-official", "plugin": "discord" },
    { "marketplace": "acme-corp-plugins", "plugin": "internal-alerts" }
  ]
}
```

**当 `allowedChannelPlugins` 被设置时，它完全替代 Anthropic 允许列表：** 只有列出的插件可以注册。不设置则回退到默认的 Anthropic 允许列表。空数组会阻止所有允许列表中的插件，但 `--dangerously-load-development-channels` 仍可绕过以进行本地测试。要完全阻止 Channels（包括开发标志），保持 `channelsEnabled` 不设置即可。

此设置需要 `channelsEnabled: true`。如果用户传入了不在列表上的插件，Claude Code 正常启动但该 Channel 不会注册，启动通知会说明该插件不在组织的批准列表中。

## 研究预览

**Channels 是一个研究预览功能。** 可用性正在逐步推出，`--channels` 标志语法和协议规范可能会根据反馈进行更改。

在预览期间，`--channels` 只接受 Anthropic 维护的允许列表中的插件，或管理员设置了 [`allowedChannelPlugins`](#限制允许运行的-channel-插件) 时组织自己的允许列表中的插件。[claude-plugins-official](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins) 中的 Channel 插件是默认的批准集合。如果传入不在有效允许列表中的内容，Claude Code 正常启动但 Channel 不会注册，启动通知会告诉你原因。

要测试你正在构建的 Channel，使用 `--dangerously-load-development-channels`。详见 [在研究预览期间测试](https://code.claude.com/docs/en/channels-reference#test-during-the-research-preview)。

在 [Claude Code GitHub 仓库](https://github.com/anthropics/claude-code/issues) 报告问题或反馈。

## Channels 与其他方式的比较

**Claude Code 有多种连接终端外系统的方式，各适合不同场景：**

| 功能 | 作用 | 适合场景 |
| :--- | :--- | :--- |
| [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web) | 在全新的云端沙箱中运行任务，从 GitHub 克隆 | 委托独立的异步任务，稍后查看结果 |
| [Claude in Slack](https://code.claude.com/docs/en/slack) | 从频道或线程中的 `@Claude` 提及生成 Web 会话 | 直接从团队对话上下文启动任务 |
| 标准 [MCP 服务器](https://code.claude.com/docs/en/mcp) | Claude 在任务执行期间查询它；不会向会话推送内容 | 让 Claude 按需读取或查询某个系统 |
| [Remote Control](https://code.claude.com/docs/en/remote-control) | 从 claude.ai 或 Claude 移动应用操控本地会话 | 离开桌面时操控正在进行的会话 |

**Channels 填补了这个列表中的空白：从非 Claude 来源向已运行的本地会话推送事件。**

- **聊天桥接**：通过 Telegram、Discord 或 iMessage 从手机向 Claude 提问，回答在同一聊天中返回，而工作在你的机器上针对真实文件执行。
- **[Webhook 接收器](https://code.claude.com/docs/en/channels-reference#example-build-a-webhook-receiver)**：来自 CI、错误追踪器、部署流水线或其他外部服务的 Webhook 到达时，Claude 已经打开了你的文件，并记得你在调试什么。

## 下一步

Channel 运行起来后，可以探索这些相关功能：

- [构建自定义 Channel](https://code.claude.com/docs/en/channels-reference) — 为还没有插件的系统构建
- [Remote Control](https://code.claude.com/docs/en/remote-control) — 从手机操控本地会话，而非向其推送事件
- [定时任务](https://code.claude.com/docs/en/scheduled-tasks) — 用定时轮询替代推送事件的响应模式
