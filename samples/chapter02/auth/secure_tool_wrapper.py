# secure_tool_wrapper.py
# 2-7-6. 認証設計のベストプラクティス: 認証チェック付きツールラッパー（完全版）
# get_auth_response() / request_credential() の組をデコレータ（ツールラッパー）に
# 切り出し、認証チェックを複数ツールで共通化する。

from google.adk.auth import AuthConfig
from google.adk.auth.auth_schemes import AuthScheme
from google.adk.auth.auth_credential import AuthCredential
from google.adk.tools.tool_context import ToolContext


def secure_tool_wrapper(
    tool_func,
    required_scopes: list[str],
    auth_scheme: AuthScheme,
    auth_credential: AuthCredential,
):
    """認証チェック付きのツールラッパー。

    `tool_context.get_auth_response()` で既存トークンを確認し、
    未認証なら `request_credential()` で認証フローを起動する。"""
    def wrapper(*args, tool_context: ToolContext, **kwargs):
        auth_config = AuthConfig(
            auth_scheme=auth_scheme,
            raw_auth_credential=auth_credential,
        )

        # 既に認証済みか確認
        exchanged = tool_context.get_auth_response(auth_config)
        if not exchanged:
            # 未認証: 認証をリクエストする
            tool_context.request_credential(auth_config)
            return {
                "status": "auth_required",
                "error": "認証が必要です。ユーザー承認をお待ちください。",
            }

        # スコープの検証（auth_schemeで宣言したスコープと比較）
        granted_scopes = getattr(auth_scheme, "scopes", [])
        if not all(s in granted_scopes for s in required_scopes):
            return {
                "status": "error",
                "error": f"必要な権限がありません: {required_scopes}",
            }

        return tool_func(*args, tool_context=tool_context, **kwargs)

    return wrapper


# 使用例（補完: 紙面には未掲載）
#
# from google.adk.tools import FunctionTool
# from oauth2_calendar import auth_scheme, auth_credential, get_calendar_events
#
# # 認証チェック付きツールとしてラップしてからFunctionTool化する
# secured_get_calendar_events = secure_tool_wrapper(
#     tool_func=get_calendar_events,
#     required_scopes=["https://www.googleapis.com/auth/calendar.readonly"],
#     auth_scheme=auth_scheme,
#     auth_credential=auth_credential,
# )
# calendar_tool = FunctionTool(func=secured_get_calendar_events)

if __name__ == "__main__":
    # 定義の確認（ToolContextはADKランタイムが注入する）
    print("secure_tool_wrapper: 認証チェック付きツールラッパーを定義済み")
