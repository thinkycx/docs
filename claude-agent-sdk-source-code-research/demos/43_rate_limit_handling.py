"""
create: 2026-07-08
update: 2026-07-08
description:
    演示 RateLimitEvent 处理模式。展示 RateLimitInfo 结构 (status, rate_limit_type,
    resets_at, utilization, overage_status)，并在实际查询中监听该事件。
    正常使用中通常不会触发 RateLimitEvent，演示展示完整的处理逻辑和推荐策略。
    核心 API: query(), RateLimitEvent, RateLimitInfo。
expect_output:
    - 打印 RateLimitEvent 和 RateLimitInfo 结构说明
    - 运行查询并监听 RateLimitEvent
    - 正常回答 "hello" 或类似简短内容
    - 总结: "未收到 RateLimitEvent (正常情况，表示未触及速率限制)"
    - 打印推荐处理策略 (allowed/allowed_warning/rejected 三种状态)
usage:
    cd demos && uv run python 43_rate_limit_handling.py
"""

import time

import anyio
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    RateLimitEvent,
    ResultMessage,
    TextBlock,
    query,
)


async def main():
    print("=== Rate Limit 处理演示 ===")
    print("说明: RateLimitEvent 在速率限制状态变化时由 CLI 发出")
    print("      通常在正常使用中不会触发，此演示展示处理模式\n")

    # --- RateLimitEvent 结构说明 ---
    print("[结构] RateLimitEvent:")
    print("  rate_limit_info: RateLimitInfo")
    print("    .status: 'allowed' | 'allowed_warning' | 'rejected'")
    print("    .rate_limit_type: 'five_hour' | 'seven_day' | 'seven_day_opus' | 'seven_day_sonnet' | 'overage'")
    print("    .resets_at: Unix timestamp (秒)")
    print("    .utilization: 0.0 - 1.0 (已使用比例)")
    print("    .overage_status: 超额状态")
    print("    .overage_disabled_reason: 超额不可用原因")
    print("  uuid: 事件唯一标识")
    print("  session_id: 会话 ID\n")

    # --- 处理模式演示 ---
    print("[处理模式] 运行查询并监听 RateLimitEvent...")
    print("-" * 50)

    options = ClaudeAgentOptions(max_turns=1)
    rate_limit_events = []

    async for msg in query(prompt="Say 'hello' briefly.", options=options):
        # 检测 RateLimitEvent
        if isinstance(msg, RateLimitEvent):
            rate_limit_events.append(msg)
            info = msg.rate_limit_info

            print(f"\n  [RateLimitEvent 检测到!]")
            print(f"    status: {info.status}")
            print(f"    type: {info.rate_limit_type}")
            print(f"    utilization: {info.utilization}")

            if info.resets_at:
                remaining = info.resets_at - int(time.time())
                print(f"    resets_at: {info.resets_at} (剩余 {remaining}s)")

            # 根据状态采取行动
            if info.status == "rejected":
                print("    [动作] 速率限制已触发! 应暂停请求。")
                if info.resets_at:
                    wait_seconds = max(0, info.resets_at - int(time.time()))
                    print(f"    [建议] 等待 {wait_seconds} 秒后重试")
            elif info.status == "allowed_warning":
                print("    [动作] 接近速率限制! 考虑减慢请求频率。")
                if info.utilization:
                    print(f"    [信息] 已使用 {info.utilization * 100:.1f}% 的配额")
            else:
                print("    [动作] 状态正常，可继续请求。")

        elif isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"  回答: {block.text}")

        elif isinstance(msg, ResultMessage):
            print(f"  完成 (cost: ${msg.total_cost_usd or 0:.6f})")

    # 总结
    print(f"\n--- 总结 ---")
    if rate_limit_events:
        print(f"  收到 {len(rate_limit_events)} 个 RateLimitEvent")
    else:
        print("  未收到 RateLimitEvent (正常情况，表示未触及速率限制)")

    # --- 推荐处理策略 ---
    print(f"\n[推荐策略]")
    print("  1. status='allowed': 正常继续")
    print("  2. status='allowed_warning': 日志记录，考虑降低请求频率")
    print("  3. status='rejected': 停止请求，等待 resets_at 后重试")
    print("  4. 使用 utilization 字段做渐进式限流")
    print("  5. 检查 overage_status 判断是否可以付费超额使用")


if __name__ == "__main__":
    anyio.run(main)
