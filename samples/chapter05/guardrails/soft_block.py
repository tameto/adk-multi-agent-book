# 5-4-7. 安全性と利便性のバランス（ソフトブロック）
"""ソフトブロックガードレールの実装"""
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types


def soft_block_guardrail(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """段階的エスカレーション型ガードレール"""
    last_message = _get_last_user_message(llm_request)
    if not last_message:
        return None

    risk_level = _assess_risk(last_message)

    if risk_level == "high":
        # 即座にブロック
        return _create_block_response(
            "このリクエストは安全上の理由からブロックされました。"
        )
    elif risk_level == "medium":
        # 確認済みフラグがあれば通過
        if callback_context.state.get("_user_confirmed"):
            callback_context.state["_user_confirmed"] = False
            return None

        # 確認を要求
        return _create_block_response(
            "この操作にはリスクが伴います。"
            "続行する場合は「続行を確認します」と入力してください。"
        )

    return None


def _get_last_user_message(llm_request):
    """最新のユーザーメッセージを取得"""
    if not llm_request.contents:
        return None
    for content in reversed(llm_request.contents):
        if content.role == "user":
            for part in content.parts:
                if part.text:
                    return part.text
    return None


def _assess_risk(text: str) -> str:
    """リスクレベルを判定する"""
    high_risk_keywords = ["全件削除", "本番環境", "DROP"]
    medium_risk_keywords = ["削除", "更新", "変更"]

    if any(kw in text for kw in high_risk_keywords):
        return "high"
    if any(kw in text for kw in medium_risk_keywords):
        return "medium"
    return "low"


def _create_block_response(message: str) -> LlmResponse:
    """ブロック応答を生成"""
    return LlmResponse(
        content=types.Content(
            parts=[types.Part(text=message)],
            role="model",
        )
    )
