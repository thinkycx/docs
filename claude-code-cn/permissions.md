---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】Claude Code 权限配置
description: Claude Code 的权限系统详解：分级权限机制、权限模式（default/auto/plan/bypassPermissions 等）、规则语法（Bash/Read/Edit/WebFetch/MCP 等工具的规则写法）、沙箱联动、托管策略、设置优先级。
category: translation
tags: [claude-code, permissions, security, translation]
refs:
  - https://code.claude.com/docs/en/permissions.md
---

# Claude Code 权限配置

> 通过细粒度权限规则、模式切换和托管策略，精确控制 Claude Code 能做什么、不能做什么。

Claude Code 支持细粒度权限——你可以精确指定 Agent 允许执行的操作和禁止的操作。权限设置可以提交版本控制、分发给所有开发者，也支持个人自定义。

---

## 权限体系

**Claude Code 的权限分三层：只读无需审批、修改类需确认、确认后记忆范围不同。**

| 工具类型 | 示例 | 是否需要审批 | "不再询问"的记忆范围 |
| :--- | :--- | :--- | :--- |
| 只读 | 文件读取、Grep | 否 | 不适用 |
| Bash 命令 | Shell 执行 | 是 | 永久（按项目目录+命令） |
| 文件修改 | Edit/Write 文件 | 是 | 仅当前会话 |

---

## 管理权限

**用 `/permissions` 查看和管理所有权限规则。**

`/permissions` 会列出所有权限规则及其来源的 `settings.json` 文件。

- **Allow** 规则：让 Claude Code 无需确认即可使用指定工具
- **Ask** 规则：Claude Code 使用指定工具时弹出确认
- **Deny** 规则：完全禁止 Claude Code 使用指定工具

规则按 deny → ask → allow 的优先级依次匹配。第一个命中的规则决定结果，规则的"具体程度"不影响优先级顺序。

一条宽泛的 deny 规则（如 `Bash(aws *)`）会阻止所有匹配的调用，即使同时存在更窄的 allow 规则（如 `Bash(aws s3 ls)`）。同理，ask 规则优先于 allow——匹配 ask 规则的调用即使同时匹配更具体的 allow 规则也照样弹确认框。

Deny 规则的行为取决于它是否带有模式匹配。裸工具名（如 `Bash`）会将工具从 Claude 的上下文中彻底移除——Claude 根本看不到它。带模式的规则（如 `Bash(rm *)`）保留工具可用性，仅在 Claude 实际调用时阻止匹配的命令。

