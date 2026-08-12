# samples/chapter03/support_agent/callbacks.py
"""コンテキスト制御のためのコールバック関数群"""
import re
import time
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools import BaseTool, ToolContext
from google.genai import types
from typing import Optional, Callable

# 型エイリアス
BeforeModelCallback = Callable[
    [CallbackContext, LlmRequest],
    Optional[LlmResponse],
]


def compose_before_model_callbacks(
    *callbacks: BeforeModelCallback,
) -> BeforeModelCallback:
    """複数のbefore_model_callbackを順序付きで合成する"""
    def composed(
        callback_context: CallbackContext,
        llm_request: LlmRequest,
    ) -> Optional[LlmResponse]:
        for callback in callbacks:
            result = callback(callback_context, llm_request)
            if result is not None:
                return result
        return None
    return composed


# --- before_model_callback ---

def rate_limit_check(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """LLM呼び出し回数を制限するコールバック"""
    call_count = callback_context.state.get("llm_call_count", 0)
    callback_context.state["llm_call_count"] = call_count + 1

    if call_count >= 10:
        return LlmResponse(
            content=types.Content(
                parts=[types.Part(
                    text="申し訳ございません。本セッションでの処理回数が"
                         "上限に達しました。新しいセッションを開始してください。"
                )]
            )
        )
    return None


def inject_order_context(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """アクティブな注文情報をLLMリクエストに注入するコールバック"""
    active_orders = callback_context.state.get("active_orders", [])

    if not active_orders:
        return None

    # 注文情報をシステムメッセージとして構築
    order_lines = []
    for order in active_orders[:5]:  # 最大5件に制限（コンテキスト予算の管理）
        order_lines.append(
            f"- 注文#{order['id']}: {order['status']} "
            f"({order.get('date', '日付不明')}) "
            f"¥{order.get('total', 0):,}"
        )

    context_message = types.Content(
        role="user",
        parts=[types.Part(
            text=f"[システム情報] ユーザーのアクティブな注文:\n"
                 + "\n".join(order_lines)
        )],
    )
    llm_request.contents.append(context_message)
    return None


# --- after_model_callback ---

# 禁止ワードリスト
PROHIBITED_WORDS = [
    "パスワード", "クレジットカード番号", "暗証番号",
    "SSN", "マイナンバー",
]

# PIIパターン
PII_PATTERNS = {
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "credit_card": r"\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}",
}


def validate_response_content(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> Optional[LlmResponse]:
    """LLMレスポンスの安全性を検証するコールバック"""
    if not llm_response.content or not llm_response.content.parts:
        return None

    response_text = ""
    for part in llm_response.content.parts:
        if hasattr(part, "text") and part.text:
            response_text += part.text

    if not response_text:
        return None

    # 禁止ワードチェック
    for word in PROHIBITED_WORDS:
        if word in response_text:
            callback_context.state["content_violation"] = {
                "type": "prohibited_word",
                "word": word,
            }
            return LlmResponse(
                content=types.Content(
                    parts=[types.Part(
                        text="申し訳ございません。セキュリティ上の理由から、"
                             "その情報をこのチャネルでお伝えすることはできません。"
                             "セキュアなフォームからお手続きください。"
                    )]
                )
            )

    # PIIパターンチェック
    masked_text = response_text
    pii_found = False
    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, masked_text):
            masked_text = re.sub(
                pattern, f"[{pii_type.upper()}_MASKED]", masked_text
            )
            pii_found = True

    if pii_found:
        return LlmResponse(
            content=types.Content(parts=[types.Part(text=masked_text)])
        )

    return None


# --- before_tool_callback ---

# ツールごとの必要権限
TOOL_PERMISSIONS = {
    "cancel_order": ["editor", "admin"],
    "process_refund": ["admin"],
    "delete_account": ["admin"],
}


def authorize_tool_access(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
) -> Optional[dict]:
    """ユーザー権限に基づいてツールアクセスを制御するコールバック"""
    tool_name = tool.name
    user_role = tool_context.state.get("user_role", "viewer")

    # 権限チェックが必要なツールか確認
    required_roles = TOOL_PERMISSIONS.get(tool_name)
    if required_roles and user_role not in required_roles:
        return {
            "error": f"権限不足です。{tool_name} の実行には "
                     f"{', '.join(required_roles)} 権限が必要です。"
                     f"現在の権限: {user_role}",
        }

    # ツール呼び出しログを記録
    call_log = tool_context.state.get("tool_call_log", [])
    call_log.append({
        "tool": tool_name,
        "args": args,
        "timestamp": time.time(),
        "user_role": user_role,
    })
    tool_context.state["tool_call_log"] = call_log

    return None


# --- after_tool_callback ---

def trim_tool_response(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
    tool_response: dict,
) -> Optional[dict]:
    """ツール実行結果を最適化するコールバック"""
    tool_name = tool.name

    # レスポンスから内部メタデータを除去
    if isinstance(tool_response, dict):
        tool_response.pop("_internal_metadata", None)
        tool_response.pop("debug_info", None)

    # 検索結果の件数制限（コンテキスト予算の節約）
    if tool_name == "search_products":
        results = tool_response.get("results", [])
        if len(results) > 5:
            tool_response["results"] = results[:5]
            tool_response["note"] = (
                f"全{len(results)}件中、関連度の高い上位5件を表示しています"
            )

    # 実行結果をStateに記録（直近の結果のみ保持）
    tool_context.state[f"last_{tool_name}_result"] = tool_response

    return tool_response
