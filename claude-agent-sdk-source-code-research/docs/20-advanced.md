# 高级主题

## Transport 抽象层

SDK 通过抽象的 `Transport` 类与 CLI 通信。默认实现是 `SubprocessCLITransport`，但你可以自定义。

### Transport 抽象类

```python
from claude_agent_sdk import Transport

class Transport:
    """传输层抽象基类"""

    async def connect(self) -> None:
        """建立连接"""
        ...

    async def write(self, data: dict) -> None:
        """发送消息到 CLI"""
        ...

    async def read_messages(self):
        """异步生成器，读取 CLI 返回的消息"""
        ...

    async def close(self) -> None:
        """关闭连接"""
        ...

    def is_ready(self) -> bool:
        """连接是否就绪"""
        ...

    async def end_input(self) -> None:
        """通知 CLI 输入结束"""
        ...
```

### 自定义 Transport

适用于非子进程场景（如通过网络代理连接远程 CLI）：

```python
from claude_agent_sdk import Transport, query, ClaudeAgentOptions
import aiohttp

class RemoteCLITransport(Transport):
    """通过 WebSocket 连接远程 CLI 服务"""

    def __init__(self, ws_url: str):
        self.ws_url = ws_url
        self.ws = None

    async def connect(self):
        self.session = aiohttp.ClientSession()
        self.ws = await self.session.ws_connect(self.ws_url)

    async def write(self, data: dict):
        import json
        await self.ws.send_str(json.dumps(data))

    async def read_messages(self):
        async for msg in self.ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                import json
                yield json.loads(msg.data)

    async def close(self):
        if self.ws:
            await self.ws.close()
        if self.session:
            await self.session.close()

    def is_ready(self) -> bool:
        return self.ws is not None and not self.ws.closed

    async def end_input(self):
        await self.write({"type": "end_input"})

# 使用自定义 Transport
options = ClaudeAgentOptions(
    transport=RemoteCLITransport("ws://cli-service:8080/agent"),
)
```

### SubprocessCLITransport 内部机制

默认的子进程传输层：

1. **CLI 发现** — 按以下顺序查找 `claude` 二进制：
   - `$PATH` 中的 `claude`
   - 常见安装路径（`~/.npm-global/bin/claude` 等）
   - 如果找不到，抛出 `CLINotFoundError`

2. **版本检查** — 启动时验证 CLI 版本兼容性

3. **优雅关闭** — 关闭顺序：
   - 关闭 stdin → 等待进程退出 → 超时后 SIGTERM → 再超时 SIGKILL

4. **NDJSON 协议** — 每行一个 JSON 消息，通过 stdin/stdout 双向通信

## SdkPluginConfig

插件系统允许扩展 SDK 能力：

```python
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(
    plugins=[
        {
            "type": "local",
            "path": "/path/to/my-plugin",
        },
    ],
)

async for msg in query(prompt="使用插件功能", options=options):
    pass
```

### 插件目录结构

```
my-plugin/
├── skills/          # 技能定义
│   └── my-skill.md
├── agents/          # 子代理定义
│   └── specialist.yaml
├── hooks/           # Hook 脚本
│   └── pre-tool-use.sh
└── mcp-servers/     # MCP 服务器配置
    └── config.json
```

### 插件配置

```python
# 单个插件
options = ClaudeAgentOptions(
    plugins=[
        {"type": "local", "path": "/plugins/code-quality"},
    ],
)

# 多个插件
options = ClaudeAgentOptions(
    plugins=[
        {"type": "local", "path": "/plugins/code-quality"},
        {"type": "local", "path": "/plugins/security-scan"},
        {"type": "local", "path": "/plugins/deploy-tools"},
    ],
)
```

## SdkBeta

启用实验性功能：

```python
options = ClaudeAgentOptions(
    betas=["context-1m-2025-08-07"],  # 1M 上下文（仅 Sonnet）
    model="claude-sonnet-4-20250514",
)
```

