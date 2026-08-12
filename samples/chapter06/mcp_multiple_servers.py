# samples/chapter06/mcp_multiple_servers.py
"""複数のMCPサーバーを統合するエージェント"""

import os

from google.adk import Agent
from google.adk.tools.mcp_tool import (
    McpToolset,
    StdioConnectionParams,
    StreamableHTTPConnectionParams,
)
from mcp import StdioServerParameters


# ファイルシステムMCPサーバー（ローカル）
filesystem_server = StdioConnectionParams(
    server_params=StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/workspace"],
    )
)

# GitHub MCPサーバー（ローカル）
github_server = StdioConnectionParams(
    server_params=StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": os.environ.get("GITHUB_TOKEN", "")},
    )
)

# BigQuery MCPサーバー（リモート）
bigquery_headers = (
    {"Authorization": f"Bearer {os.environ['BQ_MCP_TOKEN']}"}
    if os.environ.get("BQ_MCP_TOKEN")
    else None
)

bigquery_server = StreamableHTTPConnectionParams(
    url="https://bigquery-mcp.example.com/mcp",
    headers=bigquery_headers,
)

# 全MCPサーバーのツールを統合したエージェント
multi_tool_agent = Agent(
    name="multi_tool_agent",
    model="gemini-3.5-flash",
    instruction="""あなたは以下のツールを駆使してタスクを遂行するエージェントです。

    利用可能なツール:
    - fs_*: ファイルの読み書き、ディレクトリの一覧表示
    - github_*: リポジトリの参照、Issue/PRの作成・更新
    - bq_*: データ分析用のSQLクエリ実行

    タスクに合ったツールを選択してください。
    データの変更を伴う操作は、実行前にユーザーに確認を取ってください。""",
    tools=[
        McpToolset(connection_params=filesystem_server, tool_name_prefix="fs"),
        McpToolset(connection_params=github_server, tool_name_prefix="github"),
        McpToolset(
            connection_params=bigquery_server,
            tool_filter=["execute_query", "list_tables", "get_schema"],
            tool_name_prefix="bq",
        ),
    ],
)
