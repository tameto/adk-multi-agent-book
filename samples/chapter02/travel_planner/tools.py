"""第2章 ハンズオン: 旅行プランナー — 検索ツール群

観光スポット・レストラン・交通手段の検索ツールを定義する。
本番ではGoogle Places API / Maps API等を呼び出すが、
ハンズオンではダミーデータを返す。
"""


def search_spots(destination: str, preferences: str) -> dict:
    """観光スポットを検索する（ダミー実装）

    Args:
        destination: 旅行先の都市名（例: 京都、沖縄）
        preferences: 好みのジャンル（例: 歴史、自然、アート）

    Returns:
        観光スポットのリストを含む辞書
    """
    spots_db = {
        "京都": [
            {"name": "金閣寺", "genre": "歴史", "rating": 4.5, "duration_hours": 1.5},
            {"name": "嵐山竹林", "genre": "自然", "rating": 4.7, "duration_hours": 2.0},
            {"name": "伏見稲荷大社", "genre": "歴史", "rating": 4.8, "duration_hours": 2.0},
            {"name": "京都国立博物館", "genre": "アート", "rating": 4.3, "duration_hours": 2.5},
        ],
        "沖縄": [
            {"name": "美ら海水族館", "genre": "自然", "rating": 4.6, "duration_hours": 3.0},
            {"name": "首里城", "genre": "歴史", "rating": 4.4, "duration_hours": 1.5},
            {"name": "古宇利島", "genre": "自然", "rating": 4.7, "duration_hours": 3.0},
            {"name": "国際通り", "genre": "ショッピング", "rating": 4.2, "duration_hours": 2.0},
        ],
        "東京": [
            {"name": "浅草寺", "genre": "歴史", "rating": 4.5, "duration_hours": 1.5},
            {"name": "チームラボボーダレス", "genre": "アート", "rating": 4.6, "duration_hours": 2.5},
            {"name": "明治神宮", "genre": "歴史", "rating": 4.4, "duration_hours": 1.5},
            {"name": "新宿御苑", "genre": "自然", "rating": 4.3, "duration_hours": 2.0},
        ],
    }

    spots = spots_db.get(destination, [])

    # 好みでフィルタリング（部分一致）
    if preferences and spots:
        filtered = [s for s in spots if preferences in s["genre"]]
        if filtered:
            spots = filtered

    if not spots:
        return {
            "destination": destination,
            "error": f"{destination}の観光スポットデータは見つかりませんでした",
        }

    return {"destination": destination, "preferences": preferences, "spots": spots}


def search_restaurants(destination: str, cuisine: str) -> dict:
    """レストランを検索する（ダミー実装）

    Args:
        destination: 旅行先の都市名（例: 京都、沖縄）
        cuisine: 料理ジャンル（例: 和食、イタリアン、カフェ）

    Returns:
        レストランのリストを含む辞書
    """
    restaurants_db = {
        "京都": [
            {"name": "瓢亭", "cuisine": "和食", "price_range": "高級", "rating": 4.8},
            {"name": "イル・ギオットーネ", "cuisine": "イタリアン", "price_range": "中〜高", "rating": 4.5},
            {"name": "% ARABICA", "cuisine": "カフェ", "price_range": "手頃", "rating": 4.4},
            {"name": "祇園にしかわ", "cuisine": "和食", "price_range": "高級", "rating": 4.7},
        ],
        "沖縄": [
            {"name": "首里そば", "cuisine": "和食", "price_range": "手頃", "rating": 4.5},
            {"name": "ジャッキーステーキハウス", "cuisine": "洋食", "price_range": "中", "rating": 4.3},
            {"name": "浜辺の茶屋", "cuisine": "カフェ", "price_range": "手頃", "rating": 4.6},
            {"name": "琉球料理 美栄", "cuisine": "和食", "price_range": "中", "rating": 4.4},
        ],
        "東京": [
            {"name": "すきやばし次郎", "cuisine": "和食", "price_range": "高級", "rating": 4.9},
            {"name": "アフターヌーンティー", "cuisine": "カフェ", "price_range": "中", "rating": 4.2},
            {"name": "トラットリア・ダル・ビルバンテ", "cuisine": "イタリアン", "price_range": "中〜高", "rating": 4.5},
            {"name": "天ぷら近藤", "cuisine": "和食", "price_range": "高級", "rating": 4.7},
        ],
    }

    restaurants = restaurants_db.get(destination, [])

    # 料理ジャンルでフィルタリング
    if cuisine and restaurants:
        filtered = [r for r in restaurants if cuisine in r["cuisine"]]
        if filtered:
            restaurants = filtered

    if not restaurants:
        return {
            "destination": destination,
            "error": f"{destination}のレストランデータは見つかりませんでした",
        }

    return {"destination": destination, "cuisine": cuisine, "restaurants": restaurants}


def search_transport(origin: str, destination: str) -> dict:
    """交通手段を検索する（ダミー実装）

    Args:
        origin: 出発地（例: 東京、大阪）
        destination: 目的地（例: 京都、沖縄）

    Returns:
        利用可能な交通手段のリストを含む辞書
    """
    transport_db = {
        ("東京", "京都"): [
            {"mode": "新幹線", "duration": "2時間15分", "price_yen": 13320, "frequency": "約10分間隔"},
            {"mode": "飛行機", "duration": "1時間10分（+移動）", "price_yen": 15000, "frequency": "1日10便程度"},
            {"mode": "高速バス", "duration": "6〜7時間", "price_yen": 4000, "frequency": "1日数便"},
        ],
        ("東京", "沖縄"): [
            {"mode": "飛行機", "duration": "2時間45分", "price_yen": 25000, "frequency": "1日20便以上"},
        ],
        ("大阪", "京都"): [
            {"mode": "新幹線", "duration": "15分", "price_yen": 1450, "frequency": "約10分間隔"},
            {"mode": "JR新快速", "duration": "29分", "price_yen": 580, "frequency": "約15分間隔"},
            {"mode": "阪急電鉄", "duration": "43分", "price_yen": 410, "frequency": "約10分間隔"},
        ],
        ("大阪", "東京"): [
            {"mode": "新幹線", "duration": "2時間30分", "price_yen": 13870, "frequency": "約10分間隔"},
            {"mode": "飛行機", "duration": "1時間10分（+移動）", "price_yen": 12000, "frequency": "1日30便以上"},
            {"mode": "高速バス", "duration": "7〜8時間", "price_yen": 4500, "frequency": "1日数便"},
        ],
    }

    key = (origin, destination)
    transports = transport_db.get(key, [])

    if not transports:
        return {
            "origin": origin,
            "destination": destination,
            "error": f"{origin}→{destination}の交通データは見つかりませんでした",
        }

    return {"origin": origin, "destination": destination, "options": transports}
