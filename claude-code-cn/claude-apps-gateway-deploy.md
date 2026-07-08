---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Apps Gateway 部署
description: Claude Apps Gateway 的部署和运维指南。涵盖 IdP 注册、容器镜像构建、Kubernetes/Cloud Run 部署、日志和健康检查、密钥轮换、升级和安全模型。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/claude-apps-gateway-deploy.md
  - en-source/claude-apps-gateway-deploy.md
---

# Claude Apps Gateway 部署和运维

> 在 IdP 注册 gateway、构建容器、部署到 Kubernetes 或 Cloud Run，以及运维：健康检查、密钥轮换、升级和安全。

**本页涵盖 [Claude apps gateway](https://code.claude.com/docs/en/claude-apps-gateway) 的运维侧：** 在身份提供者注册 OAuth 客户端、将 gateway 部署为容器、以及日常运维。`gateway.yaml` 文件中的每个选项参见[配置参考](https://code.claude.com/docs/en/claude-apps-gateway-config)。

生产部署按四个步骤进行：

1. [设置身份提供者](#身份提供者设置)
2. [部署 gateway](#部署)
3. [设置运维](#运维)
4. [审查安全态势](#安全)

> **部署在私有网络。** Claude Code 仅连接地址为私有的 gateway。可信 gateway 可推送在开发者机器上运行命令的设置。放在内部负载均衡器或 VPN 后。

## 身份提供者设置

**注册一个机密 OAuth/OIDC Web 应用**，重定向 URI 为 `https://<gateway>/oauth/callback`。任何 OIDC 兼容 IdP 均可：Okta、Microsoft Entra ID、Google Workspace、Keycloak、Dex、PingFederate 等。

IdP 须满足三个要求：

- 在 `/.well-known/openid-configuration` 提供发现文档
- 支持授权码流程。PKCE 默认开启
- 在 id_token 中返回 `email`，可选 `groups`，或通过 userinfo 端点（设置 `oidc.userinfo_fallback: true`）

各服务商注意事项：

| IdP | 要点 |
| --- | --- |
| **Okta** | 组织授权服务器返回精简 id_token（省略 email 和 groups），须设置 `oidc.userinfo_fallback: true`。自定义授权服务器可直接包含 |
| **Microsoft Entra ID** | `issuer` = `https://login.microsoftonline.com/<tenant-id>/v2.0`。Entra 发出组 Object ID 而非名称，在策略中使用 GUID。或用 App Roles 获得可读名称 |
| **Google Workspace** | `issuer` = `https://accounts.google.com`。id_token 不携带组。使用 [`oidc.google_groups`](https://code.claude.com/docs/en/claude-apps-gateway-config#oidc) 通过 Admin SDK 查询。Google 忽略 `offline_access`，需设置 `extra_auth_params: { access_type: offline, prompt: consent }` |

> **刷新 token** 让 gateway 静默续期。没有刷新 token 时，开发者在每个 `ttl_hours` 周期后重新浏览器登录。如果 IdP 完全无法签发刷新 token，将 `session.ttl_hours` 提高到 `8` 或 `12`。

## 部署

**Gateway 是单个 Linux 二进制文件。** 因为副本无状态而 Postgres 是共享协调层，可水平扩展。

关键决策：

- **成本**：无单独许可证或按座位费。你支付推理（通过现有云或 Anthropic 承诺）加容器计算和遥测收集器
- **绕过**：Gateway 不强制唯一模型路由。有自有凭证的开发者仍可直接调用服务商。关闭该路径是网络策略决策
- **多 gateway**：每个 gateway 是独立部署，CLI 按主机名存储信任指纹和凭证
- **Serverless**：Cloud Run 可行（设 `min-instances: 1`）。Lambda 和 Cloud Functions 不行（gateway 是长期运行 HTTP 服务器）

### 容器镜像

围绕原生 `claude` 二进制文件构建自有镜像：

1. 从固定版本下载 Linux 构建
2. 验证 GPG 签名的 `manifest.json`
3. 复制到构建上下文

要求：

- **glibc 基础镜像**：动态依赖仅为 glibc 库
- **可写状态目录**：设置 `CLAUDE_CONFIG_DIR` 到可写路径如 `/tmp/.claude`
- **容器命令**：`claude gateway --config /etc/claude/gateway.yaml`

### Kubernetes

作为 Deployment 运行：

- 从 ConfigMap 挂载配置，从 Secret 挂载秘密
- 在 Ingress 终止 TLS，设置 `listen.public_url`
- 就绪探针 `GET /readyz`，存活探针 `GET /healthz`

> 优先使用平台工作负载身份而非静态 key：EKS 上 IRSA、GKE 上 Workload Identity、AKS 上 workload identity。

### Cloud Run

- 保持 `listen.port` 默认 `8080`
- 设置 `public_url` 为外部可达源（通常是内部 LB 主机名，因为 `*.run.app` 解析为公共地址会被 `/login` 拒绝）
- 以 secret 卷挂载配置
- 设 `min-instances: 1` 避免冷启动

完整 Google Cloud 示例参见 [Deploy on Google Cloud](https://code.claude.com/docs/en/claude-apps-gateway-on-gcp)。

### 推送 gateway URL 到开发者机器

Gateway 运行后，通过 MDM 或直接写入各操作系统的 `managed-settings.json` 推送 `forceLoginMethod` 和 `forceLoginGatewayUrl`。参见[客户端侧托管设置](https://code.claude.com/docs/en/claude-apps-gateway-config#client-side-managed-settings)。

## 运维

### 日志

Gateway 向 stderr 写两个流（均 JSON 友好）：

- **审计事件**：每安全相关事件单行 JSON。事件包括 `config.load`、`session.mint`、`session.refresh`、`auth.denied`、`access.denied`、`inference`、`spend.blocked` 等
- **运维日志**：`[gateway]` 前缀的人类可读行。`CLAUDE_GATEWAY_LOG_LEVEL` 控制详细度（`info`/`warn`/`error`）

### 健康检查

- `GET /healthz`：存活探针
- `GET /readyz`：就绪探针（验证存储可达）
- 两者豁免于 `access_control.allow_cidrs`

### 中断行为

**Postgres 宕机时**：

- 已登录会话继续工作（bearer token 本地验证）
- 新登录失败
- 消费限额强制默认 fail-open
- `/readyz` 报告 not-ready

**IdP 宕机时**：现有会话在 `ttl_hours` 内工作，新登录和刷新失败。

### JWT 密钥轮换

三步轮换保证现有会话有效：

1. 生成新密钥，前置到 `session.jwt_secret` 数组
2. 滚动部署。新 token 用新密钥签名；旧 token 仍可验证
3. `ttl_hours` 加余量后，移除旧密钥并再次滚动

**轮换也是强制会话失效的唯一方式**——bearer token 本地验证，没有逐会话撤销。

### Postgres 表

| 表 | 内容 | 保留 |
| --- | --- | --- |
| `kv` | 设备授权（10 分钟 TTL）和限速计数器 | 按行 TTL |
| `spend` | 每 principal 周期累计（美分） | `spend_retention_months`，默认 13 |
| `spend_limits` | 已配置上限 | 删除前保留 |
| `admin_audit` | Admin API 变更记录 | `audit_retention_days`，默认 365 |
| `principal_emails` | 每 principal 最近邮箱/显示名/IdP 组。含 PII | `identity_retention_days`，默认 90 |

### 升级

副本无状态，滚动重启随时安全。Gateway 启动时运行 schema 迁移。迁移仅追加，回滚到旧二进制文件安全（忽略多余的迁移行）。

**因为你在自有镜像中固定版本，新版本的修复（包括安全修复）只有更新固定版本并重部署才能到达。** 将 gateway 纳入与其他持有生产凭证的服务相同的补丁节奏。

## 安全

### 数据流

| 数据 | 路径 | Gateway 是否发送到 Anthropic |
| --- | --- | --- |
| 推理（提示、完成） | CLI -> gateway -> 你的上游 | 仅当 Anthropic API 是配置的上游 |
| 遥测 | CLI -> gateway -> 你的收集器 | 从不 |
| 身份 | IdP -> gateway -> JWT -> CLI | 从不 |
| 托管设置 | gateway YAML -> CLI | 从不 |
| 审计日志 | Gateway stderr -> 你的聚合器 | 从不 |

### 威胁模型摘要

- 开发者持有短期 JWT 而非原始上游 key。设备授权运行 PKCE
- 设备验证页面强制同源 POST 和每 IP 限速
- 出站请求通过 SSRF 防护，阻止 link-local 和云元数据地址

**超出范围**：被攻陷的 gateway 主机（等同于控制 MDM）和恶意 OIDC 提供者（可断言任意身份）。

### 合规态势

- **数据驻留**：Gateway 数据平面不向 Anthropic 发送任何内容（除非 Anthropic API 是上游）
- **主机进程流量**：设置 `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` 用于严格出口部署
- **客户端分析**：签入 gateway 时 CLI 禁用自身 Anthropic 侧使用分析
- **客户端机器**：CLI 仍发送 WebFetch 检查和版本检查，除非设置 `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` 和 `skipWebFetchPreflight: true`
- **TLS**：生产环境通过 HTTPS 提供 `public_url`

## 故障排除

| 症状 | 原因 | 修复 |
| --- | --- | --- |
| `/login` 显示标准账号选择器 | `forceLoginMethod` 或 `forceLoginGatewayUrl` 未设置 | 部署托管设置文件 |
| 显示"does not include Cloud gateway support" | Claude Code 版本过旧 | 更新 Claude Code |
| Gateway 主机解析为公共 IP | 主机名有公共地址 | 仅解析为私有地址 |
| 启动退出：OIDC 发现错误 | `oidc.issuer` 不可达 | 检查 issuer 可达性，私有 PKI 设 `ca_cert_pem` |
| Postgres 权限错误 | 应用角色缺少 `CREATE TABLE` | 预创建 schema 或临时授予 DDL |
| `/oauth/callback` 显示登录失败 | 邮箱域被拒绝或 `email_verified: false` | 检查 `allowed_email_domains` 和 IdP 邮箱声明 |
| Bedrock 请求返回 502 | EC2 IMDSv2 hop limit 为 1 阻止容器内元数据请求 | 提高 hop limit 到 2，或使用 ECS task role |
| TLS 证书错误 | 私有 CA 不在 CLI 信任存储 | 安装 CA 到 OS 信任存储或设置 `NODE_EXTRA_CA_CERTS` |

## 相关

- [Claude apps gateway 总览](https://code.claude.com/docs/en/claude-apps-gateway)：快速入门和开发者连接
- [配置参考](https://code.claude.com/docs/en/claude-apps-gateway-config)：每个 `gateway.yaml` 选项
