# samples/chapter10/audit_logger.py
"""監査ログの実装例（10-5-1 完全版）

ADKのコールバック機構でエージェントの行動（LLM呼び出し・ツール実行）を
PIIマスキング付きの構造化ログとして記録する。
紙面で省略した import文・generate_trace_id・audit_after_model・audit_before_tool を含む完全版。
統合版は secure_agent/audit_log.py を参照。
"""
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools import ToolContext, BaseTool
from datetime import datetime, timezone, timedelta
import json
import logging
import hashlib
import re

# 構造化ログの設定
logger = logging.getLogger("audit")
logger.setLevel(logging.INFO)

JST = timezone(timedelta(hours=9))

# PIIマスキングパターン
PII_PATTERNS = [
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "[EMAIL]"),
    (re.compile(r"\b0[0-9]{1,4}-[0-9]{1,4}-[0-9]{4}\b"), "[PHONE]"),
    (re.compile(r"\b\d{3}-\d{4}\b"), "[ZIPCODE]"),
]


def mask_pii(text: str) -> str:
    """テキストからPII（個人情報）をマスキングする"""
    masked = text
    for pattern, replacement in PII_PATTERNS:
        masked = pattern.sub(replacement, masked)
    return masked


def generate_trace_id(session_id: str, timestamp: str) -> str:
    """トレースIDを生成する"""
    raw = f"{session_id}:{timestamp}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def audit_before_model(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> LlmResponse | None:
    """LLM呼び出し前の監査ログ"""
    now = datetime.now(JST)
    session_id = callback_context.state.get("session_id", "unknown")
    user_id = callback_context.state.get("user_id", "unknown")

    # 最新のユーザー入力を取得（マスキング済み）
    user_input = ""
    if llm_request.contents:
        last_content = llm_request.contents[-1]
        if last_content.role == "user":
            for part in last_content.parts:
                if hasattr(part, "text") and part.text:
                    user_input += part.text

    log_entry = {
        "event": "llm_request",
        "timestamp": now.isoformat(),
        "trace_id": generate_trace_id(session_id, now.isoformat()),
        "session_id": session_id,
        "user_id": user_id,
        "agent_name": callback_context.agent_name,
        "user_input_masked": mask_pii(user_input),
        "content_count": len(llm_request.contents) if llm_request.contents else 0,
    }
    logger.info(json.dumps(log_entry, ensure_ascii=False))

    return None  # ログ記録のみで処理は続行


def audit_after_model(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> LlmResponse | None:
    """LLM呼び出し後の監査ログ"""
    now = datetime.now(JST)
    session_id = callback_context.state.get("session_id", "unknown")

    # レスポンスのテキスト長を記録（内容そのものは記録しない）
    response_length = 0
    if llm_response.content and llm_response.content.parts:
        for part in llm_response.content.parts:
            if hasattr(part, "text") and part.text:
                response_length += len(part.text)

    log_entry = {
        "event": "llm_response",
        "timestamp": now.isoformat(),
        "session_id": session_id,
        "agent_name": callback_context.agent_name,
        "response_length": response_length,
    }
    logger.info(json.dumps(log_entry, ensure_ascii=False))

    return None


def audit_before_tool(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
) -> dict | None:
    """ツール実行前の監査ログ

    シグネチャ: (BaseTool, dict, ToolContext) -> Optional[dict]"""
    now = datetime.now(JST)
    session_id = tool_context.state.get("session_id", "unknown")
    user_id = tool_context.state.get("user_id", "unknown")

    # 引数のマスキング
    masked_args = {}
    for key, value in args.items():
        if isinstance(value, str):
            masked_args[key] = mask_pii(value)
        else:
            masked_args[key] = value

    log_entry = {
        "event": "tool_invocation",
        "timestamp": now.isoformat(),
        "session_id": session_id,
        "user_id": user_id,
        "tool_name": tool.name,
        "args_masked": masked_args,
    }
    logger.info(json.dumps(log_entry, ensure_ascii=False))

    return None  # ログ記録のみで処理は続行
