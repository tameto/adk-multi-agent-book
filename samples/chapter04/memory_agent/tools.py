# samples/chapter04/memory_agent/tools.py
"""カスタマーサポートエージェントのツール関数"""
from google.adk.tools import ToolContext

from .state_keys import StateKeys


async def get_order_status(
    order_id: str,
    tool_context: ToolContext,
) -> dict:
    """注文の現在のステータスを取得する

    Args:
        order_id: 注文ID（例: ORD-12345）
        tool_context: ADKのToolContext
    """
    # サンプルデータ（実環境ではデータベースやAPIから取得）
    sample_orders = {
        "ORD-12345": {
            "id": "ORD-12345",
            "status": "配送中",
            "items": [
                {"name": "ワイヤレスマウス", "quantity": 1, "price": 3980},
            ],
            "total": 3980,
            "estimated_delivery": "2026-04-12",
        },
        "ORD-12346": {
            "id": "ORD-12346",
            "status": "準備中",
            "items": [
                {"name": "メカニカルキーボード", "quantity": 1, "price": 12800},
            ],
            "total": 12800,
            "estimated_delivery": "2026-04-15",
        },
    }

    order = sample_orders.get(order_id)
    if not order:
        return {"error": f"注文 {order_id} は見つかりませんでした。"}

    # 直近のツール結果をStateに保存（Compactionの対象外）
    tool_context.state[StateKeys.TEMP_LAST_TOOL_RESULT] = {
        "tool": "get_order_status",
        "order_id": order_id,
    }

    return order


async def search_products(
    query: str,
    tool_context: ToolContext,
    category: str = "",
) -> dict:
    """商品を検索する

    Args:
        query: 検索クエリ
        tool_context: ADKのToolContext
        category: カテゴリフィルタ（オプション）
    """
    # サンプルデータ
    sample_products = [
        {"id": "PROD-001", "name": "ワイヤレスマウス",
         "price": 3980, "category": "周辺機器", "rating": 4.5},
        {"id": "PROD-002", "name": "メカニカルキーボード",
         "price": 12800, "category": "周辺機器", "rating": 4.8},
        {"id": "PROD-003", "name": "USB-Cハブ 7ポート",
         "price": 4980, "category": "周辺機器", "rating": 4.2},
        {"id": "PROD-004", "name": "ノイズキャンセリングヘッドフォン",
         "price": 29800, "category": "オーディオ", "rating": 4.7},
    ]

    # 検索（簡易版）
    results = [
        p for p in sample_products
        if query.lower() in p["name"].lower()
        or query.lower() in p["category"].lower()
    ]

    if category:
        results = [p for p in results if p["category"] == category]

    # 最大件数をStateから取得
    max_results = tool_context.state.get(
        StateKeys.APP_MAX_RESULTS, 5
    )
    results = results[:max_results]

    # 検索回数をカウント
    count = tool_context.state.get(StateKeys.TEMP_SEARCH_COUNT, 0)
    tool_context.state[StateKeys.TEMP_SEARCH_COUNT] = count + 1

    return {
        "query": query,
        "total_results": len(results),
        "results": results,
    }
