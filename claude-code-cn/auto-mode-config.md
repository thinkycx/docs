---
title: 【译】Auto Mode 配置
tags:
  - claude-code
  - auto-mode
  - translation
create: 2026-06-28
update: 2026-06-28
author: thinkycx
category: translation
description: 介绍如何配置 Claude Code 的 auto mode 分类器，包括定义可信基础设施、覆盖默认的阻止和允许规则、检查生效配置以及审查拒绝记录。
refs: https://code.claude.com/docs/en/auto-mode-config.md
---

# 配置 Auto Mode

> 告诉 auto mode 分类器哪些仓库、存储桶和域名是你的组织所信任的。设置环境上下文，覆盖默认的阻止和允许规则，并使用 auto-mode CLI 子命令检查生效配置。

**[Auto mode](https://code.claude.com/docs/en/permission-modes#eliminate-prompts-with-auto-mode) 让 Claude Code 无需常规权限提示即可运行。** 它将工具调用路由到一个分类器，该分类器阻止任何不可逆、破坏性或指向你环境之外的操作。Deny 和显式 ask 规则在分类器之前评估，仍然会阻止或提示。使用 `autoMode` 设置块告诉分类器哪些仓库、存储桶和域名是你组织信任的，这样它就不会阻止常规的内部操作。

> [!NOTE]
> Auto mode 对 Anthropic API 上的所有用户可用。在 Amazon Bedrock、Google Cloud Vertex AI 和 Microsoft Foundry 上，你必须先 [设置 `CLAUDE_CODE_ENABLE_AUTO_MODE`](https://code.claude.com/docs/en/permission-modes#enable-auto-mode-on-bedrock-vertex-ai-or-foundry)。如果 Claude Code 报告 auto mode 对你的账户不可用，检查 [完整要求](https://code.claude.com/docs/en/permission-modes#eliminate-prompts-with-auto-mode)。

**默认情况下，分类器仅信任工作目录和当前仓库配置的远程。** push 到公司源码控制组织或写入团队云存储桶等操作会被阻止，直到你将它们添加到 `autoMode.environment`。

要了解如何启用 auto mode 及其默认阻止内容，参见 [Permission modes](https://code.claude.com/docs/en/permission-modes#eliminate-prompts-with-auto-mode)。本页是配置参考。

本页涵盖：

- [选择在哪里设置规则](#分类器读取配置的位置)
- [定义可信基础设施](#定义可信基础设施)
- [覆盖阻止和允许规则](#覆盖阻止和允许规则)
- [检查生效配置](#检查默认值和生效配置)
- [审查拒绝记录](#审查拒绝记录)

## 分类器读取配置的位置

**分类器读取 Claude 本身加载的相同 [CLAUDE.md](https://code.claude.com/docs/en/memory) 内容。** 因此项目 CLAUDE.md 中的指令（如 "never force push"）同时影响 Claude 和分类器。项目约定和行为规则从这里开始。

对于跨项目适用的规则（如可信基础设施或组织级 deny 规则），使用 `autoMode` 设置块。分类器从以下范围读取 `autoMode`：

| 范围 | 文件 | 用途 |
| :--- | :--- | :--- |
| 单个开发者 | `~/.claude/settings.json` | 个人可信基础设施 |
| 单个项目，单个开发者 | `.claude/settings.local.json` | 项目级可信存储桶或服务 |
| 组织范围 | [Managed settings](https://code.claude.com/docs/en/server-managed-settings) | 分发给所有开发者的可信基础设施 |
| `--settings` 标志或 Agent SDK | 内联 JSON | 自动化场景的按次覆盖 |

**分类器不从 `.claude/settings.json` 的共享项目设置中读取 `autoMode`**，因此已提交的仓库不能注入自己的 allow 规则。

各范围的条目会组合。开发者可以用个人条目扩展 `environment`、`allow`、`soft_deny` 和 `hard_deny`，但不能移除 managed settings 提供的条目。因为 allow 规则在分类器内部充当 soft block 规则的例外，开发者添加的 `allow` 条目可以覆盖组织的 `soft_deny` 条目——组合是累加的，不是硬策略边界。

> [!NOTE]
> 分类器是在 [权限系统](https://code.claude.com/docs/en/permissions) 之后运行的第二道门。对于无论用户意图或分类器配置如何都绝不应运行的操作，在 managed settings 中使用 `permissions.deny`——它在分类器被咨询之前就阻止操作，且不可被覆盖。

## 定义可信基础设施

**对大多数组织来说，`autoMode.environment` 是你唯一需要设置的字段。** 它告诉分类器哪些仓库、存储桶和域名是可信的：分类器用它来判断什么是"外部"的，因此未列出的目标都是潜在的数据外泄目标。

默认 environment 列表信任工作仓库及其配置的远程。要在该默认值之上添加自己的条目，在数组中包含字面字符串 `"$defaults"`。默认条目会在该位置拼接进来。

```json
{
  "autoMode": {
    "environment": [
      "$defaults",
      "Source control: github.example.com/acme-corp and all repos under it",
      "Trusted cloud buckets: s3://acme-build-artifacts, gs://acme-ml-datasets",
      "Trusted internal domains: *.corp.example.com, api.internal.example.com",
      "Key internal services: Jenkins at ci.example.com, Artifactory at artifacts.example.com"
    ]
  }
}
```

**条目是自然语言描述，不是正则或工具模式。** 分类器将它们作为自然语言规则阅读。按照你向新工程师描述基础设施的方式编写。完整的 environment 部分涵盖：

- **组织**：公司名称和 Claude Code 的主要用途
- **源码控制**：开发者 push 到的每个 GitHub、GitLab 或 Bitbucket 组织
- **云提供商和可信存储桶**：Claude 应该能读写的存储桶名称或前缀
- **可信内部域名**：网络内 API、仪表板和服务的主机名
- **关键内部服务**：CI、制品仓库、内部包索引、事件工具
- **额外上下文**：受监管行业约束、多租户基础设施或合规要求

**实用起始模板**（填入括号内字段，删除不适用的行）：

```json
{
  "autoMode": {
    "environment": [
      "$defaults",
      "Organization: {COMPANY_NAME}. Primary use: {PRIMARY_USE_CASE, e.g. software development, infrastructure automation}",
      "Source control: {SOURCE_CONTROL, e.g. GitHub org github.example.com/acme-corp}",
      "Cloud provider(s): {CLOUD_PROVIDERS, e.g. AWS, GCP, Azure}",
      "Trusted cloud buckets: {TRUSTED_BUCKETS, e.g. s3://acme-builds, gs://acme-datasets}",
      "Trusted internal domains: {TRUSTED_DOMAINS, e.g. *.internal.example.com, api.example.com}",
      "Key internal services: {SERVICES, e.g. Jenkins at ci.example.com, Artifactory at artifacts.example.com}",
      "Additional context: {EXTRA, e.g. regulated industry, multi-tenant infrastructure, compliance requirements}"
    ]
  }
}
```

**提供的上下文越具体，分类器就越能区分常规内部操作和数据外泄尝试。**

不需要一次性填完所有内容。合理的推进方式：从默认值开始，添加源码控制组织和关键内部服务（这解决最常见的误报，如 push 到自己的仓库）。然后添加可信域名和云存储桶。其余的在阻止出现时再补充。

## 覆盖阻止和允许规则

**三个额外字段让你替换分类器的内置规则列表：**

| 字段 | 用途 |
| :--- | :--- |
| `autoMode.hard_deny` | 无条件安全边界 |
| `autoMode.soft_deny` | 用户意图可以清除的破坏性操作 |
| `autoMode.allow` | soft block 规则的例外 |

每个都是自然语言描述的数组。对于在分类器之前运行的工具模式硬阻止，使用 [`permissions.deny`](https://code.claude.com/docs/en/permissions)。

**在分类器内部，优先级按四个层级工作：**

1. `hard_deny` 规则无条件阻止。用户意图和 `allow` 例外不适用。
2. `soft_deny` 规则其次阻止。用户意图和 `allow` 例外可以覆盖。
3. `allow` 规则然后作为匹配 `soft_deny` 规则的例外覆盖。
4. 显式用户意图覆盖剩余的 soft block：如果用户的消息直接且具体地描述了 Claude 即将执行的确切操作，分类器即使 `soft_deny` 规则匹配也会允许。

一般请求不算显式意图。让 Claude "clean up the repo" 不授权 force-push，但让 Claude "force-push this branch" 可以。

**使用建议：**
- 要放宽：当分类器反复标记默认例外未覆盖的常规模式时，添加到 `allow`
- 要收紧：对默认遗漏的环境特定破坏性风险添加到 `soft_deny`，对绝不应越过的安全边界添加到 `hard_deny`

要在添加自己规则的同时保留内置规则，在数组中包含字面字符串 `"$defaults"`。

以下示例保留所有四个列表的默认值，并向每个添加组织特定规则：

```json
{
  "autoMode": {
    "environment": [
      "$defaults",
      "Source control: github.example.com/acme-corp and all repos under it"
    ],
    "allow": [
      "$defaults",
      "Deploying to the staging namespace is allowed: staging is isolated from production and resets nightly",
      "Writing to s3://acme-scratch/ is allowed: ephemeral bucket with a 7-day lifecycle policy"
    ],
    "soft_deny": [
      "$defaults",
      "Never run database migrations outside the migrations CLI, even against dev databases",
      "Never modify files under infra/terraform/prod/: production infrastructure changes go through the review workflow"
    ],
    "hard_deny": [
      "$defaults",
      "Never send repository contents to third-party code-review APIs"
    ]
  }
}
```

> [!CAUTION]
> 在设置 `environment`、`allow`、`soft_deny` 或 `hard_deny` 时如果不包含 `"$defaults"`，会替换该部分的整个默认列表。没有 `"$defaults"` 的 `soft_deny` 数组会丢弃所有内置 soft block 规则（包括 force push、`curl | bash` 和生产部署）。没有 `"$defaults"` 的 `hard_deny` 数组会丢弃内置的数据外泄和 auto-mode 绕过规则。

**各部分独立评估**，因此单独设置 `environment` 不会影响默认的 `allow`、`soft_deny` 和 `hard_deny` 列表。

仅在你打算完全掌控列表时才省略 `"$defaults"`。要安全地这样做，运行 `claude auto-mode defaults` 打印内置规则，将它们复制到你的设置文件，然后根据你的流水线和风险容忍度审查每条规则。

## 检查默认值和生效配置

**三个 CLI 子命令帮助你检查和验证配置：**

| 命令 | 用途 |
| :--- | :--- |
| `claude auto-mode defaults` | 打印内置的 `environment`、`allow`、`soft_deny` 和 `hard_deny` 规则（JSON 格式） |
| `claude auto-mode config` | 打印分类器实际使用的规则（JSON 格式），你的设置应用在设置的位置，其他位置用默认值 |
| `claude auto-mode critique` | 获取 AI 对你自定义的 `allow`、`soft_deny` 和 `hard_deny` 规则的反馈 |

保存设置后运行 `claude auto-mode config` 确认生效规则符合预期（`"$defaults"` 已展开）。如果你写了自定义规则，`claude auto-mode critique` 会审查它们并标记模糊、冗余或可能导致误报的条目。

如果你需要移除或重写内置规则而非在其旁边添加，将 `claude auto-mode defaults` 的输出保存到文件，编辑列表，然后将结果粘贴到你的设置文件中替代 `"$defaults"`。

## 审查拒绝记录

**当 auto mode 拒绝一个工具调用时，拒绝会记录在 `/permissions` 的 Recently denied 标签页中。** 对被拒绝的操作按 `r` 标记为重试：退出对话框时，Claude Code 发送消息告诉模型可以重试该工具调用并恢复对话。

反复出现的同一目标拒绝通常意味着分类器缺少上下文。将该目标添加到 `autoMode.environment`，然后运行 `claude auto-mode config` 确认生效。

要以编程方式响应拒绝，使用 [`PermissionDenied` hook](https://code.claude.com/docs/en/hooks#permissiondenied)。

## 另请参阅

- [Permission modes](https://code.claude.com/docs/en/permission-modes#eliminate-prompts-with-auto-mode)：auto mode 是什么、默认阻止什么、如何启用
- [Managed settings](https://code.claude.com/docs/en/server-managed-settings)：在组织中部署 `autoMode` 配置
- [Permissions](https://code.claude.com/docs/en/permissions)：在分类器运行之前适用的 allow、ask 和 deny 规则
- [Settings](https://code.claude.com/docs/en/settings)：完整设置参考，包括 `autoMode` 键
