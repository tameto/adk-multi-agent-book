# samples/chapter07/push_notification.py
"""A2A Push Notification対応の実装例（7-5-4 完全版）

クライアント側で `set_task_callback()` によりWebhook URLを登録し、
サーバーからのタスク状態変更通知をFastAPIのWebhookエンドポイントで受信する。
紙面で省略した state ごとの分岐処理を含む完全版。
"""
import os
from a2a.client import Client
from a2a.types import (
    PushNotificationAuthenticationInfo,
    PushNotificationConfig,
    TaskPushNotificationConfig,
)

# Push Notificationの設定
async def setup_push_notification(
    client: Client,
    task_id: str,
    webhook_url: str,
    webhook_secret: str,
):
    """タスクのPush Notificationを設定する"""
    config = TaskPushNotificationConfig(
        task_id=task_id,
        push_notification_config=PushNotificationConfig(
            url=webhook_url,
            authentication=PushNotificationAuthenticationInfo(
                schemes=["Bearer"],
                credentials=webhook_secret,  # 本番は Secret Manager から取得
            ),
        ),
    )
    await client.set_task_callback(config)

# Webhookエンドポイント（FastAPIの例）
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()


def get_webhook_secret() -> str:
    """Webhook検証用シークレットを環境変数から取得する"""
    secret = os.environ.get("A2A_WEBHOOK_SECRET")
    if not secret:
        raise RuntimeError("A2A_WEBHOOK_SECRET を設定してください")
    return secret

@app.post("/webhook/a2a-notification")
async def handle_notification(request: Request):
    """A2A Push Notificationを受信する"""
    webhook_secret = get_webhook_secret()

    # 認証トークンの検証（不正なら401を返す。タプル返却はFastAPIでは
    # ステータス200のままJSON化されるため、JSONResponseを明示する）
    auth_header = request.headers.get("Authorization", "")
    if auth_header != f"Bearer {webhook_secret}":
        return JSONResponse(
            status_code=401, content={"error": "Unauthorized"}
        )

    body = await request.json()
    task_id = body.get("id")
    state = body.get("status", {}).get("state")

    print(f"通知受信: タスク {task_id} が {state} に変更されました")

    # 状態に応じた処理（TaskState enum の文字列値と一致）
    if state == "completed":
        pass
    elif state == "failed":
        pass
    elif state == "input-required":
        pass

    return {"status": "received"}
