# samples/chapter07/expense_server/tools.py
"""経費精算エージェントのツール関数（A2Aサーバー用）

経費データの登録・照会を行うツールを定義する。
本番ではデータベースや社内APIを呼び出すが、
ハンズオンではダミーデータを返す。
"""

from datetime import datetime

# ダミーの経費データストア
_expense_store: dict[str, dict] = {
    "EXP-001": {
        "id": "EXP-001",
        "date": "2025-07-10",
        "category": "交通費",
        "amount": 1280,
        "description": "客先訪問の電車代",
        "status": "approved",
    },
    "EXP-002": {
        "id": "EXP-002",
        "date": "2025-07-15",
        "category": "会議費",
        "amount": 8500,
        "description": "チームランチ",
        "status": "pending",
    },
}

_next_id = 3


def register_expense(
    date: str,
    category: str,
    amount: int,
    description: str,
) -> dict:
    """経費データを登録する

    Args:
        date: 経費発生日（例: 2025-07-10）
        category: カテゴリ（交通費、会議費、消耗品費、通信費 等）
        amount: 金額（円）。正の整数で指定
        description: 経費の説明

    Returns:
        登録結果を含む辞書
    """
    global _next_id

    if amount <= 0:
        return {"error": "金額は正の整数で指定してください。"}

    expense_id = f"EXP-{_next_id:03d}"
    _next_id += 1

    expense = {
        "id": expense_id,
        "date": date,
        "category": category,
        "amount": amount,
        "description": description,
        "status": "pending",
        "registered_at": datetime.now().isoformat(),
    }

    _expense_store[expense_id] = expense

    return {
        "expense_id": expense_id,
        "status": "pending",
        "message": f"経費 {expense_id}（{amount:,}円 / {category}）を登録しました。",
    }


def query_expenses(period: str) -> dict:
    """登録済み経費を照会する

    Args:
        period: 照会対象期間（例: 2025-07）

    Returns:
        経費一覧を含む辞書
    """
    matching = [
        exp for exp in _expense_store.values()
        if exp["date"].startswith(period)
    ]

    if not matching:
        return {
            "period": period,
            "total_count": 0,
            "total_amount": 0,
            "expenses": [],
            "message": f"{period}の経費データはありません。",
        }

    total_amount = sum(exp["amount"] for exp in matching)

    return {
        "period": period,
        "total_count": len(matching),
        "total_amount": total_amount,
        "expenses": matching,
    }
