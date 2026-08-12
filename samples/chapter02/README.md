# 第2章 ADK：エージェント開発フレームワーク

ADKの構成要素を機能ごとに分けて収録しています。オーケストレーション（Sequential／Parallel／Loop／カスタムエージェント）、ツール定義の各パターン、認証方式、デバッグ手法の4系統です。ハンズオンの成果物は`travel_planner/`で、ParallelAgentで3つの調査を並列実行し、その結果をSequentialAgentで日程表と予算レポートにまとめる構成になっています。

## 収録内容

| ディレクトリ／ファイル | 内容 |
|---|---|
| `travel_planner/` | ハンズオン成果物。旅行プランナーエージェント（Sequential + Parallel） |
| `instruction_examples.py` | 動的instructionと`output_key`／`output_schema`の完全版 |
| `orchestration/sequential_pipeline.py` | SequentialAgentによる順次実行 |
| `orchestration/parallel_search.py` | ParallelAgentによる並列実行 |
| `orchestration/loop_refinement.py` | LoopAgentによる自己修正ループ（最大3回） |
| `orchestration/custom_agent.py` | BaseAgent継承によるカスタムエージェント（条件分岐・多数決） |
| `orchestration/nested_pipeline.py` | Sequential内にParallelを配置する入れ子構造 |
| `orchestration/llm_delegation.py` | `sub_agents`によるLLM委譲 |
| `orchestration/conditional_routing.py` | コールバックの戻り値による動的ルーティング |
| `orchestration/hitl_approval.py` | LongRunningFunctionToolによる承認ステップ |
| `orchestration/combined_support_pipeline.py` | Parallel → Loopの組み合わせ例 |
| `tools/function_tool_*.py` | FunctionToolの各パターン（基本形、非同期、Enum、Optional、Pydantic、ToolContext） |
| `tools/agent_tool_experts.py` | AgentToolでエージェントをツール化する |
| `tools/long_running_report.py` | LongRunningFunctionToolによる長時間タスク |
| `tools/mcp_toolset_example.py` | McpToolsetでMCPサーバーを統合する（`mcp` extraが必要） |
| `tools/builtin_tools.py` | 組み込みツール（google_search、BuiltInCodeExecutor、ExecuteBashTool） |
| `tools/tool_best_practices.py` | ツール設計のベストプラクティス |
| `auth/api_key_auth.py` | APIキー認証 |
| `auth/oauth2_calendar.py` | OAuth 2.0認証（Google Calendar） |
| `auth/service_account_bigquery.py` | Service Account認証（ADC経由） |
| `auth/auth_provider_registry_example.py` | AuthProviderRegistryによるプラグイン認証（experimental API） |
| `auth/secure_tool_wrapper.py` | 認証チェック付きツールラッパー（複数ツールでの認証共通化） |
| `debugging/debug_callbacks.py` | コールバックによるログ挿入 |
| `debugging/run_agent.py` | RunnerとInMemorySessionServiceによるスクリプト実行 |

`orchestration/`と`tools/`の各ファイルは、紙面では省略しているimportやダミーツールを補って単体で読める形にしています。`root_agent`を公開しているファイルは`adk run`／`adk web`からも参照できます。

## セットアップ

```bash
cd samples/chapter02
pip install -r requirements.txt

cd travel_planner
cp .env.example .env
```

`tools/mcp_toolset_example.py`がMcpToolsetを使うため、この章の`requirements.txt`はADKの`mcp` extraを指定しています。`auth/service_account_bigquery.py`は`google-cloud-bigquery`を使います。

## 実行

ハンズオンの旅行プランナーを動かします。

```bash
cd samples/chapter02
adk run travel_planner
```

`travel_planner`はWorkflow rootのため、ADK v2.2.0では`adk run`での確認を推奨します。

個別のサンプルは定義内容の確認用に`__main__`ブロックを持たせています。対話実行は`adk run`／`adk web`を使ってください。

```bash
cd samples/chapter02
python orchestration/sequential_pipeline.py
```

## 注意事項

`auth/service_account_bigquery.py`はGoogle CloudのADC（Application Default Credentials）を使います。ローカルで試す場合は`gcloud auth application-default login`を先に実行してください。`auth/oauth2_calendar.py`は環境変数`OAUTH_CLIENT_ID`と`OAUTH_CLIENT_SECRET`が必要です。

検索ツールは全てダミー実装で、固定のデータを返します。実運用ではGoogle Places APIやMaps API等の呼び出しに差し替えます。
