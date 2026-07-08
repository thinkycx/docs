# Session 管理

Session（会话）是 Agent 对话历史的持久化单元。每次与 Agent 的交互都会产生一个 Session，其中包含完整的消息记录，支持恢复、分支和管理。

## Session 概念

- 每个 Session 对应一次完整对话，包含用户消息、Agent 回复、工具调用等全部记录
- Session 以 JSONL（JSON Lines）格式存储，每行是一条消息记录
- Session ID 是 UUID 格式的唯一标识符

## 存储位置

默认存储路径：

```
~/.claude/projects/<sanitized-cwd>/<session-id>.jsonl
```

其中 `<sanitized-cwd>` 是当前工作目录的路径清洗后的结果（将路径分隔符替换为安全字符）。

## 三种 Session 模式

### 1. 新建 Session（默认）

```python
from claude_agent_sdk import ClaudeAgentOptions

options = ClaudeAgentOptions(
    # 不设置任何 session 相关参数，自动创建新 session
)
```

### 2. 继续最近的 Session

```python
options = ClaudeAgentOptions(
    continue_conversation=True,  # 恢复最近一次对话
)
```

恢复后，Agent 可以看到之前对话的全部历史记录，如同对话从未中断。

### 3. 恢复指定 Session

```python
options = ClaudeAgentOptions(
    resume="session-uuid-here",  # 恢复指定 session ID 的对话
)
```

### 4. 分支 Session（Fork）

```python
options = ClaudeAgentOptions(
    resume="session-uuid-here",  # 基于此 session
    fork_session=True,           # 创建分支，而非直接修改原 session
)
```

Fork 会创建一个新的 Session，包含原 Session 的全部历史，后续对话只在新分支中继续，不影响原 Session。

## Session 查询 API

SDK 提供了丰富的 Session 管理函数，可以列出、查看和操作 Session。

### 列出 Session

```python
from claude_agent_sdk import list_sessions

# 列出当前目录的 session 列表
sessions = await list_sessions(
    directory=None,   # None 表示当前目录，也可指定绝对路径
    limit=50,         # 返回数量限制
    offset=0,         # 分页偏移
)

# 返回 list[SDKSessionInfo]
for session in sessions:
    print(f"ID: {session.id}")
    print(f"Title: {session.title}")
    print(f"Created: {session.created_at}")
    print(f"Updated: {session.updated_at}")
    print(f"Tag: {session.tag}")
```

### 获取 Session 详情

```python
from claude_agent_sdk import get_session_info

info = await get_session_info(
    session_id="session-uuid",
    directory=None,
)

print(f"Session: {info.id}")
print(f"Title: {info.title}")
print(f"Messages count: {info.message_count}")
```

### 获取 Session 消息

```python
from claude_agent_sdk import get_session_messages

messages = await get_session_messages(
    session_id="session-uuid",
    directory=None,
    limit=None,    # None 表示获取全部，也可指定数量
    offset=0,      # 从第几条消息开始
)

# 返回 list[SessionMessage]
for msg in messages:
    print(f"Role: {msg.role}, Content: {msg.content[:100]}")
```

### 列出子 Agent 消息

```python
from claude_agent_sdk import list_subagents, get_subagent_messages

# 列出 session 中的子 Agent
subagents = await list_subagents(
    session_id="session-uuid",
    directory=None,
)

for agent in subagents:
    print(f"Subagent: {agent}")

# 获取特定子 Agent 的消息
agent_messages = await get_subagent_messages(
    session_id="session-uuid",
    agent_id="agent-id",
    directory=None,
)
```

## Session 修改 API

### 重命名 Session

```python
from claude_agent_sdk import rename_session

await rename_session(
    session_id="session-uuid",
    title="新标题",
    directory=None,
)
```

### 标记 Session

```python
from claude_agent_sdk import tag_session

# 设置标签
await tag_session(
    session_id="session-uuid",
    tag="important",
    directory=None,
)

# 清除标签
await tag_session(
    session_id="session-uuid",
    tag=None,          # None 清除标签
    directory=None,
)
```

### 删除 Session

```python
from claude_agent_sdk import delete_session

await delete_session(
    session_id="session-uuid",
    directory=None,
)
```

### Fork Session（编程式）

```python
from claude_agent_sdk import fork_session

result = await fork_session(
    session_id="session-uuid",
    directory=None,
    up_to_message_id=None,  # 可选：从指定消息处分叉
    title="分支标题",        # 可选：新 session 标题
)

# 返回 ForkSessionResult
print(f"New session ID: {result.session_id}")
```

`up_to_message_id` 参数允许从历史中的某个特定消息处创建分支，忽略该消息之后的对话。

## SessionStore Protocol

对于需要自定义存储后端（如数据库、云存储）的场景，SDK 定义了 `SessionStore` 协议：

