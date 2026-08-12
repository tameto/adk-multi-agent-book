# samples/chapter06/mcp_firestore.py
"""Firestore MCPサーバー（MCP Toolbox）とADKの統合例"""

import os

from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters


# Firestore用のtools.yamlを指定してToolboxを起動
firestore_server = StdioConnectionParams(
    server_params=StdioServerParameters(
        command="npx",
        args=[
            "-y",
            "@toolbox-sdk/server",
            "--stdio",
            "--config", "tools-firestore.yaml",
        ],
        env={"GOOGLE_CLOUD_PROJECT": os.environ.get("GCP_PROJECT_ID", "my-project")},
    )
)

# ドキュメント管理エージェント
doc_agent = Agent(
    name="firestore_agent",
    model="gemini-3.5-flash",
    instruction="""あなたはFirestoreのドキュメントデータを管理するエージェントです。

    ## 利用可能なコレクション
    - users: ユーザー情報
    - orders: 注文データ
    - products: 商品マスタ

    ## 操作方針
    - 参照操作は自由に実行する
    - ドキュメントの作成・更新はユーザーの承認後に実行する
    - コレクション全体の削除は行わない""",
    tools=[
        McpToolset(connection_params=firestore_server),
    ],
)
