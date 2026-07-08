# 权限控制系统

权限系统控制 Agent 能否执行特定工具调用，是保障安全性的核心机制。SDK 提供了从静态规则到动态回调的完整权限控制链。

## 6 步权限评估流程

当 Agent 请求执行一个工具时，按以下顺序依次评估：

```
┌─────────────────────────────────────────────────────────────┐
│ 工具调用请求                                                  │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Hooks (PreToolUse)                                  │
│ → 如果 hook 返回 allow/deny，流程结束                         │
└─────────────────────┬───────────────────────────────────────┘
                      ▼ (hook 未决策)
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Deny 规则 (disallowed_tools)                        │
│ → 如果匹配 deny 规则，拒绝                                   │
└─────────────────────┬───────────────────────────────────────┘
                      ▼ (未匹配 deny)
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Ask 规则                                            │
│ → 如果匹配 ask 规则，跳转到 Step 6                           │
└─────────────────────┬───────────────────────────────────────┘
                      ▼ (未匹配 ask)
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Permission Mode                                     │
│ → 根据模式可能自动允许（如 bypassPermissions）                │
└─────────────────────┬───────────────────────────────────────┘
                      ▼ (模式未自动允许)
┌─────────────────────────────────────────────────────────────┐
│ Step 5: Allow 规则 (allowed_tools)                          │
│ → 如果匹配 allow 规则，允许                                  │
└─────────────────────┬───────────────────────────────────────┘
                      ▼ (未匹配 allow)
┌─────────────────────────────────────────────────────────────┐
│ Step 6: canUseTool 回调                                     │
│ → 最终决策点                                                 │
└─────────────────────────────────────────────────────────────┘
```

## PermissionMode 权限模式

```python
from claude_agent_sdk import ClaudeAgentOptions

options = ClaudeAgentOptions(
    permission_mode="default",  # 可选值见下表
)
```

| 模式 | 行为 |
|------|------|
| `"default"` | 默认模式，未匹配规则的工具需要用户确认 |
| `"acceptEdits"` | 自动允许文件编辑（Write/Edit），其他工具仍需确认 |
| `"bypassPermissions"` | 跳过所有权限检查，允许所有工具 |
| `"plan"` | 规划模式，不执行任何工具 |
| `"dontAsk"` | 不询问用户，未匹配规则的工具自动拒绝 |
| `"auto"` | 自动模式，类似 bypassPermissions |

## 静态规则：allowed_tools 和 disallowed_tools

### allowed_tools — 允许规则

```python
options = ClaudeAgentOptions(
    allowed_tools=[
        "Read",                    # 精确匹配工具名
        "Read(*)",                 # 允许 Read 的所有参数
        "Bash(npm *)",             # glob 模式：仅允许 npm 开头的命令
        "Bash(python -m pytest *)",# 允许 pytest 命令
        "Write(src/**)",           # 允许写入 src/ 目录
        "Edit(*.py)",              # 允许编辑 Python 文件
        "mcp__server__*",          # 允许某 MCP 服务器的所有工具
    ],
)
```

### disallowed_tools — 拒绝规则

```python
options = ClaudeAgentOptions(
    disallowed_tools=[
        "Bash(rm *)",              # 禁止 rm 命令
        "Bash(sudo *)",            # 禁止 sudo 命令
        "Write(/etc/*)",           # 禁止写入 /etc/
        "mcp__dangerous__*",       # 禁止某 MCP 服务器的所有工具
    ],
)
```

### Glob 模式语法

- `*` — 匹配任意字符（不含路径分隔符）
- `**` — 匹配任意路径（含分隔符）
- `?` — 匹配单个字符
- `ToolName(pattern)` — 匹配工具名 + 参数模式

参数匹配的含义取决于工具类型：
- `Bash(pattern)` — 匹配 command 参数
- `Read(pattern)` / `Write(pattern)` / `Edit(pattern)` — 匹配 file_path 参数
- `mcp__server__tool` — 精确匹配 MCP 工具全名

## can_use_tool 回调 API

`can_use_tool` 是最灵活的权限控制机制，允许通过代码逻辑动态决定权限。

**重要限制：`can_use_tool` 仅在 `ClaudeSDKClient`（流式模式）中可用，不支持 `query()` 函数与字符串 prompt 的组合。**

### 函数签名

```python
async def can_use_tool(
    tool_name: str,
    input: dict,
    context: ToolPermissionContext,
) -> PermissionResultAllow | PermissionResultDeny:
    ...
```

### ToolPermissionContext

```python
class ToolPermissionContext(TypedDict, total=False):
    signal: object               # 取消信号
    suggestions: list[str]       # 建议的权限规则
    tool_use_id: str            # 工具调用 ID
    agent_id: str | None        # 子 Agent ID（如果是子 Agent 调用）
    blocked_path: str | None    # 被阻止的路径
    decision_reason: str | None # 到达此步的原因
    title: str | None           # 工具标题
    display_name: str | None    # 工具显示名称
    description: str | None     # 工具描述
```

### 返回类型

#### PermissionResultAllow

```python
@dataclass
class PermissionResultAllow:
    behavior: str = "allow"           # 固定为 "allow"
    updated_input: dict | None = None  # 修改后的工具输入（None 表示不修改）
    updated_permissions: PermissionUpdate | None = None  # 动态更新规则
```

#### PermissionResultDeny

```python
@dataclass
class PermissionResultDeny:
    behavior: str = "deny"            # 固定为 "deny"
    message: str = ""                 # 拒绝原因（展示给 Agent）
    interrupt: bool = False           # True 时中断整个对话
```

