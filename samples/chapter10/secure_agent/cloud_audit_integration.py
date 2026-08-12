# samples/chapter10/secure_agent/cloud_audit_integration.py
"""Cloud Logging統合（10-5-2節）

エージェントの監査イベントを Cloud Logging のカスタムログとして送出する。
Google Cloud のサービス管理操作・データアクセスを記録する Cloud Audit Logs
とは別物だが、Cloud Logging から横断検索することで統合的に分析できる。

実行時依存: google-cloud-logging パッケージが必要
    pip install google-cloud-logging
認証は Application Default Credentials（ADC）を使用する。
    gcloud auth application-default login
"""
import json
from datetime import datetime, timedelta, timezone

from google.cloud import logging as cloud_logging

JST = timezone(timedelta(hours=9))


class CloudAuditLogger:
    """Cloud Loggingに監査ログを送信する"""

    def __init__(self, project_id: str, log_name: str = "agent-audit"):
        self.client = cloud_logging.Client(project=project_id)
        self.logger = self.client.logger(log_name)

    def log_agent_action(
        self,
        action: str,
        agent_name: str,
        user_id: str,
        session_id: str,
        details: dict | None = None,
        severity: str = "INFO",
    ) -> None:
        """エージェントのアクションを監査ログとして記録する"""
        entry = {
            "action": action,
            "agent_name": agent_name,
            "user_id": user_id,
            "session_id": session_id,
            "timestamp": datetime.now(JST).isoformat(),
            "details": details or {},
        }
        self.logger.log_struct(
            entry,
            severity=severity,
            labels={"component": "agent-system", "agent_name": agent_name},
        )

    def log_security_event(
        self,
        session_id: str,
        user_id: str,
        event_type: str,
        details: dict,
        agent_name: str = "",
    ) -> None:
        """セキュリティイベントを記録する

        引数順は10-5-1節の `AuditLogger.log_security_event` と揃えている。
        ローカル監査（`AuditLogger`）と Cloud 連携（`CloudAuditLogger`）を
        用途に応じて使い分けられる。
        ただし `details` の型は Cloud Logging が構造化データを扱うため
        `dict` とし、`AuditLogger`（JSON 文字列化した `str`）とは異なる。
        呼び出し側は送信先に合わせて型を組み立てる。
        """
        self.log_agent_action(
            action=f"security:{event_type}",
            agent_name=agent_name,
            user_id=user_id,
            session_id=session_id,
            details=details,
            severity="WARNING",
        )
