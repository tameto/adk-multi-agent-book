# samples/chapter04/memory_agent/state_keys.py
"""Stateキーの一元管理と型安全なアクセサ"""
from typing import Any
from pydantic import BaseModel, Field


class StateKeys:
    """Stateキーの定数定義"""
    # app: スコープ — アプリケーション全体の設定
    APP_VERSION = "app:version"
    APP_MAX_RESULTS = "app:max_search_results"
    APP_SUPPORT_LANGUAGES = "app:support_languages"

    # user: スコープ — ユーザー固有の情報
    USER_NAME = "user:name"
    USER_TIER = "user:tier"
    USER_LANGUAGE = "user:preferred_language"
    USER_IMPORTANT_CONTEXT = "user:important_context"

    # temp: スコープ — 一時データ（ターンまたぎで不要になるもの）
    TEMP_CURRENT_INTENT = "temp:current_intent"
    TEMP_SEARCH_COUNT = "temp:search_count"
    TEMP_LAST_TOOL_RESULT = "temp:last_tool_result"


# --- 型安全なアクセサ ---

VALID_TIERS = ("free", "standard", "premium")


def get_user_tier(state: dict[str, Any]) -> str:
    """ユーザーティアを型安全に取得する"""
    tier = state.get(StateKeys.USER_TIER, "free")
    if tier not in VALID_TIERS:
        return "free"
    return tier


def get_max_results(state: dict[str, Any]) -> int:
    """最大検索結果数を型安全に取得する"""
    value = state.get(StateKeys.APP_MAX_RESULTS, 5)
    if not isinstance(value, int) or value < 1:
        return 5
    return min(value, 100)


# --- Pydanticモデル ---

class UserState(BaseModel):
    """ユーザー関連のStateを構造化する"""
    name: str = "ゲスト"
    tier: str = Field(
        default="free",
        pattern="^(free|standard|premium)$",
    )
    preferred_language: str = "ja"


def load_user_state(state: dict[str, Any]) -> UserState:
    """Stateからユーザー情報を読み込む"""
    return UserState(
        name=state.get(StateKeys.USER_NAME, "ゲスト"),
        tier=state.get(StateKeys.USER_TIER, "free"),
        preferred_language=state.get(StateKeys.USER_LANGUAGE, "ja"),
    )


def save_user_state(state: dict[str, Any], user: UserState) -> None:
    """ユーザー情報をStateに書き戻す"""
    state[StateKeys.USER_NAME] = user.name
    state[StateKeys.USER_TIER] = user.tier
    state[StateKeys.USER_LANGUAGE] = user.preferred_language
