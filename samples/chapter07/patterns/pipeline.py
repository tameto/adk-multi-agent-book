# samples/chapter07/patterns/pipeline.py
"""Pipelineパターン（7-3-2）

各ステージをA2Aサーバーとして独立デプロイし、パイプラインの
オーケストレーションを ADK の SequentialAgent が担う構成。
SequentialAgentはTemplate Workflowとして利用できる。複雑な分岐や再開が必要な場合はWorkflow Runtimeを検討する。
前段の最終レスポンスが次段の入力として順に渡される。

実行前に各ステージのA2Aサーバー3台（ポート8001〜8003）を起動しておくこと。
"""

import asyncio
import os
import urllib.error
import urllib.request

from google.adk.agents import SequentialAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

# ステージ1: データ収集
stage1 = RemoteA2aAgent(
    name="data_collector",
    description="ユーザーのクエリに基づいてデータを収集する",
    agent_card="http://localhost:8001/.well-known/agent-card.json",
)

# ステージ2: 分析
stage2 = RemoteA2aAgent(
    name="data_analyzer",
    description="収集されたデータを分析する",
    agent_card="http://localhost:8002/.well-known/agent-card.json",
)

# ステージ3: レポート生成
stage3 = RemoteA2aAgent(
    name="report_generator",
    description="分析結果からレポートを生成する",
    agent_card="http://localhost:8003/.well-known/agent-card.json",
)

# パイプライン全体をSequentialAgentで構成
pipeline = SequentialAgent(
    name="report_pipeline",
    sub_agents=[stage1, stage2, stage3],
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
    """パイプラインをローカル実行する（動作確認用の補完コード）"""
    if not _check_prerequisites(
        [
            "http://localhost:8001/.well-known/agent-card.json",
            "http://localhost:8002/.well-known/agent-card.json",
            "http://localhost:8003/.well-known/agent-card.json",
        ]
    ):
        return

    runner = InMemoryRunner(agent=pipeline)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="user"
    )
    message = types.Content(
        role="user",
        parts=[types.Part(text="第1四半期の経費データからレポートを作成してください")],
    )
    async for event in runner.run_async(
        user_id="user", session_id=session.id, new_message=message
    ):
        # 各ステージの応答テキストを表示
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"[{event.author}] {part.text}")
                elif part.function_call:
                    # テキスト以外（入力要求などのツール呼び出し）も
                    # 無出力で終了しないよう進行状況を表示する
                    print(
                        f"[{event.author}] "
                        f"function_call: {part.function_call.name}"
                    )


if __name__ == "__main__":
    asyncio.run(main())
