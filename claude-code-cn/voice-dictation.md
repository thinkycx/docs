---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】语音输入
description: Claude Code CLI 的语音听写功能，支持按住录音和轻按录音两种模式。语音被实时转写到 prompt 输入中，可以在同一条消息中混合语音和打字。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/voice-dictation.md
  - en-source/voice-dictation.md
---

# 语音输入

> 在 Claude Code CLI 中通过按住录音或轻按录音的方式用语音输入 prompt。

**用说话代替打字来输入 prompt。** 语音被实时转写到 prompt 输入中，你可以在同一条消息中混合语音和打字。用 `/voice` 启用听写，然后按住按键说话或轻按一次开始、再轻按一次发送。

> [!NOTE]
> 语音听写需要 Claude Code v2.1.69 及以上版本。轻按模式需要 v2.1.116 及以上版本。

听写也可在 [agent view](https://code.claude.com/docs/en/agent-view#peek-and-reply) 中使用。

## 要求

**语音听写将录制的音频流式传输到 Anthropic 服务器进行转写，不在本地处理。** 需要以下全部条件：

| 要求 | 说明 |
|------|------|
| Claude.ai 账号 | 语音转文字服务仅在使用 Claude.ai 账号认证时可用。使用 API key、Amazon Bedrock、Google Cloud Agent Platform 或 Microsoft Foundry 时不可用 |
| 组织未启用 HIPAA 合规 | 启用时 `/voice` 显示策略禁用信息 |
| 本地麦克风 | 语音听写在远程环境（如 Claude Code on the web 或 SSH 会话）中不可用 |
| WSLg（WSL 中使用时） | WSLg 包含在 Windows 10/11 的 Microsoft Store WSL2 中。不可用时在原生 Windows 中运行 Claude Code |

转写不消耗 Claude 消息或 token，不计入 `/usage` 显示的限制。

音频录制在 macOS、Linux 和 Windows 上使用内置原生模块。Linux 上如果原生模块无法加载，Claude Code 回退到 ALSA utils 的 `arecord` 或 SoX 的 `rec`。

## 启用语音听写

运行 `/voice` 启用听写。首次启用时 Claude Code 运行麦克风检查。macOS 上如果终端从未获得授权会触发系统麦克风权限提示。

```
/voice
Voice mode enabled (hold). Hold space to record. Dictation language: en (/config to change).
```

`/voice` 接受可选模式参数：

| 命令 | 效果 |
|------|------|
| `/voice` | 切换开/关，保持当前模式 |
| `/voice hold` | 启用[按住模式](#按住录音) |
| `/voice tap` | 启用[轻按模式](#轻按录音并发送) |
| `/voice off` | 禁用 |

语音听写跨会话持久化。也可以直接在[用户设置文件](https://code.claude.com/docs/en/settings)中设置：

```json
{
  "voice": {
    "enabled": true,
    "mode": "tap"
  }
}
```

转写针对编码词汇调优。常见开发术语如 `regex`、`OAuth`、`JSON`、`localhost` 被正确识别，当前项目名和 git 分支名自动添加为识别提示。

## 按住录音

**按住模式是 push-to-talk：** 按住按键时录音，释放时停止。这是默认模式。

按住 `Space` 开始录音。Claude Code 通过监听终端的快速按键重复事件检测按住，因此录音开始前有短暂预热。页脚在预热期间显示 `keep holding…`，录音激活后切换为实时波形。

> [!TIP]
> 要跳过预热，切换到[轻按模式](#轻按录音并发送)，或[重新绑定到修饰键组合](#重新绑定听写按键)如 `meta+k`。修饰键组合在第一次按键时就开始录音。

你的语音在说话时就出现在 prompt 中（转写最终确定前显示为暗色）。释放 `Space` 停止录音并最终化文本。转写插入到光标位置，可以在 prompt 中任意位置混合打字和听写：

```
> refactor the auth middleware to ▮
  # 按住 space，说 "use the new token validation helper"
> refactor the auth middleware to use the new token validation helper▮
```

默认情况下释放按键后插入转写并等你按 `Enter`。在 `voice` 设置对象中设置 `"autoSubmit": true` 可在释放按键时自动发送（转写至少三个词时）。

## 轻按录音并发送

**轻按模式用单次按键切换录音：** 轻按一次开始，说话，再轻按一次发送。没有预热，不需要持续按住。

用 `/voice tap` 启用。prompt 输入为空时轻按 `Space` 开始录音。页脚显示实时波形。再次轻按 `Space` 停止。

**Claude Code 插入转写并在转写至少三个词时自动提交。** 较短的转写只插入不提交，避免意外轻按发送杂词。

第一次轻按只在 prompt 输入为空时开始录音，所以编写消息时仍可正常输入空格。第二次轻按无论输入内容如何都停止录音。录音在 15 秒静默或 2 分钟总时长后自动停止。

## 更改听写语言

语音听写使用与 Claude 响应语言相同的 [`language` 设置](https://code.claude.com/docs/en/settings)。如果该设置为空，听写默认英语。

支持的听写语言：

| 语言 | 代码 | 语言 | 代码 |
|------|------|------|------|
| Czech | `cs` | Korean | `ko` |
| Danish | `da` | Norwegian | `no` |
| Dutch | `nl` | Polish | `pl` |
| English | `en` | Portuguese | `pt` |
| French | `fr` | Russian | `ru` |
| German | `de` | Spanish | `es` |
| Greek | `el` | Swedish | `sv` |
| Hindi | `hi` | Turkish | `tr` |
| Indonesian | `id` | Ukrainian | `uk` |
| Italian | `it` | Japanese | `ja` |

在 `/config` 或直接在 settings 中设置语言：

```json
{
  "language": "japanese"
}
```

如果 `language` 设置不在支持列表中，`/voice` 启用时会警告并回退到英语听写。

## 重新绑定听写按键

听写按键绑定到 `Chat` 上下文中的 `voice:pushToTalk`，默认为 `Space`。在 [`~/.claude/keybindings.json`](https://code.claude.com/docs/en/keybindings) 中重新绑定：

```json
{
  "bindings": [
    {
      "context": "Chat",
      "bindings": {
        "meta+k": "voice:pushToTalk",
        "space": null
      }
    }
  ]
}
```

按住模式下避免绑定裸字母键（如 `v`），因为按住检测依赖按键重复，字母会在预热期间输入到 prompt。使用 `Space` 或修饰键组合如 `meta+k`。轻按模式没有预热，大多数按键都可用。

## 故障排除

常见问题：

- **`Voice mode requires a Claude.ai account`**：使用了 API key 或第三方提供商认证。运行 `/login` 用 Claude.ai 账号登录
- **`Voice mode is disabled by your organization's policy`**：组织合规配置禁用了语音听写
- **`Microphone access is denied`**：在系统设置中给终端授予麦克风权限
- **`No audio recording tool found`（Linux）**：原生音频模块无法加载且无回退。安装 SoX
- **按住 `Space` 时没反应**：观察 prompt 输入。如果空格持续累积说明语音听写关闭了，运行 `/voice hold`。如果只出现一两个空格然后没反应，按住检测未触发，切换到轻按模式
- **`No audio detected from microphone`**：录音开始但捕获到静默。确认正确的输入设备被设为系统默认
- **`No speech detected`**：音频到达转写服务但未识别出词语。靠近麦克风说话，减少背景噪音，确认听写语言匹配

### macOS 麦克风设置中找不到终端

如果终端应用未出现在 System Settings → Privacy & Security → Microphone 中，重置终端的权限状态让下次 `/voice` 运行触发新的权限提示：

1. 运行 `tccutil reset Microphone <bundle-id>`（替换为终端标识符）
2. 退出并重新启动终端（用 Cmd+Q 而非仅关闭窗口）
3. 启动 Claude Code 并运行 `/voice`，macOS 提示麦克风访问权限，允许它

## 参见

- [自定义键盘快捷键](https://code.claude.com/docs/en/keybindings)：重新绑定 `voice:pushToTalk` 和其他 CLI 键盘动作
- [配置设置](https://code.claude.com/docs/en/settings)：`voice`、`language` 和其他设置键的完整参考
- [交互模式](https://code.claude.com/docs/en/interactive-mode)：键盘快捷键、输入模式和会话控制
- [命令](https://code.claude.com/docs/en/commands)：`/voice`、`/config` 和所有其他命令的参考
