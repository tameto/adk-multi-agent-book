# samples/chapter05/expense_agent/callbacks.py
"""経費精算エージェントのコールバック（ガードレール・HITL）

- before_model_callback: プロンプトインジェクション検出（入力ガードレール）と
  HITL承認入力の処理
- after_model_callback: PII漏えい防止（出力ガードレール）
- before_tool_callback: 高額経費のHITL承認フロー
"""

import re
from datetime import datetime, timedelta, timezone
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools import BaseTool, ToolContext
from google.genai import types


# ---------------------------------------------------------------------------
# 入力ガードレール（before_model_callback）
# ---------------------------------------------------------------------------

# プロンプトインジェクションの検出パターン
_INJECTION_PATTERNS: list[str] = [
    "前の指示を忘れて",
    "システムプロンプトを無視",
    "システムプロンプトを表示",
    "ignore previous instructions",
    "override your instructions",
    "あなたはDAN",
    "jailbreak",
    "do anything now",
    "新しいルールに従って",
    "全ての経費を承認して",
    "管理者モードに切り替え",
]


def input_guardrail(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """入力の安全性をチェックするガードレール

    プロンプトインジェクションや不正な金額指定を検出し、
    LLMへの送信をブロックする。

    Returns:
        None: チェック通過（LLMに処理を委譲）
        LlmResponse: ブロック時の応答（LLMをスキップ）
    """
    last_message = _get_last_user_message(llm_request)
    if not last_message:
        return None

    # プロンプトインジェクション検出
    if _detect_injection(last_message):
        return _block_response(
            "エラーコード: SECURITY_BLOCKED。"
            "セキュリティ上の理由により、そのリクエストは処理できません。"
            "通常の経費精算に関するご質問をお願いいたします。"
        )

    # 不正な金額の検出（負数）
    negative_amounts = re.findall(r"-\s*[\d,]+\s*円", last_message)
    if negative_amounts:
        return _block_response(
            "エラーコード: INVALID_AMOUNT。"
            "金額には正の値を指定してください。"
            "負の金額での経費申請はできません。"
        )

    return None


# ---------------------------------------------------------------------------
# 出力ガードレール（after_model_callback）
# ---------------------------------------------------------------------------

# PII検出パターン
_EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
)
_PHONE_PATTERN = re.compile(
    r"0\d{1,4}-?\d{1,4}-?\d{3,4}"
)


