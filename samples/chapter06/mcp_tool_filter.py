# samples/chapter06/mcp_tool_filter.py
"""MCPツールのフィルタリング例"""

from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters


# PostgreSQL MCPサーバーに接続
postgres_server = StdioConnectionParams(
    server_params=StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-postgres",
              "postgresql://localhost:5432/mydb"],
    )
)

# 読み取り専用ツールのみに制限
readonly_agent = Agent(
    name="data_analyst",
    model="gemini-3.5-flash",
    instruction="データベースを参照して分析を行います。データの変更は行いません。",
    tools=[
        McpToolset(
            connection_params=postgres_server,
            tool_filter=["query"],  # SELECTクエリ用ツールのみ
        )
    ],
)
