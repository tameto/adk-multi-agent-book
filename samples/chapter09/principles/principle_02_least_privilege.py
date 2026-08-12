# samples/chapter09/principles/principle_02_least_privilege.py
"""原則2: 最小権限（Least Privilege）の実装例（9-1-2 完全版）

エージェントごとにツールセットを明示的に指定し、
before_tool_callbackで実行時の権限チェックを行う。
"""
from typing import Optional

from google.adk import Agent
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext


# 読み取り専用ツール
def search_products(query: str) -> list[dict]:
    """商品を検索します（読み取り専用）"""
    # データベース検索ロジック（ダミー実装）
    return [{"id": 1, "name": "商品A", "price": 1000}]


# 書き込みツール（限定的に付与）
def update_product_price(product_id: int, new_price: int) -> dict:
    """商品の価格を更新します（書き込み権限が必要）"""
    # 価格更新ロジック（ダミー実装）
    return {"status": "updated", "product_id": product_id, "new_price": new_price}


# ツール実行前の権限チェック（実シグネチャ: BaseTool, dict, ToolContext）
def check_tool_permission(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
) -> Optional[dict]:
    """ツール実行前に権限をチェックします"""
    # 書き込み系ツールのリスト
    write_tools = {"update_product_price", "delete_product", "create_order"}

    if tool.name in write_tools:
        # ユーザーのロールを確認
        user_role = tool_context.state.get("user_role", "viewer")
        if user_role not in ("admin", "editor"):
            return {
                "error": f"権限不足: {tool.name}の実行にはadminまたはeditorロールが必要です。"
                f"現在のロール: {user_role}"
            }
    return None  # Noneを返すと通常通りツールが実行される


# 閲覧専用エージェント（検索のみ）
viewer_agent = Agent(
    name="viewer_agent",
    model="gemini-3.5-flash",
    instruction="商品情報を検索して回答します。商品の変更はできません。",
    tools=[search_products],  # 読み取り専用ツールのみ
)

# 管理者エージェント（検索＋更新、コールバックで二重チェック）
admin_agent = Agent(
    name="admin_agent",
    model="gemini-3.5-flash",
    instruction="商品情報の検索と価格の更新を行います。",
    tools=[search_products, update_product_price],
    before_tool_callback=check_tool_permission,
)
