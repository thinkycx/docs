---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】更新日志
description: Claude Code 的版本发布说明，包含各版本的新功能、改进和 bug 修复。本页从 GitHub CHANGELOG.md 生成。
category: translation
tags: [claude-code, changelog, translation]
refs:
  - https://code.claude.com/docs/en/changelog.md
  - en-source/changelog.md
---

# Claude Code 更新日志

**各版本的新功能、改进和 bug 修复。** 本页从 [GitHub 上的 CHANGELOG.md](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) 生成。

运行 `claude --version` 检查你的安装版本。

> 注：以下仅翻译核心改动要点。完整详细内容请参阅原文。

## 2.1.202 (2026-07-06)

- 新增 `/config` 中的 "Dynamic workflow size" 设置，控制动态工作流 agent 数量
- 新增 `workflow.run_id` 和 `workflow.name` OpenTelemetry 属性
- 修复内联 Ctrl+R 历史搜索崩溃
- 修复 `/rename` 在后台会话上被还原
- 修复重复调用已加载 skill 时追加重复指令到上下文
- `/review <pr>` 改回快速单次审查；多 agent 审查用 `/code-review <level> <pr#>`

## 2.1.201 (2026-07-03)

- Claude Sonnet 5 会话不再在对话中段使用 system role 做 harness reminder

## 2.1.200 (2026-07-03)

- `AskUserQuestion` 对话框不再默认自动继续
- "default" 权限模式在 CLI、VS Code、JetBrains 中统一重命名为 "Manual"
- 修复后台会话在 sleep/wake 后静默停止

## 2.1.199 (2026-07-02)

- 堆叠斜杠技能调用如 `/skill-a /skill-b do XYZ` 现在加载所有前导技能（最多 5 个）
- SSL 证书错误现在立即失败并给出修复提示，不再浪费重试
- 流式响应在 API 中段错误后保留部分输出
- 修复后台 agent daemon 在 Linux 上每 ~50 秒杀死自己

## 2.1.198 (2026-07-01)

- **Subagents 默认后台运行**——Claude 继续工作，完成时通知
- **Claude in Chrome 正式可用**
- 新增 `/dataviz` 技能
- Gateway 新增 Claude Platform on AWS 作为上游 provider
- 后台 agent 完成代码工作后自动 commit、push 并开 draft PR
- 修复短暂网络断开导致整轮中止

## 2.1.197 (2026-06-30)

- **发布 Claude Sonnet 5**：Claude Code 默认模型，原生 1M token 上下文窗口，促销价 $2/$10 per Mtok（至 8 月 31 日）

## 2.1.196 (2026-06-29)

- 新增组织默认模型支持
- 新增会话可读默认名称
- 安全：`claude mcp list`/`get` 不再启动未批准的 `.mcp.json` 服务器
- 修复唤醒后台任务时永久删除对话
- 流式空闲看门狗默认开启所有 provider

## 2.1.195 (2026-06-26)

- 新增 `CLAUDE_CODE_DISABLE_MOUSE_CLICKS` 禁用全屏模式鼠标点击
- 修复 hook matcher 带连字符标识符意外子串匹配

## 2.1.193 (2026-06-25)

- 新增 `autoMode.classifyAllShell` 设置
- 新增 auto-mode 拒绝原因到 transcript
- 新增 `claude_code.assistant_response` OpenTelemetry 日志事件
- 新增 bash 模式文件路径自动补全
- 自动修剪空闲后台 shell 命令的内存

## 2.1.191 (2026-06-24)

- 新增 `/rewind` 支持从 `/clear` 之前恢复
- 修复流式响应时滚动位置跳到底部
- 修复后台 agent 被停止后复活

## 2.1.187 (2026-06-23)

- 新增 `sandbox.credentials` 设置阻止沙箱命令读取凭据
- 新增组织配置的模型限制
- 新增全屏模式鼠标点击支持选择菜单
- `!` bash 命令现在自动触发 Claude 响应

## 2.1.186 (2026-06-22)

- 新增 `claude mcp login/logout` CLI 命令
- 新增 `/plugin` Installed 标签的 "Skills" 部分
- `/review <pr>` 改用与 `/code-review medium` 相同的审查引擎

## 2.1.183 (2026-06-19)

- **改进 auto mode 安全**：破坏性 git 命令被阻止（`git reset --hard`、`git checkout -- .` 等）
- `git commit --amend` 被阻止（除非是 agent 本会话的提交）
- `terraform destroy`/`pulumi destroy`/`cdk destroy` 被阻止（除非用户明确要求）

## 2.1.181 (2026-06-17)

- 新增 `/config key=value` 语法
- 新增 `sandbox.allowAppleEvents` 设置
- 新增 `CLAUDE_CLIENT_PRESENCE_FILE` 环境变量
- 升级内置 Bun 运行时到 1.4
- 改进长段落流式输出：逐行显示

## 2.1.178 (2026-06-15)

- Agent teams：移除 `TeamCreate`/`TeamDelete` 工具，每个会话现有一个隐式 team
- 新增 `Tool(param:value)` 权限规则语法
- 嵌套 `.claude/skills` 目录现在在处理那里的文件时加载

## 2.1.176 (2026-06-12)

- 会话标题现在用对话语言生成
- 新增 `footerLinksRegexes` 设置
- 修复 prompt caching 在自定义 `ANTHROPIC_BASE_URL` 和 Foundry 上不读取

---

> 本文仅列出近期重要版本亮点。完整更新日志请参阅 [原文](https://code.claude.com/docs/en/changelog.md) 或 [GitHub CHANGELOG.md](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)。
