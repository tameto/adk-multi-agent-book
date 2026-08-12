# function_tool_async.py
# 2-6-2. FunctionTool: 非同期ツール関数（完全版）
# I/Oバウンドな処理を含むツールはasync関数として定義できる。
# 他のツールと並列に実行される可能性があり、レイテンシ削減に寄与する。

import httpx

from google.adk.tools import FunctionTool


async def fetch_exchange_rate(
    base_currency: str,
    target_currency: str,
) -> dict:
    """為替レートを取得する。

    Args:
        base_currency: 基準通貨コード（例: JPY, USD, EUR）
        target_currency: 変換先通貨コード（例: USD, EUR, GBP）

    Returns:
        為替レート情報"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.exchange.example.com/rate",
            params={"base": base_currency, "target": target_currency},
        )
        if response.status_code == 200:
            data = response.json()
            return {
                "base": base_currency,
                "target": target_currency,
                "rate": data["rate"],
                "updated_at": data["updated_at"],
            }
        return {"status": "error", "error": "為替レート取得に失敗しました。"}


exchange_tool = FunctionTool(func=fetch_exchange_rate)

if __name__ == "__main__":
    # 定義の確認（URLはダミーのため、実行にはAPIエンドポイントの差し替えが必要）
    print(f"ツール名: {exchange_tool.name}")
