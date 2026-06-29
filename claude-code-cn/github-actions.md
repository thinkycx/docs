---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】GitHub Actions
description: Claude Code GitHub Actions 将 AI 驱动的自动化能力引入 GitHub 工作流。通过在 PR 或 Issue 评论中 @claude，Claude 即可分析代码、创建 PR、实现功能并修复 Bug。本文覆盖安装配置、云厂商集成、升级迁移及最佳实践。
category: translation
tags: [claude-code, github-actions, ci-cd, translation]
refs:
  - https://code.claude.com/docs/en/github-actions.md
---

# Claude Code GitHub Actions

> 通过 GitHub Actions 将 Claude Code 集成到开发工作流中，实现 AI 驱动的代码自动化。

**Claude Code GitHub Actions 把 AI 自动化能力带入 GitHub 工作流。** 只需在任何 PR 或 Issue 评论中 `@claude`，Claude 就能分析代码、创建 Pull Request、实现功能、修复 Bug，同时遵循你项目的编码规范。如果你需要每个 PR 自动发起代码审查（无需手动触发），请参阅 [GitHub Code Review](https://code.claude.com/docs/en/code-review)。

> [!NOTE]
> Claude Code GitHub Actions 基于 [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) 构建，该 SDK 支持以编程方式将 Claude Code 集成到你的应用中。你可以用它构建超越 GitHub Actions 的自定义自动化工作流。

## 为什么使用 Claude Code GitHub Actions？

| 能力 | 说明 |
|------|------|
| 即时创建 PR | 描述你的需求，Claude 创建包含所有必要变更的完整 PR |
| 自动化代码实现 | 一条命令就能把 Issue 变成可运行的代码 |
| 遵循项目规范 | Claude 遵守你的 `CLAUDE.md` 规范和现有代码风格 |
| 配置简单 | 几分钟内即可完成安装并拿到 API Key |
| 默认安全 | 代码始终在 GitHub 托管的 runner 上运行 |

## Claude 能做什么？

**Claude Code 提供一个强大的 GitHub Action，改变你与代码的协作方式。**

### Claude Code Action

这个 GitHub Action 允许你在 GitHub Actions 工作流中运行 Claude Code，你可以基于它构建任何自定义工作流。

[查看仓库 ->](https://github.com/anthropics/claude-code-action)

## 安装配置

### 快速安装

**在 Claude Code 终端中运行 `/install-github-app` 即可交互式完成集成。** 该命令会将 Claude GitHub App 安装到你的仓库，然后引导你添加 GitHub Actions 工作流文件和 API Key Secret。

GitHub App 安装完成后，命令会询问是否继续 GitHub Actions 配置。在 Claude Code v2.1.187 及更高版本中，你可以选择 **Skip for now** 仅完成 App 安装，稍后再运行 `/install-github-app` 回到工作流和 Secret 配置步骤。较早版本会直接进入工作流选择。

> [!NOTE]
> - 你必须是仓库管理员才能安装 GitHub App 和添加 Secret
> - GitHub App 会请求 Contents、Issues 和 Pull requests 的读写权限
> - 快速安装仅适用于直接使用 Claude API 的用户。如果使用 Amazon Bedrock 或 Google Vertex AI，请参阅[与 Amazon Bedrock 和 Google Vertex AI 配合使用](#与-amazon-bedrock-和-google-vertex-ai-配合使用)部分

### 手动安装

**如果 `/install-github-app` 命令失败或你更喜欢手动安装，请按以下步骤操作：**

1. **安装 Claude GitHub App 到你的仓库**：[https://github.com/apps/claude](https://github.com/apps/claude)

   Claude GitHub App 需要以下仓库权限：
   - **Contents**：读写（用于修改仓库文件）
   - **Issues**：读写（用于响应 Issue）
   - **Pull requests**：读写（用于创建 PR 和推送变更）

   更多安全和权限细节，参见[安全文档](https://github.com/anthropics/claude-code-action/blob/main/docs/security.md)。

2. **将 ANTHROPIC_API_KEY 添加到仓库 Secrets**（[了解如何在 GitHub Actions 中使用 Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)）

3. **复制工作流文件**：从 [examples/claude.yml](https://github.com/anthropics/claude-code-action/blob/main/examples/claude.yml) 复制到仓库的 `.github/workflows/` 目录

> [!TIP]
> 完成快速安装或手动安装后，在 Issue 或 PR 评论中 `@claude` 来测试 Action 是否正常工作。

## 从 Beta 版升级

> [!WARNING]
> Claude Code GitHub Actions v1.0 引入了破坏性变更，从 Beta 版升级到 v1.0 需要更新工作流文件。

**如果你正在使用 Beta 版，建议更新工作流以使用 GA 版本。** 新版本简化了配置，同时新增了自动模式检测等强大功能。

### 必须的变更

所有 Beta 用户升级时必须对工作流文件做以下修改：

1. **更新 Action 版本**：将 `@beta` 改为 `@v1`
2. **移除 mode 配置**：删除 `mode: "tag"` 或 `mode: "agent"`（现在自动检测）
3. **更新 prompt 输入**：将 `direct_prompt` 替换为 `prompt`
4. **迁移 CLI 选项**：将 `max_turns`、`model`、`custom_instructions` 等移入 `claude_args`

### 破坏性变更对照表

| Beta 版参数 | v1.0 新参数 |
|------------|-------------|
| `mode` | *（已移除 — 自动检测）* |
| `direct_prompt` | `prompt` |
| `override_prompt` | `prompt` + GitHub 变量 |
| `custom_instructions` | `claude_args: --append-system-prompt` |
| `max_turns` | `claude_args: --max-turns` |
| `model` | `claude_args: --model` |
| `allowed_tools` | `claude_args: --allowedTools` |
| `disallowed_tools` | `claude_args: --disallowedTools` |
| `claude_env` | `settings` JSON 格式 |

### 升级前后对比

**Beta 版：**

```yaml
- uses: anthropics/claude-code-action@beta
  with:
    mode: "tag"
    direct_prompt: "Review this PR for security issues"
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    custom_instructions: "Follow our coding standards"
    max_turns: "10"
    model: "claude-sonnet-4-6"
```

**GA 版 (v1.0)：**

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    prompt: "Review this PR for security issues"
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    claude_args: |
      --append-system-prompt "Follow our coding standards"
      --max-turns 10
      --model claude-sonnet-4-6
```

> [!TIP]
> Action 现在会根据配置自动检测是以交互模式运行（响应 `@claude` 提及）还是以自动化模式运行（立即执行 prompt）。

## 使用场景示例

**Claude Code GitHub Actions 可以帮你处理各类任务。** [examples 目录](https://github.com/anthropics/claude-code-action/tree/main/examples)包含针对不同场景的现成工作流。

### 基础工作流

```yaml
name: Claude Code
on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
jobs:
  claude:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          # 响应评论中的 @claude 提及
```

### 使用 Skills

**`prompt` 输入既接受纯文本，也接受 [skill](https://code.claude.com/docs/en/skills) 调用：**

- 对于仓库 `.claude/skills/` 目录中的 skill，先运行 `actions/checkout`，然后传入 `/skill-name`
- 对于插件中打包的 skill，用 `plugin_marketplaces` 和 `plugins` 输入安装插件，然后传入命名空间格式 `/plugin-name:skill-name`

以下工作流安装 `code-review` 插件，并在每次新建或更新 PR 时运行其 skill：

```yaml
name: Code Review
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          plugin_marketplaces: "https://github.com/anthropics/claude-code.git"
          plugins: "code-review@claude-code-plugins"
          prompt: "/code-review:code-review ${{ github.repository }}/pull/${{ github.event.pull_request.number }}"
```

### 自定义自动化 prompt

```yaml
name: Daily Report
on:
  schedule:
    - cron: "0 9 * * *"
jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: "Generate a summary of yesterday's commits and open issues"
          claude_args: "--model opus"
```

### 常见用法

在 Issue 或 PR 评论中：

```text
@claude implement this feature based on the issue description
@claude how should I implement user authentication for this endpoint?
@claude fix the TypeError in the user dashboard component
```

Claude 会自动分析上下文并做出适当回应。

## 最佳实践

### CLAUDE.md 配置

**在仓库根目录创建 `CLAUDE.md` 文件来定义代码风格、审查标准、项目规则和偏好模式。** 这个文件引导 Claude 理解你的项目标准。

### 安全考量

> [!WARNING]
> 绝不要把 API Key 直接提交到仓库中。

完整的安全指南（包括权限、认证和最佳实践）请参阅 [Claude Code Action 安全文档](https://github.com/anthropics/claude-code-action/blob/main/docs/security.md)。

始终使用 GitHub Secrets 管理 API Key：

- 将 API Key 添加为名为 `ANTHROPIC_API_KEY` 的仓库 Secret
- 在工作流中引用：`anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}`
- 将 Action 权限限制到最低必要范围
- 合并前务必审查 Claude 的建议

始终使用 GitHub Secrets（如 `${{ secrets.ANTHROPIC_API_KEY }}`），不要在工作流文件中硬编码 API Key。

### 性能优化

**使用 Issue 模板提供上下文，保持 `CLAUDE.md` 简洁聚焦，为工作流设置合理的超时时间。**

### CI 成本

使用 Claude Code GitHub Actions 时需注意相关成本：

**GitHub Actions 成本：**

- Claude Code 运行在 GitHub 托管的 runner 上，消耗你的 GitHub Actions 分钟数
- 详细定价和分钟限制参见 [GitHub 计费文档](https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-actions/about-billing-for-github-actions)

**API 成本：**

- 每次 Claude 交互会根据 prompt 和响应长度消耗 API token
- Token 用量因任务复杂度和代码库大小而异
- 当前 token 费率参见 [Claude 定价页面](https://claude.com/platform/api)

**成本优化建议：**

| 策略 | 说明 |
|------|------|
| 使用精确的 `@claude` 命令 | 减少不必要的 API 调用 |
| 在 `claude_args` 中配置合理的 `--max-turns` | 防止过度迭代 |
| 设置工作流级别的超时时间 | 避免失控任务 |
| 使用 GitHub 的并发控制 | 限制并行运行数量 |

## 配置示例

**Claude Code Action v1 通过统一参数简化了配置：**

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    prompt: "Your instructions here" # 可选
    claude_args: "--max-turns 5" # 可选 CLI 参数
```

核心特性：

- **统一 prompt 接口** — 用 `prompt` 传递所有指令
- **Skills 支持** — 直接在 prompt 中调用已安装的 [skill](https://code.claude.com/docs/en/skills)
- **CLI 透传** — 通过 `claude_args` 传递任何 Claude Code CLI 参数
- **灵活触发器** — 支持任何 GitHub 事件

完整的工作流文件请访问 [examples 目录](https://github.com/anthropics/claude-code-action/tree/main/examples)。

> [!TIP]
> 响应 Issue 或 PR 评论时，Claude 自动响应 @claude 提及。对于其他事件，使用 `prompt` 参数提供指令。

## 与 Amazon Bedrock 和 Google Vertex AI 配合使用

**对于企业环境，你可以将 Claude Code GitHub Actions 与自己的云基础设施配合使用。** 这种方式让你掌控数据驻留和计费，同时保持相同的功能。

### 前提条件

#### Google Cloud Vertex AI：

1. 已启用 Vertex AI 的 Google Cloud 项目
2. 为 GitHub Actions 配置好 Workload Identity Federation
3. 拥有所需权限的服务账号
4. GitHub App（推荐）或使用默认的 GITHUB_TOKEN

#### Amazon Bedrock：

1. 已启用 Amazon Bedrock 的 AWS 账户
2. 在 AWS 中配置好 GitHub OIDC Identity Provider
3. 拥有 Bedrock 权限的 IAM 角色
4. GitHub App（推荐）或使用默认的 GITHUB_TOKEN

### 步骤 1：创建自定义 GitHub App（推荐用于第三方提供商）

**使用 Vertex AI 或 Bedrock 等第三方提供商时，建议创建自己的 GitHub App 以获得最佳控制和安全性：**

1. 前往 [https://github.com/settings/apps/new](https://github.com/settings/apps/new)
2. 填写基本信息：
   - **GitHub App name**：选择一个唯一名称（如 "YourOrg Claude Assistant"）
   - **Homepage URL**：你的组织网站或仓库 URL
3. 配置 App 设置：
   - **Webhooks**：取消勾选 "Active"（此集成不需要）
4. 设置所需权限：
   - **Repository permissions**：
     - Contents：Read & Write
     - Issues：Read & Write
     - Pull requests：Read & Write
5. 点击 "Create GitHub App"
6. 创建后，点击 "Generate a private key" 并保存下载的 `.pem` 文件
7. 记下 App 设置页面中的 App ID
8. 将 App 安装到你的仓库：
   - 在 App 设置页面，点击左侧的 "Install App"
   - 选择你的账户或组织
   - 选择 "Only select repositories" 并选中目标仓库
   - 点击 "Install"
9. 将 private key 作为 Secret 添加到仓库：
   - 进入仓库 Settings -> Secrets and variables -> Actions
   - 创建名为 `APP_PRIVATE_KEY` 的 Secret，内容为 `.pem` 文件内容
10. 将 App ID 添加为 Secret：
    - 创建名为 `APP_ID` 的 Secret，值为你的 GitHub App ID

> [!NOTE]
> 这个 App 将与 [actions/create-github-app-token](https://github.com/actions/create-github-app-token) Action 配合使用，在工作流中生成认证 token。

**替代方案（直接使用 Claude API 或不想设置自己的 GitHub App）**：使用 Anthropic 官方 App：

1. 从 [https://github.com/apps/claude](https://github.com/apps/claude) 安装
2. 无需额外认证配置

### 步骤 2：配置云提供商认证

选择你的云提供商并设置安全认证：

#### Amazon Bedrock

**配置 AWS 以允许 GitHub Actions 无需存储凭据即可安全认证。**

> 安全提示：使用仓库级配置，仅授予最低必要权限。

**所需配置：**

1. **启用 Amazon Bedrock**：
   - 在 Amazon Bedrock 中请求 Claude 模型访问权限
   - 对于跨区域模型，在所有需要的区域请求访问

2. **设置 GitHub OIDC Identity Provider**：
   - Provider URL：`https://token.actions.githubusercontent.com`
   - Audience：`sts.amazonaws.com`

3. **创建 GitHub Actions 的 IAM 角色**：
   - Trusted entity type：Web identity
   - Identity provider：`token.actions.githubusercontent.com`
   - 权限：`AmazonBedrockFullAccess` 策略
   - 为你的特定仓库配置信任策略

**所需的值：**

完成配置后，你需要：

- **AWS_ROLE_TO_ASSUME**：你创建的 IAM 角色的 ARN

> [!TIP]
> OIDC 比使用静态 AWS Access Key 更安全，因为凭据是临时的并且自动轮换。

详细的 OIDC 配置说明参见 [AWS 文档](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html)。

#### Google Vertex AI

**配置 Google Cloud 以允许 GitHub Actions 无需存储凭据即可安全认证。**

> 安全提示：使用仓库级配置，仅授予最低必要权限。

**所需配置：**

1. **在 Google Cloud 项目中启用 API**：
   - IAM Credentials API
   - Security Token Service (STS) API
   - Vertex AI API

2. **创建 Workload Identity Federation 资源**：
   - 创建 Workload Identity Pool
   - 添加 GitHub OIDC provider：
     - Issuer：`https://token.actions.githubusercontent.com`
     - 配置 repository 和 owner 的属性映射
     - **安全建议**：使用仓库级属性条件

3. **创建 Service Account**：
   - 仅授予 `Vertex AI User` 角色
   - **安全建议**：为每个仓库创建专用 Service Account

4. **配置 IAM 绑定**：
   - 允许 Workload Identity Pool 模拟该 Service Account
   - **安全建议**：使用仓库级 principal sets

**所需的值：**

完成配置后，你需要：

- **GCP_WORKLOAD_IDENTITY_PROVIDER**：完整的 provider 资源名称
- **GCP_SERVICE_ACCOUNT**：Service Account 邮箱地址

> [!TIP]
> Workload Identity Federation 消除了对可下载 Service Account 密钥的需求，提高了安全性。

详细配置说明请参阅 [Google Cloud Workload Identity Federation 文档](https://cloud.google.com/iam/docs/workload-identity-federation)。

### 步骤 3：添加所需的 Secrets

将以下 Secrets 添加到仓库（Settings -> Secrets and variables -> Actions）：

#### Claude API（直连）：

| Secret 名称 | 说明 |
|-------------|------|
| `ANTHROPIC_API_KEY` | 来自 [console.anthropic.com](https://console.anthropic.com) 的 API Key |
| `APP_ID`（使用自定义 App 时） | 你的 GitHub App ID |
| `APP_PRIVATE_KEY`（使用自定义 App 时） | Private key (.pem) 内容 |

#### Google Cloud Vertex AI：

| Secret 名称 | 说明 |
|-------------|------|
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | Workload Identity Provider 资源名称 |
| `GCP_SERVICE_ACCOUNT` | 具有 Vertex AI 权限的 Service Account 邮箱 |
| `APP_ID`（使用自定义 App 时） | 你的 GitHub App ID |
| `APP_PRIVATE_KEY`（使用自定义 App 时） | Private key (.pem) 内容 |

#### Amazon Bedrock：

| Secret 名称 | 说明 |
|-------------|------|
| `AWS_ROLE_TO_ASSUME` | 用于 Bedrock 访问的 IAM 角色 ARN |
| `APP_ID`（使用自定义 App 时） | 你的 GitHub App ID |
| `APP_PRIVATE_KEY`（使用自定义 App 时） | Private key (.pem) 内容 |

### 步骤 4：创建工作流文件

创建与云提供商集成的 GitHub Actions 工作流文件。以下是 Amazon Bedrock 和 Google Vertex AI 的完整配置示例：

#### Amazon Bedrock 工作流

**前提条件：**

- 已启用 Amazon Bedrock 并获得 Claude 模型权限
- 在 AWS 中将 GitHub 配置为 OIDC Identity Provider
- 拥有 Bedrock 权限且信任 GitHub Actions 的 IAM 角色

**所需 GitHub Secrets：**

| Secret 名称 | 说明 |
|-------------|------|
| `AWS_ROLE_TO_ASSUME` | 用于 Bedrock 访问的 IAM 角色 ARN |
| `APP_ID` | 你的 GitHub App ID（App 设置页面获取） |
| `APP_PRIVATE_KEY` | 为 GitHub App 生成的 Private Key |

```yaml
name: Claude PR Action

permissions:
  contents: write
  pull-requests: write
  issues: write
  id-token: write

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
  issues:
    types: [opened, assigned]

jobs:
  claude-pr:
    if: |
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'pull_request_review_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'issues' && contains(github.event.issue.body, '@claude'))
    runs-on: ubuntu-latest
    env:
      AWS_REGION: us-west-2
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Generate GitHub App token
        id: app-token
        uses: actions/create-github-app-token@v2
        with:
          app-id: ${{ secrets.APP_ID }}
          private-key: ${{ secrets.APP_PRIVATE_KEY }}

      - name: Configure AWS Credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_TO_ASSUME }}
          aws-region: us-west-2

      - uses: anthropics/claude-code-action@v1
        with:
          github_token: ${{ steps.app-token.outputs.token }}
          use_bedrock: "true"
          claude_args: '--model us.anthropic.claude-sonnet-4-6 --max-turns 10'
```

> [!TIP]
> Bedrock 的模型 ID 格式包含区域前缀（如 `us.anthropic.claude-sonnet-4-6`）。

#### Google Vertex AI 工作流

**前提条件：**

- 在 GCP 项目中启用 Vertex AI API
- 为 GitHub 配置好 Workload Identity Federation
- 拥有 Vertex AI 权限的 Service Account

**所需 GitHub Secrets：**

| Secret 名称 | 说明 |
|-------------|------|
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | Workload Identity Provider 资源名称 |
| `GCP_SERVICE_ACCOUNT` | 具有 Vertex AI 权限的 Service Account 邮箱 |
| `APP_ID` | 你的 GitHub App ID（App 设置页面获取） |
| `APP_PRIVATE_KEY` | 为 GitHub App 生成的 Private Key |

```yaml
name: Claude PR Action

permissions:
  contents: write
  pull-requests: write
  issues: write
  id-token: write

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
  issues:
    types: [opened, assigned]

jobs:
  claude-pr:
    if: |
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'pull_request_review_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'issues' && contains(github.event.issue.body, '@claude'))
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Generate GitHub App token
        id: app-token
        uses: actions/create-github-app-token@v2
        with:
          app-id: ${{ secrets.APP_ID }}
          private-key: ${{ secrets.APP_PRIVATE_KEY }}

      - name: Authenticate to Google Cloud
        id: auth
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}
          service_account: ${{ secrets.GCP_SERVICE_ACCOUNT }}

      - uses: anthropics/claude-code-action@v1
        with:
          github_token: ${{ steps.app-token.outputs.token }}
          trigger_phrase: "@claude"
          use_vertex: "true"
          claude_args: '--model claude-sonnet-4-5@20250929 --max-turns 10'
        env:
          ANTHROPIC_VERTEX_PROJECT_ID: ${{ steps.auth.outputs.project_id }}
          CLOUD_ML_REGION: us-east5
          VERTEX_REGION_CLAUDE_4_5_SONNET: us-east5
```

> [!TIP]
> Project ID 从 Google Cloud 认证步骤自动获取，无需硬编码。

## 故障排查

### Claude 不响应 @claude 命令

**检查以下几点：** 确认 GitHub App 安装正确，确认 Workflows 已启用，确认 API Key 已设置在仓库 Secrets 中，确认评论包含 `@claude`（不是 `/claude`）。

### CI 不在 Claude 的提交上运行

**确认你使用的是 GitHub App 或自定义 App（不是 Actions 用户）**，检查工作流触发器是否包含必要事件，验证 App 权限是否包含 CI 触发。

### 认证错误

确认 API Key 有效且权限充足。对于 Bedrock/Vertex，检查凭据配置，确保工作流中的 Secret 名称正确。

## 高级配置

### Action 参数

**Claude Code Action v1 采用简化配置：**

| 参数 | 说明 | 是否必需 |
|------|------|---------|
| `prompt` | Claude 的指令（纯文本或 [skill](https://code.claude.com/docs/en/skills) 名称） | 否* |
| `claude_args` | 传递给 Claude Code 的 CLI 参数 | 否 |
| `plugin_marketplaces` | 插件市场 Git URL 列表（换行分隔） | 否 |
| `plugins` | 执行前要安装的插件名称列表（换行分隔） | 否 |
| `anthropic_api_key` | Claude API Key | 是** |
| `github_token` | 用于 API 访问的 GitHub Token | 否 |
| `trigger_phrase` | 自定义触发短语（默认："@claude"） | 否 |
| `use_bedrock` | 使用 Amazon Bedrock 而非 Claude API | 否 |
| `use_vertex` | 使用 Google Vertex AI 而非 Claude API | 否 |

\*prompt 可选 — 对于 Issue/PR 评论省略时，Claude 响应触发短语
\*\*直接使用 Claude API 时必需，Bedrock/Vertex 不需要

#### 传递 CLI 参数

`claude_args` 参数接受任何 Claude Code CLI 参数：

```yaml
claude_args: "--max-turns 5 --model claude-sonnet-4-6 --mcp-config /path/to/config.json"
```

常用参数：

| 参数 | 说明 |
|------|------|
| `--max-turns` | 最大对话轮次（默认：10） |
| `--model` | 使用的模型（如 `claude-sonnet-4-6`） |
| `--mcp-config` | MCP 配置路径 |
| `--allowedTools` | 允许的工具列表（逗号分隔）。别名 `--allowed-tools` 同样有效 |
| `--debug` | 启用调试输出 |

### 替代集成方式

**虽然 `/install-github-app` 命令是推荐方式，你也可以选择：**

- **自定义 GitHub App**：适用于需要品牌化用户名或自定义认证流的组织。创建拥有所需权限（contents、issues、pull requests）的 GitHub App，并使用 actions/create-github-app-token Action 在工作流中生成 token。
- **手动 GitHub Actions**：直接配置工作流，获得最大灵活性
- **MCP 配置**：动态加载 Model Context Protocol 服务器

详细的认证、安全和高级配置指南请参阅 [Claude Code Action 文档](https://github.com/anthropics/claude-code-action/blob/main/docs)。

### 自定义 Claude 的行为

**你可以通过两种方式配置 Claude 的行为：**

1. **CLAUDE.md**：在仓库根目录创建 `CLAUDE.md` 文件，定义编码标准、审查标准和项目规则。Claude 在创建 PR 和响应请求时会遵循这些准则。详见 [Memory 文档](https://code.claude.com/docs/en/memory)。
2. **自定义 prompt**：在工作流文件中使用 `prompt` 参数提供工作流级别的指令。这允许你为不同工作流或任务自定义 Claude 的行为。
