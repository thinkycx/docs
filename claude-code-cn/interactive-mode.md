---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】交互模式
description: Claude Code 交互模式的完整参考，涵盖键盘快捷键、输入模式、Vim 编辑、命令历史、后台任务、Shell 模式、Prompt 建议等交互功能。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/interactive-mode.md
  - en-source/interactive-mode.md
---

# 交互模式

> Claude Code 会话中键盘快捷键、输入模式和交互功能的完整参考。

## 键盘快捷键

> [!NOTE]
> 键盘快捷键可能因平台和终端而异。在[全屏渲染](https://code.claude.com/docs/en/fullscreen)中，在转录查看器按 `?` 查看可用快捷键。
>
> **macOS 用户**：Option/Alt 键快捷键（`Alt+B`、`Alt+F`、`Alt+Y`、`Alt+M`、`Alt+P`）需要在终端中将 Option 配置为 Meta：
> - **iTerm2**：Settings → Profiles → Keys → General → 设置 Left/Right Option key 为 "Esc+"
> - **Apple Terminal**：Settings → Profiles → Keyboard → 勾选 "Use Option as Meta Key"
> - **VS Code**：在 VS Code 设置中设置 `"terminal.integrated.macOptionIsMeta": true`
>
> 详见[终端配置](https://code.claude.com/docs/en/terminal-config)。

### 通用控制

| 快捷键 | 说明 | 上下文 |
|--------|------|--------|
| `Ctrl+C` | 中断或清除输入 | 中断运行中的操作。无操作运行时第一次清除输入，第二次退出 Claude Code |
| `Ctrl+X Ctrl+K` | 停止本会话所有后台子 Agent。3 秒内按两次确认 | 子 Agent 控制 |
| `Ctrl+D` | 退出 Claude Code 会话 | EOF 信号 |
| `Ctrl+G` 或 `Ctrl+X Ctrl+E` | 在默认文本编辑器中打开 | 用外部编辑器编辑 prompt 或自定义回复 |
| `Ctrl+L` | 重绘屏幕 | 强制完整终端重绘。显示乱了时使用 |
| `Ctrl+O` | 切换转录查看器 | 显示详细工具使用和执行信息 |
| `Ctrl+R` | 反向搜索命令历史 | 交互式搜索历史命令 |
| `Ctrl+V` 或 `Cmd+V`(iTerm2) 或 `Alt+V`(Windows/WSL) | 从剪贴板粘贴图片 | 插入 `[Image #N]` chip |
| `Ctrl+B` | 将运行中的任务放到后台 | 后台化 Bash 命令和 Agent。tmux 用户按两次 |
| `Ctrl+T` | 切换 Claude 任务清单 | 显示/隐藏 Claude 的 to-do 清单 |
| `Left/Right` 箭头 | 在对话框标签间切换 | 在权限对话框和菜单中导航 |
| `Up/Down` 箭头或 `Ctrl+P`/`Ctrl+N` | 移动光标或导航命令历史 | 多行输入中先在 prompt 内移动，到首/末行后导航历史 |
| `Esc` | 中断 Claude 或关闭对话框 | 停止当前响应或工具调用。对话框打开时关闭对话框 |
| `Esc` + `Esc` | 清除输入草稿或回退 | 有文本时清除并保存到历史。输入为空时打开[回退菜单](https://code.claude.com/docs/en/checkpointing) |
| `Shift+Tab` 或 `Alt+M` | 循环权限模式 | 在 `default`、`acceptEdits`、`plan` 等模式间切换 |
| `Option+P`(macOS) 或 `Alt+P`(Win/Linux) | 切换模型 | 不清除 prompt 切换模型 |
| `Option+T`(macOS) 或 `Alt+T`(Win/Linux) | 切换 extended thinking | 启用/禁用扩展思考模式 |
| `Option+O`(macOS) 或 `Alt+O`(Win/Linux) | 切换 fast mode | 启用/禁用[快速模式](https://code.claude.com/docs/en/fast-mode) |

### 文本编辑

| 快捷键 | 说明 |
|--------|------|
| `Ctrl+A` | 移动光标到当前行首 |
| `Ctrl+E` | 移动光标到当前行尾 |
| `Ctrl+K` | 删除到行尾 |
| `Ctrl+U` | 从光标删除到行首 |
| `Ctrl+W` | 删除前一个单词 |
| `Ctrl+Y` | 粘贴已删除的文本 |
| `Alt+Y`（`Ctrl+Y` 之后） | 循环粘贴历史 |
| `Alt+B` | 光标向后移动一个单词 |
| `Alt+F` | 光标向前移动一个单词 |

### 多行输入

| 方法 | 快捷键 | 说明 |
|------|--------|------|
| 快速转义 | `\` + `Enter` | 所有终端可用 |
| Option 键 | `Option+Enter` | macOS 启用 Option as Meta 后可用 |
| Shift+Enter | `Shift+Enter` | iTerm2、WezTerm、Ghostty、Kitty、Warp、Apple Terminal、Windows Terminal 原生支持 |
| 控制序列 | `Ctrl+J` | 任何终端无需配置 |
| 粘贴模式 | 直接粘贴 | 代码块、日志等 |

> [!TIP]
> Shift+Enter 在 iTerm2、WezTerm、Ghostty、Kitty、Warp、Apple Terminal 和 Windows Terminal 中无需配置。VS Code、Cursor、Devin Desktop、Alacritty 和 Zed 需要运行 `/terminal-setup` 安装绑定。

### 快捷命令

| 快捷键 | 说明 |
|--------|------|
| `/` 在行首 | 命令或 skill |
| `!` 在行首 | Shell 模式 |
| `@` | 文件路径提及，触发文件路径自动补全 |

### 转录查看器

`Ctrl+O` 打开转录查看器时可用的快捷键。在[全屏渲染](https://code.claude.com/docs/en/fullscreen)中按 `?` 显示完整快捷键参考面板。

| 快捷键 | 说明 |
|--------|------|
| `?` | 切换键盘快捷键帮助面板 |
| `{` / `}` | 跳转到上/下一个用户 prompt |
| `Ctrl+E` | 切换显示全部内容 |
| `[` | 将完整对话写入终端原生滚动缓冲区 |
| `v` | 将对话写入临时文件并在 `$VISUAL` 或 `$EDITOR` 中打开 |
| `q`、`Ctrl+C`、`Esc` | 退出转录视图 |

### 语音输入

| 快捷键 | 说明 |
|--------|------|
| 按住或轻按 `Space` | 语音听写。需要启用[语音听写](https://code.claude.com/docs/en/voice-dictation) |

## 命令

在 Claude Code 中输入 `/` 查看所有可用命令，或输入 `/` 后跟任何字母进行过滤。`/` 菜单显示所有可调用的内容：内置命令、[skills](https://code.claude.com/docs/en/skills)、以及 [plugins](https://code.claude.com/docs/en/plugins) 和 [MCP servers](https://code.claude.com/docs/en/mcp#use-mcp-prompts-as-commands) 贡献的命令。

完整命令列表参见[命令参考](https://code.claude.com/docs/en/commands)。

## Vim 编辑模式

通过 `/config` → Editor mode 启用 vim 风格编辑。

### 模式切换

| 命令 | 动作 | 来源模式 |
|------|------|----------|
| `Esc` | 进入 NORMAL 模式 | INSERT, VISUAL |
| `i` | 光标前插入 | NORMAL |
| `I` | 行首插入 | NORMAL |
| `a` | 光标后插入 | NORMAL |
| `A` | 行尾插入 | NORMAL |
| `o` | 在下方打开新行 | NORMAL |
| `O` | 在上方打开新行 | NORMAL |
| `v` | 字符级视觉选择 | NORMAL |
| `V` | 行级视觉选择 | NORMAL |

### 导航（NORMAL 模式）

| 命令 | 动作 |
|------|------|
| `h`/`j`/`k`/`l` | 左/下/上/右移动 |
| `w` | 下一个单词 |
| `e` | 单词末尾 |
| `b` | 上一个单词 |
| `0` | 行首 |
| `$` | 行尾 |
| `^` | 第一个非空白字符 |
| `gg` | 输入开头 |
| `G` | 输入末尾 |
| `f{char}` | 跳转到下一个字符出现处 |
| `F{char}` | 跳转到上一个字符出现处 |
| `t{char}` | 跳转到下一个字符出现处之前 |
| `T{char}` | 跳转到上一个字符出现处之后 |
| `;` | 重复上一次 f/F/t/T 动作 |
| `,` | 反向重复上一次 f/F/t/T 动作 |
| `/` | 打开反向历史搜索 |

> [!NOTE]
> 在 vim normal 模式下，如果光标在输入开头或末尾且无法进一步移动，`j`/`k` 和方向键改为导航命令历史。

### 编辑（NORMAL 模式）

| 命令 | 动作 |
|------|------|
| `x` | 删除字符 |
| `dd` | 删除行 |
| `D` | 删除到行尾 |
| `dw`/`de`/`db` | 删除单词/到末尾/向后 |
| `cc` | 修改行 |
| `C` | 修改到行尾 |
| `cw`/`ce`/`cb` | 修改单词/到末尾/向后 |
| `yy`/`Y` | 复制行 |
| `yw`/`ye`/`yb` | 复制单词/到末尾/向后 |
| `p` | 光标后粘贴 |
| `P` | 光标前粘贴 |
| `>>` | 缩进行 |
| `<<` | 减少缩进 |
| `J` | 连接行 |
| `u` | 撤销 |
| `.` | 重复上一次修改 |

### 文本对象（NORMAL 模式）

文本对象与 `d`、`c`、`y` 等操作符配合：

| 命令 | 动作 |
|------|------|
| `iw`/`aw` | 内部/周围单词 |
| `iW`/`aW` | 内部/周围 WORD（空白分隔） |
| `i"`/`a"` | 内部/周围双引号 |
| `i'`/`a'` | 内部/周围单引号 |
| `i(`/`a(` | 内部/周围圆括号 |
| `i[`/`a[` | 内部/周围方括号 |
| `i{`/`a{` | 内部/周围花括号 |

### Visual 模式

按 `v` 进行字符级选择或 `V` 进行行级选择。移动扩展选择，操作符直接作用于选择。

| 命令 | 动作 |
|------|------|
| `d`/`x` | 删除选择 |
| `y` | 复制选择 |
| `c`/`s` | 修改选择 |
| `p` | 用寄存器内容替换选择 |
| `r{char}` | 用 `{char}` 替换每个选中字符 |
| `~`/`u`/`U` | 切换/小写/大写选择 |
| `>`/`<` | 缩进或减少缩进选中行 |
| `J` | 连接选中行 |
| `o` | 交换光标和锚点 |

不支持 `Ctrl+V` 的块级 visual 模式。

## 命令历史

Claude Code 维护当前会话的命令历史：

- 输入历史按工作目录存储
- 运行 `/clear` 时输入历史重置。前一个会话的对话被保留，可以恢复
- 连续提交相同 prompt 只记录一条历史
- 使用 Up/Down 箭头导航
- 默认禁用 `!` 历史展开

### 使用 Ctrl+R 反向搜索

按 `Ctrl+R` 交互式搜索命令历史：

1. **启动搜索**：按 `Ctrl+R` 激活反向历史搜索
2. **输入查询**：输入文本搜索历史命令。匹配结果中搜索词高亮显示
3. **导航匹配**：再次按 `Ctrl+R` 在更早的匹配间循环
4. **更改范围**：搜索默认为所有项目的 prompt。按 `Ctrl+S` 在本会话、本项目和所有项目间循环
5. **接受匹配**：按 `Tab` 或 `Esc` 接受当前匹配并继续编辑；按 `Enter` 接受并立即执行
6. **取消搜索**：按 `Ctrl+C` 取消并恢复原始输入

## 后台 Bash 命令

**Claude Code 支持在后台运行 Bash 命令，允许你在长时间进程执行时继续工作。**

### 后台化工作原理

当 Claude Code 在后台运行命令时，它异步运行命令并立即返回后台任务 ID。你可以通过以下方式运行后台命令：

- 提示 Claude Code 在后台运行命令
- 按 `Ctrl+B` 将正在运行的 Bash 工具调用移到后台。tmux 用户需按两次

**关键特性：**
- 输出写入文件，Claude 可以用 Read 工具获取
- 后台任务有唯一 ID 用于跟踪和输出获取
- Claude Code 退出时自动清理后台任务
- 输出超过 5GB 时自动终止

要完全禁用后台任务功能，设置环境变量 `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` 为 `1`。

**常见后台命令：** 构建工具（webpack、vite、make）、包管理器（npm、yarn）、测试运行器（jest、pytest）、开发服务器、长运行进程（docker、terraform）。

### Shell 模式（`!` 前缀）

**在输入前加 `!` 直接运行 shell 命令，无需经过 Claude：**

```bash
! npm test
! git status
! ls -la
```

Shell 模式特性：
- 将命令和输出添加到对话上下文
- 显示实时进度和输出
- 支持 `Ctrl+B` 后台化
- 不需要 Claude 解释或批准命令
- 支持基于历史的自动补全
- 支持实时文件路径自动补全（v2.1.193+）
- 用 `Escape`、`Backspace` 或 `Ctrl+U`（空 prompt 时）退出

从 v2.1.186 起，Claude 会自动响应命令输出，无需第二个 prompt。要恢复旧行为，在 `settings.json` 中设置 `respondToBashCommands` 为 `false`。

## Prompt 建议

**首次打开会话时，输入框中会显示灰色的示例命令帮助你开始。** Claude Code 从项目的 git 历史中选取，反映你最近工作的文件。

Claude 响应后，建议继续基于对话历史出现。

- 按 `Tab` 或右箭头将建议放入输入框，然后 `Enter` 提交
- 开始输入即可忽略建议

建议作为后台请求运行，复用父对话的 prompt 缓存，额外成本最小。

要完全禁用 prompt 建议：

```bash
export CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION=false
```

## 使用 /btw 提问附带问题

**使用 `/btw` 快速提问而不影响对话历史。** 适合需要快速答案但不想打乱主上下文或干扰 Claude 正在进行的长任务。

```
/btw what was the name of that config file again?
```

附带问题特性：
- **Claude 工作时也可用**：可以在 Claude 处理响应时运行 `/btw`，不会中断主轮次
- **无工具访问**：只能从已有上下文回答，Claude 无法读取文件、运行命令或搜索
- **单次响应**：覆盖层中没有后续轮次。要继续线程可以用 `f` 分叉成独立会话
- **低成本**：复用父对话的 prompt 缓存

答案出现后覆盖层的按键：

| 按键 | 动作 |
|------|------|
| `Space`、`Enter`、`Escape` | 关闭答案返回 prompt |
| `Up` / `Down` | 滚动答案 |
| `Left` / `Right` | 在本次和之前的 `/btw` 答案间切换 |
| `c` | 将答案复制到剪贴板（原始 Markdown） |
| `f` | 分叉成新会话，继承父对话加此问答 |
| `x` | 清除之前的 `/btw` 交换列表 |

## 任务清单

**任务清单是 Claude 的 to-do 清单：** Claude 创建的用于规划多步骤工作的条目，带有待办/进行中/完成指示。

- 按 `Ctrl+T` 切换任务清单视图
- 要查看所有任务或清除它们，直接问 Claude
- 任务在上下文压缩后持久化
- 要跨会话共享任务清单，设置 `CLAUDE_CODE_TASK_LIST_ID`

## 会话回顾

**当你离开终端后返回时，Claude Code 显示一行会话摘要。** 回顾在后台生成（上次完成轮次后至少 3 分钟且终端未聚焦时），所以你切回来时已经准备好。

运行 `/recap` 可按需生成摘要。要关闭自动回顾，在 `/config` 中禁用 **Session recap**。

## PR 审查状态

**当在有打开 PR 的分支上工作时，Claude Code 在页脚显示可点击的 PR 链接**（如 "PR #446"），带颜色下划线指示审查状态：

| 颜色 | 状态 |
|------|------|
| 绿色 | 已批准 |
| 黄色 | 等待审查 |
| 红色 | 请求修改 |
| 灰色 | Draft |

PR 合并或关闭后徽章消失。`Cmd+click`(macOS) 或 `Ctrl+click`(Win/Linux) 在浏览器中打开 PR。状态每 60 秒刷新，`gh pr` 或 `git push` 命令运行后立即刷新。

> [!NOTE]
> PR 状态需要安装并认证 `gh` CLI（`gh auth login`）。

## 参见

- [Skills](https://code.claude.com/docs/en/skills) - 自定义 prompt 和工作流
- [Checkpointing](https://code.claude.com/docs/en/checkpointing) - 回退 Claude 的编辑并恢复之前的状态
- [CLI 参考](https://code.claude.com/docs/en/cli-reference) - 命令行标志和选项
- [Settings](https://code.claude.com/docs/en/settings) - 配置选项
- [Memory 管理](https://code.claude.com/docs/en/memory) - 管理 CLAUDE.md 文件
