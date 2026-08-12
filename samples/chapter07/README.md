# 第7章 A2Aマルチエージェント実践

エージェント同士をA2A v1.0系のプロトコルで接続するサンプルです。`to_a2a()`によるA2Aサーバー化、`RemoteA2aAgent`によるクライアント側の委譲、Hub-Spoke／Pipeline／Peer-to-Peerの3パターン、SSEストリーミング、OAuth2認証、Push Notificationを収録しています。ハンズオンの成果物は`expense_server/`・`approval_server/`・`orchestrator/`の3つで、独立プロセスの経費精算エージェントと承認エージェントを、オーケストレーターが呼び分ける構成です。

## 収録内容

| ディレクトリ／ファイル | 内容 |
|---|---|
| `expense_server/` | 経費精算A2Aサーバー（ポート8001）。`to_a2a()`でStarletteアプリに変換 |
| `approval_server/` | 承認A2Aサーバー（ポート8002）。承認ルールに基づく自動承認・上長承認・部長承認 |
| `orchestrator/` | オーケストレーター。`RemoteA2aAgent`で2つのサーバーに委譲する |
| `run_servers.py` | 2つのA2Aサーバーをサブプロセスとして同時起動する |
| `client.py` | `a2a.client.Client`による低レベルクライアントの基本形 |
| `client_followup.py` | `TASK_STATE_INPUT_REQUIRED`のハンドリングとタスク状態のポーリング |
| `streaming_client.py` | SSEストリーミングクライアント（TaskStatusUpdateEvent／TaskArtifactUpdateEvent） |
| `patterns/hub_spoke.py` | Hub-Spokeパターン（RemoteA2aAgent + AgentTool） |
| `patterns/pipeline.py` | Pipelineパターン（各ステージを独立デプロイし、SequentialAgentで接続） |
| `patterns/peer_to_peer.py` | Peer-to-Peerパターン（サーバーでありクライアントでもあるエージェント） |
| `patterns/stage3_server.py` | 3台目のA2Aサーバー（レポート生成・ポート8003）。3台構成のパターン実行用 |
| `auth/oauth2_client.py` | AuthInterceptorによるBearerトークンの注入と401時の再試行 |
| `auth/oauth2_server.py` | Starletteミドルウェアによるトークン検証とスコープ確認 |
| `push_notification.py` | `set_task_callback()`によるWebhook登録と受信 |
| `a2ui/relay_server.py` | A2AイベントをUI表示用JSONに変換するWebSocket中継サーバー（ポート8080） |
| `a2ui/dashboard.py` | 複数Spokeの状態を一元管理するダッシュボード |

## セットアップ

```bash
cd samples/chapter07
pip install -r requirements.txt

cd expense_server
cp .env.example .env
cd ../approval_server
cp .env.example .env
cd ../orchestrator
cp .env.example .env
```

`requirements.txt`はADKの`a2a` extraに加えて、`a2a-sdk>=0.3.24,<0.4.0`、`uvicorn`、`fastapi`（A2UIのWebSocket中継用）、`httpx`と`google-auth`（OAuth2用）を指定しています。

ADK v2.2.0のA2A実装はexperimental（`@a2a_experimental`）です。インスタンス化時に`UserWarning`が出ます。抑制する場合は環境変数`ADK_SUPPRESS_EXPERIMENTAL_FEATURE_WARNINGS=1`を設定してください。

## 実行

ターミナルを2つ使います。1つ目でA2Aサーバー2台を起動します。

```bash
cd samples/chapter07
python run_servers.py
```

2つ目でオーケストレーターを起動します。

```bash
cd samples/chapter07
adk web .
```

http://localhost:8000 を開き、エージェント一覧から`orchestrator`を選びます。サーバーは`Ctrl+C`で両方まとめて停止します。

低レベルクライアントから直接呼び出す場合は、サーバーを起動した状態で次を実行します。

```bash
cd samples/chapter07
python client.py
python streaming_client.py
```

## サーバーの起動が前提のサンプル

`patterns/`のパターン3ファイルは、それぞれ対応するA2Aサーバーが起動していることを前提にしています。`hub_spoke.py`と`pipeline.py`はポート8001から8003の3台、`peer_to_peer.py`はポート8002と8003の2台です。`run_servers.py`が起動するのは8001と8002の2台のため、3台構成で試す場合は3台目を別のターミナルで起動します。

```bash
cd samples/chapter07
python patterns/stage3_server.py
```

`hub_spoke.py`は起動前にAgent Card URLを確認し、未起動のサーバーがあれば委譲に進まず案内を表示します。

`pipeline.py`の実行時にはADK v2.2.0が`SequentialAgent`の非推奨警告（`DeprecationWarning: ... Please use Workflow instead.`）を表示します。動作には影響ありません。分岐や再開を含む本番構成はWorkflow Runtimeで表現してください（書籍7-3-2参照）。

`a2ui/relay_server.py`と`a2ui/dashboard.py`もA2Aサーバーの起動が前提です。

`auth/oauth2_client.py`は環境変数`OAUTH2_TOKEN_URL`／`OAUTH2_CLIENT_ID`／`OAUTH2_CLIENT_SECRET`／`OAUTH2_SCOPES`、`auth/oauth2_server.py`は`OAUTH2_AUDIENCE`が必要です。認証情報はコードに直書きせず、環境変数から取得してください。

## a2a-sdkのバージョンについて

Agent Cardの定義は`a2a-sdk` 0.3.x仕様に準拠しています。`AgentCard.url`はトップレベルの必須フィールドで、`AgentSkill.tags`も必須です。0.4系ではこの構造が変わります。サンプルを新しいSDKで動かす場合は、Agent Cardの組み立て部分を先に確認してください。
