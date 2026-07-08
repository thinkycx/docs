---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Agent SDK - 安全部署
description: Claude Code 与 Agent SDK 部署安全指南，涵盖隔离技术（沙箱/容器/gVisor/VM）、凭证管理（代理模式）、网络控制和文件系统配置的纵深防御方案。
category: translation
tags: [claude-code, agent-sdk, translation]
refs:
  - https://code.claude.com/docs/en/agent-sdk/secure-deployment
  - en-source/agent-sdk/secure-deployment.md
---

# 安全部署 AI Agent

> Claude Code 与 Agent SDK 部署安全指南：隔离、凭证管理和网络控制。

**Claude Code 和 Agent SDK 是能够执行代码、访问文件和与外部服务交互的强大工具。** 与任何具备这些能力的工具一样，有意识地部署可以在获得收益的同时保持适当的控制。

与按预设代码路径执行的传统软件不同，这些工具根据上下文和目标动态生成其行为。这种灵活性是它们有价值的原因，但也意味着其行为可能受到处理内容的影响：文件、网页或用户输入。这有时被称为 prompt 注入。例如，如果仓库的 README 包含异常指令，Claude Code 可能以操作者未预料的方式将其纳入操作。本指南涵盖减少此风险的实用方法。

**好消息是，保护 Agent 部署不需要特殊基础设施。** 适用于运行任何半可信代码的原则同样适用：隔离、最小权限和纵深防御。Claude Code 内置了多项安全特性来应对常见问题，本指南连同额外的加固选项一起介绍。

并非所有部署都需要最高安全级别。在笔记本上运行 Claude Code 的开发者与在多租户环境中处理客户数据的公司有不同的需求。本指南呈现从 Claude Code 内置安全特性到加固生产架构的多种选项，你可以选择适合自己情况的方案。

## 威胁模型

