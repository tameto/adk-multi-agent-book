# 付録B 参考文献

> **このページについて**：書籍『現場で役立つ マルチエージェント設計入門 ～ADK × A2Aで実装する実践運用ガイド～』（為藤アキラ 著）の付録B「参考文献」を、著者がオンライン閲覧用に転載したものです。本文中の「第N章」は書籍の章を指します。このページの本文は書籍の一部であり、リポジトリのライセンス（Apache License 2.0）の対象外です（© 2026 Akira Tameto）。リンク切れを見つけた場合は[Issue](https://github.com/tameto/adk-multi-agent-book/issues)で報告してください。

本書の執筆で参照した公式ドキュメント、書籍、標準規格を章別に整理します。URLは執筆時点のもので、アクセス時に変更されている可能性があります。

本書は Google ADK（Agent Development Kit）、A2A（Agent2Agent）プロトコル、MCP（Model Context Protocol）、Vertex AI Agent Engine を主要な題材としています。一次情報として各プロジェクトの公式ドキュメント・公式リポジトリを参照することを推奨します。

## はじめに

- [Google ADK 公式ドキュメント](https://adk.dev/)。ADK の最新 API・機能・チュートリアルの一次情報源。本書執筆後の API 変更はここで確認する
- [google/adk-python Releases](https://github.com/google/adk-python/releases)。ADK Python 1.x / 2.x のリリース履歴、破壊的変更、セキュリティ修正の確認先。本書の検証基準である ADK v2.2.0 との差分確認に使用する
- [Digital Applied: AI Agent Adoption 2026: 120+ Enterprise Data Points](https://www.digitalapplied.com/blog/ai-agent-adoption-2026-enterprise-data-points)（2026年4月19日公開）。AIエージェントの本番到達ギャップを説明する市場データとして参照。対象調査や「本番」の定義で移行率は変わるため、本書ではラストワンマイル問題を示す補助指標として扱う
- [Anthropic Claude API Docs / Models overview](https://docs.anthropic.com/en/docs/about-claude/models/overview)。Claudeモデル系列、モデルID、移行案内の確認先。AIコーディングエージェントの検証基準モデルを更新する際に参照
- [Gemini 3.5 Flash 公式モデルページ](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash)。`gemini-3.5-flash` のモデルID、Stableステータス、トークン上限、対応機能の確認先
- [Gemini Developer API pricing](https://ai.google.dev/gemini-api/docs/pricing)。Gemini 3.5 Flashを含むGemini APIの入力・出力・キャッシュ単価の確認先
- [Google Cloud Console](https://console.cloud.google.com)。Google Cloud プロジェクトの作成・管理画面。本書のハンズオンで使用する Vertex AI / Agent Engine の有効化に必要
- [gcloud CLI インストールガイド](https://cloud.google.com/sdk/docs/install)。Google Cloud CLI のインストール手順（macOS / Linux / Windows 対応）
- [uv（Python パッケージマネージャー）インストールスクリプト](https://astral.sh/uv/install.sh)。本書で推奨する Rust 製の高速 Python パッケージマネージャー

## 第1章 AIエージェントの全体像

- Stuart Russell, Peter Norvig『Artificial Intelligence: A Modern Approach』(4th Edition, Pearson, 2020)。人工知能の古典的教科書。「センサーを通じて環境を知覚し、アクチュエータを通じて環境に作用するもの」というエージェント定義の出典

## 第2章 ADK：エージェント開発フレームワーク

本章は ADK の核となる `Agent`（`LlmAgent`エイリアス）、Workflow Runtime、Runner、Session、Tools の概念を扱います。`SequentialAgent` / `ParallelAgent` / `LoopAgent` はTemplate Workflowとして扱い、複雑な制御ではGraph-based Workflow / Dynamic Workflowを優先する方針を示します。ADK 公式ドキュメント（はじめに参照）を一次情報として参照してください。

- [Google ADK 公式ドキュメント / Agents](https://adk.dev/agents/llm-agents/)。`Agent`（`LlmAgent`）とワークフローエージェントの API リファレンス
- [google/adk-python（GitHub）](https://github.com/google/adk-python)。ADK Python 実装のソースコード。本書で紹介する API の正規の定義を確認する際に参照

## 第3章 Context Engineering & Agent Skills

本章の Agent Skills、`load_skill_from_dir()`、`InvocationContext` / `ReadonlyContext` / `Context` を中心とした ADK v2.2.0のContextモデルは ADK 公式ドキュメントに準拠しています。

- [Google ADK 公式ドキュメント / Context](https://adk.dev/context/)。`InvocationContext`、`ReadonlyContext`、`Context` と `CallbackContext` / `ToolContext` のエイリアス関係
- [Google ADK 公式ドキュメント / Skills](https://adk.dev/skills/)。Agent Skills の構造と `load_skill_from_dir()` による読み込み方法

## 第4章 Session・Memory・RAG

- [Vertex AI 生成 AI 価格表](https://cloud.google.com/vertex-ai/generative-ai/pricing)。Gemini モデルの呼び出し単価および Memory Bank / RAG Engine の料金。本書のコスト試算は参考値のため、最新料金はこのページで確認する
- [ADK 公式ドキュメント / Compaction](https://adk.dev/context/compaction/)。ADK v2.2.0で利用する compaction の設定パラメータ（`compaction_interval` / `overlap_size` / `summarizer` / `token_threshold` / `event_retention_size`）
- [Vertex AI Agent Engine / Memory Bank](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview)。Vertex AI Memory Bank の Consolidation 機能と API リファレンス
- [Vertex AI RAG Engine 公式ドキュメント](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview)。Corpus / Index / Retrieval のコンポーネントと ADK 統合

## 第5章 評価・ガードレール・HITL

本章の `adk eval`、User Personas、Callback ベースのガードレール、HITL パターンは ADK 公式ドキュメントに準拠します。

- [Google ADK 公式ドキュメント / Evaluate](https://adk.dev/evaluate/)。`adk eval` コマンドと評価セットの定義方法
- [Google ADK 公式ドキュメント / Callbacks](https://adk.dev/callbacks/)。`before_model_callback` / `after_model_callback` / `before_tool_callback` によるガードレール実装

## 第6章 MCP & ツール統合

- [Model Context Protocol 公式サイト](https://modelcontextprotocol.io/)。MCP の仕様・クライアント / サーバー SDK・サンプル実装の一次情報
- [MCP 仕様書](https://modelcontextprotocol.io/specification/2025-11-25)。JSON-RPC ベースのプロトコル定義、Tools / Resources / Prompts の 3 プリミティブ
- [modelcontextprotocol/servers（GitHub）](https://github.com/modelcontextprotocol/servers)。MCP サーバー実装集（filesystem、postgres、github 等）
- [Google ADK 公式ドキュメント / Tools / MCP](https://adk.dev/tools-custom/mcp-tools/)。ADK の `McpToolset` を使った MCP サーバー接続
- [google/mcp（GitHub）](https://github.com/google/mcp)。Google 公式MCPサーバー一覧とGoogle Cloudでのデプロイ例
- [googleapis/mcp-toolbox（GitHub）](https://github.com/googleapis/mcp-toolbox)。MCP Toolbox for Databases のソース。BigQuery / Cloud SQL / Spanner / AlloyDB 等の対応状況確認先
- [Use the BigQuery MCP server](https://docs.cloud.google.com/bigquery/docs/use-bigquery-mcp)。BigQuery remote MCP server の公式手順

## 第7章 A2A マルチエージェント実践

- [A2A プロトコル公式サイト](https://a2a-protocol.org/latest/specification/)。Agent Card、通信バインディング、タスクライフサイクルの仕様
- [a2aproject/A2A（GitHub）](https://github.com/a2aproject/A2A)。A2A プロトコル仕様のソース
- [a2aproject/A2A Releases](https://github.com/a2aproject/A2A/releases)。A2A仕様タグのリリース日と変更内容の確認先
- [a2aproject/a2a-python（GitHub）](https://github.com/a2aproject/a2a-python)。A2A Python SDK（`ClientFactory` / サーバー実装）
- [Google ADK 公式ドキュメント / A2A](https://adk.dev/a2a/)。ADK から A2A エージェントを呼び出す `RemoteA2aAgent` の使い方

## 第8章 Agent Engine & AgentOps

- [Gemini Enterprise Agent Platform pricing](https://cloud.google.com/products/gemini-enterprise-agent-platform/pricing)。Agent Runtime / Sessions / Memory Bank / Code Execution の単価確認先。TCO 比較のベースライン
- [Agent Runtime setup](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/runtime/setup)。Agent Runtime の利用に必要なAPI有効化、IAMロール、サービスエージェント、SDKインストールの確認先
- [Use an Agent Development Kit agent](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/use-an-adk-agent)。`AdkApp`でデプロイしたAgent Runtimeリソースの`async_stream_query`やSession操作の確認先
- [Set up tracing](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/tracing)。Agent RuntimeでCloud Trace / OpenTelemetryを有効化する手順。ADK v2.2.0のAgent Engineデプロイでは`--otel_to_cloud`やテレメトリ環境変数を確認する（`--trace_to_cloud`は非推奨）
- [Vertex AI Agent Engine 公式ドキュメント](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)。Agent Engine / Agent Runtime のアーキテクチャ、デプロイ、モニタリング
- [Cloud Run 公式ドキュメント](https://cloud.google.com/run/docs)。ADK エージェントを Cloud Run にデプロイする際のリファレンス
- [Google Kubernetes Engine 公式ドキュメント](https://cloud.google.com/kubernetes-engine/docs)。大規模運用時の選択肢としての GKE デプロイリファレンス

## 第9章 設計原則 & アンチパターン

本章で示す設計原則は、ADK 公式ドキュメントのベストプラクティスおよび A2A プロトコル仕様に準拠します。第2章・第7章の参照文献を併用してください。

- [Google ADK 公式ドキュメント / Workflows](https://adk.dev/workflows/)。サブエージェント設計、オーケストレータパターンの公式ガイダンス

## 第10章 セキュリティ & ガバナンス

- [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/llm-top-10/)。LLM / GenAI アプリケーション固有の10大リスク分類。プロンプトインジェクション、機密情報漏えい、過剰な自律性等、エージェント設計時の脅威モデリングの一次情報
- [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)。自律的に計画・実行するエージェントシステム向けの10大リスク分類。ゴール乗っ取り、ツール誤用、エージェント間通信、連鎖障害等の一次情報
- ISO/IEC 27001:2022『情報セキュリティマネジメントシステム / 要求事項』。情報セキュリティマネジメントの国際標準
- [GDPR（EU 一般データ保護規則）公式テキスト](https://gdpr-info.eu/)。データ主体の権利、越境転送、制裁金の規定
- [個人情報の保護に関する法律（個人情報保護法）](https://www.ppc.go.jp/personalinfo/legal/)。日本の個人情報保護法の公式ポータル
- [SOC 2（AICPA）](https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2)。セキュリティ・可用性・処理の整合性・機密性・プライバシーの監査基準

## 付録A ADK CLI リファレンス

付録A は ADK CLI コマンド（`adk create` / `adk run` / `adk web` / `adk eval` / `adk eval_set` / `adk test` / `adk optimize` / `adk migrate` / `adk conformance` / `adk deploy` / `adk api_server`）の用法をまとめたものです。最新のオプション一覧は ADK 公式ドキュメントと `adk --help` 出力を参照してください。

- [Google ADK 公式ドキュメント / CLI](https://adk.dev/api-reference/cli/)。`adk` CLI の基本的なコマンドフロー
- [google/adk-python / CLI 実装](https://github.com/google/adk-python/tree/main/src/google/adk/cli)。CLI コマンドのソース。未ドキュメント化オプションを確認する際に参照
- [google/adk-python Releases](https://github.com/google/adk-python/releases)。CLI オプションやAPIシグネチャが本書の固定範囲（ADK v2.2.0）から変わっていないか確認する一次情報

**注記**：本リストに含まれない ADK / A2A / MCP / Vertex AI の個別 API リファレンスは、各プロジェクトの公式ドキュメントのトップページから辿れます。本書のコード例は ADK v2.2.0 で検証します。以降に追加された機能は、公式ドキュメントとソースコード（`github.com/google/adk-python`）を正規の定義として扱ってください。
