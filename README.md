# 現場で役立つ マルチエージェント設計入門 サンプルコード

書籍『現場で役立つ マルチエージェント設計入門 ～ADK × A2Aで実装する実践運用ガイド～』（為藤アキラ 著）のサンプルコード公開リポジトリです。

本書の紙面に掲載しているコードは要点の抜粋です。省略した箇所は`# ...（エラーハンドリングは省略）...`のように何を省いたかをコメントで示しています。このリポジトリには、その省略部分を補った完全版を章ごとに収録しています。写経の答え合わせ、ハンズオンの詰まったところの参照、自分のプロジェクトへの流用にお使いください。

## 動作環境

| 項目 | バージョン・要件 |
|---|---|
| Python | 3.11以上 |
| Google ADK | v2.2.0（`google-adk==2.2.0`で固定） |
| A2A | A2A v1.0系（第7章のみ。`a2a-sdk>=0.3.24,<0.4.0`） |
| OS | macOS／Linux／WSL2（Windows） |
| パッケージマネージャー | uv（推奨）またはpip |
| Google Cloud CLI（gcloud） | 最新版（Google Cloudを使う章のみ） |

ADK v2.2.0は1.xに対する破壊的変更（Workflow Runtime、Task API、Event schemaの追加）を含みます。バージョンは固定ピンのまま使ってください。ADK v2.2.0のパッケージメタデータはPython 3.10以上を許容しますが、公式READMEの実行要件はPython 3.11+です。本書のサンプルも3.11以上で検証しています。

インストール後、バージョンを確認します。

```bash
adk --version
# 出力例: adk, version 2.2.0
```

## ディレクトリ構成

章ごとにディレクトリを分け、それぞれに`requirements.txt`を置いています。章によって必要なADKのextrasが異なるため、依存は章単位でインストールしてください。

| 章 | タイトル | ディレクトリ | ADKの依存指定 |
|---|---|---|---|
| 第1章 | AIエージェントの全体像 | `samples/chapter01/` | `google-adk==2.2.0` |
| 第2章 | ADK：エージェント開発フレームワーク | `samples/chapter02/` | `google-adk[mcp]==2.2.0` |
| 第3章 | Context Engineering & Agent Skills | `samples/chapter03/` | `google-adk==2.2.0` |
| 第4章 | Session・Memory・RAG | `samples/chapter04/` | `google-adk[db,gcp]==2.2.0` |
| 第5章 | 評価・ガードレール・HITL | `samples/chapter05/` | `google-adk[eval]==2.2.0` |
| 第6章 | MCP & ツール統合 | `samples/chapter06/` | `google-adk[mcp,gcp]==2.2.0` |
| 第7章 | A2Aマルチエージェント実践 | `samples/chapter07/` | `google-adk[a2a]==2.2.0` |
| 第8章 | Agent Engine & AgentOps | `samples/chapter08/` | `google-adk[gcp,otel-gcp]==2.2.0` |
| 第9章 | 設計原則 & アンチパターン | `samples/chapter09/` | `google-adk[eval]==2.2.0` |
| 第10章 | セキュリティ & ガバナンス | `samples/chapter10/` | `google-adk[gcp]==2.2.0` |

各章のディレクトリにREADMEを置いています。収録ファイルの一覧と実行方法はそちらを参照してください。

## セットアップ

### 1. リポジトリの取得

```bash
git clone https://github.com/tameto/adk-multi-agent-book.git
cd adk-multi-agent-book
```

### 2. 仮想環境の作成

リポジトリ直下に仮想環境を1つ作り、章を移動しながら使い回す構成を想定しています。

```bash
python3 -m venv .venv
source .venv/bin/activate      # macOS／Linux
# .venv\Scripts\activate       # Windows
```

uvを使う場合は次のとおりです。

```bash
uv venv
source .venv/bin/activate
```

### 3. 章ごとの依存インストール

進めたい章のディレクトリに移動し、`requirements.txt`をインストールします。

```bash
cd samples/chapter02
pip install -r requirements.txt
# uvを使う場合: uv pip install -r requirements.txt
```

章をまたぐと必要なextrasが変わります。第2章から第6章へ移るときのように依存が増える場合は、移動先の章で`requirements.txt`を再度インストールしてください。ADK本体のバージョンはどの章も`2.2.0`で共通のため、上書きインストールでextrasだけが追加されます。

### 4. 認証情報の設定

