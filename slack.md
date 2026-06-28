---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】Slack 集成
description: Claude Code 与 Slack 的集成指南。在 Slack 中 @Claude 即可发起编码任务，Claude 会自动路由到 Claude Code on the web 创建会话，完成代码审查、Bug 修复、功能实现等工作，并在完成后通知你创建 PR。
category: translation
tags: [claude-code, slack, translation]
refs: [https://code.claude.com/docs/en/slack.md]
---

# Slack 中的 Claude Code

**在 Slack 中 @Claude 发送编码任务，Claude 自动检测意图并路由到 Claude Code on the web 创建会话，让你无需离开团队对话即可委派开发工作。**

> [!NOTE]
> Claude Code in Slack 正在被 [Claude Tag](https://claude.com/docs/claude-tag/overview) 替代（适用于 Team 和 Enterprise 工作区）。Claude Tag 以组织共享身份运行 @Claude，由管理员配置访问权限，使用同一个 Slack 应用，无需重新安装，现有配置在过渡期间继续生效。要切换工作区，请参阅 [从早期 Claude in Slack 迁移](https://claude.com/docs/claude-tag/admins/migrate-from-earlier)。

Claude Code in Slack 将 Claude Code 的能力带入你的 Slack 工作区。当你在编码任务中 @Claude 时，Claude 自动检测意图并在 web 上创建 Claude Code 会话，让你无需离开团队对话即可委派开发工作。

该集成基于现有的 Claude for Slack 应用，但为编码相关请求添加了到 Claude Code on the web 的智能路由。每个会话运行在你自己的 Claude 账户下，使用你已连接的仓库和你的计划额度。

## 使用场景

- **Bug 调查与修复**：当 Bug 在 Slack 频道中被报告时，直接让 Claude 调查和修复。
- **快速代码审查与修改**：让 Claude 根据团队反馈实现小功能或重构代码。
- **协作调试**：当团队讨论提供了关键上下文（如错误复现或用户报告），Claude 可以利用这些信息指导调试。
- **并行任务执行**：在 Slack 中启动编码任务，你继续做其他工作，完成后收到通知。

## 前置条件

| 条件 | 说明 |
| :--- | :--- |
| Claude 计划 | Pro、Max、Team 或 Enterprise，具有 Claude Code 访问权限（premium seats 或 Chat + Claude Code seats） |
| Claude Code on the web | 必须启用 [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web) 访问权限 |
| GitHub 账户 | 已连接到 Claude Code on the web，至少认证了一个仓库 |
| Slack 认证 | 你的 Slack 账户通过 Claude 应用链接到你的 Claude 账户 |

## 设置 Claude Code in Slack

### 第 1 步：在 Slack 中安装 Claude App

工作区管理员需要从 Slack App Marketplace 安装 Claude 应用。访问 [Slack App Marketplace](https://slack.com/marketplace/A08SF47R6P4)，点击 "Add to Slack" 开始安装。

### 第 2 步：连接你的 Claude 账户

应用安装后，认证你的个人 Claude 账户：

1. 在 Slack 中打开 Claude 应用，点击 Apps 区域中的 "Claude"
2. 导航到 App Home 标签
3. 点击 "Connect" 将你的 Slack 账户与 Claude 账户关联
4. 在浏览器中完成认证流程

### 第 3 步：配置 Claude Code on the web

确保你的 Claude Code on the web 已正确配置：

- 访问 [claude.ai/code](https://claude.ai/code)，使用与 Slack 关联的同一账户登录
- 如果尚未连接，连接你的 GitHub 账户
- 至少认证一个你希望 Claude 使用的仓库

### 第 4 步：选择路由模式

**连接账户后，配置 Claude 如何处理你在 Slack 中的消息。** 在 Slack 的 Claude App Home 中找到 **Routing Mode** 设置。

| 模式 | 行为 |
| :--- | :--- |
| **Code only** | Claude 将所有 @mention 路由到 Claude Code 会话。适合团队仅将 Claude in Slack 用于开发任务 |
| **Code + Chat** | Claude 分析每条消息并智能路由：编码任务到 Claude Code，写作/分析/一般问题到 Claude Chat。适合想要单一 @Claude 入口处理所有工作类型的团队 |

> [!NOTE]
> 在 Code + Chat 模式下，如果 Claude 将消息路由到 Chat 但你想要编码会话，可以点击 "Retry as Code" 创建 Claude Code 会话。反之亦然。

### 第 5 步：将 Claude 添加到频道

安装后 Claude 不会自动加入任何频道。要在频道中使用 Claude，输入 `/invite @Claude` 邀请它。Claude 只能在已加入的频道中响应 @mention。

## 工作原理

### 自动检测

**当你在 Slack 频道或线程中 @Claude 时，Claude 自动分析你的消息判断是否为编码任务。** 如果检测到编码意图，会路由到 Claude Code on the web 而非作为普通聊天助手回复。

你也可以显式告诉 Claude 将请求作为编码任务处理，即使它没有自动检测到。

> [!NOTE]
> Claude Code in Slack 仅在频道（公开或私有）中工作，不支持私信（DM）。

### 上下文收集

**来自线程**：当你在线程中 @Claude 时，它会收集线程中所有消息的上下文来理解完整对话。

**来自频道**：直接在频道中 @mention 时，Claude 查看最近的频道消息获取相关上下文。

上下文帮助 Claude 理解问题、选择合适的仓库，并确定任务的处理方式。

> [!WARNING]
> 在 Slack 中调用 @Claude 时，Claude 可以访问对话上下文来更好地理解你的请求。Claude 可能会跟从上下文中其他消息的指示，因此用户应确保仅在可信的 Slack 对话中使用 Claude。

### 会话流程

1. **发起**：你 @Claude 并发送编码请求
2. **检测**：Claude 分析消息并检测编码意图
3. **创建会话**：在 claude.ai/code 上创建新的 Claude Code 会话
4. **进度更新**：Claude 在你的 Slack 线程中发布状态更新
5. **完成**：完成后 Claude @mention 你并提供摘要和操作按钮
6. **审查**：点击 "View Session" 查看完整记录，或 "Create PR" 创建 Pull Request

## 界面元素

### App Home

App Home 标签显示你的连接状态，允许你连接或断开 Slack 与 Claude 账户的关联。

### 消息操作

| 按钮 | 功能 |
| :--- | :--- |
| View Session | 在浏览器中打开完整的 Claude Code 会话，查看所有工作、继续会话或发起新请求 |
| Create PR | 直接从会话的变更创建 Pull Request |
| Retry as Code | 如果 Claude 初始以聊天助手回复但你想要编码会话，点击此按钮重试 |
| Change Repo | 如果 Claude 选错了仓库，允许你选择其他仓库 |

### 仓库选择

Claude 根据 Slack 对话的上下文自动选择仓库。如果多个仓库可能适用，Claude 会显示下拉菜单让你选择正确的仓库。

## 访问与权限

### 用户级访问

| 访问类型 | 要求 |
| :--- | :--- |
| Claude Code 会话 | 每个用户在自己的 Claude 账户下运行会话 |
| 用量和速率限制 | 会话计入用户个人的计划额度 |
| 仓库访问 | 用户只能访问自己已连接的仓库 |
| 会话历史 | 会话出现在 claude.ai/code 的 Claude Code 历史中 |

### 工作区级访问

Slack 工作区管理员控制 Claude 应用在其工作区中是否可用：

| 控制 | 说明 |
| :--- | :--- |
| 应用安装 | 工作区管理员决定是否从 Slack App Marketplace 安装 Claude 应用 |
| Enterprise Grid 分发 | 对于 Enterprise Grid 组织，组织管理员可以控制哪些工作区有权访问 Claude 应用 |
| 应用移除 | 从工作区移除应用会立即撤销该工作区中所有用户的访问权限 |

### 基于频道的访问控制

**安装后 Claude 不会自动加入任何频道。** 用户必须显式邀请 Claude 到要使用它的频道：

- **需要邀请**：在任何频道中输入 `/invite @Claude` 添加 Claude
- **频道成员资格控制访问**：Claude 只能在已加入的频道中响应 @mention
- **通过频道控制访问**：管理员可以通过管理 Claude 被邀请到的频道以及谁有权访问这些频道来控制 Claude Code 的使用
- **私有频道支持**：Claude 在公开和私有频道中都能工作，给团队灵活的可见性控制

这种基于频道的模型允许团队将 Claude Code 的使用限制在特定频道中，在工作区级权限之上提供额外的访问控制层。

## 内容可见性

**在 Slack 中**：你会看到状态更新、完成摘要和操作按钮。完整记录始终可访问。

**在 web 上**：完整的 Claude Code 会话包含完整对话历史、所有代码变更、文件操作，以及继续会话或创建 Pull Request 的能力。

对于 Enterprise 和 Team 账户，从 Claude in Slack 创建的会话对组织自动可见。详见 [Claude Code on the Web 共享](https://code.claude.com/docs/en/claude-code-on-the-web#share-sessions)。

## 最佳实践

### 编写有效请求

- **具体明确**：在相关时包含文件名、函数名或错误消息。
- **提供上下文**：如果从对话中不明显，提及仓库或项目。
- **定义成功**：解释"完成"是什么样子——Claude 应该写测试？更新文档？创建 PR？
- **使用线程**：讨论 Bug 或功能时在线程中回复，让 Claude 能收集完整上下文。

### 何时使用 Slack vs web

**使用 Slack 的场景**：上下文已存在于 Slack 讨论中，你想异步启动任务，或你正在与需要可见性的队友协作。

**直接使用 web 的场景**：你需要上传文件，想要开发过程中实时交互，或正在处理更长更复杂的任务。

## 故障排除

### "Claude Code is not enabled for your account"

**这个错误意味着你的 Claude 账户还没有云环境，而非管理员需要启用什么。** 用与 Slack 关联的同一账户在 [claude.ai/code](https://claude.ai/code) 登录一次。首次访问会创建默认云环境，之后错误就会消失。每个用户都需要单独操作。

### 会话无法启动

1. 在 Claude App Home 中验证你的 Claude 账户已连接
2. 检查你已启用 Claude Code on the web 访问权限
3. 确保至少有一个 GitHub 仓库已连接到 Claude Code

### 仓库不显示

1. 在 [claude.ai/code](https://claude.ai/code) 的 Claude Code on the web 中连接该仓库
2. 验证你对该仓库的 GitHub 权限
3. 尝试断开并重新连接你的 GitHub 账户

### 选错了仓库

1. 点击 "Change Repo" 按钮选择其他仓库
2. 在请求中包含仓库名称以获得更准确的选择

### 认证错误

1. 在 App Home 中断开并重新连接你的 Claude 账户
2. 确保你在浏览器中登录的是正确的 Claude 账户
3. 检查你的 Claude 计划是否包含 Claude Code 访问权限

### 会话过期

1. 会话在 web 上的 Claude Code 历史中保持可访问
2. 你可以从 [claude.ai/code](https://claude.ai/code) 继续或引用过去的会话

## 当前限制

- **仅支持 GitHub**：目前仅支持 GitHub 上的仓库
- **每次一个 PR**：每个会话只能创建一个 Pull Request
- **速率限制适用**：会话使用你个人 Claude 计划的速率限制
- **需要 web 访问**：用户必须有 Claude Code on the web 访问权限；没有的用户只会得到标准 Claude 聊天回复

## 相关资源

- [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web) - 了解更多 Claude Code on the web
- [Claude for Slack](https://claude.com/claude-and-slack) - 通用 Claude for Slack 文档
- [Claude Tag](https://claude.com/docs/claude-tag/overview) - 组织管理的 @Claude in Slack，管理员配置访问权限
- [Slack App Marketplace](https://slack.com/marketplace/A08SF47R6P4) - 从 Slack Marketplace 安装 Claude 应用
- [Claude Help Center](https://support.claude.com) - 获取更多支持
