# function_tool_optional_params.py
# 2-6-2. FunctionTool: Optional型の活用（完全版）
# Optional型のパラメータはJSON Schemaのrequiredに含まれない。
# LLMはユーザーが明示的に条件を指定した場合にのみ、そのパラメータを渡す。

from typing import Optional

from google.adk.tools import FunctionTool


def search_hotels(
    city: str,
    check_in: str,
    check_out: str,
    max_price: Optional[int] = None,
    min_rating: Optional[float] = None,
) -> list[dict]:
    """ホテルを検索する。

    Args:
        city: 検索する都市名
        check_in: チェックイン日（YYYY-MM-DD形式）
        check_out: チェックアウト日（YYYY-MM-DD形式）
        max_price: 1泊あたりの上限価格（円）。省略時は制限なし
        min_rating: 最低評価（1.0〜5.0）。省略時は制限なし

    Returns:
        ホテル情報のリスト"""
    # 実際の実装ではホテル検索APIを呼び出す（紙面では「実装...」と省略）
    return []


# FunctionTool化（補完: 紙面には未掲載）
hotel_search_tool = FunctionTool(func=search_hotels)

if __name__ == "__main__":
    # ツール関数の動作確認
    print(search_hotels(city="京都", check_in="2026-04-15", check_out="2026-04-17", max_price=15000))
