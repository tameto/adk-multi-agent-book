# 新旧名称対照ガイド

書籍『現場で役立つ マルチエージェント設計入門 ～ADK × A2Aで実装する実践運用ガイド～』が扱うGoogle Cloud・ADK・A2A・MCPでは、プロダクト名やAPI名の変更が続いています。本書は執筆時点（ADK v2.2.0、A2A v1.0系）の名称で書かれているため、公式ドキュメントを探すときや古い記事・コードを読むときに、名前の食い違いで迷子になることがあります。このページは、本書に関係する新旧名称を1か所にまとめた対照表です。書籍本体と違い、名称変更があり次第更新します。

- 最終更新：2026-08-20
- 基準バージョン：ADK v2.2.0 / A2A v1.0系 / 書籍執筆時点のGoogle Cloudドキュメント

## Google Cloudプロダクト名・ドキュメント

Google Cloudのエージェント関連サービスでは、**プロダクト名・ドキュメント上の呼称・APIリソース名の3つが一致しない**ことがあります。対照を表1に示します。

**表1 Google Cloudプロダクト名の新旧対照**

| 旧名称 | 現行名称（執筆時点） | 補足 |
|---|---|---|
| Reasoning Engine | Vertex AI Agent Engine | プロダクト名は改称済み。ただしAPIリソース名は`reasoningEngines`のまま（`agentengine://projects/.../reasoningEngines/ID`のURI形式、[付録A](adk-cli-reference.md)のA-10節）。Cloud Monitoringも監視リソースタイプは`aiplatform.googleapis.com/ReasoningEngine`、metric typeは`reasoning_engine/request_latencies`のように旧名ベース（書籍第8章の監視クエリ） |
| Vertex AI Agent Engineのドキュメント・料金ページ | Gemini Enterprise Agent Platform配下の**Agent Runtime** | 公式ドキュメントは`docs.cloud.google.com/gemini-enterprise-agent-platform/`配下へ、料金ページは`cloud.google.com/products/gemini-enterprise-agent-platform/pricing`へ移動し、ランタイム部分はAgent Runtimeと呼ばれる。一方でADK CLI（`adk deploy agent_engine`）とSDK（`vertexai.agent_engines`）はAgent Engine名のまま |

同じサービスが、ADK CLI・SDKでは**Agent Engine**、新ドキュメント・料金ページでは**Agent Runtime**、API・メトリクスでは**ReasoningEngine**という3つの名前で現れます。ドキュメント検索で見つからないときは、この3つの名前で探し直してください。なお、書籍第8章では、Agent EngineをVertex AI Agent Builder配下のマネージドランタイムとして説明しています。

ADK公式ドキュメントのサイト自体も、`google.github.io/adk-docs`から`adk.dev`へ移行しています。古い記事のリンクが切れている場合は`adk.dev`で同名ページを探してください。

## ADK 1.x → 2.x のAPI名

ADK 2.xは1.xとの互換エイリアスを残しつつ、推奨名を変更しています。対照を表2に示します（詳細は書籍第2章・第3章）。

**表2 ADK 1.x → 2.x の名称対照**

| 旧名称（1.x） | 現行名称（2.x） | 補足 |
|---|---|---|
| `LlmAgent` | `Agent` | `Agent`は`LlmAgent`のエイリアスで両方動く。本書はv2.2.0公式Quickstartに合わせ`Agent`表記 |
| `CallbackContext` / `ToolContext` | `Context` | 両者は`Context`の互換エイリアスとして残る。コールバック・ツール関数の引数名（`callback_context`、`tool_context`）は変えないこと |
| `Agent.global_instruction`フィールド | `GlobalInstructionPlugin`（`App`に登録） | `global_instruction`は非推奨。新規コードはプラグイン方式 |
| 既定モデル`gemini-2.5-flash` | 既定モデル`gemini-3-flash-preview` | 本書は暗黙の既定に依存せず、サンプルで`gemini-3.5-flash`を明示 |
| 内部用語 turn | step | GenAI SDK v2対応に伴い、内部用語がturnからstepへ移行しつつある |
| 同期`stream_query` | `async_stream_query` | Agent Engineデプロイでは同期版が非推奨。新規コードは非同期版を使う |

