---
create: 2026-07-08
update: 2026-07-08
author: thinkycx
title: 【译】Agent SDK - 会话存储
description: Claude Agent SDK 会话持久化存储指南，涵盖 SessionStore 接口设计、InMemorySessionStore 快速入门、S3/Redis/Postgres 参考实现、双写架构、子代理支持及适配器验证。
category: translation
tags: [claude-code, agent-sdk, translation]
refs:
  - https://code.claude.com/docs/en/agent-sdk/session-storage
  - en-source/agent-sdk/session-storage.md
---

# 会话持久化到外部存储

> 将会话 transcript 镜像到 S3、Redis 或你自己的后端，让任何主机都能恢复它们。

**默认情况下，SDK 将会话 transcript 写入本地文件系统 `~/.claude/projects/` 下的 JSONL 文件。** `SessionStore` 适配器让你将这些 transcript 镜像到自己的后端——如 S3、Redis 或数据库——这样在一台主机创建的会话可以在另一台恢复。

常见使用原因：

* **多主机部署。** Serverless 函数、自动伸缩的 worker 和 CI runner 不共享文件系统。共享存储让任何副本都能恢复任何会话。
* **持久性。** 本地容器是临时的。基于 S3 或数据库的存储可以在重启和重新部署后存活。
* **合规与审计。** 将 transcript 保存在你已管控的存储中，使用你自己的保留策略、加密和访问控制。

## `SessionStore` 接口

**`SessionStore` 是一个包含两个必需方法 `append` 和 `load`，以及三个可选方法的对象。** SDK 在查询期间调用 `append` 写入 transcript 条目，调用 `load` 在恢复时读回。

```typescript
// 从 @anthropic-ai/claude-agent-sdk 导出为
// SessionStore, SessionKey, SessionStoreEntry.

type SessionKey = {
  projectKey: string;
  sessionId: string;
  subpath?: string;
};

type SessionStore = {
  // 必需
  append(key: SessionKey, entries: SessionStoreEntry[]): Promise<void>;
  load(key: SessionKey): Promise<SessionStoreEntry[] | null>;

  // 可选
  listSessions?(
    projectKey: string,
  ): Promise<Array<{ sessionId: string; mtime: number }>>;
  delete?(key: SessionKey): Promise<void>;
  listSubkeys?(key: {
    projectKey: string;
    sessionId: string;
  }): Promise<string[]>;
};
```

```python
# 从 claude_agent_sdk 导出为
# SessionStore, SessionKey, SessionStoreEntry.

class SessionKey(TypedDict):
    project_key: str
    session_id: str
    subpath: NotRequired[str]

class SessionStore(Protocol):
    # 必需
    async def append(
        self, key: SessionKey, entries: list[SessionStoreEntry]
    ) -> None: ...
    async def load(self, key: SessionKey) -> list[SessionStoreEntry] | None: ...

    # 可选 — 省略或抛出 NotImplementedError
    async def list_sessions(
        self, project_key: str
    ) -> list[SessionStoreListEntry]: ...
    async def delete(self, key: SessionKey) -> None: ...
    async def list_subkeys(self, key: SessionListSubkeysKey) -> list[str]: ...
```

**`SessionKey` 标识一条 transcript。** `projectKey` 是工作目录的稳定、文件系统安全编码，`sessionId` 是会话 UUID，`subpath` 在条目属于子代理 transcript 或附属文件（而非主对话）时设置。将 `subpath` 视为不透明的键后缀；它遵循磁盘上的布局，例如 `subagents/agent-<id>`。`subpath` 未定义时键指向主 transcript。

| 方法 | 必需 | 调用时机 |
|:---|:---|:---|
| `append` | 是 | 每批 transcript 条目写入本地后。条目是 JSON 安全对象，对应本地 JSONL 中的一行。 |
| `load` | 是 | 设置 `resume` 时子进程启动前调用一次。会话未知时返回 `null`。 |
| `listSessions` | 否 | 由 `listSessions({ sessionStore })` 和 `query()`/`startup()` 设置 `continue: true` 时调用。未定义时这些调用会抛出异常。 |
| `delete` | 否 | 由 `deleteSession({ sessionStore })` 调用。删除主键（无 `subpath`）时必须级联到该会话的所有子键。未定义时删除为空操作——适合只追加的后端。 |
| `listSubkeys` | 否 | 恢复期间用于发现子代理 transcript。未定义时只恢复主 transcript。 |

## 快速入门

**SDK 附带 `InMemorySessionStore` 用于开发和测试。** 以下示例将 store 附加到一次查询，从 result 消息捕获 session ID，然后在第二次 `query()` 调用中从 store 恢复。第二次调用传入同一 store 实例加 `resume`，SDK 从 store 而非本地文件系统加载 transcript：

