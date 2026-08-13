# samples/chapter04/tests/test_inmemory_session.py
# 4-2-1. InMemorySessionService（テストでの活用パターン）完全版
"""InMemorySessionServiceで初期Stateを設定したテストのサンプル

samples/chapter04/ ディレクトリからでも、リポジトリルートからでも
`python -m pytest` で実行できる。
（pytest-asyncio が必要）
GCP接続は不要。

補完: 紙面では文字列リテラル（"user:name" 等）でStateキーを記述しているが、
samplesでは memory_agent/state_keys.py の定数に整合させている。
StateKeys.APP_MAX_RESULTS の実体は "app:max_search_results"。
"""
import pytest
import pytest_asyncio
from google.adk.sessions import InMemorySessionService

from memory_agent.state_keys import StateKeys


@pytest_asyncio.fixture
async def session_with_premium_user():
    """プレミアム会員のSessionを準備するフィクスチャ"""
    service = InMemorySessionService()
    session = await service.create_session(
        app_name="test_app",
        user_id="test_user",
        state={
            StateKeys.USER_NAME: "テスト太郎",
            StateKeys.USER_TIER: "premium",
            StateKeys.APP_MAX_RESULTS: 10,
        },
    )
    return session


@pytest.mark.asyncio
async def test_premium_user_gets_extended_results(session_with_premium_user):
    """プレミアム会員は拡張された検索結果を受け取れること"""
    session = session_with_premium_user
    assert session.state[StateKeys.USER_TIER] == "premium"
    assert session.state[StateKeys.APP_MAX_RESULTS] == 10
