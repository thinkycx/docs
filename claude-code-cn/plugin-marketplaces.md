---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】插件市场
description: 介绍如何创建和分发插件市场（marketplace），覆盖 marketplace.json 结构、插件来源类型、托管方式、版本解析、发布渠道、重命名迁移和组织级限制。
category: translation
tags: [claude-code, plugin-marketplaces, translation]
refs:
  - https://code.claude.com/docs/en/plugin-marketplaces.md
  - en-source/plugin-marketplaces.md
---

# 创建和分发插件市场

**插件市场是一个目录，让你向他人分发插件。** 提供集中发现、版本跟踪、自动更新和多种来源类型支持。

要安装已有市场的插件，见 [Discover and install plugins](https://code.claude.com/docs/en/discover-plugins)。

## 概览

创建和分发市场的步骤：

1. **创建插件**：构建含 skills、agents、hooks、MCP/LSP 服务器的插件
2. **创建市场文件**：定义 `marketplace.json` 列出插件及其来源
3. **托管市场**：推送到 GitHub、GitLab 或其他 git 主机
4. **分享给用户**：用户用 `/plugin marketplace add` 添加，安装个别插件

## 演练：创建本地市场

### 1. 创建目录结构

```bash
mkdir -p my-marketplace/.claude-plugin
mkdir -p my-marketplace/plugins/quality-review-plugin/.claude-plugin
mkdir -p my-marketplace/plugins/quality-review-plugin/skills/quality-review
```

### 2. 创建技能

```markdown
# my-marketplace/plugins/quality-review-plugin/skills/quality-review/SKILL.md
---
description: Review code for bugs, security, and performance
---

Review the code I've selected or the recent changes for:
- Potential bugs or edge cases
- Security concerns
- Performance issues
- Readability improvements

Be concise and actionable.
```

### 3. 创建插件清单

```json
// my-marketplace/plugins/quality-review-plugin/.claude-plugin/plugin.json
{
  "name": "quality-review-plugin",
  "description": "Adds a quality-review skill for quick code reviews",
  "version": "1.0.0"
}
```

### 4. 创建市场文件

```json
// my-marketplace/.claude-plugin/marketplace.json
{
  "name": "my-plugins",
  "owner": { "name": "Your Name" },
  "plugins": [
    {
      "name": "quality-review-plugin",
      "source": "./plugins/quality-review-plugin",
      "description": "Adds a quality-review skill for quick code reviews"
    }
  ]
}
```

### 5. 添加和安装

```shell
/plugin marketplace add ./my-marketplace
/plugin install quality-review-plugin@my-plugins
```

## 市场 Schema

### 必填字段

| 字段 | 类型 | 描述 |
|------|------|------|
| `name` | string | 市场标识符（kebab-case）。用户安装时可见 |
| `owner` | object | 维护者信息（`name` 必填，`email` 可选） |
| `plugins` | array | 可用插件列表 |

### 可选字段

| 字段 | 类型 | 描述 |
|------|------|------|
| `description` | string | 市场简述 |
| `version` | string | 市场清单版本 |
| `metadata.pluginRoot` | string | 相对插件来源路径的基目录 |
| `allowCrossMarketplaceDependenciesOn` | array | 允许跨市场依赖的市场列表 |
| `renames` | object | 旧插件名到新名的映射（v2.1.193+） |

## 插件来源

| 来源 | 类型 | 字段 |
|------|------|------|
| 相对路径 | string（如 `"./my-plugin"`） | 无 |
| `github` | object | `repo`、`ref?`、`sha?` |
| `url` | object | `url`、`ref?`、`sha?` |
| `git-subdir` | object | `url`、`path`、`ref?`、`sha?` |
| `npm` | object | `package`、`version?`、`registry?` |

### GitHub 仓库

```json
{
  "name": "github-plugin",
  "source": {
    "source": "github",
    "repo": "owner/plugin-repo",
    "ref": "v2.0.0",
    "sha": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"
  }
}
```

### Git 子目录

```json
{
  "name": "my-plugin",
  "source": {
    "source": "git-subdir",
    "url": "https://github.com/acme-corp/monorepo.git",
    "path": "tools/claude-plugin"
  }
}
```

### npm 包

```json
{
  "name": "my-npm-plugin",
  "source": {
    "source": "npm",
    "package": "@acme/claude-plugin",
    "version": "2.1.0",
    "registry": "https://npm.example.com"
  }
}
```

## 托管和分发

### GitHub（推荐）

用户添加：`/plugin marketplace add owner/repo`

### 其他 git 服务

```shell
/plugin marketplace add https://gitlab.com/company/plugins.git
```

### 私有仓库

Claude Code 使用已有 git 凭据助手。后台自动更新需设置环境变量：

| Provider | 环境变量 |
|----------|---------|
| GitHub | `GITHUB_TOKEN` 或 `GH_TOKEN` |
| GitLab | `GITLAB_TOKEN` 或 `GL_TOKEN` |
| Bitbucket | `BITBUCKET_TOKEN` |

### 为团队要求市场

在 `.claude/settings.json` 中配置：

```json
{
  "extraKnownMarketplaces": {
    "company-tools": {
      "source": { "source": "github", "repo": "your-org/claude-plugins" }
    }
  },
  "enabledPlugins": {
    "code-formatter@company-tools": true
  }
}
```

### 容器预填充

设置 `CLAUDE_CODE_PLUGIN_SEED_DIR` 指向预构建的插件目录。启动时 Claude Code 注册种子市场并使用缓存的插件而无需重新克隆。

## 版本解析和发布渠道

Claude Code 按以下优先级解析插件版本：

1. `plugin.json` 中的 `version`
2. 市场条目中的 `version`
3. Git commit SHA

省略 `version` 则每次新提交视为新版本。设置 `version` 则锁定——必须 bump 才能让用户收到更新。

### 发布渠道

设置两个市场指向同一仓库的不同 ref 实现 stable/latest 分离：

```json
// stable-tools marketplace.json
{ "plugins": [{ "name": "formatter", "source": { "source": "github", "repo": "acme/formatter", "ref": "stable" } }] }

// latest-tools marketplace.json  
{ "plugins": [{ "name": "formatter", "source": { "source": "github", "repo": "acme/formatter", "ref": "latest" } }] }
```

通过管理设置将不同市场分配给不同用户组。

## 重命名或删除插件

**`name` 是稳定标识符。** 改变它会破坏所有现有安装。要改 UI 显示名，用 `displayName`。

如必须改名，添加顶层 `renames` 条目（v2.1.193+）：

```json
{
  "name": "acme-tools",
  "plugins": [{ "name": "code-formatter", "source": "./plugins/code-formatter" }],
  "renames": {
    "formatter": "code-formatter",
    "legacy-linter": null
  }
}
```

`renames` 视为追加历史——保留旧条目。Claude Code 跟随链式重命名。

## 管理级市场限制

用 [`strictKnownMarketplaces`](https://code.claude.com/docs/en/settings#strictknownmarketplaces) 限制用户可添加的市场：

| 值 | 行为 |
|----|------|
| 未定义 | 无限制 |
| 空数组 `[]` | 完全锁定 |
| 来源列表 | 仅允许精确匹配白名单的市场 |

```json
{
  "strictKnownMarketplaces": [
    { "source": "github", "repo": "acme-corp/approved-plugins" },
    { "source": "hostPattern", "hostPattern": "^github\\.example\\.com$" }
  ]
}
```

## CLI 命令

### marketplace add

```bash
claude plugin marketplace add <source> [--scope user|project|local] [--sparse <paths...>]
```

### marketplace list

```bash
claude plugin marketplace list [--json]
```

### marketplace remove

```bash
claude plugin marketplace remove <name> [--scope <scope>]
```

### marketplace update

```bash
claude plugin marketplace update [name]
```

## 故障排查

| 问题 | 解决方案 |
|------|---------|
| 市场不加载 | 验证 URL 可访问、`.claude-plugin/marketplace.json` 存在、JSON 语法有效 |
| 插件安装失败 | 验证来源 URL 可访问、插件目录含必需文件 |
| 私有仓库认证失败 | 验证已认证（`gh auth status`）、凭据助手正确配置 |
| 离线环境更新失败 | 设置 `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1` |
| Git 操作超时 | 增加 `CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS`（毫秒） |

## 另见

- [Plugins](https://code.claude.com/docs/en/plugins) — 创建插件
- [Plugin dependencies](https://code.claude.com/docs/en/plugin-dependencies) — 版本约束
- [Plugins reference](https://code.claude.com/docs/en/plugins-reference) — 完整技术参考
- [Discover plugins](https://code.claude.com/docs/en/discover-plugins) — 安装插件