### 可用 Beta

| Beta ID | 说明 | 限制 |
|---------|------|------|
| `"context-1m-2025-08-07"` | 1M token 上下文窗口 | 仅 Sonnet 模型 |

**注意：** Beta 功能可能随时变更或移除。生产环境慎用。

## setting_sources 深度解析

`setting_sources` 控制加载哪些外部配置：

```python
# 加载所有配置源
options = ClaudeAgentOptions(
    setting_sources=["user", "project", "local"],
)

# 仅加载用户配置
options = ClaudeAgentOptions(
    setting_sources=["user"],
)

# 完全隔离 — 不加载任何外部配置
options = ClaudeAgentOptions(
    setting_sources=[],
)
```

### 配置源详解

| 源 | 路径 | 内容 |
|----|------|------|
| `"user"` | `~/.claude/settings.json` | 用户全局设置（权限、MCP 服务器等） |
| `"project"` | `.claude/settings.json` + `CLAUDE.md` | 项目级设置和提示词 |
| `"local"` | `.claude/settings.local.json` | 本地覆盖（不提交到 git） |

### 配置加载顺序与覆盖

```
user settings → project settings → local settings
（低优先级）         →          →    （高优先级）
```

后加载的配置会覆盖先加载的同名设置。

### 隔离模式

```python
# 完全隔离 — 适合多租户/不受信环境
options = ClaudeAgentOptions(
    setting_sources=[],  # 不加载任何配置
    # 所有配置必须通过代码显式传入
    system_prompt="...",
    allowed_tools=[...],
    mcp_servers={...},
)
```

## extra_args

传递任意 CLI 标志：

```python
options = ClaudeAgentOptions(
    extra_args=[
        "--verbose",
        "--no-color",
        "--timeout", "60000",
    ],
)
```

**注意：** `extra_args` 绕过了 SDK 的类型检查。传入无效标志可能导致 CLI 启动失败。

## add_dirs

允许代理访问工作目录之外的目录：

```python
options = ClaudeAgentOptions(
    cwd="/home/user/main-project",
    add_dirs=[
        "/home/user/shared-libs",       # 共享库
        "/home/user/config-templates",  # 配置模板
        "/opt/data/datasets",           # 数据集
    ],
)
```

代理可以在 `cwd` 和所有 `add_dirs` 中读写文件。

## env（环境变量）

设置 CLI 子进程的环境变量：

```python
options = ClaudeAgentOptions(
    env={
        # 标识调用方（影响 User-Agent）
        "CLAUDE_AGENT_SDK_CLIENT_APP": "my-app/1.0.0",

        # API 配置
        "ANTHROPIC_API_KEY": "sk-ant-...",

        # 自定义变量（工具可使用）
        "PROJECT_ENV": "staging",
        "DATABASE_URL": "postgresql://...",
    },
)
```

### CLAUDE_AGENT_SDK_CLIENT_APP

特殊环境变量，设置后会附加到 API 请求的 User-Agent 头：

```python
options = ClaudeAgentOptions(
    env={
        "CLAUDE_AGENT_SDK_CLIENT_APP": "code-review-bot/2.1.0",
    },
)
# User-Agent: claude-agent-sdk/0.2.111 code-review-bot/2.1.0
```

## stderr 回调

捕获 CLI 进程的 stderr 输出，用于调试：

```python
import sys

def on_stderr(data: str):
    """处理 CLI 的 stderr 输出"""
    print(f"[CLI stderr] {data}", file=sys.stderr)

options = ClaudeAgentOptions(
    stderr_callback=on_stderr,
)

async for msg in query(prompt="hello", options=options):
    pass
```

### 调试模式

