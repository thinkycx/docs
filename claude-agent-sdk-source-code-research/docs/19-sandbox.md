# 沙盒与安全

## 概述

Claude Agent SDK 提供多层安全机制来隔离代理的执行环境。核心理念是**纵深防御**：沙盒设置、权限模式、文件系统隔离、网络控制和 Hook 约束层层叠加，确保代理行为可控。

## SandboxSettings

`SandboxSettings` dataclass 控制沙盒的整体行为：

```python
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(
    sandbox={
        "enabled": True,
        "auto_allow": False,
        "network": {
            "enabled": True,
            "allow_list": ["api.example.com", "*.internal.corp"],
        },
        "ignore_violations": {
            "paths": ["/tmp/cache"],
        },
    },
)

async for msg in query(prompt="处理数据", options=options):
    pass
```

### 参数详解

| 参数 | 类型 | 说明 |
|------|------|------|
| `enabled` | `bool` | 是否启用沙盒隔离 |
| `auto_allow` | `bool` | 是否自动批准沙盒内的安全操作 |
| `network` | `SandboxNetworkConfig` | 网络访问控制 |
| `ignore_violations` | `SandboxIgnoreViolations` | 忽略特定路径的违规 |

## SandboxNetworkConfig

控制代理的网络访问权限：

```python
# 完全禁止网络访问
options = ClaudeAgentOptions(
    sandbox={
        "enabled": True,
        "network": {
            "enabled": False,  # 禁用所有网络
        },
    },
)

# 仅允许特定域名
options = ClaudeAgentOptions(
    sandbox={
        "enabled": True,
        "network": {
            "enabled": True,
            "allow_list": [
                "api.github.com",
                "registry.npmjs.org",
                "*.amazonaws.com",
            ],
        },
    },
)
```

### 网络配置字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `enabled` | `bool` | 是否允许网络访问 |
| `allow_list` | `list[str]` | 允许访问的域名列表，支持通配符 |

## SandboxIgnoreViolations

配置哪些路径的访问不被视为违规：

```python
options = ClaudeAgentOptions(
    sandbox={
        "enabled": True,
        "ignore_violations": {
            "paths": [
                "/tmp",           # 临时文件
                "/var/cache",     # 缓存目录
            ],
        },
    },
)
```

## 权限模式（permission_mode）

`permission_mode` 决定工具调用时的权限确认策略：

```python
from claude_agent_sdk import query, ClaudeAgentOptions

# 默认模式 — 通过 allowed_tools 列表控制
options = ClaudeAgentOptions(
    permission_mode="default",
    allowed_tools=["Read", "Bash(ls *)"],
)

# 接受所有 — 自动批准所有工具调用（危险！仅限测试环境）
options = ClaudeAgentOptions(
    permission_mode="acceptall",
)

# 拒绝所有未明确允许的 — 最严格模式
options = ClaudeAgentOptions(
    permission_mode="bypassaliases",
)
```

### permission_mode 选项

| 模式 | 行为 | 适用场景 |
|------|------|----------|
| `"default"` | 按 allowed_tools 列表批准，其他需确认 | 开发环境 |
| `"acceptall"` | 自动批准所有工具调用 | 测试环境、全信任场景 |
| `"bypassaliases"` | 忽略别名配置，严格匹配 | 高安全要求 |

## 文件系统隔离

### cwd（工作目录）

代理的操作限定在工作目录内：

```python
options = ClaudeAgentOptions(
    cwd="/home/user/project",  # 代理只能操作此目录
)
```

### add_dirs（额外目录）

需要访问多个目录时：

```python
options = ClaudeAgentOptions(
    cwd="/home/user/project",
    add_dirs=[
        "/home/user/shared-libs",
        "/home/user/configs",
    ],
)
```

代理可以读写 `cwd` 和 `add_dirs` 中的文件，其他路径受限。

## 安全部署原则

### 原则 1：最小权限

只授予代理完成任务所需的最少工具和权限：

```python
# 只读代理 — 只能读取和搜索
options = ClaudeAgentOptions(
    tools=["Read", "Bash"],
    allowed_tools=["Read", "Bash(find *)", "Bash(grep *)"],
    disallowed_tools=["Write", "Edit"],  # 明确禁止写入
)

# 代码生成代理 — 可以写但不能执行
options = ClaudeAgentOptions(
    tools=["Read", "Write", "Edit"],
    allowed_tools=["Read", "Write", "Edit"],
    disallowed_tools=["Bash"],  # 禁止执行命令
)
```

### 原则 2：纵深防御

组合多层控制：