エージェントを収めたディレクトリ（`hello_adk/`、`travel_planner/`など）には`.env.example`を置いています。これを`.env`にコピーして値を埋めてください。

```bash
cd samples/chapter01/hello_adk
cp .env.example .env
```

Google AI Studioで発行したAPIキーを使う場合は、次の2行を設定します。APIキーは https://aistudio.google.com/apikey から取得できます。

```bash
GOOGLE_API_KEY=your-api-key
GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

Vertex AI経由で実行する場合は、上の2行ではなく次の3行を設定します。

```bash
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

`GOOGLE_GENAI_USE_VERTEXAI=TRUE`と`GOOGLE_API_KEY`を併記するとVertex AI経路が優先されます。APIキーを設定したのに`PERMISSION_DENIED`が返る場合は、`.env`にプレースホルダのままの`GOOGLE_CLOUD_PROJECT`が残っていないかを確認してください。エージェントディレクトリの`.env`自動読み込みは`ADK_DISABLE_LOAD_DOTENV=1`で止められます。

Google Cloudのサービスを使う章では、あわせてADC（Application Default Credentials）を設定します。

```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable aiplatform.googleapis.com
```

## モデルについて

サンプルは`gemini-3.5-flash`を明示指定しています。ADK v2.2.0の`LlmAgent`の既定モデルは`gemini-3-flash-preview`ですが、本書では暗黙の既定に依存せず、各エージェント定義で`model=`を書いています。

モデルIDや料金が変わる場合は公式ドキュメントで確認し、`.env`または`agent.py`の`model=`引数で差し替えてください。サンプルは構造と設計パターンを学ぶためのもので、特定のモデル出力に依存しません。

## 注意事項

### `.env`はコミットしない

`.gitignore`で`.env`と`credentials.json`、`service-account-key.json`を除外しています。フォークして自分のリポジトリで作業する場合も、APIキーやサービスアカウントキーの漏えいを防ぐため、この除外設定を残したまま使ってください。

### 課金が発生するサンプル

次の章のサンプルはGoogle Cloudプロジェクトと課金の有効化が前提です。実行するとVertex AIのAPIコールに課金が発生します。

| 章 | 課金対象のサービス |
|---|---|
| 第4章 | Vertex AI Memory Bank、Vertex AI RAG Engine、Cloud SQL（DatabaseSessionService利用時） |
| 第5章 | Cloud DLP、Firestore（発展サンプルのみ） |
| 第6章 | BigQuery、Cloud SQL、Spanner、Firestore（MCP Toolbox接続時） |
| 第8章 | Vertex AI Agent Engine、Cloud Run／GKE、Cloud Monitoring、Cloud Trace |
| 第10章 | Cloud Logging、Secret Manager |

実行にかかる費用はモデル呼び出し回数とGoogle Cloudサービスの利用量に応じて変わります。課金状況はGoogle Cloud Consoleの「お支払い」ページで確認してください。

第1章から第3章、第7章、第9章のサンプルはAPIキーだけで動きます。第7章のA2A通信もローカルプロセス間で完結するため、Google Cloudプロジェクトは不要です。

### うまく動かないとき

| 症状 | 確認すること |
|---|---|
| `GOOGLE_API_KEY not set` | エージェントディレクトリに`.env`があるか、キーの値が入っているか |
| `PERMISSION_DENIED` | `GOOGLE_GENAI_USE_VERTEXAI`の値と、`GOOGLE_CLOUD_PROJECT`がプレースホルダのままでないか |
| `API not enabled` | 該当するGoogle Cloud APIを`gcloud services enable`で有効化したか |
| 認証エラーが頻発する | `gcloud auth application-default login`を再実行したか（トークンの期限切れ） |
| importエラー | その章の`requirements.txt`をインストールしたか（章ごとにextrasが異なる） |

## 正誤・質問

誤りや改善点に気づいたら、Issueやプルリクエストで知らせてください。コードの不具合、環境依存の再現手順、本文との食い違いなど、どれも歓迎します。

ADKやA2Aの仕様変更でサンプルが動かなくなった場合も、Issueで報告していただけると助かります。報告の際は、`adk --version`の出力、Pythonのバージョン、エラーメッセージの全文を添えてください。

## ライセンス

このリポジトリのサンプルコードはApache License 2.0で公開しています。全文は[LICENSE](LICENSE)を参照してください。

```text
Copyright 2026 Akira Tameto

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
```

書籍の本文・図表は著作権の対象であり、このライセンスの範囲には含まれません。
