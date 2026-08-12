# samples/chapter08/query_with_retry.py
"""Interactions APIのエラーハンドリング実装例（8-4-6 完全版）

レート制限（ResourceExhausted）・サービス一時停止（ServiceUnavailable）は
指数バックオフでリトライし、不正リクエスト（InvalidArgument）・リソース不在
（NotFound）はリトライせずに呼び出し元へ通知する。
紙面で省略した ServiceUnavailable / NotFound のハンドリングを含む完全版。
"""
import asyncio
import os

from google.api_core import exceptions as google_exceptions
import vertexai
from vertexai import agent_engines


def get_agent_engine() -> object:
    """環境変数で指定されたAgent Engineクライアントを取得する"""
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "my-project")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    resource_name = os.environ.get(
        "AGENT_ENGINE_RESOURCE_NAME",
        "projects/my-project/locations/us-central1/reasoningEngines/1234567890",
    )
    vertexai.init(project=project, location=location)
    return agent_engines.get(resource_name)


async def query_with_retry(
    user_id: str,
    session_id: str,
    message: str,
    max_retries: int = 3,
    agent_engine_client: object | None = None,
) -> object:
    """リトライ付きのクエリ実行（非同期ストリーミング）"""
    agent_engine = agent_engine_client or get_agent_engine()

    for attempt in range(max_retries):
        try:
            final_event = None
            async for event in agent_engine.async_stream_query(
                user_id=user_id,
                session_id=session_id,
                message=message,
            ):
                final_event = event
            return final_event

        except google_exceptions.ResourceExhausted:
            # レート制限: 指数バックオフで待機
            wait_time = 2 ** attempt
            print(f"レート制限。{wait_time}秒後にリトライします...")
            await asyncio.sleep(wait_time)

        except google_exceptions.ServiceUnavailable:
            # サービス一時停止: リトライ
            wait_time = 2 ** attempt
            print(f"サービス一時停止。{wait_time}秒後にリトライします...")
            await asyncio.sleep(wait_time)

        except google_exceptions.InvalidArgument as e:
            # 不正なリクエスト: リトライ不要
            raise ValueError(f"リクエストが不正です: {e}") from e

        except google_exceptions.NotFound:
            # リソースが見つからない: セッションの再作成を試みる
            raise ValueError(
                f"セッション {session_id} が見つかりません。"
                "新しいセッションを作成してください。"
            )

    raise RuntimeError(f"{max_retries}回のリトライ後も失敗しました")
