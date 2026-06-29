---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】Claude Code Artifacts 官方文档
description: Artifacts 将 Claude Code 终端输出一键发布为组织内可分享的实时交互网页。涵盖创建/更新/分享流程、五类构建模式（走读变更/对比方案/交互调参/进度追踪/决策回流）、页面约束（CSP/无后端/16MiB）、可用条件和组织管理。
category: translation
tags: [claude-code, artifacts, translation]
keywords: [artifacts, claude-code, official-docs]
refs:
  - https://code.claude.com/docs/en/artifacts.md
---

# 【译】Claude Code Artifacts

> **一句话理解：** Artifacts 把 Claude Code 终端里的工作成果，一键变成组织内可分享的实时网页。

> Beta 功能，需要 Team/Enterprise 计划 + `/login` 登录。完整要求见[可用条件](#可用条件全部满足才行)。

---

## 是什么

**Artifact = Claude Code 会话产出的一个实时交互网页，发布在 claude.ai 的私有 URL 上。**

浏览器打开即看。会话继续推进时，页面自动原地更新——不用刷新，不用重新打开。想让队友看到？页面头部有 Share 按钮，点一下就行。

典型用途：
- 带 reviewer 走读一个 PR，diff 旁边附行内注释
- 从会话数据生成仪表盘
- 并排展示多个设计/实现方案供评审
- 长任务运行期间维护一个自动填充的调查时间线
- 发链接给队友，替代粘到 Slack

### 不是什么

**Artifact 是工作成果的快照，不是应用。** 它是一个自包含的单页面，没有后端。具体来说：
- 不能存储表单输入
- 不能在查看时调用 API
- 不能提供多路由

需要带后端的内部工具？请部署到自己的基础设施上。

---

## 什么时候用

**判断标准：这个输出"看"比"读"更高效吗？如果是，用 artifact。**

Claude 能从会话触及的一切来构建页面——代码库、通过 [MCP 工具](https://code.claude.com/docs/en/mcp)拉取的数据等。因此一个页面能展示的信息量，远超文字描述几段话能覆盖的。

| 场景 | 做法 | 示例 Prompt |
|------|------|-------------|
| PR Review | 渲染 diff + 行内注释，按严重程度标色 | `Make an artifact that walks through this PR with the diff annotated inline.` |
| 方案对比 | 多种布局/实现并排，每个附一句 tradeoff | `Show four different layouts for the settings panel as a grid.` |
| 参数调优 | 滑块/开关绑定值，拖动时实时预览效果 | `Build an artifact with sliders for easing curve, duration, and delay.` |
| 进度同步 | 长任务运行时自动更新 checklist | `Turn this migration plan into a checklist artifact.` |
| 决策回流 | 页面上操作后 "Copy as prompt" 粘回终端 | `Make a triage board with a "Copy as prompt" button.` |

---

## 创建

**Claude 可能自行发布（当输出适合做页面时），你也可以直接要求。**

用自然语言描述即可。好的候选内容 = 任何"看比读更方便"的东西。

```
Make an artifact that walks through this PR. Render the diff with margin annotations and color-code findings by severity.
```

```
Build a dashboard artifact of last week's deploy failures by service and keep it updated as you investigate.
```

### 发布流程

1. Claude 写好 HTML/Markdown 文件到项目中
2. 首次发布新 artifact 时请求许可——弹出类似 `Claude wants to publish "Deploy failures" (deploy-failures.html) to a private page on claude.ai`
3. 你选 **Yes**
4. Claude 打印 URL，浏览器自动打开

重新发布已批准过的 artifact 不会再弹窗。

### 细节

- **标题和图标：** Claude 自动选择标题和 emoji 图标，两者出现在 [artifact 画廊](https://claude.ai/code/artifacts) 和分享链接中。想要特定标题/图标，直接告诉 Claude。
- **快捷键：** 随时按 `Ctrl+]` 从终端重新打开最近的 artifact。
- **关闭自动打开：** 设置 `CLAUDE_CODE_ARTIFACT_AUTO_OPEN=0`。
- **发布失败？** 如果 Claude 说无法发布或只写了本地 HTML 没有链接，说明[可用条件](#可用条件全部满足才行)未满足。

---

## 更新

**告诉 Claude 改什么，它编辑底层文件并重新发布到同一 URL。** 打开页面的人实时看到更新。

```
Add a per-region breakdown below the summary chart and republish.
```

### 版本机制

每次发布生成一个版本。从页面头部 **Share** 控件可以选择让查看者看到哪个版本。

### 跨会话更新

给新会话提供 artifact URL 即可更新已有页面。没有 URL 的话，新会话总是创建新 artifact。

```
Update https://claude.ai/code/artifact/5fbea6f3-... with today's numbers.
```

---

## 分享

**新 artifact 默认仅自己可见。**

打开页面后用头部 **Share** 控件操作：
- 可授权给组织内特定人，或全员
- 页面标注你为作者，所有人都能看到是谁发布的
- 作者头像链接到你的画廊 [claude.ai/code/artifacts](https://claude.ai/code/artifacts)，列出你创建的所有 artifact

### 限制

- **仅组织内：** 查看者必须以同一组织成员身份登录 claude.ai，没有对外选项
- **只读：** 分享的人能看到每个版本，但不能修改——你始终是唯一写入者
- **给外部人看？** 让 Claude 给你 HTML 文件，直接发文件

---

## 构建模式详解

**Artifact 是单个 HTML 页面，任何能用 HTML + CSS + 内联 JS 表达的内容都在范围内。**

### 走读变更

渲染 diff 或设计变更，相关行旁边加注释。reviewer 在代码旁边直接读到推理过程，不用从 PR 描述中还原上下文。

```
Make an artifact that walks through this PR. Render the diff with margin annotations and color-code findings by severity.
```

### 对比备选方案

多个变体放同一页面对照评估。适用于：布局、文案、API 设计、实现方案。

```
Make an artifact with four distinctly different layouts for the settings panel. Vary density and grouping, lay them out as a grid with a one-line tradeoff under each.
```

### 交互控件调优

把滑块/开关/输入框绑定到你正在调整的值。直接拖动探索，不用反复描述"把值改成 X 看看"。

```
Build an artifact with sliders for the easing curve, duration, and delay so I can try values on this transition. Show the animation live as I move them.
```

### 结果回流会话

Artifact 充当轻量编辑器：在页面上做决策，然后用导出控件生成文本粘回终端。页面交互的结果流回会话，形成闭环。

```
Make a triage board artifact with each open issue as a draggable card across Now, Next, Later, and Cut columns. Add a "Copy as prompt" button that gives me the final ordering to paste back here.
```

### 跟踪进行中的工作

长任务运行时让 Claude 持续更新 artifact。任何有链接的人可以跟进进展，不用盯终端。

```
Turn this migration plan into a checklist artifact. Check items off as you complete them and add a note for anything you skip.
```

---

## 视觉设计

**Claude 自带设计能力，页面默认有合理的配色、排版和布局。**

它还会在用自己的方案前，先查找你项目中已有的设计系统。要统一品牌风格，把 design tokens 记录在 Claude 能找到的地方——项目 [CLAUDE.md](https://code.claude.com/docs/en/memory) 或仓库中的 theme 文件：

```markdown
## Design system
- Colors: primary #1a4d8f, accent #f59e0b, surface #f8fafc
- Typography: Inter for body, JetBrains Mono for code
- Spacing: 8px scale, 6px border radius
```

**优先级：** 你的 prompt > 项目 design tokens > Claude 默认风格。

标题和格式随意，任何清晰的颜色/字体/间距列表都能被识别。

---

## 页面约束

**每个 artifact 是一个自包含单页面。** Claude Code 用 HTML shell 包裹文件，在严格 CSP 下提供服务。

| 约束 | 具体含义 |
|------|----------|
| 无外部请求 | CSP 阻止从任何其他主机加载脚本、样式、字体、图片，以及 `fetch`/XHR/WebSocket。Claude 自动把 CSS 和 JS 内联，图片转 data URI。 |
| 无后端 | 纯静态。不能存表单数据、自行鉴权、查看时调 API。 |
| 单页面 | 相对链接无法解析（旁边没有其他部署内容）。多段内容用页内锚点。 |
| 文件类型 | 仅 `.html` / `.htm` / `.md`。Markdown 渲染为带样式 HTML。 |
| 大小限制 | 渲染后 ≤ 16 MiB。大型嵌入图片是超限的常见原因。 |

### Token 成本

生成 artifact 消耗输出 token，带样式页面比纯文本终端输出贵。主要消耗来自：内联 CSS、交互 JS、data URI 图片。

**省 token 技巧：**
- 图表优先 SVG 或 HTML+CSS，不要嵌入位图
- 不需要的交互功能不加
- 大数据集做汇总展示，不要全量内联

---

## 可用条件（全部满足才行）

| 要求 | 条件 |
|------|------|
| 计划 | Team 或 Enterprise。Team 默认开启；Enterprise 需 Owner 在管理设置中[启用](#组织管理admin)。 |
| 认证 | `/login` 登录 claude.ai。API key、[gateway token](https://code.claude.com/docs/en/llm-gateway)、云提供商凭证均不行。 |
| 提供商 | Anthropic API 直连。不支持 [Bedrock](https://code.claude.com/docs/en/amazon-bedrock)、[Vertex AI](https://code.claude.com/docs/en/google-vertex-ai)、[Foundry](https://code.claude.com/docs/en/microsoft-foundry)。 |
| 组织策略 | 未启用 CMEK（客户管理加密密钥）、HIPAA、[零数据保留](https://code.claude.com/docs/en/zero-data-retention)。 |
| 载体 | Claude Code CLI，或 Desktop App ≥ 1.13576.0。在 [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview)、GitHub Action、MCP-server 中默认关闭；设置 `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` 时也关闭。 |

不满足时 Claude 写本地 HTML 文件或提示无法发布。

---

## 禁用方式

| 方式 | 设置 |
|------|------|
| [Settings 文件](https://code.claude.com/docs/en/settings) | `"disableArtifact": true` |
| [环境变量](https://code.claude.com/docs/en/env-vars) | `CLAUDE_CODE_DISABLE_ARTIFACT=1` |
| [权限规则](https://code.claude.com/docs/en/permissions) | 将 `Artifact` 加入 `permissions.deny` |

---

## 组织管理（Admin）

**位置：** [claude.ai/admin-settings/claude-code](https://claude.ai/admin-settings/claude-code)

Artifact 内容存储在 Anthropic 运营的基础设施上，仅对发布组织的已认证成员可见。

### 启用 / 禁用

进入 **Settings > Claude Code > Capabilities**，使用 **Artifacts** 开关。

Enterprise 计划可额外按角色控制：**Settings > Roles** → 编辑角色 → **Claude Code** 组下设置 **Artifacts** 权限。

### 保留策略

进入 **Settings > Data & privacy controls**。可分别设置：
- 仍为私有的 artifact 保留期
- 已分享的 artifact 保留期

超期自动删除。

### 审计日志

发布、分享、删除操作出现在组织审计日志的 `claude_artifact_*` 事件类型中（与 claude.ai 对话中创建的 artifact 共用同一事件族）。

### 网络白名单

查看器从沙盒化的 `*.claudeusercontent.com` 源加载 artifact。组织若限制出站网络，需将该域名加入白名单。完整列表见 [Network access requirements](https://code.claude.com/docs/en/network-config#network-access-requirements)。

### Compliance API

[Compliance API](https://docs.claude.com/en/api/compliance) 提供端点管理组织的 artifacts：

| 方法 | 端点 | 用途 |
|------|------|------|
| `GET` | `/v1/compliance/code/artifacts` | 列出组织所有 artifacts |
| `GET` | `/v1/compliance/code/artifacts/{artifact_id}/versions/{version_id}` | 获取特定版本内容 |
| `DELETE` | `/v1/compliance/code/artifacts/{artifact_id}` | 删除 artifact |

---

## 参考链接

- [Claude Code Artifacts 官方文档（原文）](https://code.claude.com/docs/en/artifacts.md)
- [Claude Code MCP 工具集成](https://code.claude.com/docs/en/mcp)
- [Claude Code 权限配置](https://code.claude.com/docs/en/permissions)
- [Claude Code 网络配置](https://code.claude.com/docs/en/network-config)
- [Compliance API 参考](https://docs.claude.com/en/api/compliance)
