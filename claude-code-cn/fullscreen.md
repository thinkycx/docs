---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】全屏渲染
description: 全屏渲染是 Claude Code CLI 的替代渲染模式，消除闪烁、保持平稳内存使用、支持鼠标操作。在备用屏幕缓冲区绘制界面，只渲染当前可见的消息。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/fullscreen.md
  - en-source/fullscreen.md
---

# 全屏渲染

> 启用更流畅、无闪烁的渲染模式，支持鼠标操作和长对话中稳定的内存使用。

> [!NOTE]
> 全屏渲染是选择加入的[研究预览](#研究预览)功能，需要 Claude Code v2.1.89 及以上版本。运行 `/tui fullscreen` 在当前对话中切换，或在 v2.1.110 之前设置 `CLAUDE_CODE_NO_FLICKER=1`。行为可能根据反馈调整。

**全屏渲染是 Claude Code CLI 的替代渲染路径，消除闪烁、保持平稳内存、支持鼠标。** 它在终端的备用屏幕缓冲区上绘制界面（像 `vim` 或 `htop`），只渲染当前可见的消息，减少每次更新发送到终端的数据量。

在 VS Code 集成终端、tmux 和 iTerm2 等渲染吞吐量成为瓶颈的终端模拟器中差异最明显。如果终端滚动位置在 Claude 工作时跳到顶部，或工具输出流入时屏幕闪烁，这个模式可以解决。

> [!NOTE]
> "全屏"描述的是 Claude Code 接管终端绘制表面的方式（像 `vim` 那样），与最大化终端窗口无关，在任何窗口大小下都可用。

## 启用全屏渲染

在任何 Claude Code 对话中运行 `/tui fullscreen`。CLI 保存 [`tui` 设置](https://code.claude.com/docs/en/settings#available-settings)并重新启动到全屏模式，对话完整保留。运行 `/tui default` 切换回经典渲染器，或 `/tui` 不带参数打印当前活跃的渲染器。

也可以在启动 Claude Code 前设置环境变量：

```bash
CLAUDE_CODE_NO_FLICKER=1 claude
```

## 变化了什么

**全屏渲染改变 CLI 绘制到终端的方式。** 输入框固定在屏幕底部而非随输出流动。如果 Claude 工作时输入不动，说明全屏渲染已激活。

因为对话在备用屏幕缓冲区而非终端滚动缓冲区中，有些操作不同：

| 之前 | 现在 | 详情 |
|------|------|------|
| `Cmd+f` 或 tmux 搜索查找文本 | `Ctrl+o` 进入转录模式，然后 `/` 搜索或 `[` 写入滚动缓冲区 | [搜索和查看对话](#搜索和查看对话) |
| 终端原生点击拖拽选择复制 | 应用内选择，鼠标释放时自动复制 | [使用鼠标](#使用鼠标) |
| `Cmd`-click 打开 URL | macOS 上 `Cmd`-click，其他平台 `Ctrl`-click | [使用鼠标](#使用鼠标) |

如果鼠标捕获干扰工作流，可以[关闭它](#保留原生文本选择)同时保持无闪烁渲染。

## 使用鼠标

**全屏渲染捕获鼠标事件并在 Claude Code 内处理：**

- **点击 prompt 输入框**：定位光标到文本任意位置
- **点击 `/` 命令或 `@` 文件列表中的建议**：接受它
- **点击选择菜单中的选项**：选择它（权限提示、`/model`、`/config` 等对话框）
- **点击折叠的工具结果**：展开查看完整输出，再次点击折叠
- **按住 `Cmd`(macOS) 或 `Ctrl`(Linux/Windows) 点击 URL 或文件路径**：打开它
- **点击拖拽**：选择对话中任意位置的文本。双击选择单词，三击选择行
- **滚轮滚动**：浏览对话

选中文本在鼠标释放时自动复制到剪贴板。要关闭此功能，在 `/config` 中切换 Copy on select。

关闭 Copy on select 后，按 `Ctrl+Shift+c` 手动复制。支持 kitty 键盘协议的终端中 `Cmd+c` 也可用。

## 滚动对话

全屏渲染在应用内处理滚动：

| 快捷键 | 动作 |
|--------|------|
| `PgUp` / `PgDn` | 向上/向下滚动半屏 |
| `Ctrl+Home` | 跳转到对话开头 |
| `Ctrl+End` | 跳转到最新消息并重新启用自动跟随 |
| 鼠标滚轮 | 每次滚动几行 |

MacBook 键盘没有专用 `PgUp`、`PgDn`、`Home`、`End` 键，按住 `Fn` 加方向键：`Fn+向上` 发送 `PgUp`，`Fn+向下` 发送 `PgDn`，`Fn+向左` 发送 `Home`，`Fn+向右` 发送 `End`。

这些动作可重新绑定。参见 [Scroll actions](https://code.claude.com/docs/en/keybindings#scroll-actions)。

### 自动跟随

**向上滚动会暂停自动跟随，新输出不会把你拉回底部。** 按 `Ctrl+End` 或滚动到底部恢复跟随。

要完全关闭自动跟随，在 `/config` 中将 Auto-scroll 设为 off。权限提示和需要响应的对话框无论此设置如何仍会滚入视图。

### 鼠标滚轮滚动

鼠标滚轮滚动需要终端将鼠标事件转发给 Claude Code。大多数终端会这样做。iTerm2 使其成为逐配置设置：如果滚轮无效但 `PgUp` 和 `PgDn` 可用，打开 Settings → Profiles → Terminal 启用 Enable mouse reporting。

如果鼠标滚轮滚动感觉慢，设置 `CLAUDE_CODE_SCROLL_SPEED` 倍增基础滚动距离：

```bash
export CLAUDE_CODE_SCROLL_SPEED=3
```

值 `3` 匹配 `vim` 和类似应用的默认值。接受 1 到 20 的值。

要交互式调整滚动速度，运行 `/scroll-speed`。

## 搜索和查看对话

**`Ctrl+o` 在正常 prompt 和转录模式间切换。**

要获得只显示最后 prompt、工具调用单行摘要和最终响应的安静视图，运行 `/focus`。

转录模式获得 `less` 风格的导航和搜索：

| 按键 | 动作 |
|------|------|
| `/` | 打开搜索。输入查找匹配，`Enter` 接受，`Esc` 取消 |
| `n` / `N` | 跳转到下/上一个匹配 |
| `j` / `k` 或 `向上` / `向下` | 滚动一行 |
| `g` / `G` 或 `Home` / `End` | 跳转到顶部/底部 |
| `Ctrl+u` / `Ctrl+d` | 滚动半页 |
| `Ctrl+b` / `Ctrl+f` 或 `Space` / `b` | 滚动整页 |
| `Ctrl+o`、`Esc` 或 `q` | 退出转录模式 |

终端的 `Cmd+f` 和 tmux 搜索看不到对话，因为它在备用屏幕缓冲区。要将内容传回终端，按 `Ctrl+o` 进入转录模式，然后：

- **`[`**：将完整对话写入终端原生滚动缓冲区（展开所有工具输出），之后 `Cmd+f`、tmux copy mode 等原生工具可以搜索
- **`v`**：将对话写入临时文件并在 `$VISUAL` 或 `$EDITOR` 中打开

## 清除对话

**2 秒内按两次 `Ctrl+L` 运行 `/clear` 开始新对话。** 第一次重绘屏幕并显示提示，第二次清除对话。macOS 上双按 `Cmd+K` 也运行 `/clear`。

## 在 tmux 中使用

全屏渲染在 tmux 中可用，有三个注意事项：

**鼠标滚轮滚动需要 tmux 的鼠标模式。** 在 `~/.tmux.conf` 中添加并重载配置：

```bash
set -g mouse on
```

**全屏渲染与 iTerm2 的 tmux 集成模式（`tmux -CC`）不兼容。** 在集成模式中备用屏幕缓冲区和鼠标跟踪无法正常工作。常规 tmux 在 iTerm2 中（不带 `-CC`）可以正常使用。

**并非所有 tmux 版本都应用来自应用的同步输出**，所以在 tmux 下可能比直接在终端中运行 Claude Code 看到更多闪烁。如果闪烁明显（特别是通过 SSH），升级到最新 tmux 或在 tmux 外的终端标签中运行 Claude Code。

## 保留原生文本选择

**鼠标捕获是最常见的摩擦点，特别是通过 SSH 或在 tmux 中。** 当 Claude Code 捕获鼠标事件时，终端原生的复制选择停止工作。

Claude Code 将选择写入系统剪贴板，使用的路径取决于设置：
- **macOS**：`pbcopy`
- **Linux**：Wayland 上 `wl-copy`，X11 上 `xclip` 或 `xsel`
- **Windows 和 WSL**：PowerShell `Set-Clipboard`
- **tmux 内**：也写入 tmux paste buffer
- **SSH**：回退到 OSC 52 转义序列

一次性原生选择时按住的键取决于终端：

| 终端 | 按键 |
|------|------|
| Terminal.app | `Fn` |
| iTerm2 | `Option` |
| VS Code、Cursor、Devin Desktop | `Shift`（macOS 上也可用 `Option`） |
| 大多数其他终端 | `Shift` |

**如果总是依赖原生选择，设置 `CLAUDE_CODE_DISABLE_MOUSE=1` 关闭鼠标捕获同时保持无闪烁渲染：**

```bash
CLAUDE_CODE_NO_FLICKER=1 CLAUDE_CODE_DISABLE_MOUSE=1 claude
```

鼠标捕获禁用后，键盘滚动仍可用。你失去的是点击定位光标、点击展开工具输出、URL 点击和滚轮滚动。

要保留滚轮滚动但关闭点击/拖拽/悬停处理，设置 `CLAUDE_CODE_DISABLE_MOUSE_CLICKS=1`（需要 v2.1.195+）。

## 研究预览

全屏渲染是研究预览功能。已在常见终端模拟器上测试，但不常见的终端或特殊配置可能遇到渲染问题。

如果遇到问题，在 Claude Code 内运行 `/feedback` 报告，或在 [claude-code GitHub repo](https://github.com/anthropics/claude-code/issues) 提 issue。

要关闭全屏渲染，运行 `/tui default`，或取消设置 `CLAUDE_CODE_NO_FLICKER`。要强制使用经典渲染器（忽略保存的 `tui` 设置），设置 `CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN=1`。
