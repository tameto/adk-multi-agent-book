# corpus_setup.py: RAGコーパスの初期セットアップ
"""Vertex AI RAG Engine のコーパスを作成し、ドキュメントを取り込むスクリプト（4-6-4節）。

RAGコーパスの作成とドキュメントのアップロードを1回だけ実行するセットアップ用途。
ハンズオン（4-7節）のStep 4は、このスクリプトでコーパスを準備してから
環境変数 RAG_CORPUS_ID を設定してエージェントを起動する前提。

RAG EngineはGA。preview配下ではなくGAの vertexai.rag モジュールを使う。

必要な環境変数:
  GCP_PROJECT              : Google CloudプロジェクトID（必須）
  GCP_LOCATION             : リージョン（デフォルト: us-central1）
  RAG_CORPUS_DISPLAY_NAME  : 作成するコーパスの表示名（デフォルト: product_documentation）
  RAG_IMPORT_PATHS         : 取り込むドキュメントのGCS URI（カンマ区切り、必須）
                             例: gs://your-bucket/docs/product_manual.pdf

実行例:
  export GCP_PROJECT="your-project-id"
  export RAG_IMPORT_PATHS="gs://your-bucket/docs/product_manual.pdf"
  python corpus_setup.py
"""
from __future__ import annotations

import os

import vertexai
from vertexai import rag  # RAG EngineはGA。preview配下ではなくGAのragモジュールを使う

# チャンク設定の既定値（4-6-4節「チャンク戦略の設計」参照）
DEFAULT_CHUNK_SIZE = 512     # チャンクサイズ（トークン数）。精度と文脈のバランスが良い
DEFAULT_CHUNK_OVERLAP = 100  # チャンク間のオーバーラップ（チャンクサイズの20〜30%が目安）


def create_corpus(display_name: str, description: str) -> rag.RagCorpus:
    """RAGコーパスを新規作成する。"""
    corpus = rag.create_corpus(
        display_name=display_name,
        description=description,
    )
    print(f"コーパスを作成しました: {corpus.name}")
    return corpus


def import_documents(
    corpus_name: str,
    paths: list[str],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> None:
    """指定したGCSパスのドキュメントをコーパスへ取り込む。

    チャンク設定は transformation_config に ChunkingConfig をネストして渡す
    （旧APIの chunk_size / chunk_overlap 直接指定は非推奨）。
    """
    rag.import_files(
        corpus_name=corpus_name,
        paths=paths,
        transformation_config=rag.TransformationConfig(
            rag.ChunkingConfig(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            ),
        ),
    )
    print(f"{len(paths)} 件のドキュメントを取り込みました: {corpus_name}")


def parse_import_paths(raw_paths: str) -> list[str]:
    """カンマ区切りのGCS URI文字列をリストへ分解する。"""
    return [path.strip() for path in raw_paths.split(",") if path.strip()]


def main() -> None:
    """環境変数を読み取り、コーパス作成とドキュメント取り込みを実行する。"""
    project = os.environ.get("GCP_PROJECT")
    if not project:
        raise ValueError("環境変数 GCP_PROJECT の設定が必要です")

    location = os.environ.get("GCP_LOCATION", "us-central1")
    display_name = os.environ.get(
        "RAG_CORPUS_DISPLAY_NAME", "product_documentation"
    )

    paths = parse_import_paths(os.environ.get("RAG_IMPORT_PATHS", ""))
    if not paths:
        raise ValueError(
            "環境変数 RAG_IMPORT_PATHS（取り込むドキュメントのGCS URI）の設定が必要です"
        )

    # Vertex AIの初期化
    vertexai.init(project=project, location=location)

    corpus = create_corpus(
        display_name=display_name,
        description="製品ドキュメントとFAQのコーパス",
    )
    import_documents(corpus_name=corpus.name, paths=paths)

    # 作成されたリソース名を RAG_CORPUS_ID としてエージェント起動時に渡す
    print(f"エージェントに設定する RAG_CORPUS_ID（リソース名）: {corpus.name}")


if __name__ == "__main__":
    main()
