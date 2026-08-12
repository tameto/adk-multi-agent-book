# 5-5-4. 非同期承認フロー
# 実行には google-cloud-firestore パッケージが必要
"""非同期承認フローの実装"""
import uuid
from datetime import datetime, timedelta

from google.cloud import firestore


class AsyncApprovalManager:
    """Firestoreを使用した非同期承認フロー"""

    def __init__(self, project_id: str):
        self.db = firestore.Client(project=project_id)
        self.collection = self.db.collection("approval_requests")

    def create_request(
        self,
        tool_name: str,
        tool_input: dict,
        requested_by: str,
        approvers: list[str],
    ) -> str:
        """承認リクエストを作成する"""
        request_id = str(uuid.uuid4())

        doc_ref = self.collection.document(request_id)
        doc_ref.set({
            "request_id": request_id,
            "tool_name": tool_name,
            "tool_input": tool_input,
            "requested_by": requested_by,
            "approvers": approvers,
            "status": "pending",
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(hours=24),
            "decisions": [],
        })

        # 承認者に通知（実装は通知システムに依存）
        self._notify_approvers(request_id, approvers, tool_name, tool_input)

        return request_id

    def approve(
        self,
        request_id: str,
        approver_id: str,
        comment: str = "",
    ) -> bool:
        """承認リクエストを承認する"""
        doc_ref = self.collection.document(request_id)
        doc = doc_ref.get()

        if not doc.exists:
            return False

        data = doc.to_dict()
        if data["status"] != "pending":
            return False

        if approver_id not in data["approvers"]:
            return False

        data["decisions"].append({
            "approver_id": approver_id,
            "decision": "approved",
            "comment": comment,
            "timestamp": datetime.now(),
        })
        data["status"] = "approved"

        doc_ref.update(data)
        return True

    def reject(
        self,
        request_id: str,
        approver_id: str,
        reason: str,
    ) -> bool:
        """承認リクエストを拒否する"""
        doc_ref = self.collection.document(request_id)
        doc = doc_ref.get()

        if not doc.exists:
            return False

        data = doc.to_dict()
        if data["status"] != "pending":
            return False

        data["decisions"].append({
            "approver_id": approver_id,
            "decision": "rejected",
            "reason": reason,
            "timestamp": datetime.now(),
        })
        data["status"] = "rejected"

        doc_ref.update(data)
        return True

    def check_status(self, request_id: str) -> dict:
        """承認リクエストのステータスを確認する"""
        doc_ref = self.collection.document(request_id)
        doc = doc_ref.get()

        if not doc.exists:
            return {"status": "not_found"}

        return doc.to_dict()

    def _notify_approvers(
        self,
        request_id: str,
        approvers: list[str],
        tool_name: str,
        tool_input: dict,
    ):
        """承認者に通知を送信する（実装例）"""
        # Pub/Sub、Slack、メール等の通知チャネルと統合
        pass
