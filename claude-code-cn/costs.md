---
title: 【译】成本管理
tags:
  - claude-code
  - costs
  - translation
create: 2026-06-28
update: 2026-06-28
author: thinkycx
category: translation
description: 介绍如何追踪 Claude Code 的 token 使用、为团队设置花费限制，以及通过上下文管理、模型选择、思考配置和预处理 hook 等手段降低成本。
refs: https://code.claude.com/docs/en/costs.md
---

# 有效管理成本

> 追踪 token 使用，设置团队花费限制，通过上下文管理、模型选择、扩展思考设置和预处理 hook 降低 Claude Code 成本。

**Claude Code 按 API token 消耗计费。** 订阅计划定价（Pro、Max、Team、Enterprise）参见 [claude.com/pricing](https://claude.com/pricing)。每位开发者的成本因模型选择、代码库规模和使用模式（如运行多实例或自动化）而差异很大。

在企业部署中，平均成本约为每位开发者每活跃天 $13，每月 $150-250，90% 的用户每活跃天花费不超过 $30。要估算你团队的花费，先用一个小型试点组，利用下方追踪工具建立基线，再进行更大范围推广。

本页涵盖如何[追踪成本](#追踪成本)、[管理团队成本](#管理团队成本)和[降低-token-使用量](#降低-token-使用量)。

## 追踪成本

### 使用 `/usage` 命令

> **注意：** `/usage` 中的 Session 区块显示 API token 用量，面向 API 用户。Claude Max 和 Pro 订阅者的用量包含在订阅中，会话成本数字与计费无关。订阅者会看到计划用量条、活动统计和用量明细。

`/usage` 顶部的 Session 区块显示当前会话的详细 token 使用统计。金额是根据 token 数量本地计算的估算值，可能与实际账单不同。权威计费请查看 [Claude Console](https://platform.claude.com/usage) 的 Usage 页面。

```text
Total cost:            $0.55
Total duration (API):  6m 19.7s
Total duration (wall): 6h 33m 10.2s
Total code changes:    0 lines added, 0 lines removed
```

在 Pro、Max、Team 或 Enterprise 计划中，`/usage` 还显示计入计划限额的用量明细。它将近期使用归因到 skill、subagent、插件和各 MCP 服务器，每项显示为总量的百分比。按 `d` 或 `w` 切换最近 24 小时和最近 7 天。数据是从本机本地会话历史近似计算的，不包含其他设备或 claude.ai 的使用。

在 [VS Code 扩展](https://code.claude.com/docs/en/vs-code#check-account-and-usage)中，相同明细在 Account & usage 对话框中显示，带 Day 和 Week 切换。需要 Claude Code v2.1.174 或更高版本。

## 管理团队成本

**使用 Claude API 时，你可以在 Console 中[设置工作区花费限制](https://platform.claude.com/docs/en/build-with-claude/workspaces#workspace-limits)来限定 Claude Code 工作区的总花费。** 管理员可以在 Console 中[查看成本和使用报告](https://platform.claude.com/docs/en/build-with-claude/workspaces#usage-and-cost-tracking)。

在 Pro 和 Max 计划中，你可以使用 `/usage-credits` 命令设置使用积分的月度花费限制。如果在还有可用积分时触达限制，Claude Code 会提示你提高或移除限制，无需离开 CLI。修改限制需要账户的账单访问权限。

> **注意：** 当你首次用 Claude Console 账户认证 Claude Code 时，系统会自动为你创建一个名为 "Claude Code" 的工作区。此工作区提供组织中所有 Claude Code 使用的集中成本追踪和管理。你不能为此工作区创建 API 密钥；它专用于 Claude Code 认证和使用。
>
> 对于有自定义速率限制的组织，此工作区中的 Claude Code 流量计入组织的整体 API 速率限制。你可以在 Claude Console 的此工作区 Limits 页面设置[工作区速率限制](https://platform.claude.com/docs/en/api/rate-limits#setting-lower-limits-for-workspaces)，以限定 Claude Code 的份额并保护其他生产工作负载。

在 Bedrock、Vertex 和 Foundry 上，Claude Code 不从你的云发送指标。已通过 [LLM 网关](https://code.claude.com/docs/en/llm-gateway)路由 Claude Code 的组织可以在网关处追踪花费，因为网关能看到每个请求。

### 速率限制建议

为团队设置 Claude Code 时，根据组织规模参考以下每用户 Token Per Minute (TPM) 和 Request Per Minute (RPM) 建议：

| 团队规模      | 每用户 TPM    | 每用户 RPM    |
| ------------- | ------------- | ------------- |
| 1-5 人        | 200k-300k     | 5-7           |
| 5-20 人       | 100k-150k     | 2.5-3.5       |
| 20-50 人      | 50k-75k       | 1.25-1.75     |
| 50-100 人     | 25k-35k       | 0.62-0.87     |
| 100-500 人    | 15k-20k       | 0.37-0.47     |
| 500+ 人       | 10k-15k       | 0.25-0.35     |

例如，200 人团队可以为每位用户申请 20k TPM，即总共 400 万 TPM（200 * 20,000 = 400 万）。

每用户 TPM 随团队规模增大而降低，因为大型组织中较少用户会同时使用 Claude Code。这些速率限制在组织级别应用而非针对单个用户，意味着其他人不活跃时个别用户可以临时消耗超出其计算份额的量。

> **注意：** 如果预期异常高的并发使用场景（如大规模实操培训），可能需要更高的每用户 TPM 分配。

### Agent Team token 成本

[Agent teams](https://code.claude.com/docs/en/agent-teams) 会生成多个 Claude Code 实例，每个都有自己的上下文窗口。Token 使用量随活跃队友数量和每个运行时长而增长。

控制 agent team 成本的方法：

* **队友使用 Sonnet。** 它在协调任务中平衡了能力和成本。
* **保持团队小规模。** 每个队友运行自己的上下文窗口，token 使用量大致与团队规模成正比。
* **保持生成提示简短。** 队友自动加载 CLAUDE.md、MCP 服务器和 skill，但生成提示中的所有内容从一开始就添加到其上下文。
* **工作完成后关闭队友。** 每个活跃队友持续消耗 token 直到退出或会话结束。
* Agent teams 默认禁用。在 [settings.json](https://code.claude.com/docs/en/settings) 或环境中设置 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 启用。参见[启用 agent teams](https://code.claude.com/docs/en/agent-teams#enable-agent-teams)。

## 降低 token 使用量

**Token 成本随上下文大小增长：Claude 处理的上下文越多，使用的 token 越多。** Claude Code 通过[提示缓存](https://code.claude.com/docs/en/prompt-caching)（降低重复内容如系统提示的成本）和自动压缩（在接近上下文限制时总结对话历史）自动优化成本。

以下策略帮助你保持上下文精简并降低每条消息的成本。

### 主动管理上下文

使用 `/usage` 检查当前 token 使用量，或[配置状态栏](https://code.claude.com/docs/en/statusline#context-window-usage)持续显示。

* **任务间清空**：切换到无关工作时使用 `/clear` 重新开始。陈旧上下文在后续每条消息中浪费 token。清空前使用 `/rename` 以便后续轻松找到会话，然后用 `/resume` 返回。
* **添加自定义压缩指令**：`/compact Focus on code samples and API usage` 告诉 Claude 在总结时保留什么。

也可以在 CLAUDE.md 中自定义压缩行为：

```markdown
# Compact instructions

When you are using compact, please focus on test output and code changes
```

### 选择合适的模型

**Sonnet 能胜任大多数编码任务且成本低于 Opus。** 将 Opus 留给复杂的架构决策或多步推理。使用 `/model` 在会话中切换模型，或在 `/config` 中设置默认值。对于简单的 subagent 任务，在 [subagent 配置](https://code.claude.com/docs/en/sub-agents#choose-a-model)中指定 `model: haiku`。

### 减少 MCP 服务器开销

MCP 工具定义[默认延迟加载](https://code.claude.com/docs/en/mcp#scale-with-mcp-tool-search)，只有工具名称进入上下文直到 Claude 使用特定工具。运行 `/context` 查看什么在占用空间。

* **优先使用 CLI 工具**：`gh`、`aws`、`gcloud`、`sentry-cli` 等工具比 MCP 服务器更节省上下文，因为它们不添加任何工具列表。Claude 可以直接运行 CLI 命令。
* **禁用未使用的服务器**：运行 `/mcp` 查看已配置的服务器并禁用未在使用的。

### 为类型语言安装代码智能插件

[代码智能插件](https://code.claude.com/docs/en/discover-plugins#code-intelligence)为 Claude 提供精确的符号导航而非基于文本的搜索，减少探索陌生代码时的不必要文件读取。单次 "go to definition" 调用可以替代原本需要 grep 然后阅读多个候选文件的过程。安装的语言服务器还能在编辑后自动报告类型错误，Claude 无需运行编译器即可发现问题。

### 将处理卸载到 hook 和 skill

**自定义 [hooks](https://code.claude.com/docs/en/hooks) 可以在 Claude 看到数据之前进行预处理。** 例如，与其让 Claude 阅读一个 10,000 行的日志文件来查找错误，hook 可以 grep `ERROR` 并只返回匹配行，将上下文从数万 token 减少到数百。

[skill](https://code.claude.com/docs/en/skills) 可以给 Claude 领域知识，使其无需探索。例如，一个 "codebase-overview" skill 可以描述项目架构、关键目录和命名约定。Claude 调用该 skill 时立即获得此上下文，而不是花费 token 阅读多个文件来理解结构。

例如，以下 PreToolUse hook 过滤测试输出只显示失败：

**settings.json 配置：**

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/filter-test-output.sh"
          }
        ]
      }
    ]
  }
}
```

**filter-test-output.sh 脚本：**

```bash
#!/bin/bash
input=$(cat)
cmd=$(echo "$input" | jq -r '.tool_input.command')

# If running tests, filter to show only failures
if [[ "$cmd" =~ ^(npm test|pytest|go test) ]]; then
  filtered_cmd="$cmd 2>&1 | grep -A 5 -E '(FAIL|ERROR|error:)' | head -100"
  echo "{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"permissionDecision\":\"allow\",\"updatedInput\":{\"command\":\"$filtered_cmd\"}}}"
else
  echo "{}"
fi
```

### 将指令从 CLAUDE.md 移到 skill

**你的 [CLAUDE.md](https://code.claude.com/docs/en/memory) 文件在会话启动时加载到上下文中。** 如果它包含特定工作流的详细指令（如 PR 审查或数据库迁移），即使在做无关工作时这些 token 也会存在。[Skills](https://code.claude.com/docs/en/skills) 按需加载，只在被调用时才加载，因此将专业指令移入 skill 可以保持基础上下文更小。目标是将 CLAUDE.md 保持在 200 行以内，只包含核心要素。

### 调整扩展思考

**扩展思考默认启用，因为它显著提升复杂规划和推理任务的表现。** 思考 token 按输出 token 计费，默认预算根据模型可达数万 token 每请求。对于不需要深度推理的简单任务，可以通过以下方式降低成本：

* 使用 `/effort` 或在 `/model` 中降低[努力级别](https://code.claude.com/docs/en/model-config#adjust-effort-level)
* 在 `/config` 中禁用思考
* 对于有[固定思考预算](https://code.claude.com/docs/en/model-config#adaptive-reasoning-and-fixed-thinking-budgets)的模型，用 `MAX_THINKING_TOKENS=8000` 降低预算

自适应推理模型忽略非零预算，应使用努力级别。在 Fable 5 上不可禁用思考（始终使用扩展思考）。

### 将冗长操作委托给 subagent

运行测试、获取文档或处理日志文件可能消耗大量上下文。将这些委托给 [subagent](https://code.claude.com/docs/en/sub-agents#isolate-high-volume-operations)，冗长输出留在 subagent 的上下文中，只有摘要返回到你的主对话。

### 管理 Agent Team 成本

当队友在 plan 模式运行时，Agent teams 的 token 使用量约为标准会话的 7 倍，因为每个队友维护自己的上下文窗口并作为独立 Claude 实例运行。保持团队任务小而自包含以限制每个队友的 token 使用。参见 [agent teams](https://code.claude.com/docs/en/agent-teams)。

### 写具体的提示

**含糊的请求如 "improve this codebase" 会触发广泛扫描。** 具体的请求如 "add input validation to the login function in auth.ts" 让 Claude 以最少的文件读取高效工作。

### 高效处理复杂任务

对于较长或更复杂的工作，以下习惯有助于避免因走错方向而浪费 token：

* **复杂任务使用 plan 模式**：按 Shift+Tab 进入 [plan 模式](https://code.claude.com/docs/en/permission-modes#analyze-before-you-edit-with-plan-mode)。Claude 探索代码库并提出方案供你批准，防止初始方向错误导致代价高昂的返工。
* **尽早纠偏**：如果 Claude 开始走偏，按 Escape 立即停止。使用 `/rewind` 或双击 Escape 将对话和代码恢复到之前的检查点。
* **提供验证目标**：在提示中包含测试用例、粘贴截图或定义预期输出。当 Claude 能自我验证时，它在你需要请求修复之前就能发现问题。
* **增量测试**：写一个文件、测试、然后继续。这能在问题修复成本低时就尽早发现。

## 后台 token 使用

Claude Code 即使空闲时也会为部分后台功能使用 token：

* **对话总结**：为 `claude --resume` 功能总结之前对话的后台任务
* **命令处理**：部分命令如 `/usage` 可能生成请求以检查状态

这些后台进程即使没有主动交互也会消耗少量 token（通常每会话低于 $0.04）。

## 理解 Claude Code 行为变化

Claude Code 定期收到可能改变功能工作方式的更新，包括成本报告。运行 `claude --version` 检查当前版本。具体计费问题请通过 [Console 账户](https://platform.claude.com/login)联系 Anthropic 支持。
