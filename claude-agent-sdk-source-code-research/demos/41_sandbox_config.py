"""
create: 2026-07-08
update: 2026-07-08
description:
    演示 SandboxSettings 配置结构：基本沙箱、网络配置、忽略规则、完整配置四种模式。
    最后以基本沙箱配置运行实际查询验证兼容性。
    核心 API: ClaudeAgentOptions.sandbox, SandboxSettings, SandboxNetworkConfig,
    SandboxIgnoreViolations。
expect_output:
    - 打印四种配置结构示例 (基本/网络/忽略规则/完整)
    - 带基本沙箱配置运行查询，回答 "sandbox test ok"
    - 打印 cost 统计
    - 如果环境不支持沙箱，打印异常提示
usage:
    cd demos && uv run python 41_sandbox_config.py
"""

import anyio
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    SandboxIgnoreViolations,
    SandboxNetworkConfig,
    SandboxSettings,
    TextBlock,
    query,
)


async def main():
    print("=== Sandbox 配置演示 ===")
    print("展示 SandboxSettings 的配置结构和字段\n")

    # --- 配置示例 1: 基本沙箱 ---
    sandbox_basic: SandboxSettings = {
        "enabled": True,
        "autoAllowBashIfSandboxed": True,
    }
    print("[配置 1] 基本沙箱")
    print(f"  {sandbox_basic}\n")

    # --- 配置示例 2: 带网络配置的沙箱 ---
    network_config: SandboxNetworkConfig = {
        "allowedDomains": ["api.github.com", "pypi.org"],
        "deniedDomains": ["evil.com"],
        "allowLocalBinding": True,
        "allowUnixSockets": ["/var/run/docker.sock"],
    }
    sandbox_network: SandboxSettings = {
        "enabled": True,
        "autoAllowBashIfSandboxed": True,
        "excludedCommands": ["git", "docker"],
        "network": network_config,
    }
    print("[配置 2] 带网络配置的沙箱")
    print(f"  enabled: True")
    print(f"  autoAllowBashIfSandboxed: True")
    print(f"  excludedCommands: ['git', 'docker']")
    print(f"  network.allowedDomains: {network_config['allowedDomains']}")
    print(f"  network.deniedDomains: {network_config['deniedDomains']}")
    print(f"  network.allowLocalBinding: True")
    print(f"  network.allowUnixSockets: {network_config['allowUnixSockets']}\n")

    # --- 配置示例 3: 带忽略规则的沙箱 ---
    ignore_violations: SandboxIgnoreViolations = {
        "file": ["/tmp/allowed_path"],
        "network": ["localhost:3000"],
    }
    sandbox_ignore: SandboxSettings = {
        "enabled": True,
        "autoAllowBashIfSandboxed": True,
        "ignoreViolations": ignore_violations,
    }
    print("[配置 3] 带忽略规则的沙箱")
    print(f"  ignoreViolations.file: {ignore_violations['file']}")
    print(f"  ignoreViolations.network: {ignore_violations['network']}\n")

    # --- 配置示例 4: 完整配置 ---
    sandbox_full: SandboxSettings = {
        "enabled": True,
        "autoAllowBashIfSandboxed": True,
        "excludedCommands": ["git", "docker", "npm"],
        "allowUnsandboxedCommands": False,
        "network": {
            "allowedDomains": ["*.npmjs.org", "api.github.com"],
            "deniedDomains": [],
            "allowLocalBinding": True,
            "allowUnixSockets": [],
        },
        "ignoreViolations": {
            "file": ["/tmp"],
            "network": [],
        },
    }
    print("[配置 4] 完整配置")
    print(f"  allowUnsandboxedCommands: False (强制所有命令在沙箱内)")
    print(f"  excludedCommands: ['git', 'docker', 'npm'] (这些命令不受沙箱限制)\n")

    # --- 实际使用: 带沙箱配置运行查询 ---
    print("[实际使用] 带基本沙箱配置运行查询")
    print("-" * 40)

    options = ClaudeAgentOptions(
        sandbox=sandbox_basic,
        max_turns=1,
    )

    try:
        async for msg in query(prompt="Say 'sandbox test ok'.", options=options):
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"  回答: {block.text}")
            elif isinstance(msg, ResultMessage):
                print(f"  完成 (cost: ${msg.total_cost_usd or 0:.6f})")
    except Exception as e:
        print(f"  [注意] 沙箱可能在当前环境不支持: {type(e).__name__}: {str(e)[:100]}")
        print("  沙箱仅在 macOS/Linux 上支持")


if __name__ == "__main__":
    anyio.run(main)
