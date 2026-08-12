# samples/chapter04/unified_context_callback.py
# 4-7-2. 検索戦略の統合パターン（パターン2: コールバック統合型）完全版
"""before_model_callbackでRAGとMemory Bankの情報を統合するサンプル

Memory Bankはcallback_context.search_memory()で明示的に検索し、
RAG側の補足情報（関連FAQ）と合わせてInstructionへ追加する。
"""
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse


# 補完: 紙面では未掲載のFAQ検索スタブ。
# 実運用ではVertex AI RAG EngineのAPI（rag.retrieval_query等）を直接呼び出して
# 話題に関連するFAQチャンクを取得する。
_FAQ_BY_TOPIC: dict[str, str] = {
    "返品": "Q. 返品期間は？ A. 商品到着後14日以内です。",
    "配送": "Q. 配送日数は？ A. 通常2〜4営業日でお届けします。",
}


async def search_faq_by_topic(topic: str) -> Optional[str]:
    """話題に関連するFAQを検索する（補完スタブ実装）"""
    return _FAQ_BY_TOPIC.get(topic)


async def inject_unified_context(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """RAGとMemoryの情報を統合してコンテキストに注入する"""
    # ユーザーの直近の話題に関連するFAQを先読みする
    recent_topic = callback_context.state.get("temp:current_topic")
    if recent_topic:
        sections: list[str] = []

        try:
            memory_response = await callback_context.search_memory(recent_topic)
        except ValueError:
            memory_response = None

        if memory_response and memory_response.memories:
            memory_lines = [
                part.text
                for entry in memory_response.memories[:3]
                for part in (entry.content.parts or [])
                if part.text
            ]
            if memory_lines:
                sections.append("[Memory Bank]\n" + "\n".join(memory_lines))

        # 話題に関連するFAQを事前に検索（RAG Engine APIを直接呼び出し）
        faq_context = await search_faq_by_topic(recent_topic)
        if faq_context:
            sections.append("[関連FAQ]\n" + faq_context)

        if sections:
            llm_request.append_instructions(["\n\n".join(sections)])

    return None