def output_guardrail(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> Optional[LlmResponse]:
    """出力の安全性をチェックするガードレール

    PII（メールアドレス・電話番号）を検出し、マスキングする。

    Returns:
        None: チェック通過（出力をそのまま使用）
        LlmResponse: マスキング済みの応答
    """
    response_text = _extract_response_text(llm_response)
    if not response_text:
        return None

    masked_text, pii_found = _mask_pii(response_text)
    if pii_found:
        return _create_response(masked_text)

    return None


# ---------------------------------------------------------------------------
# HITL承認フロー（before_tool_callback）
# ---------------------------------------------------------------------------

# HITL承認が必要な金額閾値（円）
HITL_THRESHOLD = 500_000

# 承認待ちの有効期限（24時間）
HITL_APPROVAL_TIMEOUT = timedelta(hours=24)

# 承認待ちの金額と受付時刻を保持するStateキー
PENDING_AMOUNT_KEY = "_pending_hitl_amount"
PENDING_REQUESTED_AT_KEY = "_pending_hitl_requested_at"

# ユーザーの承認を表す入力
APPROVAL_PHRASE = "承認します"


def hitl_approval_callback(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
) -> Optional[dict]:
    """高額経費のHITL承認フローを実装するコールバック

    submit_expense ツールの呼び出し前に実行される。
    金額が50万円以上の場合、HITL承認を要求する。

    Returns:
        None: 承認不要またはチェック通過（ツールを実行）
        dict: ブロック時の応答（ツール実行をスキップ）
    """
    # submit_expense 以外のツールはスルー
    if tool.name != "submit_expense":
        return None

    amount = args.get("amount", 0)

    # 閾値未満はそのまま実行
    if amount < HITL_THRESHOLD:
        return None

    # 既に承認済みかチェック（Stateに承認フラグがある場合）
    approval_key = f"_hitl_approved_{amount}"
    if tool_context.state.get(approval_key):
        # 承認は1回限り有効。フラグを落としてからツール実行を許可する
        tool_context.state[approval_key] = False
        return None

    # 承認待ちの金額と受付時刻をStateに記録する
    # （handle_hitl_approval_input が承認入力の照合に使う）
    tool_context.state[PENDING_AMOUNT_KEY] = amount
    tool_context.state[PENDING_REQUESTED_AT_KEY] = _now().isoformat()

    # 承認リクエストを返す（ツール実行をブロック）
    return {
        "action": "HITL_APPROVAL_REQUIRED",
        "message": (
            f"高額経費の申請です（{amount:,}円）。承認が必要です。\n"
            f"カテゴリ: {args.get('category', '未指定')}\n"
            f"説明: {args.get('description', '未指定')}\n"
            f"承認する場合は「{APPROVAL_PHRASE}」と入力してください。"
        ),
        "amount": amount,
    }


def handle_hitl_approval_input(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """ユーザーの承認入力を処理するコールバック

    承認待ちの経費申請がある状態で「承認します」と入力されたら、
    Stateに承認フラグを立ててLLM呼び出しをスキップする。
    受付から24時間を過ぎた承認リクエストは期限切れとして無効化する。

    Returns:
        None: 承認待ちなし、または承認入力ではない（LLMに処理を委譲）
        LlmResponse: 承認・期限切れを通知する応答（LLMをスキップ）
    """
    amount = callback_context.state.get(PENDING_AMOUNT_KEY)
    if not amount:
        return None

    last_message = _get_last_user_message(llm_request)
    if not last_message or APPROVAL_PHRASE not in last_message:
        return None

    # 承認待ちの有効期限を確認する
    if _is_expired(callback_context.state.get(PENDING_REQUESTED_AT_KEY)):
        _clear_pending(callback_context)
        return _create_response(
            f"承認待ちの申請（{amount:,}円）は受付から24時間を過ぎたため"
            "無効になりました。もう一度申請してください。"
        )

    callback_context.state[f"_hitl_approved_{amount}"] = True
    _clear_pending(callback_context)

    return _create_response(
        "承認されました。続けて申請内容を送信すると"
        f"{amount:,}円の経費を登録します。"
    )


# ---------------------------------------------------------------------------
# ヘルパー関数
# ---------------------------------------------------------------------------

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


def _now() -> datetime:
    """現在時刻をUTCで返す（承認待ちの期限判定に使う）"""
    return datetime.now(timezone.utc)


def _is_expired(requested_at: Optional[str]) -> bool:
    """承認リクエストの受付時刻が有効期限を過ぎているか判定する"""
    if not requested_at:
        # 受付時刻が記録されていない場合は期限切れ扱いにしない
        return False
    try:
        requested = datetime.fromisoformat(requested_at)
    except ValueError:
        return False
    if requested.tzinfo is None:
        requested = requested.replace(tzinfo=timezone.utc)
    return _now() - requested > HITL_APPROVAL_TIMEOUT


def _clear_pending(callback_context: CallbackContext) -> None:
    """承認待ちの状態をクリアする"""
    callback_context.state[PENDING_AMOUNT_KEY] = None
    callback_context.state[PENDING_REQUESTED_AT_KEY] = None


def _detect_injection(text: str) -> bool:
    """プロンプトインジェクションの兆候を検出する"""
    text_lower = text.lower()
    return any(
        pattern.lower() in text_lower
        for pattern in _INJECTION_PATTERNS
    )


def _mask_pii(text: str) -> tuple[str, bool]:
    """PII（メールアドレス・電話番号）をマスキングする

    Returns:
        (マスキング後のテキスト, PIIが検出されたか)
    """
    pii_found = False

    # メールアドレスのマスキング
    if _EMAIL_PATTERN.search(text):
        text = _EMAIL_PATTERN.sub("[メールアドレス]", text)
        pii_found = True

    # 電話番号のマスキング
    if _PHONE_PATTERN.search(text):
        text = _PHONE_PATTERN.sub("[電話番号]", text)
        pii_found = True

    return text, pii_found


def _extract_response_text(
    response: LlmResponse,
) -> Optional[str]:
    """LlmResponseからテキストを抽出する"""
    if not response.content or not response.content.parts:
        return None
    texts = [part.text for part in response.content.parts if part.text]
    return "\n".join(texts) if texts else None


def _block_response(message: str) -> LlmResponse:
    """ブロック時の応答を生成する"""
    return LlmResponse(
        content=types.Content(
            parts=[types.Part(text=message)],
            role="model",
        )
    )


def _create_response(text: str) -> LlmResponse:
    """テキストからLlmResponseを生成する"""
    return LlmResponse(
        content=types.Content(
            parts=[types.Part(text=text)],
            role="model",
        )
    )
