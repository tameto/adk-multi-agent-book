# samples/chapter08/monitoring/incident_response.py
"""インシデント調査スクリプト（8-6-6節の完全版）

エージェントのエラー率が急上昇したインシデントの初動調査を行う。
1. Cloud Loggingからエラーログを収集し、error_type別に件数を集計する
2. Cloud Traceから異常に遅いトレース（30秒超）を抽出する

使い方:
  export GOOGLE_CLOUD_PROJECT=your-project-id
  python incident_response.py
"""
import os
import sys
from datetime import datetime, timedelta, timezone

from google.cloud import logging as cloud_logging
from google.cloud import trace_v1


def investigate_error_spike(
    project_id: str,
    start_time: datetime,
    end_time: datetime,
) -> None:
    """エラースパイクの調査"""
    # 1. エラーログの収集
    logging_client = cloud_logging.Client(project=project_id)

    print("=== エラーログの分析 ===")
    error_entries = logging_client.list_entries(
        filter_=(
            f'severity >= ERROR '
            f'AND timestamp >= "{start_time.isoformat()}" '
            f'AND timestamp <= "{end_time.isoformat()}"'
        ),
        order_by=cloud_logging.DESCENDING,
        max_results=100,
    )

    # error_type別に件数を集計する
    error_counts: dict[str, int] = {}
    for entry in error_entries:
        error_type = getattr(entry.payload, "get", lambda k, d: d)(
            "error_type", "unknown"
        )
        error_counts[error_type] = error_counts.get(error_type, 0) + 1

    # 件数の多い順に表示する
    for error_type, count in sorted(
        error_counts.items(), key=lambda x: x[1], reverse=True
    ):
        print(f"  {error_type}: {count}件")

    # 2. トレースの確認
    print("\n=== 失敗トレースの分析 ===")
    trace_client = trace_v1.TraceServiceClient()
    traces = trace_client.list_traces(
        request={
            "project_id": project_id,
            "filter": 'root:"/reasoningEngines/"',
            "start_time": start_time,
            "end_time": end_time,
        }
    )

    # 所要時間が30秒を超えるスパンを抽出する
    slow_traces: list[dict] = []
    for t in traces:
        # 異常に遅いトレースを収集
        for span in t.spans:
            duration = span.end_time - span.start_time
            if duration.total_seconds() > 30:
                slow_traces.append(
                    {
                        "trace_id": t.trace_id,
                        "span": span.name,
                        "duration": duration.total_seconds(),
                    }
                )

    # 上位10件を表示する
    for st in slow_traces[:10]:
        print(
            f"  Trace: {st['trace_id']}, "
            f"Span: {st['span']}, "
            f"Duration: {st['duration']:.1f}s"
        )


if __name__ == "__main__":
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        print("環境変数 GOOGLE_CLOUD_PROJECT を設定してください。")
        sys.exit(2)

    # 調査の実行（直近1時間を対象とする）
    investigate_error_spike(
        project_id=project_id,
        start_time=datetime.now(timezone.utc) - timedelta(hours=1),
        end_time=datetime.now(timezone.utc),
    )
