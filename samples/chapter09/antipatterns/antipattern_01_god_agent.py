# samples/chapter09/antipatterns/antipattern_01_god_agent.py
"""アンチパターン1: God Agent（万能エージェント）の実装例（9-2-1 完全版）

1つのエージェントにすべての機能と責務を詰め込むアンチパターン（god_agent）と、
責務ごとに分割してルーターで振り分ける改善版（search_agent / order_agent /
support_agent / router）を対比する。
"""
from google.adk import Agent


# --- ツールのダミー実装（紙面では省略。実行確認用の最小実装） ---

def search_products(query: str) -> list[dict]:
    """商品を検索します（ダミー実装）"""
    return [{"id": 1, "name": "商品A"}]


def recommend_products(customer_id: str) -> list[dict]:
    """おすすめ商品を返します（ダミー実装）"""
    return [{"id": 2, "name": "商品B"}]


def create_order(customer_id: str, product_id: str, quantity: int) -> dict:
    """注文を作成します（ダミー実装）"""
    return {"status": "created"}


def update_order(order_id: str, quantity: int) -> dict:
    """注文を変更します（ダミー実装）"""
    return {"status": "updated"}


def cancel_order(order_id: str) -> dict:
    """注文をキャンセルします（ダミー実装）"""
    return {"status": "cancelled"}


def check_inventory(product_id: str) -> dict:
    """在庫を確認します（ダミー実装）"""
    return {"stock": 10}


def update_inventory(product_id: str, stock: int) -> dict:
    """在庫を更新します（ダミー実装）"""
    return {"status": "updated"}


def track_shipping(order_id: str) -> dict:
    """配送状況を追跡します（ダミー実装）"""
    return {"status": "in_transit"}


def get_shipping_estimate(order_id: str) -> dict:
    """配送予定日を返します（ダミー実装）"""
    return {"estimate": "2026-06-15"}


def search_faq(query: str) -> list[dict]:
    """FAQを検索します（ダミー実装）"""
    return [{"question": query, "answer": "回答例"}]


def answer_question(question: str) -> dict:
    """質問に回答します（ダミー実装）"""
    return {"answer": f"回答: {question}"}


def process_return(order_id: str, reason: str) -> dict:
    """返品を処理します（ダミー実装）"""
    return {"status": "accepted"}


def issue_refund(order_id: str) -> dict:
    """返金を実行します（ダミー実装）"""
    return {"status": "refunded"}


def collect_review(product_id: str, review: str) -> dict:
    """レビューを収集します（ダミー実装）"""
    return {"status": "collected"}


def analyze_reviews(product_id: str) -> dict:
    """レビューを分析します（ダミー実装）"""
    return {"sentiment": "positive"}


def generate_report(topic: str) -> dict:
    """レポートを生成します（ダミー実装）"""
    return {"report": f"レポート: {topic}"}


def export_csv(report_id: str) -> dict:
    """レポートをCSV出力します（ダミー実装）"""
    return {"file": "report.csv"}


def manage_user(user_id: str, action: str) -> dict:
    """ユーザーを管理します（ダミー実装）"""
    return {"status": "done"}


def reset_password(user_id: str) -> dict:
    """パスワードをリセットします（ダミー実装）"""
    return {"status": "reset"}


def process_payment(order_id: str, amount: int) -> dict:
    """決済を処理します（ダミー実装）"""
    return {"status": "paid"}


def verify_payment(payment_id: str) -> dict:
    """決済を検証します（ダミー実装）"""
    return {"status": "verified"}


# アンチパターン: God Agent
god_agent = Agent(
    name="god_agent",
    model="gemini-3.5-flash",  # 長いInstructionと大量ツールでコストが増える
    instruction="""あなたは万能アシスタントです。以下のすべてのタスクを処理してください:
    1. 商品検索と推薦
    2. 注文の作成・変更・キャンセル
    3. 在庫管理
    4. 配送状況の追跡
    5. カスタマーサポート（FAQ対応）
    6. 返品・返金処理
    7. レビューの収集と分析
    8. レポート生成
    9. ユーザー管理
    10. 決済処理
    ...""",
    tools=[
        search_products, recommend_products,
        create_order, update_order, cancel_order,
        check_inventory, update_inventory,
        track_shipping, get_shipping_estimate,
        search_faq, answer_question,
        process_return, issue_refund,
        collect_review, analyze_reviews,
        generate_report, export_csv,
        manage_user, reset_password,
        process_payment, verify_payment,
    ],  # 20個以上のツール
)

# 改善: 責務ごとに分割
search_agent = Agent(
    name="search_agent",
    model="gemini-3.5-flash",
    instruction="商品の検索と推薦を行います。",
    tools=[search_products, recommend_products],
)

order_agent = Agent(
    name="order_agent",
    model="gemini-3.5-flash",
    instruction="注文の作成・変更・キャンセルを処理します。",
    tools=[create_order, update_order, cancel_order],
)

support_agent = Agent(
    name="support_agent",
    model="gemini-3.5-flash",
    instruction="カスタマーサポートの問い合わせに回答します。",
    tools=[search_faq, answer_question, track_shipping],
)

# ルーターで振り分け
router = Agent(
    name="router",
    model="gemini-3.5-flash",
    instruction="""ユーザーのリクエストを対応するエージェントに振り分けます。
    - 商品の検索・推薦 → search_agent
    - 注文関連 → order_agent
    - 問い合わせ・サポート → support_agent""",
    sub_agents=[search_agent, order_agent, support_agent],
)
