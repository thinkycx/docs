# 子 Agent 系统

子 Agent（Subagent）允许将复杂任务分解为多个专注于特定领域的 Agent，每个子 Agent 拥有独立的工具集和提示词，由主 Agent 通过 Agent 工具按需调用。

## AgentDefinition 数据类

```python
from dataclasses import dataclass

@dataclass
class AgentDefinition:
    name: str | None = None              # Agent 名称（可选，默认使用 key）
    description: str = ""                # Agent 描述，告诉主 Agent 何时调用
    prompt: str = ""                     # Agent 的系统提示词
    tools: list[str] | None = None       # 可用工具列表
    model: str | None = None             # 模型选择: "sonnet" / "opus" / "haiku"
    allowed_tools: list[str] | None = None     # 允许的工具（glob 模式）
    disallowed_tools: list[str] | None = None  # 禁止的工具（glob 模式）
    mcp_servers: dict | None = None      # 子 Agent 专用 MCP 服务器配置
    permission_mode: str | None = None   # 权限模式覆盖
    max_turns: int | None = None         # 最大对话轮数限制
```

## 配置子 Agent

通过 `ClaudeAgentOptions` 的 `agents` 参数注册子 Agent：

```python
from claude_agent_sdk import ClaudeAgentOptions, AgentDefinition

options = ClaudeAgentOptions(
    prompt="你是一个全栈开发助手，可以调用专门的子 Agent 完成特定任务。",
    agents={
        "reviewer": AgentDefinition(
            description="代码审查专家，负责检查代码质量、安全性和最佳实践",
            prompt="""你是一个严格的代码审查员。
检查以下方面：
- 代码风格和一致性
- 潜在的 bug 和边界情况
- 安全漏洞
- 性能问题
- 测试覆盖率""",
            tools=["Read", "Bash"],
            model="opus",
            max_turns=10,
        ),
        "docs_writer": AgentDefinition(
            description="文档撰写专家，负责生成 API 文档和使用说明",
            prompt="你是一个技术文档撰写专家，生成清晰、准确的文档。",
            tools=["Read", "Write", "Edit"],
            model="sonnet",
        ),
        "test_writer": AgentDefinition(
            description="测试用例编写专家，负责编写单元测试和集成测试",
            prompt="你是一个测试工程师，擅长编写全面的测试用例。使用 pytest 框架。",
            tools=["Read", "Write", "Edit", "Bash"],
            allowed_tools=["Bash(pytest *)", "Bash(python -m pytest *)"],
            model="sonnet",
        ),
    },
)
```

## 主 Agent 如何调用子 Agent

主 Agent 在对话过程中通过内置的 **Agent 工具** 按名称调用子 Agent。SDK 自动向主 Agent 注册该工具，主 Agent 根据任务描述自动选择合适的子 Agent：

```
用户: "请审查 src/auth.py 的代码并编写相应的测试"

主 Agent 思考: 需要先调用 reviewer 审查代码，再调用 test_writer 编写测试

主 Agent 调用: Agent(name="reviewer", task="审查 src/auth.py 的代码质量和安全性")
  → reviewer 子 Agent 执行审查，返回结果

主 Agent 调用: Agent(name="test_writer", task="为 src/auth.py 编写单元测试")
  → test_writer 子 Agent 编写测试
```

子 Agent 的调用对用户透明，在消息流中体现为 `ToolUseBlock(tool_name="Agent", ...)` 和对应的 `ToolResultBlock`。

## 文件系统 Agent

除了通过代码定义，还可以通过文件系统定义 Agent：

```
.claude/agents/
├── reviewer.md
├── docs-writer.md
└── test-writer.md
```

每个 `.md` 文件的内容即为该 Agent 的 prompt，文件名作为 Agent 名称。

要加载文件系统 Agent，需要在 `setting_sources` 中包含 `"project"`：

```python
options = ClaudeAgentOptions(
    setting_sources=["project"],  # 加载 .claude/ 目录下的配置
    # 代码定义的 agents 和文件系统 agents 可以共存
    agents={
        "extra_agent": AgentDefinition(...)
    },
)
```

文件系统 Agent 示例（`.claude/agents/reviewer.md`）：

```markdown
---
description: 代码审查专家
tools:
  - Read
  - Bash
model: opus
max_turns: 10
---

你是一个严格的代码审查员。
检查代码的质量、安全性和最佳实践。
```

## 继承与隔离

### 子 Agent 从父 Agent 继承：

- **会话上下文** — 子 Agent 可以看到父 Agent 传递的任务描述
- **文件系统访问** — 同一个工作目录
- **环境变量** — 继承父进程的环境
- **Session 归属** — 子 Agent 的消息记录在父 Session 的子路径下

