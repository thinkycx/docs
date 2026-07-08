---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Apps Gateway GCP
description: 在 Google Cloud 上部署 Claude Apps Gateway 的完整示例：Cloud Run 或 GKE、Cloud SQL for PostgreSQL、Secret Manager、以及 Google Cloud Agent Platform 服务账号认证。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/claude-apps-gateway-on-gcp.md
  - en-source/claude-apps-gateway-on-gcp.md
---

# 在 Google Cloud 上部署 Claude Apps Gateway

> 在 Google Cloud 上运行 Claude apps gateway 的完整示例：Cloud Run 或 GKE、Cloud SQL for PostgreSQL、Secret Manager、以及连接 Google Cloud Agent Platform 的服务账号认证。

**本页展示一种在 Google Cloud 上运行 Claude apps gateway 的方式。** 配置是客户自管基础设施的可工作示例而非受支持的生产部署——用它了解各部分如何组合，然后根据自身环境调整。平台无关的要求参见[部署指南](https://code.claude.com/docs/en/claude-apps-gateway-deploy)。

本示例使用 Google Cloud Agent Platform 作为模型上游，Cloud Run 或 GKE 作为计算。Google Workspace 是示例 IdP，但任何 OIDC 兼容 IdP 均可。

## 构建内容

参考配置包含：

| 组件 | 说明 |
| --- | --- |
| **Cloud Run** 服务或 **GKE** Deployment | 运行 gateway 容器 |
| **Artifact Registry** 仓库 | 存储 gateway 镜像 |
| **Cloud SQL for PostgreSQL** | 仅私有 IP，作为 gateway 的存储 |
| **Secret Manager** | 存储 `gateway.yaml`、JWT 签名密钥、OIDC 客户端密钥和 Postgres URL |
| **服务账号** | 具有 `roles/aiplatform.user`，直接附加在 Cloud Run 或通过 Workload Identity 绑定在 GKE |
| **内部应用负载均衡器** | Cloud Run 上的内部 ALB，或 GKE 上 `gce-internal` 类的内部 Ingress |

## 前提条件

- 启用计费的 GCP 项目，具有创建上述资源的权限
- `gcloud` CLI 已认证，Docker 已安装
- GKE 路径需要：`kubectl` 和在同一 VPC 的 GKE 集群
- Model Garden 中需要的 Claude 模型的访问权限
- Google Workspace OAuth 2.0 Web 应用客户端
- Gateway 的 TLS 主机名

设置项目和区域：

```bash
export PROJECT_ID=<your-project>
export REGION=us-east5
gcloud config set project "$PROJECT_ID"
```

## 部署 gateway

### 步骤 1：启用 API

```bash
gcloud services enable \
  aiplatform.googleapis.com \
  artifactregistry.googleapis.com \
  sqladmin.googleapis.com \
  secretmanager.googleapis.com \
  iamcredentials.googleapis.com \
  iam.googleapis.com \
  compute.googleapis.com \
  servicenetworking.googleapis.com \
  run.googleapis.com \
  container.googleapis.com
```

### 步骤 2：创建服务账号并授予 IAM

```bash
gcloud iam service-accounts create claude-gateway --display-name="Claude apps gateway"
SA="claude-gateway@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${SA}" --role="roles/aiplatform.user" --condition=None
```

然后在 Model Garden 启用项目的 Claude 模型。

### 步骤 3：构建并推送镜像

按[容器镜像要求](https://code.claude.com/docs/en/claude-apps-gateway-deploy#container-image)使用 `linux-x64` glibc 二进制文件构建：

```bash
gcloud artifacts repositories create claude-gateway \
  --repository-format=docker --location="$REGION"
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

docker build --platform=linux/amd64 --provenance=false \
  -t "${REGION}-docker.pkg.dev/${PROJECT_ID}/claude-gateway/gateway:<version>" .
docker push "${REGION}-docker.pkg.dev/${PROJECT_ID}/claude-gateway/gateway:<version>"
```

### 步骤 4：配置 Cloud SQL for PostgreSQL

通过 Private Services Access 创建仅私有 IP 的实例：

```bash
VPC=cc-gateway-vpc
gcloud compute networks create "$VPC" --subnet-mode=custom
gcloud compute networks subnets create cc-gateway-subnet \
  --network="$VPC" --region="$REGION" --range=10.0.0.0/24

gcloud compute addresses create "google-managed-services-${VPC}" \
  --global --purpose=VPC_PEERING --prefix-length=16 --network="$VPC"
gcloud services vpc-peerings connect \
  --service=servicenetworking.googleapis.com \
  --ranges="google-managed-services-${VPC}" --network="$VPC"

gcloud sql instances create claude-gateway-db \
  --database-version=POSTGRES_16 --tier=db-g1-small --region="$REGION" \
  --network="projects/${PROJECT_ID}/global/networks/${VPC}" --no-assign-ip
gcloud sql databases create claude_gateway --instance=claude-gateway-db
PGPASS="$(openssl rand -hex 24)"
gcloud sql users create gateway --instance=claude-gateway-db --password="$PGPASS"
```

### 步骤 5：编写 gateway.yaml

`upstreams` 块指向 Google Cloud Agent Platform，`auth: {}` 通过运行时服务账号的 Application Default Credentials 认证。

**`trusted_proxies` 设置参考：**

| 前端 | `trusted_proxies` |
| --- | --- |
| 直接访问 Cloud Run（无 LB） | `[169.254.0.0/16]` |
| Cloud Run 前内部 ALB | `169.254.0.0/16` 加代理专用子网 CIDR |
| GKE 内部 Ingress（`gce-internal`） | 代理专用子网 CIDR |

```yaml
listen:
  host: 0.0.0.0
  port: 8080
  public_url: https://claude-gateway.internal.example.com
  trusted_proxies: [169.254.0.0/16, <your-proxy-only-subnet-cidr>]

oidc:
  issuer: https://accounts.google.com
  client_id: <your-oauth-client-id>
  client_secret: ${OIDC_CLIENT_SECRET}
  allowed_email_domains: [example.com]
  scopes: [openid, profile, email]
  extra_auth_params: { access_type: offline, prompt: consent }

session:
  jwt_secret: ${GATEWAY_JWT_SECRET}

store:
  postgres_url: ${GATEWAY_POSTGRES_URL}

upstreams:
  - provider: vertex
    region: <your-region>
    project_id: <your-project>
    auth: {}
```

> Google id_token 不携带 `groups` 声明。要在 [`managed.policies`](https://code.claude.com/docs/en/claude-apps-gateway-config#managed) 中使用基于组的策略，需配置 [`oidc.google_groups`](https://code.claude.com/docs/en/claude-apps-gateway-config#oidc)。

### 步骤 6：存储秘密

创建四个 Secret Manager 秘密并授予服务账号 `roles/secretmanager.secretAccessor`：

| 秘密 | 来源 |
| --- | --- |
| `gateway-jwt-secret` | `openssl rand -base64 32` |
| `gateway-oidc-client-secret` | Google Cloud Console OAuth 客户端 |
| `gateway-postgres-url` | Cloud SQL 步骤的 `$GATEWAY_POSTGRES_URL` |
| `gateway-config` | 上一步的完整 `gateway.yaml` |

秘密到达容器的方式因路径而异：
- Cloud Run：`gateway.yaml` 作为文件挂载，其余三个注入为环境变量
- GKE：通过 Secret Manager CSI 驱动挂载为文件

### 步骤 7：部署

**Cloud Run 路径：**

```bash
gcloud run deploy claude-gateway \
  --image="${REGION}-docker.pkg.dev/${PROJECT_ID}/claude-gateway/gateway:<version>" \
  --region="$REGION" \
  --service-account="claude-gateway@${PROJECT_ID}.iam.gserviceaccount.com" \
  --min-instances=1 \
  --timeout=3600 \
  --ingress=internal-and-cloud-load-balancing \
  --network="$VPC" --subnet=cc-gateway-subnet --vpc-egress=private-ranges-only \
  --set-secrets=/etc/claude/gateway.yaml=gateway-config:latest,GATEWAY_JWT_SECRET=gateway-jwt-secret:latest,OIDC_CLIENT_SECRET=gateway-oidc-client-secret:latest,GATEWAY_POSTGRES_URL=gateway-postgres-url:latest \
  --no-invoker-iam-check
```

Direct VPC egress 让服务直接到达 Cloud SQL 私有 IP。公网出口到 Google Cloud Agent Platform 和 `accounts.google.com` 直接走互联网。

**Cloud Run invoker IAM 检查必须开放或禁用。** Gateway 运行自己的 OIDC，客户端不携带 GCP token：

- `--no-invoker-iam-check`：禁用检查（推荐）
- `--allow-unauthenticated`：授予 `allUsers` `run.invoker` 角色

**GKE 路径：**

在 `$VPC` 上的集群启用 Workload Identity，绑定 Google 服务账号到 Kubernetes 服务账号：

```bash
gcloud container clusters update <cluster> --region="$REGION" \
  --workload-pool="${PROJECT_ID}.svc.id.goog"

kubectl create namespace claude-gateway
kubectl create serviceaccount gateway -n claude-gateway

gcloud iam service-accounts add-iam-policy-binding \
  "claude-gateway@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:${PROJECT_ID}.svc.id.goog[claude-gateway/gateway]"

kubectl annotate serviceaccount gateway -n claude-gateway \
  iam.gke.io/gcp-service-account="claude-gateway@${PROJECT_ID}.iam.gserviceaccount.com"
```

部署为标准 Deployment + Service + 内部 Ingress（class `gce-internal`）。附加 BackendConfig 提高 `timeoutSec` 防止长流式响应被截断。

### 步骤 8：推送 gateway URL 到开发者机器

在[托管设置文件](https://code.claude.com/docs/en/claude-apps-gateway#set-the-gateway-url)中设置 `forceLoginMethod` 和 `forceLoginGatewayUrl`。

## Terraform 参考

[参考部署资源](https://github.com/anthropics/claude-code/tree/main/examples/gateway/gcp)自动化 Cloud Run 路径：

- `setup.sh`：幂等 `gcloud` 配置器
- `terraform/`：同一部署的基础设施即代码
- `gateway.yaml.example` 和 distroless 运行时镜像的 `Dockerfile`

资源默认 Cloud Run ingress 为 `internal`，无需负载均衡器。

## 故障排除

| 症状 | 原因 | 修复 |
| --- | --- | --- |
| Cloud Run 容器未到达前返回 `403 Forbidden` | Invoker IAM 检查仍启用 | 用 `--no-invoker-iam-check` 或 `--allow-unauthenticated` |
| `--no-invoker-iam-check` 被拒绝 | 被 `constraints/run.managed.requireInvokerIam` 阻止 | 用 `--allow-unauthenticated`，或用 GKE 路径 |
| 容器 manifest 类型错误 | 非 amd64 构建或 buildx 发出 OCI image index | 用 `--platform=linux/amd64 --provenance=false` |
| Postgres 连接超时 | 服务未附加到 VPC | 用 `--network` 和 `--subnet` 部署 |
| Agent Platform 返回 `403 PERMISSION_DENIED` | 运行时未使用正确服务账号，或模型未在 Model Garden 启用 | 设置 `--service-account`，在 Model Garden 启用模型 |
| 流式响应被截断 | 前端请求超时（GKE Ingress 默认 30s，Cloud Run 默认 300s） | GKE 附加 BackendConfig 提高 `timeoutSec`；Cloud Run 用 `--timeout=3600` |

## 下一步

- [配置参考](https://code.claude.com/docs/en/claude-apps-gateway-config)：每个 `gateway.yaml` 选项
- [部署和运维](https://code.claude.com/docs/en/claude-apps-gateway-deploy)：IdP 设置、健康检查、JWT 密钥轮换、升级和安全模型
- [Claude apps gateway 总览](https://code.claude.com/docs/en/claude-apps-gateway)：快速入门和连接开发者
