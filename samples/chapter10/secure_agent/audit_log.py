# samples/chapter10/secure_agent/audit_log.py
"""監査ログ実装

エージェントの全操作を構造化JSON形式で記録する。
PIIマスキング付きで、コンプライアンス要件に対応。
"""
import hashlib
import json
import logging
import re
from datetime import datetime, timedelta, timezone

# 構造化ログの設定
logger = logging.getLogger("audit")
logger.setLevel(logging.INFO)

JST = timezone(timedelta(hours=9))

# PIIマスキングパターン
PII_PATTERNS: list[tuple[re.Pattern, str]] = [
    (
        re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        ),
        "[EMAIL]",
    ),
    (re.compile(r"\b0[0-9]{1,4}-[0-9]{1,4}-[0-9]{4}\b"), "[PHONE]"),
    (re.compile(r"\b\d{3}-\d{4}\b"), "[ZIPCODE]"),
    # クレジットカード番号（簡易パターン）
    (re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"), "[CARD]"),
]


def mask_pii(text: str) -> str:
    """テキストからPII（個人情報）をマスキングする"""
    masked = text
    for pattern, replacement in PII_PATTERNS:
        masked = pattern.sub(replacement, masked)
    return masked


def _generate_trace_id(session_id: str, timestamp: str) -> str:
    """トレースIDを生成する"""
    raw = f"{session_id}:{timestamp}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


class AuditLogger:
    """構造化された監査ログの記録

    全イベントをJSON形式でログ出力する。
    本番環境ではCloud Loggingに自動送信される。
    """

    def log_llm_request(
        self,
        session_id: str,
        user_id: str,
        agent_name: str,
        user_input: str,
        content_count: int,
    ) -> None:
        """LLM呼び出し前のログを記録する"""
        now = datetime.now(JST)
        entry = {
            "event": "llm_request",
            "timestamp": now.isoformat(),
            "trace_id": _generate_trace_id(session_id, now.isoformat()),
            "session_id": session_id,
            "user_id": user_id,
            "agent_name": agent_name,
            "user_input_masked": mask_pii(user_input),
            "content_count": content_count,
        }
        logger.info(json.dumps(entry, ensure_ascii=False))

    def log_llm_response(
        self,
        session_id: str,
        agent_name: str,
        response_length: int,
    ) -> None:
        """LLM呼び出し後のログを記録する"""
        now = datetime.now(JST)
        entry = {
            "event": "llm_response",
            "timestamp": now.isoformat(),
            "session_id": session_id,
            "agent_name": agent_name,
            "response_length": response_length,
        }
        logger.info(json.dumps(entry, ensure_ascii=False))

    def log_tool_invocation(
        self,
        session_id: str,
        user_id: str,
        tool_name: str,
        args: dict,
    ) -> None:
        """ツール実行のログを記録する"""
        now = datetime.now(JST)
        # 引数のPIIをマスキング
        masked_args = {}
        for key, value in args.items():
            if isinstance(value, str):
                masked_args[key] = mask_pii(value)
            else:
                masked_args[key] = value

        entry = {
            "event": "tool_invocation",
            "timestamp": now.isoformat(),
            "session_id": session_id,
            "user_id": user_id,
            "tool_name": tool_name,
            "args_masked": masked_args,
        }
        logger.info(json.dumps(entry, ensure_ascii=False))

    def log_security_event(
        self,
        session_id: str,
        user_id: str,
        event_type: str,
        details: str,
    ) -> None:
        """セキュリティイベントのログを記録する"""
        now = datetime.now(JST)
        entry = {
            "event": "security",
            "timestamp": now.isoformat(),
            "session_id": session_id,
            "user_id": user_id,
            "security_event_type": event_type,
            "details": details,
        }
        logger.warning(json.dumps(entry, ensure_ascii=False))


# グローバルインスタンス
audit_logger = AuditLogger()