> **注意：** 权限规则由 Claude Code 执行，不是由模型执行。你在 prompt 或 `CLAUDE.md` 中的指令只影响 Claude"想做什么"，不会改变 Claude Code"允许做什么"。要授予或撤销访问权限，用 `/permissions`、这里描述的规则、[权限模式](https://code.claude.com/docs/en/permission-modes) 或 [PreToolUse hook](#用-hooks-扩展权限)。

---

## 权限模式

**通过模式切换来全局控制工具审批策略。** 在 [settings 文件](https://code.claude.com/docs/en/settings#settings-files) 中设置 `defaultMode`。详见 [Permission modes](https://code.claude.com/docs/en/permission-modes)。

| 模式 | 描述 |
| :--- | :--- |
| `default` | 标准模式：每个工具首次使用时弹出确认 |
| `acceptEdits` | 自动接受文件编辑和常见文件系统命令（`mkdir`、`touch`、`mv`、`cp`），限于工作目录或 `additionalDirectories` |
| `plan` | 规划模式：Claude 读文件、跑只读命令来探索，但不修改源文件 |
| `auto` | 自动审批工具调用，后台安全检查验证操作是否符合你的请求。当前为研究预览版 |
| `dontAsk` | 自动拒绝工具，除非已通过 `/permissions` 或 `permissions.allow` 规则预批准 |
| `bypassPermissions` | 跳过权限提示，除非有显式 `ask` 规则强制弹出。`rm -rf /` 和 `rm -rf ~` 等根/家目录删除仍作为兜底保护弹出确认 |

> **警告：** `bypassPermissions` 模式跳过权限提示，包括对 `.git`、`.config/git`、`.claude`、`.vscode`、`.idea`、`.husky`、`.cargo`、`.devcontainer`、`.yarn`、`.mvn` 的写入。显式 `ask` 规则仍会强制弹出确认，根目录和家目录的删除操作仍会触发确认。仅在隔离环境（容器、虚拟机）中使用此模式。

要禁止使用 `bypassPermissions` 或 `auto` 模式，在任意 [settings 文件](https://code.claude.com/docs/en/settings#settings-files) 中设置 `permissions.disableBypassPermissionsMode` 或 `permissions.disableAutoMode` 为 `"disable"`。这在[托管设置](#托管设置)中最有用——因为那里不可被覆盖。

---

## 权限规则语法

**规则格式为 `Tool` 或 `Tool(specifier)`。**

### 匹配工具的所有用途

仅用工具名（不加括号）匹配该工具的一切调用：

| 规则 | 效果 |
| :--- | :--- |
| `Bash` | 匹配所有 Bash 命令 |
| `WebFetch` | 匹配所有 Web 请求 |
| `Read` | 匹配所有文件读取 |

`Bash(*)` 等价于 `Bash`，匹配所有 Bash 命令。作为 deny 规则时，两种写法都会将工具从 Claude 的上下文中移除。

### 用 specifier 做细粒度控制

在括号中加 specifier 匹配特定的工具使用：

| 规则 | 效果 |
| :--- | :--- |
| `Bash(npm run build)` | 精确匹配 `npm run build` 命令 |
| `Read(./.env)` | 匹配读取当前目录下的 `.env` 文件 |
| `WebFetch(domain:example.com)` | 匹配对 example.com 的请求 |

### 按输入参数匹配

Deny 和 ask 规则可以用 `Tool(param:value)` 匹配工具的顶层输入参数。当 Claude 调用工具时携带该参数且值匹配，规则生效。Allow 规则仍使用各工具自身的 specifier 语法（因为单个参数匹配无法证明调用整体安全）。

| 规则 | 匹配 |
| :--- | :--- |
| `Agent(model:opus)` | 请求 Opus 模型层级的 Agent 调用 |
| `Agent(isolation:worktree)` | 请求 git worktree 的 Agent 调用 |
| `Bash(run_in_background:true)` | 后台运行的 Bash 调用 |

参数匹配规则：

- 参数名必须是工具输入的直接字段（如 Agent 工具的 `model`），嵌套在对象或数组内的字段不可匹配
- 每条规则只能命名一个参数。要同时限制 `model` 和 `isolation`，需要写两条规则
- 值支持 `*` 通配——`Agent(isolation:*)` 匹配任何显式 isolation 值。不带 `*` 则精确匹配
- 模型省略的参数永远不被匹配——`Agent(model:*)` 不匹配未设置 `model` 的调用
- 值与 Claude 发送的原始输入比较，不经过标准化。`Agent(model:opus)` 匹配别名 `opus` 但不匹配完整 model ID。用 [`--verbose`](https://code.claude.com/docs/en/cli-reference) 查看每次工具调用的参数名和值
- 冒号两侧的空格被忽略

工具已有自身规范化规则的字段不能用此方式匹配：Bash/PowerShell 的 `command`、Read/Edit/Write 的 `file_path`、Grep/Glob 的 `path`、NotebookEdit 的 `notebook_path`、WebFetch 的 `url`。比如 `Bash(command:rm *)` 可被复合命令绕过，Claude Code 会忽略它并在启动时发出警告。应该用 `Bash(rm *)`、`Read(./path)` 或 `WebFetch(domain:host)` 代替。

### 通配符模式

Bash 规则支持 `*` 通配。通配符可出现在命令的任意位置。以下配置允许 npm 和 git commit 命令，但阻止 git push：

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(git commit *)",
      "Bash(git * main)",
      "Bash(* --version)",
      "Bash(* --help *)"
    ],
    "deny": [
      "Bash(git push *)"
    ]
  }
}
```

`*` 前面的空格很重要：`Bash(ls *)` 匹配 `ls -la` 但不匹配 `lsof`；而 `Bash(ls*)` 两者都匹配。`:*` 后缀是尾部通配的等价写法——`Bash(ls:*)` 匹配的命令与 `Bash(ls *)` 相同。

权限对话框中选择"Yes, don't ask again"时保存的是空格分隔形式。`:*` 形式仅在模式末尾被识别。在 `Bash(git:* push)` 这样的模式中，冒号被当作字面字符，不会匹配 git 命令。

### 工具名通配

Deny 和 ask 规则支持在工具名位置使用通配符。模式必须匹配完整工具名：`"*"` 匹配所有工具，`"mcp__*"` 匹配所有 MCP 服务器的所有工具。被裸名通配 deny 匹配的工具会从 Claude 上下文中移除。以下配置拒绝所有 MCP 工具：

```json
{
  "permissions": {
    "deny": [
      "mcp__*"
    ]
  }
}
```

Allow 规则仅在 `mcp__<server>__` 前缀之后接受通配符。server 段必须无通配——确保规则指向你配置的特定服务器。`mcp__puppeteer__*` 匹配 puppeteer 服务器的所有工具，`mcp__github__get_*` 匹配其 `get_` 开头的工具。不含锚定前缀的 allow 通配（如 `"*"`、`"B*"`、`"mcp__*"`）会被跳过并发出警告。

工具名匹配不到任何已知工具的 deny/ask 规则会产生启动警告以便排查拼写错误。包含 `_` 或 `*` 的工具名不受此检查限制。

工具在交互界面和 transcript 中的标签可能与其规范名不同。例如标签显示 `Stop Task` 的工具规范名是 `TaskStop`。权限规则和 [hook 匹配器](https://code.claude.com/docs/en/hooks) 只识别规范名。用 [tools reference](https://code.claude.com/docs/en/tools-reference) 查询规范名。

---

## 各工具的权限规则

### Bash

**Bash 规则支持 `*` 通配，可出现在命令任意位置。**

- `Bash(npm run build)` 精确匹配 `npm run build`
- `Bash(npm run test *)` 匹配以 `npm run test` 开头的命令
- `Bash(npm *)` 匹配以 `npm ` 开头的命令
- `Bash(* install)` 匹配以 ` install` 结尾的命令
- `Bash(git * main)` 匹配如 `git checkout main`、`git log --oneline main` 等

单个 `*` 匹配任意字符序列（含空格），一个通配符可跨越多个参数。`Bash(git *)` 匹配 `git log --oneline --all`，`Bash(git * main)` 匹配 `git push origin main` 和 `git merge main`。

当 `*` 出现在末尾且前面有空格时（如 `Bash(ls *)`），它强制词边界——前缀后必须跟空格或到达字符串末尾。`Bash(ls *)` 匹配 `ls -la` 但不匹配 `lsof`。而 `Bash(ls*)` 没有空格，两者都匹配。

#### 复合命令

> **提示：** Claude Code 能识别 shell 操作符。`Bash(safe-cmd *)` 这样的规则不会给 `safe-cmd && other-cmd` 放行。识别的命令分隔符包括 `&&`、`||`、`;`、`|`、`|&`、`&` 和换行符。规则必须独立匹配每个子命令。

选择"Yes, don't ask again"批准复合命令时，Claude Code 会为每个需要审批的子命令保存单独的规则（而非整条复合命令一条规则）。例如批准 `git status && npm test` 会保存 `npm test` 规则，后续单独的 `npm test` 也会被识别。子命令如 `cd` 进子目录会生成独立的 Read 规则。单次复合命令最多保存 5 条规则。

#### 进程包装器

匹配 Bash 规则前，Claude Code 会剥离一组固定的进程包装器——`Bash(npm test *)` 也能匹配 `timeout 30 npm test`。识别的包装器有：`timeout`、`time`、`nice`、`nohup`、`stdbuf`。

裸 `xargs` 也会被剥离——`Bash(grep *)` 匹配 `xargs grep pattern`。但只在 `xargs` 没有参数时生效；`xargs -n1 grep pattern` 会被当作 `xargs` 命令匹配，内部命令的规则不覆盖它。

此包装器列表是内置的、不可配置。开发环境运行器如 `direnv exec`、`devbox run`、`mise exec`、`npx`、`docker exec` 不在列表中。由于这些工具会将其参数作为命令执行，`Bash(devbox run *)` 会匹配 `run` 后的任何内容（包括 `devbox run rm -rf .`）。要批准环境运行器内的工作，应写同时包含运行器和内部命令的具体规则（如 `Bash(devbox run npm test)`），每个要允许的内部命令写一条。

执行包装器如 `watch`、`setsid`、`ionice`、`flock` 始终弹出确认，不能被前缀规则（如 `Bash(watch *)`）自动批准。`find` 带 `-exec` 或 `-delete` 同理：`Bash(find *)` 规则不覆盖这些形式。要批准特定调用，写完整命令的精确匹配规则。

#### 只读命令

Claude Code 内置识别一组 Bash 命令为只读，在所有模式下不弹确认。包括 `ls`、`cat`、`echo`、`pwd`、`head`、`tail`、`grep`、`find`、`wc`、`which`、`diff`、`stat`、`du`、`cd`，以及只读形式的 `git`。此集合不可配置；要对这些命令强制弹确认，加 `ask` 或 `deny` 规则。

所有 flag 均为只读的命令允许未引用的 glob 模式——`ls *.ts` 和 `wc -l src/*.py` 不弹确认。带有写/执行能力 flag 的命令（如 `find`、`sort`、`sed`、`git`）在存在未引用 glob 时仍会弹确认——因为 glob 可能展开为 `-delete` 之类的 flag。

`cd` 到工作目录或 [additional directory](#工作目录) 内的路径也是只读的。`cd packages/api && ls` 这样的复合命令在每部分都单独满足条件时不弹确认。`cd` 和 `git` 组合在同一复合命令中始终弹确认，无论目标目录如何。

> **警告：** 试图约束命令参数的 Bash 权限模式天生脆弱。例如 `Bash(curl http://github.com/ *)` 意图限制 curl 只访问 GitHub，但无法匹配：
>
> - 选项在 URL 前：`curl -X GET http://github.com/...`
> - 不同协议：`curl https://github.com/...`
> - 重定向：`curl -L http://bit.ly/xyz`（重定向到 GitHub）
> - 变量：`URL=http://github.com && curl $URL`
> - 多余空格：`curl  http://github.com`
>
> 更可靠的 URL 过滤方案：
> - **限制 Bash 网络工具**：用 deny 规则阻止 `curl`、`wget` 等，用 WebFetch 工具配合 `WebFetch(domain:github.com)` 权限放行允许的域名
> - **用 PreToolUse hooks**：实现 hook 验证 Bash 命令中的 URL 并阻止不允许的域名
> - **加 CLAUDE.md 引导**：在 `CLAUDE.md` 中描述允许的 curl 模式。这能引导 Claude 的行为但不构成强制边界，需与上述方案配合使用
>
> 注意：仅用 WebFetch 不能阻止网络访问。如果 Bash 被允许，Claude 仍可通过 `curl`、`wget` 等工具访问任何 URL。

### PowerShell

**PowerShell 规则与 Bash 规则形状相同。** 通配符 `*` 可出现在任意位置，`:*` 后缀等价于尾部 ` *`，裸 `PowerShell` 或 `PowerShell(*)` 匹配所有命令。

```json
{
  "permissions": {
    "allow": [
      "PowerShell(Get-ChildItem *)",
      "PowerShell(git commit *)"
    ],
    "deny": [
      "PowerShell(Remove-Item *)"
    ]
  }
}
```

常见别名会被规范化后匹配。为 cmdlet 名写的规则也匹配其别名——`PowerShell(Get-ChildItem *)` 匹配 `gci`、`ls`、`dir`。匹配不区分大小写。

Claude Code 解析 PowerShell AST，独立检查复合命令中的每个命令。管道操作符 `|`、语句分隔符 `;`，以及 PowerShell 7+ 的链式操作符 `&&` 和 `||` 将复合命令拆分为子命令。规则必须匹配每个子命令才能放行整条复合命令。

### Read 和 Edit

**`Edit` 规则适用于所有内置的文件编辑工具。** Claude 会尽力将 `Read` 规则应用于所有内置的文件读取工具（如 Grep、Glob）、prompt 中的 `@file` 引用，以及连接的 [IDE](https://code.claude.com/docs/en/vs-code#the-built-in-ide-mcp-server) 共享的选中内容和打开文件上下文。

> **警告：** Read 和 Edit deny 规则适用于 Claude 的内置文件工具以及 Claude Code 在 Bash 中识别的文件命令（如 `cat`、`head`、`tail`、`sed`）。它们不适用于间接读写文件的任意子进程（如自行打开文件的 Python 或 Node 脚本）。要实现 OS 级别阻止所有进程访问路径的效果，启用 [sandbox](https://code.claude.com/docs/en/sandboxing)。

Read 和 Edit 规则遵循 [gitignore](https://git-scm.com/docs/gitignore) 规范，有四种路径模式：

| 模式 | 含义 | 示例 | 匹配 |
| :--- | :--- | :--- | :--- |
| `//path` | 从文件系统根的绝对路径 | `Read(//Users/alice/secrets/**)` | `/Users/alice/secrets/**` |
| `~/path` | 从 home 目录的路径 | `Read(~/Documents/*.pdf)` | `/Users/alice/Documents/*.pdf` |
| `/path` | 相对于项目根的路径 | `Edit(/src/**/*.ts)` | `<项目根>/src/**/*.ts` |
| `path` 或 `./path` | 相对于当前目录的路径 | `Read(*.env)` | `<cwd>/*.env` |

> **警告：** `/Users/alice/file` 不是绝对路径，它是相对于项目根的。绝对路径请用 `//Users/alice/file`。

Windows 上路径会被标准化为 POSIX 形式：`C:\Users\alice` 变为 `/c/Users/alice`。用 `//c/**/.env` 匹配该驱动器上所有 `.env` 文件，用 `//**/.env` 跨所有驱动器匹配。

