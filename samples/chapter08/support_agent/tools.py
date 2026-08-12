# samples/chapter08/support_agent/tools.py
"""カスタマーサポートエージェントのツール関数"""
import json
import logging

logger = logging.getLogger(__name__)

# サンプルFAQデータ（実環境ではデータベースやRAGから取得）
FAQ_DATABASE: dict[str, str] = {
    "返品": (
        "商品到着後14日以内であれば返品を承ります。"
        "マイページの注文履歴から返品申請を行ってください。"
    ),
    "送料": (
        "5,000円以上のご注文で送料無料です。"
        "5,000円未満の場合、全国一律550円の送料がかかります。"
    ),
    "支払い方法": (
        "クレジットカード（VISA / Mastercard / JCB）、"
        "コンビニ決済、銀行振込に対応しています。"
    ),
    "配送日数": (
        "通常、ご注文から2〜5営業日で配送されます。"
        "お届け先や在庫状況により前後する場合があります。"
    ),
}

# サンプル注文データ
SAMPLE_ORDERS: dict[str, dict] = {
    "ORD-10001": {
        "id": "ORD-10001",
        "customer_id": "C-001",
        "status": "配送中",
        "items": [{"name": "ワイヤレスマウス", "quantity": 1, "price": 3980}],
        "total": 3980,
        "created_at": "2025-06-01",
    },
    "ORD-10002": {
        "id": "ORD-10002",
        "customer_id": "C-002",
        "status": "準備中",
        "items": [{"name": "キーボード", "quantity": 1, "price": 12800}],
        "total": 12800,
        "created_at": "2025-06-02",
    },
}


def search_faq(query: str) -> dict:
    """FAQデータベースからキーワードに一致する回答を検索する

    Args:
        query: 検索キーワード（例: 返品、送料）
    """
    results = []
    for keyword, answer in FAQ_DATABASE.items():
        if keyword in query or query in keyword:
            results.append({"keyword": keyword, "answer": answer})

    if not results:
        return {
            "found": False,
            "message": f"「{query}」に一致するFAQが見つかりませんでした。",
        }

    return {"found": True, "results": results}


def get_order_status(order_id: str) -> dict:
    """注文IDから注文のステータスを取得する

    Args:
        order_id: 注文ID（例: ORD-10001）
    """
    order = SAMPLE_ORDERS.get(order_id)
    if not order:
        return {"error": f"注文 {order_id} は見つかりませんでした。"}

    logger.info(
        json.dumps(
            {"event": "order_lookup", "order_id": order_id},
            ensure_ascii=False,
        )
    )
    return order


def escalate_to_human(reason: str) -> dict:
    """対応困難な問い合わせを人間のオペレーターにエスカレーションする

    Args:
        reason: エスカレーションの理由
    """
    logger.warning(
        json.dumps(
            {"event": "escalation", "reason": reason},
            ensure_ascii=False,
        )
    )
    return {
        "status": "escalated",
        "message": "人間のオペレーターに転送します。しばらくお待ちください。",
        "reason": reason,
    }