```python
options = ClaudeAgentOptions(
    # 层 1：限制工具集
    tools=["Read", "Bash", "Write"],
    allowed_tools=["Read", "Bash(npm test)", "Bash(npm run lint)"],

    # 层 2：禁用危险工具
    disallowed_tools=["Bash(rm *)", "Bash(curl *)", "Bash(wget *)"],

    # 层 3：文件系统隔离
    cwd="/sandbox/project",

    # 层 4：沙盒
    sandbox={
        "enabled": True,
        "network": {"enabled": False},
    },

    # 层 5：Hook 验证
    hooks={
        "PreToolUse": [
            {
                "matcher": {"tool_name": "Bash"},
                "hook": {"type": "callback"},
            }
        ],
    },

    # 层 6：预算限制
    max_budget_usd=0.50,
    max_turns=10,
)
```

### 原则 3：最小网络暴露

```python
# 开发环境 — 允许包管理器
options = ClaudeAgentOptions(
    sandbox={
        "enabled": True,
        "network": {
            "enabled": True,
            "allow_list": [
                "registry.npmjs.org",
                "pypi.org",
                "files.pythonhosted.org",
            ],
        },
    },
)

# 生产环境 — 完全离线
options = ClaudeAgentOptions(
    sandbox={
        "enabled": True,
        "network": {"enabled": False},
    },
)
```

## 生产加固模式

### 模式 1：完全受限代理

适合处理不受信输入（如用户提交的代码）：

```python
options = ClaudeAgentOptions(
    # 严格权限
    permission_mode="default",
    tools=["Read"],
    allowed_tools=["Read"],

    # 沙盒隔离
    sandbox={
        "enabled": True,
        "network": {"enabled": False},
    },

    # 限制范围
    cwd="/sandbox/readonly-workspace",
    max_turns=5,
    max_budget_usd=0.10,

    # 不加载任何外部配置
    setting_sources=[],
)
```

### 模式 2：CI/CD 代理

适合自动化流水线：

```python
options = ClaudeAgentOptions(
    permission_mode="acceptall",  # CI 环境自动批准
    tools={"type": "preset", "preset": "claude_code"},
    allowed_tools=[
        "Read", "Write", "Edit",
        "Bash(npm *)", "Bash(git *)", "Bash(make *)",
    ],

    sandbox={
        "enabled": True,
        "network": {
            "enabled": True,
            "allow_list": [
                "registry.npmjs.org",
                "github.com",
                "*.githubusercontent.com",
            ],
        },
    },

    cwd="/workspace/repo",
    max_turns=30,
    max_budget_usd=5.00,
)
```

### 模式 3：内部开发代理

适合受信内部开发者使用：

```python
options = ClaudeAgentOptions(
    permission_mode="default",
    tools={"type": "preset", "preset": "claude_code"},
    allowed_tools=[
        "Read", "Write", "Edit",
        "Bash(ls *)", "Bash(cat *)", "Bash(git *)",
        "Bash(python *)", "Bash(pip *)",
    ],

    sandbox={
        "enabled": True,
        "network": {"enabled": True},  # 允许网络但有沙盒
    },

    cwd="/home/developer/project",
    add_dirs=["/home/developer/.config"],
    setting_sources=["user", "project"],

    max_budget_usd=2.00,
)
```

## Hook 增强安全

通过 Hook 实现细粒度的运行时安全策略：

```python
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    HookCallback,
    PreToolUseHookInput,
)
import re

async def security_hook(input: PreToolUseHookInput) -> dict:
    """拦截危险命令"""
    if input.tool_name == "Bash":
        command = input.tool_input.get("command", "")

        # 禁止危险操作
        dangerous_patterns = [
            r"rm\s+-rf\s+/",
            r"curl.*\|.*sh",
            r"wget.*\|.*bash",
            r"chmod\s+777",
            r"sudo\s+",
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, command):
                return {
                    "decision": "deny",
                    "reason": f"安全策略禁止: 匹配规则 {pattern}",
                }

    return {"decision": "allow"}

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            {
                "matcher": {"tool_name": "Bash"},
                "hook": {"type": "callback"},
                "callback": security_hook,
            }
        ],
    },
)
```

## 注意事项

1. **沙盒依赖 CLI 实现** — SDK 的沙盒是通过 CLI 子进程的环境隔离实现的，不是容器级隔离。对于高安全场景，建议在容器内运行。

2. **`acceptall` 极度危险** — 仅在完全受控环境（如 CI、测试）中使用。任何接收外部输入的场景都不应使用。

3. **`allowed_tools` 支持通配符但需谨慎** — `"Bash(*)"` 等价于允许所有命令。使用更精确的模式如 `"Bash(npm test)"` 或 `"Bash(git status)"`.

4. **网络 allow_list 是域名级** — 无法精确到 URL 路径。如需更细粒度控制，使用 Hook 拦截。

5. **`setting_sources=[]` 实现完全隔离** — 当设为空列表时，不加载任何用户或项目配置，确保代理行为完全由代码控制。
