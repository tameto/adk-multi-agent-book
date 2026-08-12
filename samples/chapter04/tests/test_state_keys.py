# samples/chapter04/tests/test_state_keys.py
"""Stateキー定義と型安全なアクセサのテスト

samples/chapter04/ ディレクトリから `python -m pytest` で実行する。
GCP接続は不要。
"""
from memory_agent.state_keys import (
    StateKeys,
    get_max_results,
    get_user_tier,
    load_user_state,
    save_user_state,
)


class TestGetUserTier:
    """ユーザーティア取得のテスト"""

    def test_valid_tier(self):
        assert get_user_tier({"user:tier": "premium"}) == "premium"

    def test_invalid_tier_returns_free(self):
        assert get_user_tier({"user:tier": "unknown"}) == "free"

    def test_missing_key_returns_free(self):
        assert get_user_tier({}) == "free"


class TestGetMaxResults:
    """最大検索結果数取得のテスト"""

    def test_valid_value(self):
        assert get_max_results({"app:max_search_results": 10}) == 10

    def test_exceeds_limit_returns_100(self):
        assert get_max_results({"app:max_search_results": 500}) == 100

    def test_negative_returns_default(self):
        assert get_max_results({"app:max_search_results": -1}) == 5


class TestUserState:
    """UserState Pydanticモデルのテスト"""

    def test_load_and_save(self):
        state = {
            "user:name": "田中太郎",
            "user:tier": "premium",
            "user:preferred_language": "en",
        }
        user = load_user_state(state)
        assert user.name == "田中太郎"
        assert user.tier == "premium"
        assert user.preferred_language == "en"

        # 書き戻し
        new_state = {}
        save_user_state(new_state, user)
        assert new_state[StateKeys.USER_NAME] == "田中太郎"
