# samples/chapter07/auth/oauth2_client.py
"""OAuth2認証付きA2Aクライアント（7-5-2 クライアント側）

a2a-sdk の AuthInterceptor と InMemoryContextCredentialStore を組み合わせ、
ClientFactory に認証情報を注入する。Bearer トークンは ClientCallContext 経由で
動的に渡す。401応答時はトークンを再取得して再試行する。

認証情報は環境変数から取得する（コードへの直書き禁止）:
    OAUTH2_TOKEN_URL / OAUTH2_CLIENT_ID / OAUTH2_CLIENT_SECRET / OAUTH2_SCOPES
"""

import asyncio
import os

import httpx
from a2a.client import (
    AuthInterceptor,
    ClientCallContext,
    ClientFactory,
    InMemoryContextCredentialStore,
    create_text_message_object,
)


class OAuth2A2aClient:
    """OAuth2認証付きA2Aクライアント"""

    def __init__(
        self,
        url: str,
        token_url: str,
        client_id: str,
        client_secret: str,
        scopes: list[str],
        session_id: str = "default",
        scheme_name: str = "bearerAuth",
    ):
        self.url = url
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = scopes
        self.session_id = session_id
        self.scheme_name = scheme_name
        self._store = InMemoryContextCredentialStore()
        self._client = None

    async def _fetch_token(self) -> str:
        """OAuth2トークンを取得する"""
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                self.token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "scope": " ".join(self.scopes),
                },
            )
            response.raise_for_status()
            return response.json()["access_token"]

    async def _ensure_client(self):
        """初回呼び出し時に Client を遅延生成する"""
        if self._client is None:
            token = await self._fetch_token()
            await self._store.set_credentials(
                session_id=self.session_id,
                security_scheme_name=self.scheme_name,
                credential=token,
            )
            self._client = await ClientFactory.connect(
                self.url,
                interceptors=[AuthInterceptor(credential_service=self._store)],
            )
        return self._client

    async def send_message(self, text: str):
        """認証付きでメッセージを送信し、各イベントを yield する"""
        client = await self._ensure_client()
        request = create_text_message_object(content=text)
        context = ClientCallContext(state={"sessionId": self.session_id})
        try:
            async for event in client.send_message(request, context=context):
                yield event
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                # トークンが期限切れの場合、再取得して再試行
                token = await self._fetch_token()
                await self._store.set_credentials(
                    session_id=self.session_id,
                    security_scheme_name=self.scheme_name,
                    credential=token,
                )
                async for event in client.send_message(request, context=context):
                    yield event
            else:
                raise


async def main() -> None:
    """OAuth2認証付きクライアントの動作確認（補完コード）"""
    # 認証情報は環境変数から取得する
    required_env = [
        "OAUTH2_TOKEN_URL",
        "OAUTH2_CLIENT_ID",
        "OAUTH2_CLIENT_SECRET",
    ]
    missing = [name for name in required_env if not os.environ.get(name)]
    if missing:
        print(
            "OAuth2クライアントの実行には環境変数が必要です: "
            + ", ".join(missing)
        )
        print(
            "例: OAUTH2_TOKEN_URL, OAUTH2_CLIENT_ID, "
            "OAUTH2_CLIENT_SECRET を設定してから再実行してください。"
        )
        return

    client = OAuth2A2aClient(
        url=os.environ.get("A2A_SERVER_URL", "http://localhost:8001"),
        token_url=os.environ["OAUTH2_TOKEN_URL"],
        client_id=os.environ["OAUTH2_CLIENT_ID"],
        client_secret=os.environ["OAUTH2_CLIENT_SECRET"],
        scopes=os.environ.get("OAUTH2_SCOPES", "expense:read expense:write").split(),
        # スキーム名はサーバー側 Agent Card の security_schemes の定義と一致させる
        scheme_name="oauth2",
    )

    async for event in client.send_message("2026年7月10日の交通費1280円を登録してください"):
        if isinstance(event, tuple):
            task, _update = event
            print(f"タスクID: {task.id} / 状態: {task.status.state}")


if __name__ == "__main__":
    asyncio.run(main())
