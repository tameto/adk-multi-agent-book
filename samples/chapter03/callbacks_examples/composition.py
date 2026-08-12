# samples/chapter03/callbacks_examples/composition.py
"""3-4-6 コールバックの合成パターン（完全版）

複数の関心事（認証、ログ、フィルタリング等）を別々のコールバック関数に分離し、
合成して使うパターン。各コールバックがNoneを返せば次へ進み、
LlmResponseを返せば以降をスキップして早期リターンする。
"""
from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from typing import Optional, Callable

# 型エイリアスの定義
BeforeModelCallback = Callable[
    [CallbackContext, LlmRequest],
    Optional[LlmResponse],
]

def compose_before_model_callbacks(
    *callbacks: BeforeModelCallback,
) -> BeforeModelCallback:
    """複数のbefore_model_callbackを合成する"""
    def composed(
        callback_context: CallbackContext,
        llm_request: LlmRequest,
    ) -> Optional[LlmResponse]:
        for callback in callbacks:
            result = callback(callback_context, llm_request)
            if result is not None:
                # いずれかのコールバックがLlmResponseを返したらLLM呼び出しをスキップ
                return result
        return None
    return composed

# 個別のコールバック関数を定義
def log_request(ctx: CallbackContext, req: LlmRequest) -> Optional[LlmResponse]:
    """リクエストをログに記録する"""
    import logging
    logging.info(f"LLMリクエスト: {len(req.contents)} メッセージ")
    return None

def check_rate_limit(ctx: CallbackContext, req: LlmRequest) -> Optional[LlmResponse]:
    """レート制限をチェックする"""
    count = ctx.state.get("request_count", 0)
    if count >= 100:
        return LlmResponse(
            content=types.Content(parts=[types.Part(text="本日のリクエスト上限に達しました。")])
        )
    ctx.state["request_count"] = count + 1
    return None

def inject_context(ctx: CallbackContext, req: LlmRequest) -> Optional[LlmResponse]:
    """コンテキスト情報を注入する"""
    user_info = ctx.state.get("user_info", {})
    if user_info:
        info_text = f"[ユーザー情報] {user_info.get('name', '不明')} ({user_info.get('tier', '一般')})"
        req.contents.append(
            types.Content(role="user", parts=[types.Part(text=info_text)])
        )
    return None

# コールバックの合成
agent = Agent(
    name="support_agent",
    model="gemini-3.5-flash",
    instruction="...",
    before_model_callback=compose_before_model_callbacks(
        log_request,        # 1. ログ記録
        check_rate_limit,   # 2. レート制限チェック
        inject_context,     # 3. コンテキスト注入
    ),
)
