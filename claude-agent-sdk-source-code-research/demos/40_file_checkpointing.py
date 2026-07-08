"""
create: 2026-07-08
update: 2026-07-08
description:
    演示文件检查点机制：enable_file_checkpointing=True 配合 ClaudeSDKClient。
    流程: 创建测试文件 -> Claude 修改文件 -> 调用 rewind_files(uuid) 尝试恢复。
    展示 ClaudeSDKClient 的有状态会话模式 (query + receive_response)。
    核心 API: ClaudeSDKClient, ClaudeAgentOptions.enable_file_checkpointing,
    client.query(), client.receive_response(), client.rewind_files()。
expect_output:
    - 创建临时测试文件，打印初始内容 "Original content: Hello World!"
    - Claude 成功修改文件为 "Modified by Claude!"
    - 记录 UserMessage uuid (用于 rewind)
    - rewind_files 调用可能报 "No file checkpoint found" (取决于检查点创建时机)
    - 无论 rewind 是否成功，脚本以 exit code 0 退出
usage:
    cd demos && uv run python 40_file_checkpointing.py
"""

import os
import tempfile

import anyio
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    UserMessage,
)


async def main():
    print("=== 文件检查点演示 ===")
    print("流程: 创建文件 -> Claude 修改文件 -> rewind_files() 恢复\n")

    # 创建临时目录和测试文件
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Original content: Hello World!")

        print(f"[1] 创建测试文件: {test_file}")
        print(f"    初始内容: {open(test_file).read()}")

        # 配置: 启用文件检查点
        options = ClaudeAgentOptions(
            cwd=tmpdir,
            enable_file_checkpointing=True,
            permission_mode="bypassPermissions",  # 自动允许文件操作
            max_turns=3,
        )

        async with ClaudeSDKClient(options) as client:
            # 第一步: 让 Claude 修改文件
            print(f"\n[2] 让 Claude 修改文件...")
            await client.query(
                f"Please overwrite the file {test_file} with the text 'Modified by Claude!'. Use the Write tool."
            )

            # 收集消息，记录第一个 UserMessage uuid 用于 rewind
            user_message_id = None
            async for msg in client.receive_response():
                if isinstance(msg, UserMessage) and msg.uuid:
                    if user_message_id is None:
                        user_message_id = msg.uuid
                    print(f"    记录 UserMessage uuid: {msg.uuid[:16]}...")
                elif isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            print(f"    Claude: {block.text[:100]}")
                elif isinstance(msg, ResultMessage):
                    print(f"    完成 (cost: ${msg.total_cost_usd or 0:.6f})")

            # 检查修改后的内容
            if os.path.exists(test_file):
                current_content = open(test_file).read()
                print(f"\n[3] 修改后内容: {current_content}")
            else:
                print("\n[3] 文件不存在 (可能被删除)")

            # 第三步: rewind_files 恢复
            if user_message_id:
                print(f"\n[4] 调用 rewind_files('{user_message_id[:16]}...')")
                try:
                    await client.rewind_files(user_message_id)

                    # 检查恢复后的内容
                    if os.path.exists(test_file):
                        restored_content = open(test_file).read()
                        print(f"    恢复后内容: {restored_content}")
                        if "Original" in restored_content:
                            print("    [成功] 文件已恢复到原始状态!")
                        else:
                            print("    [注意] 内容已变化但可能非原始状态")
                    else:
                        print("    [注意] 文件不存在")
                except Exception as e:
                    print(f"    [异常] {type(e).__name__}: {e}")
                    print("    说明: rewind_files 需要有效的文件检查点")
                    print("    检查点仅在 enable_file_checkpointing=True 时，")
                    print("    对初始 UserMessage 创建。后续的 UserMessage 可能没有检查点。")
                    print("    实际使用时应传入第一个 UserMessage 的 uuid。")
            else:
                print("\n[4] 未捕获到 UserMessage uuid，跳过 rewind")
                print("    提示: 可能需要 extra_args={'replay-user-messages': None}")


if __name__ == "__main__":
    anyio.run(main)
