# service_account_bigquery.py
# 2-7-4. Service Account認証（完全版）
# Google Cloud環境ではApplication Default Credentials（ADC）により
# Service Accountの認証情報が自動的に注入される。
# ローカル開発では `gcloud auth application-default login` でADCを設定する。
# 依存パッケージ: google-cloud-bigquery

import os

from google.adk.tools import FunctionTool
from google.cloud import bigquery


def query_bigquery(
    sql: str,
) -> dict:
    """BigQueryでSQLクエリを実行する。

    Args:
        sql: 実行するSQLクエリ

    Returns:
        クエリ結果"""
    # Application Default Credentials（ADC）を使用
    # GCP環境ではService Accountが自動的に使用される
    client = bigquery.Client(project=os.environ["GOOGLE_CLOUD_PROJECT"])

    query_job = client.query(sql)
    results = query_job.result()

    rows = [dict(row) for row in results]
    return {"status": "success", "row_count": len(rows), "rows": rows[:100]}


bigquery_tool = FunctionTool(func=query_bigquery)

if __name__ == "__main__":
    # 定義の確認（実行には環境変数 GOOGLE_CLOUD_PROJECT とADCの設定が必要）
    print(f"ツール名: {bigquery_tool.name}")
