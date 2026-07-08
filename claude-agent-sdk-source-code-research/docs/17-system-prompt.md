# System Prompt 配置

## 概述

`system_prompt` 参数控制模型的行为指令。Claude Agent SDK 提供三种配置模式，从完全自定义到复用 Claude Code 的默认能力，适应不同场景。

## 三种配置模式

### 模式 1：字符串（完全替换）

直接传入字符串，完全替换默认的 system prompt：

```python
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(
    system_prompt="你是一个专业的代码审查助手。只关注安全漏洞和性能问题。用中文回答。",
)

async for msg in query(prompt="审查这段代码", options=options):
    pass
```

**特点：**
- 完全控制模型行为
- 不包含 Claude Code 的默认指令（工具使用规范、安全准则等）
- 适合：简单问答、不需要工具的场景、有严格提示词要求的应用

### 模式 2：预设（使用 Claude Code 默认 prompt）

使用 `claude_code` 预设，获得 Claude Code 的完整默认能力：

```python
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(
    system_prompt={"type": "preset", "preset": "claude_code"},
)

async for msg in query(prompt="修复这个 bug", options=options):
    pass
```

**特点：**
- 包含 Claude Code 的全套默认指令
- 工具使用规范（何时用 Bash、何时用 Edit 等）
- 安全准则和最佳实践
- 适合：需要完整 Claude Code 能力的编码代理

### 模式 3：预设 + 追加（扩展默认 prompt）

在 Claude Code 默认 prompt 基础上追加自定义指令：

```python
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(
    system_prompt={
        "type": "preset",
        "preset": "claude_code",
        "append": """
额外要求：
1. 所有代码注释使用中文
2. 优先使用 Python 3.12+ 特性
3. 遵循 Google Python 风格指南
4. 每个函数必须有 docstring
""",
    },
)

async for msg in query(prompt="重构这个模块", options=options):
    pass
```

**特点：**
- 保留 Claude Code 的全部默认能力
- 在此基础上添加项目/团队/场景特定指令
- 适合：大多数生产场景，既要工具能力又要定制行为

### 不设置（None）

当 `system_prompt` 为 `None`（默认值）时，使用最小化的系统提示：

```python
options = ClaudeAgentOptions(
    system_prompt=None,  # 默认值
)
```

这相当于"原始 Claude"模式，没有 Claude Code 的工具使用指引。

## 与 CLAUDE.md 的交互

当 `setting_sources` 包含 `"project"` 时，SDK 会自动加载工作目录中的 CLAUDE.md 文件：

```python
options = ClaudeAgentOptions(
    system_prompt={"type": "preset", "preset": "claude_code"},
    setting_sources=["user", "project"],  # 加载 CLAUDE.md
    cwd="/path/to/project",
)
```

CLAUDE.md 的内容会被注入到系统上下文中，类似于 `append`，但由项目维护而非代码硬编码。

### CLAUDE.md 加载规则

- `setting_sources` 包含 `"project"` → 加载 `{cwd}/.claude/CLAUDE.md` 和 `{cwd}/CLAUDE.md`
- `setting_sources` 包含 `"user"` → 加载 `~/.claude/CLAUDE.md`
- `setting_sources` 为 `[]` → 不加载任何 CLAUDE.md

## 选择指南

| 场景 | 推荐模式 | 理由 |
|------|----------|------|
| 简单问答机器人 | 字符串 | 不需要工具，完全控制行为 |
| 代码编辑代理 | 预设 + 追加 | 需要工具规范，加上业务定制 |
| 复刻 Claude Code 体验 | 预设 | 完整的 Claude Code 行为 |
| 安全评审工具 | 字符串 | 严格限定角色和输出格式 |
| 多项目通用代理 | 预设 + CLAUDE.md | 通过 CLAUDE.md 适配各项目 |
| API 封装/转发 | None | 最小化干预 |

## 实战示例

### 代码审查代理

```python
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(
    system_prompt={
        "type": "preset",
        "preset": "claude_code",
        "append": """
你是一个代码审查代理。审查规则：
1. 检查安全漏洞（SQL注入、XSS、SSRF等）
2. 检查性能问题（N+1查询、内存泄漏）
3. 检查代码风格一致性
4. 输出格式：严重程度(P0-P3) + 文件:行号 + 问题描述 + 修复建议
5. 不要自动修改代码，只报告问题
""",
    },
    tools=["Read", "Bash"],  # 只需要读取能力
    allowed_tools=["Read", "Bash(find *)", "Bash(git *)"],
)
```

### 文档生成器

```python
options = ClaudeAgentOptions(
    system_prompt="""你是一个技术文档生成器。

要求：
- 使用中文撰写
- 包含概述、参数说明、返回值、示例代码
- 示例代码必须可运行
- 使用 Markdown 格式
- 函数签名使用代码块

输出纯 Markdown 文本，不执行任何工具。""",
    tools=[],  # 禁用所有工具
)
```

### 交互式编程助手

```python
options = ClaudeAgentOptions(
    system_prompt={
        "type": "preset",
        "preset": "claude_code",
        "append": """
交互规范：
- 修改代码前先解释方案
- 每次最多修改 3 个文件
- 修改后自动运行相关测试
- 如果测试失败，立即回滚并报告
""",
    },
    setting_sources=["user", "project"],  # 加载项目 CLAUDE.md
)
```

## 注意事项

1. **字符串模式下工具使用不稳定** — 如果启用了工具但用字符串替换了 system prompt，模型可能不知道如何正确使用工具（缺少使用规范）。建议搭配 `tools=[]` 或使用预设模式。

2. **预设内容可能随版本更新** — `claude_code` 预设的具体内容由 CLI 版本决定，升级 CLI 可能改变默认行为。

3. **`append` 不会覆盖默认指令** — 如果 append 的内容与预设冲突，模型会尝试平衡两者。如需完全覆盖，使用字符串模式。

4. **system_prompt 长度影响成本** — 系统提示占用 input tokens。`claude_code` 预设本身较长，追加内容会进一步增加成本。

5. **CLAUDE.md 优先级** — 在预设 + 追加模式下，最终上下文顺序为：预设指令 → CLAUDE.md 内容 → append 内容。
