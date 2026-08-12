# mcp_toolset_example.py
# 2-6-4. McpToolset: MCPサーバーの統合（完全版）
# MCPサーバーが公開するツール群をADKのBaseTool互換に変換してLLMに渡す。
# 接続ライフサイクルはRunnerが自動管理する。

from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

# MCPサーバーへの接続（Streamable HTTP方式、v2.2.0でも推奨）
mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="http://localhost:3000/mcp",
    ),
)

# MCPツールセットをエージェントのtoolsに渡す
agent = Agent(
    name="data_agent",
    model="gemini-3.5-flash",
    instruction="ユーザーのデータ分析要求に応えてください。",
    tools=[mcp_toolset],
)

# adk run / adk web から参照できるようroot_agentとして公開する（補完）
root_agent = agent

if __name__ == "__main__":
    # 定義内容の確認（実行には localhost:3000 でMCPサーバーの起動が必要）
    print(f"エージェント: {agent.name}")
    print("接続方式: Streamable HTTP（http://localhost:3000/mcp）")
