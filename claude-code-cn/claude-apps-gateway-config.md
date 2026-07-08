---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Apps Gateway 配置
description: Claude Apps Gateway 的 gateway.yaml 配置参考。涵盖监听和 TLS、OIDC、会话、Postgres 存储、多种上游服务商、模型路由、托管策略和遥测。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/claude-apps-gateway-config.md
  - en-source/claude-apps-gateway-config.md
---

# Claude Apps Gateway 配置参考

> gateway.yaml 所有选项的参考：监听和 TLS、OIDC、会话、Postgres 存储、Amazon Bedrock/Claude Platform on AWS/Google Cloud Agent Platform/Microsoft Foundry 上游、模型路由、托管策略和遥测。

**Claude apps gateway 通过一个 YAML 文件配置**，通常命名为 `gateway.yaml`。文件定义 gateway 的所有行为：监听位置、开发者如何登录、推理去向、应用哪些策略和遥测。

首次编写建议从[快速入门](https://code.claude.com/docs/en/claude-apps-gateway#quickstart)开始。配置满意后，[部署指南](https://code.claude.com/docs/en/claude-apps-gateway-deploy)涵盖容器化和在 Kubernetes、Cloud Run 上托管。

Gateway 在启动时读取文件一次：`claude gateway --config /path/to/gateway.yaml`。所有选项在启动时按 schema 验证，错误配置在启动时以字段级错误失败而非首次使用时。未知 key 导致启动失败，拼写错误作为命名错误暴露。

## 文件结构

**五个部分为[必需](#必需部分)。** 其他部分为[可选](#可选部分)，省略时取默认值。

**必需部分：**

- [`listen`](#listen)：绑定地址、公共 URL、TLS 终止
- [`oidc`](#oidc)：身份提供者（IdP），包括 issuer、客户端、声明映射和谁可登录
- [`session`](#session)：gateway 签发的 bearer token，含密钥和生命周期
- [`store`](#store)：PostgreSQL，用于设备授权和限速计数器
- [`upstreams`](#upstreams)：推理去向

**可选部分：**

- [`admin`](#admin)：Admin API 认证和消费限额保留
- [`enforcement`](#enforcement)：消费限额 fail-open/fail-closed 行为
- [`models`](#models)：管理员策划的模型列表和按上游 ID
- [`managed`](#managed)：按 IdP 组的托管设置策略
- [`telemetry`](#telemetry)：向你的可观测性栈转发 OTLP
- [`access_control`、`limits`、`timeouts`、`rate_limits`](#http-调优)：IP 允许/拒绝、请求大小限制、上游首字节超时和每 IP 登录限速

## 秘密展开

不要在 `gateway.yaml` 中直接写秘密。使用以下形式引用：

| 形式 | 解析为 | 用于 |
| --- | --- | --- |
| `${VAR}` | 环境变量 `VAR`。未定义时启动失败 | 容器环境变量、AWS Secrets Manager 注入 |
| `${file:/path}` | 文件内容（trim 后） | Kubernetes Secret 卷挂载、Vault Agent、SOPS |

## 必需部分

### `listen`

控制 gateway 在哪里服务：绑定地址和端口、外部可见源和可选 TLS 终止。

| 字段 | 必需 | 说明 |
| --- | --- | --- |
| `host` | 否 | 绑定地址。默认 `0.0.0.0` |
| `port` | 否 | 绑定端口。默认 `8080` |
| `public_url` | 代理后必需 | 外部可见的 `https://` 源，用于构建 IdP `redirect_uri` 和发现元数据。启用[遥测](#telemetry)也需要 |
| `tls.cert` / `tls.key` | 否 | Gateway 自行终止 TLS 时的 PEM 路径 |
| `trusted_proxies` | 否 | 前置负载均衡器的 CIDR 或 IP。设置后 gateway 仅信任这些对端的 `X-Forwarded-For`，记录真实客户端 IP |

### `oidc`

连接 gateway 到身份提供者并决定谁可登录。

| 字段 | 必需 | 说明 |
| --- | --- | --- |
| `issuer` | 是 | OIDC 发现基础。必须在 `/.well-known/openid-configuration` 提供发现文档 |
| `client_id` / `client_secret` | 是 | OAuth 客户端注册 |
| `allowed_email_domains` | 否 | 拒绝 `email` 声明不在这些域中的 id_token |
| `allowed_groups` | 否 | 限制登录到这些 IdP 组的成员 |
| `groups_claim` | 否 | 哪个 id_token 声明携带组成员。默认 `groups`。Entra 用 `roles` |
| `google_groups` | 否 | 通过 Google Workspace Admin SDK Directory API 查询用户组 |
| `email_claim` | 否 | 哪个声明携带邮箱。默认 `email` |
| `scopes` | 否 | 完全覆盖请求的 OIDC scope。默认 `[openid, profile, email, offline_access]` |
| `extra_auth_params` | 否 | 附加到 IdP 授权请求的额外查询参数 |
| `userinfo_fallback` | 否 | id_token 省略 email 或 groups 时从 `/userinfo` 获取。默认 `false` |
| `use_pkce` | 否 | 发送 PKCE（S256）挑战。默认 `true` |
| `clock_skew_seconds` | 否 | 容忍时钟漂移。默认 `0` |
| `token_endpoint_auth_method` | 否 | 覆盖 token 端点认证方法 |
| `id_token_signed_response_alg` | 否 | 预期签名算法。默认 `RS256` |
| `form_action_origins` | 否 | `/device` 页面 CSP form-action 的额外源 |
| `ca_cert_pem` | 否 | 仅用于 IdP 请求的 PEM CA 证书 |

### `session`

| 字段 | 必需 | 说明 |
| --- | --- | --- |
| `jwt_secret` | 是 | 至少 32 字节熵。签署 HS256 bearer token。接受单字符串或数组用于轮换 |
| `ttl_hours` | 否 | Bearer token 生命周期。默认 `1` |

### `store`

| 字段 | 必需 | 说明 |
| --- | --- | --- |
| `postgres_url` | 是 | `postgres://` 或 `postgresql://` URL |
| `username` | 否 | 覆盖 URL 中的用户 |
| `password` | 否 | 数据库凭证，优先于 URL 中的凭证 |
| `max_connections` | 否 | 每副本连接池大小。默认 `5` |

### `upstreams`

**`upstreams` 是有序列表。** Gateway 将推理转发到第一个能解析请求模型的上游。`5xx`、`429`、`401`、`403`、`404` 或超时时故障转移到下一个；其他 `4xx` 不转移。

支持的上游服务商：

**Anthropic API：**

```yaml
upstreams:
  - provider: anthropic
    auth:
      api_key: ${ANTHROPIC_API_KEY}
```

**Amazon Bedrock：**

```yaml
upstreams:
  - provider: bedrock
    region: us-east-1
    auth: {}   # AWS 默认凭证链
```

**Claude Platform on AWS（需 v2.1.198+）：**

```yaml
upstreams:
  - provider: anthropicAws
    region: us-east-1
    workspace_id: wrkspc_...
    auth:
      api_key: ${ANTHROPIC_AWS_API_KEY}
```

**Google Cloud Agent Platform：**

```yaml
upstreams:
  - provider: vertex
    region: us-east5
    project_id: example-prod
    auth: {}   # Application Default Credentials
```

**Microsoft Foundry：**

```yaml
upstreams:
  - provider: foundry
    resource: example-foundry
    auth: { use_azure_ad: true }
```

**多上游故障转移**：同一服务商可多次出现（需设不同 `name:`）。覆盖不同区域、不同账户、预置吞吐量 vs 按需、跨服务商回退。

## 可选部分

### `admin`

启用 `/v1/organizations/spend_limits` 和逐开发者消费强制。参见 [Spend limits](https://code.claude.com/docs/en/claude-apps-gateway-spend-limits)。

| 字段 | 说明 |
| --- | --- |
| `write_keys` | `{id, key}` 数组，完全访问 admin 端点 |
| `read_keys` | `{id, key}` 数组，仅 GET 访问 |
| `admin_groups` | IdP 组名，JWT 含此组的用户有完全 admin 访问 |
| `blocked_message` | 附加到 429 消息的文本 |
| `audit_retention_days` | 默认 365 |
| `spend_retention_months` | 默认 13 |
| `identity_retention_days` | 默认 90 |
| `group_limit_mode` | `min`（默认）或 `max` |

### `enforcement`

| 字段 | 说明 |
| --- | --- |
| `fail_closed_on_error` | 默认 `false`。Postgres 中断时消费强制 fail-open |

### `models`

**可选的管理员策划模型列表**，在 `/v1/models` 提供并用于按上游翻译模型 ID。非美国 Bedrock 区域、预置吞吐量 ARN 和 Microsoft Foundry 部署名称必需。

```yaml
auto_include_builtin_models: true
models:
  - id: claude-opus-4-8
    label: Claude Opus 4.8
    upstream_model:
      anthropic: claude-opus-4-8
      bedrock: us.anthropic.claude-opus-4-8
      foundry: your-opus-deployment-name
```

### `managed`

**按 IdP 组或邮箱域定义基于角色的访问策略。** 策略按顺序评估，首个匹配被选中。

```yaml
managed:
  policies:
    - match: { groups: [eng-contractors] }
      cli:
        availableModels: [claude-sonnet-4-6]
        permissions: { deny: ["WebFetch", "WebSearch"] }
    - match: {}
      cli:
        availableModels: [claude-opus-4-8, claude-sonnet-4-6, claude-haiku-4-5]
```

**`match: {}` 作为基础层**，其他策略继承未设置的 key。合并规则：

- **白名单**（`availableModels`、`permissions.allow`）：具体策略完全替换基础
- **黑名单和 hook 数组**：取并集
- **记录类型 key**（`env`、`modelOverrides`）：浅合并

`availableModels` 同时在 `/v1/messages` 服务端强制。

匹配器：

| 匹配器 | 行为 |
| --- | --- |
| `match: {}` | 匹配所有已认证用户 |
| `match: { groups: [a, b] }` | JWT groups 声明包含任一列出组 |
| `match: { email_domain: example.com }` | 邮箱域匹配 |
| 两者组合 | 两个条件都必须匹配 |

**`cli` 中的内容**

每个 `cli` 值是完整的 Claude Code `managed-settings.json` 文档（用 YAML 表达）。运维方常用的 key：

| Key | 强制方 | 效果 |
| --- | --- | --- |
| `availableModels` | Gateway + CLI | 模型白名单 |
| `permissions.allow` / `.deny` | CLI | 工具和命令规则 |
| `permissions.disableBypassPermissionsMode` | CLI | 设为 `disable` 阻止 `--dangerously-skip-permissions` |
| `allowManagedPermissionRulesOnly` | CLI | `true` 时忽略用户和项目权限规则 |
| `env` | CLI | 合并到 CLI 进程的环境变量 |
| `hooks` | CLI | 组织级 hooks |

**安全批准对话框**：因设置通过网络到达，CLI 在应用任何可运行 shell 命令或改变流量方向的内容前向开发者显示一次性安全批准对话框。

**优先级**：设备同时有本地 `managed-settings.json` 或 MDM 策略时，最高优先级源提供所有策略设置。优先级从高到低：策略 helper > Gateway 下发 > MDM > `managed-settings.json` 文件 > HKCU 注册表。

### `telemetry`

**CLI 向 gateway 发送 OTLP over HTTP 的 metrics、logs 和可选 traces**，gateway 逐字转发到各配置目标。

```yaml
telemetry:
  forward_to:
    - url: https://otel-collector.internal.example.com
      headers:
        Authorization: ${OTLP_TOKEN}
      metrics: true
      logs: false
      traces: false
```

每个目标独立 opt-in `metrics`、`logs` 和 `traces`，默认仅 metrics。信号敏感度不同：

- **Metrics**：聚合计数器（token 数、请求数、延迟）
- **Logs 和 traces**：可携带完整 bash 命令、工具输入和文件路径

仅在具备相应访问控制和保留策略的目标上启用 logs 和 traces。

配置 `telemetry.forward_to` 加 `listen.public_url` 即自动开启遥测。Gateway 向每个连接的客户端推送五个环境变量。

### HTTP 调优

| 块 | Key | 默认 | 说明 |
| --- | --- | --- | --- |
| `access_control` | `allow_cidrs` / `deny_cidrs` | 空 | 入站 IP 允许/拒绝 |
| `limits` | `max_request_bytes` | 32 MiB | 最大请求体 |
| `timeouts` | `upstream_ttfb_ms` | 120000 | 上游响应头最大等待时间（首字节） |
| `rate_limits` | `device_authorization.max` / `.window_seconds` | 30 / 600 | 每 IP 设备授权端点限速 |
| `rate_limits` | `device_verify.max` / `.window_seconds` | 10 / 600 | 每 IP user_code 提交限速 |

## 客户端侧托管设置

**将开发者机器指向 gateway 需在每台设备上单独配置。** Gateway 不能自行推送这些 key，因为它们告诉客户端 gateway 在哪里。

CLI 需在各操作系统的 `managed-settings.json` 中设置：

```json
{
  "forceLoginMethod": "gateway",
  "forceLoginGatewayUrl": "https://claude-gateway.internal.example.com"
}
```

通过 MDM 平台部署。文件路径按平台：

| 平台 | 路径 |
| --- | --- |
| macOS | `/Library/Application Support/ClaudeCode/managed-settings.json` |
| Linux 和 WSL | `/etc/claude-code/managed-settings.json` |
| Windows | `C:\Program Files\ClaudeCode\managed-settings.json` |

`forceLoginGatewayUrl` 和 `forceLoginMethod` 的 `"gateway"` 值仅从管理员控制的托管层生效。开发者在自己的 `~/.claude/settings.json` 中设置无效。

## 相关

- [Claude apps gateway 总览](https://code.claude.com/docs/en/claude-apps-gateway)：快速入门和开发者连接
- [部署指南](https://code.claude.com/docs/en/claude-apps-gateway-deploy)：IdP 设置、容器镜像、Kubernetes/Cloud Run 和运维
- [Spend limits](https://code.claude.com/docs/en/claude-apps-gateway-spend-limits)：逐开发者上限和 Admin API
