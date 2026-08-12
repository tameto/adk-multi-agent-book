# samples/chapter07/a2ui/relay_server.py
"""A2UI: WebSocket中継サーバー（7-4-3 ステータス表示パターン）

A2Aストリーミングの各イベントを transform_for_ui() でフロントエンド表示用の
JSON（status / result / message の3種）に変換し、WebSocketでユーザーに中継する。

実行前にA2Aサーバー（ポート8001）を起動しておくこと。
起動: python relay_server.py（ポート8080で待ち受け）
"""

import json

from fastapi import FastAPI, WebSocket
from a2a.client import ClientFactory, create_text_message_object
from a2a.types import Message, TaskArtifactUpdateEvent, TaskStatusUpdateEvent

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocketでA2Aストリーミングをユーザーに中継する"""
    await websocket.accept()

    # ユーザーからのメッセージを受信
    user_message = await websocket.receive_text()

    client = await ClientFactory.connect("http://localhost:8001")
    request = create_text_message_object(content=user_message)

    # A2Aストリーミングの各イベントをWebSocketで中継
    async for event in client.send_message(request):
        # イベントをUI表示用の形式に変換
        ui_event = transform_for_ui(event)
        if ui_event:
            await websocket.send_text(json.dumps(ui_event))

    await websocket.close()


def transform_for_ui(event) -> dict | None:
    """A2Aイベントをフロントエンド表示用に変換する"""
    if isinstance(event, tuple):
        _task, update = event
        if isinstance(update, TaskStatusUpdateEvent):
            message_text = ""
            if update.status.message:
                message_text = " ".join(
                    p.root.text for p in update.status.message.parts
                    if hasattr(p.root, "text")
                )
            return {
                "type": "status",
                "state": update.status.state.value,
                "message": message_text,
                "timestamp": update.status.timestamp,
            }
        elif isinstance(update, TaskArtifactUpdateEvent):
            artifact = update.artifact
            return {
                "type": "result",
                "name": artifact.name or "",
                "parts": [
                    p.root.model_dump() for p in artifact.parts
                ],
            }
    elif isinstance(event, Message):
        text = " ".join(
            p.root.text for p in event.parts if hasattr(p.root, "text")
        )
        return {
            "type": "message",
            "text": text,
        }

    return None


if __name__ == "__main__":
    import uvicorn

    # WebSocket中継サーバーをポート8080で起動
    uvicorn.run(app, host="0.0.0.0", port=8080)
