# samples/chapter03/context_propagation/state_scopes.py
"""3-2-7 Stateスコープの使い分け例（完全版）

エージェント間で共有すべき情報は user: スコープに、
エージェント固有の情報は session スコープに、
1回限りの中間結果は temp: スコープに格納する。
"""
from google.adk.sessions import Session


# Stateスコープの使い分け例
def setup_state(session: Session) -> None:
    """セッション開始時のState初期化"""
    # app スコープ: 全ユーザー共通設定
    session.state["app:company_name"] = "TechShop"
    session.state["app:support_hours"] = "9:00-18:00"

    # user スコープ: ユーザー固有情報（認証後に設定）
    session.state["user:name"] = "田中太郎"
    session.state["user:tier"] = "premium"
    session.state["user:order_count"] = 42

    # session スコープ: この対話固有のデータ
    session.state["current_topic"] = None
    session.state["escalation_requested"] = False

    # temp スコープ: 1回のInvocation内で破棄される
    session.state["temp:search_cache"] = {}