示例：

- `Edit(/docs/**)`：编辑 `<项目>/docs/`，不包括 `/docs/` 或 `<项目>/.claude/docs/`
- `Read(~/.zshrc)`：读取 home 目录的 `.zshrc`
- `Edit(//tmp/scratch.txt)`：编辑绝对路径 `/tmp/scratch.txt`
- `Read(src/**)`：读取 `<当前目录>/src/`

规则只匹配其锚点下的文件，锚点决定 deny 规则的覆盖范围。裸文件名遵循 gitignore 语义——在任意深度匹配。`Read(.env)` 和 `Read(**/.env)` 等价：

| Deny 规则 | 阻止 | 不阻止 |
| :--- | :--- | :--- |
| `Read(.env)` 或 `Read(**/.env)` | 当前目录及其子目录下的所有 `.env` | 父目录或其他项目中的 `.env` |
| `Read(//**/.env)` | 文件系统上所有位置的 `.env` | 无（规则锚定在文件系统根） |

> **说明：** 在 gitignore 模式中，`*` 匹配单个路径段内的字符（可出现在模式任意位置），`**` 跨目录匹配。要允许所有文件访问，只用不带括号的工具名：`Read`、`Edit` 或 `Write`。

当 Claude 访问符号链接时，权限规则检查两个路径：符号链接本身和它解析到的文件。Allow 和 deny 规则对这对路径的处理不同：

