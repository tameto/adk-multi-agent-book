from datetime import datetime, timedelta, timezone
from dataclasses import dataclass

JST = timezone(timedelta(hours=9))


@dataclass
class RetentionPolicy:
    """データ保持ポリシー"""
    # セッションデータの保持期間
    session_ttl: timedelta = timedelta(days=30)
    # 監査ログの保持期間
    audit_log_ttl: timedelta = timedelta(days=365)
    # PIIを含むデータの保持期間
    pii_data_ttl: timedelta = timedelta(days=90)
    # Memory Bankの保持期間
    memory_ttl: timedelta = timedelta(days=180)


class DataRetentionManager:
    """データ保持ポリシーに基づくデータライフサイクル管理"""

    def __init__(self, policy: RetentionPolicy):
        self.policy = policy

    def is_expired(self, created_at: datetime, data_type: str) -> bool:
        """データが保持期間を超過しているか判定する"""
        now = datetime.now(JST)
        ttl_map = {
            "session": self.policy.session_ttl,
            "audit_log": self.policy.audit_log_ttl,
            "pii": self.policy.pii_data_ttl,
            "memory": self.policy.memory_ttl,
        }
        ttl = ttl_map.get(data_type, self.policy.session_ttl)
        return now - created_at > ttl

    def get_deletion_candidates(
        self, records: list[dict], data_type: str
    ) -> list[dict]:
        """削除対象のレコードを抽出する"""
        return [
            record for record in records
            if self.is_expired(record["created_at"], data_type)
        ]
