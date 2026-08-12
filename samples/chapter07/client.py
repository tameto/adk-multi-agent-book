# samples/chapter07/client.py
"""低レベルA2Aクライアントの基本的な呼び出し（7-2-2）

a2a-sdk の公式クライアント（a2a.client.Client）を直接使い、
経費精算A2Aサーバー（ポート8001）にメッセージを送信する。

実行前に expense_server を起動しておくこと:
    cd samples/chapter07 && python run_servers.py
"""

import asyncio

from a2a.client import ClientFactory, create_text_message_object
from a2a.types import TaskState


async def main() -> None:
    # Agent Card を自動取得して Client を生成（/.well-known/agent-card.json をGET）
    client = await ClientFactory.connect("http://localhost:8001")

    # Agent Cardの能力を確認
    card = await client.get_card()
    print(f"エージェント名: {card.name}")
    print(f"スキル: {[s.name for s in card.skills]}")

    # メッセージの送信（AsyncIterator が返る。ストリーミング/ポーリングは自動判定）
    request = create_text_message_object(
        content="2026年7月10日の交通費1280円を登録してください。品川から渋谷への電車代です。"
    )

    async for event in client.send_message(request):
        # event は (Task, Optional[UpdateEvent]) のタプル、または Message
        if isinstance(event, tuple):
            task, _update = event
            print(f"タスクID: {task.id}")
            print(f"状態: {task.status.state}")
            if task.status.state == TaskState.completed:
                for artifact in task.artifacts or []:
                    for part in artifact.parts:
                        if hasattr(part.root, "text"):
                            print(f"結果: {part.root.text}")


if __name__ == "__main__":
    asyncio.run(main())
