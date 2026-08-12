# samples/chapter08/monitoring/dashboard_setup.py
"""Cloud Monitoring ダッシュボードの作成（8-6-7 完全版）

Python SDK（monitoring_dashboard_v1）でダッシュボードをプログラム的に作成する例。
宣言的に定義する場合の同等構成は同ディレクトリの dashboard.json を参照
（gcloud monitoring dashboards create --config-from-file=dashboard.json で適用できる）。
紙面で省略したエラー率ウィジェットの定義を含む完全版。
"""
import os
import sys

from google.cloud import monitoring_dashboard_v1


def create_agent_dashboard(project_id: str):
    """エージェント運用ダッシュボードを作成する"""
    client = monitoring_dashboard_v1.DashboardsServiceClient()

    dashboard = monitoring_dashboard_v1.Dashboard(
        display_name="Agent Operations Dashboard",
        grid_layout=monitoring_dashboard_v1.GridLayout(
            columns=2,
            widgets=[
                # リクエスト数ウィジェット
                monitoring_dashboard_v1.Widget(
                    title="Requests per Second",
                    xy_chart=monitoring_dashboard_v1.XyChart(
                        data_sets=[
                            monitoring_dashboard_v1.XyChart.DataSet(
                                time_series_query=monitoring_dashboard_v1.TimeSeriesQuery(
                                    time_series_filter=monitoring_dashboard_v1.TimeSeriesFilter(
                                        filter='metric.type="custom.googleapis.com/agent/request_count"',
                                    )
                                ),
                                plot_type=monitoring_dashboard_v1.XyChart.DataSet.PlotType.LINE,
                            )
                        ],
                    ),
                ),
                # エラー率ウィジェット
                monitoring_dashboard_v1.Widget(
                    title="Error Rate",
                    xy_chart=monitoring_dashboard_v1.XyChart(
                        data_sets=[
                            monitoring_dashboard_v1.XyChart.DataSet(
                                time_series_query=monitoring_dashboard_v1.TimeSeriesQuery(
                                    time_series_filter=monitoring_dashboard_v1.TimeSeriesFilter(
                                        filter='metric.type="custom.googleapis.com/agent/error_rate"',
                                    )
                                ),
                                plot_type=monitoring_dashboard_v1.XyChart.DataSet.PlotType.LINE,
                            )
                        ],
                    ),
                ),
            ],
        ),
    )

    result = client.create_dashboard(
        request={
            "parent": f"projects/{project_id}",
            "dashboard": dashboard,
        }
    )
    print(f"Dashboard created: {result.name}")


if __name__ == "__main__":
    # 実行例（紙面では省略。プロジェクトIDは環境変数から取得する）
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        print("環境変数 GOOGLE_CLOUD_PROJECT を設定してください。")
        sys.exit(2)

    create_agent_dashboard(project_id)
