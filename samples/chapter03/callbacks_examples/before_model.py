# samples/chapter03/callbacks_examples/before_model.py
"""3-4-1 before_model_callback（完全版）

LLMの呼び出し直前に実行されるコールバック。
リクエストの検査・修正や、条件に応じたLLM呼び出しのスキップに使う。
"""
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from typing import Optional

def inject_context_before_model(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """LLM呼び出し前にコンテキスト情報を注入するコールバック"""
    # ユーザーのアクティブな注文情報を取得
    active_orders = callback_context.state.get("active_orders", [])

    if active_orders:
        # アクティブな注文情報をシステムメッセージとして注入
        order_info = "\n".join(
            f"- 注文#{o['id']}: {o['status']} ({o['date']})"
            for o in active_orders
        )
        context_message = types.Content(
            role="user",
            parts=[types.Part(text=f"[システム情報] 現在のアクティブな注文:\n{order_info}")],
        )
        # リクエストのcontentsに追加
        llm_request.contents.append(context_message)

    return None  # Noneを返すとLLM呼び出しが続行される


def rate_limit_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """レート制限を実装するコールバック"""
    import time

    # 最後のLLM呼び出し時刻を取得
    last_call_time = callback_context.state.get("last_llm_call_time", 0)
    current_time = time.time()

    # 1秒以内の連続呼び出しを制限
    if current_time - last_call_time < 1.0:
        return LlmResponse(
            content=types.Content(
                parts=[types.Part(text="リクエストの処理間隔が短すぎます。少々お待ちください。")]
            )
        )

    # 呼び出し時刻を記録
    callback_context.state["last_llm_call_time"] = current_time
    return None
