---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】调试配置
description: 当 CLAUDE.md、settings、hooks、MCP 服务器或 skills 未生效时，使用 /context、/doctor、/hooks、/mcp 等命令诊断配置加载问题，找出真正被加载的内容。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/debug-your-config.md
  - en-source/debug-your-config.md
---

# 调试配置

> 诊断 CLAUDE.md、settings、hooks、MCP 服务器或 skills 未生效的原因。使用 /context、/doctor、/hooks 和 /mcp 查看实际加载了什么。

**当 Claude 忽略了你的指令或配置的功能没有出现时，原因通常是文件没有加载、从非预期的位置加载、或被其他文件覆盖。** 本指南教你如何检查 Claude Code 实际加载了什么，从而缩小问题范围。

安装、认证和网络连接问题请参见[安装排错](https://code.claude.com/docs/en/troubleshoot-install)。

## 查看加载到上下文中的内容

**`/context` 命令显示当前会话上下文窗口中的所有内容**，按类别分组：系统 prompt、memory 文件、skills、自定义子代理及其来源、MCP 工具、对话消息。先运行它确认你的 `CLAUDE.md`、规则或 skill 描述是否存在。

针对特定类别可用专属命令跟进：

| 命令 | 显示内容 |
| :--- | :--- |
| `/memory` | 已加载的 `CLAUDE.md` 和规则文件，以及自动记忆 |
| `/skills` | 来自项目、用户和插件的可用 skills |
| `/hooks` | 当前活动的 hook 配置 |
| `/mcp` | 已连接的 MCP 服务器及其状态 |
| `/permissions` | 当前生效的 allow 和 deny 规则 |
| `/doctor` | 配置诊断：无效的键、schema 错误、安装健康状态。v2.1.196 起还会报告同一作用域中重复的[子代理](https://code.claude.com/docs/en/sub-agents)名称并标记哪个生效 |
| `/debug [issue]` | 启用调试日志并提示 Claude 使用日志输出和设置路径进行诊断 |
| `/status` | 活动的设置来源，包括托管设置是否生效 |

如果 `/memory` 中缺少某个文件，请对照 [CLAUDE.md 文件加载机制](https://code.claude.com/docs/en/memory#how-claude-md-files-load) 检查其位置。子目录的 `CLAUDE.md` 文件在 Claude 用 Read 工具读取该目录中的文件时按需加载，不是在会话启动时加载。

如果 `/memory` 确认文件已加载但 Claude 仍未遵循某条指令，问题通常出在指令的写法而非是否被加载。CLAUDE.md 对"新队友式"的指导内容效果最好，如项目约定、构建命令、文件归属等。

当指令模糊到可有多种解读、两个文件给出冲突的方向、或文件过长导致单条规则关注度下降时，遵从度会下降。[编写有效指令](https://code.claude.com/docs/en/memory#write-effective-instructions)介绍了保持高遵从度的具体性、大小和结构模式。

> CLAUDE.md 和权限解决不同问题。CLAUDE.md 告诉 Claude 项目的工作方式以便做出好决策。[权限](https://code.claude.com/docs/en/permissions)和 [hooks](https://code.claude.com/docs/en/hooks) 强制执行限制，无论 Claude 做何决策。用 CLAUDE.md 表达"我们这里这样做"，用权限或 hooks 设置安全边界和绝不允许发生的事情——需要保证而非指引时。

## 检查已解析的设置

**设置从 managed、user、project 和 local 作用域合并。** Managed 设置始终优先。其余的按 local → project → user 的顺序，越近的覆盖越远的。部分设置也可通过命令行标志或[环境变量](https://code.claude.com/docs/en/env-vars)设置，作为另一个覆盖层。当某个设置未生效时，通常是被另一个作用域或环境变量覆盖了。

运行 `/doctor` 验证配置文件并发现无效的键或 schema 错误。当 `/doctor` 报告问题时，按 `f` 将诊断报告发给 Claude 让它帮你修复。

运行 `/status` 查看哪些设置来源处于活动状态，包括托管设置是否生效。要了解特定键的优先级，参见[作用域交互](https://code.claude.com/docs/en/settings#how-scopes-interact)。

## 检查 MCP 服务器

**运行 `/mcp` 查看每个已配置服务器的连接状态和审批情况。** 服务器可能定义正确但不提供工具，常见原因：

- `.mcp.json` 中的项目级服务器需要一次性审批。如果审批提示被关闭，服务器保持禁用状态，直到从 `/mcp` 中审批。
- 启动失败的服务器在 `/mcp` 中显示为 failed。`command` 或 `args` 中的相对路径是常见原因，因为它们相对于你启动 Claude Code 的目录而非 `.mcp.json` 的位置解析。
- 已连接但工具数为零的服务器已启动成功但未返回工具列表。从 `/mcp` 选择 **Reconnect**。如果数量仍为零，运行 `claude --debug mcp` 查看服务器的 stderr 输出。

配置位置和作用域规则参见 [MCP](https://code.claude.com/docs/en/mcp)。

## 检查 hooks

**运行 `/hooks` 列出当前会话中按事件分组的所有已注册 hook。** 如果你定义的 hook 没有出现，说明它未被读取：hooks 需在 settings 文件的 `"hooks"` 键下定义，不是独立文件。

如果 hook 出现但未触发，匹配器（matcher）通常是原因。`matcher` 字段是单个字符串，用 `|` 匹配多个工具名，如 `"Edit|Write"`。v2.1.191 起 `,` 也可作为分隔符，即 `"Edit,Write"` 等效。早期版本中逗号会落入正则表达式求值，matcher 永远不会匹配，所以如果不在 v2.1.191 以上请用 `|`。工具名拼写错误会以相同方式静默失败。数组值是 schema 错误：Claude Code 显示设置错误通知，`/doctor` 报告验证失败，hook 条目被丢弃因此不会出现在 `/hooks` 中。

编辑 `settings.json` 后会在短暂的文件稳定延迟后在运行中的会话生效，无需重启。如果保存几秒后 `/hooks` 仍显示旧定义，再次运行 `/hooks` 刷新视图。

如果 `/hooks` 显示了 hook 但仍不触发，下一步是实时观察 hook 求值。用 `claude --debug hooks` 启动会话并触发工具调用。调试日志记录每个事件、检查了哪些 matcher、以及 hook 的退出码和输出。参见 [Debug hooks](https://code.claude.com/docs/en/hooks#debug-hooks) 了解日志格式，[hooks 故障排除](https://code.claude.com/docs/en/hooks-guide#limitations-and-troubleshooting) 了解常见失败模式。

## 对比干净配置测试

**用 [`claude --safe-mode`](https://code.claude.com/docs/en/cli-reference#cli-flags) 启动会话**（需 v2.1.169 或更高版本），禁用所有自定义项，包括 CLAUDE.md、skills、plugins、hooks、MCP 服务器、自定义命令和代理。认证、模型选择、内置工具和权限正常工作。如果问题在安全模式下消失，说明是其中某个自定义项导致的；用上面的针对性检查找出具体是哪个。安全模式仍应用组织的托管 hooks 和设置策略。

如果问题在安全模式下仍存在，或你怀疑设置本身有问题，对比一个不加载任何常规配置的会话。将 [`CLAUDE_CONFIG_DIR`](https://code.claude.com/docs/en/env-vars) 指向空目录绕过 `~/.claude` 下的所有内容，并从没有 `.claude` 文件夹、`.mcp.json` 或 `CLAUDE.md` 的目录启动以跳过项目配置：

```bash
cd /tmp && CLAUDE_CONFIG_DIR=/tmp/claude-clean claude
```

干净会话没有用户或项目设置、hooks、MCP 服务器、插件或 memory。

- 如果你的组织部署了 Managed 设置，它们仍会生效，因为它们在 `~/.claude` 之外的系统路径
- 在 Linux 和 Windows 上，你会被提示重新登录，因为凭据存储在配置目录下
- 在 macOS 上，凭据在 Keychain 中，会延续到干净会话

如果问题在这里消失，原因在你的真实 `~/.claude` 或项目 `.claude` 文件中。逐个恢复它们以找出是哪个。如果仍存在，原因在用户和项目配置之外。运行 `/status` 检查托管设置是否生效，查找影响 Claude Code 的[环境变量](https://code.claude.com/docs/en/env-vars)，然后参见[故障排除](https://code.claude.com/docs/en/troubleshooting)。

## 常见原因速查

**大多数配置意外可追溯到少量位置和语法规则。** 检查这些再假设是 bug：

| 症状 | 原因 | 修复 |
| :--- | :--- | :--- |
| Hook 从不触发 | `matcher` 是 JSON 数组而非字符串 | 使用单个字符串加 `\|` 匹配多个工具，如 `"Edit\|Write"` |
| Hook 从不触发 | `matcher` 在 v2.1.191 之前使用 `,` 作为分隔符 | v2.1.191 起 `,` 等同于 `\|`。早期版本将逗号作为字面量求值。请使用 `\|` 或升级 |
| Hook 从不触发 | `matcher` 值为小写，如 `"bash"` | 匹配区分大小写。工具名首字母大写：`Bash`、`Edit`、`Write`、`Read` |
| Hook 从不触发 | Hooks 定义在独立文件而非 `settings.json` 中 | 项目或用户配置没有独立 hooks 文件。在 `settings.json` 的 `"hooks"` 键下定义。仅[插件](https://code.claude.com/docs/en/plugins-reference#hooks)加载单独的 `hooks/hooks.json` |
| 全局设置的权限、hooks 或 env 被忽略 | 配置写到了 `~/.claude.json` | `~/.claude.json` 存储应用状态和 UI 开关。`permissions`、`hooks` 和 `env` 应在 `~/.claude/settings.json` 中。这是两个不同的文件 |
| `settings.json` 中的值看似被忽略 | 同一个键在 `settings.local.json` 中设置了 | `settings.local.json` 覆盖 `settings.json`，两者都覆盖 `~/.claude/settings.json` |
| Skill 不出现在 `/skills` 中 | Skill 文件在 `.claude/skills/name.md` 而非文件夹中 | 使用文件夹加内部 `SKILL.md`：`.claude/skills/name/SKILL.md` |
| Skill 出现在 `/skills` 但 Claude 从不调用 | Skill frontmatter 中有 `disable-model-invocation: true`，或描述与请求措辞不匹配 | 在 `/skills` 中检查标记：`user-only` 标签表示 Claude 不会自主触发 |
| 子目录 `CLAUDE.md` 指令似乎被忽略 | 子目录文件按需加载，不在会话启动时 | 它们在 Claude 用 Read 工具读取该目录中的文件时加载，不是启动时，也不是写入或创建文件时 |
| 子代理忽略 `CLAUDE.md` 指令 | 内置的 Explore 和 Plan 代理跳过 `CLAUDE.md`。自定义子代理与主对话相同方式加载 | 对 Explore 或 Plan，在委派 prompt 中重述指令。对自定义子代理，将关键指令放在代理文件正文中（成为代理的系统 prompt） |
| 清理逻辑在会话结束时从不运行 | 未配置 `SessionEnd` hook | 在 `settings.json` 中添加 `SessionEnd` hook |
| `.mcp.json` 中的 MCP 服务器从不加载 | 文件在 `.claude/` 下或使用了 Claude Desktop 的配置格式 | 项目 MCP 配置在仓库根目录的 `.mcp.json`，不在 `.claude/` 内 |
| `settings.json` 中 `mcpServers` 下添加的 MCP 服务器从不出现 | `settings.json` 不读取 `mcpServers` 键 | 在仓库根目录的 `.mcp.json` 定义项目服务器，或运行 `claude mcp add --scope user` 添加用户级服务器 |
| 添加了项目 MCP 服务器但不出现 | 一次性审批提示被关闭 | 项目级服务器需要审批。运行 `/mcp` 查看状态并审批 |
| MCP 服务器在某些目录启动失败 | `command` 或 `args` 使用相对路径 | 本地脚本使用绝对路径。`PATH` 中的可执行文件如 `npx` 或 `uvx` 可直接使用 |
| MCP 服务器启动时缺少预期环境变量 | 变量在 `settings.json` 的 `env` 中，不会传播到 MCP 子进程 | 在 `.mcp.json` 中设置每个服务器的 `env` |
| `Bash(rm *)` deny 规则未阻止 `/bin/rm` 或 `find -delete` | 前缀规则匹配字面命令字符串，不是底层可执行文件 | 为每个变体添加显式模式，或使用 [PreToolUse hook](https://code.claude.com/docs/en/hooks-guide) 或[沙箱](https://code.claude.com/docs/en/sandboxing)作为硬保证 |

## 相关资源

- **[`.claude` 目录参考](https://code.claude.com/docs/en/claude-directory)**：每个配置文件位置及谁读取它
- **[设置](https://code.claude.com/docs/en/settings)**：优先级顺序和完整键列表
- **[Hooks 参考](https://code.claude.com/docs/en/hooks)**：事件名、负载和 `--debug hooks` 输出格式
- **[MCP](https://code.claude.com/docs/en/mcp)**：服务器配置、审批和 `/mcp` 输出
- **[安装排错](https://code.claude.com/docs/en/troubleshoot-install)**：`command not found`、PATH 和认证问题
- **[故障排除](https://code.claude.com/docs/en/troubleshooting)**：性能、挂起和搜索问题
