# samples/chapter06/mcp_tool_filter_callback.py
"""コールバック関数によるMCPツールフィルタリング"""

from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters


def safe_tools_only(tool, readonly_context=None):
    """書き込み系のツールを除外するフィルタ"""
    # ツール名に書き込み系キーワードが含まれる場合は除外
    write_keywords = ["write", "delete", "update", "insert", "drop", "create"]
    tool_name_lower = tool.name.lower()
    return not any(kw in tool_name_lower for kw in write_keywords)


postgres_server = StdioConnectionParams(
    server_params=StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-postgres",
              "postgresql://localhost:5432/mydb"],
    )
)

toolset = McpToolset(
    connection_params=postgres_server,
    tool_filter=safe_tools_only,
)