```typescript
import { query, InMemorySessionStore } from "@anthropic-ai/claude-agent-sdk";

const store = new InMemorySessionStore();

let sessionId: string | undefined;
for await (const message of query({
  prompt: "List the TypeScript files under src/",
  options: { sessionStore: store },
})) {
  if (message.type === "result") {
    sessionId = message.session_id;
  }
}

// 从 store 恢复。agent 拥有第一次调用的完整上下文。
for await (const message of query({
  prompt: "Summarize what those files do",
  options: { sessionStore: store, resume: sessionId },
})) {
  if (message.type === "result" && message.subtype === "success") {
    console.log(message.result);
  }
}
```

```python
import asyncio
from claude_agent_sdk import (
    ClaudeAgentOptions,
    InMemorySessionStore,
    ResultMessage,
    query,
)

store = InMemorySessionStore()


async def main():
    session_id = None
    async for message in query(
        prompt="List the Python files under src/",
        options=ClaudeAgentOptions(session_store=store),
    ):
        if isinstance(message, ResultMessage):
            session_id = message.session_id

    # 从 store 恢复。agent 拥有第一次调用的完整上下文。
    async for message in query(
        prompt="Summarize what those files do",
        options=ClaudeAgentOptions(session_store=store, resume=session_id),
    ):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(message.result)


asyncio.run(main())
```

第二次查询打印第一次查询中文件的摘要，证明 agent 从 store 恢复了完整上下文。

## 编写自己的适配器

**对你的后端实现 `append` 和 `load`。** 如果需要 `listSessions()`、`deleteSession()` 和子代理恢复对 store 工作，添加 `listSessions`、`delete` 和 `listSubkeys`。

传给 `append` 的条目类型为 `SessionStoreEntry`（一个 `{ type: string; ... }` 对象）。将它们视为不透明的 JSON 安全值：按顺序持久化，从 `load` 中按相同顺序返回。`load` 必须返回与 appended 内容 deep-equal 的条目；不要求字节级相同的序列化，所以像 Postgres `jsonb` 这种重新排列对象键的后端也可以。

## 参考实现

