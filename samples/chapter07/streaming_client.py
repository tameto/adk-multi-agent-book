# samples/chapter07/streaming_client.py
"""SSEストリーミングクライアント（7-4-1）

a2a.client.Client.send_message() は Agent Card の capabilities.streaming=true を
自動検出し、AsyncIterator でストリーミングイベントを返す。
TaskStatusUpdateEvent（状態変更）と TaskArtifactUpdateEvent（成果物）を
リアルタイムに受信して表示する。

実行前にストリーミング対応のA2Aサーバー（ポート8001）を起動しておくこと。
"""

import asyncio

from a2a.client import ClientFactory, create_text_message_object
from a2a.types import (
    Message,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatusUpdateEvent,
)


async def stream_task():
    """ストリーミングでタスクを実行する"""
    client = await ClientFactory.connect("http://localhost:8001")

    request = create_text_message_object(content="2025年7月の経費一覧を照会してください")

    async for event in client.send_message(request):
        # event は (Task, UpdateEvent | None) のタプル、または Message
        if isinstance(event, tuple):
            task, update = event
            if isinstance(update, TaskStatusUpdateEvent):
                print(f"[状態変更] {update.status.state}")
                if update.status.message:
                    for part in update.status.message.parts:
                        if hasattr(part.root, "text"):
                            print(f"  → {part.root.text}")
            elif isinstance(update, TaskArtifactUpdateEvent):
                artifact = update.artifact
                print(f"[成果物] {artifact.name or '無名'}")
                for part in artifact.parts:
                    if hasattr(part.root, "text"):
                        print(f"  → {part.root.text}")
        elif isinstance(event, Message):
            for part in event.parts:
                if hasattr(part.root, "text"):
                    print(f"[メッセージ] {part.root.text}")


if __name__ == "__main__":
    asyncio.run(stream_task())
