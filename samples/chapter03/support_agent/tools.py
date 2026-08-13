# samples/chapter03/support_agent/tools.py
"""カスタマーサポートエージェントのツール関数"""
from google.adk.tools import ToolContext
from google.genai import types


async def get_order_status(
    order_id: str,
    tool_context: ToolContext,
) -> dict:
    """注文の現在のステータスを取得する

    Args:
        order_id: 注文ID。"ORD-" で始まる英数字の文字列（例: ORD-12345）
        tool_context: ADKのToolContext

    Returns:
        注文情報を含む辞書
    """
    # サンプルデータ（実環境ではデータベースやAPIから取得）
    sample_orders = {
        "ORD-12345": {
            "id": "ORD-12345",
            "status": "配送中",
            "items": [
                {"name": "ワイヤレスマウス", "quantity": 1, "price": 3980},
                {"name": "USBハブ", "quantity": 1, "price": 2480},
            ],
            "total": 6460,
            "created_at": "2025-01-15",
            "estimated_delivery": "2025-01-18",
        },
        "ORD-12346": {
            "id": "ORD-12346",
            "status": "準備中",
            "items": [
                {"name": "メカニカルキーボード", "quantity": 1, "price": 12800},
            ],
            "total": 12800,
            "created_at": "2025-01-16",
            "estimated_delivery": "2025-01-20",
        },
    }

    order = sample_orders.get(order_id)
    if not order:
        return {"error": f"注文 {order_id} は見つかりませんでした。"}

    return order


async def cancel_order(
    order_id: str,
    reason: str,
    tool_context: ToolContext,
) -> dict:
    """注文をキャンセルする

    Args:
        order_id: 注文ID（例: ORD-12345）
        reason: キャンセル理由
        tool_context: ADKのToolContext

    Returns:
        キャンセル結果を含む辞書
    """
    # 注文ステータスの確認（実環境ではDBを参照）
    shipped_orders = ["ORD-12345"]

    if order_id in shipped_orders:
        return {
            "error": "発送済みの注文はキャンセルできません。"
                     "返品手続きをご案内します。"
        }

    # キャンセル処理の実行
    # Artifactとしてキャンセル記録を保存
    cancel_record = types.Part.from_text(
        text=f"キャンセル記録\n"
        f"注文ID: {order_id}\n"
        f"理由: {reason}\n"
    )
    version = await tool_context.save_artifact(
        f"cancel_{order_id}.txt", cancel_record
    )

    return {
        "order_id": order_id,
        "status": "cancelled",
        "message": f"注文 {order_id} のキャンセルを受け付けました。",
        "reason": reason,
        "artifact_version": version,
    }


async def search_products(
    query: str,
    tool_context: ToolContext,
    category: str = "",
    max_results: int = 10,
) -> dict:
    """商品を検索する

    Args:
        query: 検索クエリ
        tool_context: ADKのToolContext
        category: カテゴリによるフィルタ（オプション）
        max_results: 最大結果数（デフォルト: 10）

    Returns:
        検索結果を含む辞書
    """
    # サンプルデータ（実環境では検索エンジンやDBを使用）
    sample_products = [
        {"id": "PROD-001", "name": "ワイヤレスマウス", "price": 3980,
         "category": "周辺機器", "rating": 4.5, "stock": 150},
        {"id": "PROD-002", "name": "メカニカルキーボード", "price": 12800,
         "category": "周辺機器", "rating": 4.8, "stock": 30},
        {"id": "PROD-003", "name": "USB-Cハブ 7ポート", "price": 4980,
         "category": "周辺機器", "rating": 4.2, "stock": 200},
        {"id": "PROD-004", "name": "ノイズキャンセリングヘッドフォン", "price": 29800,
         "category": "オーディオ", "rating": 4.7, "stock": 45},
        {"id": "PROD-005", "name": "ウェブカメラ 4K", "price": 8980,
         "category": "周辺機器", "rating": 4.3, "stock": 80},
    ]

    # 簡易検索（実環境では全文検索エンジンを使用）
    results = [
        p for p in sample_products
        if query.lower() in p["name"].lower()
        or query.lower() in p["category"].lower()
    ]

    # カテゴリフィルタ
    if category:
        results = [p for p in results if p["category"] == category]

    # 結果数の制限
    results = results[:max_results]

    # 検索回数をStateに記録
    search_count = tool_context.state.get("search_count", 0)
    tool_context.state["search_count"] = search_count + 1

    return {
        "query": query,
        "total_results": len(results),
        "results": results,
    }


async def get_product_details(
    product_id: str,
    tool_context: ToolContext,
) -> dict:
    """商品IDを指定して詳細情報を取得する

    Args:
        product_id: 商品ID（例: PROD-001）
        tool_context: ADKのToolContext

    Returns:
        商品の詳細情報を含む辞書
    """
    # サンプルデータ（実環境ではDBやAPIから取得）
    products_db = {
        "PROD-001": {
            "id": "PROD-001",
            "name": "ワイヤレスマウス",
            "price": 3980,
            "category": "周辺機器",
            "description": "2.4GHz無線接続、静音クリック、バッテリー寿命12ヶ月",
            "stock": 150,
            "rating": 4.5,
            "reviews_count": 234,
        },
        "PROD-002": {
            "id": "PROD-002",
            "name": "メカニカルキーボード",
            "price": 12800,
            "category": "周辺機器",
            "description": "Cherry MX青軸、RGB LED、USB-C接続、日本語配列",
            "stock": 30,
            "rating": 4.8,
            "reviews_count": 89,
        },
        "PROD-003": {
            "id": "PROD-003",
            "name": "USB-Cハブ 7ポート",
            "price": 4980,
            "category": "周辺機器",
            "description": "USB-C x2、USB-A x3、HDMI、SD/microSDスロット",
            "stock": 200,
            "rating": 4.2,
            "reviews_count": 156,
        },
        "PROD-004": {
            "id": "PROD-004",
            "name": "ノイズキャンセリングヘッドフォン",
            "price": 29800,
            "category": "オーディオ",
            "description": "アクティブNC、Bluetooth 5.3、バッテリー30時間",
            "stock": 45,
            "rating": 4.7,
            "reviews_count": 312,
        },
        "PROD-005": {
            "id": "PROD-005",
            "name": "ウェブカメラ 4K",
            "price": 8980,
            "category": "周辺機器",
            "description": "4K 30fps、オートフォーカス、内蔵マイク、プライバシーカバー付き",
            "stock": 80,
            "rating": 4.3,
            "reviews_count": 67,
        },
    }

    product = products_db.get(product_id)
    if not product:
        return {"error": f"商品 {product_id} は見つかりませんでした。"}

    return product
