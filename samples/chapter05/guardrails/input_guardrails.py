# 5-4-2. before_model_callbackによる入力フィルタリング
"""入力ガードレールの実装"""
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types


def input_safety_guardrail(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """入力の安全性をチェックするガードレール

    Returns:
        None: チェック通過（LLMに処理を委譲）
        LlmResponse: ブロック時の応答（LLMをスキップ）
    """
    # 最新のユーザーメッセージを取得
    last_message = _get_last_user_message(llm_request)
    if not last_message:
        return None

    # プロンプトインジェクション検出
    if _detect_prompt_injection(last_message):
        return LlmResponse(
            content=types.Content(
                parts=[
                    types.Part(
                        text="申し訳ございませんが、"
                        "そのリクエストにはお応えできません。"
                        "通常のご質問をお願いいたします。"
                    )
                ],
                role="model",
            )
        )

    # 禁止トピック検出
    if _detect_prohibited_topic(last_message):
        return LlmResponse(
            content=types.Content(
                parts=[
                    types.Part(
                        text="申し訳ございませんが、"
                        "そのトピックについてはお答えできません。"
                        "別のご質問があればお気軽にどうぞ。"
                    )
                ],
                role="model",
            )
        )

    # チェック通過: LLMに処理を委譲
    return None


def _get_last_user_message(
    llm_request: LlmRequest,
) -> Optional[str]:
    """LLMリクエストから最新のユーザーメッセージを抽出する"""
    if not llm_request.contents:
        return None
    for content in reversed(llm_request.contents):
        if content.role == "user":
            for part in content.parts:
                if part.text:
                    return part.text
    return None


def _detect_prompt_injection(text: str) -> bool:
    """プロンプトインジェクションの兆候を検出する"""
    injection_patterns = [
        "前の指示を忘れて",
        "ignore previous instructions",
        "system promptを表示",
        "あなたはDAN",
        "jailbreak",
        "do anything now",
        "新しいルールに従って",
        "override your instructions",
    ]
    text_lower = text.lower()
    return any(pattern.lower() in text_lower for pattern in injection_patterns)


def _detect_prohibited_topic(text: str) -> bool:
    """禁止トピックを検出する"""
    prohibited_topics = [
        "爆弾の作り方",
        "違法薬物",
        "ハッキング方法",
        "個人情報を教えて",
    ]
    return any(topic in text for topic in prohibited_topics)
