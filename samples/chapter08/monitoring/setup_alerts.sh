#!/bin/bash
# samples/chapter08/monitoring/setup_alerts.sh
# Cloud Monitoringのアラート設定スクリプト
#
# 使い方:
#   export GOOGLE_CLOUD_PROJECT=your-project-id
#   export NOTIFICATION_CHANNEL_ID=12345
#   bash setup_alerts.sh

set -euo pipefail

: "${GOOGLE_CLOUD_PROJECT:?環境変数 GOOGLE_CLOUD_PROJECT を設定してください}"
: "${NOTIFICATION_CHANNEL_ID:?環境変数 NOTIFICATION_CHANNEL_ID を設定してください}"

CHANNEL="projects/${GOOGLE_CLOUD_PROJECT}/notificationChannels/${NOTIFICATION_CHANNEL_ID}"

echo "=== Cloud Monitoring アラート設定 ==="
echo "  Project: ${GOOGLE_CLOUD_PROJECT}"
echo ""

# --- 1. レイテンシアラート ---
echo "1. レイテンシアラートを作成中..."
gcloud alpha monitoring policies create \
  --project="${GOOGLE_CLOUD_PROJECT}" \
  --display-name="Agent Engine - P99 Latency > 30s" \
  --condition-display-name="P99 Latency Threshold" \
  --condition-filter='resource.type="aiplatform.googleapis.com/ReasoningEngine" AND metric.type="aiplatform.googleapis.com/reasoning_engine/request_latencies"' \
  --condition-threshold-value=30000 \
  --condition-threshold-comparison=COMPARISON_GT \
  --condition-threshold-duration="300s" \
  --notification-channels="${CHANNEL}" \
  --documentation="Agent EngineのP99レイテンシが30秒を超えました。トレースを確認してください。" \
  --quiet 2>/dev/null || echo "  (既に存在するか、権限不足です)"

# --- 2. エラーレートアラート ---
echo "2. エラーレートアラートを作成中..."
gcloud alpha monitoring policies create \
  --project="${GOOGLE_CLOUD_PROJECT}" \
  --display-name="Agent Engine - Error Rate > 5%" \
  --condition-display-name="Error Rate Threshold" \
  --condition-filter='metric.type="custom.googleapis.com/agent/error_rate"' \
  --condition-threshold-value=0.05 \
  --condition-threshold-comparison=COMPARISON_GT \
  --condition-threshold-duration="300s" \
  --notification-channels="${CHANNEL}" \
  --documentation="エージェントのエラー率が5%を超えました。ログを確認してください。" \
  --quiet 2>/dev/null || echo "  (既に存在するか、権限不足です)"

# --- 3. エスカレーション数アラート ---
echo "3. エスカレーション数のログベースメトリクスを作成中..."
gcloud logging metrics create agent_escalation_count \
  --project="${GOOGLE_CLOUD_PROJECT}" \
  --description="エージェントのエスカレーション発生回数" \
  --log-filter='jsonPayload.event="escalation"' \
  --quiet 2>/dev/null || echo "  (既に存在します)"

echo ""
echo "=== アラート設定完了 ==="
echo "Cloud Consoleで確認: https://console.cloud.google.com/monitoring/alerting?project=${GOOGLE_CLOUD_PROJECT}"
