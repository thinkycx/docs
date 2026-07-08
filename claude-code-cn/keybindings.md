---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】快捷键配置
description: Claude Code 支持自定义快捷键绑定，通过 keybindings.json 配置文件实现个性化的键盘操作。本文详细列出所有可用上下文、动作和按键语法。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/keybindings.md
  - en-source/keybindings.md
---

# 自定义快捷键

> 通过 keybindings 配置文件自定义 Claude Code 的键盘快捷键。

**自定义快捷键需要 Claude Code v2.1.18 或更高版本。** 用 `claude --version` 查看当前版本。

Claude Code 支持自定义快捷键。运行 `/keybindings` 可创建或打开配置文件 `~/.claude/keybindings.json`。

## 配置文件

**keybindings 配置文件是一个包含 `bindings` 数组的 JSON 对象。** 每个 block 指定一个上下文和按键到动作的映射。

修改 keybindings 文件后会自动检测并生效，无需重启 Claude Code。

| 字段 | 说明 |
| :--- | :--- |
| `$schema` | 可选，JSON Schema URL，用于编辑器自动补全 |
| `$docs` | 可选，文档链接 |
| `bindings` | 按上下文分组的绑定数组 |

下面的示例将 `Ctrl+E` 绑定到在 Chat 上下文中打开外部编辑器，并解除 `Ctrl+U` 的绑定：

```json
{
  "$schema": "https://www.schemastore.org/claude-code-keybindings.json",
  "$docs": "https://code.claude.com/docs/en/keybindings",
  "bindings": [
    {
      "context": "Chat",
      "bindings": {
        "ctrl+e": "chat:externalEditor",
        "ctrl+u": null
      }
    }
  ]
}
```

## 上下文

**每个绑定 block 指定一个上下文（context），表示绑定在哪些场景下生效：**

| 上下文 | 说明 |
| :--- | :--- |
| `Global` | 应用内所有位置生效 |
| `Chat` | 主聊天输入区 |
| `Autocomplete` | 自动补全菜单打开时 |
| `Settings` | 设置菜单 |
| `Confirmation` | 权限确认和确认对话框 |
| `Tabs` | Tab 导航组件 |
| `Help` | 帮助菜单可见时 |
| `Transcript` | 对话记录查看器 |
| `HistorySearch` | 历史搜索模式（Ctrl+R） |
| `Task` | 后台任务运行时 |
| `ThemePicker` | 主题选择对话框 |
| `Attachments` | 图片附件导航 |
| `Footer` | 底部指示器导航（任务、团队、diff） |
| `MessageSelector` | 回退和总结对话框中的消息选择 |
| `DiffDialog` | Diff 查看器导航 |
| `ModelPicker` | 模型选择器的 effort 级别 |
| `Select` | 通用选择/列表组件 |
| `Plugin` | 插件对话框（浏览、发现、管理） |
| `Scroll` | 全屏模式下的对话滚动和文本选择 |
| `Doctor` | `/doctor` 诊断界面 |

## 可用动作

**动作遵循 `namespace:action` 格式。** 例如 `chat:submit` 发送消息，`app:toggleTodos` 显示任务列表。每个上下文有各自可用的动作。

### App 动作

`Global` 上下文中可用的动作：

