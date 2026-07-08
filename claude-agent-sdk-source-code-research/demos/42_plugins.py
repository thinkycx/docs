"""
create: 2026-07-08
update: 2026-07-08
description:
    演示 SdkPluginConfig 结构和使用模式。展示插件目录结构 (package.json manifest)。
    创建临时示例插件目录，展示配置方式，然后以不带插件的基线查询验证流程。
    核心 API: ClaudeAgentOptions.plugins, SdkPluginConfig。
expect_output:
    - 打印 SdkPluginConfig 结构说明 (type: "local", path: 绝对路径)
    - 创建临时插件目录和 package.json manifest
    - 展示 ClaudeAgentOptions 中 plugins 配置代码
    - 基线查询回答 "plugin demo ok"
    - 打印插件可提供的能力列表 (commands, skills, hooks, agents)
usage:
    cd demos && uv run python 42_plugins.py
"""

import os
import tempfile

import anyio
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    SdkPluginConfig,
    TextBlock,
    query,
)


async def main():
    print("=== 插件配置演示 ===")
    print("展示 SdkPluginConfig 结构和使用模式\n")

    # --- 配置说明 ---
    print("[说明] SdkPluginConfig 结构:")
    print('  type: "local" (目前仅支持本地插件)')
    print("  path: 插件目录路径 (绝对路径)\n")

    # --- 配置示例 ---
    plugin_config: SdkPluginConfig = {
        "type": "local",
        "path": "/path/to/my-plugin",
    }
    print(f"[示例] 单个插件配置: {plugin_config}")

    # 多插件配置
    plugins_list = [
        SdkPluginConfig(type="local", path="/path/to/plugin-a"),
        SdkPluginConfig(type="local", path="/path/to/plugin-b"),
    ]
    print(f"[示例] 多插件配置: {plugins_list}\n")

    # --- 创建一个最小的示例插件目录 ---
    print("[演示] 创建临时示例插件目录结构...")
    with tempfile.TemporaryDirectory() as tmpdir:
        plugin_dir = os.path.join(tmpdir, "my-test-plugin")
        os.makedirs(plugin_dir)

        # 创建最小的 plugin manifest (package.json)
        manifest_path = os.path.join(plugin_dir, "package.json")
        with open(manifest_path, "w") as f:
            f.write("""{
  "name": "my-test-plugin",
  "version": "1.0.0",
  "description": "A demo plugin for Claude Code",
  "claude_plugin": {
    "commands": [],
    "skills": [],
    "hooks": []
  }
}""")

        print(f"  插件目录: {plugin_dir}")
        print(f"  manifest: {manifest_path}")
        print(f"  内容: {open(manifest_path).read()[:100]}...\n")

        # --- 使用插件配置 ---
        print("[使用模式] ClaudeAgentOptions 中配置 plugins:")
        print(f"""
    options = ClaudeAgentOptions(
        plugins=[
            SdkPluginConfig(type="local", path="{plugin_dir}"),
        ],
        max_turns=1,
    )
""")

        # 实际运行 (不带真实插件以避免错误)
        print("[实际运行] 不带插件的基线查询 (插件路径需要有效的 Claude Code 插件)")
        print("-" * 40)

        options = ClaudeAgentOptions(
            # 注: 不传入无效插件路径，避免报错
            # plugins=[SdkPluginConfig(type="local", path=plugin_dir)],
            max_turns=1,
        )

        async for msg in query(prompt="Say 'plugin demo ok'.", options=options):
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"  回答: {block.text}")
            elif isinstance(msg, ResultMessage):
                print(f"  完成 (cost: ${msg.total_cost_usd or 0:.6f})")

    print("\n[参考] 插件可以提供:")
    print("  - 自定义命令 (slash commands)")
    print("  - 自定义 skills")
    print("  - 自定义 hooks")
    print("  - 自定义 agents")


if __name__ == "__main__":
    anyio.run(main)
