# samples/chapter08/deploy/session_migrator.py
"""セッションデータの移行スクリプト（8-2-7節 マイグレーション戦略の完全版）

Agent Engine（VertexAiSessionService）のセッションを
DatabaseSessionService（Cloud SQL等の外部DB）に移行する。
Agent Engine → Cloud Runマイグレーション時に使用する。

使い方:
  export GOOGLE_CLOUD_PROJECT=your-project-id
  export GOOGLE_CLOUD_LOCATION=us-central1
  export AGENT_ENGINE_ID=1234567890
  export TARGET_DB_URL="postgresql+asyncpg://user:pass@host/db"
  python session_migrator.py user-001 user-002 ...
"""
import asyncio
import os
import sys

from google.adk.sessions import DatabaseSessionService, VertexAiSessionService


async def migrate_sessions(
    source_project: str,
    source_location: str,
    agent_engine_id: str,
    target_db_url: str,
    user_ids: list[str],
) -> None:
    """Agent EngineのセッションをDatabaseSessionServiceに移行する"""
    # 移行元: VertexAiSessionService
    source = VertexAiSessionService(
        project=source_project,
        location=source_location,
        agent_engine_id=agent_engine_id,
    )

    # 移行先: DatabaseSessionService
    target = DatabaseSessionService(db_url=target_db_url)

    migrated_count = 0
    for user_id in user_ids:
        # ユーザーのセッション一覧を取得
        # （list_sessions()はListSessionsResponseを返すため.sessionsを参照する）
        sessions = (
            await source.list_sessions(
                app_name="my-agent",
                user_id=user_id,
            )
        ).sessions

        for session in sessions:
            # セッションの詳細を取得
            session_data = await source.get_session(
                app_name="my-agent",
                user_id=user_id,
                session_id=session.id,
            )

            # 移行先にセッションを作成（session_idをそのまま引き継ぐ）
            target_session = await target.create_session(
                app_name="my-agent",
                user_id=user_id,
                state=session_data.state,
                session_id=session.id,
            )

            # 会話履歴（events）も1件ずつ移行する
            for event in session_data.events:
                await target.append_event(session=target_session, event=event)

            migrated_count += 1

    print(f"移行完了: {migrated_count}セッション")


if __name__ == "__main__":
    # 移行対象のユーザーIDはコマンドライン引数で受け取る
    if len(sys.argv) < 2:
        print("使い方: python session_migrator.py <user_id> [<user_id> ...]")
        sys.exit(1)

    asyncio.run(
        migrate_sessions(
            source_project=os.environ["GOOGLE_CLOUD_PROJECT"],
            source_location=os.environ.get(
                "GOOGLE_CLOUD_LOCATION", "us-central1"
            ),
            agent_engine_id=os.environ["AGENT_ENGINE_ID"],
            target_db_url=os.environ["TARGET_DB_URL"],
            user_ids=sys.argv[1:],
        )
    )
