# samples/chapter06/infra_monitor/agent.py
"""第6章 ハンズオン: インフラ監視エージェント

BigQuery MCPサーバー（ログ分析）と kubectl CLIラッパー（Kubernetes状態確認）を
組み合わせたインフラ監視エージェント。
"""

import os
import sys
from pathlib import Path

from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

try:
    from .tools import kubectl_get_events, kubectl_get_nodes, kubectl_get_pods
except ImportError:
    # ADKがエージェントディレクトリを直接ロードする場合のフォールバック
    sys.path.insert(0, os.path.dirname(__file__))
    from tools import kubectl_get_events, kubectl_get_nodes, kubectl_get_pods

def _bigquery_enabled() -> bool:
    """BigQuery MCPサーバーを接続するかどうかを環境変数から判定する"""
    return os.environ.get("ENABLE_BIGQUERY_MCP") == "1"


def _build_tools() -> list:
    """ローカル検証時に外部MCPサーバーなしでも起動できるツール構成を返す"""
    tools = [
        kubectl_get_pods,
        kubectl_get_nodes,
        kubectl_get_events,
    ]

    if not _bigquery_enabled():
        return tools

    # BigQuery MCPサーバー（MCP Toolbox）の接続パラメータ。
    # 実行には Node.js v18+、gcloud認証、tools.yaml（同ディレクトリ）が必要。
    config_path = os.environ.get(
        "TOOLBOX_CONFIG",
        str(Path(__file__).with_name("tools.yaml")),
    )
    bigquery_connection = StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "@toolbox-sdk/server",
                "--stdio",
                "--config",
                config_path,
            ],
            env={"GOOGLE_CLOUD_PROJECT": os.environ.get("GCP_PROJECT_ID", "")},
        )
    )
    tools.append(McpToolset(connection_params=bigquery_connection))
    return tools


def _build_instruction() -> str:
    """ツール構成に合わせて行動指針を組み立てる

    BigQuery MCPが無効なローカル検証時は、未登録のログ分析ツールを
    モデルが呼び出してエラーになるのを防ぐため、kubectl運用に限定した
    指示を返す。
    """
    common_footer = """
## 判断の手順
1. まずユーザーのリクエストに応じて適切なツールでデータを収集する
2. 収集したデータを分析し、異常や問題点を特定する
3. 問題が見つかった場合は、具体的な対処法を提示する

## レポート形式
調査結果は以下の形式で報告する:
- **概要**: 何を調査し、何が分かったか
- **詳細**: 具体的なデータや数値
- **推奨対処**: 問題がある場合の対処法
"""

    if _bigquery_enabled():
        return (
            """あなたはインフラ監視の専門エージェントです。
BigQueryに蓄積されたアプリケーションログの分析と、
Kubernetesクラスタの状態監視を担当します。

## ツールの使い分け
- **ログ分析**: BigQuery MCPツールでSQLクエリを実行し、ログを検索・集計する
- **クラスタ状態確認**: kubectlツール群を使用してPod・Node・イベントを確認する

## BigQueryクエリのルール
- 必ず LIMIT 句を付ける（最大1000行）
- SELECT * は避け、必要なカラムのみ指定する
- 大きなテーブルにはパーティションフィルタを使用する
"""
            + common_footer
        )

    # ローカル検証モード（BigQuery MCP無効）: kubectlツールのみを案内する
    return (
        """あなたはインフラ監視の専門エージェントです。
Kubernetesクラスタの状態監視を担当します。

## ツールの使い分け
- **クラスタ状態確認**: kubectlツール群を使用してPod・Node・イベントを確認する

ログ分析用のBigQuery MCPツールは現在無効です。ログ分析を求められた場合は、
ENABLE_BIGQUERY_MCP=1 で再起動が必要なことを伝え、kubectlで確認できる範囲を案内する。
"""
        + common_footer
    )


# インフラ監視エージェントの定義
root_agent = Agent(
    name="infra_monitor",
    model="gemini-3.5-flash",
    instruction=_build_instruction(),
    tools=_build_tools(),
)
