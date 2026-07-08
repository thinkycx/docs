---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Apps Gateway 限额
description: Claude Apps Gateway 的消费限额功能，按日/周/月限制每个开发者的使用量。通过 Admin API 设置上限，gateway 实时强制执行。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/claude-apps-gateway-spend-limits.md
  - en-source/claude-apps-gateway-spend-limits.md
---

# Claude Apps Gateway 消费限额

> 按日、周或月限制每个开发者通过 Claude apps gateway 的消费。通过 Admin API 设置上限，gateway 在每个请求上实时强制执行。

**消费限额为每个开发者设定指定周期内的消费上限。** 开发者超过上限时，gateway 在其下一个请求返回 `429` 并阻止至周期重置或管理员提高上限。用消费限额为共享凭证的每个开发者、组或整个组织设置天花板。

Claude apps gateway 通过一个共享上游凭证转发所有推理，服务商账单将一切归属于该凭证而非个人开发者。没有逐开发者限制，一个失控的 agent 群可以花光组织的全部承诺。消费限额是 gateway 在共享账单之上的逐开发者视图和断路器。

## 设置上限

**在 `gateway.yaml` 配置 [`admin:`](https://code.claude.com/docs/en/claude-apps-gateway-config#admin) 块后**，gateway 在 `/v1/organizations/spend_limits` 提供 admin API，并在每个推理请求上实时强制上限。上限通过该 API 设置而非在 `gateway.yaml` 中。

设置组织级默认每月 $500/开发者：

```bash
curl -sS https://claude-gateway.internal.example.com/v1/organizations/spend_limits \
  -H "x-api-key: $GATEWAY_ADMIN_WRITE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"scope": {"type": "organization"}, "amount": "50000", "period": "monthly"}'
```

为 `contractors` 组设置更严格的每日 $100 上限：

```bash
curl -sS https://claude-gateway.internal.example.com/v1/organizations/spend_limits \
  -H "x-api-key: $GATEWAY_ADMIN_WRITE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"scope": {"type": "rbac_group", "rbac_group_id": "contractors"}, "amount": "10000", "period": "daily"}'
```

| 字段 | 值 | 说明 |
| --- | --- | --- |
| `scope.type` | `user`、`rbac_group`、`organization` | `user` 按 OIDC `sub` 定位单个开发者；`rbac_group` 按 IdP 组名定位；`organization` 是全组织默认 |
| `amount` | 美分整数字符串或 `null` | `null` 无限制。`"0"` 阻止所有请求 |
| `period` | `daily`、`weekly`、`monthly` | 每个 scope 可按周期持有一个上限，各自独立强制 |

**组或组织上限是每人默认值**，非共享池。每个周期内开发者的有效上限解析顺序：用户级覆盖 -> 最严格的组上限 -> 组织默认 -> 无限制。[`admin.group_limit_mode: max`](https://code.claude.com/docs/en/claude-apps-gateway-config#admin) 将多组取值翻转为最宽松。

### Admin API 认证

发送以下之一：

- `x-api-key` header 匹配 [`admin.write_keys`](https://code.claude.com/docs/en/claude-apps-gateway-config#admin) 中的 key（完全访问）或 `admin.read_keys`（仅 GET）
- Gateway bearer token 且 `groups` 声明包含 [`admin.admin_groups`](https://code.claude.com/docs/en/claude-apps-gateway-config#admin) 中的某个组（完全访问，审计为 `oidc:<sub>`）

## 强制执行原理

**每个 `/v1/messages` 请求上**，gateway 在一次 Postgres 查询中解析开发者的上限和周期累计消费。超出任何上限时返回 `429`，`error.type: billing_error`，header `x-should-retry: false`。

`/v1/messages/count_tokens` 豁免。Token 计数免费，无论上限状态都可执行。

**响应后**，使用量计量器从流式响应中读取 token 计数，按 USD 列表价定价，增量更新 Postgres 中三个周期桶的计数器。计量器是流上的单一读者，客户端字节不受影响，计量失败不破坏响应。

消费限额是断路器而非发票。权威计费请对照服务商的使用量报告。

**定价使用与 Claude Code CLI 成本展示相同的表**，跨 Anthropic、Amazon Bedrock、Google Cloud Agent Platform 和 Microsoft Foundry ID 格式的模型 ID 规范化。无法识别的模型 ID 按未知模型默认层（$5/$25 每百万输入/输出 token）定价而非零，防止未识别 ID 绕过上限。

**客户端中止也计费。** 上游仅在流的终止帧报告输出 token，中止的流不携带。计量器从流内容大小保持保守下限估计（约每 token 4 字符），在终止使用量帧缺失时计费。完整流始终使用上游报告的计数。

### Postgres 可用性

预检查以 2 秒超时查询 Postgres。如果存储不可达或超时，**默认 fail-open**：请求继续，gateway 记录警告。设置 [`enforcement.fail_closed_on_error: true`](https://code.claude.com/docs/en/claude-apps-gateway-config#enforcement) 改为 fail-closed（返回相同 `429 billing_error`）。

Fail-open 防止存储中断成为推理中断；fail-closed 保证无未计量消费。

## Admin API 参考

端点在 `/v1/organizations/spend_limits` 下：

| 方法和路径 | 说明 |
| --- | --- |
| `GET /v1/organizations/spend_limits` | 列出已配置上限。查询：`?limit=&after_id=&before_id=` |
| `POST /v1/organizations/spend_limits` | 为 `{scope, period}` 创建或替换上限 |
| `GET /v1/organizations/spend_limits/{id}` | 按 `spl_` 前缀 ID 获取单个上限 |
| `DELETE /v1/organizations/spend_limits/{id}` | 删除单个上限 |
| `GET /v1/organizations/spend_limits/effective` | 每个 principal 每周期的解析上限和累计消费 |
| `GET /v1/organizations/spend_limits/audit` | Admin 变更记录，最新优先 |

约定与 Anthropic Admin API 一致：

- 每个对象有 `type` 字段
- `spl_` 前缀 ID
- 金额为美分整数字符串；`POST` 拒绝 `USD` 以外的 `currency`
- `{type: "error", error: {type, message}, request_id}` 错误封装
- 每个 admin 响应含 `request-id` 响应 header

每次变更在同一事务中写入 before/after 行到 `admin_audit`。

### `/effective`

返回 Anthropic 的 `SpendSummary` schema：每行是一个 principal 一个周期，含解析上限、周期累计消费和 `actor` 对象。Gateway 特定差异：

- `user_id` 是 OIDC `sub`
- `actor.name` 和 `actor.email_address` 在 principal 首次推理请求前为 `null`
- 每行带 `groups` 数组（gateway 扩展，展示所有适用的上限层）

| 查询参数 | 说明 |
| --- | --- |
| `user_ids[]` | 可重复。按 OIDC `sub` 过滤 |
| `period[]` | 可重复。过滤 `daily`、`weekly` 或 `monthly` 行 |
| `sort` | `spend_desc` 按消费降序。需恰好一个 `period[]` |
| `q` | 大小写不敏感子串过滤，匹配 OIDC `sub`、最近邮箱和显示名 |
| `limit` / `page` | 页大小 1-1000（默认 20）和上一响应 `next_page` 的不透明游标 |

> `q=` 和 `user_ids[]=` 通过 GET 查询字符串传递，前置代理/负载均衡器的访问日志会捕获它们。如果 PII 日志策略严格，在那里清理这些参数。

### `/audit`

返回消费限额变更记录：谁改了哪个上限、before/after 快照和可选原因，最新优先。

### 分页

原始列表通过 `after_id` 和 `before_id` 分页（互斥的 `spl_...` ID）。`/effective` 通过 `next_page` 不透明 token 分页。`limit` 为 1-1000，默认 20。

## 数据生命周期

Gateway 持有四个消费相关表，每小时清理强制保留窗口：

| 表 | 内容 | 保留 |
| --- | --- | --- |
| `spend` | 每 principal 周期累计计数器（美分） | [`admin.spend_retention_months`](https://code.claude.com/docs/en/claude-apps-gateway-config#admin)，默认 13 |
| `spend_limits` | 已配置的上限 | 通过 API 删除前一直保留 |
| `admin_audit` | 变更记录 | [`admin.audit_retention_days`](https://code.claude.com/docs/en/claude-apps-gateway-config#admin)，默认 365 |
| `principal_emails` | 每个 principal 最近邮箱、显示名和 IdP 组。含 PII | [`admin.identity_retention_days`](https://code.claude.com/docs/en/claude-apps-gateway-config#admin) 自最近活动起，默认 90 |

`identity_retention_days` 有意短于 `spend_retention_months`：已撤销身份停止刷新并自然淡出，而其匿名消费计数器保留用于同比报告。

**开发者离职时**，通过 `DELETE /v1/organizations/spend_limits/{id}` 删除用户级上限；消费和身份行按上述保留窗口自然淡出。如需立即擦除，直接对 gateway 数据库运行 `DELETE FROM principal_emails WHERE principal = '<sub>'`。

## 相关

- [`admin` 和 `enforcement` 配置](https://code.claude.com/docs/en/claude-apps-gateway-config#admin)：启用 admin API 和调整保留
- [部署指南](https://code.claude.com/docs/en/claude-apps-gateway-deploy#postgres)：Postgres schema 和备份指导
