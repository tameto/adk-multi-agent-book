# oauth2_calendar.py
# 2-7-3. OAuth 2.0認証（完全版）
# OpenIdConnectWithConfigスキームとOAuth2Authクレデンシャルの組み合わせで、
# Google Calendarへのユーザー同意ベースのアクセスを実装する。
# 実行には環境変数 OAUTH_CLIENT_ID / OAUTH_CLIENT_SECRET の設定が必要。

import os

from google.adk.auth import AuthConfig
from google.adk.auth.auth_schemes import OpenIdConnectWithConfig
from google.adk.auth.auth_credential import (
    AuthCredential,
    AuthCredentialTypes,
    OAuth2Auth,
)
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext

# 認証スキーム（OAuth 2.0 / OpenID Connect）
auth_scheme = OpenIdConnectWithConfig(
    authorization_endpoint="https://accounts.google.com/o/oauth2/auth",
    token_endpoint="https://oauth2.googleapis.com/token",
    scopes=["https://www.googleapis.com/auth/calendar.readonly"],
)

def create_auth_credential() -> AuthCredential:
    """環境変数からOAuthクライアント認証情報を生成する"""
    client_id = os.environ.get("OAUTH_CLIENT_ID")
    client_secret = os.environ.get("OAUTH_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError(
            "OAUTH_CLIENT_ID と OAUTH_CLIENT_SECRET を設定してください"
        )

    return AuthCredential(
        auth_type=AuthCredentialTypes.OPEN_ID_CONNECT,
        oauth2=OAuth2Auth(
            client_id=client_id,
            client_secret=client_secret,
        ),
    )


def get_calendar_events(
    date: str,
    tool_context: ToolContext,
) -> dict:
    """Google Calendarから予定を取得する。

    Args:
        date: 日付（YYYY-MM-DD形式）

    Returns:
        予定のリスト、または認証要求レスポンス"""
    # 認証設定をバンドルする
    auth_config = AuthConfig(
        auth_scheme=auth_scheme,
        raw_auth_credential=create_auth_credential(),
    )

    # 既に認証済みか確認（ADKランタイムが自動で管理）
    exchanged = tool_context.get_auth_response(auth_config)
    if not exchanged:
        # 未認証: 認証フローをリクエストする
        tool_context.request_credential(auth_config)
        return {
            "status": "auth_required",
            "message": "Google Calendarへのアクセスを許可してください。",
        }

    # 認証済みトークンを使ってAPIを呼び出す
    import httpx
    access_token = exchanged.oauth2.access_token
    response = httpx.get(
        "https://www.googleapis.com/calendar/v3/calendars/primary/events",
        params={"timeMin": f"{date}T00:00:00Z", "timeMax": f"{date}T23:59:59Z"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    return response.json()


calendar_tool = FunctionTool(func=get_calendar_events)

if __name__ == "__main__":
    # 定義の確認（認証フローはADKランタイム経由で動作する）
    print(f"ツール名: {calendar_tool.name}")
    print(f"スコープ: {auth_scheme.scopes}")
