from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types
import re


# 機密情報パターン（出力に含まれてはならない）
SENSITIVE_PATTERNS: list[re.Pattern] = [
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),  # メールアドレス
    re.compile(r"\b0[0-9]{1,4}-[0-9]{1,4}-[0-9]{4}\b"),  # 電話番号（日本）
    re.compile(r"\b\d{3}-\d{4}\b"),  # 郵便番号
    re.compile(r"(AIza[0-9A-Za-z_-]{35})"),  # Google APIキー
    re.compile(r"(sk-[A-Za-z0-9]{48})"),  # OpenAI APIキー
]


def after_model_guard(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> LlmResponse | None:
    """モデルの出力から機密情報を検出するガードレール"""
    if not llm_response.content or not llm_response.content.parts:
        return None

    for part in llm_response.content.parts:
        if not hasattr(part, "text") or not part.text:
            continue
        for pattern in SENSITIVE_PATTERNS:
            if pattern.search(part.text):
                # 機密情報を検出した場合、応答を差し替える
                return LlmResponse(
                    content=types.Content(
                        role="model",
                        parts=[types.Part(
                            text="回答に機密情報が含まれる可能性を検出しました。"
                            "内容を確認のうえ、再度お問い合わせください。"
                        )],
                    )
                )

    return None  # 問題なければ元のレスポンスをそのまま返す
