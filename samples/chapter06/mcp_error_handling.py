# samples/chapter06/mcp_error_handling.py
"""MCPツール呼び出しのエラーハンドリング"""

import logging

from google.adk import Agent
from google.adk.tools import BaseTool
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from google.adk.tools.tool_context import ToolContext
from mcp import StdioServerParameters

logger = logging.getLogger(__name__)


# タイムアウト設定を含むMCPサーバーパラメータ
server_params = StdioConnectionParams(
    server_params=StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/workspace"],
    )
)


# before_tool_callbackでエラーハンドリングを追加
async def handle_tool_errors(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
):
    """ツール呼び出し前にバリデーションを行うコールバック"""
    logger.info(f"ツール呼び出し: {tool.name}, 入力: {args}")

    # ファイルパスのバリデーション（パストラバーサル防止）
    if "path" in args:
        path = args["path"]
        if ".." in path:
            logger.warning(f"不正なファイルパスを検出: {path}")
            # dictを返すと実ツールをスキップしてそのdictを結果として扱う
            return {"error": "指定されたパスにはアクセスできません"}

    return None  # Noneを返すと通常通りツールを実行


agent = Agent(
    name="safe_file_agent",
    model="gemini-3.5-flash",
    instruction="ファイル操作を安全に行うエージェントです。",
    tools=[
        McpToolset(connection_params=server_params),
    ],
    before_tool_callback=handle_tool_errors,
)
