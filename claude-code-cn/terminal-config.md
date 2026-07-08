---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】终端配置
description: 为 Claude Code 配置终端的指南，涵盖 Shift+Enter 换行、Option 键快捷键、终端铃声通知、tmux 配置、颜色主题、全屏渲染和 Vim 模式等常见问题的解决方案。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/terminal-config.md
  - en-source/terminal-config.md
---

# 为 Claude Code 配置终端

> 修复 Shift+Enter 换行、获取 Claude 完成时的终端铃声、配置 tmux、匹配颜色主题、在 Claude Code CLI 中启用 Vim 模式。

**Claude Code 在任何终端中无需配置即可工作。** 本页用于某些特定行为不符合预期时的修复。找到你的症状：

- [Shift+Enter 提交而非插入换行](#输入多行-prompt)
- [Option 键快捷键在 macOS 上没反应](#启用-macos-上的-option-键快捷键)
- [Claude 完成时没有声音或提醒](#获取终端铃声或通知)
- [你在 tmux 中运行 Claude Code](#配置-tmux)
- [显示闪烁或滚动缓冲区跳动](#切换到全屏渲染)
- [想在 prompt 中使用 Vim 键](#用-vim-键绑定编辑-prompt)

本页是关于让你的终端向 Claude Code 发送正确信号。要改变 Claude Code 本身响应哪些按键，参见 [keybindings](https://code.claude.com/docs/en/keybindings)。

## 输入多行 Prompt

**按 Enter 提交消息。要插入换行而不提交，按 Ctrl+J 或输入 `\` 然后按 Enter。** 两者在所有终端中无需设置即可使用。

大多数终端也可以按 Shift+Enter，但支持因终端模拟器而异：

| 终端 | Shift+Enter 换行 |
|------|-----------------|
| Ghostty、Kitty、iTerm2、WezTerm、Warp、Apple Terminal、Windows Terminal | 无需设置即可使用 |
| VS Code、Cursor、Devin Desktop、Alacritty、Zed | 运行 `/terminal-setup` 一次 |
| gnome-terminal、JetBrains IDE（PyCharm、Android Studio） | 不可用；使用 Ctrl+J 或 `\` + Enter |

VS Code、Cursor、Devin Desktop、Alacritty 和 Zed 中，`/terminal-setup` 将 Shift+Enter 和其他键绑定写入终端配置文件。

VS Code、Cursor 和 Devin Desktop 中，`/terminal-setup` 还更新两个编辑器设置：将 `terminal.integrated.gpuAcceleration` 设为 `"off"` 防止集成终端中的文字乱码，设置 `terminal.integrated.mouseWheelScrollSensitivity` 使[全屏模式](https://code.claude.com/docs/en/fullscreen)中滚动更流畅。

如果在 tmux 中运行，即使外部终端支持 Shift+Enter，也需要[下方的 tmux 配置](#配置-tmux)。

要将换行绑定到不同按键，或交换行为（Enter 插入换行、Shift+Enter 提交），在 [keybindings 文件](https://code.claude.com/docs/en/keybindings)中映射 `chat:newline` 和 `chat:submit` 动作。

## 启用 macOS 上的 Option 键快捷键

一些 Claude Code 快捷键使用 Option 键（如 Option+Enter 换行、Option+P 切换模型）。macOS 上大多数终端默认不将 Option 作为修饰键发送。终端中此设置通常标记为 "Use Option as Meta Key"。

**Apple Terminal：** 打开 Settings → Profiles → Keyboard，勾选 "Use Option as Meta Key"。

**iTerm2：** 打开 Settings → Profiles → Keys → General，将 Left Option key 和 Right Option key 设为 "Esc+"。

运行 `/terminal-setup` 在 iTerm2 中启用 Settings → General → Selection 下的 "Applications in terminal may access clipboard"，使 `/copy` 命令可以写入系统剪贴板。

**VS Code：** 在设置中添加 `"terminal.integrated.macOptionIsMeta": true`。

对于 Ghostty、Kitty 等终端，在终端配置文件中查找 Option-as-Alt 或 Option-as-Meta 设置。

## 获取终端铃声或通知

**当 Claude 完成任务或暂停等待权限提示时，它会触发通知事件。** 这让你可以在长任务运行时切换到其他工作。

默认情况下 Claude Code 仅在 Ghostty、Kitty 和 iTerm2 中发送桌面通知。其他终端中，设置 [`preferredNotifChannel`](https://code.claude.com/docs/en/settings#available-settings) 为 `"terminal_bell"` 响终端铃声，或配置 [Notification hook](#用-notification-hook-播放声音) 自定义声音或命令。

桌面通知通过 SSH 到达本地机器，远程会话仍可提醒你。

### 用 Notification hook 播放声音

在任何终端中可以配置 [Notification hook](https://code.claude.com/docs/en/hooks-guide#get-notified-when-claude-needs-input) 在 Claude 需要注意时播放声音或运行自定义命令：

```json
{
  "hooks": {
    "Notification": [
      {
        "hooks": [{ "type": "command", "command": "afplay /System/Library/Sounds/Glass.aiff" }]
      }
    ]
  }
}
```

## 配置 tmux

**当 Claude Code 在 tmux 中运行时，两件事默认会坏：** Shift+Enter 提交而非换行，桌面通知和[进度条](https://code.claude.com/docs/en/settings#available-settings)无法到达外部终端。在 `~/.tmux.conf` 中添加以下行，然后运行 `tmux source-file ~/.tmux.conf` 应用：

```bash
set -g allow-passthrough on
set -s extended-keys on
set -as terminal-features 'xterm*:extkeys'
```

- `allow-passthrough`：让通知和进度更新到达外部终端
- `extended-keys`：让 tmux 区分 Shift+Enter 和普通 Enter

## 匹配颜色主题

**使用 `/theme` 命令或 `/config` 中的主题选择器选择匹配终端的 Claude Code 主题。** 选择 auto 选项检测终端的亮/暗背景。Claude Code 不控制终端自身的颜色方案。

要自定义界面底部显示的内容，配置[自定义状态行](https://code.claude.com/docs/en/statusline)。

### 创建自定义主题

> [!NOTE]
> 自定义主题需要 Claude Code v2.1.118 及以上版本。

`/theme` 列出内置预设和自定义主题。在列表末尾选择 **New custom theme...** 交互式创建。

每个自定义主题是 `~/.claude/themes/` 中的一个 JSON 文件：

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 在 `/theme` 中显示的标签 |
| `base` | string | 起始的内置预设：`dark`、`light`、`dark-daltonized`、`light-daltonized`、`dark-ansi`、`light-ansi` |
| `overrides` | object | 颜色 token 名到颜色值的映射 |

颜色值支持 `#rrggbb`、`#rgb`、`rgb(r,g,b)`、`ansi256(n)` 或 `ansi:<name>`。

示例：

```json
{
  "name": "Dracula",
  "base": "dark",
  "overrides": {
    "claude": "#bd93f9",
    "error": "#ff5555",
    "success": "#50fa7b"
  }
}
```

Claude Code 监视 `~/.claude/themes/` 并在文件更改时重载，编辑器中的修改无需重启即可应用。

**主要颜色 token 类别：**

| 类别 | 示例 token |
|------|-----------|
| 文本和强调色 | `claude`、`text`、`inactive`、`subtle`、`permission` |
| 状态色 | `success`、`error`、`warning`、`merged` |
| 输入框和模式指示器 | `promptBorder`、`planMode`、`autoAccept`、`bashBorder` |
| Diff 渲染 | `diffAdded`、`diffRemoved`、`diffAddedWord`、`diffRemovedWord` |
| 全屏模式 | `userMessageBackground`、`selectionBg` |
| 使用量计量器 | `rate_limit_fill`、`rate_limit_empty` |

## 切换到全屏渲染

**如果显示闪烁或 Claude 工作时滚动位置跳动，切换到[全屏渲染模式](https://code.claude.com/docs/en/fullscreen)。** 它在终端为全屏应用保留的独立屏幕上绘制，保持平稳内存并支持鼠标滚动和选择。

运行 `/tui fullscreen` 在当前会话中切换。要设为默认：

```bash
CLAUDE_CODE_NO_FLICKER=1 claude
```

或在 settings.json 中设置：

```json
{
  "env": {
    "CLAUDE_CODE_NO_FLICKER": "1"
  }
}
```

## 粘贴大量内容

**粘贴超过 10,000 字符到 prompt 时，Claude Code 将输入折叠为 `[Pasted text]` 占位符保持输入框可用。** 完整内容在提交时仍会发送给 Claude。

VS Code 集成终端可能在非常大的粘贴中丢失字符，推荐使用基于文件的工作流。对于整个文件或长日志等非常大的输入，将内容写入文件并让 Claude 读取。

## 用 Vim 键绑定编辑 Prompt

**Claude Code 包含 Vim 风格的 prompt 输入编辑模式。** 通过 `/config` → Editor mode 启用，或在 `~/.claude/settings.json` 中设置 `editorMode` 为 `"vim"`。

Vim 模式支持 NORMAL 和 VISUAL 模式的子集动作和操作符，如 `hjkl` 导航、`v`/`V` 选择、带文本对象的 `d`/`c`/`y`。完整按键表参见 [Vim editor mode reference](https://code.claude.com/docs/en/interactive-mode#vim-editor-mode)。

在 INSERT 模式下 Enter 仍提交 prompt（不像标准 Vim）。使用 NORMAL 模式的 `o`/`O` 或 Ctrl+J 插入换行。

## 相关资源

- [交互模式](https://code.claude.com/docs/en/interactive-mode)：完整键盘快捷键参考和 Vim 按键表
- [Keybindings](https://code.claude.com/docs/en/keybindings)：重映射任何 Claude Code 快捷键
- [全屏渲染](https://code.claude.com/docs/en/fullscreen)：全屏模式下滚动、搜索和复制的详情
- [Hooks 指南](https://code.claude.com/docs/en/hooks-guide)：更多 Linux 和 Windows 的 Notification hook 示例
- [故障排除](https://code.claude.com/docs/en/troubleshooting)：终端配置之外的问题修复
