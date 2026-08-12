# samples/chapter04/rag_corpora.py
"""複数のRAGコーパスの使い分け例（4-6-3節）

情報の種類ごとにコーパスを分離し、name / description と
検索パラメータ（similarity_top_k / vector_distance_threshold）を
コーパスごとに最適化する。

必要な環境変数:
  GCP_PROJECT        : Google CloudプロジェクトID
  GCP_LOCATION       : リージョン（デフォルト: us-central1）
  PRODUCT_CORPUS_ID  : 製品ドキュメント用RAG CorpusのID
  FAQ_CORPUS_ID      : FAQ用RAG CorpusのID
  POLICY_CORPUS_ID   : ポリシー・規約用RAG CorpusのID
"""
import os

from google.adk import Agent
from google.adk.tools.retrieval import VertexAiRagRetrieval

# RAG Corpusのリソース名は環境変数から組み立てる
GCP_PROJECT = os.environ.get("GCP_PROJECT", "YOUR_PROJECT")
GCP_LOCATION = os.environ.get("GCP_LOCATION", "us-central1")
PRODUCT_CORPUS_ID = os.environ.get("PRODUCT_CORPUS_ID", "PRODUCT_CORPUS_ID")
FAQ_CORPUS_ID = os.environ.get("FAQ_CORPUS_ID", "FAQ_CORPUS_ID")
POLICY_CORPUS_ID = os.environ.get("POLICY_CORPUS_ID", "POLICY_CORPUS_ID")

# 製品ドキュメント用のRAGツール
product_docs = VertexAiRagRetrieval(
    name="product_docs",
    description="製品の仕様、機能、互換性情報を検索します。"
                "製品についての技術的な質問に回答する際に使用してください。",
    rag_corpora=[
        f"projects/{GCP_PROJECT}/locations/{GCP_LOCATION}"
        f"/ragCorpora/{PRODUCT_CORPUS_ID}",
    ],
    similarity_top_k=5,
    vector_distance_threshold=0.5,
)

# FAQコーパス用のRAGツール
faq_docs = VertexAiRagRetrieval(
    name="faq_docs",
    description="よくある質問と回答を検索します。"
                "一般的な問い合わせに対する標準的な回答を取得する際に使用してください。",
    rag_corpora=[
        f"projects/{GCP_PROJECT}/locations/{GCP_LOCATION}"
        f"/ragCorpora/{FAQ_CORPUS_ID}",
    ],
    similarity_top_k=3,
    vector_distance_threshold=0.4,  # FAQは精度重視
)

# ポリシー・規約コーパス用のRAGツール
policy_docs = VertexAiRagRetrieval(
    name="policy_docs",
    description="返品ポリシー、利用規約、保証規定を検索します。"
                "ポリシーや法的な質問に回答する際に使用してください。",
    rag_corpora=[
        f"projects/{GCP_PROJECT}/locations/{GCP_LOCATION}"
        f"/ragCorpora/{POLICY_CORPUS_ID}",
    ],
    similarity_top_k=3,
    vector_distance_threshold=0.3,  # 規約は高精度が必須
)

# エージェントに3つのRAGツールを装備
agent = Agent(
    name="support_agent",
    model="gemini-3.5-flash",
    instruction="""カスタマーサポートエージェントです。

    ## ツールの使い分け
    - 製品の仕様や技術的な質問 → product_docs
    - 一般的な問い合わせ → faq_docs
    - 返品・保証・規約に関する質問 → policy_docs

    回答には検索結果を根拠として使用してください。""",
    tools=[product_docs, faq_docs, policy_docs],
)


if __name__ == "__main__":
    # ツール構成の確認（API呼び出しは行わない）
    for tool in (product_docs, faq_docs, policy_docs):
        print(f"RAGツール: {tool.name}")
    print(f"エージェント: {agent.name}（ツール数: {len(agent.tools)}）")
