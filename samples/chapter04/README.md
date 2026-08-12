# 第4章 Session・Memory・RAG

会話の状態をどこに置き、どこまで残すかを設計するためのサンプルです。SessionServiceの3実装（InMemory／Database／VertexAi）、Stateキーの一元管理、Compaction、Vertex AI Memory Bank、Vertex AI RAG Engineを収録しています。ハンズオンの成果物は`memory_agent/`で、会員ティアに応じた動的Instructionと20 invocationごとのCompactionを組み込んだカスタマーサポートエージェントです。

## 収録内容

| ディレクトリ／ファイル | 内容 |
|---|---|
| `memory_agent/agent.py` | ハンズオン成果物。Compaction・RAG・PreloadMemoryToolを統合した`App`定義 |
| `memory_agent/session_config.py` | 環境変数に応じたSessionService／MemoryServiceの生成 |
| `memory_agent/state_keys.py` | Stateキーの定数定義と型安全なアクセサ |
| `memory_agent/tools.py` | 商品検索・注文照会のツール関数 |
| `session_db_config.py` | DatabaseSessionServiceの接続設定（Cloud SQL Auth Proxy経由を含む） |
| `corpus_setup.py` | Vertex AI RAG Engineのコーパス作成とドキュメント取り込み |
| `rag_corpora.py` | 複数コーパスの使い分けと検索パラメータの調整 |
| `knowledge_memory_integration.py` | 静的知識（RAG）と動的記憶（Memory Bank）を分離して統合する構成 |
| `unified_context_callback.py` | before_model_callbackでRAGとMemory Bankの結果を統合する |
| `tests/` | Stateキー・SessionService設定・import副作用のテスト（GCP接続不要） |
| `pytest.ini` | asyncフィクスチャを紙面どおりに書くための`asyncio_mode = auto` |

## セットアップ

```bash
cd samples/chapter04
pip install -r requirements.txt

cd memory_agent
cp .env.example .env
```

`requirements.txt`はADKの`db,gcp` extrasに加えて、RAG EngineとMemory Bank用の`google-cloud-aiplatform`、DatabaseSessionService用のドライバ（`asyncpg`／`aiosqlite`／`greenlet`）を含みます。

## 実行

インメモリのMemory Serviceで動かす場合は次のとおりです。Google Cloudプロジェクトは不要です。

```bash
cd samples/chapter04
adk run memory_agent --memory_service_uri="memory://"
```

Vertex AI Memory Bankに接続する場合は、Agent Engineのリソース名を指定します。

```bash
adk run memory_agent \
  --memory_service_uri="agentengine://projects/YOUR_PROJECT_ID/locations/us-central1/reasoningEngines/REASONING_ENGINE_ID"
```

RAG検索を試す場合は、先にコーパスを作成して`RAG_CORPUS_ID`を設定します。

```bash
export GCP_PROJECT=your-project-id
python corpus_setup.py
```

テストはGCP接続なしで実行できます。

```bash
cd samples/chapter04
python -m pytest
```

`python -m`で実行するとカレントディレクトリが`sys.path`に入り、`memory_agent`パッケージを絶対importで解決できます。

## Google Cloudが必要なサンプル

`corpus_setup.py`、`rag_corpora.py`、`knowledge_memory_integration.py`、`unified_context_callback.py`と、Memory Bankに接続する`adk run`はGoogle Cloudプロジェクトと課金の有効化が前提です。Vertex AI Memory BankとRAG EngineのAPIコールに課金が発生します。`session_db_config.py`をCloud SQLに向ける場合もインスタンスの費用がかかります。

`memory_agent`は`instruction=build_instruction`で動的Instructionを使うため、`adk web`ではエージェント情報の表示が失敗する場合があります。Session・State・Memory・Compactionの確認は`adk run memory_agent`を主経路にしてください。