### 子 Agent 不继承：

- **工具集** — 仅限于 `tools` / `allowed_tools` 中定义的工具
- **系统提示词** — 使用自己的 `prompt`
- **MCP 服务器** — 需要通过 `mcp_servers` 单独配置
- **模型** — 可以使用不同的模型
- **权限模式** — 可以通过 `permission_mode` 覆盖

## 并行化与上下文隔离

子 Agent 系统的核心优势：

1. **任务并行** — 主 Agent 可以同时调用多个子 Agent 处理不同文件
2. **上下文隔离** — 每个子 Agent 有独立的对话上下文，不会相互污染
3. **专注性** — 子 Agent 的 prompt 和工具集聚焦于特定任务，减少干扰
4. **成本控制** — 可以为不同子 Agent 选择不同模型（简单任务用 haiku，复杂任务用 opus）

```python
# 主 Agent 可以并行调用多个子 Agent
# Claude 会自动判断何时可以并行调用
options = ClaudeAgentOptions(
    prompt="你是项目管理 Agent。当需要同时处理多个文件时，并行调用相关子 Agent。",
    agents={
        "frontend_dev": AgentDefinition(
            description="前端开发，处理 React/TypeScript 文件",
            prompt="你是前端专家，使用 React + TypeScript。",
            tools=["Read", "Write", "Edit", "Bash"],
            allowed_tools=["Bash(npm *)", "Bash(npx *)"],
            model="sonnet",
        ),
        "backend_dev": AgentDefinition(
            description="后端开发，处理 Python/FastAPI 文件",
            prompt="你是后端专家，使用 Python + FastAPI。",
            tools=["Read", "Write", "Edit", "Bash"],
            allowed_tools=["Bash(python *)", "Bash(pytest *)"],
            model="sonnet",
        ),
        "devops": AgentDefinition(
            description="DevOps 工程师，处理 Docker/CI 配置",
            prompt="你是 DevOps 专家，管理部署和 CI/CD。",
            tools=["Read", "Write", "Edit", "Bash"],
            model="haiku",
            max_turns=5,
        ),
    },
)
```

## 完整示例：代码审查 + 文档生成流水线

```python
import anyio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AgentDefinition,
    AssistantMessage,
    TextBlock,
)

async def main():
    options = ClaudeAgentOptions(
        prompt="""你是一个项目管理 Agent。收到用户的代码变更后：
1. 先调用 reviewer 进行代码审查
2. 如果审查通过，调用 docs_writer 更新文档
3. 最后汇总报告""",
        agents={
            "reviewer": AgentDefinition(
                description="代码审查，检查质量和安全性",
                prompt="""严格审查代码：
- 检查逻辑错误和边界情况
- 识别安全漏洞
- 评估代码可读性
审查完成后输出 PASS 或 FAIL 及详细原因。""",
                tools=["Read", "Bash"],
                model="opus",
                max_turns=8,
            ),
            "docs_writer": AgentDefinition(
                description="根据代码变更更新 API 文档",
                prompt="""根据代码变更生成或更新文档：
- 更新函数签名和参数说明
- 添加使用示例
- 维护 CHANGELOG""",
                tools=["Read", "Write", "Edit"],
                model="sonnet",
                max_turns=5,
            ),
        },
        allowed_tools=["Read", "Agent"],
        permission_mode="bypassPermissions",
    )

    async with ClaudeSDKClient(options) as client:
        await client.query("请审查 src/api/auth.py 的最近改动并更新文档")

        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

anyio.run(main)
```

## 子 Agent 的 max_turns 限制

`max_turns` 控制子 Agent 的最大对话轮数，防止子 Agent 陷入无限循环：

```python
AgentDefinition(
    description="简单查询 Agent",
    prompt="回答用户问题",
    tools=["Read"],
    max_turns=3,  # 最多 3 轮对话后强制返回
)
```

当子 Agent 达到 max_turns 限制时，其当前累积的输出会返回给主 Agent，主 Agent 可以决定是否需要进一步处理。

## 注意事项

- 子 Agent 的 `description` 非常重要，主 Agent 依据描述决定何时调用哪个子 Agent
- 子 Agent 名称（字典 key）建议使用小写字母和下划线，避免特殊字符
- 嵌套调用：子 Agent 本身也可以定义 `agents`，但要注意避免循环调用
- 文件系统 Agent 和代码定义的 Agent 名称冲突时，代码定义优先
- `tools` 参数定义可用工具列表，`allowed_tools` 进一步用 glob 模式限制参数
