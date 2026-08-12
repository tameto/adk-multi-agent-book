# samples/chapter07/approval_server/tools.py
"""承認エージェントのツール関数（A2Aサーバー用）

経費精算の承認フローを管理するツールを定義する。
承認ルールに基づき、自動承認・上長承認・部長承認を判定する。
"""

from datetime import datetime

# ダミーの承認データストア
_approval_store: dict[str, dict] = {}
_next_id = 1

# 承認ルールの閾値
AUTO_APPROVE_LIMIT = 5_000       # 5,000円以下: 自動承認
MANAGER_APPROVE_LIMIT = 50_000   # 50,001円以上: 部長承認が必要


def submit_approval(expense_id: str, amount: int, reason: str) -> dict:
    """承認申請を受け付け、承認ルールに基づき判定する

    承認ルール:
    - 5,000円以下: 自動承認
    - 5,001円〜50,000円: 上長承認が必要（INPUT_REQUIRED）
    - 50,001円以上: 部長承認が必要（INPUT_REQUIRED）

    Args:
        expense_id: 経費ID（例: EXP-001）
        amount: 経費金額（円）
        reason: 承認申請の理由

    Returns:
        承認結果を含む辞書
    """
    global _next_id

    approval_id = f"APR-{_next_id:03d}"
    _next_id += 1

    # 自動承認（5,000円以下）
    if amount <= AUTO_APPROVE_LIMIT:
        approval = {
            "id": approval_id,
            "expense_id": expense_id,
            "amount": amount,
            "reason": reason,
            "status": "approved",
            "approver": "system",
            "decided_at": datetime.now().isoformat(),
            "message": (
                f"経費 {expense_id}（{amount:,}円）は"
                f"自動承認されました。"
            ),
        }
        _approval_store[approval_id] = approval
        return approval

    # 上長承認が必要（5,001円〜50,000円）
    if amount <= MANAGER_APPROVE_LIMIT:
        approval = {
            "id": approval_id,
            "expense_id": expense_id,
            "amount": amount,
            "reason": reason,
            "status": "pending_manager",
            "required_approver": "上長",
            "message": (
                f"経費 {expense_id}（{amount:,}円）は"
                f"上長の承認が必要です。承認依頼を送信しました。"
            ),
        }
        _approval_store[approval_id] = approval
        return approval

    # 部長承認が必要（50,001円以上）
    approval = {
        "id": approval_id,
        "expense_id": expense_id,
        "amount": amount,
        "reason": reason,
        "status": "pending_director",
        "required_approver": "部長",
        "message": (
            f"経費 {expense_id}（{amount:,}円）は"
            f"部長の承認が必要です。承認依頼を送信しました。"
        ),
    }
    _approval_store[approval_id] = approval
    return approval


def check_approval_status(approval_id: str) -> dict:
    """承認ステータスを確認する

    Args:
        approval_id: 承認ID（例: APR-001）

    Returns:
        承認ステータスを含む辞書
    """
    approval = _approval_store.get(approval_id)
    if not approval:
        return {"error": f"承認ID {approval_id} は見つかりませんでした。"}

    return approval
