# samples/chapter03/callbacks_examples/guardrails.py
"""3-4-8 ガードレールとしてのコールバック活用（完全版）

- 入力ガードレール: プロンプトインジェクション対策（before_model_callback）
- 出力ガードレール: PII（個人識別情報）の漏えい防止（after_model_callback）
- ツールガードレール: 破壊的操作の制御（before_tool_callback）
"""
import re
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools import BaseTool, ToolContext
from google.genai import types
from typing import Optional

# --- 入力ガードレール: プロンプトインジェクション対策 ---

# プロンプトインジェクションのパターン
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"system\s*:\s*",
    r"you\s+are\s+now\s+a\s+",
    r"forget\s+(all\s+)?your\s+instructions",
    r"以前の指示を(すべて)?無視",
    r"あなたは今から",
]

def detect_prompt_injection(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """プロンプトインジェクションを検出するガードレール"""
    # 最新のユーザーメッセージを取得
    user_messages = [
        c for c in llm_request.contents
        if c.role == "user"
    ]
    if not user_messages:
        return None

    last_message = user_messages[-1]
    text = " ".join(
        p.text for p in last_message.parts if hasattr(p, "text") and p.text
    )

    # パターンマッチング
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            # 検出ログを記録
            callback_context.state["injection_detected"] = True
            callback_context.state["injection_pattern"] = pattern

            return LlmResponse(
                content=types.Content(
                    parts=[types.Part(
                        text="申し訳ございません。ご質問の内容を"
                             "もう少し具体的にお教えいただけますか？"
                    )]
                )
            )

    return None


# --- 出力ガードレール: PII（個人識別情報）の漏えい防止 ---

# PIIパターンの定義
PII_PATTERNS = {
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "phone_jp": r"0\d{1,4}-?\d{1,4}-?\d{4}",
    "credit_card": r"\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}",
    "my_number": r"\d{4}\s?\d{4}\s?\d{4}",
}

def mask_pii_in_response(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> Optional[LlmResponse]:
    """LLMレスポンスからPIIをマスクするガードレール"""
    parts = llm_response.content.parts if llm_response.content else []
    if not parts:
        return None

    text = parts[0].text if parts[0].text else ""
    masked = False

    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, text):
            # PIIをマスク
            text = re.sub(pattern, f"[{pii_type.upper()}_MASKED]", text)
            masked = True

            # 検出ログを記録
            pii_log = callback_context.state.get("pii_detection_log", [])
            pii_log.append({"type": pii_type, "action": "masked"})
            callback_context.state["pii_detection_log"] = pii_log

    if masked:
        return LlmResponse(
            content=types.Content(parts=[types.Part(text=text)])
        )

    return None


# --- ツールガードレール: 破壊的操作の制御 ---

# 破壊的操作に分類されるツール
DESTRUCTIVE_TOOLS = {
    "cancel_order": "注文のキャンセル",
    "delete_account": "アカウントの削除",
    "process_refund": "返金処理",
}

def confirm_destructive_action(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
) -> Optional[dict]:
    """破壊的操作に対して確認を要求するガードレール"""
    tool_name = tool.name

    if tool_name not in DESTRUCTIVE_TOOLS:
        return None

    # 確認済みフラグをチェック
    confirmation_key = f"confirmed_{tool_name}_{hash(str(args))}"
    if tool_context.state.get(confirmation_key):
        # 確認済みの場合はツール実行を続行
        return None

    # 未確認の場合は確認メッセージを返す
    action_name = DESTRUCTIVE_TOOLS[tool_name]
    return {
        "status": "confirmation_required",
        "message": f"{action_name}を実行します。この操作は取り消せません。"
                   f"続行する場合は「はい」とお答えください。",
        "action": tool_name,
        "args": args,
    }
