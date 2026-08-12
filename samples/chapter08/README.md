# 第8章 Agent Engine & AgentOps

ローカルで動くエージェントを本番環境に載せ、動かし続けるためのサンプルです。Vertex AI Agent Engine／Cloud Run／GKEの3つのデプロイ先、Cloud Monitoringのダッシュボードとアラート、インシデント調査、セッションデータの移行を収録しています。デプロイ対象は`support_agent/`で、ルーティングエージェントと専門エージェントを分けたマルチエージェント構成です。

## 収録内容

| ディレクトリ／ファイル | 内容 |
|---|---|
| `support_agent/` | デプロイ対象のカスタマーサポートエージェント（構造化ログ付き） |
| `deploy/deploy.sh` | Agent Engineへのデプロイスクリプト（`adk deploy`） |
| `deploy/deploy_sdk.py` | Python SDKによるデプロイ（CI/CD組み込み向け） |
| `deploy/cloud_run/agent.py` | Cloud Runデプロイ用のエージェント定義（`app.py`が読み込む） |
| `deploy/cloud_run/app.py` | ADKエージェントをFastAPIでラップしたHTTPサーバー |
| `deploy/cloud_run/Dockerfile` | Cloud Run用のコンテナ定義 |
| `deploy/cloud_run/deploy_cloud_run.sh` | Cloud Runへのデプロイスクリプト |
| `deploy/gke/deployment.yaml` | GKE用マニフェスト（Deployment + Service + HPA） |
| `deploy/session_migrator.py` | Agent Engine（VertexAiSessionService）から外部DBへのセッション移行 |
| `monitoring/dashboard.json` | Cloud Monitoringダッシュボードの宣言的定義 |
| `monitoring/dashboard_setup.py` | Python SDKによるダッシュボード作成 |
| `monitoring/agent_alerts.py` | Python SDKによるAlertPolicy作成（エラー率5%超、ツール失敗率10%超） |
| `monitoring/setup_alerts.sh` | gcloud CLIによる同等のアラート設定 |
| `monitoring/incident_response.py` | Cloud LoggingとCloud Traceを使った初動調査 |
| `query_with_retry.py` | Interactions APIの指数バックオフとエラー分類 |
| `test_alert.py` | 意図的にエラーを発生させてアラートの発火を確認する |

## セットアップ

```bash
cd samples/chapter08
pip install -r requirements.txt

cd support_agent
cp .env.example .env
```

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1
gcloud auth application-default login
gcloud services enable aiplatform.googleapis.com
```

`requirements.txt`はADKの`gcp,otel-gcp` extrasに加えて、`google-cloud-aiplatform[agent-engines]`、OpenTelemetryのOTLPエクスポーター、Monitoring／Logging／Traceの各クライアントを含みます。Cloud Runへのデプロイでは`deploy/cloud_run/requirements.txt`が別に使われます。

## 実行

デプロイ前にローカルで動作を確認します。

```bash
cd samples/chapter08
adk run support_agent
```

Agent Engineにデプロイします。

```bash
cd samples/chapter08/deploy
bash deploy.sh
```

Cloud Runにデプロイする場合は`deploy/cloud_run/deploy_cloud_run.sh`を使います。GKEの場合はプロジェクトIDを置換してマニフェストを適用します。

```bash
cd samples/chapter08/deploy/gke
sed "s/my-project/${GOOGLE_CLOUD_PROJECT}/g" deployment.yaml | kubectl apply -f -
```

監視の設定、アラートの動作確認、インシデント調査は次の順で実行します。

```bash
cd samples/chapter08/monitoring
python dashboard_setup.py
python agent_alerts.py
python incident_response.py    # Cloud LoggingとCloud Traceを参照

cd ..
export AGENT_ENGINE_RESOURCE_NAME="projects/.../reasoningEngines/..."
python test_alert.py           # 意図的にエラーを発生させてアラートを確認
```

## Google Cloudが必要なサンプル

この章のサンプルは`support_agent`のローカル実行を除き、すべてGoogle Cloudプロジェクトと課金の有効化が前提です。Agent Engineのデプロイ、Cloud Run／GKEの実行、Cloud Monitoringのダッシュボードとアラート、Cloud LoggingとCloud Traceの参照で課金が発生します。

デプロイしたAgent Engineのインスタンスは、動かしていなくても保持コストがかかります。ハンズオンを終えたら削除してください。`deploy/cloud_run/app.py`はDatabaseSessionServiceを使うため、`DATABASE_URL`にCloud SQL等の接続文字列を設定する必要があります。
