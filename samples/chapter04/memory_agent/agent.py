# samples/chapter04/memory_agent/agent.py
"""Memory Engineering対応のカスタマーサポートエージェント"""
import os
from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.models import Gemini
from google.adk.tools.retrieval import VertexAiRagRetrieval
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.runners import Runner

from .session_config import create_session_service, create_memory_service
from .state_keys import StateKeys, get_user_tier
from .tools import search_products, get_order_status


def build_instruction(ctx: ReadonlyContext) -> str:
    """ユーザーの会員ティアに応じた動的Instructionを生成する"""
    user_name = ctx.state.get(StateKeys.USER_NAME, "ゲスト")
    user_tier = get_user_tier(ctx.state)

    tier_policies = {
        "premium": """## プレミアム会員対応
- 最優先で対応してください
- 特別割引（最大20%）の案内が可能です
- 返品期限を30日間に延長できます""",
        "standard": """## スタンダード会員対応
- 通常の対応手順に従ってください
- 標準的な返品・交換ポリシーを適用します""",
        "free": """## 無料会員対応
- 基本的な問い合わせのみ対応します
- 会員登録の案内を行ってください""",
    }

    policy = tier_policies.get(user_tier, tier_policies["free"])

    return f"""カスタマーサポートエージェントです。

## Current Context
- ユーザー: {user_name}（{user_tier}会員）

{policy}

## 情報の使い分け
- 製品の仕様に関する質問: product_docs ツールで検索してください
- 過去の対話で学んだユーザー情報: Memory Bankから先読みされた記憶を参照してください

## 記憶に関する指針
- ユーザーの製品の使用状況、技術レベル、嗜好を覚えてください
- 一時的な話題は記憶する必要はありません

## 共通ルール
- 個人情報（パスワード、クレジットカード番号等）は聞き出さないでください
- 確認できた事実のみを伝えてください
- 日本語で回答してください"""


async def save_session_to_memory(callback_context: CallbackContext) -> None:
    """MemoryServiceが有効な場合、現在のSessionをMemoryへ取り込む"""
    try:
        await callback_context.add_session_to_memory()
    except ValueError:
        # memory_service=None の開発実行では保存処理だけをスキップする
        return


# --- RAG / Memory ツールの設定（環境変数で制御） ---
tools_list = [search_products, get_order_status, PreloadMemoryTool()]

rag_corpus_id = os.environ.get("RAG_CORPUS_ID")
if rag_corpus_id:
    product_docs = VertexAiRagRetrieval(
        name="product_docs",
        description="製品ドキュメント、仕様書、FAQを検索します。"
                    "製品についての質問に回答する際に使用してください。",
        rag_corpora=[
            f"projects/{os.environ.get('GCP_PROJECT', '')}"
            f"/locations/{os.environ.get('GCP_LOCATION', 'us-central1')}"
            f"/ragCorpora/{rag_corpus_id}"
        ],
        similarity_top_k=5,
        vector_distance_threshold=0.5,
    )
    tools_list.append(product_docs)


# --- エージェントの定義 ---
root_agent = Agent(
    name="support_agent",
    model="gemini-3.5-flash",
    instruction=build_instruction,
    tools=tools_list,
    after_agent_callback=save_session_to_memory,
)


# --- App + Compactionの構成（公式API: App クラス経由） ---
# Compactionは Agent 直下ではなく App クラスの events_compaction_config で設定する
app = App(
    name="customer_support",
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=20,   # 20 invocation ごとにCompactionを実行
        overlap_size=2,           # 直前の2 invocationを要約に含めて保持
        summarizer=LlmEventSummarizer(
            llm=Gemini(model="gemini-3.5-flash"),
        ),
    ),
)


def create_runner() -> Runner:
    """プログラムから直接実行する場合のRunnerを生成する。

    adk run / adk web はこのグローバル関数ではなく、公開された app を読み込み、
    CLIオプションからSession/Artifact/Memoryサービスを構成する。
    """
    return Runner(
        app=app,
        session_service=create_session_service(),
        memory_service=create_memory_service(),
    )
