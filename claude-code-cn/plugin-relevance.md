---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】插件推荐
description: 介绍如何在 marketplace.json 的插件条目中添加 relevance 块，让 Claude Code 根据用户当前工作上下文推荐安装相关插件。
category: translation
tags: [claude-code, plugin-relevance, translation]
refs:
  - https://code.claude.com/docs/en/plugin-relevance.md
  - en-source/plugin-relevance.md
---

# 为组织推荐插件

**在 marketplace.json 的插件条目中添加 `relevance` 块，让 Claude Code 根据用户工作上下文建议安装相关插件。**

如果你运营组织的插件市场，可以让 Claude Code 根据用户正在做的事情推荐特定插件。在 `marketplace.json` 中为插件条目添加 `relevance` 对象，然后在管理设置中将市场加入白名单。当用户会话匹配声明的信号时，Claude Code 浮现该插件的安装建议。

市场声明的建议通过管理设置 ([managed settings](https://code.claude.com/docs/en/settings#settings-files)) 按市场单独启用。没有管理员将市场加入白名单，任何市场的 `relevance` 声明都不会产生建议。

此功能需要 Claude Code v2.1.152 或更高版本。

## 工作原理

**信号匹配在用户本地机器上进行。不增加网络流量，不向 Anthropic 或市场运营者报告匹配了什么。**

每个插件条目可以携带一个 `relevance` 对象，命名一个主题和一个或多个信号。信号是 Claude Code 针对当前会话测试的模式（如工作目录、Claude 读过的文件等）。

当信号匹配且插件未安装时，Claude Code 在三个位置展示：

| 展示位置 | 描述 | 最低版本 |
|---------|------|---------|
| Spinner 提示 | Claude 响应时 spinner 下方显示 "Working with *topic*? Install the *plugin* plugin" | v2.1.152 |
| 会话启动建议 | `cwd` 信号匹配时，首轮前显示一行通知 | v2.1.153 |
| `/plugin` Discover 标签 | 插件置顶并标注匹配原因 | v2.1.154 |

Claude Code 永远不会自动安装插件。用户始终确认。

## 添加 relevance 到插件条目

```json
{
  "name": "acme-corp-plugins",
  "owner": { "name": "Acme Platform Team" },
  "plugins": [
    {
      "name": "terraform-helpers",
      "source": "./plugins/terraform-helpers",
      "description": "Acme conventions and helpers for Terraform",
      "relevance": {
        "topic": "Terraform",
        "signals": {
          "cli": ["terraform"],
          "filesRead": ["**/*.tf"]
        }
      }
    }
  ]
}
```

## 字段参考

### `relevance`

| 字段 | 类型 | 描述 |
|------|------|------|
| `topic` | string | 可选。填入 "Working with *topic*?" 的短语。通常是产品名。默认为插件名连字符分段首字母大写。最长 64 字符 |
| `signals` | object | 决定插件何时相关的匹配器。至少需要一个信号 |

### `relevance.signals`

| 字段 | 类型 | 描述 |
|------|------|------|
| `cwd` | array of strings | Glob 模式匹配会话工作目录。唯一能在会话启动时（首轮前）匹配的信号。最多 10 个，每个 256 字符 |
| `cli` | array of strings | Claude 本会话运行的 shell 命令名称。精确匹配。最多 10 个，每个 64 字符 |
| `hosts` | array of strings | 本会话 Bash 命令中 URL 的主机名。纯小写主机名，无 scheme/port/path。最多 20 个，每个 128 字符 |
| `filesRead` | array of strings | Glob 模式匹配 Claude 本会话读过的文件路径。最多 10 个，每个 256 字符 |
| `manifestDeps` | array of objects | 匹配 Claude 读过的包清单中声明的依赖。每个条目 `{ "file": "...", "pattern": "..." }`。最多 10 个 |

`cli`、`hosts`、`filesRead`、`manifestDeps` 需要会话历史，仅在 spinner 提示和 Discover 标签中匹配。只有 `cwd` 能在会话启动时匹配。

### manifestDeps 示例

```json
{
  "name": "stripe-helpers",
  "source": "./plugins/stripe-helpers",
  "relevance": {
    "topic": "Stripe",
    "signals": {
      "manifestDeps": [
        {
          "file": "[/\\\\]package\\.json$",
          "pattern": "\"stripe\"\\s*:"
        }
      ]
    }
  }
}
```

## 在管理设置中启用建议

**仅在 marketplace.json 中声明 `relevance` 不够。管理员必须在管理设置中将市场加入白名单。**

在 `managed-settings.json` 中添加市场名到 `pluginSuggestionMarketplaces`：

```json
{
  "extraKnownMarketplaces": {
    "acme-corp-plugins": {
      "source": {
        "source": "github",
        "repo": "acme-corp/claude-plugins"
      }
    }
  },
  "pluginSuggestionMarketplaces": ["acme-corp-plugins"]
}
```

官方市场免除源声明要求，只需白名单名称：

```json
{
  "pluginSuggestionMarketplaces": ["claude-plugins-official"]
}
```

## 用户看到什么

Spinner 提示：

```text
Working with Terraform? Install the terraform-helpers plugin:
/plugin install terraform-helpers@acme-corp-plugins
```

会话启动通知：

```text
plugin suggestion: terraform-helpers@acme-corp-plugins · /plugin
```

频率限制：

- 每三个会话最多展示一次（spinner 和启动通知合并计算）
- 安装后不再重复
- 启动通知展示两次后停止

## 验证市场

运行 `claude plugin validate` 检查 `relevance` 块：

```
claude plugin validate ./my-marketplace
```

验证器报告 `relevance` 和 `relevance.signals` 下的未知键为警告，标记非对象的 `relevance` 值，拒绝包含 scheme/port/path 的 `signals.hosts` 条目。

## 另见

- [Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces) — 构建托管插件的市场
- [Plugin hints](https://code.claude.com/docs/en/plugin-hints) — 从你自己的 CLI 提示用户
- [Settings](https://code.claude.com/docs/en/settings) — `pluginSuggestionMarketplaces` 和 `extraKnownMarketplaces` 完整参考
