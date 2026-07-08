---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】错误参考
description: 查阅 Claude Code 运行时错误消息的含义和修复方法。涵盖服务器错误、使用限额、认证、网络、请求和安装错误的完整参考。
category: translation
tags: [claude-code, translation]
refs:
  - https://code.claude.com/docs/en/errors.md
  - en-source/errors.md
---

# 错误参考

> 查阅 Claude Code 运行时错误消息的含义和修复方法。

**本页列出 Claude Code 显示的运行时错误及恢复方式。** 安装错误（如 `command not found` 或 TLS 失败）请参见[安装排错](https://code.claude.com/docs/en/troubleshoot-install)。

这些错误和恢复命令适用于 CLI、[Desktop](https://code.claude.com/docs/en/desktop) 和 [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web)，因为三者包装的是同一个 Claude Code CLI。

Claude Code 调用 Claude API 获取模型响应，大多数运行时错误对应底层 API 错误码。原始 HTTP 状态码定义参见 [Claude Platform 错误参考](https://platform.claude.com/docs/en/api/errors)。

## 错误速查表

| 消息 | 章节 |
| :--- | :--- |
| `API Error: 500 Internal server error` | [服务器错误](#api-error-500-internal-server-error) |
| `API Error: Repeated 529 Overloaded errors` | [服务器错误](#api-error-repeated-529-overloaded-errors) |
| `Request timed out` | [服务器错误](#request-timed-out) |
| `Server error mid-response` / `Connection closed mid-response` | [服务器错误](#响应可能不完整) |
| `You've hit your session limit` / `weekly limit` | [使用限额](#使用限额) |
| `Not logged in · Please run /login` | [认证错误](#not-logged-in) |
| `Invalid API key` | [认证错误](#invalid-api-key) |
| `Unable to connect to API` | [网络错误](#unable-to-connect-to-api) |
| `SSL certificate verification failed` | [网络错误](#ssl-证书错误) |
| `Prompt is too long` | [请求错误](#prompt-is-too-long) |
| `There's an issue with the selected model` | [请求错误](#模型问题) |
| Responses seem lower quality | [响应质量](#响应质量似乎下降) |

## 自动重试

**Claude Code 在显示错误前自动重试瞬态故障。** 服务器错误、过载响应、请求超时、临时 429 限流和断连都会重试最多 10 次（指数退避）。

两类故障不重试：TLS 证书验证失败（第一次尝试即失败），以及已流式输出可见内容后的服务器错误（保留部分响应并附加通知）。

重试期间，spinner 显示 `Retrying in Ns · attempt x/y` 倒计时。

| 变量 | 默认值 | 效果 |
| :--- | :--- | :--- |
| [`CLAUDE_CODE_MAX_RETRIES`](https://code.claude.com/docs/en/env-vars) | 10 | 重试次数 |
| [`CLAUDE_CODE_RETRY_WATCHDOG`](https://code.claude.com/docs/en/env-vars) | 未设置 | 设为 `1` 在无人值守会话中无限重试 429 和 529 |
| [`API_TIMEOUT_MS`](https://code.claude.com/docs/en/env-vars) | 600000 | 每请求超时（毫秒） |

## 服务器错误

### API Error: 500 Internal server error

API 内部意外故障。非你的 prompt、设置或账户导致。

**处理：** 检查 [status.claude.com](https://status.claude.com)；等一分钟重试；输入 `try again`。

### API Error: Repeated 529 Overloaded errors

API 暂时满载。不是你的使用限制，不计入配额。

**处理：** 检查状态页；几分钟后重试；运行 `/model` 切换模型。

### Request timed out

API 在连接截止时间前未响应。默认请求超时 10 分钟。

**处理：** 重试；分解大任务；提高 `API_TIMEOUT_MS`。

### 响应可能不完整

流式响应在 Claude 已产生可见输出后失败。Claude Code 保留已流式内容并附加通知。

**处理：** 阅读已流式的响应；回复 `continue` 让 Claude 接续。

### Auto mode 无法判断动作安全性

[Auto mode](https://code.claude.com/docs/en/permission-modes#eliminate-prompts-with-auto-mode) 的分类器未能产生决策。读取、搜索和工作目录内的编辑不受影响。

**处理：** 几秒后重试；如持续失败，切换[权限模式](https://code.claude.com/docs/en/permission-modes)手动审批；如上下文超限，运行 `/compact`。

## 使用限额

### You've hit your session limit

订阅计划的滚动使用额度已用完。

**处理：** 等待消息中显示的重置时间；运行 `/usage` 查看限额；运行 `/usage-credits` 购买额外用量。

### Usage credits required for 1M context

选择的模型使用 1M 扩展上下文，你的计划仅通过 usage credits 提供。

**处理：** 运行 `/model` 选择无 `[1m]` 后缀的变体；或运行 `/usage-credits` 开启按量计费。

### Credit balance is too low

Console 组织的预付费额度已用完。

**处理：** 在 [platform.claude.com](https://platform.claude.com/settings/billing) 充值并考虑启用自动充值。

## 认证错误

### Not logged in

无可用凭据。

**处理：** 运行 `/login`；确认 `ANTHROPIC_API_KEY` 已设置并 export。

### Invalid API key

`ANTHROPIC_API_KEY` 或 `apiKeyHelper` 返回的密钥被 API 拒绝。

**处理：** 检查拼写和是否被撤销；运行 `env | grep ANTHROPIC` 检查；取消设置后运行 `/login`。

### OAuth token revoked or expired

保存的登录不再有效。

**处理：** 运行 `/login` 重新登录；如反复出现先运行 `/logout`。

### AWS credentials expired or invalid

AWS 会话令牌过期或被拒绝，自动刷新未成功。

**处理：** 运行消息中指示的 `awsAuthRefresh` 命令（如 `aws sso login`）；或运行 `/login` 选择刷新凭据选项。

## 网络错误

### Unable to connect to API

到 API 的 TCP 连接失败或未完成。

**处理：** 运行 `curl -I https://api.anthropic.com` 确认网络连通；设置 `HTTPS_PROXY`；确保防火墙允许[网络访问要求](https://code.claude.com/docs/en/network-config#network-access-requirements)中的域名。

### SSL 证书错误

代理或安全设备用自己的证书拦截 TLS 流量，Claude Code 不信任它。

**处理：** 导出组织 CA 包并设置 `NODE_EXTRA_CA_CERTS=/path/to/ca-bundle.pem`；参见[网络配置](https://code.claude.com/docs/en/network-config#custom-ca-certificates)。

## 请求错误

### Prompt is too long

对话加附件超出模型上下文窗口。

**处理：** 运行 `/compact` 或 `/clear`；运行 `/context` 查看占用分布；禁用不用的 MCP 服务器。

### Request too large

原始请求体超过 API 字节限制（最大 30 MB）。

**处理：** 按 Esc 两次回退；用路径引用大文件而非粘贴内容。

### 模型问题

配置的模型名未识别或账户无权访问。

**处理：** 运行 `/model` 从可用模型中选择；使用 `sonnet` 或 `opus` 等别名而非完整版本 ID；检查[优先级顺序](https://code.claude.com/docs/en/model-config#setting-your-model)中的过期值。

### thinking.type.enabled is not supported for this model

Claude Code 版本低于 Sonnet 5、Opus 4.8 或 Opus 4.7 所需的最低版本。

**处理：** 运行 `claude update` 并重启；或运行 `/model` 选择旧模型。

### Usage Policy refusal

API 因对话内容触发[使用政策](https://www.anthropic.com/legal/aup)检查而拒绝响应。

**处理：** 按 Esc 两次或运行 `/rewind` 回退到触发拒绝的轮次之前；运行 `/clear` 开始新对话。

## 安装错误

### Installation was killed before it could finish

安装脚本报告 `claude install` 步骤被信号终止。Linux 上退出码 137 意味着 OOM killer 终止了进程。

**处理：** 停止其他进程释放内存后重试；添加 swap 空间或使用更大实例。参见[低内存 Linux 服务器安装](https://code.claude.com/docs/en/troubleshoot-install#install-killed-on-low-memory-linux-servers)。

### The connection dropped while downloading the update

下载 Claude Code 二进制时连接断开，重试未恢复。

**处理：** 再次运行 `claude update`；设置 `HTTPS_PROXY`；请网络团队允许 `downloads.claude.ai` 的完整下载。

## 命令行错误

### --bg and --print conflict

`--bg` 与 `-p`/`--print` 组合。`--bg` 启动可附加的后台会话，`--print` 非交互运行永不启动交互会话。

**处理：** 去掉 `-p`。`--bg` 将 prompt 作为位置参数：`claude --bg "<task>"`。

## 配置警告

### Workspace has not been trusted

Claude Code 发现项目设置中的 `permissions.allow` 规则但未应用，因为[允许规则需要工作区信任](https://code.claude.com/docs/en/permissions#project-allow-rules-and-workspace-trust)。

**处理：** 在目录中运行 `claude` 并接受信任对话框；非交互模式下在 `~/.claude.json` 中设置 `hasTrustDialogAccepted`。

## 响应质量似乎下降

**如果 Claude 的回答似乎不如预期但无错误显示**，原因通常是对话状态而非模型本身。检查：

- **模型选择**：运行 `/model` 确认当前模型
- **Effort 级别**：运行 `/effort` 检查并提高
- **上下文压力**：运行 `/context` 查看窗口使用；接近满时运行 `/compact`
- **过期指令**：大型或过时的 `CLAUDE.md` 文件消耗上下文

回退（`/rewind`）通常比在线程中纠正更好。纠正保留错误尝试在上下文中，可能锚定后续回答。

## 报告错误

- 在 Claude Code 内运行 `/feedback` 发送记录和描述给 Anthropic
- 运行 `/doctor` 检查本地配置问题
- 检查 [status.claude.com](https://status.claude.com)
- 搜索 [GitHub issues](https://github.com/anthropics/claude-code/issues)
