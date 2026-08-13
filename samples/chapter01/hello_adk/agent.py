"""第1章 ハンズオン: 天気・観光情報エージェント（完全版）

adk create で生成される構造に準拠したエージェント定義。
get_weather と get_sightseeing の2つのツールを持ち、
天気と観光情報を組み合わせた提案ができる。

本文（第1章）では get_weather だけの最小構成から始め、
get_sightseeing を追加してエージェントを拡張する流れを解説している。
このファイルは、その拡張まで済ませた完全版に相当する。

実行方法:
    adk run hello_adk
    adk web .
"""

from google.adk import Agent


def get_weather(city: str) -> dict:
    """指定された都市の天気情報を返す（ダミー実装）

    Args:
        city: 天気を取得したい都市名（例: 東京、大阪、福岡、札幌）

    Returns:
        都市名・気温・天候・湿度を含む辞書
    """
    # ダミーの天気データ（本番ではOpenWeatherMap等のAPIを呼び出す）
    weather_data = {
        "東京": {"temperature": 22, "condition": "晴れ", "humidity": 45},
        "大阪": {"temperature": 24, "condition": "曇り", "humidity": 60},
        "福岡": {"temperature": 26, "condition": "晴れ", "humidity": 55},
        "札幌": {"temperature": 15, "condition": "雨", "humidity": 75},
    }

    if city in weather_data:
        data = weather_data[city]
        return {
            "status": "success",
            "city": city,
            "temperature": data["temperature"],
            "condition": data["condition"],
            "humidity": data["humidity"],
        }

    return {"status": "error", "message": f"{city}の天気情報は見つかりませんでした"}


def get_sightseeing(city: str) -> dict:
    """指定された都市の観光情報を返す（ダミー実装）

    Args:
        city: 観光情報を取得したい都市名（例: 東京、大阪、福岡、札幌）

    Returns:
        都市名・観光スポットのリスト・おすすめの季節を含む辞書
    """
    # ダミーの観光データ（本番では観光情報APIやRAGを利用する）
    sightseeing_data = {
        "東京": {
            "spots": ["浅草寺", "東京タワー", "明治神宮"],
            "recommended_season": "春（桜の季節）",
        },
        "大阪": {
            "spots": ["大阪城", "道頓堀", "通天閣"],
            "recommended_season": "秋（紅葉の季節）",
        },
        "福岡": {
            "spots": ["太宰府天満宮", "福岡タワー", "櫛田神社"],
            "recommended_season": "春（梅の季節）",
        },
        "札幌": {
            "spots": ["大通公園", "時計台", "藻岩山"],
            "recommended_season": "冬（雪まつりの季節）",
        },
    }

    if city in sightseeing_data:
        data = sightseeing_data[city]
        return {
            "status": "success",
            "city": city,
            "spots": data["spots"],
            "recommended_season": data["recommended_season"],
        }

    return {"status": "error", "message": f"{city}の観光情報は見つかりませんでした"}


# エージェント定義
root_agent = Agent(
    model="gemini-3.5-flash",
    name="weather_agent",
    instruction=(
        "ユーザーが指定した都市の天気と観光情報を教えてください。"
        "都市名が指定されていない場合は、どの都市について知りたいか確認してください。"
        "天気と観光情報を組み合わせて、具体的な提案ができる場合は提案してください。"
        "例: 晴れの日なら屋外の観光スポットを推薦する。"
    ),
    tools=[get_weather, get_sightseeing],
)
