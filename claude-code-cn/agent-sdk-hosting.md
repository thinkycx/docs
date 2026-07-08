---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Agent SDK - 托管部署
description: Agent SDK 生产环境部署指南，涵盖子进程架构、会话持久化、扩容、可观测性以及 Docker/Kubernetes/沙箱提供商下的多租户隔离方案。
category: translation
tags: [claude-code, agent-sdk, translation]
refs:
  - https://code.claude.com/docs/en/agent-sdk/hosting
  - en-source/agent-sdk/hosting.md
---

# 托管 Agent SDK

> 生产环境部署 Agent SDK：子进程架构、会话持久化、扩容、可观测性和多租户隔离，适用于 Docker、Kubernetes 和沙箱提供商。

**Agent SDK 生成并管理一个 `claude` CLI 子进程，该进程拥有 shell、工作目录和磁盘上的会话文件。** 托管它不同于托管无状态 API 包装器。每个运行中的 Agent 都是一个与本地状态绑定的长生命期进程，这决定了你如何分配资源、持久化会话和跨租户扩展。

本页涵盖在你自己的基础设施上自托管：理解 [子进程模型](#子进程模型)、[选择会话模式](#选择会话模式)、[配置容器](#配置容器)，以及处理 [生产关注点](#处理生产关注点)（持久化、可观测性、认证和多租户隔离）。可部署的 Dockerfile 和 Kubernetes manifest 见 [托管 cookbook](https://github.com/anthropics/claude-cookbooks/tree/main/claude_agent_sdk/hosting)。

如果你不需要基础设施控制、自定义隔离或自有数据面，可以考虑 [Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview)：Anthropic 托管的 REST API，由 Anthropic 运行 Agent 和沙箱，你的应用只需发送事件和接收流式结果，无需操作托管基础设施。

> 关于沙箱之外的安全加固（网络控制、凭证管理和隔离选项），见 [安全部署](https://code.claude.com/docs/en/agent-sdk/secure-deployment)。

## 子进程模型

**本页所有托管决策都源于 SDK 运行 Agent 的方式。** 当你的代码调用 `query()` 时，SDK 生成一个独立的 `claude` CLI 进程并通过 stdio 通信。该子进程拥有 shell、工作目录和本地磁盘上的 JSONL 会话 transcript。

一个 Agent 会话对应一个子进程。运行 N 个并发会话意味着 N 个子进程，每个都有自己的进程树和 transcript 文件。默认情况下它们都继承你应用的工作目录，因此当会话需要独立文件系统时在每个 `query()` 调用上传入 `cwd`：

```typescript
query({ prompt, options: { cwd: "/work/session-a" } })
```

```python
query(prompt=prompt, options=ClaudeAgentOptions(cwd="/work/session-a"))
```

### 驻留在本地磁盘的状态

**三类 Agent 状态默认存在于容器文件系统上。它们都不会在容器重启、缩容或迁移到不同节点后存活。**

| 状态 | 默认位置 |
|:---|:---|
| 会话 transcript | `~/.claude/projects/`，或设置了 `CLAUDE_CONFIG_DIR` 时该目录下的 `projects/` |
| `CLAUDE.md` 记忆文件 | 用户层为 `~/.claude/CLAUDE.md`，项目层为会话工作目录 |
| 工作目录产物 | 会话的工作目录 |

要跨主机持久化 transcript，配置 [`SessionStore` 适配器](https://code.claude.com/docs/en/agent-sdk/session-storage)。记忆文件和其他工作目录产物需要自己的存储策略，如挂载卷或对象存储同步。

关于会话、恢复和分叉在 API 层面的工作方式，见 [Sessions](https://code.claude.com/docs/en/agent-sdk/sessions)。

## 选择会话模式

**以下四种模式涵盖会话生命周期：容器存活时间与其服务的会话之间的关系。** 关于容器在哪里运行，[托管 cookbook](https://github.com/anthropics/claude-cookbooks/blob/main/claude_agent_sdk/07_Hosting_the_agent.ipynb) 有针对本地 Docker、Modal 和 Kubernetes 的 [可部署代码](https://github.com/anthropics/claude-cookbooks/tree/main/claude_agent_sdk/hosting)。在此选择会话模式，从 cookbook 选择部署目标。

### 临时会话（Ephemeral）

**为每个用户任务创建容器，任务完成后销毁。** 适合一次性任务。用户在任务进行中仍可与 AI 交互，但完成后容器即销毁。

示例负载：bug 调查与修复、发票/收据提取、文档翻译、媒体转换。

容器运行一个调用 SDK 后退出的一次性入口。以下是最小化的 TypeScript 版本：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

const prompt = process.env.TASK_PROMPT!;
for await (const message of query({ prompt, options: { maxTurns: 20 } })) {
  console.log(message);
}
```

### 长期会话（Long-running）

**运行持久容器实例，通常每容器托管多个 SDK 进程，服务持续工作。** 适合执行自主操作、提供内容或处理高流量消息流的 Agent。

示例负载：分诊和回复来信的邮件 Agent、通过容器端口为用户托管可编辑站点的建站器、处理来自 Slack 等平台持续流量的聊天机器人。

容器暴露 HTTP 或 WebSocket 端点，将每个活跃会话映射到长生命期的 query 及其背后的子进程。TypeScript 中用 [`streamInput()`](https://code.claude.com/docs/en/agent-sdk/typescript#query-object) 向活跃会话添加 turn，用 [`startup()`](https://code.claude.com/docs/en/agent-sdk/typescript#startup) 在流量到来前预热子进程。Python 中用 [`ClaudeSDKClient`](https://code.claude.com/docs/en/agent-sdk/python#claudesdkclient) 跨 turn 保持会话打开。调整容器大小以容纳最大并发会话数。

### 混合会话（Hybrid）

**临时容器在启动时从 [`SessionStore`](https://code.claude.com/docs/en/agent-sdk/session-storage) 恢复水合，并将更新持久化回去。** 适合跨多次交互但在两次交互之间空闲的会话。容器在空闲时缩减，用户返回时重新启动。

示例负载：间歇性签到的个人项目经理、跨数小时暂停和恢复的深度研究、跨交互加载工单历史的客服 Agent。

调整提供商的空闲超时，匹配你预期用户返回的频率。未配置 `SessionStore` 时缩减容器会丢失 transcript，因此对此模式来说 store 是必需的而非可选的。

此模式的关键在于通过 ID 恢复会话并挂载共享 store：

```typescript
import { query, type SessionStore } from "@anthropic-ai/claude-agent-sdk";

declare const userInput: string;
declare const sessionId: string;          // 从你的数据库按用户查找
declare const sessionStore: SessionStore; // S3、Redis、Postgres 或你自己的适配器

for await (const message of query({
  prompt: userInput,
  options: { resume: sessionId, sessionStore },
})) {
  // ...
}
```

```python
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt=user_input,
    options=ClaudeAgentOptions(
        resume=session_id,            # 从你的数据库按用户查找
        session_store=session_store,  # S3、Redis、Postgres 或你自己的适配器
    ),
):
    ...
```

完整 `SessionStore` 接口和参考适配器见 [Session storage](https://code.claude.com/docs/en/agent-sdk/session-storage)。

### 多代理容器（Multi-agent）

**在一个容器内运行多个 SDK 子进程。** 适合必须紧密协作的代理，例如代理在共享环境中相互交互的多代理模拟。

给每个代理独立的工作目录以避免互相覆盖文件，隔离设置加载以防单个代理的 `CLAUDE.md` 文件泄漏到其他代理。具体选项见 [多租户隔离](#多租户隔离)。

## 配置容器

### 基于容器的沙箱

**在沙箱容器内运行 SDK 以获得进程隔离、资源限制、网络控制和临时文件系统。** 多个提供商专门提供适合 Agent SDK 模型的沙箱容器环境。

选择提供商时需要回答的问题：

| 维度 | 考虑因素 |
|:---|:---|
| 谁运行沙箱 | 沙箱即服务提供商为你运营基础设施；自托管选项让你在自己的基础设施上运行软件 |
| 冷启动延迟 | 从"创建沙箱"到"准备接受首个请求"的时间。临时模式需要亚秒启动，长期模式可容忍更多 |
| 持久存储 | 提供商是否提供持久卷还是仅临时磁盘。混合模式需要持久存储，无论在沙箱内还是旁边 |
| 定价模式 | 按秒、按请求或固定每小时计费。按秒适合突发临时负载，按小时适合长期会话 |
| 网络 | 支持自定义出口规则、出站代理和私有 VPC 对等，适用于受监管环境 |

**可评估的提供商：**

- [Modal Sandbox](https://modal.com/docs/guide/sandbox)（附 [演示实现](https://modal.com/docs/examples/claude-slack-gif-creator)）
- [Cloudflare Sandboxes](https://github.com/cloudflare/sandbox-sdk)
- [Daytona](https://www.daytona.io/)
- [E2B](https://e2b.dev/)
- [Fly Machines](https://fly.io/docs/machines/)
- [Vercel Sandbox](https://vercel.com/docs/functions/sandbox)

自托管选项如 Docker、gVisor 和 Firecracker，以及详细的隔离配置，见 [隔离技术](https://code.claude.com/docs/en/agent-sdk/secure-deployment#isolation-technologies)。

### 运行时依赖

**容器只需要你 SDK 的语言运行时：**

- Python SDK 需要 Python 3.10+，TypeScript SDK 需要 Node.js 18+
- 两个 SDK 包都内置了目标平台的原生 Claude Code 二进制文件，因此子进程无需单独安装 Claude Code 或 Node.js

内置二进制文件锁定到 SDK 包版本，因此更新 SDK 就是更新 CLI。SDK 遵循 semver：持续采用 patch 版本，在采用 minor 版本前审查 [TypeScript](https://github.com/anthropics/claude-agent-sdk-typescript/blob/main/CHANGELOG.md) 或 [Python](https://github.com/anthropics/claude-agent-sdk-python/blob/main/CHANGELOG.md) changelog。

### 资源

**1 GiB 内存、5 GiB 磁盘和 1 CPU 每代理是新启动实例的合理起点。** 内存使用随会话长度和工具活动增长，因此根据你实际需要的会话长度和并发数来规划，而非空闲基线。扩容计算见 [扩容与并发](#扩容与并发)。

### 网络

**SDK 需要到 `api.anthropic.com` 的出站 HTTPS 访问**，或在 Amazon Bedrock 或 Google Cloud Agent Platform 上运行时需要到提供商区域端点的访问。如果 Agent 使用 [MCP 服务器](https://code.claude.com/docs/en/agent-sdk/mcp) 或外部工具，还需要到这些端点的出站访问。生产环境中，通过出口代理路由出站流量，强制执行域名白名单、注入凭证并记录请求。详见 [安全部署](https://code.claude.com/docs/en/agent-sdk/secure-deployment)。

对于入站流量，在容器上暴露 HTTP 或 WebSocket 端口。你的应用在该端口处理客户端请求并在内部调用 SDK；子进程本身不监听网络。

## 处理生产关注点

**在发布自托管 Agent 之前需要处理以下决策。**

### 会话与状态持久化

**默认本地磁盘在重启、缩容或迁移到不同节点后丢失。** 对于用户期望恢复的任何会话，通过 [`SessionStore` 适配器](https://code.claude.com/docs/en/agent-sdk/session-storage) 将 transcript 镜像到持久存储。S3、Redis 和 Postgres 适配器及一致性套件见 [参考实现](https://code.claude.com/docs/en/agent-sdk/session-storage#reference-implementations)。

**`SessionStore` 行为的三个要点：**

| 要点 | 说明 |
|:---|:---|
| 仅 transcript | `SessionStore` 镜像 transcript，不包括 `CLAUDE.md` 记忆文件或其他工作目录产物。挂载共享卷或单独同步它们 |
| 镜像而非替代 | 子进程先写入本地磁盘，store 接收每批的副本。本地写入保持权威性 |
| `mirror_error` 消息 | store 拒绝的批次最多重发三次，每次重试前短暂退避；超时调用不重试。如果仍失败，SDK 丢弃该批次，发出 `{ type: "system", subtype: "mirror_error" }` 消息并继续 query。如果 store 持久性重要，对此告警 |

### 可观测性

**Agent SDK 是长生命期进程，跨多次 API 往返生成工具调用。** 没有遥测你无法看到哪些工具运行了、每个花了多长时间、或会话在哪里卡住了。

SDK 从环境继承 OpenTelemetry 配置。在容器或编排器层设置 OTEL 环境变量，每次 `query()` 调用都会导出 span、metrics 和 log 事件到你的 collector。以下示例为三个信号启用 OTLP 导出。`CLAUDE_CODE_ENHANCED_TELEMETRY_BETA` 仅 trace 需要；如果只导出 metrics 和 logs 可省略。

```bash
CLAUDE_CODE_ENABLE_TELEMETRY=1
CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1
OTEL_TRACES_EXPORTER=otlp
OTEL_METRICS_EXPORTER=otlp
OTEL_LOGS_EXPORTER=otlp
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_EXPORTER_OTLP_ENDPOINT=http://collector.example.com:4318
```

Prompt 文本和工具输入默认不包含在导出中。详见 [控制导出中的敏感数据](https://code.claude.com/docs/en/agent-sdk/observability#control-sensitive-data-in-exports) 和 [可观测性](https://code.claude.com/docs/en/agent-sdk/observability) 完整信号目录。

### 认证与密钥

**托管时有三个认证关注点：**

| 关注点 | 方案 |
|:---|:---|
| Anthropic API | 子进程从环境读取 `ANTHROPIC_API_KEY`。从密钥管理器提供，或设置 `ANTHROPIC_BASE_URL` 通过代理路由模型调用，由代理在容器外注入密钥。详见 [凭证管理](https://code.claude.com/docs/en/agent-sdk/secure-deployment#credential-management) 和 [SDK 概览](https://code.claude.com/docs/en/agent-sdk/overview#get-started) |
| 入站认证 | 在 Agent 容器前的网关处放置认证。Agent 应接收预认证的请求，不应成为验证用户 token 的组件 |
| 出站工具 | 将工具凭证置于 Agent 环境之外。通过代理路由出站调用，代理在请求离开容器后注入 API key。Agent 发出调用，代理添加凭证 |

### 扩容与并发

**每个会话在自己的子进程中运行，因此主机上的并发受限于 RAM 能容纳多少子进程。**

每主机容量计算公式：

```text
每主机代理数 = (主机 RAM - 开销) / (每会话 RAM 上限)
```

通过运行代表性会话到目标长度、在预期工具负载下记录峰值 RSS 来测量每会话上限。[资源](#资源) 中的 1 GiB 起点是下限而非上限。

**水平扩展路由取决于你的模式。** 对于长期会话（容器承载多个会话），在负载均衡器后运行容器池，通过 `sessionId` 的一致性哈希将会话固定到某容器。固定的会话持续命中同一容器（同一运行中的子进程），直到被驱逐或容器重启。

单个会话的大规模并发 [子代理](https://code.claude.com/docs/en/agent-sdk/subagents) 扇出可能触发 API 限流。将工作分成较小批次而非一次大范围调度。

### 成本

**Anthropic token 成本通常比容器基础设施成本高一个数量级或更多。** 最低配置容器约每小时 $0.05，而单个长 Agent 会话可花费数美元的 token。详见 [成本追踪](https://code.claude.com/docs/en/agent-sdk/cost-tracking)。

### 多租户隔离

**默认 SDK 行为从文件系统读取设置和 `CLAUDE.md` 记忆文件。** 在服务多租户的共享容器中，这些文件可能将一个租户的上下文泄漏到另一个租户的会话中。

**在共享容器内隔离租户的方法：**

| 措施 | 说明 |
|:---|:---|
| `settingSources: []` | TypeScript 传入 `settingSources: []`，Python 传入 `setting_sources=[]`，不加载任何文件系统设置 |
| 禁用自动记忆 | 在 `env` 中设置 `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`。[自动记忆](https://code.claude.com/docs/en/memory#auto-memory) 在 `~/.claude/projects/<project>/memory/` 下无论 `settingSources` 如何都会加载到系统 prompt。详见 [settingSources 不控制的内容](https://code.claude.com/docs/en/agent-sdk/claude-code-features#what-settingsources-does-not-control) |
| 独立配置目录 | 将 `CLAUDE_CONFIG_DIR` 指向每租户目录，租户不共享 `~/.claude.json` 全局配置 |
| 独立工作目录 | 在每次 `query()` 调用上显式传入 `cwd` |
| 租户级出口规则 | 在代理处应用每租户出口规则（不同出站 IP、凭证或域白名单），防止受损租户通过其他租户的出站策略泄漏数据 |

以下示例同时应用四个 SDK 级选项。构造 `tenantDir` 和 `configDir` 使每个租户获得其他租户无法读取的路径。TypeScript 中 `env` 替换子进程环境，因此展开 `...process.env` 以保留 `PATH` 和 `ANTHROPIC_API_KEY` 等继承变量。Python 中 `env` 合并到继承环境之上。

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

declare const prompt: string;
declare const tenantDir: string;
declare const configDir: string;

for await (const message of query({
  prompt,
  options: {
    cwd: tenantDir,
    settingSources: [],
    env: {
      ...process.env,
      CLAUDE_CONFIG_DIR: configDir,
      CLAUDE_CODE_DISABLE_AUTO_MEMORY: "1",
    },
  },
})) {
  // ...
}
```

```python
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt=prompt,
    options=ClaudeAgentOptions(
        cwd=tenant_dir,
        setting_sources=[],
        env={
            "CLAUDE_CONFIG_DIR": config_dir,
            "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1",
        },
    ),
):
    ...
```

租户级网络控制详见 [安全部署](https://code.claude.com/docs/en/agent-sdk/secure-deployment)。

## 已知限制

**在部署设计中规划以下限制：**

| 限制 | 应对措施 |
|:---|:---|
| 无顶层会话超时 | 会话不会自行超时。在 `Options` 中设置 `maxTurns` 限制 Agent 在停止前进行的工具调用往返数 |
| 长会话的内存增长 | 限制会话长度或定期回收子进程。见 [扩容与并发](#扩容与并发) |
| 大规模并行子代理扇出可能触发限流 | 将工作分成较小批次而非一次大范围调度 |
| 无子代理墙钟时间截止 | 通过 `AgentDefinition` 中的 `maxTurns` 限制每个 [子代理](https://code.claude.com/docs/en/agent-sdk/subagents)。仅后台子代理支持 `CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS` 停滞看门狗，在 `run_in_background` 子代理停止产出时触发；这不是总运行时间截止 |

## 后续步骤

- [托管 cookbook](https://github.com/anthropics/claude-cookbooks/blob/main/claude_agent_sdk/07_Hosting_the_agent.ipynb)：notebook 演练，附 Docker、Modal 和 Kubernetes 的 [可部署代码](https://github.com/anthropics/claude-cookbooks/tree/main/claude_agent_sdk/hosting)
- [Session storage](https://code.claude.com/docs/en/agent-sdk/session-storage)：通过 `SessionStore` 适配器跨主机持久化 transcript
- [可观测性](https://code.claude.com/docs/en/agent-sdk/observability)：导出 OTEL trace、metrics 和 logs 到你的 collector
- [安全部署](https://code.claude.com/docs/en/agent-sdk/secure-deployment)：网络控制、凭证管理和隔离加固
- [成本追踪](https://code.claude.com/docs/en/agent-sdk/cost-tracking)：每会话 token 和成本核算
