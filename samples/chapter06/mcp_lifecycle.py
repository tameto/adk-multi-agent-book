# samples/chapter06/mcp_lifecycle.py
"""MCPサーバー接続のライフサイクル管理（Runner自動管理パターン）"""

import asyncio
import shutil
import subprocess

from google.adk import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from google.genai.types import Content, Part
from mcp import StdioServerParameters


def _node_supports_mcp_server() -> bool:
    """MCP filesystem server の実行に必要な Node.js v18+ を確認する"""
    if not shutil.which("node") or not shutil.which("npx"):
        print("Node.js と npx が見つかりません。MCPサーバー実行には Node.js v18+ が必要です。")
        return False

    result = subprocess.run(
        ["node", "--version"],
        capture_output=True,
        text=True,
        check=False,
        timeout=5,
    )
    version = result.stdout.strip().lstrip("v")
    major = int(version.split(".", 1)[0]) if version else 0
    if major < 18:
        print(
            f"Node.js {result.stdout.strip()} が検出されました。"
            " MCP filesystem server の実行には Node.js v18+ が必要です。"
        )
        return False

    return True


async def main():
    if not _node_supports_mcp_server():
        return

    # MCPサーバーパラメータ
    server_params = StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
        )
    )

    # McpToolsetをAgentのtools=[]に直接渡す
    # runner.close()がToolsetのclose()をawaitしてリソースを解放する
    agent = Agent(
        name="file_agent",
        model="gemini-3.5-flash",
        instruction="ファイル操作を行うエージェントです。",
        tools=[
            McpToolset(connection_params=server_params),
        ],
    )

    session_service = InMemorySessionService()
    runner = Runner(
        agent=agent,
        app_name="mcp_demo",
        session_service=session_service,
    )

    session = await session_service.create_session(
        app_name="mcp_demo", user_id="user1"
    )

    try:
        async for event in runner.run_async(
            session_id=session.id,
            user_id="user1",
            new_message=Content(
                role="user",
                parts=[
                    Part(text="/tmpディレクトリのファイル一覧を表示してください")
                ],
            ),
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text)
    finally:
        await runner.close()


if __name__ == "__main__":
    asyncio.run(main())
