# conditional_routing.py
# 2-4-7. 条件分岐: コールバックによる動的ルーティング（完全版）
# コールバックの戻り値で実行フローを制御する。
# - Noneを返す: 通常のフローが続行される
# - LlmResponseを返す: LLM呼び出し（before）/出力（after）が上書きされる

from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai.types import Content, Part


def route_by_language(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> LlmResponse | None:
    """ユーザーの言語に基づいてルーティングする（before_model_callback）

    ADK v2.2.0 はコールバックを callback_context=... のキーワード引数で
    呼び出すため、第1引数名は callback_context に合わせる。
    """
    user_message = callback_context.user_content.parts[0].text

    # 簡易的な言語判定
    if any(ord(c) > 0x3000 for c in user_message):
        # 日本語の場合: 日本語対応instructionを追加
        callback_context.state["detected_language"] = "ja"
    else:
        callback_context.state["detected_language"] = "en"

    # Noneを返すと通常のLLM呼び出しが続行される
    return None


def check_safety(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> LlmResponse | None:
    """LLMの出力を安全性チェックする（after_model_callback）"""
    response_text = llm_response.content.parts[0].text

    # 安全でない内容が含まれている場合、代替レスポンスを返す
    blocked_words = ["機密", "パスワード", "シークレット"]
    if any(word in response_text for word in blocked_words):
        return LlmResponse(
            content=Content(
                role="model",
                parts=[Part(text="申し訳ございません。セキュリティ上の理由により、その情報は提供できません。")],
            )
        )

    # Noneを返すと元のレスポンスがそのまま返される
    return None


def cache_hit_check(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> LlmResponse | None:
    """キャッシュにヒットした場合、LLM呼び出しをスキップする"""
    cache_key = callback_context.user_content.parts[0].text
    cached = callback_context.state.get(f"cache:{cache_key}")

    if cached:
        # キャッシュヒット: LLMを呼ばずに返す
        return LlmResponse(
            content=Content(role="model", parts=[Part(text=cached)])
        )

    # キャッシュミス: 通常のLLM呼び出しを続行
    return None


agent = Agent(
    name="safe_agent",
    model="gemini-3.5-flash",
    instruction="ユーザーの質問に回答してください。",
    before_model_callback=route_by_language,
    after_model_callback=check_safety,
)

# adk run / adk web から参照できるようroot_agentとして公開する（補完）
root_agent = agent

if __name__ == "__main__":
    # 定義内容の確認（対話実行は adk run / adk web を使用）
    print(f"エージェント: {agent.name}")
    print("コールバック: before=route_by_language / after=check_safety")
