---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】服务端托管设置
description: 通过 claude.ai 控制台集中配置 Claude Code 的服务端托管设置，无需设备管理基础设施。涵盖配置方式、设置下发、安全审批和平台可用性。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/server-managed-settings.md
  - en-source/server-managed-settings.md
---

# 配置服务端托管设置

> 通过服务器下发的设置集中配置组织的 Claude Code，无需设备管理基础设施。

**服务端托管设置允许组织 Owner 在 [Admin Settings > Claude Code > Managed settings](https://claude.ai/admin-settings/claude-code) 中集中配置 Claude Code。** 用户通过组织 OAuth 登录或直接配置的 API 密钥认证时，Claude Code 客户端自动获取这些设置。参见[平台可用性](#平台可用性)了解支持的平台。

适用于没有设备管理基础设施、或需要管理非托管设备上用户的组织。

> 服务端托管设置适用于 [Claude for Teams](https://claude.com/pricing?utm_source=claude_code&utm_medium=docs&utm_content=server_settings_teams#team-&-enterprise) 和 [Claude for Enterprise](https://anthropic.com/contact-sales?utm_source=claude_code&utm_medium=docs&utm_content=server_settings_enterprise) 客户。

## 前提条件

使用服务端托管设置需要：

- Claude for Teams 或 Claude for Enterprise 计划
- 组织中的 Owner 或 Primary Owner 角色（查看和编辑配置）
- Claude Code v2.1.38 或更高版本（Teams），或 v2.1.30 或更高版本（Enterprise）
- 网络可访问 `api.anthropic.com`

## 选择服务端托管还是端点托管设置

**Claude Code 支持两种集中配置方式：**

| 方式 | 适用场景 | 安全模型 |
| :--- | :--- | :--- |
| **服务端托管设置** | 无 MDM 的组织，或非托管设备上的用户 | 认证时从 Anthropic 服务器下发 |
| **[端点托管设置](https://code.claude.com/docs/en/settings#settings-files)** | 有 MDM 或端点管理的组织 | 通过 MDM 配置文件、注册表策略或托管设置文件部署到设备 |

如果设备已注册 MDM 或端点管理方案，端点托管设置提供更强的安全保证，因为设置文件可在 OS 层面保护不被用户修改。端点托管设置无法到达[云会话](https://code.claude.com/docs/en/model-config#surface-coverage)，所以使用 Web 版 Claude Code 的组织也应配置服务端托管设置。

## 配置服务端托管设置

### 步骤 1：打开管理控制台

在 claude.ai 控制台进入 [Admin Settings > Claude Code > Managed settings](https://claude.ai/admin-settings/claude-code)。

如果链接重定向到其他 Admin Settings 页面，说明你的账号没有所需角色。Admin 和其他非 Owner 角色无法查看或编辑。

### 步骤 2：定义设置

**以 JSON 添加配置。** 支持 [`settings.json` 中可用的所有设置](https://code.claude.com/docs/en/settings#available-settings)（少量仅限 OS 层策略的除外）。包括 [hooks](https://code.claude.com/docs/en/hooks)、[环境变量](https://code.claude.com/docs/en/env-vars) 和[仅托管设置](https://code.claude.com/docs/en/permissions#managed-only-settings)如 `allowManagedPermissionRulesOnly`。

权限拒绝列表示例：

```json
{
  "permissions": {
    "deny": [
      "Bash(curl *)",
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ],
    "disableBypassPermissionsMode": "disable"
  },
  "allowManagedPermissionRulesOnly": true
}
```

Hook 配置示例（每次文件编辑后运行审计脚本）：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "/usr/local/bin/audit-edit.sh" }
        ]
      }
    ]
  }
}
```

Auto mode 配置示例：

```json
{
  "autoMode": {
    "environment": [
      "Source control: github.example.com/acme-corp and all repos under it",
      "Trusted cloud buckets: s3://acme-build-artifacts, gs://acme-ml-datasets",
      "Trusted internal domains: *.corp.example.com"
    ]
  }
}
```

由于 hook 执行 Shell 命令，用户在应用前会看到[安全审批对话框](#安全审批对话框)。

### 步骤 3：保存和部署

保存更改。Claude Code 客户端在下次启动或每小时轮询时收到更新的设置。

### 验证设置下发

让用户重启 Claude Code。如果配置包含触发[安全审批对话框](#安全审批对话框)的设置，用户启动时会看到描述托管设置的提示。也可让用户运行 `/permissions` 查看生效的权限规则。

### 访问控制

可管理服务端托管设置的角色：

- **Primary Owner**
- **Owner**

限制访问给可信人员，因为设置变更影响组织中所有用户。

### 仅托管设置

大多数[设置键](https://code.claude.com/docs/en/settings#available-settings)在任何作用域工作。少数键仅从托管设置读取，放在用户或项目设置文件中无效。参见[仅托管设置](https://code.claude.com/docs/en/permissions#managed-only-settings)完整列表。

### 当前限制

- 设置统一应用于组织中所有用户。尚不支持按组配置。
- [`managed-mcp.json`](https://code.claude.com/docs/en/managed-mcp) 文件无法通过服务端托管设置分发。改用 `allowedMcpServers` 和 `deniedMcpServers` 策略键。
- 仅限 OS 层策略源的设置（如 `policyHelper` 和 `wslInheritsWindowsSettings`）不被支持。通过 MDM 或系统 `managed-settings.json` 文件部署。

## 设置下发

### 设置优先级

**服务端托管设置和[端点托管设置](https://code.claude.com/docs/en/settings#settings-files)同属最高优先级层。** 没有其他设置层可以覆盖它们，包括命令行参数。

在托管层内，已配置的 [`policyHelper`](https://code.claude.com/docs/en/settings#compute-managed-settings-with-a-policy-helper) 优先于所有其他托管源（包括服务端托管设置）。

否则，Claude Code 使用第一个提供非空配置的源。服务端托管设置优先检查，然后是端点托管设置。源不合并：如果服务端托管设置提供了任何键，其他端点托管设置被忽略。

### 获取和缓存行为

Claude Code 在启动时从 Anthropic 服务器获取设置，活跃会话期间每小时轮询更新。

**首次启动无缓存设置时：**
- Claude Code 异步获取设置
- 获取失败则继续运行（无托管设置）
- 设置加载前有一个短暂窗口期，限制未执行

**后续启动有缓存设置时：**
- 缓存设置立即在启动时应用（下述变量除外）
- Claude Code 在后台获取新设置
- 缓存设置在网络故障期间持续有效

自 v2.1.198 起，Claude Code 在服务器确认负载之前扣留缓存 `env` 块中三类变量：
- 代理和 TLS 配置（如 `HTTPS_PROXY`、`NODE_EXTRA_CA_CERTS`）
- API 路由和提供商选择（如 `ANTHROPIC_BASE_URL`、`CLAUDE_CODE_USE_BEDROCK`）
- 认证凭证（如 `ANTHROPIC_API_KEY`、`ANTHROPIC_AUTH_TOKEN`）

如果你的组织需要代理才能访问 `api.anthropic.com`，在 Shell 环境或[用户设置](https://code.claude.com/docs/en/settings#settings-files)中设置代理，而非仅在托管 `env` 块中。

### 无效条目处理

交付的负载以宽容模式解析。当条目 schema 验证失败时，Claude Code 剥离该条目、显示验证错误并应用所有剩余有效设置。

### 强制启动时失败关闭

默认情况下，远程设置获取失败时 CLI 继续运行（无托管设置）。对于不接受此短暂未执行窗口的环境，在托管设置中设置 `forceRemoteSettingsRefresh: true`：

```json
{
  "forceRemoteSettingsRefresh": true
}
```

启用后，CLI 在启动时阻塞直到远程设置获取成功。获取失败则退出而非继续。自 v2.1.139 起，`claude auth` 子命令（如 `claude auth login`）豁免此检查。

启用前确保网络策略允许连接 `api.anthropic.com`。端点不可达时 CLI 启动退出，用户无法使用 Claude Code。

### 安全审批对话框

**以下设置需要用户明确批准后 Claude Code 才应用：**

- Shell 命令设置
- 不在已知安全允许列表中的自定义环境变量
- Hook 配置
- 通过托管设置下发的 `claudeMd` 内容

用户看到安全对话框说明正在配置什么。拒绝设置则 Claude Code 退出。

> 使用 `-p` 标志的非交互模式下，Claude Code 跳过安全对话框直接应用设置。

## 平台可用性

**服务端托管设置需要直连 `api.anthropic.com`**，且会话需通过组织 OAuth 登录或直接配置的 API 密钥认证。`apiKeyHelper` 脚本返回的密钥不触发设置获取。

以下第三方模型提供商不支持服务端托管设置：

- Amazon Bedrock
- Google Cloud Agent Platform
- Microsoft Foundry
- [Claude Platform on AWS](https://code.claude.com/docs/en/claude-platform-on-aws)
- 通过 `ANTHROPIC_BASE_URL` 的自定义 API 端点或第三方 [LLM 网关](https://code.claude.com/docs/en/llm-gateway)

对于 Amazon Bedrock、Google Cloud Agent Platform 和 Microsoft Foundry 部署，自托管的 [Claude apps gateway](https://code.claude.com/docs/en/claude-apps-gateway) 提供等效的远程托管设置下发。

## 审计日志

设置变更的审计日志事件可通过 compliance API 或审计日志导出获取。联系 Anthropic 账户团队获取访问权限。

## 安全考量

**服务端托管设置提供集中策略执行，但作为客户端控制而非安全边界运行。** 在非托管设备上，用户无需管理员或 sudo 权限即可绕过。

| 场景 | 行为 |
| :--- | :--- |
| 用户编辑缓存设置文件 | 篡改文件在启动时应用，下次服务器获取时恢复正确设置。自 v2.1.198 起，`env` 块中的传输/路由/认证变量在服务器确认前被扣留 |
| 用户删除缓存设置文件 | 首次启动行为：异步获取设置，短暂未执行窗口 |
| 用户运行修改过的 Claude Code 二进制 | 能运行修改客户端的用户能绕过任何客户端控制 |
| 用户运行旧版 Claude Code | 早于服务端托管设置的版本不获取或应用 |
| API 不可用 | 有缓存则应用缓存，否则下次成功获取前不执行。使用 `forceRemoteSettingsRefresh: true` 时 CLI 退出 |
| 用户使用第三方模型提供商 | 服务端托管设置被绕过 |

要检测运行时配置变更，使用 [`ConfigChange` hooks](https://code.claude.com/docs/en/hooks#configchange)。

要限制用户可用凭证访问的组织，参见 [Tenant Restrictions](https://support.claude.com/en/articles/13198485-enforce-network-level-access-control-with-tenant-restrictions)。更强执行保证请使用 MDM 注册设备上的[端点托管设置](https://code.claude.com/docs/en/settings#settings-files)。

## 相关页面

- [设置](https://code.claude.com/docs/en/settings)：完整配置参考
- [端点托管设置](https://code.claude.com/docs/en/settings#settings-files)：IT 部署到设备的托管设置
- [认证](https://code.claude.com/docs/en/authentication)：设置用户访问
- [安全](https://code.claude.com/docs/en/security)：安全保障和最佳实践
