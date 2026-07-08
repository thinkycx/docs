"""
create: 2026-07-08
update: 2026-07-08
description:
    演示全面的错误处理模式：try/except 各种 SDK 异常 + ResultMessage.subtype 检测。
    演示1: 正常查询，展示 ResultMessage.subtype == "success" 的检测。
    演示2: 使用无效 CLI 路径触发 CLINotFoundError 异常。
    并附带异常继承关系和 ResultMessage.subtype 可能值参考。
    核心 API: ClaudeSDKError, CLINotFoundError, CLIConnectionError, ProcessError,
    CLIJSONDecodeError, ResultMessage.subtype。
expect_output:
    - 演示1: 正常回答 + subtype: success, is_error: False
    - 演示2: 捕获 CLINotFoundError，打印 "Claude Code not found at: /nonexistent/path/to/claude"
    - 打印异常继承关系图 (ClaudeSDKError 为基类)
    - 打印 ResultMessage.subtype 五种可能值
usage:
    cd demos && uv run python 39_error_handling.py
"""

import anyio
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKError,
    CLIConnectionError,
    CLIJSONDecodeError,
    CLINotFoundError,
    ProcessError,
    ResultMessage,
    TextBlock,
    query,
)


async def demo_error_handling():
    """演示正常查询中的错误处理模式"""
    print("=== 错误处理演示 ===\n")

    # --- 演示 1: 正常查询 + ResultMessage subtype 检测 ---
    print("[演示 1] 正常查询 - 检测 ResultMessage.subtype")
    print("-" * 40)

    options = ClaudeAgentOptions(max_turns=1)

    try:
        async for msg in query(prompt="Say 'hello'.", options=options):
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"  回答: {block.text}")

            elif isinstance(msg, ResultMessage):
                print(f"  subtype: {msg.subtype}")
                print(f"  is_error: {msg.is_error}")

                # 检测各种 ResultMessage 子类型
                match msg.subtype:
                    case "success":
                        print("  [状态] 查询成功完成")
                    case "error_max_turns":
                        print("  [状态] 达到最大轮次限制")
                    case "error_max_budget_usd":
                        print("  [状态] 超出预算限制")
                    case "error_during_execution":
                        print("  [状态] 执行期间发生错误")
                    case "error_max_structured_output_retries":
                        print("  [状态] 结构化输出重试次数超限")
                    case _:
                        print(f"  [状态] 未知子类型: {msg.subtype}")

    except CLINotFoundError as e:
        print(f"  [CLINotFoundError] Claude CLI 未找到: {e}")
        print("  解决方案: 确保 claude CLI 已安装并在 PATH 中")

    except CLIConnectionError as e:
        print(f"  [CLIConnectionError] CLI 连接失败: {e}")
        print("  解决方案: 检查 CLI 进程是否正常运行")

    except CLIJSONDecodeError as e:
        print(f"  [CLIJSONDecodeError] JSON 解析失败: {e}")
        print("  解决方案: CLI 输出格式异常，检查 CLI 版本")

    except ProcessError as e:
        print(f"  [ProcessError] 进程错误: {e}")
        print("  解决方案: CLI 进程异常退出")

    except ClaudeSDKError as e:
        # 基础异常类，捕获所有 SDK 异常
        print(f"  [ClaudeSDKError] SDK 错误: {e}")

    # --- 演示 2: 无效 CLI 路径触发 CLINotFoundError ---
    print(f"\n[演示 2] 无效 CLI 路径 - 触发异常")
    print("-" * 40)

    options_bad = ClaudeAgentOptions(
        cli_path="/nonexistent/path/to/claude",
        max_turns=1,
    )

    try:
        async for msg in query(prompt="hello", options=options_bad):
            pass
    except (CLINotFoundError, ProcessError, ClaudeSDKError) as e:
        print(f"  [捕获] {type(e).__name__}: {str(e)[:100]}")
        print("  预期行为: 无效 CLI 路径应抛出异常")
    except FileNotFoundError as e:
        print(f"  [捕获] FileNotFoundError: {str(e)[:100]}")
        print("  预期行为: 操作系统找不到指定路径")

    # --- 异常继承关系说明 ---
    print(f"\n[参考] 异常继承关系:")
    print("  ClaudeSDKError (基类)")
    print("    ├── CLINotFoundError  - CLI 可执行文件未找到")
    print("    ├── CLIConnectionError - 连接/通信失败")
    print("    ├── ProcessError - 进程异常退出")
    print("    └── CLIJSONDecodeError - 输出解析失败")

    print(f"\n[参考] ResultMessage.subtype 可能的值:")
    print("    - success: 正常完成")
    print("    - error_max_turns: 达到最大轮次")
    print("    - error_max_budget_usd: 超出预算")
    print("    - error_during_execution: 执行错误")
    print("    - error_max_structured_output_retries: 结构化输出重试超限")


async def main():
    await demo_error_handling()


if __name__ == "__main__":
    anyio.run(main)
