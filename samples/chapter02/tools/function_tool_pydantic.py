# function_tool_pydantic.py
# 2-6-2. FunctionTool: Pydanticモデルの活用（完全版）
# 複雑な入力を受け取る場合は、Pydanticモデルをパラメータの型に使用できる。

from pydantic import BaseModel, Field

from google.adk.tools import FunctionTool


class SearchCriteria(BaseModel):
    """検索条件"""
    city: str = Field(description="都市名")
    check_in: str = Field(description="チェックイン日（YYYY-MM-DD）")
    check_out: str = Field(description="チェックアウト日（YYYY-MM-DD）")
    guests: int = Field(default=1, description="宿泊人数")
    amenities: list[str] = Field(default=[], description="必要な設備（wifi, parking等）")


def search_hotels(criteria: SearchCriteria) -> list[dict]:
    """指定された条件でホテルを検索する。

    Args:
        criteria: 検索条件

    Returns:
        ホテル情報のリスト"""
    # 実際の実装ではホテル検索APIを呼び出す（紙面では「実装...」と省略）
    return []


# FunctionTool化（補完: 紙面には未掲載）
hotel_search_tool = FunctionTool(func=search_hotels)

if __name__ == "__main__":
    # ツール関数の動作確認
    criteria = SearchCriteria(city="京都", check_in="2026-04-15", check_out="2026-04-17")
    print(search_hotels(criteria=criteria))
