# samples/chapter10/secure_agent/tools.py
"""セキュリティ強化カスタマーサポートエージェントのツール群

各ツールは before_tool_callback で権限チェックされた後に実行される。
"""

# サンプル顧客データ（実環境ではデータベースから取得）
SAMPLE_CUSTOMERS: dict[str, dict] = {
    "C-001": {
        "id": "C-001",
        "name": "山田太郎",
        "email": "yamada@example.com",
        "plan": "standard",
        "status": "active",
        "created_at": "2024-01-15",
    },
    "C-002": {
        "id": "C-002",
        "name": "佐藤花子",
        "email": "sato@example.com",
        "plan": "premium",
        "status": "active",
        "created_at": "2024-03-20",
    },
    "C-003": {
        "id": "C-003",
        "name": "鈴木一郎",
        "email": "suzuki@example.com",
        "plan": "standard",
        "status": "suspended",
        "created_at": "2024-06-10",
    },
}

# サンプル注文データ
SAMPLE_ORDERS: dict[str, dict] = {
    "O-1001": {
        "id": "O-1001",
        "customer_id": "C-001",
        "amount": 9800,
        "status": "completed",
        "items": ["ワイヤレスマウス", "USBハブ"],
    },
    "O-1002": {
        "id": "O-1002",
        "customer_id": "C-002",
        "amount": 24800,
        "status": "processing",
        "items": ["メカニカルキーボード", "モニターアーム"],
    },
}

VALID_PLANS = ("standard", "premium", "enterprise")


def lookup_customer(customer_id: str) -> dict:
    """顧客情報を検索する

    Args:
        customer_id: 顧客ID（例: C-001）
    """
    customer = SAMPLE_CUSTOMERS.get(customer_id)
    if not customer:
        return {"error": f"顧客 {customer_id} は見つかりませんでした。"}

    # PIIを含まない安全な情報のみ返す
    return {
        "id": customer["id"],
        "plan": customer["plan"],
        "status": customer["status"],
        "created_at": customer["created_at"],
    }


def update_subscription(customer_id: str, plan: str) -> dict:
    """顧客のサブスクリプションプランを変更する

    editor以上の権限が必要（before_tool_callbackで制御）。

    Args:
        customer_id: 顧客ID（例: C-001）
        plan: 新しいプラン名（standard / premium / enterprise）
    """
    customer = SAMPLE_CUSTOMERS.get(customer_id)
    if not customer:
        return {"error": f"顧客 {customer_id} は見つかりませんでした。"}

    if plan not in VALID_PLANS:
        return {
            "error": f"無効なプラン名です。"
                     f"有効なプラン: {', '.join(VALID_PLANS)}"
        }

    if customer["status"] != "active":
        return {
            "error": "アカウントが停止中のため、プラン変更できません。"
        }

    old_plan = customer["plan"]
    # 実環境ではDBを更新する
    return {
        "customer_id": customer_id,
        "old_plan": old_plan,
        "new_plan": plan,
        "status": "updated",
        "message": f"プランを {old_plan} から {plan} に変更しました。",
    }


def process_refund(order_id: str, amount: int) -> dict:
    """返金処理を実行する

    admin権限が必要（before_tool_callbackで制御）。
    本番環境ではHITL（人間の承認）を組み合わせることを推奨。

    Args:
        order_id: 注文ID（例: O-1001）
        amount: 返金額（円）
    """
    order = SAMPLE_ORDERS.get(order_id)
    if not order:
        return {"error": f"注文 {order_id} は見つかりませんでした。"}

    if amount <= 0:
        return {"error": "返金額は1円以上を指定してください。"}

    if amount > order["amount"]:
        return {
            "error": f"返金額が注文金額（{order['amount']}円）を超えています。"
        }

    # 実環境では決済APIを呼び出す
    return {
        "order_id": order_id,
        "refund_amount": amount,
        "original_amount": order["amount"],
        "status": "refunded",
        "message": f"注文 {order_id} に対して {amount}円の返金を処理しました。",
    }
