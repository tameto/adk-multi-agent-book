# samples/chapter10/secure_agent/callbacks.py
"""セキュリティコールバック群

ADKの4種類のコールバックを使った多層防御の実装。
- before_model_callback: プロンプトインジェクション検出 + Kill Switch
- after_model_callback: PII/機密情報フィルタ
- before_tool_callback: ロールベースアクセス制御
- after_tool_callback: 間接インジェクション検出
"""
import logging
import re

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools import BaseTool, ToolContext
from google.genai import types

from .audit_log import audit_logger, mask_pii
from .kill_switch import kill_switch

logger = logging.getLogger(__name__)

# --- プロンプトインジェクション検出パターン ---
INJECTION_PATTERNS: list[re.Pattern] = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"(指示|命令)を(すべて|全て)?無視", re.IGNORECASE),
    re.compile(r"system\s*prompt", re.IGNORECASE),
    re.compile(r"システムプロンプト", re.IGNORECASE),
    re.compile(r"jailbreak", re.IGNORECASE),
    re.compile(r"<\s*/?system\s*>", re.IGNORECASE),
    re.compile(r"you\s+are\s+now", re.IGNORECASE),
]

# --- PII検出パターン ---
PII_PATTERNS: list[tuple[re.Pattern, str]] = [
    (
        re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        ),
        "[EMAIL]",
    ),
    (re.compile(r"\b0[0-9]{1,4}-[0-9]{1,4}-[0-9]{4}\b"), "[PHONE]"),
    (re.compile(r"\b\d{3}-\d{4}\b"), "[ZIPCODE]"),
    (re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"), "[CARD]"),
]

# --- ロール別ツール権限マップ ---
ROLE_PERMISSIONS: dict[str, set[str]] = {
    "viewer": {"lookup_customer"},
    "editor": {"lookup_customer", "update_subscription"},
    "admin": {"lookup_customer", "update_subscription", "process_refund"},
}

# --- ツール実行回数制限 ---
MAX_TOOL_CALLS_PER_SESSION = 50
MAX_TOOL_CALLS_PER_TOOL = 10


def _make_blocked_response(message: str) -> LlmResponse:
    """ブロック時の固定レスポンスを生成する"""
    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part(text=message)],
        )
    )


# ===== before_model_callback =====