## ADK CLIのオプション・パス

CLIレベルの非推奨・変更を表3に示します（詳細は[付録A](adk-cli-reference.md)）。

**表3 ADK CLIの新旧対照**

| 旧名称 | 現行名称 | 補足 |
|---|---|---|
| `--trace_to_cloud`（`adk deploy agent_engine`） | `--otel_to_cloud` | agent_engineでは非推奨。`adk web` / `adk deploy cloud_run`では両オプションとも現役 |
| `--staging_bucket` / `--env_file` / `--requirements_file` / `--adk_app` / `--absolutize_imports`（agent_engine） | `.agent_engine_config.json`と`AGENT`ディレクトリ直下の`requirements.txt`、機密情報はSecret Manager | いずれもagent_engineで非推奨。`--requirements_file`は値を渡しても無視される |
| 開発用API `GET /app-info/{app_name}` | `GET /apps/{app_name}/app-info` | 旧パスは不可 |
| `adk eval`のヘルプ表示の`AGENT_MODULE_FILE_PATH` | `AGENT_DIR` | v2.2.0のヘルプ文に古い引数名が残っているが、実装上はエージェントディレクトリを指定する |

## A2A v0.3.x → v1.0系のメソッド名

A2AのJSON-RPC／gRPCメソッド名は、v1.0系でPascalCaseに変更されました。対照を表4に示します（詳細は書籍第7章）。

**表4 A2Aメソッド名の新旧対照**

| 旧名称（v0.3.x） | 現行名称（v1.0系） | 操作 |
|---|---|---|
| `message/send` | `SendMessage` | タスクにメッセージを送信（同期） |
| `message/stream` | `SendStreamingMessage` | タスクにメッセージを送信（ストリーミング） |
| `tasks/get` | `GetTask` | タスクの現在の状態を取得 |
| （なし） | `ListTasks` | タスク一覧の取得。v1.0.0で追加 |
| `tasks/cancel` | `CancelTask` | タスクのキャンセル |
| `tasks/resubscribe` | `SubscribeToTask` | ストリーミング再接続 |
| `tasks/pushNotificationConfig/set` | `CreateTaskPushNotificationConfig` | Push Notification URL登録 |

本書のADK v2.2.0サンプルは`a2a-sdk` 0.3.xを使うため、JSON-RPC上では旧メソッド名で通信します。HTTP+JSON／RESTバインディングでは`POST /message:send`のようなURLパターンを使います。

## MCPのトランスポート名

MCP（Model Context Protocol）のリモート接続方式は、仕様の2025年改訂で置き換えられました。対照を表5に示します（詳細は書籍第6章）。

**表5 MCPトランスポートの新旧対照**

| 旧名称 | 現行名称 | 補足 |
|---|---|---|
| HTTP+SSE | Streamable HTTP | Streamable HTTPが正式トランスポート。HTTP+SSEは後方互換として残るが新規利用は非推奨 |
| `SseConnectionParams`（ADKの接続クラス） | `StreamableHTTPConnectionParams` | 旧仕様のHTTP+SSEサーバーに接続する場合のみ`SseConnectionParams`を使う |

## 名前で見つからないときの探し方

- **APIリソース名で探す**：プロダクト名が変わってもAPIリソース名（`reasoningEngines`など）は互換性のため残ることが多く、REST APIリファレンスやgcloudコマンドはリソース名から辿れます
- **メトリクスは旧名も確認する**：Cloud Monitoringの監視リソースタイプやmetric typeには改称前の名前が残ります（例：`ReasoningEngine`）
- **リリースノートを確認する**：改称・非推奨の一次情報は各プロジェクトのリリースノートです。[google/adk-python Releases](https://github.com/google/adk-python/releases)、[a2aproject/A2A Releases](https://github.com/a2aproject/A2A/releases)、[Google Cloud release notes](https://cloud.google.com/release-notes)を参照してください

このページに載っていない名称変更に気づいた場合は、[Issue](https://github.com/tameto/adk-multi-agent-book/issues)で知らせてください。
