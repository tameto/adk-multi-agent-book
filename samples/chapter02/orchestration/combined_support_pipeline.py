# combined_support_pipeline.py
# 2-4-10. 実践: パターンの組み合わせ例（完全版）
# ECサイトのカスタマーサポートシステム。
# ParallelAgent（情報収集）→ LoopAgent（回答生成と品質レビュー）を
# SequentialAgentで接続する。
# Template Workflowとして利用できる。複雑な分岐や再開が必要な場合はWorkflow Runtimeを検討する。

from google.adk import Agent
from google.adk.agents import SequentialAgent, ParallelAgent, LoopAgent
from google.adk.tools import FunctionTool

# --- ここから補完: 紙面では省略されている検索ツールのダミー実装 ---


def search_orders(query: str) -> list[dict]:
    """注文IDまたは顧客情報から注文データを検索する（ダミー実装）。

    Args:
        query: 注文IDまたは顧客名等の検索キーワード

    Returns:
        注文情報のリスト"""
    return [{"order_id": "ORD-20260409-001", "status": "shipped", "query": query}]


def search_inquiry_history(customer_id: str) -> list[dict]:
    """顧客IDから過去の問い合わせ履歴を取得する（ダミー実装）。

    Args:
        customer_id: 顧客ID

    Returns:
        問い合わせ履歴のリスト"""
    return [{"customer_id": customer_id, "date": "2026-03-01", "topic": "配送遅延"}]


order_search_tool = FunctionTool(func=search_orders)
history_search_tool = FunctionTool(func=search_inquiry_history)

# --- ここまで補完 ---

# === レベル1: 情報収集（並列） ===
order_lookup = Agent(
    name="order_lookup",
    model="gemini-3.5-flash",
    description="注文情報を検索する",
    instruction="注文IDまたは顧客情報から注文データを検索してください。",
    tools=[order_search_tool],
    output_key="order_info",
)

customer_history = Agent(
    name="customer_history",
    model="gemini-3.5-flash",
    description="顧客の過去の問い合わせ履歴を取得する",
    instruction="顧客IDから過去の問い合わせ履歴を取得してください。",
    tools=[history_search_tool],
    output_key="customer_history",
)

info_gathering = ParallelAgent(
    name="info_gathering",
    sub_agents=[order_lookup, customer_history],
)

# === レベル2: 問題分析と回答生成（ループ） ===
draft_response = Agent(
    name="draft_response",
    model="gemini-3.5-flash",
    instruction="収集された情報に基づいて、顧客への回答ドラフトを作成してください。",
    output_key="response_draft",
)

quality_check = Agent(
    name="quality_check",
    model="gemini-3.5-flash",
    instruction="""回答ドラフトを以下の基準でレビューしてください:
- 事実関係が正確か
- 丁寧で共感的なトーンか
- 具体的なアクションが示されているか
品質が十分であればタスクを完了としてください。""",
    output_key="quality_result",
)

review_loop = LoopAgent(
    name="review_loop",
    sub_agents=[draft_response, quality_check],
    max_iterations=2,
)

# === レベル3: 全体パイプライン ===
root_agent = SequentialAgent(
    name="support_pipeline",
    sub_agents=[info_gathering, review_loop],
)

if __name__ == "__main__":
    # 定義内容の確認（対話実行は adk run / adk web を使用）
    print(f"全体パイプライン: {root_agent.name}")
    print(f"フェーズ: {[agent.name for agent in root_agent.sub_agents]}")
