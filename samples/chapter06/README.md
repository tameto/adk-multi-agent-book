# 第6章 MCP & ツール統合

外部システムをエージェントのツールとして取り込むサンプルです。MCP（Model Context Protocol）サーバーへのstdio接続とStreamable HTTP接続、MCP Toolbox経由でのBigQuery／Cloud SQL／Spanner／Firestore統合、CLIコマンドのラッパー化を収録しています。ハンズオンの成果物は`infra_monitor/`で、BigQuery MCPサーバー（ログ分析）とkubectlラッパー（Kubernetes状態確認）を組み合わせたインフラ監視エージェントです。

## 収録内容

| ディレクトリ／ファイル | 内容 |
|---|---|
| `infra_monitor/` | ハンズオン成果物。インフラ監視エージェント（MCP + CLIラッパー） |
| `mcp_stdio_basic.py` | stdioトランスポートによるMCPサーバー接続の基本形 |
| `mcp_streamable_http_basic.py` | Streamable HTTPによるリモートMCPサーバー接続 |
| `mcp_multiple_servers.py` | 複数のMCPサーバーを1つのエージェントに統合する |
| `mcp_tool_filter.py` | `tool_filter`によるツールの絞り込み |
| `mcp_tool_filter_callback.py` | コールバック関数による動的フィルタリング（書き込み系の除外） |
| `mcp_lifecycle.py` | Runnerによる接続ライフサイクルの自動管理 |
| `mcp_error_handling.py` | MCPツール呼び出しのエラーハンドリング |
| `mcp_bigquery.py`／`tools.yaml` | BigQuery MCPサーバー（MCP Toolbox）との統合 |
| `mcp_cloudsql.py`／`tools-cloudsql.yaml` | Cloud SQL MCPサーバーとの統合 |
| `mcp_spanner.py`／`tools-spanner.yaml` | Spanner MCPサーバーとの統合 |
| `mcp_firestore.py`／`tools-firestore.yaml` | Firestore MCPサーバーとの統合 |
| `cli_basic.py` | gcloud CLIをツール化する基本パターン |
| `cli_secure.py` | サブコマンドのホワイトリストによるCLI実行の制限 |
| `cli_kubectl.py` | kubectlのツール化（`secrets`は意図的に除外） |
| `cli_terraform.py` | Terraformのツール化 |
| `mcp_cli_hybrid.py` | MCPとCLIを併用するハイブリッド構成 |
| `tool_catalog.py` | ツールカタログの定義例 |
| `tool_permissions.py` | エージェントのロールごとのツール権限マトリクス |
| `tool_audit.py` | ツール呼び出しの監査ログ |

`tools*.yaml`はMCP Toolboxの設定ファイルです。データソースの定義とツールの定義を`---`区切りで並べます。

## セットアップ

```bash
cd samples/chapter06
pip install -r requirements.txt

cd infra_monitor
cp .env.example .env
```

MCP Toolboxの起動にはNode.js v18以上が必要です。`node --version`で確認してください。

## 実行

BigQuery MCPを無効にしたまま、kubectlラッパー（ダミーデータ）だけで起動できます。この構成ならGoogle Cloudプロジェクトは不要です。

```bash
cd samples/chapter06
export ENABLE_BIGQUERY_MCP=0
adk run infra_monitor
```

BigQuery MCPサーバーにも接続する場合は、ADCの設定とプロジェクトIDの指定を加えます。

```bash
gcloud auth application-default login
export GCP_PROJECT_ID="your-project-id"
export ENABLE_BIGQUERY_MCP=1
adk run infra_monitor
```

ブラウザで確認する場合は`adk web .`を実行し、http://localhost:8000 でエージェント一覧から`infra_monitor`を選びます。

## Google Cloudが必要なサンプル

`mcp_bigquery.py`、`mcp_cloudsql.py`、`mcp_spanner.py`、`mcp_firestore.py`、および`ENABLE_BIGQUERY_MCP=1`での`infra_monitor`は、Google Cloudプロジェクトと該当サービスの有効化が前提です。クエリの実行に応じて課金が発生します。

CLIラッパーのサンプルは実際に`gcloud`／`kubectl`／`terraform`を呼び出します。読み取り系のサブコマンドだけを許可するホワイトリストを実装していますが、対象の環境で実行される点に注意してください。`infra_monitor/tools.py`のkubectlラッパーはダミーデータを返す実装で、実際のクラスタには接続しません。
