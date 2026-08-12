# samples/chapter07/patterns/hub_spoke.py
"""Hub-Spokeパターン（7-3-1）

中央のオーケストレーター（Hub）が、各専門エージェント（Spoke）を
RemoteA2aAgent + AgentTool として組み込み、LLMの判断で呼び分ける。

実行前に Spoke となるA2Aサーバー3台（ポート8001〜8003）を起動しておくこと。
"""

import asyncio
import os
import urllib.error
import urllib.request

from google.adk import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.runners import InMemoryRunner
from google.adk.tools import AgentTool
from google.genai import types

# 各A2AエージェントをRemoteA2aAgent としてラップ
data_collection_remote = RemoteA2aAgent(
    name="data_collection_agent",
    description="外部データソースから情報を収集する",
    agent_card="http://localhost:8001/.well-known/agent-card.json",
)

analysis_remote = RemoteA2aAgent(
    name="analysis_agent",
    description="収集したデータを分析し、示唆を抽出する",
    agent_card="http://localhost:8002/.well-known/agent-card.json",
)

report_remote = RemoteA2aAgent(
    name="report_agent",
    description="分析結果からレポート文書を生成する",
    agent_card="http://localhost:8003/.well-known/agent-card.json",
)

# オーケストレーター: LLMがどのエージェントを呼ぶか判断する
orchestrator = Agent(
    name="report_orchestrator",
    model="gemini-3.5-flash",
    instruction="""あなたはレポート作成のオーケストレーターです。

ユーザーのリクエストに応じて、以下の手順で処理を進めてください:
1. data_collection_agent でデータを収集する
2. analysis_agent で収集したデータを分析する
3. report_agent で分析結果からレポートを生成する

各ステップの結果を確認し、必要に応じて再実行してください。""",
    tools=[
        AgentTool(agent=data_collection_remote),
        AgentTool(agent=analysis_remote),
        AgentTool(agent=report_remote),
    ],
)


def _check_prerequisites(agent_card_urls: list[str]) -> bool:
    """ローカル実行に必要なAPIキーとA2Aサーバー起動状態を確認する"""
    if not os.environ.get("GOOGLE_API_KEY") and os.environ.get(
        "GOOGLE_GENAI_USE_VERTEXAI"
    ) != "TRUE":
        print("GOOGLE_API_KEY または Vertex AI 設定が必要です。")
        return False

    ok = True
    for url in agent_card_urls:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status >= 400:
                    raise urllib.error.URLError(f"HTTP {response.status}")
        except urllib.error.URLError:
            print(f"A2Aサーバーが未起動です: {url}")
            ok = False
    return ok


async def main() -> None:
    """オーケストレーターをローカル実行する（動作確認用の補完コード）"""
    if not _check_prerequisites(
        [
            "http://localhost:8001/.well-known/agent-card.json",
            "http://localhost:8002/.well-known/agent-card.json",
            "http://localhost:8003/.well-known/agent-card.json",
        ]
    ):
        return

    runner = InMemoryRunner(agent=orchestrator)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="user"
    )
    message = types.Content(
        role="user",
        parts=[types.Part(text="先月の売上データを収集・分析してレポートを作成してください")],
    )
    async for event in runner.run_async(
        user_id="user", session_id=session.id, new_message=message
    ):
        # 最終応答のテキストを表示
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text)


if __name__ == "__main__":
    asyncio.run(main())
