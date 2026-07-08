# Hook 事件系统

Hook 是拦截和修改 Agent 行为的回调机制，在工具调用、提示提交、停止等关键节点触发。

## Hook 事件类型总览

| 事件 | 触发时机 | 典型用途 |
|------|---------|---------|
| `PreToolUse` | 工具执行前 | 拦截、修改输入、批准/拒绝 |
| `PostToolUse` | 工具执行后 | 监控输出、注入反馈 |
| `PostToolUseFailure` | 工具执行失败后 | 错误恢复 |
| `UserPromptSubmit` | 用户消息提交时 | 注入上下文、修改提示 |
| `Stop` | Agent 准备停止时 | 阻止/延续执行 |
| `SubagentStop` | 子 Agent 停止时 | 子 Agent 结果处理 |
| `SubagentStart` | 子 Agent 启动时 | 子 Agent 配置修改 |
| `PreCompact` | 上下文压缩前 | 自定义压缩策略 |
| `Notification` | 通知事件 | 外部通知（Slack 等） |
| `PermissionRequest` | 权限请求时 | 自定义权限 UI |

## 配置方式

```python
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[check_bash]),   # 仅匹配 Bash 工具
            HookMatcher(matcher=None, hooks=[log_all_tools]),   # 匹配所有工具
        ],
        "PostToolUse": [
            HookMatcher(matcher="Write|Edit", hooks=[review_writes]),
        ],
        "UserPromptSubmit": [
            HookMatcher(matcher=None, hooks=[inject_context]),
        ],
        "Stop": [
            HookMatcher(matcher=None, hooks=[on_stop]),
        ],
    }
)
```

## HookMatcher

```python
@dataclass
class HookMatcher:
    matcher: str | None      # 正则表达式匹配工具名，None = 匹配所有
    hooks: list[HookCallback]  # 回调函数列表
    timeout: int | None = None  # 超时(ms)
```

- `matcher` 是正则表达式字符串，匹配工具名
- 同一事件的多个 HookMatcher 并发执行（不是顺序）
- 同一 HookMatcher 内的多个 hooks 也并发执行

## 回调函数签名

```python
async def my_hook(
    input: HookInput,           # 事件相关的输入数据
    tool_use_id: str | None,    # 工具调用 ID（仅工具相关事件）
    context: HookContext,       # 上下文信息
) -> HookJSONOutput:            # 返回决策
    ...
```

### HookContext

```python
class HookContext(TypedDict):
    session_id: str
    transcript_path: str
    cwd: str
    permission_mode: str
```

## Hook 输出字段

```python
class HookJSONOutput(TypedDict, total=False):
    continue_: bool              # 是否继续执行（False = 停止）
    suppressOutput: bool         # 抑制工具输出
    stopReason: str             # 停止原因（continue_=False 时）
    permissionDecision: str     # "allow" | "deny"（PreToolUse 专用）
    reason: str                 # 决策原因
    systemMessage: str          # 注入系统消息
    additionalContext: str      # 注入额外上下文
    hookSpecificOutput: dict    # 事件特定的输出
```

## 各事件详解

### PreToolUse — 工具执行前拦截

```python
async def block_dangerous_commands(input, tool_use_id, context):
    tool_name = input.get("tool_name", "")
    tool_input = input.get("tool_input", {})

    # 拒绝危险命令
    if tool_name == "Bash":
        cmd = tool_input.get("command", "")
        if "rm -rf" in cmd or "sudo" in cmd:
            return {
                "permissionDecision": "deny",
                "reason": "禁止执行危险命令"
            }

    # 允许其他工具
    return {"permissionDecision": "allow"}
```

PreToolUseHookInput 字段：
- `tool_name` — 工具名称
- `tool_input` — 工具输入参数

### PostToolUse — 工具执行后回调

```python
async def monitor_output(input, tool_use_id, context):
    tool_name = input.get("tool_name", "")
    tool_output = input.get("tool_output", "")

    if "error" in tool_output.lower():
        return {
            "systemMessage": f"⚠️ {tool_name} 执行出现错误",
            "additionalContext": "请检查输出并考虑重试"
        }
    return {}
```

PostToolUseHookInput 字段：
- `tool_name` — 工具名称
- `tool_input` — 工具输入
- `tool_output` — 工具输出结果

### UserPromptSubmit — 提示提交时

```python
async def add_project_context(input, tool_use_id, context):
    return {
        "additionalContext": "当前项目使用 Python 3.12，测试框架为 pytest"
    }
```

UserPromptSubmitHookInput 字段：
- `user_prompt` — 用户消息内容

### Stop — Agent 停止时

```python
async def prevent_premature_stop(input, tool_use_id, context):
    stop_reason = input.get("stop_reason", "")

    if stop_reason == "end_turn" and not input.get("all_tasks_complete"):
        return {
            "continue_": True,  # 注意下划线，避免与 Python 关键字冲突
            "systemMessage": "还有未完成的任务，请继续"
        }
    return {}
```

StopHookInput 字段：
- `stop_reason` — 停止原因

### SubagentStart — 子 Agent 启动

```python
async def configure_subagent(input, tool_use_id, context):
    return {
        "hookSpecificOutput": {
            "additionalSystemPrompt": "子 Agent 额外指令..."
        }
    }
```

### Notification — 通知事件

```python
async def send_to_slack(input, tool_use_id, context):
    message = input.get("message", "")
    # 可以在这里发送到 Slack/邮件等外部系统
    print(f"[通知] {message}")
    return {
        "hookSpecificOutput": {
            "delivered": True
        }
    }
```

## 异步 Hook

Hook 可以返回异步标记，表示处理将异步完成：

```python
async def async_approval(input, tool_use_id, context):
    return {
        "async_": True,
        "asyncTimeout": 30000  # 30 秒超时
    }
```

异步 Hook 让 CLI 进程退出，稍后通过恢复 session 继续。适用于需要人工审批的场景。

## 并发执行机制

同一事件的所有 HookMatcher 并发触发：

```python
hooks={
    "PreToolUse": [
        HookMatcher(matcher=None, hooks=[hook_a]),  # 与 hook_b 并发
        HookMatcher(matcher=None, hooks=[hook_b]),  # 与 hook_a 并发
    ]
}
```

决策合并规则：
- 任何一个返回 `deny` → 工具被拒绝
- 所有都返回 `allow` → 工具被允许
- 多个 `systemMessage` 会合并

## 完整示例

```python
import anyio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, HookMatcher, AssistantMessage, TextBlock

async def security_hook(input, tool_use_id, context):
    tool_name = input.get("tool_name", "")
    tool_input = input.get("tool_input", {})

    if tool_name == "Write":
        path = tool_input.get("file_path", "")
        if path.startswith("/etc/") or path.startswith("/usr/"):
            return {"permissionDecision": "deny", "reason": "禁止写入系统目录"}

    return {"permissionDecision": "allow"}

async def main():
    options = ClaudeAgentOptions(
        hooks={
            "PreToolUse": [
                HookMatcher(matcher="Write|Edit", hooks=[security_hook])
            ]
        },
        allowed_tools=["Read", "Write", "Bash"],
    )

    async with ClaudeSDKClient(options) as client:
        await client.query("创建一个 hello.py 文件")
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

anyio.run(main)
```
