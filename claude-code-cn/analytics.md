---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】使用分析
description: Claude Code 提供分析仪表盘帮助团队追踪使用指标、开发者采纳率和工程效率。本文介绍了 Team/Enterprise 和 API 两种方案的仪表盘功能、GitHub 贡献指标集成以及 PR 归因机制。
category: translation
tags: [claude-code, analytics, translation]
refs:
  - https://code.claude.com/docs/en/analytics.md
---

# 使用分析追踪团队用量

> 在分析仪表盘中查看 Claude Code 使用指标、追踪采纳率并衡量工程效率。

**Claude Code 提供分析仪表盘，帮助团队了解开发者使用模式、追踪贡献指标并衡量对工程效率的影响。** 根据你的方案类型访问对应的仪表盘：

| 方案 | 仪表盘地址 | 包含内容 | 更多信息 |
| --- | --- | --- | --- |
| Claude for Teams / Enterprise | [claude.ai/analytics/claude-code](https://claude.ai/analytics/claude-code) | 使用指标、GitHub 集成的贡献指标、排行榜、数据导出 | [详情](#team-和-enterprise-方案的分析功能) |
| API（Claude Console） | [platform.claude.com/claude-code](https://platform.claude.com/claude-code) | 使用指标、花费追踪、团队洞察 | [详情](#api-客户的分析功能) |

## Team 和 Enterprise 方案的分析功能

**管理员和所有者可在仪表盘中查看使用和贡献数据。** 访问 [claude.ai/analytics/claude-code](https://claude.ai/analytics/claude-code) 即可打开。

Team 和 Enterprise 方案的仪表盘包含：

- **使用指标**：接受的代码行数、建议接受率、每日活跃用户和会话数
- **贡献指标**：在 Claude Code 协助下提交的 PR 和代码行数，需 [GitHub 集成](#启用贡献指标)
- **排行榜**：按 Claude Code 使用量排名的顶级贡献者
- **数据导出**：下载贡献数据为 CSV 用于自定义报告

如需按用户查看 token 用量和成本估算，请配置 [OpenTelemetry 导出](https://code.claude.com/docs/en/monitoring-usage)。

### 启用贡献指标

> 贡献指标目前处于公测阶段，适用于 Claude for Teams 和 Claude for Enterprise 方案。这些指标仅覆盖 claude.ai 组织内的用户，不包含通过 Claude Console API 或第三方集成的用量。

**所有 Team 和 Enterprise 账户都可查看使用和采纳数据，但贡献指标需要额外配置 GitHub 连接。** 需要 Owner 角色来配置分析设置，GitHub 管理员需要安装 GitHub App。

> 已启用[零数据保留](https://code.claude.com/docs/en/zero-data-retention)的组织无法使用贡献指标，仪表盘将仅显示使用指标。

配置步骤：

1. **安装 GitHub App** - GitHub 管理员在 [github.com/apps/claude](https://github.com/apps/claude) 安装 Claude GitHub App
2. **启用 Claude Code 分析** - Claude Owner 访问 [claude.ai/admin-settings/claude-code](https://claude.ai/admin-settings/claude-code) 并开启分析功能
3. **启用 GitHub 分析** - 在同一页面开启 "GitHub analytics" 开关
4. **完成 GitHub 认证** - 完成 GitHub 认证流程，选择要纳入分析的 GitHub 组织

启用后数据通常在 24 小时内显示，每日更新。如果没有数据，可能会看到以下提示：

- **"GitHub app required"**：需要安装 GitHub App 才能查看贡献指标
- **"Data processing in progress"**：几天后再查看，确认已安装 GitHub App

贡献指标支持 GitHub Cloud 和 GitHub Enterprise Server。

### 查看汇总指标

> 这些指标采取保守计算策略，代表的是 Claude Code 实际影响的低估值。只有高置信度确认 Claude Code 参与的行数和 PR 才被纳入统计。

**仪表盘顶部显示以下汇总指标：**

| 指标 | 说明 |
| --- | --- |
| PRs with CC | 包含至少一行 Claude Code 编写代码的已合并 PR 总数 |
| Lines of code with CC | 所有已合并 PR 中由 Claude Code 协助编写的代码行数。只计算"有效行"：规范化后超过 3 个字符的行，排除空行和仅含括号或简单标点的行 |
| PRs with Claude Code (%) | 包含 Claude Code 协助代码的已合并 PR 占比 |
| Suggestion accept rate | 用户接受 Claude Code 代码编辑建议（包括 Edit、Write、NotebookEdit 工具）的比例 |
| Lines of code accepted | Claude Code 编写的、被用户在会话中接受的代码行数总计。不含被拒绝的建议，也不追踪后续删除 |

### 探索图表

**仪表盘包含多个图表，可视化展示趋势变化。**

#### 追踪采纳趋势

Adoption 图表展示每日使用趋势：

- **users**：每日活跃用户数
- **sessions**：每日活跃 Claude Code 会话数

#### 衡量每用户 PR 数

此图表展示单个开发者的活动趋势：

- **PRs per user**：每日合并的 PR 总数除以每日活跃用户数
- **users**：每日活跃用户数

**通过此图可以观察随着 Claude Code 采纳率增长，个人生产力的变化。**

#### 查看 Pull Request 分布

Pull requests 图表展示已合并 PR 的每日分布：

- **PRs with CC**：包含 Claude Code 协助代码的 PR
- **PRs without CC**：不包含 Claude Code 协助代码的 PR

可切换到 **Lines of code** 视图，按代码行数查看同样的分布。

#### 查找顶级贡献者

排行榜展示按贡献量排名的前 10 名用户。可切换：

- **Pull requests**：展示每个用户的 Claude Code PR 与全部 PR 对比
- **Lines of code**：展示每个用户的 Claude Code 代码行数与全部代码行数对比

点击 **Export all users** 可下载所有用户的完整贡献数据 CSV。导出包含全部用户，不限于显示的前 10 名。

### PR 归因机制

**启用贡献指标后，Claude Code 会分析已合并 PR，判断哪些代码由 Claude Code 协助编写。** 通过将 Claude Code 会话活动与 PR 代码进行匹配来实现。

#### 标记标准

如果 PR 包含至少一行在 Claude Code 会话中编写的代码，就会被标记为 "with Claude Code"。系统采用保守匹配策略：只有高置信度确认 Claude Code 参与的代码才被计为协助代码。

#### 归因流程

当 PR 被合并时：

1. 从 PR diff 中提取新增行
2. 识别在时间窗口内编辑过匹配文件的 Claude Code 会话
3. 使用多种策略将 PR 行与 Claude Code 输出进行匹配
4. 计算 AI 协助行数和总行数的指标

比较前会对行进行规范化：去除首尾空白、合并多个空格、统一引号格式、转换为小写。

包含 Claude Code 协助行的已合并 PR 会在 GitHub 中被标记 `claude-code-assisted` 标签。

#### 时间窗口

归因匹配考虑 PR 合并日期前 21 天到后 2 天内的会话。

#### 排除的文件

**以下自动生成的文件会自动排除在分析之外：**

| 类别 | 示例 |
| --- | --- |
| 锁文件 | package-lock.json、yarn.lock、Cargo.lock 等 |
| 生成代码 | Protobuf 输出、构建产物、压缩文件 |
| 构建目录 | dist/、build/、node_modules/、target/ |
| 测试固件 | 快照、cassettes、mock 数据 |
| 超长行 | 超过 1000 字符的行（可能是压缩或生成内容） |

#### 归因注意事项

解读归因数据时需注意：

- 被开发者大幅改写（差异超过 20%）的代码不会归因给 Claude Code
- 超出 21 天窗口的会话不被考虑
- 算法不考虑 PR 的源分支或目标分支

### 充分利用分析功能

**利用贡献指标来证明 ROI、识别采纳模式并找到可以帮助他人入门的团队成员。**

#### 监控采纳情况

追踪 Adoption 图表和用户数来识别：

- 可以分享最佳实践的活跃用户
- 组织范围内的整体采纳趋势
- 可能表示摩擦或问题的使用下降

#### 衡量 ROI

贡献指标帮助回答"这个工具值不值得投资"——用你自己代码库的数据：

- 追踪随着采纳率增长，每用户 PR 数的变化
- 对比有无 Claude Code 协助时提交的 PR 和代码行数
- 结合 [DORA 指标](https://dora.dev/)、Sprint 速度或其他工程 KPI 来理解采纳 Claude Code 带来的变化

#### 识别高级用户

排行榜帮你找到 Claude Code 采纳度高的团队成员，他们可以：

- 与团队分享提示技巧和工作流
- 提供关于哪些方面效果好的反馈
- 帮助新用户入门

#### 编程方式访问数据

要通过 GitHub 查询此数据，搜索带有 `claude-code-assisted` 标签的 PR。

## API 客户的分析功能

**API 客户可在 Console 仪表盘查看使用和花费指标。** 访问 [platform.claude.com/claude-code](https://platform.claude.com/claude-code)。需要 UsageView 权限，Developer、Billing、Admin、Owner 和 Primary Owner 角色均有此权限。

> 贡献指标和 GitHub 集成目前不适用于 API 客户。Console 仪表盘仅显示使用和花费指标。

Console 仪表盘显示：

- **Lines of code accepted**：Claude Code 编写的、被用户接受的代码行数总计。不含被拒绝的建议，不追踪后续删除
- **Suggestion accept rate**：用户接受代码编辑工具（Edit、Write、NotebookEdit）使用建议的比例
- **Activity**：以图表展示的每日活跃用户和会话数
- **Spend**：每日 API 花费（美元）及用户数

### 查看团队洞察

团队洞察表格展示按用户的指标：

| 字段 | 说明 |
| --- | --- |
| Members | 所有已认证 Claude Code 的用户。API Key 用户显示 Key 标识符，OAuth 用户显示邮箱 |
| Spend this month | 当月每用户 API 总花费 |
| Lines this month | 当月每用户接受的代码行数总计 |

> Console 仪表盘中的花费数据为用于分析的估算值。实际费用请参考账单页面。

## 相关资源

- [OpenTelemetry 监控](https://code.claude.com/docs/en/monitoring-usage)：将实时指标和事件导出到可观测性平台
- [有效管理成本](https://code.claude.com/docs/en/costs)：设置花费限制并优化 token 使用
- [权限](https://code.claude.com/docs/en/permissions)：配置角色和权限
