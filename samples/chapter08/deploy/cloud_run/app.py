# samples/chapter08/deploy/cloud_run/app.py
"""Cloud Run用のHTTPサーバー（8-2-5節の完全版）

ADKエージェントをFastAPIでラップし、Cloud Run上でHTTPサービスとして
公開する。Session永続化はDatabaseSessionService（Cloud SQL等の外部DB）を使用する。

実行前に以下の環境変数を設定すること:
  DATABASE_URL: セッション保存先のDB接続文字列
    （例: postgresql+asyncpg://user:pass@host/db）
"""
import os

import uvicorn
from fastapi import FastAPI
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types
from pydantic import BaseModel

try:
    from .agent import root_agent
except ImportError:
    from agent import root_agent

app = FastAPI()
runner: Runner | None = None
session_service: DatabaseSessionService | None = None


def get_runner() -> Runner:
    """環境変数からSessionServiceを初期化し、Runnerを取得する"""
    global runner, session_service
    if runner is not None:
        return runner

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL を設定してください")

    # セッションサービスは外部DBを使用（Cloud SQL等）
    # 接続文字列は環境変数から取得する（コードに直書きしない）
    session_service = DatabaseSessionService(db_url=db_url)
    runner = Runner(
        agent=root_agent,
        app_name="my-agent",
        session_service=session_service,
    )
    return runner


async def ensure_session(user_id: str, session_id: str) -> None:
    """指定されたSessionがなければ作成する"""
    if session_service is None:
        raise RuntimeError("SessionService が初期化されていません")

    existing_session = await session_service.get_session(
        app_name="my-agent",
        user_id=user_id,
        session_id=session_id,
    )
    if existing_session is None:
        await session_service.create_session(
            app_name="my-agent",
            user_id=user_id,
            session_id=session_id,
        )


class ChatRequest(BaseModel):
    """対話リクエスト"""
    session_id: str
    user_id: str
    message: str


class ChatResponse(BaseModel):
    """対話レスポンス"""
    response: str
    session_id: str


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """エージェントとの対話エンドポイント"""
    active_runner = get_runner()
    await ensure_session(
        user_id=request.user_id,
        session_id=request.session_id,
    )

    # ユーザーメッセージを作成
    user_content = types.Content(
        role="user",
        parts=[types.Part(text=request.message)],
    )

    # Runnerを実行し、最後のエージェント応答を取得
    final_response = ""
    async for event in active_runner.run_async(
        user_id=request.user_id,
        session_id=request.session_id,
        new_message=user_content,
    ):
        if event.is_final_response() and event.content:
            final_response = event.content.parts[0].text

    return ChatResponse(
        response=final_response,
        session_id=request.session_id,
    )


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness Probe用エンドポイント（GKEのlivenessProbeでも使用）"""
    return {"status": "ok"}


@app.get("/ready")
async def ready() -> dict[str, str]:
    """Readiness Probe用エンドポイント（GKEのreadinessProbeでも使用）"""
    return {"status": "ready"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
