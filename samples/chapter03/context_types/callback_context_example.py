# samples/chapter03/context_types/callback_context_example.py
# 3-2-4. CallbackContext（完全版）
# CallbackContext クラス自体はADK本体（google.adk.agents.callback_context）が
# 提供するクラスのため、本ファイルには収録しない。
"""CallbackContextを使ったbefore_model_callbackのサンプル

Stateへの書き込み（呼び出し回数の記録）と、
LlmResponseの差し替えによるLLM呼び出しの打ち切りを実装する。
"""
from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from typing import Optional


def before_model_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """LLM呼び出し前にコンテキストを操作するコールバック"""
    # 呼び出し回数をStateに記録（書き込みが可能）
    call_count = callback_context.state.get("llm_call_count", 0)
    callback_context.state["llm_call_count"] = call_count + 1

    # リクエスト内容を検証（必要に応じてレスポンスを差し替え）
    if call_count >= 10:
        return LlmResponse(
            content=types.Content(
                parts=[types.Part(text="呼び出し回数の上限に達しました。")]
            )
        )
    return None  # Noneを返すと通常のLLM呼び出しが続行される


# 補完: 紙面ではコールバック関数のみ掲載。エージェントへの組み込み例。
agent = Agent(
    name="rate_limited_agent",
    model="gemini-3.5-flash",
    instruction="ユーザーの質問に回答してください。",
    before_model_callback=before_model_callback,
)