- **Allow 规则**：仅当符号链接路径和目标路径都匹配时生效。允许目录内指向外部的符号链接仍会弹出确认
- **Deny 规则**：符号链接路径或目标路径任一匹配即生效。指向被 deny 文件的符号链接本身也被 deny

例如，`Read(./project/**)` 允许、`Read(~/.ssh/**)` 禁止时，`./project/key` 指向 `~/.ssh/id_rsa` 的符号链接被阻止：目标不满足 allow 规则且匹配 deny 规则。

### WebFetch

**WebFetch 规则用 `domain:` 前缀，按请求 URL 的主机名匹配。** 匹配不区分大小写，支持 `*` 通配，且会剥离尾部 `.`——`example.com.` 和 `example.com` 等价。

- `WebFetch(domain:example.com)` 匹配 `example.com`
- `WebFetch(domain:*.example.com)` 匹配任意深度的子域名（如 `api.example.com`、`a.b.example.com`），但不匹配 `example.com` 本身
- `WebFetch(domain:*)` 匹配所有域名，等价于裸 `WebFetch` 规则

在非开头 `*.` 或裸 `*` 的位置，通配符只匹配两个点之间的文本。`WebFetch(domain:example.*)` 匹配 `example.org`（`*` 变为 `org`），但不匹配 `example.evil.com`（`*` 需跨越点变为 `evil.com`）。这防止尾部通配匹配到攻击者可注册的域名。

