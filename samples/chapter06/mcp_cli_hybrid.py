# samples/chapter06/mcp_cli_hybrid.py
"""MCP + CLIハイブリッドエージェントの実装例"""

import os
import subprocess

from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters


# MCP: BigQueryへの構造化接続（MCP Toolbox経由）
bigquery_server = StdioConnectionParams(
    server_params=StdioServerParameters(
        command="npx",
        args=["-y", "@toolbox-sdk/server", "--stdio", "--config", "tools.yaml"],
        env={"GOOGLE_CLOUD_PROJECT": os.environ.get("GCP_PROJECT_ID", "my-project")},
    )
)


# CLI: 社内独自の分析レポートツール
def generate_report(query_result: str, report_type: str = "summary") -> dict:
    """社内レポートツールで分析レポートを生成する

    Args:
        query_result: BigQueryクエリの実行結果（JSON文字列）
        report_type: レポートタイプ（summary / detailed / executive）

    Returns:
        生成されたレポートの内容"""
    cmd = [
        "internal-report-tool",
        "--type", report_type,
        "--format", "markdown",
    ]

    try:
        result = subprocess.run(
            cmd,
            input=query_result,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            return {"report": result.stdout}
        return {"error": result.stderr}
    except subprocess.TimeoutExpired:
        return {"error": "レポート生成がタイムアウトしました"}
    except FileNotFoundError:
        return {"error": "internal-report-toolがインストールされていません"}


# CLI: データの可視化ツール
def create_chart(data_json: str, chart_type: str, title: str) -> dict:
    """データをチャートとして可視化する

    Args:
        data_json: 可視化するデータ（JSON文字列）
        chart_type: チャートタイプ（bar / line / pie / scatter）
        title: チャートのタイトル

    Returns:
        生成されたチャートファイルのパス"""
    allowed_chart_types = {"bar", "line", "pie", "scatter"}
    if chart_type not in allowed_chart_types:
        return {"error": f"不正なチャートタイプです。利用可能: {allowed_chart_types}"}

    cmd = [
        "chart-gen",
        "--type", chart_type,
        "--title", title,
        "--output", "/tmp/chart_output.png",
    ]

    try:
        result = subprocess.run(
            cmd,
            input=data_json,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return {"chart_path": "/tmp/chart_output.png", "message": "チャートを生成しました"}
        return {"error": result.stderr}
    except subprocess.TimeoutExpired:
        return {"error": "チャート生成がタイムアウトしました"}
    except FileNotFoundError:
        return {"error": "chart-genがインストールされていません"}


# ハイブリッドエージェント
hybrid_analyst = Agent(
    name="hybrid_analyst",
    model="gemini-3.5-flash",
    instruction="""あなたはデータ分析の専門家です。
    BigQuery（MCPサーバー経由）でデータを取得し、社内ツール（CLI）で分析レポートやチャートを生成します。

    ## ワークフロー
    1. BigQueryでデータを取得
    2. 必要に応じてレポートを生成（generate_report）
    3. 必要に応じてチャートを作成（create_chart）

    ## ツール使い分け
    - データ取得・SQL実行: BigQuery MCPツールを使用
    - レポート生成・可視化: CLI ツールを使用""",
    tools=[
        McpToolset(connection_params=bigquery_server),  # MCP
        generate_report,  # CLI
        create_chart,     # CLI
    ],
)
