#!/bin/bash
# samples/chapter08/deploy/cloud_run/deploy_cloud_run.sh
# Cloud Runへのデプロイスクリプト（8-2-5節の完全版）
#
# 使い方:
#   export GOOGLE_CLOUD_PROJECT=your-project-id
#   export DATABASE_URL="postgresql+asyncpg://user:pass@host/db"
#   bash deploy_cloud_run.sh

set -euo pipefail

# --- 環境変数チェック ---
: "${GOOGLE_CLOUD_PROJECT:?環境変数 GOOGLE_CLOUD_PROJECT を設定してください}"
: "${DATABASE_URL:?環境変数 DATABASE_URL を設定してください}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-my-agent}"

echo "=== Cloud Run デプロイ ==="
echo "  Project: ${GOOGLE_CLOUD_PROJECT}"
echo "  Region:  ${REGION}"
echo "  Service: ${SERVICE_NAME}"
echo ""

# --- Cloud Runへのデプロイ ---
# --source . によりソースからビルド（Dockerfileを使用）してデプロイする
# 注: --allow-unauthenticated は検証用。本番ではIAM認証を構成すること
gcloud run deploy "${SERVICE_NAME}" \
  --source . \
  --region "${REGION}" \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT},DATABASE_URL=${DATABASE_URL}" \
  --allow-unauthenticated \
  --project "${GOOGLE_CLOUD_PROJECT}"

echo ""
echo "=== デプロイ完了 ==="
echo "Cloud Consoleで確認: https://console.cloud.google.com/run?project=${GOOGLE_CLOUD_PROJECT}"
