# samples/chapter08/monitoring/agent_alerts.py
"""エージェント層アラートの作成（8-6-5節の完全版）

Python SDK（monitoring_v3.AlertPolicyServiceClient）で、カスタムメトリクスを
閾値・持続時間付きで監視するAlertPolicyを作成する。
本文表8-12のエージェント層アラート（エラー率5%超、ツール呼び出し失敗率10%超）を
プログラム的に登録する。gcloud CLIで同等の設定を行う場合は、同ディレクトリの
setup_alerts.sh を参照。

使い方:
  export GOOGLE_CLOUD_PROJECT=your-project-id
  export NOTIFICATION_CHANNEL_ID=12345
  python agent_alerts.py
"""
import os
import sys

from google.cloud import monitoring_v3
from google.protobuf import duration_pb2


def _build_threshold_policy(
    display_name: str,
    condition_display_name: str,
    metric_type: str,
    threshold_value: float,
    channel: str,
    documentation: str,
    duration_seconds: int = 300,
) -> monitoring_v3.AlertPolicy:
    """カスタムメトリクスの閾値超過を監視するAlertPolicyを組み立てる"""
    condition = monitoring_v3.AlertPolicy.Condition(
        display_name=condition_display_name,
        condition_threshold=monitoring_v3.AlertPolicy.Condition.MetricThreshold(
            filter=f'metric.type="{metric_type}"',
            comparison=monitoring_v3.ComparisonType.COMPARISON_GT,
            threshold_value=threshold_value,
            # 持続時間: 一時的なスパイクをノイズとして除外する
            duration=duration_pb2.Duration(seconds=duration_seconds),
            aggregations=[
                monitoring_v3.Aggregation(
                    alignment_period=duration_pb2.Duration(
                        seconds=duration_seconds
                    ),
                    per_series_aligner=(
                        monitoring_v3.Aggregation.Aligner.ALIGN_MEAN
                    ),
                )
            ],
        ),
    )
    return monitoring_v3.AlertPolicy(
        display_name=display_name,
        combiner=monitoring_v3.AlertPolicy.ConditionCombinerType.OR,
        conditions=[condition],
        notification_channels=[channel],
        documentation=monitoring_v3.AlertPolicy.Documentation(
            content=documentation,
            mime_type="text/markdown",
        ),
    )


def create_agent_layer_alerts(
    project_id: str,
    notification_channel_id: str,
) -> list[str]:
    """エージェント層のアラートポリシーを作成し、作成したリソース名を返す"""
    client = monitoring_v3.AlertPolicyServiceClient()
    project_name = f"projects/{project_id}"
    channel = (
        f"projects/{project_id}/notificationChannels/{notification_channel_id}"
    )

    # 表8-12のエージェント層アラートに対応する2ポリシーを定義する
    policies = [
        _build_threshold_policy(
            display_name="Agent Engine - Error Rate > 5%",
            condition_display_name="Error Rate Threshold",
            metric_type="custom.googleapis.com/agent/error_rate",
            threshold_value=0.05,
            channel=channel,
            documentation=(
                "エージェントのエラー率が5%を超えました。ログを確認してください。"
            ),
        ),
        _build_threshold_policy(
            display_name="Agent Engine - Tool Failure Rate > 10%",
            condition_display_name="Tool Failure Rate Threshold",
            metric_type="custom.googleapis.com/agent/tool_failure_rate",
            threshold_value=0.10,
            channel=channel,
            documentation=(
                "ツール呼び出しの失敗率が10%を超えました。"
                "外部API断を確認してください。"
            ),
        ),
    ]

    created_names: list[str] = []
    for policy in policies:
        created = client.create_alert_policy(
            name=project_name,
            alert_policy=policy,
        )
        print(f"AlertPolicy created: {created.name}")
        created_names.append(created.name)

    return created_names


if __name__ == "__main__":
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    channel_id = os.environ.get("NOTIFICATION_CHANNEL_ID")
    if not project_id or not channel_id:
        print(
            "環境変数 GOOGLE_CLOUD_PROJECT と NOTIFICATION_CHANNEL_ID を"
            "設定してください。"
        )
        sys.exit(2)

    create_agent_layer_alerts(project_id, channel_id)
