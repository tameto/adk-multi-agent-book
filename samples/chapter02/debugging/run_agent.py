# run_agent.py
# 2-5-4. Pythonスクリプトからの実行（完全版）
# RunnerとInMemorySessionServiceを使い、インメモリ環境でエージェントを実行する。
# 前提: adk create my_agent で生成したプロジェクトと同じ階層に置いて実行する。

import asyncio
from importlib import import_module

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part


def load_root_agent():
    """adk create my_agent で生成したエージェントを読み込む"""
    try:
        return import_module("my_agent.agent").root_agent
    except ModuleNotFoundError as exc:
        if exc.name == "my_agent":
            raise RuntimeError(
                "先に `adk create my_agent` でプロジェクトを作成し、"
                "このスクリプトを同じ階層で実行してください"
            ) from exc
        raise


async def main():
    root_agent = load_root_agent()

    # ランナーの初期化
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name="my_app",
        session_service=session_service,
    )

    # セッションの作成
    session = await session_service.create_session(
        app_name="my_app",
        user_id="user1",
    )

    # ユーザーメッセージの送信
    user_message = Content(
        role="user",
        parts=[Part(text="京都に2泊3日で旅行したいです。")],
    )

    # エージェントの実行（run_asyncはAsyncGeneratorなのでawaitせず直接iterate）
    events = runner.run_async(
        session_id=session.id,
        user_id="user1",
        new_message=user_message,
    )

    # レスポンスの表示
    async for event in events:
        if event.content and event.content.parts:
            print(event.content.parts[0].text)


# 本番環境では、SessionServiceをVertexAiSessionServiceに差し替える。
# エージェントのコードはそのままに、実行環境だけを切り替えられる。
#
# from google.adk.sessions import VertexAiSessionService
#
# session_service = VertexAiSessionService(
#     project="my-gcp-project",
#     location="us-central1",
#     agent_engine_id="1234567890",
# )
#
# runner = Runner(
#     agent=root_agent,
#     app_name="my_app",
#     session_service=session_service,
# )

if __name__ == "__main__":
    asyncio.run(main())
