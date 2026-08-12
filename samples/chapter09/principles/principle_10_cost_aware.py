# samples/chapter09/principles/principle_10_cost_aware.py
"""原則10: コスト意識（Cost-Aware Design）の実装例（9-1-10 完全版）

コスト最適化を3つのレイヤーで実装する。
- レイヤー1: タスクに応じた責務分離とモデル設定
- レイヤー2: キャッシュによるLLM呼び出しの削減
- レイヤー3: コスト監視とアラート
"""
import logging
import os

from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse

logger = logging.getLogger(__name__)


# --- 外部サービスのダミー実装（紙面では省略。実行確認用の最小実装） ---

class _DummyCache:
    """インメモリキャッシュのダミー実装。本番ではRedis等に置き換える"""

    def __init__(self) -> None:
        self._store: dict[str, object] = {}

    def get(self, key: str) -> object | None:
        return self._store.get(key)

    def set(self, key: str, value: object, ttl: int = 3600) -> None:
        self._store[key] = value


class _DummySearchEngine:
    """検索エンジンのダミー実装"""

    def search(self, query: str) -> list[dict]:
        return [{"result": f"{query} の検索結果"}]


cache = _DummyCache()
search_engine = _DummySearchEngine()


# レイヤー1: タスクに応じた責務分離とモデル設定

# 簡単なルーティング → 同じメインモデルを短いInstructionで低レイテンシ運用
router_agent = Agent(
    name="router",
    model="gemini-3.5-flash",
    instruction="""ユーザーのリクエストを分類し、対応するエージェントに振り分けます。
    カテゴリ: search（検索）、order（注文）、support（サポート）""",
)

# 複雑な推論 → 同じメインモデルで深い分析用のInstructionを分離
analysis_agent = Agent(
    name="analyzer",
    model="gemini-3.5-flash",
    instruction="""複雑なデータ分析と意思決定支援を行います。
    多角的な視点から分析し、根拠とともに推奨事項を提示します。""",
)


# レイヤー2: キャッシュによるLLM呼び出しの削減

def cached_search(query: str) -> dict:
    """キャッシュ付き検索ツール"""
    # キャッシュキーの生成
    cache_key = f"search:{query.lower().strip()}"

    # キャッシュヒット
    cached_result = cache.get(cache_key)
    if cached_result:
        return {"source": "cache", "results": cached_result}

    # キャッシュミス → 実際に検索
    results = search_engine.search(query)
    cache.set(cache_key, results, ttl=3600)  # 1時間キャッシュ
    return {"source": "live", "results": results}


# レイヤー3: コスト監視とアラート

def _price_from_env(name: str) -> float:
    """公式PricingのUSD/1K tokens換算値を環境変数から取得する"""
    value = os.environ.get(name)
    return float(value) if value else 0.0


# モデル別の料金テーブル。実運用では公式PricingのUSD/1M tokensを
# USD/1K tokensへ換算し、環境変数から注入する。
MODEL_PRICING_PER_1K = {
    "gemini-3.5-flash": {
        "input": _price_from_env("GEMINI_3_5_FLASH_INPUT_PER_1K"),
        "input_over_200k": _price_from_env(
            "GEMINI_3_5_FLASH_INPUT_OVER_200K_PER_1K"
        ),
        "output": _price_from_env("GEMINI_3_5_FLASH_OUTPUT_PER_1K"),
        "output_over_200k": _price_from_env(
            "GEMINI_3_5_FLASH_OUTPUT_OVER_200K_PER_1K"
        ),
    },
}
DEFAULT_PRICING_MODEL = "gemini-3.5-flash"


def _unit_price(pricing: dict[str, float], token_type: str, input_tokens: int) -> float:
    """入力長200K超のティアがあるモデルでは高い単価を返します。"""
    if input_tokens > 200_000:
        return pricing.get(f"{token_type}_over_200k", pricing[token_type])
    return pricing[token_type]


def cost_monitoring_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
):
    """LLM応答後にコストを計算し、閾値を超えたらアラートを発行します"""
    usage = llm_response.usage_metadata
    if usage:
        # モデル別単価を取得（Stateにモデル名がなければデフォルト単価を使用）
        model_name = callback_context.state.get("model_name", DEFAULT_PRICING_MODEL)
        pricing = MODEL_PRICING_PER_1K.get(
            model_name, MODEL_PRICING_PER_1K[DEFAULT_PRICING_MODEL]
        )

        # セッションの累計コストを計算（単価はUSD/1Kトークン）
        input_tokens = usage.prompt_token_count or 0
        output_tokens = usage.candidates_token_count or 0
        input_unit_price = _unit_price(pricing, "input", input_tokens)
        output_unit_price = _unit_price(pricing, "output", input_tokens)
        if input_unit_price <= 0 or output_unit_price <= 0:
            logger.info(
                "モデル単価が未設定のためコスト計算をスキップ",
                extra={"model_name": model_name},
            )
            return None

        input_cost = input_tokens / 1000 * input_unit_price
        output_cost = output_tokens / 1000 * output_unit_price
        session_cost = callback_context.state.get("_session_cost", 0.0)
        session_cost += input_cost + output_cost
        callback_context.state["_session_cost"] = session_cost

        # コスト閾値チェック
        cost_limit = callback_context.state.get("cost_limit_usd", 1.0)
        if session_cost > cost_limit:
            logger.warning(
                "コスト閾値超過",
                extra={
                    "session_cost": session_cost,
                    "cost_limit": cost_limit,
                    "agent_name": callback_context.agent_name,
                },
            )
    return None
