#!/bin/bash
# samples/chapter08/deploy/deploy.sh
# Agent Engineへのデプロイスクリプト
#
# 使い方:
#   export GOOGLE_CLOUD_PROJECT=your-project-id
#   export GOOGLE_CLOUD_LOCATION=us-central1
#   bash deploy.sh

set -euo pipefail

# --- 環境変数チェック ---
: "${GOOGLE_CLOUD_PROJECT:?環境変数 GOOGLE_CLOUD_PROJECT を設定してください}"
: "${GOOGLE_CLOUD_LOCATION:=us-central1}"

AGENT_DIR="$(cd "$(dirname "$0")/../support_agent" && pwd)"
DISPLAY_NAME="${DISPLAY_NAME:-customer-support-agent}"

echo "=== Agent Engine デプロイ ==="
echo "  Project:  ${GOOGLE_CLOUD_PROJECT}"
echo "  Region:   ${GOOGLE_CLOUD_LOCATION}"
echo "  Agent:    ${AGENT_DIR}"
echo "  Name:     ${DISPLAY_NAME}"
echo ""

# --- 前提条件の確認 ---
echo "1. APIの有効化を確認中..."
gcloud services enable \
  aiplatform.googleapis.com \
  storage.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
  telemetry.googleapis.com \
  cloudtrace.googleapis.com \
  cloudresourcemanager.googleapis.com \
  secretmanager.googleapis.com \
  --project="${GOOGLE_CLOUD_PROJECT}" \
  --quiet

# --- デプロイ実行 ---
echo "2. Agent Engineにデプロイ中..."
adk deploy agent_engine "${AGENT_DIR}" \
  --project "${GOOGLE_CLOUD_PROJECT}" \
  --region "${GOOGLE_CLOUD_LOCATION}" \
  --display_name "${DISPLAY_NAME}" \
  --otel_to_cloud

echo ""
echo "=== デプロイ完了 ==="
echo "Cloud Consoleで確認: https://console.cloud.google.com/vertex-ai/agents?project=${GOOGLE_CLOUD_PROJECT}"
