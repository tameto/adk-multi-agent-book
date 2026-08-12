# samples/chapter03/review_analysis_example/tools.py
"""3-5-6 Step 4: 関数ツールの実装（完全版）

スキルが参照するツールは、エージェント側の関数ツールとして実装する。
スキルディレクトリ内には置かない。
紙面では support_agent/tools.py への追記として示しているが、
本リポジトリではEnd-to-End手順の例を独立ディレクトリにまとめている。
"""
from google.adk.tools import ToolContext


async def analyze_reviews(
    product_id: str,
    tool_context: ToolContext,
    period_days: int = 30,
) -> dict:
    """商品レビューを分析する"""
    reviews_db = tool_context.state.get("reviews_db", {})
    reviews = reviews_db.get(product_id, [])

    if not reviews:
        return {
            "product_id": product_id,
            "error": "レビューが見つかりませんでした",
        }

    positive_count = sum(1 for r in reviews if r.get("rating", 3) >= 4)
    sentiment_score = positive_count / len(reviews) if reviews else 0.5

    return {
        "product_id": product_id,
        "total_reviews": len(reviews),
        "period_days": period_days,
        "sentiment_score": round(sentiment_score, 2),
        "summary": f"直近{period_days}日間で{len(reviews)}件のレビュー。"
                   f"感情スコア: {sentiment_score:.2f}",
    }


async def get_review_trends(
    product_id: str,
    tool_context: ToolContext,
) -> dict:
    """レビューのトレンドを取得する"""
    reviews_db = tool_context.state.get("reviews_db", {})
    reviews = reviews_db.get(product_id, [])

    all_keywords = []
    for review in reviews:
        all_keywords.extend(review.get("keywords", []))

    keyword_counts = {}
    for kw in all_keywords:
        keyword_counts[kw] = keyword_counts.get(kw, 0) + 1

    top_keywords = sorted(
        keyword_counts.items(), key=lambda x: x[1], reverse=True
    )[:5]

    return {
        "product_id": product_id,
        "top_keywords": [{"keyword": k, "count": c} for k, c in top_keywords],
        "rating_trend": "stable",
    }
