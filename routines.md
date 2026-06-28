---
create: 2026-06-28
update: 2026-06-28
author: thinkycx
title: 【译】Routines 自动化任务
description: Routines 是 Claude Code 的云端自动化能力，支持定时调度、API 触发和 GitHub 事件驱动三种方式，让 Claude 在无人值守的环境中自动执行代码审查、告警分流、文档维护等重复性任务。
category: translation
tags: [claude-code, routines, automation, translation]
refs: [https://code.claude.com/docs/en/routines.md]
---

# 用 Routines 实现自动化

> **让 Claude Code 全自动运行。** 定义 routine，按计划调度、通过 API 触发或响应 GitHub 事件，全部运行在 Anthropic 托管的云基础设施上。

> [!NOTE]
> Routines 目前处于研究预览阶段，行为、限制和 API 接口可能随时变更。

**Routine 就是一份保存好的 Claude Code 配置：** 包含一条 prompt、一个或多个仓库、以及一组 [connectors](https://code.claude.com/docs/en/mcp)，打包一次即可自动运行。Routine 在 Anthropic 托管的云基础设施上执行，即使你的电脑合上盖子，任务也会继续运行。

每个 routine 可以挂载一个或多个触发器：

| 触发器类型 | 说明 |
| :--- | :--- |
| **Schedule（定时）** | 按周期运行，如每小时、每晚、每周，或在指定的未来时间点运行一次 |
| **API** | 通过向 routine 专属的 HTTP 端点发送 POST 请求来按需触发 |
| **GitHub** | 响应仓库事件（如 Pull Request 或 Release）自动运行 |

一个 routine 可以组合多种触发器。例如一个 PR 审查 routine 可以每晚定时运行，也可以从部署脚本触发，还能响应每个新 PR。

**适用计划与入口：** Pro、Max、Team 和 Enterprise 用户开启 [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web) 后即可使用。在 [claude.ai/code/routines](https://claude.ai/code/routines) 创建和管理，或在 CLI 中使用 `/schedule` 命令。

**组织管控：** Team 和 Enterprise Owner 可以在 [claude.ai/admin-settings/claude-code](https://claude.ai/admin-settings/claude-code) 通过 Routines 开关为全体成员关闭此功能。关闭后已有 routine 停止运行，成员也无法新建。

本文涵盖创建 routine、配置各类触发器、管理运行记录以及用量限制。

---

## 典型使用场景

以下示例将触发器类型与适合 routine 的工作场景配对：无人值守、可重复、且有明确产出。

| 场景 | 触发器 | 做什么 |
| :--- | :--- | :--- |
| **Backlog 维护** | Schedule（每个工作日晚上） | 通过 connector 读取 issue tracker 中新增的 issue，自动打标签、根据涉及的代码区域分配负责人，并在 Slack 发送摘要 |
| **告警分流** | API（由监控工具调用） | 拉取堆栈跟踪，关联最近的 commit，开出带修复方案的 Draft PR 并附告警链接，on-call 直接审查 PR 而不是从零开始排查 |
| **定制代码审查** | GitHub（`pull_request.opened`） | 按团队自有的 checklist 进行审查，对安全、性能、风格问题留行内评论，并添加总结 comment |
| **部署验证** | API（由 CD 流水线调用） | 对新构建跑冒烟测试、扫描错误日志检查回归，在部署窗口关闭前向发布频道发送通过/不通过结论 |
| **文档漂移检测** | Schedule（每周） | 扫描上周合并的 PR，标记引用了已变更 API 的文档，向文档仓库开出更新 PR |
| **SDK 同步移植** | GitHub（`pull_request.closed`，筛选已合并 PR） | 将一种语言 SDK 的变更自动移植到另一种语言 SDK 仓库，开出对应 PR |

---

## 创建 Routine

**三种入口，统一云端账户：** 可以在 Web 端 [claude.ai/code/routines](https://claude.ai/code/routines)、桌面应用或 CLI 中创建。三个入口写入同一个云端账户，在一个入口创建的 routine 会立即出现在其他入口。在桌面应用中，点击侧边栏 **Routines** → **New routine** → 选 **Remote**；如果选 **Local** 则创建的是 [Desktop scheduled task](https://code.claude.com/docs/en/desktop-scheduled-tasks)，运行在本机而非云端。

创建表单需要设置 routine 的 prompt、仓库、环境、connectors 和触发器。

**Routine 以完整的 Claude Code 云会话方式自主运行：** 没有权限模式选择器，运行期间也没有审批弹窗。会话可以执行 shell 命令、使用仓库中提交的 [skills](https://code.claude.com/docs/en/skills)、调用你添加的任何 connector。Routine 的访问范围取决于：

- 你选择的仓库及其分支推送设置
- [环境](https://code.claude.com/docs/en/claude-code-on-the-web#the-cloud-environment) 的网络访问和变量
- 你添加的 connectors

每项都应限定为 routine 实际需要的最小范围。

**归属与身份：** Routine 归属于你的个人 claude.ai 账户，不会与队友共享，计入你账户的每日运行配额。Routine 通过你连接的 GitHub 身份或 connector 执行的任何操作都以你的身份呈现：commit 和 PR 显示你的 GitHub 用户名，Slack 消息、Linear ticket 等也使用你的关联账号。

### 从 Web 创建

**步骤 1：打开创建表单**

访问 [claude.ai/code/routines](https://claude.ai/code/routines) 并点击 **New routine**。

**步骤 2：命名并编写 Prompt**

为 routine 起一个描述性名称，编写 Claude 每次运行时执行的 prompt。Prompt 是最关键的部分：routine 自主运行，因此 prompt 必须自包含，明确说明要做什么以及成功的标准。

Prompt 输入框包含一个模型选择器，Claude 每次运行都使用你选定的模型。

**步骤 3：选择仓库**

添加一个或多个 GitHub 仓库供 Claude 工作。每个仓库在运行开始时从默认分支克隆，Claude 的变更会推送到 `claude/` 前缀的分支。

**步骤 4：选择环境**

选择一个 [云环境](https://code.claude.com/docs/en/claude-code-on-the-web#the-cloud-environment)。环境控制云会话可以访问的资源：

| 配置项 | 说明 |
| :--- | :--- |
| 网络访问 | 设置每次运行可用的互联网访问级别 |
| 环境变量 | 提供 API key、token 或其他 secret |
| Setup 脚本 | 安装 routine 需要的依赖和工具，结果会被 [缓存](https://code.claude.com/docs/en/claude-code-on-the-web#environment-caching)，不会每次都重新运行 |

默认提供一个 **Default** 环境，使用 **Trusted** 网络访问级别，允许 [默认列表](https://code.claude.com/docs/en/claude-code-on-the-web#default-allowed-domains) 中的包注册中心、云服务商 API、容器注册中心和常见开发域名，阻止其他所有域名。如果 routine 需要访问你自己的服务或列表外的域名，运行前先编辑环境的 [网络访问](https://code.claude.com/docs/en/claude-code-on-the-web#network-access) 设置。如需使用独立环境，先 [创建一个](https://code.claude.com/docs/en/claude-code-on-the-web#configure-your-environment)。

**步骤 5：选择触发器**

在 **Select a trigger** 下选择 routine 的启动方式，可以选一种也可以组合多种：

- **Schedule**：选择预设频率进行周期运行，或指定一个具体时间戳做一次性运行。详见 [添加 Schedule 触发器](#添加-schedule-触发器)。
- **GitHub event**：选择仓库、要响应的事件以及可选的过滤条件。详见 [添加 GitHub 触发器](#添加-github-触发器)。
- **API**：选择 API 后保存 routine，URL 和 token 在保存后生成（因为它们依赖 routine ID）。详见 [添加 API 触发器](#添加-api-触发器)。

**步骤 6：检查 Connectors 和 Permissions**

表单底部的 **Connectors** 和 **Permissions** 标签页控制 routine 的可达范围。

- **Connectors** 下，你连接的所有 [MCP connectors](https://code.claude.com/docs/en/mcp) 默认全部包含。移除 routine 不需要的。Claude 可以使用已包含 connector 的所有工具（包括写入），运行期间不会请求权限。
- **Permissions** 下，对需要 Claude 推送到非 `claude/` 前缀分支的仓库启用 **Allow unrestricted branch pushes**。

**步骤 7：创建**

点击 **Create**。Routine 出现在列表中，下次触发器匹配时即开始运行。如需立即启动一次，在 routine 详情页点击 **Run now**。

每次运行会创建一个新的会话，与你的其他会话并列，你可以查看 Claude 做了什么、审查变更并创建 Pull Request。

### 从 CLI 创建

**在任意会话中运行 `/schedule` 即可对话式创建定时 routine。** 你也可以直接传入描述，例如 `/schedule daily PR review at 9am`（周期性）或 `/schedule clean up feature flag in one week`（一次性）。Claude 会引导你完成与 Web 表单相同的信息收集，然后将 routine 保存到你的账户。

CLI 的 `/schedule` 只能创建定时 routine。添加 API 或 GitHub 触发器需要在 Web 端 [claude.ai/code/routines](https://claude.ai/code/routines) 编辑。

CLI 也支持管理已有 routine：运行 `/schedule list` 查看所有 routine，`/schedule update` 修改，`/schedule run` 立即触发。

---

## 配置触发器

**Routine 在其某个触发器匹配时启动。** 你可以在同一个 routine 上挂载任意组合的 schedule、API 和 GitHub 触发器，随时通过 routine 编辑表单的 **Select a trigger** 部分增减。

### 添加 Schedule 触发器

**Schedule 触发器按周期运行 routine，或在指定的未来时间运行一次。** 在 **Select a trigger** 中选择预设频率：hourly、daily、weekdays 或 weekly。时间按你的本地时区输入并自动转换，因此 routine 会在你指定的当地时间运行，无论云基础设施在哪里。

运行可能在计划时间后几分钟开始（由于错峰机制），每个 routine 的偏移量是固定的。

**自定义间隔：** 如需"每两小时"或"每月第一天"等自定义间隔，先在表单中选择最接近的预设，然后在 CLI 中运行 `/schedule update` 来设置具体的 cron 表达式。最小间隔为一小时，更频繁的表达式会被拒绝。

#### 一次性运行

**一次性 schedule 在指定时间戳触发 routine 一次。** 适合提醒自己、在 rollout 完成后开清理 PR、或在上游变更落地后启动后续任务。触发后 routine 自动禁用，Web UI 标记为 **Ran**。如需再次运行，编辑 routine 并设置新的一次性时间。

在 CLI 中用自然语言描述时间即可创建一次性运行。Claude 会根据当前时间解析表述，并在保存前确认绝对时间戳。

```text
/schedule tomorrow at 9am, summarize yesterday's merged PRs
```

```text
/schedule in 2 weeks, open a cleanup PR that removes the feature flag
```

一次性运行的时区转换规则与周期性 schedule 相同。

**一次性运行不计入每日 routine 运行上限。** 它们像普通会话一样消耗订阅用量，但不占用每账户每日 routine 运行配额。详见 [用量与限制](#用量与限制)。

### 添加 API 触发器

**API 触发器为 routine 提供一个专属 HTTP 端点。** 向该端点携带 bearer token 发送 POST 请求，即可启动新会话并返回会话 URL。用这种方式可以将 Claude Code 接入告警系统、部署流水线、内部工具——任何能发 HTTP 请求的地方。

API 触发器通过 Web 端添加到已有 routine。CLI 目前不支持创建或撤销 token。

**步骤 1：打开编辑表单**

前往 [claude.ai/code/routines](https://claude.ai/code/routines)，点击要通过 API 触发的 routine，再点击铅笔图标打开 **Edit routine**。

**步骤 2：添加 API 触发器**

滚动到 **Instructions** 框下方的 **Select a trigger** 部分，点击 **Add another trigger**，选择 **API**。

**步骤 3：复制 URL 并生成 Token**

弹窗会显示该 routine 的 URL 和示例 curl 命令。复制 URL，然后点击 **Generate token** 并立即复制 token。Token 只显示一次且无法再次获取，请妥善保存（如存入告警工具的 secret store）。

**步骤 4：调用端点**

POST 请求时在 `Authorization: Bearer` header 中携带 token。完整示例见下方 [触发 Routine](#触发-routine)。

每个 routine 有自己的 token，仅限触发该 routine。如需轮换或吊销，回到同一弹窗点击 **Regenerate** 或 **Revoke**。

#### 触发 Routine

向 `/fire` 端点发送 POST 请求，在 `Authorization` header 中携带 bearer token。请求体接受一个可选的 `text` 字段，用于传递运行时上下文（如告警正文或失败日志），该内容会连同保存的 prompt 一起传给 routine。`text` 的值是自由文本，不会被解析：即使你发送 JSON 或其他结构化数据，routine 收到的也是原始字符串。

示例——从 shell 触发一个 routine：

```bash
curl -X POST https://api.anthropic.com/v1/claude_code/routines/trig_01ABCDEFGHJKLMNOPQRSTUVW/fire \
  -H "Authorization: Bearer sk-ant-oat01-xxxxx" \
  -H "anthropic-beta: experimental-cc-routine-2026-04-01" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"text": "Sentry alert SEN-4521 fired in prod. Stack trace attached."}'
```

成功时返回包含新会话 ID 和 URL 的 JSON：

```json
{
  "type": "routine_fire",
  "claude_code_session_id": "session_01HJKLMNOPQRSTUVWXYZ",
  "claude_code_session_url": "https://claude.ai/code/session_01HJKLMNOPQRSTUVWXYZ"
}
```

在浏览器中打开 session URL 可以实时观看运行过程、审查变更或手动继续对话。

> [!WARNING]
> `/fire` 端点目前在 `experimental-cc-routine-2026-04-01` beta header 下提供。研究预览期间，请求/响应格式、速率限制和 token 语义可能变更。破坏性变更会放在新的带日期 beta header 版本后面，最近的两个旧版本继续有效，给调用方迁移时间。

#### API 参考

完整的 API 参考（包含所有错误响应、校验规则和字段限制）见 Claude Platform 文档中的 [Trigger a routine via API](https://platform.claude.com/docs/en/api/claude-code/routines-fire)。

`/fire` 端点仅面向 claude.ai 用户，不属于 Claude Platform API。

### 添加 GitHub 触发器

**GitHub 触发器在连接仓库上发生匹配事件时自动启动新会话。** 每个匹配的事件都会启动独立的会话。

> [!NOTE]
> 研究预览期间，GitHub webhook 事件受每 routine 和每账户的小时级上限约束。超出限制的事件会被丢弃，直到窗口重置。在 [claude.ai/code/routines](https://claude.ai/code/routines) 查看你当前的限额。

GitHub 触发器只能在 Web UI 中配置。

**步骤 1：打开编辑表单**

前往 [claude.ai/code/routines](https://claude.ai/code/routines)，点击 routine，再点击铅笔图标打开 **Edit routine**。

**步骤 2：添加 GitHub event 触发器**

滚动到 **Select a trigger** 部分，点击 **Add another trigger**，选择 **GitHub event**。

**步骤 3：安装 Claude GitHub App**

你要订阅的仓库必须安装了 Claude GitHub App。如果尚未安装，触发器设置会引导你完成安装。

> [!NOTE]
> 在 CLI 中运行 `/web-setup` 会授予仓库克隆权限，但不会安装 Claude GitHub App，也不会开启 webhook 推送。GitHub 触发器需要安装 Claude GitHub App，触发器设置会提示你安装。

**步骤 4：配置触发器**

选择仓库，从 [支持的事件](#支持的事件) 列表中选择事件，可选添加过滤条件，然后保存触发器。

#### 支持的事件

GitHub 触发器可以订阅以下事件类别。在每个类别内你可以选择具体的 action（如 `pull_request.opened`），也可以响应该类别下的所有 action。

| 事件 | 触发条件 |
| :--- | :--- |
| Pull request | PR 被打开、关闭、指派、加标签、同步或其他更新 |
| Release | Release 被创建、发布、编辑或删除 |

#### 过滤 Pull Request

**使用过滤器缩小启动会话的 PR 范围。** 所有过滤条件必须同时满足 routine 才会触发。可用的过滤字段：

| 过滤字段 | 匹配对象 |
| :--- | :--- |
| Author | PR 作者的 GitHub 用户名 |
| Title | PR 标题文本 |
| Body | PR 描述文本 |
| Base branch | PR 目标分支 |
| Head branch | PR 来源分支 |
| Labels | PR 上的标签 |
| Is draft | PR 是否为草稿状态 |
| Is merged | PR 是否已合并 |

每个过滤器将字段与运算符配对：equals、contains、starts with、is one of、is not one of 或 matches regex。

**`matches regex` 运算符对整个字段值进行匹配，而非子串匹配。** 要匹配任何包含 `hotfix` 的标题，应写 `.*hotfix.*`。如果不加前后的 `.*`，则只匹配标题恰好为 `hotfix` 且前后无其他内容的情况。如果只需要字面子串匹配，用 `contains` 运算符更合适。

几个过滤组合示例：

| 场景 | 过滤条件 | 效果 |
| :--- | :--- | :--- |
| Auth 模块审查 | base branch 为 `main`，head branch contains `auth-provider` | 将涉及认证的 PR 发给专项 reviewer |
| 仅非草稿 | is draft 为 `false` | 跳过草稿，仅在 PR ready for review 时运行 |
| 标签门控的 backport | labels 包含 `needs-backport` | 仅当维护者打上标签时触发另一分支的移植 |

#### 事件与会话的映射关系

**每个匹配的 GitHub 事件启动一个新会话。** GitHub 触发的 routine 不支持跨事件复用会话，两次 PR 更新会产生两个独立会话。

---

## 管理 Routine

点击列表中的 routine 打开详情页，可查看仓库、connectors、prompt、schedule、API token、GitHub 触发器以及历史运行列表。

### 查看和交互运行记录

**点击任何一次运行即可打开为完整会话。** 在会话中可以看到 Claude 做了什么、审查变更、创建 Pull Request 或继续对话。每次运行的会话与普通会话一样，可通过会话标题旁的下拉菜单重命名、归档或删除。

> [!NOTE]
> 运行列表中的绿色状态表示会话已启动并正常退出，没有基础设施层面的错误。这并不意味着 prompt 中的任务成功完成。请打开运行记录阅读对话内容以确认 Claude 实际做了什么。网络请求被阻止、connector 工具缺失、任务级失败等问题都会在对话中体现，而不是在状态指示器中。

### 编辑和控制 Routine

在详情页你可以：

| 操作 | 说明 |
| :--- | :--- |
| **Run now** | 立即启动一次运行，不等待下次计划时间 |
| **Repeats 开关** | 暂停或恢复 schedule。暂停后配置保留但不运行，恢复后继续 |
| **Edit routine（铅笔图标）** | 修改名称、prompt、仓库、环境、connectors 或任何触发器 |
| **Delete（删除图标）** | 移除 routine。该 routine 此前创建的会话保留在你的会话列表中 |

### 仓库与分支权限

**Routine 需要 GitHub 访问权限来克隆仓库。** 从 CLI 用 `/schedule` 创建时，Claude 会检查你的账户是否已连接 GitHub，如未连接会提示运行 `/web-setup`。详见 [GitHub 认证选项](https://code.claude.com/docs/en/claude-code-on-the-web#github-authentication-options)。

每个添加的仓库在每次运行时都会被克隆。除非你的 prompt 另有指定，Claude 从仓库的默认分支开始工作。

**默认情况下 Claude 只能推送到 `claude/` 前缀的分支。** 这防止 routine 意外修改受保护或长期存在的分支。如需取消限制，在创建或编辑 routine 时为对应仓库启用 **Allow unrestricted branch pushes**。

### Connectors

**Routine 可以使用你连接的 MCP connectors 在运行期间读写外部服务。** 例如，一个分流支持请求的 routine 可能从 Slack 频道读取消息并在 Linear 中创建 issue。

Connectors 是你 claude.ai 账户上的 [集成](https://code.claude.com/docs/en/mcp#use-mcp-servers-from-claude-ai)。在 CLI 中用 `claude mcp add` 添加的 MCP server 存储在本机而非 claude.ai 账户中，因此不会出现在 connectors 列表里。要在 routine 中使用这些 server，请到 [claude.ai/customize/connectors](https://claude.ai/customize/connectors) 将其添加为 connector，或在提交到仓库的 [`.mcp.json`](https://code.claude.com/docs/en/mcp#project-scope) 中声明。

创建 routine 时，你当前连接的所有 connectors 默认全部包含。移除不需要的，以限制 Claude 在运行期间可访问的工具。你也可以直接在 routine 表单中添加 connector。

要在 routine 表单之外管理或添加 connectors，访问 claude.ai 的 **Settings > Connectors**，或在 CLI 中使用 `/schedule update`。

### 环境与网络访问

**每个 routine 运行在一个 [云环境](https://code.claude.com/docs/en/claude-code-on-the-web#the-cloud-environment) 中，** 该环境控制网络访问、环境变量和 setup 脚本。Routine 在每次运行时继承环境的网络策略。

**Default** 环境使用 **Trusted** 网络访问级别：可达 [默认白名单](https://code.claude.com/docs/en/claude-code-on-the-web#default-allowed-domains) 中的包注册中心、云服务商 API、容器注册中心和常见开发域名，但无法访问任意域名。对其他主机的出站请求会以 `403` 和 `x-deny-reason: host_not_allowed` 被拒绝。MCP connector 流量通过 Anthropic 服务器路由，因此你添加到 routine 的 connectors 无需额外配置域名即可正常工作。移除不需要的 connectors，见 [Connectors](#connectors)。

**允许额外域名的步骤：**

1. 在 routine 详情页点击铅笔图标打开 **Edit routine**。
2. 在 **Instructions** 框下方点击显示环境名称（如 **Default**）的云图标。
3. 将鼠标悬停在列表中的环境上，点击右侧出现的设置图标。
4. 在 **Update cloud environment** 对话框中，将 **Network access** 改为 **Custom**，在 **Allowed domains** 中输入你的域名。勾选 **Also include default list of common package managers** 可在自定义域名之外保留 [默认白名单](https://code.claude.com/docs/en/claude-code-on-the-web#default-allowed-domains)。选择 **Full** 则完全不限制访问。
5. 点击 **Save changes**，新策略从下次运行生效。

更多信息见 [Network access](https://code.claude.com/docs/en/claude-code-on-the-web#network-access)。

---

## 用量与限制

**Routine 与交互式会话消耗相同的订阅用量。** 除标准订阅限制外，routine 还有每账户每日运行次数上限。在 [claude.ai/code/routines](https://claude.ai/code/routines) 或 [claude.ai/settings/usage](https://claude.ai/settings/usage) 查看当前消耗和剩余每日 routine 运行次数。

当 routine 达到每日上限或订阅用量限制时，启用了 usage credits 的组织可以继续以计量超额方式运行 routine。未启用 usage credits 的情况下，额外运行会被拒绝直到窗口重置。在 claude.ai 的 **Settings > Billing** 开启 usage credits。

**一次性运行不计入每日 routine 上限。** 它们像普通会话一样消耗订阅用量，但不占用每账户每日 routine 运行配额。

---

## 故障排除

### `/schedule` 提示 "No commands match" 或 "Unknown command"

**CLI 在某些条件不满足时会隐藏 `/schedule` 命令，** 导致命令菜单显示 `No commands match "/schedule"`，提交后返回 `Unknown command: /schedule`。通常原因是：

| 原因 | 解决方法 |
| :--- | :--- |
| 使用了 Console API key 或云服务商（Bedrock、Vertex、Foundry）认证 | `/schedule` 要求 claude.ai 订阅登录。如果 shell 中设置了 `ANTHROPIC_API_KEY` 或 `ANTHROPIC_AUTH_TOKEN`，或 `settings.json` 中设置了 `apiKeyHelper`，先移除它们（这些优先于 claude.ai 登录） |
| 环境中设置了 `DISABLE_TELEMETRY`、`DO_NOT_TRACK`、`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` 或 `DISABLE_GROWTHBOOK` | 这些会禁用 feature flag 获取，而 `/schedule` 依赖它。在 shell 环境或 [`settings.json`](https://code.claude.com/docs/en/settings#available-settings) 的 `env` 块中移除 |
| 在 Claude Code on the web 会话中 | 改用 [Web UI](https://claude.ai/code/routines) 管理 routine |
| CLI 版本低于 v2.1.81 | 运行 `claude update` |

无论 CLI 如何配置，你始终可以在 [claude.ai/code/routines](https://claude.ai/code/routines) 创建和管理 routine。

### "Routines are disabled by your organization's policy"

**你所在的 Team 或 Enterprise 组织的 Owner 可能关闭了 Routines 开关**（位于 [claude.ai/admin-settings/claude-code](https://claude.ai/admin-settings/claude-code)）。这是服务器端的组织设置，无法通过本地配置覆盖。请联系 Owner 为你的组织启用 routines。

---

## 相关资源

- [`/loop` 和会话内调度](https://code.claude.com/docs/en/scheduled-tasks)：在打开的 CLI 会话中调度本地任务
- [桌面定时任务](https://code.claude.com/docs/en/desktop-scheduled-tasks)：在本机运行的本地定时任务，可访问本地文件
- [云环境](https://code.claude.com/docs/en/claude-code-on-the-web#the-cloud-environment)：配置云会话的运行环境
- [MCP connectors](https://code.claude.com/docs/en/mcp)：连接 Slack、Linear、Google Drive 等外部服务
- [GitHub Actions](https://code.claude.com/docs/en/github-actions)：在 CI 流水线中响应仓库事件运行 Claude
