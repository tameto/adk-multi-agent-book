# tool_best_practices.py
# 2-6-7. ツール設計のベストプラクティス（完全版）
# 1. docstringはLLMへの説明書
# 2. エラーハンドリングは辞書で返す
# 3. 冪等性を確保する
# 4. 1つのツールは1つの責務
# 5. ツール数の目安は10個以下（本文参照）
# 6. 戻り値は一貫した構造にする
# 7. 副作用を持つツールには確認メッセージを含める

from dataclasses import dataclass

# --- ここから補完: 紙面では前提とされているダミーのデータベース・API実装 ---


class OrderNotFoundError(Exception):
    """注文が見つからない場合の例外（ダミー定義）"""


class DatabaseError(Exception):
    """データベース障害を表す例外（ダミー定義）"""


@dataclass
class Order:
    """注文レコード（ダミー定義）"""
    order_id: str
    status: str = "confirmed"
    delivery_date: str = "2026-04-20"


@dataclass
class User:
    """ユーザーレコード（ダミー定義）"""
    user_id: str
    name: str = "山田太郎"


class DummyDatabase:
    """インメモリのダミーデータベース"""

    def get_order(self, order_id: str) -> Order:
        """注文を取得する。存在しない場合はOrderNotFoundErrorを送出する"""
        if not order_id.startswith("ORD-"):
            raise OrderNotFoundError(order_id)
        return Order(order_id=order_id)

    def cancel_order(self, order_id: str) -> None:
        """注文をキャンセル状態に更新する"""

    def get_user(self, user_id: str) -> User | None:
        """ユーザーを取得する。存在しない場合はNoneを返す"""
        return User(user_id=user_id)

    def delete_user(self, user_id: str) -> None:
        """ユーザーを削除する"""


class DummySearchApi:
    """ダミーの検索API"""

    def search(self, **kwargs) -> list[dict]:
        """検索を実行する"""
        return []


database = DummyDatabase()
api = DummySearchApi()

# --- ここまで補完 ---


# === 1. docstringはLLMへの説明書 ===

# 良い例: 具体的で、使い方が明確
def search_restaurants(
    area: str,
    cuisine: str,
    budget_max: int,
) -> list[dict]:
    """指定エリア・ジャンル・予算でレストランを検索する。

    Args:
        area: 検索エリア（例: 京都駅周辺、嵐山、祇園）
        cuisine: 料理ジャンル（例: 和食、イタリアン、フレンチ、中華）
        budget_max: 1人あたりの予算上限（円）（例: 3000、5000、10000）

    Returns:
        レストラン情報のリスト。各レストランはname, address, rating, price_rangeを含む"""
    # 実際の実装ではレストラン検索APIを呼び出す
    return api.search(area=area, cuisine=cuisine, budget_max=budget_max)


# 悪い例: 曖昧で、LLMが正しく使えない
def search(q: str) -> list:
    """検索する"""
    ...


# === 2. エラーハンドリングは辞書で返す ===

def get_order_status(order_id: str) -> dict:
    """注文のステータスを取得する。

    Args:
        order_id: 注文ID（例: ORD-20260409-001）

    Returns:
        注文ステータス情報"""
    try:
        order = database.get_order(order_id)
        return {
            "status": "success",
            "order_id": order_id,
            "order_status": order.status,
            "estimated_delivery": order.delivery_date,
        }
    except OrderNotFoundError:
        return {
            "status": "error",
            "error": f"注文ID '{order_id}' が見つかりません。注文IDを確認してください。",
        }
    except DatabaseError:
        return {
            "status": "error",
            "error": "データベースに一時的な問題が発生しています。しばらくしてからお試しください。",
        }


# === 3. 冪等性を確保する ===

# 良い例: 同じ入力に対して同じ結果を返す（冪等）
def cancel_order(order_id: str) -> dict:
    """注文をキャンセルする。

    Args:
        order_id: キャンセルする注文ID

    Returns:
        キャンセル結果"""
    order = database.get_order(order_id)

    if order.status == "cancelled":
        # 既にキャンセル済み → 成功として返す（冪等性）
        return {"status": "success", "message": "この注文は既にキャンセル済みです。"}

    if order.status in ("shipped", "delivered"):
        return {"status": "error", "message": "発送済みの注文はキャンセルできません。"}

    database.cancel_order(order_id)
    return {"status": "success", "message": "注文をキャンセルしました。"}


# === 4. 1つのツールは1つの責務 ===

# 良い例: 責務が明確に分離
def search_flights(departure: str, arrival: str, date: str) -> list[dict]:
    """航空券を検索する。"""
    # 実際の実装では航空券検索APIを呼び出す
    return api.search(departure=departure, arrival=arrival, date=date)


def book_flight(flight_id: str, passenger_name: str) -> dict:
    """航空券を予約する。"""
    # 実際の実装では予約APIを呼び出す
    return {"status": "success", "flight_id": flight_id, "passenger": passenger_name}


# 悪い例: 1つのツールに複数の責務
def handle_flight(action: str, **kwargs) -> dict:
    """航空券の検索・予約・キャンセルを行う。"""
    if action == "search": ...
    elif action == "book": ...
    elif action == "cancel": ...
    return {}


# === 6. 戻り値は一貫した構造にする ===

# 良い例: 全てのツールが同じ構造のレスポンスを返す
# （紙面ではパラメータを (...) と省略。以下は補完したシグネチャ）
def search_hotels(city: str, check_in: str, check_out: str) -> dict:
    """ホテルを検索する。

    Args:
        city: 都市名
        check_in: チェックイン日（YYYY-MM-DD形式）
        check_out: チェックアウト日（YYYY-MM-DD形式）

    Returns:
        statusフィールドを持つ検索結果"""
    try:
        results = api.search(city=city, check_in=check_in, check_out=check_out)
        return {
            "status": "success",
            "count": len(results),
            "results": results,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


# === 7. 副作用を持つツールには確認メッセージを含める ===

def delete_account(user_id: str) -> dict:
    """ユーザーアカウントを削除する。

    Args:
        user_id: 削除するユーザーのID

    Returns:
        削除結果
    """
    # 実際の削除前に確認情報を返す
    user = database.get_user(user_id)
    if not user:
        return {"status": "error", "error": "ユーザーが見つかりません。"}

    database.delete_user(user_id)
    return {
        "status": "success",
        "message": f"ユーザー '{user.name}'（ID: {user_id}）のアカウントを削除しました。",
        "warning": "この操作は元に戻せません。",
    }


if __name__ == "__main__":
    # ツール関数の動作確認
    print(get_order_status(order_id="ORD-20260409-001"))
    print(get_order_status(order_id="INVALID-ID"))
    print(cancel_order(order_id="ORD-20260409-001"))
    print(search_hotels(city="京都", check_in="2026-04-15", check_out="2026-04-17"))
