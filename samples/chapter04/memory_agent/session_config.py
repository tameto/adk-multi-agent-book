# samples/chapter04/memory_agent/session_config.py
"""環境変数ベースのSessionService / MemoryService設定"""
import os
from google.adk.sessions import (
    InMemorySessionService,
    DatabaseSessionService,
    VertexAiSessionService,
)
from google.adk.memory import (
    InMemoryMemoryService,
    VertexAiMemoryBankService,
)


def create_session_service():
    """環境に応じたSessionServiceを生成する"""
    env = os.environ.get("AGENT_ENV", "dev")

    if env == "dev":
        # ローカル開発: メモリ上に保持
        return InMemorySessionService()
    elif env == "staging":
        # ステージング: PostgreSQLに永続化
        db_url = os.environ.get("DATABASE_URL")
        if not db_url:
            raise ValueError(
                "AGENT_ENV=staging では DATABASE_URL の設定が必要です"
            )
        return DatabaseSessionService(db_url=db_url)
    else:
        # 本番: Vertex AIマネージドストレージ
        project = os.environ.get("GCP_PROJECT")
        location = os.environ.get("GCP_LOCATION", "us-central1")
        agent_engine_id = os.environ.get("AGENT_ENGINE_ID")
        if not project:
            raise ValueError(
                "AGENT_ENV=prod では GCP_PROJECT の設定が必要です"
            )
        if not agent_engine_id:
            raise ValueError(
                "AGENT_ENV=prod では AGENT_ENGINE_ID の設定が必要です"
            )
        return VertexAiSessionService(
            project=project,
            location=location,
            agent_engine_id=agent_engine_id,
        )


def create_memory_service():
    """環境変数に基づいてMemoryServiceを生成する"""
    enable_memory = os.environ.get(
        "ENABLE_MEMORY_BANK", "false"
    ).lower() == "true"

    if not enable_memory:
        return None

    env = os.environ.get("AGENT_ENV", "dev")

    if env == "dev":
        # 開発時: インメモリのMemoryService
        return InMemoryMemoryService()
    else:
        # ステージング・本番: Vertex AI Memory Bank
        project = os.environ.get("GCP_PROJECT")
        location = os.environ.get("GCP_LOCATION", "us-central1")
        agent_engine_id = os.environ.get("AGENT_ENGINE_ID")
        if not project:
            raise ValueError(
                "Memory Bank の有効化には GCP_PROJECT の設定が必要です"
            )
        if not agent_engine_id:
            raise ValueError(
                "Memory Bank の有効化には AGENT_ENGINE_ID の設定が必要です"
            )
        return VertexAiMemoryBankService(
            project=project,
            location=location,
            agent_engine_id=agent_engine_id,
        )
