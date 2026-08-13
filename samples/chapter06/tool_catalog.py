# samples/chapter06/tool_catalog.py
"""ツールカタログの定義例"""

TOOL_CATALOG = {
    "bigquery": {
        "type": "mcp",
        "package": "@toolbox-sdk/server",
        "config": "tools.yaml",
        "description": "BigQueryへのクエリ実行・スキーマ参照",
        "required_iam_roles": ["roles/bigquery.dataViewer"],
        "risk_level": "medium",  # データ参照可能
        "approval_required": False,
    },
    "cloudsql": {
        "type": "mcp",
        "package": "@toolbox-sdk/server",
        "config": "tools-cloudsql.yaml",
        "description": "Cloud SQL（PostgreSQL/MySQL）への接続",
        "required_iam_roles": ["roles/cloudsql.viewer"],
        "risk_level": "high",  # 本番DBへのアクセス
        "approval_required": True,
    },
    "gcloud": {
        "type": "cli",
        "command": "gcloud",
        "description": "Google Cloudリソースの管理",
        "required_permissions": ["gcloud CLI認証済み"],
        "risk_level": "high",
        "approval_required": True,
    },
    "kubectl": {
        "type": "cli",
        "command": "kubectl",
        "description": "Kubernetesクラスタの操作",
        "required_permissions": ["kubeconfig設定済み"],
        "risk_level": "high",
        "approval_required": True,
    },
}