def detect_injection(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> LlmResponse | None:
    """プロンプトインジェクション検出 + Kill Switchチェック

    before_model_callbackとして使用。
    """
    agent_name = callback_context.agent_name
    session_id = callback_context.state.get("session_id", "unknown")
    user_id = callback_context.state.get("user_id", "unknown")

    try:
        # Kill Switchチェック
        if kill_switch.is_agent_killed(agent_name):
            audit_logger.log_security_event(
                session_id, user_id, "kill_switch",
                f"エージェント '{agent_name}' は停止中です",
            )
            return _make_blocked_response(
                "現在メンテナンス中です。しばらくお待ちください。"
            )

        # ユーザー入力の抽出
        user_input = ""
        if llm_request.contents:
            last_content = llm_request.contents[-1]
            if last_content.role == "user":
                for part in last_content.parts:
                    if hasattr(part, "text") and part.text:
                        user_input += part.text

        # 監査ログの記録
        audit_logger.log_llm_request(
            session_id, user_id, agent_name,
            user_input,
            len(llm_request.contents) if llm_request.contents else 0,
        )

        # プロンプトインジェクション検出
        for pattern in INJECTION_PATTERNS:
            if pattern.search(user_input):
                audit_logger.log_security_event(
                    session_id, user_id, "prompt_injection",
                    f"パターン検出: {pattern.pattern}",
                )
                return _make_blocked_response(
                    "そのリクエストには対応できません。"
                    "別の表現でお試しください。"
                )

    except Exception as e:
        # ガードレールのエラーは安全側に倒す
        logger.error("before_model_callback エラー: %s", e)
        return _make_blocked_response(
            "一時的なエラーが発生しました。もう一度お試しください。"
        )

    return None  # 正常: 処理を続行


# ===== after_model_callback =====

def filter_sensitive_output(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> LlmResponse | None:
    """出力に含まれるPII/機密情報をマスキングする

    after_model_callbackとして使用。
    """
    session_id = callback_context.state.get("session_id", "unknown")
    agent_name = callback_context.agent_name

    try:
        if not llm_response.content or not llm_response.content.parts:
            return None

        modified = False
        new_parts: list[types.Part] = []
        response_length = 0

        for part in llm_response.content.parts:
            if hasattr(part, "text") and part.text:
                response_length += len(part.text)
                masked_text = mask_pii(part.text)
                if masked_text != part.text:
                    modified = True
                    audit_logger.log_security_event(
                        session_id, "", "pii_filtered",
                        "出力からPIIを検出・マスキングしました",
                    )
                new_parts.append(types.Part(text=masked_text))
            else:
                new_parts.append(part)

        # 監査ログ
        audit_logger.log_llm_response(
            session_id, agent_name, response_length,
        )

        if modified:
            return LlmResponse(
                content=types.Content(role="model", parts=new_parts)
            )

    except Exception as e:
        logger.error("after_model_callback エラー: %s", e)

    return None  # 変更なし: 元のレスポンスをそのまま返す


# ===== before_tool_callback =====

# ツール結果に潜む間接プロンプトインジェクションのパターン
TOOL_RESULT_PATTERNS: list[re.Pattern] = [
    re.compile(r"\[SYSTEM\]", re.IGNORECASE),
    re.compile(r"\[INST\]", re.IGNORECASE),
    re.compile(r"<\|im_start\|>system", re.IGNORECASE),
    re.compile(
        r"(ignore|disregard)\s+(previous|above|all)\s+"
        r"(instructions|context)",
        re.IGNORECASE,
    ),
    re.compile(r"(指示|命令)を(すべて|全て)?無視", re.IGNORECASE),
]


def check_tool_permission(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
) -> dict | None:
    """ロールベースのアクセス制御 + 実行回数制限

    before_tool_callbackとして使用。
    シグネチャ: (BaseTool, dict, ToolContext) -> Optional[dict]
    """
    tool_name = tool.name
    session_id = tool_context.state.get("session_id", "unknown")
    user_id = tool_context.state.get("user_id", "unknown")
    user_role = tool_context.state.get("user_role", "viewer")

    try:
        # ツール単位のKill Switchチェック
        if kill_switch.is_tool_killed(tool_name):
            audit_logger.log_security_event(
                session_id, user_id, "tool_kill_switch",
                f"ツール '{tool_name}' は停止中です",
            )
            return {"error": f"ツール '{tool_name}' は現在利用できません。"}

        # ロールベースアクセス制御
        allowed_tools = ROLE_PERMISSIONS.get(user_role, set())
        if tool_name not in allowed_tools:
            audit_logger.log_security_event(
                session_id, user_id, "permission_denied",
                f"ロール '{user_role}' はツール '{tool_name}' の"
                f"実行権限がありません",
            )
            return {
                "error": f"権限がありません。"
                         f"この操作には上位の権限が必要です。"
            }

        # セッション全体の実行回数制限
        total_key = "_total_tool_calls"
        total_calls = tool_context.state.get(total_key, 0)
        if total_calls >= MAX_TOOL_CALLS_PER_SESSION:
            return {
                "error": f"セッションあたりのツール実行上限"
                         f"（{MAX_TOOL_CALLS_PER_SESSION}回）に達しました。"
            }

        # ツール単位の実行回数制限
        tool_key = f"_tool_calls_{tool_name}"
        tool_calls = tool_context.state.get(tool_key, 0)
        if tool_calls >= MAX_TOOL_CALLS_PER_TOOL:
            return {
                "error": f"ツール '{tool_name}' の実行上限"
                         f"（{MAX_TOOL_CALLS_PER_TOOL}回）に達しました。"
            }

        # カウントを更新
        tool_context.state[total_key] = total_calls + 1
        tool_context.state[tool_key] = tool_calls + 1

        # 監査ログ
        audit_logger.log_tool_invocation(
            session_id, user_id, tool_name, args,
        )

    except Exception as e:
        logger.error("before_tool_callback エラー: %s", e)
        return {"error": "一時的なエラーが発生しました。"}

    return None  # 正常: ツール実行を続行


# ===== after_tool_callback =====

def sanitize_indirect_injection(text: str) -> tuple[str, bool]:
    """テキストから間接インジェクションパターンを除去する

    Returns:
        サニタイズ後のテキストと、検出有無のタプル
    """
    sanitized = text
    detected = False
    for pattern in TOOL_RESULT_PATTERNS:
        if pattern.search(sanitized):
            detected = True
            sanitized = pattern.sub("[FILTERED]", sanitized)
    return sanitized, detected


def after_tool_guard(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
    tool_response: dict,
) -> dict | None:
    """ツール結果の間接インジェクション検出とサニタイズ

    after_tool_callbackとして使用。
    シグネチャ: (BaseTool, dict, ToolContext, dict) -> Optional[dict]
    """
    session_id = tool_context.state.get("session_id", "unknown")
    user_id = tool_context.state.get("user_id", "unknown")

    try:
        if not isinstance(tool_response, dict):
            return None

        sanitized: dict = {}
        any_detected = False
        for key, value in tool_response.items():
            if isinstance(value, str):
                cleaned, detected = sanitize_indirect_injection(value)
                sanitized[key] = cleaned
                any_detected = any_detected or detected
            else:
                sanitized[key] = value

        if any_detected:
            audit_logger.log_security_event(
                session_id, user_id, "indirect_injection",
                f"ツール '{tool.name}' の結果に"
                f"不審なパターンを検出しました",
            )
            return sanitized

    except Exception as e:
        logger.error("after_tool_callback エラー: %s", e)
        return None

    return None  # 検出なし: 元のレスポンスをそのまま返す
