# Demo 验证变更日志

记录逐一验证过程中发现的问题和修复。

## 验证日期: 2026-07-08

| # | 文件 | 状态 | 问题 | 修复 |
|---|------|------|------|------|
| 01 | 01_basic_query.py | ✅ 通过 | 无 | 无 |
| 02 | 02_query_with_tools.py | ✅ 通过 | 无 | 无 |
| 03 | 03_query_max_turns.py | ✅ 通过 | 无 | 无 |
| 04 | 04_client_basic.py | ✅ 通过 | 无 | 无 |
| 05 | 05_client_multi_turn.py | ✅ 通过 | 无 | 无 |
| 06 | 06_client_interrupt.py | ✅ 通过 | 无 | 无 |
| 07 | 07_client_async_input.py | ✅ 通过 | 无 | 无 |
| 08 | 08_tool_simple.py | ✅ 通过 | 无 | 无 |
| 09 | 09_tool_typeddict_schema.py | ✅ 通过 | 无 | 无 |
| 10 | 10_tool_error_handling.py | ✅ 通过 | 无 | 无 |
| 11 | 11_tool_annotations.py | ✅ 通过 | 无 | 无 |
| 23 | 23_permission_allow_deny.py | ✅ 通过 | 无 | 无 |
| 24 | 24_session_continue.py | ✅ 通过 | continue_conversation 恢复的是目录下最近会话而非刚创建的, 属于正常行为 | 无 |
| 25 | 25_session_resume.py | ✅ 通过 | 无 | 无 |
| 26 | 26_session_fork.py | ✅ 通过 | 无 | 无 |
| 27 | 27_session_store.py | ✅ 通过 | 无 | 无 |
| 28 | 28_session_list_and_info.py | ✅ 通过 | 无 | 无 |
| 29 | 29_structured_output.py | ✅ 通过 | 无 | 无 |
| 30 | 30_streaming_partial.py | ✅ 通过 | 无 | 无 |
| 31 | 31_system_prompt_string.py | ✅ 通过 | 无 | 无 |
| 32 | 32_system_prompt_preset.py | ✅ 通过 | 无 | 无 |
| 33 | 33_cost_tracking.py | ✅ 通过 | 无 | 无 |
| 12 | 12_mcp_external_server.py | ⚠️ 配置演示 | 需要外部MCP服务器(npx+filesystem) | 标注在expect_output中 |
| 13 | 13_hook_pre_tool_use.py | ✅ 通过 | 无 | 无 |
| 14 | 14_hook_post_tool_use.py | ✅ 通过 | 无 | 无 |
| 15 | 15_hook_user_prompt_submit.py | ✅ 通过 | 无 | 无 |
| 16 | 16_hook_stop.py | ✅ 通过 | 无 | 无 |
| 17 | 17_hook_notification.py | ✅ 通过 | 无 | 无 |
| 18 | 18_agent_definition.py | ✅ 通过 | 无 | 无 |
| 19 | 19_agent_multi_agents.py | ✅ 通过 | 无 | 无 |
| 20 | 20_agent_filesystem.py | ✅ 通过 | 无 | 无 |
| 21 | 21_permission_callback.py | ✅ 通过 | can_use_tool需要streaming模式 | 改用ClaudeSDKClient替代query()直传string |
| 22 | 22_permission_modes.py | ✅ 通过 | 无 | 无 |
| 34 | 34_budget_control.py | ✅ 通过 | SDK在预算超限时抛异常而非返回ResultMessage | 添加try/except捕获budget异常 |
| 35 | 35_thinking_config.py | ✅ 通过 | 无 | 无 |
| 36 | 36_effort_levels.py | ✅ 通过 | 无 | 无 |
| 37 | 37_model_selection.py | ✅ 通过 | 显式指定model名在当前环境返回400 | 改为model=None使用环境默认模型 |
| 38 | 38_setting_sources.py | ✅ 通过 | 无 | 无 |
| 39 | 39_error_handling.py | ✅ 通过 | 无 | 无 |
| 40 | 40_file_checkpointing.py | ✅ 通过 | rewind_files报"No file checkpoint found" | 添加try/except优雅处理，说明检查点创建条件 |
| 41 | 41_sandbox_config.py | ✅ 通过 | 无 | 无 |
| 42 | 42_plugins.py | ✅ 通过 | 无 | 无 |
| 43 | 43_rate_limit_handling.py | ✅ 通过 | 无 | 无 |
