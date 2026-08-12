# samples/chapter03/callbacks_examples/after_model.py
"""3-4-2 after_model_callback（完全版）

LLMのレスポンスを受け取った直後に実行されるコールバック。
レスポンスの検証、フィルタリング、加工に使用する。
"""
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from typing import Optional

def validate_response(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> Optional[LlmResponse]:
    """LLMレスポンスの品質を検証するコールバック"""
    parts = llm_response.content.parts if llm_response.content else []
    response_text = parts[0].text if parts else ""

    # 禁止ワードのチェック
    prohibited_words = ["パスワード", "クレジットカード番号", "SSN"]
    for word in prohibited_words:
        if word in response_text:
            # 禁止ワードが含まれている場合、安全なレスポンスに差し替え
            return LlmResponse(
                content=types.Content(
                    parts=[types.Part(
                        text="申し訳ございません。セキュリティ上の理由から、"
                             "その情報をこのチャネルでお伝えすることはできません。"
                             "セキュアなフォームからお手続きください。"
                    )]
                )
            )

    # レスポンスの長さチェック
    if len(response_text) > 2000:
        callback_context.state["response_truncated"] = True

    return None  # Noneを返すと元のレスポンスがそのまま使用される
