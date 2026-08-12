# samples/chapter06/mcp_spanner.py
"""Spanner MCPサーバー（MCP Toolbox）とADKの統合例"""

import os

from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters


# Spanner用のtools.yamlを指定してToolboxを起動
spanner_server = StdioConnectionParams(
    server_params=StdioServerParameters(
        command="npx",
        args=[
            "-y",
            "@toolbox-sdk/server",
            "--stdio",
            "--config", "tools-spanner.yaml",
        ],
        env={"GOOGLE_CLOUD_PROJECT": os.environ.get("GCP_PROJECT_ID", "my-project")},
    )
)

# Spannerデータ参照エージェント
spanner_agent = Agent(
    name="spanner_reader",
    model="gemini-3.5-flash",
    instruction="""あなたはCloud Spannerのデータを参照する分析エージェントです。

    Spannerは分散データベースであり、以下の特性を理解した上でクエリを組み立ててください。
    - 主キーによるアクセスが最も効率的
    - インターリーブテーブルの親子関係を活用する
    - セカンダリインデックスの存在を確認してから使う

    データの参照のみを行い、変更操作は行いません。""",
    tools=[
        McpToolset(
            connection_params=spanner_server,
            tool_filter=["execute_query"],  # 読み取り専用ツールのみ公開
        ),
    ],
)