### MCP

**MCP 规则使用 Claude Code 中配置的服务器名，可选加工具名。**

- `mcp__puppeteer` 匹配 puppeteer 服务器提供的任何工具
- `mcp__puppeteer__*` 用通配语法，同样匹配 puppeteer 服务器的所有工具
- `mcp__puppeteer__puppeteer_navigate` 匹配 puppeteer 服务器提供的 `puppeteer_navigate` 工具

### Agent（子 Agent）

**用 `Agent(AgentName)` 规则控制 Claude 可以使用的 [子 Agent](https://code.claude.com/docs/en/sub-agents)：**

- `Agent(Explore)` 匹配 Explore 子 Agent
- `Agent(Plan)` 匹配 Plan 子 Agent
- `Agent(my-custom-agent)` 匹配名为 `my-custom-agent` 的自定义子 Agent

将这些规则加入 settings 的 `deny` 数组或用 `--disallowedTools` CLI flag 禁用特定 Agent。禁用 Explore Agent 的示例：

```json
{
  "permissions": {
    "deny": ["Agent(Explore)"]
  }
}
```

### Cd

**`Cd` 规则控制 [`/cd` 命令](https://code.claude.com/docs/en/commands) 能切换到哪些目录。** `Cd` 不是模型可调用的工具——Claude 无法调用它，规则仅在你运行 `/cd` 时生效。

裸 `Cd` deny 规则完全禁用 `/cd`。`Cd(<path-pattern>)` deny 规则阻止匹配的目标。Deny 规则检查目标的所有拼写方式（包括符号链接解析经过的每一跳），因此为一个路径写的规则也会阻止解析到它的目标。

添加任何 `Cd` allow 规则会将 `/cd` 切换为白名单模式：解析后的目标目录必须匹配某条 allow 规则，否则 `/cd` 拒绝执行。未配置任何 `Cd` 规则时，`/cd` 保持默认行为——遇到陌生目录时弹出信任确认。

路径模式与 [Read 和 Edit 规则](#read-和-edit) 共享 `//`、`~/`、`/` 锚点，但匹配锚定到整个目录路径。`*` 匹配恰好一个路径段，`**` 跨段匹配。尾部 `/**` 也匹配其命名的根：

| 规则 | 匹配 | 不匹配 |
| :--- | :--- | :--- |
| `Cd(~/code/*)` | `~/code/app` | `~/code/app/src`、`~/code` |
| `Cd(~/code/**)` | `~/code` 及其下所有目录 | `~/code` 之外的目录 |
| `Cd(**/node_modules)` | 任意深度的 `node_modules` 目录 | `node_modules/pkg` |

---

## 用 Hooks 扩展权限

**[Claude Code hooks](https://code.claude.com/docs/en/hooks-guide) 允许注册自定义 shell 命令在运行时做权限评估。**

Claude Code 发起工具调用时，PreToolUse hooks 在权限提示之前运行。Hook 输出可以拒绝工具调用、强制弹出提示、或跳过提示让调用继续。

Hook 决策不能绕过权限规则。无论 PreToolUse hook 返回什么，deny 和 ask 规则照样评估——deny 规则阻止调用，ask 规则照样弹确认（即使 hook 返回了 `"allow"` 或 `"ask"`）。这保持了[管理权限](#管理权限)中描述的 deny 优先级，包括托管设置中的 deny 规则。

阻止型 hook 也优先于 allow 规则。以退出码 2 退出的 hook 会在权限规则评估之前停止工具调用——即使 allow 规则本来会放行。要实现"所有 Bash 命令不弹确认但特定几个要阻止"，把 `"Bash"` 加入 allow 列表，再注册一个 PreToolUse hook 拒绝那些特定命令。参见 [Block edits to protected files](https://code.claude.com/docs/en/hooks-guide#block-edits-to-protected-files) 了解可适配的 hook 脚本。

---

## 工作目录

**默认情况下 Claude 只能访问你启动时所在的目录。** 可以扩展访问范围：

| 方式 | 说明 |
| :--- | :--- |
| 启动时 | `--add-dir <path>` CLI 参数 |
| 会话中 | `/add-dir` 命令 |
| 持久配置 | 在 [settings 文件](https://code.claude.com/docs/en/settings#settings-files) 中添加 `additionalDirectories` |

附加目录中的文件遵循与原始工作目录相同的权限规则：无需确认即可读取，文件编辑权限跟随当前权限模式。

要更改会话的主工作目录（而非添加另一个），用 [`/cd`](https://code.claude.com/docs/en/commands)（需 v2.1.169+）。与 `/add-dir` 不同，`/cd` 会迁移会话：加载新目录的 `CLAUDE.md`，`--resume` 从那里找到会话。

### 附加目录授予文件访问，不授予配置

**添加目录仅扩展 Claude 可读写文件的范围，不使该目录成为完整的配置根。** 大部分 `.claude/` 配置不会从附加目录发现，但有少量例外。

这些例外仅适用于通过 `--add-dir` flag 或 `/add-dir` 命令添加的目录。settings 文件中 `permissions.additionalDirectories` 列出的目录仅授予文件访问，不加载以下任何配置。

从 `--add-dir` 目录加载的配置：

| 配置 | 是否从 `--add-dir` 加载 |
| :--- | :--- |
| [Skills](https://code.claude.com/docs/en/skills) 在 `.claude/skills/` | 是，支持热重载 |
| [子 Agent](https://code.claude.com/docs/en/sub-agents) 在 `.claude/agents/` | 是 |
| [Settings](https://code.claude.com/docs/en/settings) 在 `.claude/settings.json` 和 `.claude/settings.local.json` | 仅 `enabledPlugins` 和 `extraKnownMarketplaces` 键 |
| [CLAUDE.md](https://code.claude.com/docs/en/memory) 文件、`.claude/rules/`、`CLAUDE.local.md` | 仅当设置 `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` 时。`CLAUDE.local.md` 还需要 `local` 设置来源（默认启用） |

命令和输出样式从当前工作目录及其父目录、`~/.claude/` 和托管设置中发现。Hooks 和其他 `settings.json` 键从当前工作目录的 `.claude/` 文件夹加载（无父目录回溯），加上 `~/.claude/settings.json` 和托管设置。要跨项目共享配置，用以下方式：

- **用户级配置**：将文件放在 `~/.claude/agents/`、`~/.claude/output-styles/` 或 `~/.claude/settings.json`，在所有项目中可用
- **插件**：打包为 [plugin](https://code.claude.com/docs/en/plugins) 分发给团队安装
- **从配置目录启动**：在包含所需 `.claude/` 配置的目录中运行 Claude Code

---

## 权限与沙箱的联动

**权限和 [沙箱](https://code.claude.com/docs/en/sandboxing) 是互补的安全层。**

| 层面 | 作用范围 |
| :--- | :--- |
| 权限 | 控制 Claude Code 能用哪些工具、访问哪些文件或域名。适用于所有工具（Bash、Read、Edit、WebFetch、MCP） |
| 沙箱 | 提供 OS 级强制执行，限制 Bash 工具的文件系统和网络访问。仅适用于 Bash 命令及其子进程 |

两者配合实现纵深防御：

- 权限 deny 规则阻止 Claude 尝试访问受限资源
- 沙箱限制阻止 Bash 命令触达定义边界之外的资源——即使 prompt 注入绕过了 Claude 的决策
- 沙箱的文件系统限制合并 [`sandbox.filesystem`](https://code.claude.com/docs/en/sandboxing) 设置与 Read/Edit deny 规则，最终形成沙箱边界
- 网络限制合并 WebFetch 权限规则与沙箱的 `allowedDomains` 和 `deniedDomains` 列表

启用沙箱且 `autoAllowBashIfSandboxed: true`（默认值）时，被沙箱保护的 Bash 命令不弹确认——即使权限包含裸 `Bash` ask 规则或[等价的 `Bash(*)` 形式](#匹配工具的所有用途)。沙箱边界替代了整工具级别的确认。以下检查仍然生效：

- 带内容的 ask 规则（如 `Bash(git push *)`）仍强制弹确认
- 显式 deny 规则仍生效
- `rm` 或 `rmdir` 命令目标为 `/`、home 目录或其他关键系统路径时仍触发确认

不会在沙箱内运行的命令（如被排除的命令）仍遵守裸 `Bash` ask 规则。参见 [sandbox modes](https://code.claude.com/docs/en/sandboxing#sandbox-modes) 更改此行为。

---

## 托管设置

**对于需要集中控制 Claude Code 配置的组织，管理员可以部署不可被用户或项目设置覆盖的托管设置。**

托管策略与常规 settings 文件格式相同，可通过 MDM/OS 级策略、托管设置文件或 [server-managed settings](https://code.claude.com/docs/en/server-managed-settings) 分发。分发机制和文件位置参见 [settings files](https://code.claude.com/docs/en/settings#settings-files)。

### 仅限托管的设置

**以下设置仅从托管设置中读取，放在用户或项目设置文件中无效。**

| 设置 | 描述 |
| :--- | :--- |
| `allowAllClaudeAiMcps` | 为 `true` 时，claude.ai connectors 与已部署的 `managed-mcp.json` 并行加载而非被其排他控制抑制。参见 [Managed MCP configuration](https://code.claude.com/docs/en/managed-mcp) |
| `allowedChannelPlugins` | 可推送消息的 channel 插件白名单。设置时替换默认 Anthropic 白名单。需 `channelsEnabled: true`。参见 [Restrict which channel plugins can run](https://code.claude.com/docs/en/channels#restrict-which-channel-plugins-can-run) |
| `allowManagedHooksOnly` | 为 `true` 时，仅加载托管 hooks、SDK hooks 和托管设置 `enabledPlugins` 中强制启用的插件 hooks。用户、项目和所有其他插件 hooks 被阻止 |
| `allowManagedMcpServersOnly` | 为 `true` 时，仅尊重托管设置中的 `allowedMcpServers`。`deniedMcpServers` 仍从所有来源合并。参见 [Managed MCP configuration](https://code.claude.com/docs/en/managed-mcp) |
| `allowManagedPermissionRulesOnly` | 为 `true` 时，阻止用户和项目设置定义 `allow`、`ask` 或 `deny` 权限规则。仅托管设置中的规则生效。不影响 MCP 服务器白名单（用 `allowManagedMcpServersOnly`） |
| `blockedMarketplaces` | 市场来源黑名单。被阻止的来源在下载前检查，不会接触文件系统。参见 [managed marketplace restrictions](https://code.claude.com/docs/en/plugin-marketplaces#managed-marketplace-restrictions) |
| `channelsEnabled` | 为组织启用 [channels](https://code.claude.com/docs/en/channels)。参见 [enterprise controls](https://code.claude.com/docs/en/channels#enterprise-controls) 了解各计划的默认值 |
| `forceRemoteSettingsRefresh` | 为 `true` 时，CLI 启动前阻塞直到远程托管设置重新获取完毕，获取失败则退出。参见 [fail-closed enforcement](https://code.claude.com/docs/en/server-managed-settings#enforce-fail-closed-startup) |
| `pluginTrustMessage` | 附加到安装前插件信任警告的自定义消息 |
| `sandbox.filesystem.allowManagedReadPathsOnly` | 为 `true` 时，仅尊重托管设置中的 `filesystem.allowRead` 路径。`denyRead` 仍从所有来源合并 |
| `sandbox.network.allowManagedDomainsOnly` | 为 `true` 时，仅尊重托管设置中的 `allowedDomains` 和 `WebFetch(domain:...)` allow 规则。非允许域名自动阻止而不提示用户。denied 域名仍从所有来源合并 |
| `strictKnownMarketplaces` | 控制用户可以添加和安装插件的市场来源。参见 [managed marketplace restrictions](https://code.claude.com/docs/en/plugin-marketplaces#managed-marketplace-restrictions) |
| `strictPluginOnlyCustomization` | 阻止来自用户和项目来源的 skills、agents、hooks 和 MCP servers，使其只能来自插件或托管设置。`true` 锁定全部四个表面；数组（如 `["skills", "hooks"]`）只锁定指定的。参见 [`strictPluginOnlyCustomization`](https://code.claude.com/docs/en/settings#strictpluginonlycustomization) |
| `wslInheritsWindowsSettings` | Windows HKLM 注册表键或 `C:\Program Files\ClaudeCode\managed-settings.json` 中为 `true` 时，WSL 除读取 `/etc/claude-code` 外还从 Windows 策略链读取托管设置。参见 [Settings files](https://code.claude.com/docs/en/settings#settings-files) |

`disableBypassPermissionsMode` 通常放在托管设置中执行组织策略，但它在任何作用域都生效。用户可以在自己的设置中设置它来锁住自己不用 bypass 模式。

> **说明：** 在 Team 和 Enterprise 计划中，Owner 在 [Claude Code admin settings](https://claude.ai/admin-settings/claude-code) 中为整个组织启用或禁用 [Remote Control](https://code.claude.com/docs/en/remote-control) 和 [web sessions](https://code.claude.com/docs/en/claude-code-on-the-web)。Remote Control 还可通过 [`disableRemoteControl`](https://code.claude.com/docs/en/settings#available-settings) 设置按设备禁用。Web sessions 没有按设备的托管设置键。

---

## 设置优先级

**权限规则遵循与所有 Claude Code 设置相同的 [优先级](https://code.claude.com/docs/en/settings#settings-precedence)：**

1. **托管设置**：不能被任何其他级别覆盖（包括命令行参数）
2. **命令行参数**：临时会话覆盖
3. **本地项目设置**（`.claude/settings.local.json`）
4. **共享项目设置**（`.claude/settings.json`）
5. **用户设置**（`~/.claude/settings.json`）

如果某工具在任何级别被 deny，其他级别都无法 allow 它。例如托管设置的 deny 无法被 `--allowedTools` 覆盖，而 `--disallowedTools` 可以在托管设置基础上添加更多限制。

跨设置作用域同理：如果用户设置 allow 了某权限而项目设置 deny 了它，deny 规则生效。反过来也成立——用户级 deny 阻止项目级 allow，因为任何作用域的 deny 规则都在 allow 规则之前评估。

嵌入宿主可通过 SDK `managedSettings` 选项在 [`parentSettingsBehavior`](https://code.claude.com/docs/en/settings#settings-precedence) 设为 `"merge"` 时提供额外的托管策略；嵌入方的值只能收紧策略、不能放松。

---

## 示例配置

这个 [仓库](https://github.com/anthropics/claude-code/tree/main/examples/settings) 包含常见部署场景的起始 settings 配置。以它们为起点，根据需求调整。

---

## 参见

- [Settings](https://code.claude.com/docs/en/settings)：完整配置参考（含权限设置表）
- [Configure auto mode](https://code.claude.com/docs/en/auto-mode-config)：告诉 auto 模式分类器你的组织信任哪些基础设施
- [Sandboxing](https://code.claude.com/docs/en/sandboxing)：Bash 命令的 OS 级文件系统和网络隔离
- [Authentication](https://code.claude.com/docs/en/authentication)：设置 Claude Code 的用户访问
- [Security](https://code.claude.com/docs/en/security)：安全保障和最佳实践
- [Hooks](https://code.claude.com/docs/en/hooks-guide)：自动化工作流和扩展权限评估
