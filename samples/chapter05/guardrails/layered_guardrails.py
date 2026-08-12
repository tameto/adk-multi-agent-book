# 5-4-6. ガードレールの構成パターン（パターン1: レイヤードガードレール）
"""レイヤードガードレールの実装"""
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types


def create_layered_input_guardrail(guardrails: list):
    """複数のガードレールを順番に適用するファクトリ関数"""

    def layered_guardrail(
        callback_context: CallbackContext,
        llm_request: LlmRequest,
    ) -> Optional[LlmResponse]:
        for guardrail in guardrails:
            result = guardrail(callback_context, llm_request)
            if result is not None:
                # いずれかのガードレールがブロックしたら即座に返す
                return result
        return None

    return layered_guardrail


# --- 以下は紙面では「別途定義済みの前提」とした2つのガードレールの最小実装（補完） ---

def rate_limit_guardrail(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """レート制限ガードレール（最小実装）: 1セッション20リクエストまで許可する"""
    request_count = callback_context.state.get("_request_count", 0) + 1
    callback_context.state["_request_count"] = request_count

    if request_count > 20:
        return LlmResponse(
            content=types.Content(
                parts=[
                    types.Part(
                        text="リクエスト数が上限に達しました。"
                        "しばらく時間をおいてからお試しください。"
                    )
                ],
                role="model",
            )
        )
    return None


def topic_restriction_guardrail(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """トピック制限ガードレール（最小実装）: 対応範囲外のトピックをブロックする"""
    restricted_topics = ["投資助言", "医療診断", "法律相談"]

    if not llm_request.contents:
        return None
    for content in reversed(llm_request.contents):
        if content.role == "user":
            for part in content.parts:
                if part.text and any(t in part.text for t in restricted_topics):
                    return LlmResponse(
                        content=types.Content(
                            parts=[
                                types.Part(
                                    text="このトピックは本エージェントの"
                                    "対応範囲外です。専門の窓口にご相談ください。"
                                )
                            ],
                            role="model",
                        )
                    )
            break
    return None


# 使用例
try:
    from .input_guardrails import input_safety_guardrail
except ImportError:
    from guardrails.input_guardrails import input_safety_guardrail

# レート制限 → プロンプトインジェクション → 安全性の順にチェック
layered_input = create_layered_input_guardrail([
    rate_limit_guardrail,
    input_safety_guardrail,
    topic_restriction_guardrail,
])
