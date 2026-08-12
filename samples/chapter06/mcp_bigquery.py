# samples/chapter06/mcp_bigquery.py
"""BigQuery MCPサーバー（MCP Toolbox）とADKの統合例"""

import os

from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters


# MCP Toolboxを起動して tools.yaml の定義をMCPツールとして公開
bigquery_server = StdioConnectionParams(
    server_params=StdioServerParameters(
        command="npx",
        args=[
            "-y",
            "@toolbox-sdk/server",
            "--stdio",
            "--config", os.environ.get("TOOLBOX_CONFIG", "tools.yaml"),
        ],
        env={"GOOGLE_CLOUD_PROJECT": os.environ.get("GCP_PROJECT_ID", "my-project")},
    )
)

# データ分析エージェント
data_analyst = Agent(
    name="data_analyst",
    model="gemini-3.5-flash",
    instruction="""あなたはBigQueryを使ったデータ分析の専門家です。

    ## 利用可能なツール
    - get_dataset_info: データセットのメタデータを取得
    - get_table_info: テーブルのスキーマ情報を取得
    - execute_query: SQLクエリを実行

    ## 分析の手順
    1. まずスキーマ情報を確認し、データの構造を理解する
    2. ユーザーの質問に答えるためのSQLクエリを組み立てる
    3. クエリを実行し、結果をわかりやすく説明する

    ## 注意事項
    - 大量のデータをスキャンするクエリは、先にWHERE句で絞り込む
    - SELECT *は避け、必要なカラムのみを指定する
    - コストに配慮し、LIMIT句を適切に使用する""",
    tools=[
        McpToolset(connection_params=bigquery_server),
    ],
)