```python
import logging

logger = logging.getLogger("claude-cli")

def debug_stderr(data: str):
    # 过滤噪音
    if "debug" in data.lower() or "error" in data.lower():
        logger.debug(f"CLI: {data.strip()}")

options = ClaudeAgentOptions(
    stderr_callback=debug_stderr,
    env={
        "CLAUDE_CODE_DEBUG": "1",  # 开启 CLI 调试输出
    },
)
```

## OTEL（OpenTelemetry）集成

通过环境变量启用遥测：

```python
options = ClaudeAgentOptions(
    env={
        # 启用遥测
        "CLAUDE_CODE_ENABLE_TELEMETRY": "1",

        # 配置 OTEL exporter
        "OTEL_TRACES_EXPORTER": "otlp",
        "OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:4318",
        "OTEL_SERVICE_NAME": "my-agent-service",
    },
)
```

### 遥测数据

启用后，CLI 会导出：
- API 调用 span（耗时、令牌数）
- 工具执行 span
- 整体查询 trace

### 与 Jaeger/Grafana Tempo 集成

```python
options = ClaudeAgentOptions(
    env={
        "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
        "OTEL_TRACES_EXPORTER": "otlp",
        "OTEL_EXPORTER_OTLP_ENDPOINT": "http://jaeger:4318",
        "OTEL_EXPORTER_OTLP_PROTOCOL": "http/protobuf",
        "OTEL_SERVICE_NAME": "agent-sdk-prod",
        "OTEL_RESOURCE_ATTRIBUTES": "deployment.environment=production",
    },
)
```

## 综合高级示例

### 多目录、多插件、遥测、自定义安全策略

```python
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(
    # 模型与思考
    model="claude-sonnet-4-20250514",
    thinking={"type": "adaptive"},
    effort="high",

    # 系统提示
    system_prompt={
        "type": "preset",
        "preset": "claude_code",
        "append": "额外指令：所有输出使用中文",
    },

    # 工具与权限
    tools={"type": "preset", "preset": "claude_code"},
    allowed_tools=["Read", "Write", "Edit", "Bash(npm *)", "Bash(git *)"],
    disallowed_tools=["Bash(rm -rf *)"],

    # 文件系统
    cwd="/workspace/main-project",
    add_dirs=["/workspace/shared", "/workspace/configs"],

    # 配置源
    setting_sources=["project"],  # 只加载项目配置

    # 插件
    plugins=[
        {"type": "local", "path": "/plugins/lint-rules"},
    ],

    # Beta 功能
    betas=["context-1m-2025-08-07"],

    # 沙盒
    sandbox={
        "enabled": True,
        "network": {
            "enabled": True,
            "allow_list": ["registry.npmjs.org", "api.github.com"],
        },
    },

    # 预算
    max_budget_usd=2.00,
    max_turns=20,

    # 环境变量
    env={
        "CLAUDE_AGENT_SDK_CLIENT_APP": "enterprise-agent/3.0",
        "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
        "OTEL_TRACES_EXPORTER": "otlp",
        "OTEL_EXPORTER_OTLP_ENDPOINT": "http://otel-collector:4318",
    },

    # 调试
    stderr_callback=lambda data: logging.debug(f"CLI: {data}"),
)

async for msg in query(prompt="重构认证模块", options=options):
    process(msg)
```

## 注意事项

1. **自定义 Transport 需要完整实现** — 所有方法都必须实现，缺失任何方法会导致运行时错误。

2. **插件路径必须为绝对路径** — 相对路径行为未定义。

3. **`extra_args` 可能破坏兼容性** — CLI 升级可能移除或修改标志。避免依赖未文档化的标志。

4. **环境变量中不要传敏感信息的明文** — 虽然传递 API Key 通过 env 是支持的，但在日志中可能泄漏。生产中考虑使用 secret manager。

5. **OTEL 有性能开销** — 遥测会增加少量延迟。在高吞吐场景下可通过采样率控制。

6. **`setting_sources=[]` 不影响 system_prompt** — 即使清空配置源，代码中设置的 system_prompt 仍然生效。配置源只影响外部文件加载。
