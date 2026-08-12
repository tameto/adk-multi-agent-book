# samples/chapter04/knowledge_memory_integration.py
"""静的知識（RAG）と動的記憶（Memory Bank）の統合構成例（4-7-1節）

RAG Engineに静的知識（製品ドキュメント・ポリシー）を置き、
Memory Bankにユーザー固有の動的記憶を置く分離設計を、
Runnerで1つの構成に統合する。

必要な環境変数:
  GCP_PROJECT        : Google CloudプロジェクトID
  GCP_LOCATION       : リージョン（デフォルト: us-central1）
  AGENT_ENGINE_ID    : Memory Bankを紐づけるAgent EngineのID
  PRODUCT_CORPUS_ID  : 製品ドキュメント用RAG CorpusのID
  POLICY_CORPUS_ID   : ポリシー・規約用RAG CorpusのID
"""
import os

from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.memory import VertexAiMemoryBankService
from google.adk.runners import Runner
from google.adk.sessions import VertexAiSessionService
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.tools.retrieval import VertexAiRagRetrieval

# プロジェクト情報とRAG CorpusのIDは環境変数から取得する
GCP_PROJECT = os.environ.get("GCP_PROJECT", "YOUR_PROJECT_ID")
GCP_LOCATION = os.environ.get("GCP_LOCATION", "us-central1")
AGENT_ENGINE_ID = os.environ.get("AGENT_ENGINE_ID", "YOUR_AGENT_ENGINE_ID")
PRODUCT_CORPUS_ID = os.environ.get("PRODUCT_CORPUS_ID", "PRODUCT_CORPUS_ID")
POLICY_CORPUS_ID = os.environ.get("POLICY_CORPUS_ID", "POLICY_CORPUS_ID")

# RAGツール: 静的知識の検索
product_docs = VertexAiRagRetrieval(
    name="product_docs",
    description="製品ドキュメント、FAQ、利用規約を検索します。"
                "製品の仕様や手続きについての質問に回答する際に使用してください。",
    rag_corpora=[
        f"projects/{GCP_PROJECT}/locations/{GCP_LOCATION}"
        f"/ragCorpora/{PRODUCT_CORPUS_ID}",
    ],
    similarity_top_k=5,
    vector_distance_threshold=0.5,
)

policy_docs = VertexAiRagRetrieval(
    name="policy_docs",
    description="返品ポリシー、配送規定、保証規定を検索します。"
                "ポリシーや規定に関する質問に回答する際に使用してください。",
    rag_corpora=[
        f"projects/{GCP_PROJECT}/locations/{GCP_LOCATION}"
        f"/ragCorpora/{POLICY_CORPUS_ID}",
    ],
    similarity_top_k=3,
    vector_distance_threshold=0.3,  # 規約は高精度が必須
)

async def save_session_to_memory(callback_context: CallbackContext) -> None:
    """対話後に現在のSessionをMemory Bankへ取り込む"""
    await callback_context.add_session_to_memory()


# エージェントの定義: RAGツールとMemory検索ツールを装備
agent = Agent(
    name="support_agent",
    model="gemini-3.5-flash",
    instruction="""カスタマーサポートエージェントです。

    ## 情報の使い分け
    - 製品の仕様や手続きに関する質問: product_docs を検索してください
    - ポリシーや規定に関する質問: policy_docs を検索してください
    - ユーザーの過去の問い合わせや嗜好: Memory Bankから先読みされた記憶を参照してください

    ## 回答ルール
    - 検索結果に基づいて回答してください
    - 情報が見つからない場合は、正直にその旨を伝えてください
    - ユーザーの過去のやり取りを踏まえて、パーソナライズした応答を心がけてください""",
    tools=[product_docs, policy_docs, PreloadMemoryTool()],
    after_agent_callback=save_session_to_memory,
)

# Memory Bank: 動的記憶の管理
memory_service = VertexAiMemoryBankService(
    project=GCP_PROJECT,
    location=GCP_LOCATION,
    agent_engine_id=AGENT_ENGINE_ID,
)

# SessionService: Session管理
session_service = VertexAiSessionService(
    project=GCP_PROJECT,
    location=GCP_LOCATION,
    agent_engine_id=AGENT_ENGINE_ID,
)

# Runnerで統合（Compactionなしの構成例。本番ではApp経由で有効化する。4-4節参照）
runner = Runner(
    agent=agent,
    app_name="customer_support",
    session_service=session_service,
    memory_service=memory_service,  # Memory BankをRunnerへ接続
)


if __name__ == "__main__":
    # 構成の確認（API呼び出しは行わない）
    print(f"エージェント: {agent.name}")
    print(f"RAGツール: {[tool.name for tool in agent.tools]}")
    print(f"SessionService: {type(session_service).__name__}")
    print(f"MemoryService: {type(memory_service).__name__}")
