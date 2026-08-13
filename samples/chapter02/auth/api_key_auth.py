# api_key_auth.py
# 2-7-2. API Key認証（完全版）
# リクエストヘッダーにAPIキーを付与する最もシンプルな認証方式。
# APIキーは環境変数またはSecret Managerから取得し、コードに直書きしない。

import os

from google.adk.tools import FunctionTool


def call_weather_api(city: str) -> dict:
    """外部Weather APIを呼び出して天気情報を取得する。

    Args:
        city: 都市名

    Returns:
        天気情報"""
    import httpx

    # 環境変数からAPIキーを取得（コードに直書きしない）
    api_key = os.environ.get("WEATHER_API_KEY")
    if not api_key:
        return {"status": "error", "error": "Weather APIキーが設定されていません。"}

    response = httpx.get(
        "https://api.weather.example.com/v1/forecast",
        params={"city": city},
        headers={"Authorization": f"Bearer {api_key}"},
    )

    if response.status_code == 200:
        return response.json()
    else:
        return {"status": "error", "error": f"API呼び出しに失敗しました: {response.status_code}"}


weather_tool = FunctionTool(func=call_weather_api)

if __name__ == "__main__":
    # 定義の確認（実行には環境変数 WEATHER_API_KEY と実在するAPIエンドポイントが必要）
    print(f"ツール名: {weather_tool.name}")
