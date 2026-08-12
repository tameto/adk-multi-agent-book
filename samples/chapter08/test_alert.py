# samples/chapter08/test_alert.py
"""アラート動作確認用のエラー発生スクリプト（8-7 ハンズオン ステップ5）

存在しないセッションIDで async_stream_query を呼び出して意図的にエラーを
発生させ、agent_alerts.py で登録したエージェント層アラート（エラー率5%超）の
発火を確認する。デプロイ済みリソース名は環境変数
AGENT_ENGINE_RESOURCE_NAME で指定する。

使い方:
  export GOOGLE_CLOUD_PROJECT=your-project-id
  export GOOGLE_CLOUD_LOCATION=us-central1
  export AGENT_ENGINE_RESOURCE_NAME=projects/.../reasoningEngines/1234567890
  python test_alert.py
"""
import asyncio
import os
import sys

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


async def trigger_errors(
    error_count: int = 5,
    agent_engine_client: object | None = None,
) -> int:
    """存在しないセッションIDでクエリを実行し、意図的にエラーを発生させる"""
    agent_engine = agent_engine_client or get_agent_engine()

    triggered = 0
    for i in range(error_count):
        # 実在しないセッションIDを使い、NotFound系のエラーを誘発する
        missing_session_id = f"nonexistent-session-{i}"
        try:
            async for _event in agent_engine.async_stream_query(
                user_id="alert-test-user",
                session_id=missing_session_id,
                message="アラート発火テスト",
            ):
                pass
            print(f"[{i}] エラーが発生しませんでした（想定外）")
        except google_exceptions.NotFound:
            # 想定どおりのエラー。アラートの集計対象になる
            triggered += 1
            print(f"[{i}] NotFound を発生させました（アラート集計対象）")
        except google_exceptions.GoogleAPICallError as e:
            # NotFound以外のAPIエラーもエラー率に計上される
            triggered += 1
            print(f"[{i}] APIエラーを発生させました: {type(e).__name__}")

    return triggered


async def main() -> None:
    """指定回数のエラーを発生させ、アラート確認の案内を表示する"""
    error_count = int(os.environ.get("ERROR_COUNT", "5"))
    triggered = await trigger_errors(error_count=error_count)

    print(f"合計 {triggered} 件のエラーを発生させました。")
    print(
        "数分後に Cloud Monitoring のアラート"
        "（Agent Engine - Error Rate > 5%）が発火することを確認してください。"
    )


if __name__ == "__main__":
    if not os.environ.get("AGENT_ENGINE_RESOURCE_NAME"):
        print(
            "環境変数 AGENT_ENGINE_RESOURCE_NAME を"
            "デプロイ済みリソース名に設定してください。"
        )
        sys.exit(2)

    asyncio.run(main())
