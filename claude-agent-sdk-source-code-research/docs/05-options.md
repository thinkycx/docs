# ClaudeAgentOptions 全参数详解

`ClaudeAgentOptions` 是一个 dataclass，包含约 50 个配置参数，控制 SDK 的所有行为。

```python
from claude_agent_sdk import ClaudeAgentOptions

options = ClaudeAgentOptions(
    system_prompt="...",
    allowed_tools=["Read", "Bash"],
    max_turns=5,
)
```

## 工具配置

### tools
```python
tools: list[str] | {"type": "preset", "preset": "claude_code"} | None = None
```
控制**可用工具集**（哪些工具存在）：
- `list[str]` — 指定工具名，如 `["Bash", "Read", "Edit"]`
- `[]` — 禁用所有内置工具
- `{"type": "preset", "preset": "claude_code"}` — 使用 Claude Code 全部默认工具
- `None` — 使用 CLI 默认工具集

### allowed_tools
```python
allowed_tools: list[str] = []
```
控制**免询问工具**（自动批准，不弹权限确认）：
- 工具名列表，如 `["Read", "Bash(ls *)"]`
- 支持通配符模式，如 `"Bash(npm *)"` 仅允许 npm 命令
- MCP 工具格式：`"mcp__server_name__tool_name"`

### disallowed_tools
```python
disallowed_tools: list[str] = []
```
**禁用工具**（从模型上下文中完全移除）：
- 优先级高于 allowed_tools
- 被禁用的工具 Claude 无法看到也无法调用

### mcp_servers
```python
mcp_servers: dict[str, McpServerConfig] | str | Path = {}
```
MCP 服务器配置：
- dict：键为服务器名，值为配置
- str/Path：指向 MCP 配置 JSON 文件

### strict_mcp_config
```python
strict_mcp_config: bool = False
```
为 True 时，仅使用 `mcp_servers` 中的配置，忽略 CLI 加载的其他 MCP 配置。

## 提示词配置

### system_prompt
```python
system_prompt: str | dict | None = None
```
三种模式：
- `str` — 自定义系统提示词（完全替换默认）
- `{"type": "preset", "preset": "claude_code"}` — Claude Code 默认提示词
- `{"type": "preset", "preset": "claude_code", "append": "额外指令"}` — 默认 + 追加
- `None` — 无特殊系统提示词

## 会话控制

### continue_conversation
```python
continue_conversation: bool = False
```
续接当前目录的最近一次对话。与 `resume` 互斥。

### resume
```python
resume: str | None = None
```
恢复指定 session ID 的对话。

### session_id
```python
session_id: str | None = None
```
使用指定 UUID 作为 session ID（而非自动生成）。

### fork_session
```python
fork_session: bool = False
```
配合 `resume` 使用，从指定 session 分叉出新会话。

### max_turns
```python
max_turns: int | None = None
```
最大对话轮数。超出后停止，ResultMessage.subtype 为 "error_max_turns"。

### max_budget_usd
```python
max_budget_usd: float | None = None
```
最大预算（美元）。超出后停止，ResultMessage.subtype 为 "error_max_budget_usd"。

## 权限控制

### permission_mode
```python
permission_mode: PermissionMode | None = None
```
权限模式：
| 模式 | 效果 |
|------|------|
| `"default"` | 标准权限，危险操作需确认 |
| `"acceptEdits"` | 自动批准文件编辑 |
| `"bypassPermissions"` | 跳过所有权限检查 |
| `"plan"` | 规划模式，不执行工具 |
| `"dontAsk"` | 不询问，未预先批准则拒绝 |
| `"auto"` | 自动模式 |

### can_use_tool
```python
can_use_tool: CanUseTool | None = None
```
自定义权限回调函数（仅在 CLI 权限评估为 "ask" 时触发）。

### permission_prompt_tool_name
```python
permission_prompt_tool_name: str | None = None
```
将权限请求路由到指定 MCP 工具（替代默认处理器）。与 `can_use_tool` 互斥。

## 模型配置