| 动作 | 默认键 | 说明 |
| :--- | :--- | :--- |
| `app:interrupt` | Ctrl+C | 取消当前操作 |
| `app:exit` | Ctrl+D | 退出 Claude Code |
| `app:redraw` | （未绑定） | 强制终端重绘 |
| `app:toggleTodos` | Ctrl+T | 切换 Claude 的待办清单可见性。不是 [`/tasks`](https://code.claude.com/docs/en/commands) 后台任务视图 |
| `app:toggleTranscript` | Ctrl+O | 切换详细对话记录 |

### 历史动作

命令历史导航相关的动作：

| 动作 | 默认键 | 说明 |
| :--- | :--- | :--- |
| `history:search` | Ctrl+R | 打开历史搜索 |
| `history:previous` | Up | 上一条历史 |
| `history:next` | Down | 下一条历史 |

### Chat 动作

`Chat` 上下文中可用的动作：

| 动作 | 默认键 | 说明 |
| :--- | :--- | :--- |
| `chat:cancel` | Escape | 取消当前输入 |
| `chat:clearInput` | Ctrl+L | 强制全屏重绘并保留输入。在[全屏渲染](https://code.claude.com/docs/en/fullscreen#clear-the-conversation)中，2 秒内按两次执行 `/clear` |
| `chat:clearScreen` | Cmd+K | 在[全屏渲染](https://code.claude.com/docs/en/fullscreen#clear-the-conversation)中，2 秒内按两次执行 `/clear` |
| `chat:killAgents` | Ctrl+X Ctrl+K | 终止本会话所有运行中的[后台子代理](https://code.claude.com/docs/en/sub-agents#run-subagents-in-foreground-or-background) |
| `chat:cycleMode` | Shift+Tab* | 切换权限模式 |
| `chat:modelPicker` | Meta+P | 打开模型选择器 |
| `chat:fastMode` | Meta+O | 切换快速模式 |
| `chat:thinkingToggle` | Meta+T | 切换扩展思考 |
| `chat:submit` | Enter | 发送消息 |
| `chat:newline` | Ctrl+J | 插入换行而不发送 |
| `chat:undo` | Ctrl+_, Ctrl+Shift+- | 撤销上一步 |
| `chat:externalEditor` | Ctrl+G, Ctrl+X Ctrl+E | 在外部编辑器中打开 |
| `chat:stash` | Ctrl+S | 暂存当前 prompt |
| `chat:imagePaste` | Ctrl+V（Windows/WSL 上为 Alt+V） | 从剪贴板粘贴图片。WSL 上两个快捷键默认都绑定 |

*在无 VT 模式的 Windows（Node <24.2.0/<22.17.0，Bun <1.2.23）上，默认为 Meta+M。

### 自动补全动作

`Autocomplete` 上下文中可用的动作：

| 动作 | 默认键 | 说明 |
| :--- | :--- | :--- |
| `autocomplete:accept` | Tab | 接受建议 |
| `autocomplete:dismiss` | Escape | 关闭菜单 |
| `autocomplete:previous` | Up | 上一条建议 |
| `autocomplete:next` | Down | 下一条建议 |

### 确认动作

`Confirmation` 上下文中可用的动作：

| 动作 | 默认键 | 说明 |
| :--- | :--- | :--- |
| `confirm:yes` | Y, Enter | 确认 |
| `confirm:no` | N, Escape | 拒绝 |
| `confirm:previous` | Up | 上一个选项 |
| `confirm:next` | Down | 下一个选项 |
| `confirm:nextField` | Tab | 下一个字段 |
| `confirm:previousField` | （未绑定） | 上一个字段 |
| `confirm:toggle` | Space | 切换选择 |
| `confirm:cycleMode` | Shift+Tab | 切换权限模式 |
| `confirm:toggleExplanation` | Ctrl+E | 切换权限说明 |

### 权限动作

`Confirmation` 上下文中权限对话框可用的动作：

| 动作 | 默认键 | 说明 |
| :--- | :--- | :--- |
| `permission:toggleDebug` | （未绑定） | 切换权限调试信息。v2.1.146 移除了之前的 Ctrl+D 默认绑定，因为它遮蔽了 `app:exit` |

### 对话记录动作

`Transcript` 上下文中可用的动作：

| 动作 | 默认键 | 说明 |
| :--- | :--- | :--- |
| `transcript:toggleShowAll` | Ctrl+E | 切换显示全部内容 |
| `transcript:exit` | q, Ctrl+C, Escape | 退出记录视图 |

### 历史搜索动作

`HistorySearch` 上下文中可用的动作：

| 动作 | 默认键 | 说明 |
| :--- | :--- | :--- |
| `historySearch:next` | Ctrl+R | 下一个匹配 |
| `historySearch:accept` | Escape, Tab | 接受选择 |
| `historySearch:cancel` | Ctrl+C | 取消搜索 |
| `historySearch:execute` | Enter | 执行选中的命令 |
| `historySearch:cycleScope` | Ctrl+S | 切换范围：会话、项目、全局 |

### 任务动作

`Task` 上下文中可用的动作：

| 动作 | 默认键 | 说明 |
| :--- | :--- | :--- |
| `task:background` | Ctrl+B, Ctrl+X Ctrl+B | 将当前任务转为后台。Ctrl+X Ctrl+B 组合键需要 v2.1.169 或更高版本，可避免 tmux 前缀冲突 |

### 主题动作

`ThemePicker` 上下文中可用的动作：

| 动作 | 默认键 | 说明 |
| :--- | :--- | :--- |
| `theme:toggleSyntaxHighlighting` | Ctrl+T | 切换语法高亮 |

### 帮助动作

`Help` 上下文中可用的动作：

| 动作 | 默认键 | 说明 |
| :--- | :--- | :--- |
| `help:dismiss` | Escape | 关闭帮助菜单 |

### Tab 动作

`Tabs` 上下文中可用的动作：

| 动作 | 默认键 | 说明 |
| :--- | :--- | :--- |
| `tabs:next` | Tab, Right | 下一个 tab |
| `tabs:previous` | Shift+Tab, Left | 上一个 tab |

### 附件动作

`Attachments` 上下文中可用的动作：

| 动作 | 默认键 | 说明 |
| :--- | :--- | :--- |
| `attachments:next` | Right | 下一个附件 |
| `attachments:previous` | Left | 上一个附件 |
| `attachments:remove` | Backspace, Delete | 移除选中的附件 |
| `attachments:exit` | Down, Escape | 退出附件导航 |

### Footer 动作

`Footer` 上下文中可用的动作：

| 动作 | 默认键 | 说明 |
| :--- | :--- | :--- |
| `footer:next` | Right | 下一个 footer 项 |
| `footer:previous` | Left | 上一个 footer 项 |
| `footer:up` | Up | 向上导航（顶部时取消选择） |
| `footer:down` | Down | 向下导航 |
| `footer:openSelected` | Enter | 打开选中的 footer 项 |
| `footer:clearSelection` | Escape | 清除 footer 选择 |

### 消息选择动作

`MessageSelector` 上下文中可用的动作：

| 动作 | 默认键 | 说明 |
| :--- | :--- | :--- |
| `messageSelector:up` | Up, K, Ctrl+P | 列表上移 |
| `messageSelector:down` | Down, J, Ctrl+N | 列表下移 |
| `messageSelector:top` | Ctrl+Up, Shift+Up, Meta+Up, Shift+K | 跳到顶部 |
| `messageSelector:bottom` | Ctrl+Down, Shift+Down, Meta+Down, Shift+J | 跳到底部 |
| `messageSelector:select` | Enter | 选择消息 |

### Diff 动作

`DiffDialog` 上下文中可用的动作：

| 动作 | 默认键 | 说明 |
| :--- | :--- | :--- |
| `diff:dismiss` | Escape | 关闭 diff 查看器 |
| `diff:previousSource` | Left | 上一个 diff 来源 |
| `diff:nextSource` | Right | 下一个 diff 来源 |
| `diff:previousFile` | Up, K | 文件列表中上一个文件；详情视图中向上滚动一行 |
| `diff:nextFile` | Down, J | 文件列表中下一个文件；详情视图中向下滚动一行 |
| `diff:viewDetails` | Enter | 查看 diff 详情 |
| `diff:back` | （视上下文而定） | 返回 diff 查看器上一级 |

Diff 详情视图还将类似 pager 的按键绑定到标准[滚动动作](#滚动动作)。这些绑定属于 `DiffDialog` 上下文，仅在详情视图中生效：

| 动作 | 默认键 | 说明 |
| :--- | :--- | :--- |
| `scroll:pageUp` | PageUp | 向上滚动半个视口 |
| `scroll:pageDown` | PageDown | 向下滚动半个视口 |
| `scroll:fullPageUp` | Shift+Space, B | 向上滚动整个视口 |
| `scroll:fullPageDown` | Space | 向下滚动整个视口 |
| `scroll:top` | G, Home | 跳到顶部 |
| `scroll:bottom` | Shift+G, End | 跳到底部 |

### 模型选择器动作

`ModelPicker` 上下文中可用的动作：

| 动作 | 默认键 | 说明 |
| :--- | :--- | :--- |
| `modelPicker:decreaseEffort` | Left | 降低 effort 级别 |
| `modelPicker:increaseEffort` | Right | 提高 effort 级别 |
| `modelPicker:thisSessionOnly` | s | 仅对本会话应用高亮模型 |

### Select 动作

`Select` 上下文中可用的动作：

| 动作 | 默认键 | 说明 |
| :--- | :--- | :--- |
| `select:next` | Down, J, Ctrl+N | 下一个选项 |
| `select:previous` | Up, K, Ctrl+P | 上一个选项 |
| `select:accept` | Enter | 接受选择 |
| `select:cancel` | Escape | 取消选择 |

### Plugin 动作

`Plugin` 上下文中可用的动作：

| 动作 | 默认键 | 说明 |
| :--- | :--- | :--- |
| `plugin:toggle` | Space | 切换插件选择 |
| `plugin:install` | I | 安装选中的插件 |
| `plugin:favorite` | F | 收藏选中的插件，使其在 Installed 标签页靠前排列 |

### Settings 动作

`Settings` 上下文中可用的动作。`select:accept` 和 `confirm:no` 动作复用自 [Select](#select-动作) 和 [确认动作](#确认动作) 上下文，但行为适配了 Settings 场景：每个设置修改即生效，所以 Escape 关闭面板时修改已经保存。

| 动作 | 默认键 | 说明 |
| :--- | :--- | :--- |
| `settings:search` | / | 进入搜索模式 |
| `settings:retry` | R | 出错时重试加载用量数据 |
| `select:accept` | Enter, Space | 修改选中的设置或打开其子菜单 |
| `confirm:no` | Escape | 关闭面板。修改已保存 |

### Doctor 动作

`Doctor` 上下文中可用的动作：

| 动作 | 默认键 | 说明 |
| :--- | :--- | :--- |
| `doctor:fix` | F | 将诊断报告发送给 Claude 来修复问题。仅在发现问题时激活 |

### 语音动作

启用[语音输入](https://code.claude.com/docs/en/voice-dictation)时 `Chat` 上下文中可用的动作：

| 动作 | 默认键 | 说明 |
| :--- | :--- | :--- |
| `voice:pushToTalk` | Space | 语音输入 prompt。根据 `/voice` 模式决定按住还是点按 |

### 滚动动作

启用[全屏渲染](https://code.claude.com/docs/en/fullscreen)时 `Scroll` 上下文中可用的动作：

| 动作 | 默认键 | 说明 |
| :--- | :--- | :--- |
| `scroll:lineUp` | （未绑定） | 向上滚动一行。鼠标滚轮触发此动作 |
| `scroll:lineDown` | （未绑定） | 向下滚动一行。鼠标滚轮触发此动作 |
| `scroll:pageUp` | PageUp | 向上滚动半个视口高度 |
| `scroll:pageDown` | PageDown | 向下滚动半个视口高度 |
| `scroll:top` | Ctrl+Home | 跳到对话开头 |
| `scroll:bottom` | Ctrl+End | 跳到最新消息并重新启用自动跟随 |
| `scroll:halfPageUp` | （未绑定） | 向上滚动半个视口。与 `scroll:pageUp` 行为相同，提供 vi 风格重绑定 |
| `scroll:halfPageDown` | （未绑定） | 向下滚动半个视口。与 `scroll:pageDown` 行为相同，提供 vi 风格重绑定 |
| `scroll:fullPageUp` | （未绑定） | 向上滚动整个视口高度 |
| `scroll:fullPageDown` | （未绑定） | 向下滚动整个视口高度 |
| `selection:copy` | Ctrl+Shift+C / Cmd+C | 复制选中文本到剪贴板 |
| `selection:clear` | （未绑定） | 清除当前文本选择 |
| `selection:extendLeft` | Shift+Left | 向左扩展选择一列 |
| `selection:extendRight` | Shift+Right | 向右扩展选择一列 |
| `selection:extendUp` | Shift+Up | 向上扩展选择一行。选择到顶部边缘时滚动视口 |
| `selection:extendDown` | Shift+Down | 向下扩展选择一行。选择到底部边缘时滚动视口 |
| `selection:extendLineStart` | Shift+Home | 扩展选择到行首 |
| `selection:extendLineEnd` | Shift+End | 扩展选择到行尾 |

## 按键语法

### 修饰键

使用 `+` 分隔符组合修饰键：

- `ctrl` 或 `control` — Control 键
- `shift` — Shift 键
- `alt`、`opt`、`option` 或 `meta` — Windows/Linux 上的 Alt 键，macOS 上的 Option 键
- `cmd`、`command`、`super` 或 `win` — macOS 上的 Command 键，Windows 上的 Win 键，Linux 上的 Super 键

`cmd` 组仅在支持 Super 修饰符的终端中检测，如支持 Kitty 键盘协议或 xterm 的 `modifyOtherKeys` 模式的终端。大多数终端不发送它，所以如果要让绑定在所有终端中生效，请使用 `ctrl` 或 `meta`。

示例：

```text
ctrl+k          Ctrl + K
shift+tab       Shift + Tab
meta+p          macOS 上 Option + P，其他平台 Alt + P
ctrl+shift+c    多修饰键组合
```

### 大写字母

**单独的大写字母隐含 Shift。** 例如 `K` 等同于 `shift+k`。这对 vim 风格绑定很有用。

带修饰键的大写字母（如 `ctrl+K`）仅作风格处理，不隐含 Shift：`ctrl+K` 与 `ctrl+k` 相同。

### 组合键（Chords）

**组合键是用空格分隔的按键序列：**

```text
ctrl+k ctrl+s   先按 Ctrl+K，释放，再按 Ctrl+S
```

### 特殊键

- `escape` 或 `esc` — Escape 键
- `enter` 或 `return` — Enter 键
- `tab` — Tab 键
- `space` — 空格键
- `up`、`down`、`left`、`right` — 方向键
- `backspace`、`delete` — 删除键

## 解除默认快捷键

**将动作设为 `null` 即可解除默认快捷键绑定：**

```json
{
  "bindings": [
    {
      "context": "Chat",
      "bindings": {
        "ctrl+s": null
      }
    }
  ]
}
```

这也适用于组合键绑定。解除共享同一前缀的所有组合键后，该前缀就可以作为单键绑定使用。任何活动上下文中的组合键都会保留其前缀，所以必须在定义它的上下文中逐个解除。

默认的 `Ctrl+X` 系列跨两个上下文：`Chat` 中的 `ctrl+x ctrl+k` 和 `ctrl+x ctrl+e`，以及 `Task` 中的 `ctrl+x ctrl+b`。要释放 `ctrl+x` 本身作为单键绑定，需要解除所有这些：

```json
{
  "bindings": [
    {
      "context": "Task",
      "bindings": {
        "ctrl+x ctrl+b": null
      }
    },
    {
      "context": "Chat",
      "bindings": {
        "ctrl+x ctrl+k": null,
        "ctrl+x ctrl+e": null,
        "ctrl+x": "chat:newline"
      }
    }
  ]
}
```

如果只解除了部分组合键，按下前缀仍会进入组合键等待模式。

## 保留快捷键

**以下快捷键无法重新绑定：**

| 快捷键 | 原因 |
| :--- | :--- |
| Ctrl+C | 硬编码的中断/取消 |
| Ctrl+D | 硬编码的退出 |
| Ctrl+M | 在终端中与 Enter 相同（都发送 CR） |
| Caps Lock | 终端应用无法接收 |

## 终端冲突

**部分快捷键可能与终端多路复用器冲突：**

| 快捷键 | 冲突 |
| :--- | :--- |
| Ctrl+B | tmux 前缀（需按两次发送） |
| Ctrl+A | GNU screen 前缀 |
| Ctrl+Z | Unix 进程挂起（SIGTSTP） |

## Vim 模式交互

**通过 `/config` → Editor mode 启用 vim 模式后，快捷键绑定和 vim 模式独立运作：**

- **Vim 模式** 在文本输入层处理输入（光标移动、模式切换、动作）
- **快捷键绑定** 在组件层处理操作（切换待办、提交等）
- Vim 模式中的 Escape 切换 INSERT 到 NORMAL 模式，不触发 `chat:cancel`
- 大多数 Ctrl+key 快捷键穿透 vim 模式到达快捷键绑定系统
- Vim NORMAL 模式中，`?` 显示帮助菜单（vim 行为）
- Vim NORMAL 模式中，`/` 打开历史搜索，等同于标准模式的 Ctrl+R

## 验证

**Claude Code 会验证你的快捷键配置，对以下情况显示警告：**

- 解析错误（无效的 JSON 或结构）
- 无效的上下文名称
- 保留快捷键冲突
- 终端多路复用器冲突
- 同一上下文中的重复绑定

运行 `/doctor` 可查看快捷键相关警告。