**Agent 可能因 prompt 注入（嵌入在处理内容中的指令）或模型错误而采取意外操作。** Claude 模型设计为抵抗此类攻击；详见 [模型概览](https://platform.claude.com/docs/en/about-claude/models/overview) 和你部署模型的 system card 了解评估详情。

纵深防御仍是良好实践。例如，如果 Agent 处理了一个指示其将客户数据发送到外部服务器的恶意文件，网络控制可以完全阻断该请求。

## 内置安全特性

**Claude Code 内置了多项安全特性来应对常见问题。** 详见 [安全文档](https://code.claude.com/docs/en/security)。

| 特性 | 说明 |
|:---|:---|
| 权限系统 | 每个工具和 bash 命令可配置为允许、阻止或提示用户批准。使用 glob 模式创建规则如"允许所有 npm 命令"或"阻止任何带 sudo 的命令"。组织可设置跨所有用户适用的策略。见 [permissions](https://code.claude.com/docs/en/permissions) |
| 命令解析 | 执行 bash 命令前，Claude Code 将其解析为 AST 并与权限规则匹配。无法干净解析或不匹配允许规则的命令需要显式批准。`eval` 等少数构造无论允许规则如何都需要批准。这是权限门控而非沙箱；不推断命令是否危险 |
| 搜索结果摘要 | 搜索结果经过摘要而非将原始内容直接传入上下文，降低来自恶意网页内容的 prompt 注入风险 |
| 沙箱模式 | Bash 命令可在限制文件系统和网络访问的沙箱环境中运行。见 [沙箱文档](https://code.claude.com/docs/en/sandboxing) |

## 安全原则

**对于需要超越 Claude Code 默认的额外加固部署，以下原则指导可用选项。**

### 安全边界

**安全边界分隔不同信任级别的组件。** 对高安全部署，你可以将敏感资源（如凭证）放在包含 Agent 的边界之外。如果 Agent 环境中出现问题，边界外的资源仍受保护。

例如，与其给 Agent 直接访问 API key，不如在 Agent 环境外运行代理将 key 注入请求。Agent 可以发起 API 调用，但永远看不到凭证本身。此模式对多租户部署或处理不可信内容很有用。

### 最小权限

**可将 Agent 限制为仅其特定任务所需的能力：**

| 资源 | 限制选项 |
|:---|:---|
| 文件系统 | 仅挂载需要的目录，优先只读 |
| 网络 | 通过代理限制到特定端点 |
| 凭证 | 通过代理注入而非直接暴露 |
| 系统能力 | 在容器中丢弃 Linux capabilities |

### 纵深防御

**对高安全环境，层叠多个控制提供额外保护：**

- 容器隔离
- 网络限制
- 文件系统控制
- 代理处的请求验证

正确的组合取决于你的威胁模型和运营需求。

## 隔离技术

**不同隔离技术在安全强度、性能和运营复杂度之间有不同权衡。**

> 在所有这些配置中，Claude Code（或你的 Agent SDK 应用）运行在隔离边界内部（沙箱、容器或 VM）。下述安全控制限制 Agent 从该边界内能访问什么。

| 技术 | 隔离强度 | 性能开销 | 复杂度 |
|:---|:---|:---|:---|
| 沙箱运行时 | 良好（安全默认值） | 极低 | 低 |
| 容器（Docker） | 取决于配置 | 低 | 中 |
| gVisor | 优秀（正确配置时） | 中/高 | 中 |
| VM（Firecracker、QEMU） | 优秀（正确配置时） | 高 | 中/高 |

### 沙箱运行时

**不使用容器的轻量级隔离方案，[sandbox-runtime](https://github.com/anthropic-experimental/sandbox-runtime) 在操作系统层面强制执行文件系统和网络限制。**

主要优势是简单：无需 Docker 配置、容器镜像或网络设置。代理和文件系统限制内置。你提供一个指定允许域名和路径的配置文件。

**工作原理：**

| 方面 | 机制 |
|:---|:---|
| 文件系统 | 使用 OS 原语（Linux 上 `bubblewrap`，macOS 上 `sandbox-exec`）限制对配置路径的读写访问 |
| 网络 | 移除网络命名空间（Linux）或使用 Seatbelt profiles（macOS）通过内置代理路由流量 |
| 配置 | 基于 JSON 的域名和文件系统路径白名单 |

**安装：**

```bash
npm install @anthropic-ai/sandbox-runtime
```

然后创建配置文件指定允许的路径和域名。

**安全注意事项：**

1. **共享主机内核**：与 VM 不同，沙箱化进程共享主机内核。内核漏洞理论上可能使逃逸成为可能。某些威胁模型下这是可接受的，但如需内核级隔离，使用 gVisor 或独立 VM。

2. **无 TLS 检查**：代理基于客户端提供的主机名对域名进行白名单过滤，不终止或检查加密流量。沙箱内的代码可能使用 [域前置](https://en.wikipedia.org/wiki/Domain_fronting) 等技术访问白名单之外的主机。如果威胁模型需要更强保证，配置 [TLS 终止代理](#流量转发)。详见 [沙箱安全限制](https://code.claude.com/docs/en/sandboxing#security-limitations)。另外，如果 Agent 对允许的域名有宽松凭证，确保它不能利用该域名触发其他网络请求或泄漏数据。

对许多单开发者和 CI/CD 场景，sandbox-runtime 以最小设置显著提升了安全门槛。以下章节涵盖需要更强隔离的容器和 VM。

### 容器

**容器通过 Linux 命名空间提供隔离。** 每个容器有自己的文件系统、进程树和网络栈视图，同时共享主机内核。

安全加固的容器配置示例：

```bash
docker run \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --security-opt seccomp=/path/to/seccomp-profile.json \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=100m \
  --tmpfs /home/agent:rw,noexec,nosuid,size=500m \
  --network none \
  --memory 2g \
  --cpus 2 \
  --pids-limit 100 \
  --user 1000:1000 \
  -v /path/to/code:/workspace:ro \
  -v /var/run/proxy.sock:/var/run/proxy.sock:ro \
  agent-image
```

**各选项说明：**

| 选项 | 用途 |
|:---|:---|
| `--cap-drop ALL` | 移除可能导致权限提升的 Linux capabilities，如 `NET_ADMIN` 和 `SYS_ADMIN` |
| `--security-opt no-new-privileges` | 阻止进程通过 setuid 二进制获取权限 |
| `--security-opt seccomp=...` | 限制可用系统调用；Docker 默认阻止约 44 个，自定义 profile 可阻止更多 |
| `--read-only` | 使容器根文件系统不可变，阻止 Agent 持久化变更 |
| `--tmpfs /tmp:...` | 提供仅在内存中存在、容器停止时清除的可写临时目录 |
| `--network none` | 移除所有网络接口；Agent 通过下面挂载的 Unix socket 通信 |
| `--memory 2g` | 限制内存使用以防资源耗尽 |
| `--pids-limit 100` | 限制进程数以防 fork bomb |
| `--user 1000:1000` | 以非 root 用户运行 |
| `-v ...:/workspace:ro` | 只读挂载代码，Agent 可分析但不能修改。**避免挂载 `~/.ssh`、`~/.aws` 或 `~/.config` 等敏感主机目录** |
| `-v .../proxy.sock:...` | 挂载连接到容器外运行的代理的 Unix socket |

**Unix socket 架构：**

使用 `--network none` 时，容器没有任何网络接口。Agent 访问外界的唯一方式是通过挂载的 Unix socket，它连接到主机上运行的代理。该代理可以强制执行域白名单、注入凭证并记录所有流量。

这与 [sandbox-runtime](https://github.com/anthropic-experimental/sandbox-runtime) 使用的架构相同。即使 Agent 因 prompt 注入而被攻陷，也无法向任意服务器泄漏数据。它只能通过代理通信，代理控制哪些域名可达。更多详情见 [Claude Code 沙箱博文](https://www.anthropic.com/engineering/claude-code-sandboxing)。

**额外加固选项：**

| 选项 | 用途 |
|:---|:---|
| `--userns-remap` | 将容器 root 映射到非特权主机用户；需要 daemon 配置但限制容器逃逸损害 |
| `--ipc private` | 隔离进程间通信以防跨容器攻击 |

### gVisor

**标准容器共享主机内核：容器内代码发起系统调用时直接到达运行主机的同一内核。** 内核漏洞可能允许容器逃逸。gVisor 通过在用户空间拦截系统调用解决此问题，实现自己的兼容层处理大多数系统调用而不涉及真实内核。

如果 Agent 运行恶意代码（可能因 prompt 注入），该代码在容器内运行，可能尝试内核利用。有了 gVisor，攻击面大大缩小：恶意代码需要先利用 gVisor 的用户空间实现，且对真实内核的访问有限。

配合 Docker 使用 gVisor，安装 `runsc` 运行时并配置 daemon：

```json
// /etc/docker/daemon.json
{
  "runtimes": {
    "runsc": {
      "path": "/usr/local/bin/runsc"
    }
  }
}
```

然后运行容器：

```bash
docker run --runtime=runsc agent-image
```

**性能影响：**

| 负载类型 | 开销 |
|:---|:---|
| CPU 密集计算 | 约 0%（无系统调用拦截） |
| 简单系统调用 | 约 2x 慢 |
| 文件 I/O 密集 | 对重度 open/close 模式最高 10-200x 慢 |

对多租户环境或处理不可信内容时，额外的隔离通常值得性能开销。

### 虚拟机

**VM 通过 CPU 虚拟化扩展提供硬件级隔离。** 每个 VM 运行自己的内核，创建强边界。客户内核中的漏洞不会直接危及主机。然而 VM 并非自动比 gVisor 等替代方案"更安全"。VM 安全严重依赖 hypervisor 和设备模拟代码。

Firecracker 专为轻量级 microVM 隔离设计。可在 125ms 内启动 VM，内存开销不到 5 MiB，剥离不必要的设备模拟以减小攻击面。

此方式下，Agent VM 没有外部网络接口，通过 `vsock`（虚拟 socket）通信。所有流量通过 vsock 路由到主机上的代理，代理在转发请求前强制执行白名单并注入凭证。

### 云部署

**对云部署，可将上述任何隔离技术与云原生网络控制结合：**

1. 在无互联网网关的私有子网中运行 Agent 容器
2. 配置云防火墙规则（AWS Security Groups、GCP VPC 防火墙）阻止除到代理之外的所有出口
3. 运行代理（如带 `credential_injector` 过滤器的 [Envoy](https://www.envoyproxy.io/)）验证请求、强制执行域白名单、注入凭证并转发到外部 API
4. 为 Agent 的服务账号分配最小 IAM 权限，尽可能通过代理路由敏感访问
5. 在代理处记录所有流量用于审计

## 凭证管理

**Agent 经常需要凭证来调用 API、访问仓库或与云服务交互。** 挑战在于提供此访问而不暴露凭证本身。

### 代理模式

**推荐做法是在 Agent 安全边界之外运行代理，将凭证注入出站请求。** Agent 不带凭证发送请求，代理添加凭证并转发到目的地。

此模式的优势：

1. Agent 永远看不到实际凭证
2. 代理可强制执行允许端点的白名单
3. 代理可记录所有请求用于审计
4. 凭证存储在一个安全位置而非分发到每个 Agent

### 配置 Claude Code 使用代理

**Claude Code 支持两种通过代理路由采样请求的方法：**

**方式 1：ANTHROPIC_BASE_URL（简单但仅适用于采样 API 请求）**

```bash
export ANTHROPIC_BASE_URL="http://localhost:8080"
```

这告诉 Claude Code 和 Agent SDK 将采样请求发送到你的代理而非直接到 Claude API。代理接收明文 HTTP 请求，可检查和修改（包括注入凭证），然后转发到真实 API。

**方式 2：HTTP_PROXY / HTTPS_PROXY（系统级）**

```bash
export HTTP_PROXY="http://localhost:8080"
export HTTPS_PROXY="http://localhost:8080"
```

Claude Code 和 Agent SDK 遵循这些标准环境变量，通过代理路由所有 HTTP 流量。对 HTTPS，代理创建加密的 CONNECT 隧道：不终止 TLS 则无法查看或修改请求内容。

### 实现代理

可自建代理或使用现有方案：

| 方案 | 说明 |
|:---|:---|
| [Envoy Proxy](https://www.envoyproxy.io/) | 生产级代理，`credential_injector` 过滤器用于添加认证头 |
| [mitmproxy](https://mitmproxy.org/) | TLS 终止代理，用于检查和修改 HTTPS 流量 |
| [Squid](http://www.squid-cache.org/) | 带访问控制列表的缓存代理 |
| [LiteLLM](https://github.com/BerriAI/litellm) | LLM 网关，支持凭证注入和限流 |

### 其他服务的凭证

**除了从 Claude API 采样，Agent 经常需要对其他服务的认证访问**（git 仓库、数据库、内部 API 等）。有两种主要方式：

#### 自定义工具

通过 MCP 服务器或自定义工具提供访问，将请求路由到 Agent 安全边界之外运行的服务。Agent 调用工具，实际的认证请求在外部发生。工具调用到代理，代理注入凭证。

例如，git MCP 服务器可以接受 Agent 的命令，但将其转发到主机上运行的 git 代理，代理在联系远程仓库前添加认证。Agent 永远看不到凭证。

优势：

- **无需 TLS 拦截**：外部服务直接发起认证请求
- **凭证留在外部**：Agent 只看到工具接口而非底层凭证

#### 流量转发

对 Claude API 调用，`ANTHROPIC_BASE_URL` 让你将请求路由到可明文检查和修改的代理。但对其他 HTTPS 服务（GitHub、npm 注册表、内部 API），流量通常是端到端加密的。即使通过 `HTTP_PROXY` 路由，代理只看到不透明的 TLS 隧道，无法注入凭证。

**要修改到任意服务的 HTTPS 流量（不使用自定义工具），需要 TLS 终止代理**，解密流量、检查或修改、然后重新加密后转发。需要：

1. 在 Agent 容器外运行代理
2. 在 Agent 的信任存储中安装代理的 CA 证书（让 Agent 信任代理的证书）
3. 配置 `HTTP_PROXY`/`HTTPS_PROXY` 通过代理路由流量

此方式可处理任何基于 HTTP 的服务而无需编写自定义工具，但增加了证书管理的复杂性。

注意并非所有程序都遵循 `HTTP_PROXY`/`HTTPS_PROXY`。大多数工具（curl、pip、npm、git）遵循，但某些可能绕过这些变量直接连接。例如 Node.js `fetch()` 默认忽略这些变量；Node 24+ 中可设置 `NODE_USE_ENV_PROXY=1` 启用支持。如需全面覆盖，可用 [proxychains](https://github.com/haad/proxychains) 拦截网络调用，或配置 iptables 将出站流量重定向到透明代理。

> **透明代理** 在网络层拦截流量，客户端无需配置就能使用它。常规代理需要客户端显式连接并说 HTTP CONNECT 或 SOCKS 协议。透明代理（如 Squid 或 mitmproxy 透明模式）可处理原始重定向的 TCP 连接。

两种方式仍需 TLS 终止代理和受信 CA 证书。它们只是确保流量确实到达代理。

## 文件系统配置

**文件系统控制决定 Agent 可以读写哪些文件。**

### 只读代码挂载

Agent 需要分析但不修改代码时，只读挂载目录：

```bash
docker run -v /path/to/code:/workspace:ro agent-image
```

> **警告**：即使只读访问代码目录也可能暴露凭证。挂载前应排除或清理的常见文件：

| 文件 | 风险 |
|:---|:---|
| `.env`, `.env.local` | API key、数据库密码、密钥 |
| `~/.git-credentials` | 明文的 Git 密码/token |
| `~/.aws/credentials` | AWS 访问密钥 |
| `~/.config/gcloud/application_default_credentials.json` | Google Cloud ADC token |
| `~/.azure/` | Azure CLI 凭证 |
| `~/.docker/config.json` | Docker 注册表认证 token |
| `~/.kube/config` | Kubernetes 集群凭证 |
| `.npmrc`, `.pypirc` | 包注册表 token |
| `*-service-account.json` | GCP 服务账号密钥 |
| `*.pem`, `*.key` | 私钥 |

建议仅复制所需的源文件，或使用类似 `.dockerignore` 的过滤方式。

### 可写位置

**如果 Agent 需要写文件，根据是否需要持久化有几种选项：**

对容器中的临时工作区，使用 `tmpfs` 挂载（仅存在于内存中，容器停止时清除）：

```bash
docker run \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=100m \
  --tmpfs /workspace:rw,noexec,size=500m \
  agent-image
```

如果要在持久化前审查变更，overlay 文件系统让 Agent 写入而不修改底层文件。变更存储在单独的层中，可检查、应用或丢弃。对完全持久化的输出，挂载专用卷但与敏感目录分开。

## 延伸阅读

- [Claude Code 安全文档](https://code.claude.com/docs/en/security)
- [托管 Agent SDK](https://code.claude.com/docs/en/agent-sdk/hosting)
- [处理权限](https://code.claude.com/docs/en/agent-sdk/permissions)
- [Sandbox runtime](https://github.com/anthropic-experimental/sandbox-runtime)
- [The Lethal Trifecta for AI Agents](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [gVisor Documentation](https://gvisor.dev/docs/)
- [Firecracker Documentation](https://firecracker-microvm.github.io/)
