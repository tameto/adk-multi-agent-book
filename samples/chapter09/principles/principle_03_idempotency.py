# samples/chapter09/principles/principle_03_idempotency.py
"""原則3: 冪等性（Idempotency）の実装例（9-1-3 完全版）

冪等キーの導入とupsertパターンにより、
同じ引数で複数回呼び出しても結果が変わらないツールを設計する。
"""
import hashlib
import json
import uuid

from google.adk import Agent


# --- インメモリDBのダミー実装（紙面では省略。実行確認用の最小実装） ---

class _DummyCollection:
    """find_one / insert_one だけを持つインメモリコレクション"""

    def __init__(self) -> None:
        self._docs: list[dict] = []

    def find_one(self, query: dict) -> dict | None:
        """クエリに一致する最初のドキュメントを返します"""
        for doc in self._docs:
            if all(doc.get(key) == value for key, value in query.items()):
                return doc
        return None

    def insert_one(self, doc: dict) -> None:
        """ドキュメントを追加します"""
        self._docs.append(doc)


class _DummyDb:
    """ordersコレクションだけを持つダミーDB"""

    def __init__(self) -> None:
        self.orders = _DummyCollection()


db = _DummyDb()


def generate_order_id() -> str:
    """注文IDを生成します（ダミー実装）"""
    return f"ORD-{uuid.uuid4().hex[:8].upper()}"


# 冪等キーを使ったツール設計
def create_order(
    customer_id: str,
    product_id: str,
    quantity: int,
    idempotency_key: str | None = None,
) -> dict:
    """注文を作成します。冪等キーにより重複注文を防止します。

    Args:
        customer_id: 顧客ID
        product_id: 商品ID
        quantity: 数量
        idempotency_key: 冪等キー（省略時は自動生成）"""
    # 冪等キーが未指定の場合、引数から生成
    if idempotency_key is None:
        key_source = json.dumps(
            {"customer_id": customer_id, "product_id": product_id, "quantity": quantity},
            sort_keys=True,
        )
        idempotency_key = hashlib.sha256(key_source.encode()).hexdigest()[:16]

    # 既存の注文を確認（upsertパターン）
    existing_order = db.orders.find_one({"idempotency_key": idempotency_key})
    if existing_order:
        # 既に同じキーの注文がある場合、その結果を返す
        return {
            "status": "already_exists",
            "order_id": existing_order["order_id"],
            "message": "この注文は既に処理済みです。",
        }

    # 新規注文を作成
    order = {
        "order_id": generate_order_id(),
        "idempotency_key": idempotency_key,
        "customer_id": customer_id,
        "product_id": product_id,
        "quantity": quantity,
    }
    db.orders.insert_one(order)

    return {"status": "created", "order_id": order["order_id"]}


# 冪等なツールを持つエージェント
order_agent = Agent(
    name="order_agent",
    model="gemini-3.5-flash",
    instruction="""注文処理を行います。
    注文作成時は必ずidempotency_keyを指定してください。
    同じ顧客・商品・数量の組み合わせには同じキーを使用します。""",
    tools=[create_order],
)


if __name__ == "__main__":
    # 同じ引数で2回呼んでも結果が変わらないことを確認する
    first = create_order("C001", "P100", 2)
    second = create_order("C001", "P100", 2)
    print(f"1回目: {first}")   # status: created
    print(f"2回目: {second}")  # status: already_exists（同じorder_id）
