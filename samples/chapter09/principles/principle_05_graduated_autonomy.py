# samples/chapter09/principles/principle_05_graduated_autonomy.py
"""原則5: 段階的自律性（Graduated Autonomy）の実装例（9-1-5 完全版）

before_tool_callbackとStateを組み合わせて、
自律レベル×ツールのリスクレベルに応じた承認フローを実装する。
"""
from enum import IntEnum
from typing import Optional

from google.adk import Agent
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext


# --- ツールのダミー実装（紙面では省略。実行確認用の最小実装） ---

def search_products(query: str) -> list[dict]:
    """商品を検索します（lowリスク・ダミー実装）"""
    return [{"id": 1, "name": "商品A", "price": 1000}]


def update_product_price(product_id: int, new_price: int) -> dict:
    """商品の価格を更新します（mediumリスク・ダミー実装）"""
    return {"status": "updated", "product_id": product_id, "new_price": new_price}


def create_order(customer_id: str, product_id: str, quantity: int) -> dict:
    """注文を作成します（mediumリスク・ダミー実装）"""
    return {"status": "created", "customer_id": customer_id}


def delete_product(product_id: int) -> dict:
    """商品を削除します（highリスク・ダミー実装）"""
    return {"status": "deleted", "product_id": product_id}


class AutonomyLevel(IntEnum):
    """自律レベルの定義"""
    FULL_HITL = 0       # すべてのアクションに人間の承認が必要
    SUPERVISED = 1      # 書き込み操作のみ承認が必要
    SEMI_AUTONOMOUS = 2 # 高リスク操作のみ承認が必要
    AUTONOMOUS = 3      # 完全自律（ログのみ記録）


# リスクレベルの定義
TOOL_RISK_LEVELS = {
    "search_products": "low",
    "get_order_status": "low",
    "update_product_price": "medium",
    "create_order": "medium",
    "delete_product": "high",
    "refund_order": "high",
    "modify_user_permissions": "critical",
}


def graduated_autonomy_callback(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
) -> Optional[dict]:
    """自律レベルに応じて承認を要求します"""
    # 現在の自律レベルを取得
    autonomy_level = AutonomyLevel(
        tool_context.state.get("autonomy_level", AutonomyLevel.FULL_HITL)
    )

    # ツールのリスクレベルを取得
    risk_level = TOOL_RISK_LEVELS.get(tool.name, "medium")

    # 自律レベルに基づいて承認要否を判定
    needs_approval = False

    if autonomy_level == AutonomyLevel.FULL_HITL:
        needs_approval = True
    elif autonomy_level == AutonomyLevel.SUPERVISED:
        needs_approval = risk_level in ("medium", "high", "critical")
    elif autonomy_level == AutonomyLevel.SEMI_AUTONOMOUS:
        needs_approval = risk_level in ("high", "critical")
    elif autonomy_level == AutonomyLevel.AUTONOMOUS:
        needs_approval = risk_level == "critical"

    if needs_approval:
        return {
            "action_required": "human_approval",
            "tool_name": tool.name,
            "tool_args": args,
            "risk_level": risk_level,
            "message": f"[承認待ち] {tool.name}（リスク: {risk_level}）の実行には承認が必要です。",
        }

    return None  # 承認不要 → 実行を続行


# 自律レベルを適用したエージェント
agent = Agent(
    name="graduated_agent",
    model="gemini-3.5-flash",
    instruction="商品管理と注文処理を行います。",
    tools=[search_products, update_product_price, create_order, delete_product],
    before_tool_callback=graduated_autonomy_callback,
)
