import os
from google.cloud import secretmanager


def get_secret(secret_id: str, project_id: str | None = None) -> str:
    """Secret Managerから認証情報を取得する"""
    if project_id is None:
        project_id = os.environ["GOOGLE_CLOUD_PROJECT"]

    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("utf-8")


def create_authenticated_tool(api_name: str) -> dict:
    """認証情報をSecret Managerから取得してツール設定を構成する"""
    api_key = get_secret(f"{api_name}-api-key")
    return {
        "api_key": api_key,
        "timeout": 30,
        "retry_count": 3,
    }
