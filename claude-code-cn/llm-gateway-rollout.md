---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Gateway 推广
description: 管理员为组织部署 LLM 网关的完整流程：确认路由、签发凭证、测试 Claude Code、分发托管设置、验证推广效果。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/llm-gateway-rollout.md
  - en-source/llm-gateway-rollout.md
---

# 为组织推广 LLM 网关

> 部署网关产品用于 Claude Code：配置转发、签发开发者凭证、通过托管设置分发配置、验证推广效果。

**本页引导管理员完成 LLM 网关的组织级推广。** 假设你已部署了满足[网关要求](#网关要求)的网关产品。具体产品的部署和运维不在此覆盖范围。

> - 开发者连接现有网关：[连接 Claude Code 到 LLM 网关](https://code.claude.com/docs/en/llm-gateway-connect)
> - Claude Code 向网关发送的内容：[网关协议参考](https://code.claude.com/docs/en/llm-gateway-protocol)

## 前提条件

完成推广需要：

- 已部署在基础设施上的网关，通过 HTTPS 监听你将分发给开发者的确切地址（非重定向地址），且已配置 Claude 模型名称路由
- 网关用于转发的提供商凭证
- 将设置文件分发到开发者机器的方式（MDM 或配置管理）

### 网关要求

**网关产品必须满足以下条件：**

| 要求 | 说明 |
| :--- | :--- |
| 接受支持的 API 格式 | [API 格式表](https://code.claude.com/docs/en/llm-gateway-protocol#api-formats)中的格式之一 |
| 流式传输响应 | SSE 逐步传递而非缓冲完整响应 |
| 路由 Claude 模型名称 | 映射开发者使用的模型名到上游模型 |
| 原样转发请求头和 Body | 透传 `anthropic-beta`、`anthropic-version` 和请求体 |
| 原样返回上游错误 | Claude Code 的自动恢复依赖错误措辞匹配 |
| 豁免 WAF 请求体检查 | Claude Code 的 prompt 包含源码和 XML 标签，会触发 XSS 规则 |

可选：提供 `GET /v1/models` 以支持[模型发现](https://code.claude.com/docs/en/llm-gateway-protocol#model-discovery)。

## 推广步骤

**推广分五步，每步有检查点：**

1. [确认网关路由模型](#确认网关路由模型)
2. [签发开发者凭证](#签发开发者凭证)
3. [针对网关测试 Claude Code](#针对网关测试-claude-code)
4. [分发配置](#分发配置)
5. [从开发者机器验证](#验证推广效果)

涉及三种凭证：

| 凭证 | 持有者 | 检查点中的占位符 |
| :--- | :--- | :--- |
| 提供商凭证 | 网关（转发给上游） | 配置在网关上；不出现在客户端命令中 |
| 网关管理凭证 | 你（网关的管理/测试接口） | `<gateway-key>` |
| 开发者密钥 | 每位开发者 | `<developer-key>` |

### 确认网关路由模型

**用最小请求测试端到端路径：**

```bash
curl -X POST "https://llm-gateway.example.com/v1/messages" \
  -H "Authorization: Bearer <gateway-key>" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model": "claude-sonnet-4-6", "max_tokens": 1, "messages": [{"role": "user", "content": "."}]}'
```

**检查点**：`200` + `content` 字段表示网关到达了提供商。`404` 表示模型名未路由；来自提供商的 `401` 表示网关的提供商凭证有误。

对网关路由配置中的每个 Claude 模型名重复测试。

> 避免在重定向后面提供网关。重定向可能丢弃请求体或剥离凭证头，且模型发现将任何重定向视为失败。

### 签发开发者凭证

**每位开发者需要自己的网关密钥。** 在网关创建每人一个凭证，并确认新签发的密钥有效：

```bash
curl -X POST "https://llm-gateway.example.com/v1/messages" \
  -H "Authorization: Bearer <developer-key>" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model": "claude-sonnet-4-6", "max_tokens": 1, "messages": [{"role": "user", "content": "."}]}'
```

**检查点**：`200` + `content` 字段表示开发者密钥到达网关且网关成功转发。

每人一个密钥（而非共享密钥）才能实现按人归属用量和独立吊销。

### 针对网关测试 Claude Code

**在分发前，自己先以开发者身份通过网关运行 Claude Code：**

```bash
export ANTHROPIC_BASE_URL=https://llm-gateway.example.com
export ANTHROPIC_AUTH_TOKEN="<developer-key>"
```

然后发送单次提示：

```bash
claude -p "Reply with one word: connected"
```

**检查点**：收到回复，且网关日志中显示 `POST /v1/messages` 状态 200。

排查提示：
- `Not logged in`：检查网关日志区分原因——日志为空说明凭证未到达会话；日志显示 `x-api-key` 被拒说明应切换到 `ANTHROPIC_API_KEY`
- `Failed to authenticate. API Error: 401`：凭证被发送但被拒绝，网关日志显示方向
- 命令卡住无输出：检查网关日志而非等待——无到达请求说明 Base URL 不对

### 分发配置

**每台开发者机器需要网关地址和凭证。** 通过[托管设置](https://code.claude.com/docs/en/settings#settings-files)集中分发，或交给开发者自行设置。

#### 需分发的变量

| 变量/设置 | 作用 | 何时包含 |
| :--- | :--- | :--- |
| `ANTHROPIC_BASE_URL` | 将请求路由到网关 | 始终 |
| `apiKeyHelper` 或 `ANTHROPIC_AUTH_TOKEN`/`ANTHROPIC_API_KEY` | 认证请求 | 始终（三选一） |
| `ANTHROPIC_CUSTOM_HEADERS` | 添加额外 HTTP 头 | 网关需要租户/路由头 |
| `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY` | 启动时查询网关模型列表 | 网关提供 `/v1/models` |
| `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` | 阻止发送预发布能力 | 网关转发到不支持 beta 字段的上游 |
| `ANTHROPIC_MODEL` 等 | 设置模型名 | 网关路由非默认模型名 |
| 提供商特定 Base URL 变量 | 云服务商格式路由 | 网关前置于特定云服务商 |

#### 通过托管设置分发

通过 MDM、注册表策略或配置管理推送[托管设置文件](https://code.claude.com/docs/en/settings#settings-files)的 `env` 块：

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://llm-gateway.example.com"
  },
  "apiKeyHelper": "/usr/local/bin/get-gateway-key"
}
```

托管的 `ANTHROPIC_BASE_URL` 是强制的，开发者的 Shell 导出无法覆盖。

**不要在托管设置中同时包含 `forceLoginMethod`/`forceLoginOrgUUID` 和网关凭证。** 自 v2.1.146 起，这两个键会阻止所有网关凭证变量，导致开发者看到 `This machine's managed settings require a first-party login`。

[服务端托管设置](https://code.claude.com/docs/en/server-managed-settings#platform-availability)需要直连 `api.anthropic.com`，因此无法到达网关路由的会话。网关部署使用此处基于文件的托管设置路径。

需要单独分发的场景：
- 桌面应用：部署 MDM 交付的第三方推理配置
- CI Runner：在 Runner 环境中设置变量
- 托管 Windows 上的 WSL：需要 `wslInheritsWindowsSettings` 为 `true`

#### 交给开发者自行设置

如果没有托管设置分发机制，发给每位开发者：

- 网关 URL
- 个人凭证
- 凭证应放入哪个变量
- 条件变量及其值

**检查点**：开发者机器上 `claude` 启动不显示登录界面；`/status` 的 `Anthropic base URL` 显示网关地址。

### 验证推广效果

**从开发者机器确认（非网关主机），确保测试覆盖开发者实际使用的网络路径：**

```bash
curl -N -X POST "https://llm-gateway.example.com/v1/messages" \
  -H "Authorization: Bearer <developer-key>" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model": "claude-sonnet-4-6", "max_tokens": 16, "stream": true, "messages": [{"role": "user", "content": "count to 3"}]}'
```

应看到 `data:` 行逐步到达。整个响应在停顿后一次性到达表示网关在缓冲（会卡住 Claude Code）；`404` 表示模型名未路由。

然后启动 `claude` 发送消息。各症状对应：
- 登录提示：凭证缺失——检查 `/status` 的 `Setting sources`
- `Failed to authenticate`：网关拒绝请求——查看网关日志
- 密钥一次性审批提示：使用 `ANTHROPIC_API_KEY` 时首次使用的正常行为

最后检查网关日志：凭证标识开发者，[`x-claude-code-session-id`](https://code.claude.com/docs/en/llm-gateway-protocol#request-headers) 头按会话分组请求。

## 维护网关

**推广后需关注三类变化：**

| 变化 | 网关未跟上时的症状 | 应对措施 |
| :--- | :--- | :--- |
| 新 Claude Code 版本新增 beta 值和 Body 字段 | 开发者更新后报告 `400` 错误指向新字段 | 原样转发 `anthropic-*` 头和请求体；在新版本到达开发者前测试 |
| 新 Claude 模型可用 | 选择新模型名时返回 `404` | 在网关路由配置中添加模型名 |
| 凭证过期或需轮换 | 所有开发者请求返回上游 `401` | 轮换网关提供商凭证；开发者密钥在网关轮换 |

设置速率限制时，考虑客户端[重试瞬态失败](https://code.claude.com/docs/en/errors#automatic-retries)（含 `429`）最多 10 次带退避，遵循 `Retry-After`。

## 相关资源

- [连接 Claude Code 到 LLM 网关](https://code.claude.com/docs/en/llm-gateway-connect)：开发者设置步骤和排障表
- [网关协议参考](https://code.claude.com/docs/en/llm-gateway-protocol)：网关运维的协议协定
- [设置文件和优先级](https://code.claude.com/docs/en/settings#settings-files)：托管、项目和用户设置的组合方式
- [为组织设置 Claude Code](https://code.claude.com/docs/en/admin-setup)：网关所属的更广泛组织设置
