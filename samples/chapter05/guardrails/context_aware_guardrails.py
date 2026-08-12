# 5-4-6. ガードレールの構成パターン（パターン2: コンテキスト依存ガードレール）
"""コンテキスト依存ガードレールの実装"""
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types


def context_aware_guardrail(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """ユーザーの権限レベルに応じてガードレールを適用する"""
    # Sessionのstateからユーザー権限を取得
    user_role = callback_context.state.get("user_role", "guest")

    # 権限レベルに応じたガードレール設定
    guardrail_config = ROLE_GUARDRAIL_CONFIG.get(user_role, STRICT_CONFIG)

    last_message = _get_last_user_message(llm_request)
    if not last_message:
        return None

    # 禁止トピックチェック（権限レベルで閾値が変わる）
    if _is_restricted_topic(last_message, guardrail_config["restricted_topics"]):
        return _create_block_response(
            "この操作にはより高い権限が必要です。"
            "管理者にお問い合わせください。"
        )

    # トークン制限チェック
    if len(last_message) > guardrail_config["max_input_length"]:
        return _create_block_response(
            "入力が長すぎます。より短い形式で入力してください。"
        )

    return None


# 権限レベル別のガードレール設定
STRICT_CONFIG = {
    "restricted_topics": ["管理操作", "データ削除", "設定変更"],
    "max_input_length": 1000,
}

ROLE_GUARDRAIL_CONFIG = {
    "guest": STRICT_CONFIG,
    "user": {
        "restricted_topics": ["データ削除", "設定変更"],
        "max_input_length": 5000,
    },
    "admin": {
        "restricted_topics": [],
        "max_input_length": 10000,
    },
}


def _get_last_user_message(llm_request):
    """LLMリクエストから最新のユーザーメッセージを取得"""
    if not llm_request.contents:
        return None
    for content in reversed(llm_request.contents):
        if content.role == "user":
            for part in content.parts:
                if part.text:
                    return part.text
    return None


def _is_restricted_topic(text: str, topics: list[str]) -> bool:
    """制限トピックに該当するかチェック"""
    return any(topic in text for topic in topics)


def _create_block_response(message: str) -> LlmResponse:
    """ブロック応答を生成"""
    return LlmResponse(
        content=types.Content(
            parts=[types.Part(text=message)],
            role="model",
        )
    )
