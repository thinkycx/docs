---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】安全指引
description: 介绍 security-guidance 插件的安装和使用，该插件让 Claude 在编写代码时自动审查漏洞并在同一会话中修复，覆盖逐编辑模式匹配、每轮 diff 审查和提交级深度审查三层检测。
category: translation
tags: [claude-code, security-guidance, translation]
refs:
  - https://code.claude.com/docs/en/security-guidance.md
  - en-source/security-guidance.md
---

# 在 Claude 写代码时捕获安全问题

**安装 security-guidance 插件，让 Claude 在工作时自动审查自己的代码变更中的漏洞，并在同一会话中修复。**

该插件捕获注入、不安全反序列化、不安全 DOM API 等问题——在代码到达 PR 之前——减少下游人工安全审查的负担。

安装后，插件自动运行。无需调用，无需记住命令。

## 前提条件

- Claude Code CLI v2.1.144 或更高版本
- Python 3.8+ 在 `PATH` 中（插件按顺序尝试 `python3`、`python`、`py -3`）
- 工作目录是 git 仓库（end-of-turn 和 commit 审查基于 git state，非仓库静默跳过；逐编辑模式匹配在任何地方工作）

## 安装插件

```text
/plugin install security-guidance@claude-plugins-official
```

选择 user scope 写入用户设置，使其在每个新本地会话加载。

激活当前会话：

```text
/reload-plugins
```

### 在云会话和共享仓库启用

用户作用域插件不会带入 [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web)。要在那里启用，或为克隆仓库的所有人启用：

```json
// .claude/settings.json
{
  "enabledPlugins": {
    "security-guidance@claude-plugins-official": true
  }
}
```

