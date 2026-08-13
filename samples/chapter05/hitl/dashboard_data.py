# 5-5-7. 発展: 承認ダッシュボードの設計
# 実行には google-cloud-firestore パッケージが必要
"""承認ダッシュボードのデータ取得"""
from datetime import datetime, timedelta

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter


class ApprovalDashboard:
    """承認ダッシュボードのデータを提供するクラス"""

    def __init__(self, project_id: str):
        self.db = firestore.Client(project=project_id)
        self.collection = self.db.collection("approval_requests")

    def get_summary(self) -> dict:
        """ダッシュボードサマリーを取得する"""
        now = datetime.now()
        last_24h = now - timedelta(hours=24)

        # 過去24時間のリクエスト
        recent_docs = (
            self.collection
            .where(filter=FieldFilter("created_at", ">=", last_24h))
            .stream()
        )

        summary = {
            "pending": 0,
            "approved": 0,
            "rejected": 0,
            "expired": 0,
            "avg_response_time_minutes": 0,
            "by_tool": {},
        }

        response_times = []

        for doc in recent_docs:
            data = doc.to_dict()
            status = data["status"]
            summary[status] = summary.get(status, 0) + 1

            # ツール別の集計
            tool_name = data["tool_name"]
            if tool_name not in summary["by_tool"]:
                summary["by_tool"][tool_name] = {
                    "pending": 0,
                    "approved": 0,
                    "rejected": 0,
                }
            summary["by_tool"][tool_name][status] += 1

            # 応答時間の計算
            if data["decisions"]:
                first_decision = data["decisions"][0]
                response_time = (
                    first_decision["timestamp"] - data["created_at"]
                ).total_seconds() / 60
                response_times.append(response_time)

        if response_times:
            summary["avg_response_time_minutes"] = (
                sum(response_times) / len(response_times)
            )

        return summary