### PermissionUpdate — 动态规则更新

允许在回调中动态添加权限规则，后续调用将直接匹配新规则：

```python
@dataclass
class PermissionUpdate:
    add_allowed: list[str] | None = None      # 新增 allow 规则
    add_disallowed: list[str] | None = None   # 新增 deny 规则
```

## 完整示例

### 基础权限控制

```python
import anyio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
)

async def my_permission_handler(tool_name, input, context):
    """自定义权限回调"""

    # 允许所有读取操作
    if tool_name == "Read":
        return PermissionResultAllow()

    # Bash 命令白名单
    if tool_name == "Bash":
        cmd = input.get("command", "")
        safe_prefixes = ["ls", "cat", "grep", "find", "git status", "git diff"]

        if any(cmd.startswith(prefix) for prefix in safe_prefixes):
            return PermissionResultAllow()

        return PermissionResultDeny(
            message=f"不允许执行命令: {cmd}"
        )

    # 写入仅限特定目录
    if tool_name in ("Write", "Edit"):
        path = input.get("file_path", "")
        if path.startswith("/tmp/") or path.startswith("./src/"):
            return PermissionResultAllow()

        return PermissionResultDeny(
            message=f"不允许写入路径: {path}"
        )

    # 默认拒绝未知工具
    return PermissionResultDeny(message=f"未知工具: {tool_name}")

async def main():
    options = ClaudeAgentOptions(
        can_use_tool=my_permission_handler,
        permission_mode="default",
    )

    async with ClaudeSDKClient(options) as client:
        await client.query("列出当前目录的文件")
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

anyio.run(main)
```

### 动态权限升级

```python
async def escalation_handler(tool_name, input, context):
    """首次写入时询问用户，允许后自动添加规则"""

    if tool_name == "Write":
        path = input.get("file_path", "")

        # 模拟用户确认（实际场景中可接入 UI）
        user_approved = await ask_user_permission(
            f"允许写入 {path}？"
        )

        if user_approved:
            # 动态添加规则：后续对同一目录的写入自动允许
            import os
            dir_pattern = os.path.dirname(path) + "/*"
            return PermissionResultAllow(
                updated_permissions=PermissionUpdate(
                    add_allowed=[f"Write({dir_pattern})"]
                )
            )
        else:
            return PermissionResultDeny(message="用户拒绝写入")

    return PermissionResultAllow()
```

### 修改工具输入

```python
async def sanitize_handler(tool_name, input, context):
    """修改工具输入，添加安全措施"""

    if tool_name == "Bash":
        cmd = input.get("command", "")

        # 自动添加 timeout 前缀
        if not cmd.startswith("timeout"):
            return PermissionResultAllow(
                updated_input={"command": f"timeout 30 {cmd}"}
            )

    return PermissionResultAllow()
```

### 中断对话

```python
async def critical_guard(tool_name, input, context):
    """检测到严重安全风险时中断整个对话"""

    if tool_name == "Bash":
        cmd = input.get("command", "")
        critical_patterns = ["curl | bash", "eval(", "rm -rf /"]

        for pattern in critical_patterns:
            if pattern in cmd:
                return PermissionResultDeny(
                    message=f"检测到危险操作: {pattern}",
                    interrupt=True  # 中断整个对话，不再继续
                )

    return PermissionResultAllow()
```

## 与 Hooks 的协作

权限系统的 Step 1 是 PreToolUse Hook。Hook 和 `can_use_tool` 的区别：

| 特性 | PreToolUse Hook | can_use_tool |
|------|----------------|--------------|
| 执行顺序 | 最先（Step 1） | 最后（Step 6） |
| 优先级 | 最高，可覆盖一切 | 最低，兜底决策 |
| 并发 | 多个 Hook 并发执行 | 单一回调 |
| 适用场景 | 全局安全策略、审计日志 | 交互式权限确认 |
| 支持修改输入 | 否 | 是（updated_input） |
| 动态规则更新 | 否 | 是（updated_permissions） |

推荐做法：
- 用 Hook 实现硬性安全规则（绝对不允许的操作）
- 用 `can_use_tool` 实现需要动态判断的权限逻辑

## 组合配置示例

```python
options = ClaudeAgentOptions(
    # 权限模式：自动允许文件编辑
    permission_mode="acceptEdits",

    # 静态允许规则
    allowed_tools=[
        "Read(*)",
        "Bash(git *)",
        "Bash(npm test)",
        "mcp__github__*",
    ],

    # 静态拒绝规则（优先于 allow）
    disallowed_tools=[
        "Bash(rm -rf *)",
        "Bash(sudo *)",
        "Write(/etc/*)",
    ],

    # 动态回调（处理未匹配规则的情况）
    can_use_tool=my_permission_handler,

    # Hook（最高优先级安全策略）
    hooks={
        "PreToolUse": [
            HookMatcher(matcher=None, hooks=[audit_log]),  # 审计所有工具调用
        ]
    },
)
```

## 注意事项

- `disallowed_tools` 优先于 `allowed_tools`（Step 2 在 Step 5 之前）
- `bypassPermissions` 模式会跳过 Step 5 和 Step 6，但不跳过 Step 1（Hook）和 Step 2（deny）
- `can_use_tool` 的 `interrupt=True` 会立即终止整个 Agent 对话
- 子 Agent 的权限由其自身的 `allowed_tools` / `disallowed_tools` 控制，与父 Agent 独立
- 使用 `query()` 函数时，`can_use_tool` 回调不生效，请使用 `ClaudeSDKClient`