管理员可通过管理设置 ([managed settings](https://code.claude.com/docs/en/admin-setup)) 组织级启用。

## 三层检查

**插件在三个时间点审查 Claude 的工作，每层深度不同。**

| 层 | 时机 | 机制 | 成本 |
|----|------|------|------|
| 逐编辑模式匹配 | Claude 写文件时 | 确定性字符串匹配，无模型调用 | 零 |
| 每轮 Diff 审查 | 每轮结束后 | 后台模型审查本轮所有变更 | 标准模型用量 |
| 提交/推送审查 | Claude 执行 `git commit` 或 `git push` 时 | 更深的 agentic 审查，读取周围代码 | 多轮模型用量 |

### 逐编辑模式匹配

Claude 写入文件时，插件扫描已知风险模式。无模型调用，零成本。

示例模式类别：
- 动态代码执行：`eval(`、`new Function`、`os.system`、`child_process.exec`
- 不安全反序列化：`pickle`
- DOM 注入：`dangerouslySetInnerHTML`、`.innerHTML =`、`document.write`
- 工作流文件：`.github/workflows/` 下的编辑

每个模式每文件每会话只触发一次。

### 每轮 Diff 审查

一轮是 Claude 响应的一个回合。轮结束后，插件计算工作树中本轮所有变更的 git diff，发送给独立 Claude 做安全审查。后台运行不延迟回复。

能捕获模式匹配无法发现的问题：授权绕过、IDOR、注入、SSRF、弱加密等。

每轮最多覆盖 30 个变更文件，连续最多触发三次。

### 提交/推送审查

Claude 通过 Bash 工具运行 `git commit` 或 `git push` 时触发。读取周围代码（调用者、清洁器、相关文件）判断发现是否为真，降低误报。

每滚动小时上限 20 次。如果提交审查的发现与每轮审查已报告的重复，不会重复提示。

### 审查独立性

- 逐编辑检查是确定性字符串匹配，无模型参与
- 每轮和提交审查作为独立 Claude 调用运行，有新鲜上下文和安全聚焦的 prompt
- 没有任何层阻止写入或提交。发现作为指令传达给写代码的 Claude

## 添加自定义规则

### 模型审查的指导文件

创建 `.claude/claude-security-guidance.md`，用自然语言描述你的威胁模型和审查清单：

```markdown
# Security guidance for this repo

- Do not log `customer_id` or `account_number` at INFO level or above.
- All routes under `/admin` must call `require_role("admin")` before any database read.
- Use `crypto.timingSafeEqual` for token comparison instead of `===`.
```

### 自定义逐编辑模式

创建 `.claude/security-patterns.yaml`：

```yaml
patterns:
  - rule_name: internal_api_key
    substrings: ["sk_live_", "AKIA"]
    reminder: "Hardcoded API key prefix. Load credentials from the secret manager."
  - rule_name: tenant_unfiltered_query
    regex: "\\.objects\\.all\\(\\)"
    paths: ["**/src/tenants/**"]
    reminder: "Multi-tenant code must filter by org_id."
```

| 字段 | 类型 | 描述 |
|------|------|------|
| `rule_name` | string | 警告中显示的标识符 |
| `reminder` | string | 追加到 Claude 上下文的警告文本，上限 1 KB |
| `regex` | string | Python 正则匹配编辑内容 |
| `substrings` | list | 字面子串；与 `regex` 二选一 |
| `paths` | list | 可选 glob 模式；规则仅适用于匹配文件 |
| `exclude_paths` | list | 可选 glob 模式，跳过匹配文件 |

### 规则文件查找位置

| 范围 | 路径 | 备注 |
|------|------|------|
| 用户 | `~/.claude/claude-security-guidance.md` | 适用于你机器上每个项目 |
| 项目 | `.claude/claude-security-guidance.md` | 随仓库提交 |
| 项目本地 | `.claude/claude-security-guidance.local.md` | gitignored，个人覆盖 |

插件加载所有存在的位置并拼接，指导文件合并上限 8 KB。

## 使用成本

- 逐编辑模式匹配：零成本
- 每轮和提交审查：额外模型用量计入 [usage](https://code.claude.com/docs/en/costs)
- 默认使用 Claude Opus 4.7。可通过 `SECURITY_REVIEW_MODEL`（每轮审查）和 `SG_AGENTIC_MODEL`（提交审查）设置不同模型

所有计划均可使用。

## 禁用或卸载

| 环境变量 | 效果 |
|---------|------|
| `ENABLE_PATTERN_RULES=0` | 禁用逐编辑模式匹配 |
| `ENABLE_STOP_REVIEW=0` | 禁用每轮 diff 审查 |
| `ENABLE_COMMIT_REVIEW=0` | 禁用提交/推送审查 |
| `ENABLE_CODE_SECURITY_REVIEW=0` | 一次性禁用所有模型审查 |
| `SECURITY_GUIDANCE_DISABLE=1` | 完全禁用插件（无需卸载） |

暂停：`/plugin disable security-guidance@claude-plugins-official`

卸载：`/plugin uninstall security-guidance@claude-plugins-official`

## 与其他安全工具的配合

| 阶段 | 工具 | 覆盖范围 |
|------|------|---------|
| 会话中 | Security guidance 插件 | Claude 写的代码中的常见漏洞，同会话修复 |
| 按需 | [`/security-review`](https://code.claude.com/docs/en/commands#all-commands) | 当前分支的一次性安全扫描 |
| PR 时 | [Code Review](https://code.claude.com/docs/en/code-review)（Team/Enterprise） | 多 agent 正确性和安全审查 |
| CI 中 | 现有静态分析和依赖扫描 | 语言特定规则、供应链检查 |

每个后续阶段捕获前面阶段遗漏的。插件的价值是减少到达它们的体量，而非消除对它们的需求。

## 故障排查

插件将运行时诊断写入 `~/.claude/security/log.txt`。

常见跳过原因：
- 目录不是 git 仓库
- 会话无 Anthropic 认证（仅逐编辑模式匹配运行）
- `security-patterns.yaml` 存在但 PyYAML 不可导入（用 `security-patterns.json` 替代）

## 相关资源

- [Code Review](https://code.claude.com/docs/en/code-review) — 设置 PR 时的多 agent 审查
- [Hooks guide](https://code.claude.com/docs/en/hooks-guide) — 在相同生命周期点构建自己的检查
- [Discover plugins](https://code.claude.com/docs/en/discover-plugins#official-anthropic-marketplace) — 浏览其他官方插件
