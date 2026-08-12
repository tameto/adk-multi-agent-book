# samples/chapter06/mcp_streamable_http_basic.py
"""Streamable HTTPトランスポートによるリモートMCPサーバー接続の例"""

import os

from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams


# リモートMCPサーバーの接続パラメータ
auth_headers = (
    {"Authorization": f"Bearer {os.environ['MCP_API_TOKEN']}"}
    if os.environ.get("MCP_API_TOKEN")
    else None
)

remote_server = StreamableHTTPConnectionParams(
    url="https://mcp-server.example.com/mcp",
    # 認証トークンは環境変数から取得（コードへのハードコード禁止）
    headers=auth_headers,
)

agent = Agent(
    name="remote_tool_agent",
    model="gemini-3.5-flash",
    instruction="リモートツールを活用してタスクを遂行するエージェントです。",
    tools=[
        McpToolset(
            connection_params=remote_server,
        )
    ],
)
