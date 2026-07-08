---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】插件依赖
description: 介绍如何在 plugin.json 中声明依赖版本约束，防止上游插件发布破坏性变更时影响你的插件。覆盖声明语法、版本解析、冲突处理和孤立清理。
category: translation
tags: [claude-code, plugin-dependencies, translation]
refs:
  - https://code.claude.com/docs/en/plugin-dependencies.md
  - en-source/plugin-dependencies.md
---

# 约束插件依赖版本

**在 plugin.json 中声明版本约束，让你的插件在上游发布破坏性变更时仍能正常工作。**

插件可以通过 `plugin.json` 或市场条目中列出依赖。默认情况下依赖跟踪最新版本，上游发布可能在不通知的情况下改变依赖。版本约束让你将依赖锁定在经测试的版本范围内。

安装声明了依赖的插件时，Claude Code 自动解析并安装依赖。如果依赖后来丢失，`/reload-plugins` 和后台自动更新会重新安装（前提是其市场已在你配置的市场中）。

本指南面向在 `plugin.json` 中声明依赖的插件作者和标记发布的市场维护者。

> 依赖版本约束需要 Claude Code v2.1.110 或更高版本。

## 为什么要约束依赖版本

**场景示例：** 平台团队维护 `secrets-vault` v2.1.0，部署团队的 `deploy-kit` 调用它获取凭据。没有版本约束，平台团队重命名 MCP 工具后，自动更新会移动所有人的 `secrets-vault` 到新版本，`deploy-kit` 就坏了。

有了 `~2.1.0` 约束，用户保持在最高匹配的 `2.1.x` 补丁版本。部署团队按自己的节奏升级。

## 声明带版本约束的依赖

在 `plugin.json` 的 `dependencies` 数组中列出：

```json
{
  "name": "deploy-kit",
  "version": "3.1.0",
  "dependencies": [
    "audit-logger",
    { "name": "secrets-vault", "version": "~2.1.0" }
  ]
}
```

| 字段 | 类型 | 描述 |
|------|------|------|
| `name` | string | 插件名。在声明插件的同一市场内解析。必填 |
| `version` | string | [semver 范围](https://github.com/npm/node-semver#ranges)，如 `~2.1.0`、`^2.0`、`>=1.4`、`=2.1.0` |
| `marketplace` | string | 不同市场来解析 `name`。跨市场依赖需白名单允许 |

## 跨市场依赖

**默认 Claude Code 拒绝自动安装来自不同市场的依赖。**

要允许，根市场维护者在 `marketplace.json` 中添加目标市场到 `allowCrossMarketplaceDependenciesOn`：

```json
{
  "name": "acme-tools",
  "owner": { "name": "Acme" },
  "allowCrossMarketplaceDependenciesOn": ["acme-shared"],
  "plugins": [
    {
      "name": "deploy-kit",
      "source": "./deploy-kit",
      "dependencies": [
        { "name": "audit-logger", "marketplace": "acme-shared" }
      ]
    }
  ]
}
```

## 标记插件发布

**版本约束基于市场仓库的 git tag 解析。** 上游插件必须用特定命名约定标记发布。

标记格式：`{plugin-name}--v{version}`

```bash
claude plugin tag --push
```

该命令从插件清单和市场条目推导 tag 名，验证内容，检查 `plugin.json` 和市场条目版本一致，要求干净工作树，tag 已存在则拒绝。加 `--dry-run` 预览。

安装 `{ "name": "secrets-vault", "version": "~2.1.0" }` 时，Claude Code 列出市场 tag，过滤 `secrets-vault--v` 开头的，取满足范围的最高版本。

## 约束交互

**多个已安装插件约束同一依赖时，Claude Code 取交集并解析满足所有约束的最高版本。**

| 插件 A 要求 | 插件 B 要求 | 结果 |
|------------|------------|------|
| `^2.0` | `>=2.1` | 一次安装：2.1.0 及以上的最高 `2.x` tag。两个插件加载 |
| `~2.1` | `~3.0` | 安装插件 B 失败 `range-conflict`。A 和依赖不受影响 |
| `=2.1.0` | 无 | 依赖停留在 `2.1.0`。A 安装期间自动更新跳过更新版本 |

卸载最后一个约束依赖的插件后，依赖恢复跟踪市场条目。

## 启用/禁用带依赖的插件

**启用插件也启用其依赖；禁用被其他启用的插件依赖的插件会被阻止。** 需要 v2.1.143+。

启用时的条件处理：

| 条件 | 结果 |
|------|------|
| 依赖未安装 | 启用失败，打印 `claude plugin install` 命令 |
| 依赖被组织策略阻止 | 启用失败，标明被阻止的依赖 |
| 依赖在更高优先级作用域被设为 `false` | 启用失败。在该作用域启用依赖，或传 `--scope` |
| 所有依赖已安装且允许 | 启用成功，为插件和各依赖写入 `true` |

禁用被依赖的插件时，错误消息给出链式命令按正确顺序禁用。

## 清理孤立的自动安装依赖

```bash
claude plugin prune
```

列出不再有已安装插件需要的自动安装依赖并在确认后移除。默认操作用户作用域，`--scope project` 或 `--scope local` 指定其他作用域。`--dry-run` 预览，`-y` 跳过确认。

卸载时顺带清理：

```bash
claude plugin uninstall deploy-kit --prune
```

## 解决依赖错误

| 错误 | 含义 | 解决方法 |
|------|------|---------|
| `dependency-unsatisfied` | 声明的依赖未安装或已禁用 | 运行错误消息中的 `claude plugin install`。如果依赖市场未配置，用 `claude plugin marketplace add` 添加 |
| `range-conflict` | 版本要求无法组合 | 卸载或更新冲突插件，修复无效 `version` 字符串，简化长 `\|\|` 链 |
| `dependency-version-unsatisfied` | 已安装依赖版本在声明范围外 | 运行 `claude plugin install <dependency>@<marketplace>` 重新解析 |
| `no-matching-tag` | 依赖仓库无满足范围的 tag | 检查上游是否按约定标记发布，或放宽范围 |

编程检查：`claude plugin list --json` 读取每个插件的 `errors` 字段。

## 另见

- [Create plugins](https://code.claude.com/docs/en/plugins) — 构建含技能、agent 和 hooks 的插件
- [Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces) — 为团队托管插件
- [Plugins reference](https://code.claude.com/docs/en/plugins-reference#plugin-manifest-schema) — 完整 `plugin.json` schema
- [Version management](https://code.claude.com/docs/en/plugins-reference#version-management) — 插件自身版本的解析方式
