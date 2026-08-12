# samples/chapter06/mcp_stdio_basic.py
"""stdioトランスポートによるMCPサーバー接続の基本例"""

from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters


# MCPサーバーの接続パラメータを定義
filesystem_server = StdioConnectionParams(
    server_params=StdioServerParameters(
        command="npx",  # 実行コマンド
        args=[
            "-y",
            "@modelcontextprotocol/server-filesystem",
            "/path/to/allowed/directory",
        ],
        env=None,  # 環境変数（必要に応じて辞書で指定）
    )
)

# McpToolsetを使ってADKエージェントのツールとして統合
agent = Agent(
    name="file_assistant",
    model="gemini-3.5-flash",
    instruction="""あなたはファイル操作を支援するアシスタントです。
    ユーザーの指示に従い、ファイルの読み取り、一覧表示、検索を行います。
    ファイルの内容を変更する前に、必ずユーザーに確認を取ってください。""",
    tools=[
        McpToolset(
            connection_params=filesystem_server,
            # 利用するツールを名前で制限（省略時は全ツール）
            # tool_filter=["read_file", "list_directory"],
        )
    ],
)
