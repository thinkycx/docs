---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Claude Apps Gateway
description: Claude Apps Gateway 是内置于 claude 二进制文件的自托管网关服务，支持 SSO 登录、按组模型访问控制和 OTLP 遥测。本文介绍部署理由、快速入门和开发者连接。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/claude-apps-gateway.md
  - en-source/claude-apps-gateway.md
---

# Claude Apps Gateway（Amazon Bedrock、Claude Platform on AWS、Google Cloud、Microsoft Foundry）

> 通过自托管 gateway 运行 Claude Code，支持 Amazon Bedrock、Claude Platform on AWS、Google Cloud 或 Microsoft Foundry 后端，并提供 SSO 登录、按组模型访问和 OTLP 遥测。

**Claude apps gateway 面向必须或倾向于通过自有云服务商路由推理的组织**（例如满足[数据驻留](https://code.claude.com/docs/en/claude-apps-gateway-deploy#compliance-posture)要求）。如果没有此需求且需要 SCIM 配置或 Claude Code Web/移动端等功能，Claude Enterprise 可能更合适。各部署方式的完整对比参见[功能可用性](https://code.claude.com/docs/en/feature-availability)页面。

**Claude apps gateway 是一个自托管服务，位于开发者的 Claude Code 客户端和模型服务商之间。** 开发者用企业 IdP 登录而非持有 API key 或云凭证。Gateway 持有上游凭证、按 IdP 组强制模型访问和[托管设置](https://code.claude.com/docs/en/permissions#managed-settings)，并将使用遥测转发到你的可观测性栈。

它内置于 `claude` 二进制文件，运行 Claude Code 的同一可执行文件通过 `claude gateway --config gateway.yaml` 运行 gateway 服务器。

本页涵盖：

- [为何选择 Claude apps gateway](#为何选择-claude-apps-gateway)
- [快速入门](#快速入门)和[前提条件](#前提条件)
- [连接开发者](#连接开发者)
- [可用性和限制](#可用性和限制)

配套页面深入展开：[配置参考](https://code.claude.com/docs/en/claude-apps-gateway-config)涵盖 YAML 文件的每个选项，[部署指南](https://code.claude.com/docs/en/claude-apps-gateway-deploy)涵盖 IdP 设置、Kubernetes/Cloud Run 部署和运维。

## 为何选择 Claude apps gateway

[Gateway 总览](https://code.claude.com/docs/en/gateways)介绍了 gateway 的作用和使用理由。Claude apps gateway 是 Anthropic 自有 gateway，内置于 `claude` 二进制文件且与每个 Claude Code 版本一起测试，转发 Claude Code 发送的 header 和请求字段无需运维方维护单独的白名单。部署后提供：

| 能力 | 说明 |
| --- | --- |
| **凭证管理** | 上游 API key 或云凭证仅存在于你的基础设施。开发者通过企业 SSO 认证获得短期 bearer token，离职在 IdP 中处理 |
| **访问控制** | IdP 组映射到模型白名单和托管设置策略。Gateway 服务端强制模型访问，不同团队获得不同模型、工具和权限 |
| **设置下发** | Gateway 向已登录客户端自行下发托管设置，取代 claude.ai 管理控制台的[服务端托管设置](https://code.claude.com/docs/en/server-managed-settings) |
| **遥测** | 每个配置的目标接收 [OTLP 指标](https://code.claude.com/docs/en/monitoring-usage)，含 token 计数、模型、用户身份和延迟 |
| **上游路由** | 客户端向 gateway 说 Anthropic Messages API，gateway 为各上游翻译（Bedrock、Claude Platform on AWS、Google Cloud Agent Platform、Microsoft Foundry 或 Anthropic API），支持故障转移 |

> Gateway 数据平面不向 Anthropic 基础设施发送任何内容，除非 Anthropic API 是配置的上游。你控制遥测、审计日志、托管设置和开发者 IdP 身份的去向。

### 其他 gateway 实现

如果你已运行 LLM gateway 或 API gateway 满足需求，继续使用；[Other LLM gateways](https://code.claude.com/docs/en/llm-gateway) 介绍如何配置 Claude Code。

[Gateway 协议参考](https://code.claude.com/docs/en/llm-gateway-protocol)文档记录了 Claude Code 对任何 gateway 的期望：调用的端点、需转发的 header 和 body 字段、以及剥离时失效的功能。

## 快速入门

**最小路径：在 IdP 注册 OAuth 客户端、编写 `gateway.yaml`、用 Docker Compose 运行 gateway 和 Postgres、端到端验证登录。** 示例使用 Amazon Bedrock 上游；切换 `upstreams` 块即可用其他服务商。

> **部署在私有网络。** Claude Code 仅连接地址为私有的 gateway。这是安全防护——可信 gateway 可推送在开发者机器上执行命令的设置。将 gateway 放在内部负载均衡器或 VPN 后，使用解析为私有 IP 的主机名。

### 前提条件

| 需要 | 详情 |
| --- | --- |
| Claude Code v2.1.195 或更高 | `claude gateway` 子命令和 gateway 登录流程在 v2.1.195 出现。Gateway 服务器和开发者机器都需 v2.1.195+。Claude Platform on AWS 上游需 v2.1.198+ |
| OIDC 身份提供者 | Okta、Microsoft Entra ID、Google Workspace、Keycloak、Dex 或其他 OIDC 兼容 IdP。不支持 SAML 和 LDAP |
| PostgreSQL 14 或更高 | 支撑设备登录流程和限速计数器。Gateway 启动时自行迁移 schema |
| 模型上游 | Amazon Bedrock 凭证、Claude Platform on AWS 凭证、Google Cloud 凭证、Microsoft Foundry 资源或 Anthropic API key。支持多上游故障转移 |
| HTTPS | Gateway 必须通过 `https://` 从开发者笔记本和登录浏览器可达 |
| 私有网络地址 | `/login` 时 Claude Code 要求 gateway 主机名仅解析为私有地址（RFC 1918、CGNAT、IPv6 ULA 或环回） |
| Linux 运行时 | Gateway 服务器仅在原生 Linux 二进制文件上运行。macOS 可用于本地开发。不支持 Windows |

### 步骤

**步骤 1：在 IdP 注册 OAuth 客户端**

创建 OIDC Web 应用并设置重定向 URI 为 `https://claude-gateway.<your-domain>/oauth/callback`。记下 `client_id` 和 `client_secret`。

**步骤 2：配置 PostgreSQL 数据库**

任何 Postgres 14+ 均可。Gateway 启动时自动迁移 schema，数据库用户需要 `CREATE TABLE` 权限。

**步骤 3：编写 gateway.yaml**

秘密通过 `${ENV_VAR}` 展开读取。最小配置有五个部分：

```yaml
listen:
  host: 0.0.0.0
  port: 8080
  public_url: https://claude-gateway.internal.example.com

oidc:
  issuer: https://login.example.com
  client_id: 0oa1example2
  client_secret: ${OIDC_CLIENT_SECRET}
  allowed_email_domains: [example.com]
  userinfo_fallback: true

session:
  jwt_secret: ${GATEWAY_JWT_SECRET}        # openssl rand -base64 32
  ttl_hours: 1

store:
  postgres_url: ${GATEWAY_POSTGRES_URL}

upstreams:
  - provider: bedrock
    region: us-east-1
    auth: {}

auto_include_builtin_models: true
```

> Amazon Bedrock 上游需要 AWS 主体具有 `bedrock:InvokeModel` 和 `bedrock:InvokeModelWithResponseStream` 权限，并在 Bedrock 控制台启用模型访问。生产环境优先使用 IRSA/ECS task role/EC2 instance profile 而非静态 key。

**步骤 4：运行**

围绕 `claude` 二进制文件构建符合[镜像要求](https://code.claude.com/docs/en/claude-apps-gateway-deploy#container-image)的容器镜像，与 Postgres 一起运行：

```yaml
services:
  gateway:
    image: <your-registry>/claude-gateway:<version>
    ports: ["8080:8080"]
    volumes: ["./gateway.yaml:/etc/claude/gateway.yaml:ro"]
    environment:
      OIDC_CLIENT_SECRET: ${OIDC_CLIENT_SECRET}
      GATEWAY_JWT_SECRET: ${GATEWAY_JWT_SECRET}
      GATEWAY_POSTGRES_URL: postgres://gw:pw@postgres/gateway
    depends_on:
      postgres:
        condition: service_healthy
  postgres:
    image: postgres:16-alpine
    environment: { POSTGRES_USER: gw, POSTGRES_PASSWORD: pw, POSTGRES_DB: gateway }
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U gw"]
      interval: 5s
    volumes: ["pgdata:/var/lib/postgresql/data"]
volumes: { pgdata: }
```

**启动是 fail-closed 的**——配置、Postgres 连接、OIDC 发现或上游客户端构建中任何一个不可达或配置错误，gateway 退出并报错而非在降级状态下服务流量。

成功启动日志：

```text
{"ts":"...","evt":"config.load","path":"/etc/claude/gateway.yaml","sha256":"..."}
[gateway] ... info migration 1 applied
[gateway] ... info claude gateway listening on http://0.0.0.0:8080
```

**步骤 5：验证认证表面**

三项检查确认 gateway 可认证真实用户：

1. 获取发现文档：`curl -s https://claude-gateway.internal.example.com/.well-known/oauth-authorization-server | jq`
2. 请求设备授权：`curl -s -X POST https://claude-gateway.internal.example.com/oauth/device_authorization | jq`
3. 在浏览器打开 `verification_uri_complete` 完成登录

**步骤 6：让开发者登录**

在开发者机器的[托管设置文件](https://code.claude.com/docs/en/settings#settings-files)中设置 `forceLoginMethod` 为 `"gateway"` 和 `forceLoginGatewayUrl` 为 gateway 的 `public_url`，然后运行 `/login`。

## 连接开发者

**开发者用企业工作账号一次浏览器登录即可连接。** 不需要 claude.ai 账号、API key 或订阅——模型请求通过 gateway 使用组织的上游凭证。

### 设置 gateway URL

在各操作系统的[托管设置文件](https://code.claude.com/docs/en/settings#settings-files)中设置（通过 MDM 部署）：

```json
{
  "forceLoginMethod": "gateway",
  "forceLoginGatewayUrl": "https://claude-gateway.internal.example.com"
}
```

开发者按 Enter 连接。首次连接的 TLS 指纹提示仍会出现。

登录选择器中没有 gateway 选项供开发者手动选择。`forceLoginGatewayUrl` 在开发者自己的设置文件中被忽略。两个 key 都属于推送到机器的文件，而非 gateway 的 `managed.policies[].cli` 块。

### CI 管道和远程机器

**没有无人值守管道的 service-token 流程。** Gateway 登录始终运行浏览器设备流程。开发者已登录后，该机器上所有 Claude Code 调用（包括 `claude -p` 和 Agent SDK 会话）使用 gateway 会话。

设备流程将轮询 CLI 和批准浏览器分离，因此无显示器的远程开发机也能工作：开发者通过 SSH 在远程机器运行 `/login`，在笔记本浏览器打开验证链接。

### 对开发者的强制约束

| 约束 | 说明 |
| --- | --- |
| 模型访问 | 策略未授权的模型请求返回 400。`/model` 选择器被过滤到策略的 `availableModels` 白名单 |
| 遥测目标 | 配置[遥测转发](https://code.claude.com/docs/en/claude-apps-gateway-config#telemetry)时，OTLP 导出端点固定到 gateway |
| 凭证 | Gateway token 是会话唯一凭证。`ANTHROPIC_AUTH_TOKEN`、`ANTHROPIC_API_KEY`、`apiKeyHelper` 和 claude.ai 登录在已登录时被忽略 |
| 托管设置 | 锁定的 key 不能本地覆盖。CLI 在启动和每小时轮询时应用策略 |
| 启动 | Gateway 不可达时已登录会话在约 10 秒后报错退出 |
| 撤销访问 | IdP 中禁用的用户在 `ttl_hours` 内过期（下次刷新失败时） |

### 组织可见内容

使用遥测携带开发者身份、token 计数、模型和延迟到组织的收集器。**Gateway 不记录或存储提示或完成内容。** 是否收集更丰富的遥测（logs 和 traces，可能包含命令和文件路径）是组织的[逐目标选择](https://code.claude.com/docs/en/claude-apps-gateway-config#telemetry)。

## 可用性和限制

| 功能 | 状态 | 备注 |
| --- | --- | --- |
| 推理转发（Bedrock、Claude Platform on AWS、Google Cloud、Microsoft Foundry、Anthropic） | 可用 | 支持按上游模型翻译和故障转移。Claude Platform on AWS 上游需 v2.1.198+ |
| 按 IdP 组的模型访问和托管设置 | 可用 | 模型访问服务端强制；托管设置按组下发 |
| 遥测扇出（OTLP/HTTP） | 可用 | 每次导出标记身份；支持 protobuf 和 JSON 编码 |
| OIDC 身份提供者 | 可用 | 任何 OIDC 兼容 IdP |
| 用户和组级别消费限额 | 可用 | 参见 [Spend limits](https://code.claude.com/docs/en/claude-apps-gateway-spend-limits) |
| 服务端 Web 搜索 | 不可用 | CLI 无法确认上游是否支持，禁用 WebSearch |
| 标准 prompt 缓存 | 可用 | `cache_control` 断点转发到所有上游 |
| 1 小时缓存 TTL | 不可用 | Gateway 会话使用 5 分钟 TTL |
| Auto mode | 需 opt-in | 设置 `CLAUDE_CODE_ENABLE_AUTO_MODE=1` |
| 全局缓存范围等第一方优化 | 不可用 | Gateway 会话不启用 |
| OTLP/gRPC | 不支持 | 仅 OTLP over HTTP |
| SAML、LDAP 等非 OIDC 认证 | 不支持 | 仅 OIDC。需要时前置 OIDC 桥接 |
| 多租户（多 OIDC issuer） | 不支持 | 每 gateway 一个 issuer。运行独立实例 |
| Windows 服务器 | 不支持 | 部署在 Linux。macOS 仅限本地开发 |
| Helm chart | 无 | Gateway 作为标准无状态 Deployment 运行 |
| 管理 UI | 无 | 配置是 YAML 文件；重部署以更改 |

## 下一步

- 扩展 `gateway.yaml`（按组 RBAC、多上游故障转移、遥测目标）——参见[配置参考](https://code.claude.com/docs/en/claude-apps-gateway-config)
- 从 Compose 迁移到生产部署——参见[部署和运维指南](https://code.claude.com/docs/en/claude-apps-gateway-deploy)
- 设置消费限额——参见 [Spend limits](https://code.claude.com/docs/en/claude-apps-gateway-spend-limits)
- Google Cloud 完整示例——参见 [Deploy on Google Cloud](https://code.claude.com/docs/en/claude-apps-gateway-on-gcp)
