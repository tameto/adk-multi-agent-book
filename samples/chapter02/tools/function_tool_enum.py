# function_tool_enum.py
# 2-6-2. FunctionTool: Enum型によるパラメータ制約（完全版）
# パラメータの取りうる値が限定されている場合、Enum型でLLMに選択肢を明示する。

from enum import Enum

from google.adk.tools import FunctionTool


class SortOrder(str, Enum):
    """ソート順"""
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    RATING_DESC = "rating_desc"
    DISTANCE_ASC = "distance_asc"


def search_with_sort(
    query: str,
    sort_by: SortOrder = SortOrder.RATING_DESC,
) -> list[dict]:
    """検索結果をソートして返す。

    Args:
        query: 検索キーワード
        sort_by: ソート順（price_asc: 安い順, price_desc: 高い順,
                 rating_desc: 評価順, distance_asc: 近い順）

    Returns:
        ソートされた検索結果"""
    # 実際の実装では検索APIを呼び出してソートする（紙面では「実装...」と省略）
    return []


sorted_search_tool = FunctionTool(func=search_with_sort)

if __name__ == "__main__":
    # ツール関数の動作確認
    print(search_with_sort(query="京都 ホテル", sort_by=SortOrder.PRICE_ASC))