### model
```python
model: str | None = None
```
Claude 模型 ID，如 `"claude-sonnet-4-5"`, `"claude-opus-4-5"`。

### fallback_model
```python
fallback_model: str | None = None
```
主模型不可用时的备选模型。

### thinking
```python
thinking: ThinkingConfig | None = None
```
思考模式配置：
- `{"type": "adaptive"}` — 自适应（Opus 4.6+ 默认）
- `{"type": "enabled", "budget_tokens": 8000}` — 固定 token 预算
- `{"type": "disabled"}` — 禁用思考

### effort
```python
effort: EffortLevel | None = None
```
努力级别：`"low"` / `"medium"` / `"high"` / `"xhigh"` / `"max"`

## Agent 与 Hook

### agents
```python
agents: dict[str, AgentDefinition] | None = None
```
编程定义子 Agent。键为 Agent 名称。

### hooks
```python
hooks: dict[HookEvent, list[HookMatcher]] | None = None
```
Hook 事件回调。同一事件的多个 matcher 并发执行。

### skills
```python
skills: list[str] | "all" | None = None
```
启用的 Skill 列表。设置后自动允许 Skill 工具。

### plugins
```python
plugins: list[SdkPluginConfig] = []
```
加载本地插件。

## 输出控制

### output_format
```python
output_format: dict[str, Any] | None = None
```
结构化输出格式：
```python
output_format={
    "type": "json_schema",
    "schema": {
        "type": "object",
        "properties": {"answer": {"type": "string"}},
        "required": ["answer"]
    }
}
```

### include_partial_messages
```python
include_partial_messages: bool = False
```
启用后，会 yield StreamEvent 消息（包含实时文本增量）。

### include_hook_events
```python
include_hook_events: bool = False
```
启用后，消息流中包含 HookEventMessage。

### enable_file_checkpointing
```python
enable_file_checkpointing: bool = False
```
启用文件检查点，支持 `client.rewind_files()` 回退。

## 环境配置

### cwd
```python
cwd: str | Path | None = None
```
工作目录。默认为当前进程 cwd。

### cli_path
```python
cli_path: str | Path | None = None
```
Claude CLI 路径。未指定时使用捆绑 CLI。

### settings
```python
settings: str | None = None
```
额外设置文件路径（最高优先级的 "flag settings" 层）。

### add_dirs
```python
add_dirs: list[str | Path] = []
```
Claude 可访问的额外目录列表。

### env
```python
env: dict[str, str] = {}
```
传给 CLI 子进程的环境变量。

### extra_args
```python
extra_args: dict[str, str | None] = {}
```
额外 CLI 参数。键不含 `--`，值为 None 表示布尔标志。

### setting_sources
```python
setting_sources: list[SettingSource] | None = None
```
控制加载哪些配置源：
- `None` — 加载所有（user + project + local）
- `[]` — 不加载任何文件配置（SDK 隔离模式）
- `["user"]` — 仅全局用户配置
- `["user", "project"]` — 用户 + 项目

## Session Store

### session_store
```python
session_store: SessionStore | None = None
```
外部 Session 存储适配器。设置后自动镜像转写数据。

### session_store_flush
```python
session_store_flush: SessionStoreFlushMode = "batched"
```
刷新模式：`"batched"`（批量，默认）或 `"eager"`（每帧即刷）。

### load_timeout_ms
```python
load_timeout_ms: int = 60_000
```
从 store 加载 session 的超时时间（毫秒）。

## 其他

### betas
```python
betas: list[SdkBeta] = []
```
启用 Beta 功能，如 `["context-1m-2025-08-07"]`（1M 上下文窗口）。

### sandbox
```python
sandbox: SandboxSettings | None = None
```
沙盒隔离设置。

### task_budget
```python
task_budget: TaskBudget | None = None
```
API 端 token 预算。

### user
```python
user: str | None = None
```
关联的用户标识。

### stderr
```python
stderr: Callable[[str], None] | None = None
```
CLI 子进程 stderr 输出回调（调试用）。
