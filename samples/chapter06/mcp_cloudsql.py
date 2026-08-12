# samples/chapter06/mcp_cloudsql.py
"""Cloud SQL MCPサーバー（MCP Toolbox）とADKの統合例"""

import os

from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters


# Cloud SQL用のtools.yamlを指定してToolboxを起動
cloudsql_server = StdioConnectionParams(
    server_params=StdioServerParameters(
        command="npx",
        args=[
            "-y",
            "@toolbox-sdk/server",
            "--stdio",
            "--config", "tools-cloudsql.yaml",
        ],
        env={
            "GOOGLE_CLOUD_PROJECT": os.environ.get("GCP_PROJECT_ID", "my-project"),
            "DB_PASSWORD": os.environ.get("DB_PASSWORD", ""),
        },
    )
)

# 業務データベース操作エージェント
db_agent = Agent(
    name="db_operator",
    model="gemini-3.5-flash",
    instruction="""あなたはCloud SQL上の業務データベースを操作するエージェントです。

    ## 権限
    - SELECT: 許可
    - INSERT/UPDATE: ユーザーの明示的な承認後のみ実行
    - DELETE/DROP: 禁止

    ## 操作の手順
    1. テーブル構造を確認する
    2. ユーザーの要求を理解し、必要なクエリを構築する
    3. SELECTクエリは即座に実行する
    4. データ変更クエリは、実行前にSQLの内容をユーザーに提示し承認を得る""",
    tools=[
        McpToolset(connection_params=cloudsql_server),
    ],
)
