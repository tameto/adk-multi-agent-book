# samples/chapter05/expense_agent/tools.py
"""経費精算エージェントのツール関数

経費の申請・照会・承認を行うツールを定義する。
本番ではデータベースや社内APIを呼び出すが、
ハンズオンではダミーデータを返す。
"""

from copy import deepcopy
from datetime import datetime

from google.adk.tools import ToolContext

# ダミーの経費データストア。本番ではDBや社内APIでセッション間の分離を担保する。
_INITIAL_EXPENSE_STORE: dict[str, dict] = {
    "EXP-001": {
        "id": "EXP-001",
        "date": "2025-07-10",
        "category": "交通費",
        "amount": 1280,
        "description": "客先訪問のタクシー代",
        "status": "approved",
        "submitted_by": "user-001",
        "submitted_at": "2025-07-10T10:00:00",
    },
    "EXP-002": {
        "id": "EXP-002",
        "date": "2025-07-15",
        "category": "会議費",
        "amount": 8500,
        "description": "チームランチミーティング",
        "status": "pending",
        "submitted_by": "user-001",
        "submitted_at": "2025-07-15T14:30:00",
    },
    "EXP-003": {
        "id": "EXP-003",
        "date": "2025-07-20",
        "category": "交通費",
        "amount": 650000,
        "description": "海外出張の航空券",
        "status": "pending_approval",
        "submitted_by": "user-002",
        "submitted_at": "2025-07-20T09:00:00",
    },
}

_INITIAL_NEXT_ID = 4
_STORE_STATE_KEY = "temp:expense_store"
_NEXT_ID_STATE_KEY = "temp:expense_next_id"

# 直接関数を呼び出すテストやデモ用のフォールバックストア。
_expense_store: dict[str, dict] = deepcopy(_INITIAL_EXPENSE_STORE)

# 経費IDカウンター（ハンズオン用インメモリ。本番ではDBのシーケンスや採番サービスを使う）
_next_id = _INITIAL_NEXT_ID


def reset_data() -> None:
    """直接実行やテスト時にフォールバックのダミーデータを初期化する。"""
    global _expense_store, _next_id
    _expense_store = deepcopy(_INITIAL_EXPENSE_STORE)
    _next_id = _INITIAL_NEXT_ID


def _get_store(tool_context: ToolContext | None) -> dict[str, dict]:
    if tool_context is None:
        return _expense_store
    return tool_context.state.setdefault(
        _STORE_STATE_KEY,
        deepcopy(_INITIAL_EXPENSE_STORE),
    )


def _set_store(
    tool_context: ToolContext | None,
    store: dict[str, dict],
) -> None:
    if tool_context is not None:
        tool_context.state[_STORE_STATE_KEY] = store


def _issue_expense_id(tool_context: ToolContext | None) -> str:
    global _next_id

    if tool_context is None:
        expense_id = f"EXP-{_next_id:03d}"
        _next_id += 1
        return expense_id

    next_id = tool_context.state.setdefault(_NEXT_ID_STATE_KEY, _INITIAL_NEXT_ID)
    tool_context.state[_NEXT_ID_STATE_KEY] = next_id + 1
    return f"EXP-{next_id:03d}"


def submit_expense(
    date: str,
    category: str,
    amount: int,
    description: str,
    tool_context: ToolContext | None = None,
) -> dict:
    """経費を申請する

    Args:
        date: 経費発生日（例: 2025-07-10）
        category: カテゴリ（交通費、会議費、消耗品費、通信費 等）
        amount: 金額（円）。正の整数で指定
        description: 業務目的・補足（例: 客先訪問の移動）。タクシー代などの費目名は含めない

    Returns:
        申請結果を含む辞書
    """
    # 金額バリデーション
    if amount <= 0:
        return {"error": "金額は正の整数で指定してください。"}

    if amount > 1_000_000_000:
        return {"error": "金額が上限（10億円）を超えています。"}

    store = _get_store(tool_context)
    expense_id = _issue_expense_id(tool_context)

    # 高額経費の場合は承認待ちステータス
    status = "pending_approval" if amount >= 500_000 else "pending"

    expense = {
        "id": expense_id,
        "date": date,
        "category": category,
        "amount": amount,
        "description": description,
        "status": status,
        "submitted_by": "user-001",
        "submitted_at": datetime.now().isoformat(),
    }

    store[expense_id] = expense
    _set_store(tool_context, store)

    result = {
        "expense_id": expense_id,
        "status": status,
        "message": f"経費 {expense_id} を申請しました。",
    }

    # 高額経費の場合は承認が必要な旨を通知
    if status == "pending_approval":
        result["message"] += (
            f" 金額が50万円以上のため、承認が必要です。"
        )

    return result


def query_expenses(
    user_id: str,
    month: str,
    tool_context: ToolContext | None = None,
) -> dict:
    """経費一覧を照会する

    Args:
        user_id: ユーザーID（例: user-001）
        month: 照会対象月（例: 2025-07）

    Returns:
        経費一覧を含む辞書
    """
    store = _get_store(tool_context)

    # 該当ユーザー・月の経費をフィルタリング
    matching = [
        deepcopy(exp) for exp in store.values()
        if exp["submitted_by"] == user_id
        and exp["date"].startswith(month)
    ]

    if not matching:
        return {
            "user_id": user_id,
            "month": month,
            "total_count": 0,
            "total_amount": 0,
            "expenses": [],
            "message": f"{month}の経費データはありません。",
        }

    total_amount = sum(exp["amount"] for exp in matching)

    return {
        "user_id": user_id,
        "month": month,
        "total_count": len(matching),
        "total_amount": total_amount,
        "expenses": matching,
    }


def approve_expense(
    expense_id: str,
    tool_context: ToolContext | None = None,
) -> dict:
    """経費を承認する

    Args:
        expense_id: 経費ID（例: EXP-001）

    Returns:
        承認結果を含む辞書
    """
    store = _get_store(tool_context)
    expense = store.get(expense_id)

    if not expense:
        return {"error": f"経費 {expense_id} は見つかりませんでした。"}

    if expense["status"] == "approved":
        return {
            "expense_id": expense_id,
            "message": f"経費 {expense_id} は既に承認済みです。",
        }

    if expense["status"] not in ("pending", "pending_approval"):
        return {
            "expense_id": expense_id,
            "error": f"経費 {expense_id} は承認できない状態です"
                     f"（現在のステータス: {expense['status']}）。",
        }

    # 承認処理
    expense["status"] = "approved"
    expense["approved_at"] = datetime.now().isoformat()
    _set_store(tool_context, store)

    return {
        "expense_id": expense_id,
        "amount": expense["amount"],
        "status": "approved",
        "message": f"経費 {expense_id}（{expense['amount']:,}円）を承認しました。",
    }
