---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Web 快速开始
description: Claude Code on the web 允许你在浏览器或手机上运行 Claude Code，连接 GitHub 仓库后提交任务，Claude 在云端 VM 中克隆代码、执行修改并推送分支供你审查。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/web-quickstart.md
  - en-source/web-quickstart.md
---

# 在 Web 上使用 Claude Code

> 从浏览器或手机在云端运行 Claude Code。连接 GitHub 仓库，提交任务，审查 PR，无需本地环境。

> [!NOTE]
> Claude Code on the web 处于研究预览阶段，面向 Pro、Max 和 Team 用户开放，Enterprise 用户需要 premium 席位或 Chat + Claude Code 席位。

**Claude Code on the web 运行在 Anthropic 管理的云基础设施上，而非你的本地机器。** 从 [claude.ai/code](https://claude.ai/code) 或 Claude 移动端提交任务。

你需要一个 GitHub 仓库来开始。Claude 将其克隆到隔离的虚拟机中，进行修改，然后推送分支供你审查。会话跨设备持久化，在笔记本上启动的任务可以稍后在手机上审查。

**Claude Code on the web 适合以下场景：**

| 场景 | 说明 |
|------|------|
| **并行任务** | 同时运行多个独立任务，每个有自己的会话和分支，无需管理多个 worktree |
| **本地没有的仓库** | Claude 每次会话都全新克隆，你不需要在本地检出 |
| **不需要频繁指导的任务** | 提交明确的任务后去做别的事，完成后再审查结果 |
| **代码探索和提问** | 了解代码库或追踪功能实现，无需本地检出 |

如果需要本地配置、工具或环境，本地运行 Claude Code 或使用 [Remote Control](https://code.claude.com/docs/en/remote-control) 更合适。

## 会话如何运行

当你提交任务时：

1. **克隆和准备**：仓库被克隆到 Anthropic 管理的 VM，如果配置了 [setup script](https://code.claude.com/docs/en/claude-code-on-the-web#setup-scripts) 则运行。
2. **配置网络**：根据环境的[访问级别](https://code.claude.com/docs/en/claude-code-on-the-web#access-levels)设置网络访问。
3. **工作**：Claude 分析代码、修改文件、运行测试、检查工作。你可以全程观看和引导，也可以离开等完成后再回来。
4. **推送分支**：当 Claude 到达停止点时推送分支到 GitHub。你审查 diff、留行内评论、创建 PR，或继续发消息。

分支推送后会话不会关闭。PR 创建和后续编辑都在同一个对话中进行。

## 运行方式对比

**Claude Code 在所有平台上行为一致，区别在于代码执行位置和本地配置是否可用。**

| | Web | Remote Control | 终端 CLI | 桌面应用 |
|---|---|---|---|---|
| **代码运行在** | Anthropic 云端 VM | 你的机器 | 你的机器 | 你的机器或云端 VM |
| **聊天界面** | claude.ai 或移动端 | claude.ai 或移动端 | 终端 | 桌面 UI |
| **使用本地配置** | 否，仅仓库 | 是 | 是 | 本地是/云端否 |
| **需要 GitHub** | 是，或通过 `--cloud` [打包本地仓库](https://code.claude.com/docs/en/claude-code-on-the-web#send-local-repositories-without-github) | 否 | 否 | 仅云端会话需要 |
| **断开后继续运行** | 是 | 终端保持打开时 | 否 | 取决于会话类型 |
| **[权限模式](https://code.claude.com/docs/en/permission-modes)** | Accept edits, Plan, Auto | Ask, Auto accept edits, Plan | 所有模式 | 取决于会话类型 |
| **网络访问** | 按环境配置 | 你机器的网络 | 你机器的网络 | 取决于会话类型 |

## 连接 GitHub 并创建环境

**这是一次性设置流程。** 如果你已经使用 GitHub CLI，也可以[从终端完成](#从终端连接)。

### 浏览器设置步骤

1. **访问 claude.ai/code**：打开 [claude.ai/code](https://claude.ai/code) 并使用 Anthropic 账号登录。
2. **安装 Claude GitHub App**：登录后会提示连接 GitHub，按提示安装 Claude GitHub App 并授权访问仓库。云端会话使用已有的 GitHub 仓库，如需新项目请先[在 GitHub 上创建空仓库](https://github.com/new)。
3. **创建环境**：连接 GitHub 后会提示创建云端环境。环境控制 Claude 在会话期间的网络访问权限和创建会话时运行的内容。

环境表单字段：

| 字段 | 说明 |
|------|------|
| **Name** | 显示标签。多环境时便于区分不同项目或访问级别 |
| **Network access** | 控制会话的网络访问。默认 `Trusted`，允许连接 npm、PyPI、RubyGems 等[常见包注册表](https://code.claude.com/docs/en/claude-code-on-the-web#default-allowed-domains)，阻止一般互联网访问 |
| **Environment variables** | 可选的环境变量，`.env` 格式。不要给值加引号，引号会被存储为值的一部分 |
| **Setup script** | 可选的 Bash 脚本，在 Claude Code 启动前运行。用于安装云端 VM 未包含的系统工具 |

首次项目保持默认值，点击 **Create environment** 即可。之后可以编辑或创建额外环境。

### 从终端连接

如果你已使用 GitHub CLI (`gh`)，可以不开浏览器完成设置。需要 [Claude Code CLI](https://code.claude.com/docs/en/quickstart)。

> [!NOTE]
> 启用了 [Zero Data Retention](https://code.claude.com/docs/en/zero-data-retention) 的组织无法使用 `/web-setup` 或其他云端会话功能。如果 GitHub CLI 未安装或未认证，`/web-setup` 会打开浏览器引导流程。

1. **认证 GitHub CLI**：`gh auth login`
2. **登录 Claude**：在 Claude Code CLI 中运行 `/login`
3. **运行 /web-setup**：在 Claude Code CLI 中运行 `/web-setup`

这会将你的 `gh` token 同步到 Claude 账号。如果没有云端环境，`/web-setup` 会创建一个带 Trusted 网络访问的默认环境。完成后可以从终端用 `--cloud` 启动云端会话或用 `/schedule` 设置定期任务。

## 开始任务

GitHub 已连接且环境已创建后，就可以提交任务了。

1. **选择仓库和分支**：从 [claude.ai/code](https://claude.ai/code) 或 Claude 移动端的 Code 标签，点击输入框下方的仓库选择器选择仓库。每个仓库显示分支选择器，可选择从特性分支而非默认分支开始。可添加多个仓库在一个会话中跨仓库工作。
2. **选择权限模式**：模式下拉默认为 **Accept edits**，Claude 直接修改并推送分支。切换到 **Plan mode** 让 Claude 先提出方案等你同意再编辑文件。
3. **描述任务并提交**：输入你想要的内容然后按 Enter。要具体：
   - 指明文件或函数："Add a README with setup instructions" 或 "Fix the failing auth test in `tests/test_auth.py`" 比 "fix tests" 好
   - 如果有错误输出就粘贴进来
   - 描述预期行为，而非仅描述症状

Claude 克隆仓库、运行 setup script，然后开始工作。每个任务有自己的会话和分支，不需要等一个完成再开始下一个。

## 预填充会话

**你可以通过 URL 参数预填充 prompt、仓库和环境。** 可用于构建集成，比如在 issue tracker 中添加按钮直接打开 Claude Code 并带上 issue 描述。

| 参数 | 说明 |
|------|------|
| `prompt` | 预填充到输入框的文本。别名 `q` 也可用 |
| `prompt_url` | 获取 prompt 文本的 URL，用于太长无法嵌入 query string 的 prompt。URL 必须允许跨域请求。设置了 `prompt` 时忽略 |
| `repositories` | 逗号分隔的 `owner/repo` slug 列表。别名 `repo` 也可用 |
| `environment` | 要预选的环境名称或 ID |

示例：

```text
https://claude.ai/code?prompt=Fix%20the%20login%20bug&repositories=acme/webapp
```

## 审查和迭代

**Claude 完成后，审查修改、对特定行留反馈，持续迭代直到 diff 看起来正确。**

1. **打开 diff 视图**：diff 指示器显示整个会话中添加和删除的行数（如 `+42 -18`），点击打开 diff 视图。
2. **留行内评论**：在 diff 中选择任意行，输入反馈然后按 Enter。评论会随下一条消息一起发送。Claude 看到的是 "at `src/auth.ts:47`, don't catch the error here" 和你的主要指令，你不需要描述问题位置。
3. **创建 PR**：diff 看起来正确时，点击 diff 视图顶部的 **Create PR**。可以创建正式 PR、draft PR，或跳转到 GitHub 的编辑页面（带生成的标题和描述）。
4. **PR 后继续迭代**：PR 创建后会话保持活跃。将 CI 失败输出或 reviewer 评论粘贴到聊天中让 Claude 处理。

## 常见问题排查

### 连接 GitHub 后看不到仓库

**云端会话可以使用已连接 GitHub 账号能看到的任何仓库**，不受 Claude GitHub App 安装范围限制。如果仓库缺失，确认已连接的 GitHub 账号在 GitHub 上有该仓库的访问权限。

### 页面只显示 GitHub 登录按钮

云端会话需要已连接的 GitHub 账号。通过浏览器流程连接，或使用 GitHub CLI 从终端运行 `/web-setup`。

### "Not available for the selected organization"

Enterprise 组织可能需要 Owner 启用 Claude Code on the web。联系 Anthropic 客户团队。

### `/web-setup` 显示 "No commands match" 或 "Unknown command"

`/web-setup` 在 Claude Code CLI 内运行，不是在 shell 中。先启动 `claude`，然后在提示符中输入 `/web-setup`。

如果在 Claude Code 内输入后命令菜单显示 `No commands match "/web-setup"`，通常是 CLI 版本低于 v2.1.80 或使用了 API key / 第三方提供商认证。运行 `claude update`，然后 `/login` 使用 claude.ai 账号登录。

### Setup script 失败

setup script 以非零状态退出会阻止会话启动。常见原因：

- 包安装失败，因为注册表不在网络访问级别范围内
- 脚本引用了全新克隆中不存在的文件或路径
- 本地可用的命令在 Ubuntu 上需要不同调用方式

调试方法：在脚本顶部添加 `set -x` 查看哪个命令失败。非关键命令添加 `|| true` 以免阻止会话启动。

### 新会话在 setup 阶段卡住或超时

如果新会话卡在 setup script 步骤或在脚本完成前失败，脚本可能超过了约五分钟的环境缓存构建时间预算。

修复方法：精简脚本使其在五分钟内完成：
- 用 `&` 和 `wait` 并行运行独立安装
- 将大型下载移到 SessionStart hook 中后台运行
- 移除长时间的重试 sleep

### 关闭标签页后会话继续运行

**这是设计如此。** 关闭标签页不会停止会话。它在后台继续运行直到 Claude 完成当前任务。从侧边栏可以归档或删除会话。

## 后续步骤

- [使用 Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web)：完整参考，包括将会话传送到终端、setup scripts、环境变量和网络配置
- [Routines](https://code.claude.com/docs/en/routines)：按计划、API 调用或 GitHub 事件自动化工作
- [CLAUDE.md](https://code.claude.com/docs/en/memory)：给 Claude 持久化指令和上下文
- 安装 Claude 移动端（[iOS](https://apps.apple.com/us/app/claude-by-anthropic/id6473753684) / [Android](https://play.google.com/store/apps/details?id=com.anthropic.claude)）从手机监控会话