**TypeScript SDK 仓库在 [`examples/session-stores/`](https://github.com/anthropics/claude-agent-sdk-typescript/tree/main/examples/session-stores) 下包含可运行的 S3、Redis 和 Postgres 参考适配器。** 它们未发布到 npm；将你需要的 `src/` 文件复制到项目中并安装对应的后端客户端。

| 适配器 | 后端客户端 | 存储模型 |
|:---|:---|:---|
| [`S3SessionStore`](https://github.com/anthropics/claude-agent-sdk-typescript/tree/main/examples/session-stores/s3) | `@aws-sdk/client-s3` | 每次 `append()` 一个 JSONL 分片文件；`load()` 列出、排序并拼接。 |
| [`RedisSessionStore`](https://github.com/anthropics/claude-agent-sdk-typescript/tree/main/examples/session-stores/redis) | `ioredis` | 每个 transcript 一个 `RPUSH`/`LRANGE` list，加一个 sorted-set 会话索引。 |
| [`PostgresSessionStore`](https://github.com/anthropics/claude-agent-sdk-typescript/tree/main/examples/session-stores/postgres) | `pg` | `jsonb` 表中每条目一行，按 `BIGSERIAL` 排序。 |

每个适配器接收预配置的客户端实例，所以你控制凭据、TLS、区域和连接池。例如使用 S3：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";
import { S3Client } from "@aws-sdk/client-s3";
import { S3SessionStore } from "./S3SessionStore"; // 从 examples/session-stores/s3 复制

const store = new S3SessionStore({
  bucket: "my-claude-sessions",
  prefix: "transcripts",
  client: new S3Client({ region: "us-east-1" }),
});

for await (const message of query({
  prompt: "Hello!",
  options: { sessionStore: store },
})) {
  if (message.type === "result" && message.subtype === "success") {
    console.log(message.result);
  }
}

// 稍后，可能在不同主机上：
for await (const message of query({
  prompt: "Continue where we left off",
  options: { sessionStore: store, resume: "previous-session-id" },
})) {
  // ...
}
```

### 验证你的适配器

**两个 SDK 都附带一致性测试套件**，断言 `append`、`load` 和可选方法必须满足的行为契约。可选方法未实现时测试自动跳过。

TypeScript 中，从示例目录复制 [`shared/conformance.ts`](https://github.com/anthropics/claude-agent-sdk-typescript/blob/main/examples/session-stores/shared/conformance.ts) 到你的测试套件。Python 中，套件随包发布：

```python
import pytest
from claude_agent_sdk.testing import run_session_store_conformance


@pytest.mark.asyncio
async def test_my_store_conformance():
    await run_session_store_conformance(MyRedisStore)
```

## 行为说明

### 双写架构

**store 是镜像，不是替代。** Claude Code 子进程总是先写入本地磁盘；然后 SDK 将每批数据转发给 `append()`。如果想让本地副本临时存在，在 `options.env` 中将 `CLAUDE_CONFIG_DIR` 指向临时目录。因为镜像依赖本地写入，`sessionStore` 不能与 `persistSession: false` 组合——同时设置两者时 SDK 会抛出异常。也不能与 `enableFileCheckpointing` 组合，因为文件历史备份 blob 直接写入本地磁盘而不镜像到 store。

### 镜像写入是尽力而为

**如果 `append()` 拒绝，SDK 最多重试两次（短暂退避），总共最多三次尝试。** 超时的调用不重试，因为原始调用可能仍然落地。如果批次仍然失败，错误被记录，一条 `{ type: "system", subtype: "mirror_error" }` 消息被发出到迭代器中，批次被丢弃，查询继续。本地 transcript 已经在磁盘上持久化，所以 store 中断不会打断 agent 或丢失本地数据。如果需要检测 store 数据丢失，监控 `mirror_error`。因为重试的批次可能重复投递已落地的条目，在你的 `append()` 实现中按 `entry.uuid` 去重。

### `getSessionMessages` 返回压缩后的链

**`getSessionMessages({ sessionStore })` 返回 agent 恢复时会看到的链接消息链。** 自动压缩后，早期轮次被摘要替代，所以一个 store 中有 503 条原始条目的会话可能从 `getSessionMessages` 返回 18 条消息。要获取完整原始历史（包括压缩前的轮次和元数据条目），直接调用 `store.load(key)`。

### `forkSession` 不是字节拷贝

**`forkSession({ sessionStore })` 读取源条目，重写每个 `sessionId` 字段并重新映射消息 UUID，然后在新键下追加转换后的条目。** 适配器级别的拷贝或 `CopyObject` 快捷方式会产生仍引用旧 session ID 的 transcript，所以 SDK 不使用它。

### 子代理 transcript

**子代理 transcript 在 `subpath: "subagents/agent-<id>"` 下镜像。** `listSubagents({ sessionStore })` 需要适配器实现 `listSubkeys`；`getSubagentMessages({ sessionStore })` 可用时使用它，不可用时回退到直接 subpath。恢复时也调用 `listSubkeys` 来还原子代理文件；没有它只有主 transcript 被物化。

### 保留策略

**SDK 从不主动从你的 store 中删除数据。** 保留策略是适配器的责任：根据合规要求实现 TTL、S3 生命周期策略或计划清理。`CLAUDE_CONFIG_DIR` 下的本地 transcript 由 `cleanupPeriodDays` 设置独立清扫。

## 支持的函数

以下 SDK 函数接受 `sessionStore` 选项，提供时操作 store 而非本地文件系统：

* [`query()`](https://code.claude.com/docs/en/agent-sdk/typescript#query)
* [`startup()`](https://code.claude.com/docs/en/agent-sdk/typescript#startup)
* [`listSessions()`](https://code.claude.com/docs/en/agent-sdk/typescript#listsessions)
* [`getSessionInfo()`](https://code.claude.com/docs/en/agent-sdk/typescript#getsessioninfo)
* [`getSessionMessages()`](https://code.claude.com/docs/en/agent-sdk/typescript#getsessionmessages)
* [`renameSession()`](https://code.claude.com/docs/en/agent-sdk/typescript#renamesession)
* [`tagSession()`](https://code.claude.com/docs/en/agent-sdk/typescript#tagsession)
* [`deleteSession()`](https://code.claude.com/docs/en/agent-sdk/typescript)
* [`forkSession()`](https://code.claude.com/docs/en/agent-sdk/typescript)
* [`listSubagents()`](https://code.claude.com/docs/en/agent-sdk/typescript)
* [`getSubagentMessages()`](https://code.claude.com/docs/en/agent-sdk/typescript)

## 相关资源

* [使用会话](https://code.claude.com/docs/en/agent-sdk/sessions)：无需自定义 store 的继续、恢复和分叉
* [托管 SDK](https://code.claude.com/docs/en/agent-sdk/hosting)：多主机环境的部署模式
* [TypeScript `Options`](https://code.claude.com/docs/en/agent-sdk/typescript#options)：完整选项参考
* [`examples/session-stores/`](https://github.com/anthropics/claude-agent-sdk-typescript/tree/main/examples/session-stores)：可运行的 S3、Redis 和 Postgres 参考适配器
