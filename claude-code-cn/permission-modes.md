---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】权限模式
description: Claude Code 提供多种权限模式来控制操作审批流程，从逐一审批到完全自动化，适配不同安全需求和使用场景。本文详解各模式的行为差异、切换方式及受保护路径机制。
category: translation
tags: [claude-code, permission-modes, translation]
refs:
  - https://code.claude.com/docs/en/permission-modes.md
---

# 选择权限模式

**权限模式决定了 Claude 执行操作前是否需要你逐一确认——模式越宽松，中断越少，但你的掌控力也越低。**

当 Claude 想要编辑文件、执行 Shell 命令或发起网络请求时，默认会暂停等待你批准。权限模式控制着这种暂停发生的频率。默认模式下你需要逐一审查每个操作；而更宽松的模式允许 Claude 连续工作更长时间，完成后再汇报结果。敏感工作选严格模式，信任方向时选少打扰模式。

在 CLI 中按 `Shift+Tab` 循环切换模式，在 VS Code、Desktop 和 claude.ai 中使用模式选择器。

## 可用模式一览

| 模式 | 无需审批即可执行的操作 | 适用场景 |
| :--- | :--- | :--- |
| `default` | 仅读取 | 新手入门、敏感工作 |
| [`acceptEdits`](#acceptedits-模式自动批准文件编辑) | 读取、文件编辑、常用文件系统命令（`mkdir`、`touch`、`mv`、`cp` 等） | 边写边审的开发迭代 |
| [`plan`](#plan-模式先分析再动手) | 仅读取 | 改代码之前先摸清项目 |
| [`auto`](#auto-模式消除审批提示) | 所有操作（后台安全检查） | 长任务、减少审批疲劳 |
| [`dontAsk`](#dontask-模式仅允许预批准工具) | 仅预批准的工具 | CI 管道和受限脚本环境 |
| [`bypassPermissions`](#bypasspermissions-模式跳过所有检查) | 所有操作 | 仅限隔离容器和虚拟机 |

**在除 `bypassPermissions` 外的所有模式中，对[受保护路径](#受保护路径)的写入永远不会被自动批准**，以防仓库状态和 Claude 自身配置被意外破坏。

模式只是设定基线。你可以在此基础上叠加[权限规则](https://code.claude.com/docs/en/permissions#manage-permissions)来预批准或阻止特定工具。Deny 规则和显式 Ask 规则在所有模式下都生效，包括 `bypassPermissions`。Allow 规则在 `bypassPermissions` 下无效，因为所有操作本身已被允许。

## 切换权限模式

你可以在会话中途、启动时或作为持久默认值来切换模式。模式通过以下控件设置，而不是在聊天中向 Claude 发消息。

### CLI

**会话中切换**：按 `Shift+Tab` 循环 `default` → `acceptEdits` → `plan`。状态栏显示当前模式。以下模式不在默认循环中：

- `auto`：当账户满足 [auto 模式要求](#auto-模式消除审批提示)时出现。循环切到 auto 时会弹出确认提示，选择 **No, don't ask again** 可将 auto 从循环中移除
- `bypassPermissions`：需要用 `--permission-mode bypassPermissions`、`--dangerously-skip-permissions` 或 `--allow-dangerously-skip-permissions` 启动后才出现。`--allow-` 变体将该模式加入循环但不激活
- `dontAsk`：永远不出现在循环中，用 `--permission-mode dontAsk` 设置

可选模式排在 `plan` 之后，`bypassPermissions` 在前，`auto` 在后。如果两者都启用，切换时会先经过 `bypassPermissions` 再到 `auto`。

**启动时指定**：

```bash
claude --permission-mode plan
```

**设为默认**：在 [settings](https://code.claude.com/docs/en/settings#settings-files) 中设置 `defaultMode`：

```json
{
  "permissions": {
    "defaultMode": "acceptEdits"
  }
}
```

`--permission-mode` 参数同样适用于 `-p` [非交互模式](https://code.claude.com/docs/en/headless)。

### VS Code

**会话中切换**：点击输入框底部的模式指示器。

**设为默认**：在 VS Code 设置中配置 `claudeCode.initialPermissionMode`，或使用 Claude Code 扩展设置面板。

模式指示器的标签对应关系：

| UI 标签 | 对应模式 |
| :--- | :--- |
| Ask before edits | `default` |
| Edit automatically | `acceptEdits` |
| Plan mode | `plan` |
| Auto mode | `auto` |
| Bypass permissions | `bypassPermissions` |

Auto 模式在账户满足[所有要求](#auto-模式消除审批提示)时才出现。`claudeCode.initialPermissionMode` 设置不接受 `auto`。要默认以 auto 模式启动，需在 [user settings](https://code.claude.com/docs/en/settings#settings-files) 中设置 `defaultMode`。Claude Code 会忽略项目设置和本地设置中的 `defaultMode: "auto"`。

Bypass permissions 需先在扩展设置中启用 **Allow dangerously skip permissions** 开关。

详见 [VS Code 指南](https://code.claude.com/docs/en/vs-code)。

### JetBrains

JetBrains 插件在 IDE 终端中运行 Claude Code，切换方式与 CLI 一致：按 `Shift+Tab` 循环，或启动时传 `--permission-mode`。

### Desktop

使用发送按钮旁的模式选择器。Auto 和 Bypass permissions 需先在 Desktop 设置中启用。详见 [Desktop 指南](https://code.claude.com/docs/en/desktop#choose-a-permission-mode)。

### Web 和移动端

在 [claude.ai/code](https://claude.ai/code) 或移动端的输入框旁使用模式下拉菜单。权限提示会在 claude.ai 中弹出等待批准。可见的模式取决于会话运行位置：

- **云端会话**（[Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web)）：Accept edits、Plan mode、Auto mode。Accept edits 对应 `default` 模式——云端环境默认预批准文件编辑，因此下拉菜单显示 Accept edits 而非 Ask permissions。设置中的 `defaultMode: "acceptEdits"` 仍有效。Auto 模式仅在组织允许且所选模型支持时出现。Bypass permissions 不可用。
- **[Remote Control](https://code.claude.com/docs/en/remote-control) 会话**（本地机器）：Ask permissions、Auto accept edits、Plan mode。Auto 和 Bypass permissions 不可用。

Remote Control 还可以在启动 host 时指定初始模式：

```bash
claude remote-control --permission-mode acceptEdits
```

## acceptEdits 模式：自动批准文件编辑

**让 Claude 在工作目录内自由创建和编辑文件，无需逐一确认。** 状态栏显示 `⏵⏵ accept edits on`。

除文件编辑外，`acceptEdits` 还自动批准常用文件系统 Bash 命令：`mkdir`、`touch`、`rm`、`rmdir`、`mv`、`cp`、`sed`。加上安全环境变量前缀（如 `LANG=C`、`NO_COLOR=1`）或进程包装器（如 `timeout`、`nice`、`nohup`）也同样自动批准。自动批准仅适用于工作目录或 `additionalDirectories` 内的路径。超出范围的路径、对[受保护路径](#受保护路径)的写入以及其他所有 Bash 命令仍需手动确认。

启用 [PowerShell 工具](https://code.claude.com/docs/en/tools-reference#powershell-tool)时，`acceptEdits` 模式还自动批准作用域内路径的 `Set-Content`、`Add-Content`、`Clear-Content` 和 `Remove-Item` 及其别名，受保护路径规则同样适用。

适合在编辑器中或通过 `git diff` 事后审查变更，而非逐一内联批准。从 default 模式按一次 `Shift+Tab` 即可进入，或直接启动：

```bash
claude --permission-mode acceptEdits
```

## plan 模式：先分析再动手

**Claude 只做研究和方案设计，不修改你的源代码。** Claude 会读取文件、执行探索性 Shell 命令并撰写计划，但不会编辑你的代码。权限提示的行为与 default 模式一致。

按 `Shift+Tab` 进入，或在单条提示前加 `/plan`。也可直接启动：

```bash
claude --permission-mode plan
```

再按一次 `Shift+Tab` 可退出 plan 模式而不批准计划。

### 审查并批准计划

计划就绪后，Claude 会展示方案并询问后续步骤。你可以：

- 批准并以 auto 模式开始执行
- 批准并以 acceptEdits 模式执行
- 批准并逐一审查每次编辑
- 继续规划并给出反馈
- 用 [Ultraplan](https://code.claude.com/docs/en/ultraplan) 在浏览器中细化方案

批准计划会退出 plan 模式并切换到对应的权限模式，Claude 随即开始编辑。要再次规划，用 `Shift+Tab` 切回 plan 模式，或在下一条提示前加 `/plan`。

按 `Ctrl+G` 可在默认文本编辑器中打开并直接修改方案。启用 [`showClearContextOnPlanAccept`](https://code.claude.com/docs/en/settings#available-settings) 后，每个批准选项还会提供先清除规划上下文的选项。

接受计划时还会自动从计划内容中为会话命名（除非你已用 `--name` 或 `/rename` 设置了名称）。

### 将 plan 模式设为默认

在 `.claude/settings.json` 中设置：

```json
{
  "permissions": {
    "defaultMode": "plan"
  }
}
```

## auto 模式：消除审批提示

> 需要 Claude Code v2.1.83 或更高版本。

**Claude 全自动执行，一个独立的分类器模型在操作运行前进行安全审查。** 分类器会阻止超出你请求范围的操作、针对未识别基础设施的操作，或受恶意内容驱动的操作。显式 [ask 规则](https://code.claude.com/docs/en/permissions#manage-permissions)仍会强制弹出提示。

Auto 模式还会引导 Claude 持续工作而不停下来问澄清性问题（当你的提示或技能明确需要时，Claude 仍会提问）。如果想要更强的自主行为同时保留权限提示，改用 [Proactive output style](https://code.claude.com/docs/en/output-styles)。

> ⚠️ Auto 模式是研究预览功能。它减少了权限提示但不保证安全。在你信任整体方向的任务中使用，不要将其作为敏感操作审查的替代品。

### 开启条件

Auto 模式需同时满足以下所有条件：

| 条件 | 要求 |
| :--- | :--- |
| 计划 | 所有计划均可 |
| 管理员 | Team/Enterprise 中，Owner 需在 [Claude Code admin settings](https://claude.ai/admin-settings/claude-code) 中启用；也可通过 managed settings 中 `permissions.disableAutoMode` 设为 `"disable"` 来锁定关闭 |
| 模型 | Anthropic API：Claude Opus 4.6+，Sonnet 4.6；Bedrock/Vertex AI/Foundry：仅 Opus 4.7 和 Opus 4.8。不支持 Sonnet 4.5、Opus 4.5、Haiku 及 claude-3 系列 |
| 提供商 | Anthropic API 默认可用；Bedrock/Vertex AI/Foundry 需[设置 `CLAUDE_CODE_ENABLE_AUTO_MODE`](#在-bedrockvertex-aifoundry-上启用-auto-模式) |

如果 Claude Code 报告 auto 模式不可用，说明上述某项条件未满足（非临时故障）。若看到消息称某模型 "cannot determine the safety" of an action，则是分类器的临时故障，参见[错误参考](https://code.claude.com/docs/en/errors#auto-mode-cannot-determine-the-safety-of-an-action)。

如果你在 settings 中设了 `defaultMode: "auto"` 但会话以 `default` 模式启动且无报错，该设置可能位于 `.claude/settings.json` 或 `.claude/settings.local.json` 中。Claude Code v2.1.142 及以后会忽略这些文件中的 `auto` 设置（防止仓库给自己授予 auto 模式），请移至 `~/.claude/settings.json`。

### 在 Bedrock/Vertex AI/Foundry 上启用 auto 模式

在 [Amazon Bedrock](https://code.claude.com/docs/en/amazon-bedrock)、[Google Cloud Vertex AI](https://code.claude.com/docs/en/google-vertex-ai) 和 [Microsoft Foundry](https://code.claude.com/docs/en/microsoft-foundry) 上，auto 模式默认不出现在 `Shift+Tab` 循环中，需设置 `CLAUDE_CODE_ENABLE_AUTO_MODE` 为 `1`（v2.1.158+）。仅支持 Opus 4.7 和 Opus 4.8。

为单个开发者启用，在 `~/.claude/settings.json` 的 `env` 块中添加：

```json
{
  "env": {
    "CLAUDE_CODE_ENABLE_AUTO_MODE": "1"
  }
}
```

为组织启用，在 [managed settings](https://code.claude.com/docs/en/settings#settings-files) 中添加相同的 `env` 块。

设置后 auto 模式出现在每次会话的 `Shift+Tab` 循环中。要设为默认启动模式，还需在 user 或 managed settings 中设置 `"permissions": {"defaultMode": "auto"}`。在这些提供商上，没有 `CLAUDE_CODE_ENABLE_AUTO_MODE` 时 Claude Code 会忽略 `defaultMode: "auto"`。

要阻止开发者启用 auto 模式，在 managed settings 中将 `disableAutoMode` 设为 `"disable"`。

如果通过配置了 `ANTHROPIC_BASE_URL` 的 [LLM gateway](https://code.claude.com/docs/en/llm-gateway) 连接，auto 模式可能无需上述环境变量即可访问（因为网关将请求路由到了 Anthropic API）。`disableAutoMode` 设置同样适用。

### 分类器默认阻止的操作

**分类器信任你的工作目录和仓库已配置的远程地址。其他一切被视为外部，直到你[配置受信基础设施](https://code.claude.com/docs/en/auto-mode-config)。**

**默认阻止**：

- 下载并执行代码（如 `curl | bash`）
- 向外部端点发送敏感数据
- 生产部署和迁移
- 云存储的批量删除
- 授予 IAM 或仓库权限
- 修改共享基础设施
- 不可逆删除会话前已存在的文件
- Force push，或直接 push 到 `main`
- `git reset --hard`、`git checkout -- .`、`git restore .`、`git clean -fd`、`git stash drop`、`git stash clear`（分类器假设这些会丢弃未提交的更改）
- `git commit --amend`（当 HEAD 提交不是本次会话创建时）
- `terraform destroy`、`pulumi destroy`、`cdk destroy`、`terragrunt destroy`，以及包含资源销毁的 plan apply

**默认允许**：

- 工作目录内的本地文件操作
- 安装 lock 文件或 manifest 中声明的依赖
- 读取 `.env` 并向对应 API 发送凭据
- 只读 HTTP 请求
- Push 到你启动时所在的分支或 Claude 创建的分支

沙箱网络访问请求通过分类器路由，而非默认允许。运行 `claude auto-mode defaults` 可查看完整规则列表。如果常规操作被阻止，管理员可通过 `autoMode.environment` 设置添加受信仓库、存储桶和服务，详见[配置 auto 模式](https://code.claude.com/docs/en/auto-mode-config)。

### 对话中声明的边界

**分类器将你在对话中声明的边界视为阻止信号。** 如果你告诉 Claude "don't push" 或 "wait until I review before deploying"，即使默认规则允许，分类器也会阻止匹配操作。边界在你后续消息中解除前一直有效。Claude 自行判断条件已满足并不能解除边界。

边界不作为规则存储。分类器每次检查时从会话记录中重新读取，因此如果[上下文压缩](https://code.claude.com/docs/en/costs#reduce-token-usage)移除了声明边界的消息，该边界可能丢失。要硬性保证，请添加 [deny 规则](https://code.claude.com/docs/en/permissions#permission-rule-syntax)。

### auto 模式的回退机制

每个被拒绝的操作会显示通知，并出现在 `/permissions` 的 Recently denied 标签页中，按 `r` 可手动批准重试。

如果分类器连续阻止 3 次或累计阻止 20 次，auto 模式暂停，Claude Code 恢复逐一提示。批准被提示的操作后恢复 auto 模式。这些阈值不可配置。任何被允许的操作会重置连续计数器；累计计数器在整个会话中持续，仅在其自身限制触发回退时重置。

在 `-p` [非交互模式](https://code.claude.com/docs/en/headless)下，反复阻止会终止会话（因为没有用户可以提示）。

反复阻止通常意味着分类器缺少关于你基础设施的上下文。用 `/feedback` 报告误报，或让管理员[配置受信基础设施](https://code.claude.com/docs/en/auto-mode-config)。

### 分类器如何评估操作

每个操作按固定顺序判定，第一个匹配的步骤生效：

1. 匹配你的 [allow 或 deny 规则](https://code.claude.com/docs/en/permissions#manage-permissions)的操作立即解决——但对[受保护路径](#受保护路径)的写入即使匹配 allow 规则也会路由到分类器
2. 工作目录内的只读操作和文件编辑被自动批准——但对[受保护路径](#受保护路径)的写入除外
3. 其他所有操作发送给分类器
4. 如果分类器阻止，Claude 收到原因并尝试替代方案

进入 auto 模式时，授予任意代码执行的宽泛 allow 规则会被丢弃：

- 通配 `Bash(*)` 或 `PowerShell(*)`
- 通配解释器如 `Bash(python*)`
- 包管理器 run 命令
- `Agent` allow 规则

窄规则如 `Bash(npm test)` 保留。离开 auto 模式时被丢弃的规则恢复。

分类器看到用户消息、工具调用和 CLAUDE.md 内容。工具结果被剥离，因此文件或网页中的恶意内容无法直接操纵分类器。另一个服务端探针在 Claude 读取前扫描传入的工具结果并标记可疑内容。更多关于这些层如何协同工作的信息，参见 [auto mode 公告](https://claude.com/blog/auto-mode)和[工程深度解析](https://www.anthropic.com/engineering/claude-code-auto-mode)。

### auto 模式如何处理子代理

分类器在三个节点检查[子代理](https://code.claude.com/docs/en/sub-agents)的工作：

1. **子代理启动前**：评估委派的任务描述，危险任务在产生时即被阻止
2. **子代理运行中**：其每个操作都通过分类器，规则与父会话相同；子代理 frontmatter 中的 `permissionMode` 被忽略
3. **子代理完成时**：分类器审查其完整操作历史；如果返回检查标记问题，安全警告会被添加到子代理结果的前面

步骤 1 需要 Claude Code v2.1.178+。更早版本仅在步骤 2 和 3 应用分类器。

### 成本与延迟

分类器运行在服务端配置的模型上，独立于你的 `/model` 选择，因此切换模型不影响分类器可用性。分类器调用计入你的 token 用量。每次检查发送一部分会话记录加待执行操作，在执行前增加一次往返。受保护路径外的读取和工作目录编辑跳过分类器，因此开销主要来自 Shell 命令和网络操作。

## dontAsk 模式：仅允许预批准工具

**自动拒绝所有需要提示的工具调用，只有匹配 allow 规则和[只读 Bash 命令](https://code.claude.com/docs/en/permissions#read-only-commands)的操作能执行。** 显式 [`ask` 规则](https://code.claude.com/docs/en/permissions#manage-permissions)同样被拒绝而非弹出提示。这使该模式完全无交互，适合 CI 管道或预先严格定义 Claude 权限的受限环境。[Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web) 的云端会话忽略 `defaultMode: "dontAsk"`。

启动时设置：

```bash
claude --permission-mode dontAsk
```

## bypassPermissions 模式：跳过所有检查

**禁用所有权限提示和安全检查，工具调用立即执行。** 从 v2.1.126 起包括对[受保护路径](#受保护路径)的写入（更早版本仍会提示）。显式 [ask 规则](https://code.claude.com/docs/en/permissions#manage-permissions)在此模式下仍强制提示；针对文件系统根目录或 home 目录的删除操作（如 `rm -rf /` 和 `rm -rf ~`）仍会提示，作为防止模型错误的断路器。**仅在容器、虚拟机或无互联网的 dev container 等隔离环境中使用。**

你无法从未使用启用标志启动的会话中进入 `bypassPermissions`，需用以下标志重新启动：

```bash
claude --permission-mode bypassPermissions
```

`--dangerously-skip-permissions` 标志等效。

在 Linux 和 macOS 上，以 root 或 `sudo` 运行时 Claude Code 拒绝以此模式启动：

```text
--dangerously-skip-permissions cannot be used with root/sudo privileges for security reasons
```

在可识别的沙箱内此检查会自动跳过。要在容器中自主运行，使用 [dev container](https://code.claude.com/docs/en/devcontainer) 配置（以非 root 用户运行 Claude Code）。

[Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web) 不尊重设置文件中的 `defaultMode: "bypassPermissions"` 或 `"dontAsk"`，因此仓库签入的设置无法让云端会话以 bypass-permissions 模式启动。该设置被静默忽略，会话以模式下拉菜单显示的模式启动。

> ⚠️ `bypassPermissions` 对提示注入或意外操作不提供任何保护。需要后台安全检查且少权限提示时，请用 [auto 模式](#auto-模式消除审批提示)。管理员可通过 managed settings 中将 `permissions.disableBypassPermissionsMode` 设为 `"disable"` 来阻止此模式。

## 受保护路径

**在除 `bypassPermissions` 外的所有模式中，对一小组特定路径的写入永远不会被自动批准，以防止仓库状态和 Claude 自身配置被意外破坏。**

| 模式 | 受保护路径写入的处理 |
| :--- | :--- |
| `default`、`acceptEdits`、`plan` | 弹出提示 |
| `auto` | 路由到分类器 |
| `dontAsk` | 拒绝 |
| `bypassPermissions` | 允许 |

设置文件中的 [`permissions.allow`](https://code.claude.com/docs/en/permissions#manage-permissions) 规则不能预批准受保护路径的写入。安全检查在 Claude Code 评估 settings 文件中的 allow 规则之前运行，因此 `~/.claude/settings.json` 或 `.claude/settings.json` 中的 `Edit(.claude/**)` 条目不改变上表中各模式的行为。在需要提示的模式中，`.claude/` 写入的提示会提供 **Yes, and allow Claude to edit its own settings for this session** 选项，批准后该会话内后续 `.claude/` 写入不再提示。

### 受保护目录

- `.git`
- `.config/git`
- `.vscode`
- `.idea`
- `.husky`
- `.cargo`
- `.devcontainer`
- `.yarn`
- `.mvn`
- `.claude`（`.claude/worktrees` 除外，Claude 在此存放自己的 git worktrees）

### 受保护文件

- `.gitconfig`、`.gitmodules`
- `.bashrc`、`.bash_profile`、`.bash_login`、`.bash_aliases`、`.bash_logout`、`.zshrc`、`.zprofile`、`.zshenv`、`.zlogin`、`.zlogout`、`.profile`、`.envrc`
- `.npmrc`、`.yarnrc`、`.yarnrc.yml`、`.pnp.cjs`、`.pnp.loader.mjs`、`.pnpmfile.cjs`、`bunfig.toml`、`.bunfig.toml`
- `.bazelrc`、`.bazelversion`、`.bazeliskrc`
- `.pre-commit-config.yaml`、`lefthook.yml`、`lefthook.yaml`、`.lefthook.yml`、`.lefthook.yaml`
- `gradle-wrapper.properties`、`maven-wrapper.properties`
- `.devcontainer.json`
- `.ripgreprc`、`pyrightconfig.json`
- `.mcp.json`、`.claude.json`

## 延伸阅读

- [权限](https://code.claude.com/docs/en/permissions)：allow、ask、deny 规则；managed 策略
- [配置 auto 模式](https://code.claude.com/docs/en/auto-mode-config)：告诉分类器你的组织信任哪些基础设施
- [Hooks](https://code.claude.com/docs/en/hooks)：通过 `PreToolUse` 和 `PermissionRequest` hooks 实现自定义权限逻辑
- [Ultraplan](https://code.claude.com/docs/en/ultraplan)：在 Claude Code on the web 会话中运行 plan 模式并在浏览器中审查
- [安全](https://code.claude.com/docs/en/security)：安全防护和最佳实践
- [沙箱](https://code.claude.com/docs/en/sandboxing)：Bash 命令的文件系统和网络隔离
- [非交互模式](https://code.claude.com/docs/en/headless)：用 `-p` 标志运行 Claude Code