### 必需方法

```python
from typing import Protocol, TypedDict

class SessionKey(TypedDict):
    project_key: str    # 项目标识（通常是目录路径的 hash）
    session_id: str     # Session UUID
    subpath: str        # 子路径（子 Agent 使用）

class SessionStore(Protocol):
    async def append(self, key: SessionKey, entries: list[SessionStoreEntry]) -> None:
        """追加消息到 session"""
        ...

    async def load(self, key: SessionKey) -> list[SessionStoreEntry] | None:
        """加载 session 的全部消息，不存在时返回 None"""
        ...
```

### 可选方法

```python
class SessionStore(Protocol):
    # 必需
    async def append(self, key: SessionKey, entries: list[SessionStoreEntry]) -> None: ...
    async def load(self, key: SessionKey) -> list[SessionStoreEntry] | None: ...

    # 可选
    async def list_sessions(self) -> list[SDKSessionInfo]: ...
    async def list_session_summaries(self) -> list[SDKSessionInfo]: ...
    async def delete(self, key: SessionKey) -> None: ...
    async def list_subkeys(self, key: SessionKey) -> list[str]: ...
```

### InMemorySessionStore

SDK 提供了内存实现作为参考：

```python
from claude_agent_sdk import InMemorySessionStore

store = InMemorySessionStore()

# 使用 store 作为自定义存储
options = ClaudeAgentOptions(
    session_store=store,
)
```

`InMemorySessionStore` 将所有消息存储在 Python 字典中，适合测试和短生命周期场景。

## Store-backed API

当使用自定义 SessionStore 时，可以通过 `*_from_store` 和 `*_via_store` 变体函数操作：

```python
from claude_agent_sdk import (
    list_sessions_from_store,
    get_session_messages_from_store,
    fork_session_via_store,
)

# 从自定义 store 列出 sessions
sessions = await list_sessions_from_store(store)

# 从自定义 store 获取消息
messages = await get_session_messages_from_store(store, session_id="...")

# 通过自定义 store 执行 fork
result = await fork_session_via_store(store, session_id="...", title="Fork")
```

## 工具函数

### project_key_for_directory

```python
from claude_agent_sdk import project_key_for_directory

# 获取目录对应的 project_key
key = project_key_for_directory("/path/to/project")
# 用于构造 SessionKey
```

### import_session_to_store

将文件系统中的 Session 迁移到自定义 Store：

```python
from claude_agent_sdk import import_session_to_store

await import_session_to_store(
    session_id="session-uuid",
    store=my_store,
    directory="/path/to/project",
)
```

## 完整示例：Session 管理器

```python
import anyio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    list_sessions,
    get_session_messages,
    fork_session,
    rename_session,
    delete_session,
    AssistantMessage,
    TextBlock,
)

async def session_manager():
    """演示 Session 的完整生命周期"""

    # 1. 创建新 Session
    options = ClaudeAgentOptions(
        prompt="你是一个编程助手",
        allowed_tools=["Read", "Bash"],
        permission_mode="bypassPermissions",
    )

    async with ClaudeSDKClient(options) as client:
        await client.query("帮我分析当前目录的项目结构")
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

        # 获取当前 session ID
        session_id = client.session_id
        print(f"\n创建了 Session: {session_id}")

    # 2. 列出所有 Session
    sessions = await list_sessions()
    print(f"\n共有 {len(sessions)} 个 Session")

    # 3. 重命名 Session
    await rename_session(session_id, "项目结构分析")
    print("已重命名 Session")

    # 4. 恢复 Session 继续对话
    resume_options = ClaudeAgentOptions(
        resume=session_id,
        allowed_tools=["Read", "Bash"],
        permission_mode="bypassPermissions",
    )

    async with ClaudeSDKClient(resume_options) as client:
        await client.query("基于刚才的分析，有什么改进建议？")
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

    # 5. Fork Session 进行实验性对话
    fork_result = await fork_session(session_id, title="实验性分支")
    print(f"\n创建了分支 Session: {fork_result.session_id}")

    # 6. 查看 Session 消息
    messages = await get_session_messages(session_id)
    print(f"\n原 Session 包含 {len(messages)} 条消息")

    # 7. 清理：删除分支
    await delete_session(fork_result.session_id)
    print("已删除分支 Session")

anyio.run(session_manager)
```

## 注意事项

- Session 文件是 JSONL 格式，每行一个 JSON 对象，可以直接用文本工具查看
- `continue_conversation=True` 恢复的是最近一次同目录下的 Session
- Fork 操作是轻量级的，只复制引用而非完整复制消息
- 自定义 SessionStore 需要实现线程安全（`append` 可能被并发调用）
- `project_key_for_directory` 的输出是确定性的，相同目录总是产生相同的 key
- Session ID 在整个系统中全局唯一，不会跨项目冲突
