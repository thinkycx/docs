---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】GitLab CI/CD
description: Claude Code 与 GitLab CI/CD 的集成指南。通过在 CI/CD 流水线中运行 Claude，实现从 Issue 自动创建 MR、代码审查、Bug 修复等 AI 驱动的开发工作流。支持 Claude API、Amazon Bedrock 和 Google Vertex AI 三种后端。
category: translation
tags: [claude-code, gitlab, ci-cd, translation]
refs: [https://code.claude.com/docs/en/gitlab-ci-cd.md]
---

# Claude Code GitLab CI/CD

**将 Claude Code 集成到 GitLab CI/CD 中，可以在流水线中运行 AI 任务，自动创建 MR、修复 Bug、响应评论。支持 Claude API、Amazon Bedrock 和 Google Vertex AI 三种后端。**

> [!NOTE]
> Claude Code for GitLab CI/CD 目前处于 beta 阶段，功能可能会随迭代而变化。
>
> 该集成由 GitLab 维护。如需支持，请参阅 [GitLab issue](https://gitlab.com/gitlab-org/gitlab/-/issues/573776)。

> [!NOTE]
> 该集成基于 [Claude Code CLI 和 Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) 构建，支持在 CI/CD 任务和自定义自动化工作流中以编程方式使用 Claude。

## 为什么在 GitLab 中使用 Claude Code？

**核心价值在于将 AI 能力嵌入你已有的 GitLab 工作流，无需切换上下文。**

| 能力 | 说明 |
| :--- | :--- |
| 即时创建 MR | 描述需求，Claude 自动生成完整的 MR（含变更和说明） |
| 自动化实现 | 一条命令或一次 @mention 就能把 Issue 变成可运行的代码 |
| 项目感知 | Claude 遵循 `CLAUDE.md` 约定和现有代码风格 |
| 配置简单 | 在 `.gitlab-ci.yml` 中加一个 job + 一个 masked 变量即可 |
| 企业级 | 可选 Claude API、Amazon Bedrock 或 Google Vertex AI，满足数据驻留和采购要求 |
| 默认安全 | 在你自己的 Runner 上运行，分支保护和审批规则照常生效 |

## 工作原理

**Claude Code 通过 GitLab CI/CD 在隔离的 job 中运行 AI 任务，将结果以 MR 的形式提交回代码库。**

1. **事件驱动编排**：GitLab 监听你选择的触发方式（例如在 Issue、MR 或 Review 线程中 @claude 评论）。Job 从线程和仓库中收集上下文，构建 prompt，然后运行 Claude Code。

2. **后端抽象**：根据环境选择合适的提供商：
   - Claude API（SaaS）
   - Amazon Bedrock（基于 IAM 的访问，跨区域选项）
   - Google Vertex AI（GCP 原生，Workload Identity Federation）

3. **沙箱执行**：每次交互运行在有严格网络和文件系统规则的容器中。Claude Code 通过工作区范围的权限约束写入操作。所有变更都通过 MR 流转，审阅者可以看到 diff，审批规则照常生效。

选择区域端点可以降低延迟并满足数据主权要求，同时利用现有的云服务协议。

## Claude 能做什么？

**Claude Code 在 CI/CD 工作流中的典型用途：**

- 根据 Issue 描述或评论创建和更新 MR
- 分析性能回退并提出优化方案
- 直接在分支中实现功能，然后开 MR
- 修复测试或评论中发现的 Bug 和回退
- 响应后续评论进行迭代修改

## 配置

### 快速配置

**最快的上手方式：在 `.gitlab-ci.yml` 中加一个最小 job，并将 API Key 设为 masked 变量。**

1. **添加 masked CI/CD 变量**
   - 进入 **Settings** → **CI/CD** → **Variables**
   - 添加 `ANTHROPIC_API_KEY`（masked，按需 protected）

2. **在 `.gitlab-ci.yml` 中添加 Claude job**

```yaml
stages:
  - ai

claude:
  stage: ai
  image: node:24-alpine3.21
  # 根据你想要的触发方式调整 rules：
  # - 手动运行
  # - merge request 事件
  # - 当评论包含 '@claude' 时通过 web/API 触发
  rules:
    - if: '$CI_PIPELINE_SOURCE == "web"'
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
  variables:
    GIT_STRATEGY: fetch
  before_script:
    - apk update
    - apk add --no-cache git curl bash
    - curl -fsSL https://claude.ai/install.sh | bash
  script:
    # 可选：如果你的环境提供了 GitLab MCP server，在此启动
    - /bin/gitlab-mcp-server || true
    # 通过 web/API 触发并附带上下文时使用 AI_FLOW_* 变量
    - echo "$AI_FLOW_INPUT for $AI_FLOW_CONTEXT on $AI_FLOW_EVENT"
    - >
      claude
      -p "${AI_FLOW_INPUT:-'Review this MR and implement the requested changes'}"
      --permission-mode acceptEdits
      --allowedTools "Bash Read Edit Write mcp__gitlab"
      --debug
```

添加 job 和 `ANTHROPIC_API_KEY` 变量后，可以从 **CI/CD** → **Pipelines** 手动运行 job 进行测试，或从 MR 中触发让 Claude 在分支中提出更新并按需创建 MR。

> [!NOTE]
> 如果要使用 Amazon Bedrock 或 Google Vertex AI 而非 Claude API，请参阅下方 [使用 Amazon Bedrock 和 Google Vertex AI](#使用-amazon-bedrock-和-google-vertex-ai) 部分了解认证和环境配置。

### 手动配置（推荐用于生产环境）

**如果你需要更精细的控制或使用企业级后端：**

1. **配置后端访问**：
   - **Claude API**：创建 `ANTHROPIC_API_KEY` 并存储为 masked CI/CD 变量
   - **Amazon Bedrock**：配置 **GitLab** → **AWS OIDC** 并创建具有 Bedrock 权限的 IAM 角色
   - **Google Vertex AI**：为 GitLab 配置 Workload Identity Federation → GCP

2. **添加 GitLab API 操作所需的项目凭据**：
   - 默认使用 `CI_JOB_TOKEN`，或创建具有 `api` scope 的 Project Access Token
   - 如使用 PAT，存储为 `GITLAB_ACCESS_TOKEN`（masked）

3. **在 `.gitlab-ci.yml` 中添加 Claude job**（见下方示例）

4. **（可选）启用 @mention 触发**：
   - 为 "Comments (notes)" 添加项目 Webhook 到你的事件监听器
   - 当评论包含 `@claude` 时，让监听器通过 Pipeline Trigger API 调用并传入 `AI_FLOW_INPUT` 和 `AI_FLOW_CONTEXT` 等变量

## 使用示例

### 从 Issue 生成 MR

在 Issue 评论中：

```text
@claude implement this feature based on the issue description
```

Claude 分析 Issue 和代码库，在分支中写入变更，然后创建 MR 供审查。

### 获取实现建议

在 MR 讨论中：

```text
@claude suggest a concrete approach to cache the results of this API call
```

Claude 提出方案，添加适当的缓存代码，并更新 MR。

### 快速修复 Bug

在 Issue 或 MR 评论中：

```text
@claude fix the TypeError in the user dashboard component
```

Claude 定位 Bug，实现修复，并更新分支或创建新 MR。

## 使用 Amazon Bedrock 和 Google Vertex AI

**对于企业环境，你可以在自己的云基础设施上运行 Claude Code，获得相同的开发体验。**

### Amazon Bedrock

#### 前置条件

| 条件 | 说明 |
| :--- | :--- |
| AWS 账户 | 已开通 Amazon Bedrock 并获得所需 Claude 模型的访问权限 |
| GitLab OIDC | GitLab 已配置为 AWS IAM 中的 OIDC 身份提供商 |
| IAM 角色 | 具有 Bedrock 权限，信任策略限制到你的 GitLab 项目/分支 |
| CI/CD 变量 | `AWS_ROLE_TO_ASSUME`（角色 ARN）、`AWS_REGION`（Bedrock 区域） |

#### 配置步骤

配置 AWS 允许 GitLab CI job 通过 OIDC 承担 IAM 角色（无需静态 Key）。

**必需配置：**

1. 启用 Amazon Bedrock 并申请目标 Claude 模型的访问权限
2. 如果尚未创建，为 GitLab 创建 IAM OIDC 提供商
3. 创建信任 GitLab OIDC 提供商的 IAM 角色，限制到你的项目和受保护分支
4. 附加 Bedrock invoke API 的最小权限策略

**需要存储为 CI/CD 变量的值：**

- `AWS_ROLE_TO_ASSUME`
- `AWS_REGION`

在 Settings → CI/CD → Variables 中添加变量。

### Google Vertex AI

#### 前置条件

| 条件 | 说明 |
| :--- | :--- |
| Google Cloud 项目 | 已启用 Vertex AI API，配置了信任 GitLab OIDC 的 Workload Identity Federation |
| 专用服务账号 | 仅具有所需 Vertex AI 角色 |
| CI/CD 变量 | `GCP_WORKLOAD_IDENTITY_PROVIDER`（完整资源名称）、`GCP_SERVICE_ACCOUNT`（服务账号邮箱） |

#### 配置步骤

配置 Google Cloud 允许 GitLab CI job 通过 Workload Identity Federation 模拟服务账号。

**必需配置：**

1. 启用 IAM Credentials API、STS API 和 Vertex AI API
2. 为 GitLab OIDC 创建 Workload Identity Pool 和 Provider
3. 创建具有 Vertex AI 角色的专用服务账号
4. 授予 WIF principal 模拟服务账号的权限

**需要存储为 CI/CD 变量的值：**

- `GCP_WORKLOAD_IDENTITY_PROVIDER`
- `GCP_SERVICE_ACCOUNT`
- `CLOUD_ML_REGION`（例如 `us-east5`）

## 配置示例

### 基础 .gitlab-ci.yml（Claude API）

```yaml
stages:
  - ai

claude:
  stage: ai
  image: node:24-alpine3.21
  rules:
    - if: '$CI_PIPELINE_SOURCE == "web"'
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
  variables:
    GIT_STRATEGY: fetch
  before_script:
    - apk update
    - apk add --no-cache git curl bash
    - curl -fsSL https://claude.ai/install.sh | bash
  script:
    - /bin/gitlab-mcp-server || true
    - >
      claude
      -p "${AI_FLOW_INPUT:-'Summarize recent changes and suggest improvements'}"
      --permission-mode acceptEdits
      --allowedTools "Bash Read Edit Write mcp__gitlab"
      --debug
  # Claude Code 将使用 CI/CD 变量中的 ANTHROPIC_API_KEY
```

### Amazon Bedrock job 示例（OIDC）

**前置条件：**

- Amazon Bedrock 已启用并获得所选 Claude 模型的访问权限
- GitLab OIDC 已配置在 AWS 中，角色信任你的 GitLab 项目和分支
- IAM 角色具有 Bedrock 权限（建议最小权限）

**必需 CI/CD 变量：**

- `AWS_ROLE_TO_ASSUME`：用于 Bedrock 访问的 IAM 角色 ARN
- `AWS_REGION`：Bedrock 区域（例如 `us-west-2`）

```yaml
claude-bedrock:
  stage: ai
  image: node:24-alpine3.21
  rules:
    - if: '$CI_PIPELINE_SOURCE == "web"'
  before_script:
    - apk add --no-cache bash curl jq git python3 py3-pip
    - pip install --no-cache-dir awscli
    - curl -fsSL https://claude.ai/install.sh | bash
    # 用 GitLab OIDC token 换取 AWS 凭据
    - export AWS_WEB_IDENTITY_TOKEN_FILE="${CI_JOB_JWT_FILE:-/tmp/oidc_token}"
    - if [ -n "${CI_JOB_JWT_V2}" ]; then printf "%s" "$CI_JOB_JWT_V2" > "$AWS_WEB_IDENTITY_TOKEN_FILE"; fi
    - >
      aws sts assume-role-with-web-identity
      --role-arn "$AWS_ROLE_TO_ASSUME"
      --role-session-name "gitlab-claude-$(date +%s)"
      --web-identity-token "file://$AWS_WEB_IDENTITY_TOKEN_FILE"
      --duration-seconds 3600 > /tmp/aws_creds.json
    - export AWS_ACCESS_KEY_ID="$(jq -r .Credentials.AccessKeyId /tmp/aws_creds.json)"
    - export AWS_SECRET_ACCESS_KEY="$(jq -r .Credentials.SecretAccessKey /tmp/aws_creds.json)"
    - export AWS_SESSION_TOKEN="$(jq -r .Credentials.SessionToken /tmp/aws_creds.json)"
  script:
    - /bin/gitlab-mcp-server || true
    - >
      claude
      -p "${AI_FLOW_INPUT:-'Implement the requested changes and open an MR'}"
      --permission-mode acceptEdits
      --allowedTools "Bash Read Edit Write mcp__gitlab"
      --debug
  variables:
    AWS_REGION: "us-west-2"
```

> [!NOTE]
> Bedrock 的 Model ID 包含区域前缀（例如 `us.anthropic.claude-sonnet-4-6`）。在 job 配置或 prompt 中传入所需模型。

### Google Vertex AI job 示例（Workload Identity Federation）

**前置条件：**

- 你的 GCP 项目已启用 Vertex AI API
- 已配置信任 GitLab OIDC 的 Workload Identity Federation
- 具有 Vertex AI 权限的服务账号

**必需 CI/CD 变量：**

- `GCP_WORKLOAD_IDENTITY_PROVIDER`：完整 Provider 资源名称
- `GCP_SERVICE_ACCOUNT`：服务账号邮箱
- `CLOUD_ML_REGION`：Vertex 区域（例如 `us-east5`）

```yaml
claude-vertex:
  stage: ai
  image: gcr.io/google.com/cloudsdktool/google-cloud-cli:slim
  rules:
    - if: '$CI_PIPELINE_SOURCE == "web"'
  before_script:
    - apt-get update && apt-get install -y git && apt-get clean
    - curl -fsSL https://claude.ai/install.sh | bash
    # 通过 WIF 认证到 Google Cloud（无需下载 Key）
    - >
      gcloud auth login --cred-file=<(cat <<EOF
      {
        "type": "external_account",
        "audience": "${GCP_WORKLOAD_IDENTITY_PROVIDER}",
        "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
        "service_account_impersonation_url": "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/${GCP_SERVICE_ACCOUNT}:generateAccessToken",
        "token_url": "https://sts.googleapis.com/v1/token"
      }
      EOF
      )
    - gcloud config set project "$(gcloud projects list --format='value(projectId)' --filter="name:${CI_PROJECT_NAMESPACE}" | head -n1)" || true
  script:
    - /bin/gitlab-mcp-server || true
    - >
      CLOUD_ML_REGION="${CLOUD_ML_REGION:-us-east5}"
      claude
      -p "${AI_FLOW_INPUT:-'Review and update code as requested'}"
      --permission-mode acceptEdits
      --allowedTools "Bash Read Edit Write mcp__gitlab"
      --debug
  variables:
    CLOUD_ML_REGION: "us-east5"
```

> [!NOTE]
> 使用 Workload Identity Federation 时无需存储服务账号 Key。建议使用仓库范围的信任条件和最小权限服务账号。

## 最佳实践

### CLAUDE.md 配置

**在仓库根目录创建 `CLAUDE.md` 文件，定义编码规范、审查标准和项目特定规则。** Claude 在运行时会读取该文件，并在生成变更时遵循你的约定。

### 安全注意事项

**绝对不要将 API Key 或云凭据提交到仓库。** 始终使用 GitLab CI/CD 变量：

- 将 `ANTHROPIC_API_KEY` 添加为 masked 变量（按需 protect）
- 尽可能使用后端特定的 OIDC（无长期有效的 Key）
- 限制 job 权限和网络出口
- 像审查其他贡献者一样审查 Claude 的 MR

### 性能优化

- `CLAUDE.md` 保持精简聚焦
- 提供清晰的 Issue/MR 描述以减少迭代次数
- 配置合理的 job 超时以避免失控运行
- 在 Runner 中缓存 npm 和包安装

### CI 成本

**使用 Claude Code + GitLab CI/CD 时需要关注的成本：**

| 成本类型 | 说明 |
| :--- | :--- |
| GitLab Runner 时间 | Claude 在你的 Runner 上运行，消耗计算分钟数。详见 GitLab 计划的 Runner 计费说明 |
| API 成本 | 每次 Claude 交互根据 prompt 和响应大小消耗 token。token 用量因任务复杂度和代码库大小而异。详见 [Anthropic 定价](https://platform.claude.com/docs/en/about-claude/pricing) |

**成本优化建议：**

- 使用明确的 `@claude` 命令减少不必要的轮次
- 设置适当的 `max_turns` 和 job 超时值
- 限制并发以控制并行运行数

## 安全与治理

- 每个 job 运行在有限制网络访问的隔离容器中
- Claude 的变更通过 MR 流转，审阅者可以看到每个 diff
- 分支保护和审批规则适用于 AI 生成的代码
- Claude Code 使用工作区范围的权限约束写入
- 成本在你的控制下，因为使用你自己的后端凭据

## 故障排除

### Claude 不响应 @claude 命令

- 验证你的流水线已被触发（手动、MR 事件，或通过 note 事件监听器/Webhook）
- 确保 CI/CD 变量（`ANTHROPIC_API_KEY` 或云后端设置）存在且未被遮罩
- 检查评论是否包含 `@claude`（而非 `/claude`），且 mention 触发器已配置

### Job 无法写评论或开 MR

- 确保 `CI_JOB_TOKEN` 对项目有足够权限，或使用具有 `api` scope 的 Project Access Token
- 检查 `--allowedTools` 中已启用 `mcp__gitlab` 工具
- 确认 job 运行在 MR 上下文中或通过 `AI_FLOW_*` 变量提供了足够上下文

### 认证错误

- **Claude API**：确认 `ANTHROPIC_API_KEY` 有效且未过期
- **Bedrock/Vertex**：验证 OIDC/WIF 配置、角色模拟和 secret 名称；确认区域和模型可用性

## 高级配置

### 常用参数和变量

Claude Code 支持以下常用输入：

| 参数/变量 | 说明 |
| :--- | :--- |
| `prompt` / `prompt_file` | 通过 `-p` 内联提供指令或通过文件提供 |
| `max_turns` | 限制来回迭代的最大次数 |
| `timeout_minutes` | 限制总执行时间 |
| `ANTHROPIC_API_KEY` | Claude API 必需（Bedrock/Vertex 不使用） |
| 后端特定环境变量 | `AWS_REGION`、Vertex 的 project/region 变量 |

> [!NOTE]
> 具体 flag 和参数可能因 `@anthropic-ai/claude-code` 版本而异。在 job 中运行 `claude --help` 查看支持的选项。

### 自定义 Claude 的行为

你可以通过两种主要方式引导 Claude：

1. **CLAUDE.md**：定义编码规范、安全要求和项目约定。Claude 在运行时读取此文件并遵循你的规则。
2. **自定义 prompt**：通过 job 中的 `prompt`/`prompt_file` 传入任务特定指令。不同 job 可以使用不同 prompt（例如审查、实现、重构）。
