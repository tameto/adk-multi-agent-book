# samples/chapter07/a2ui/dashboard.py
"""A2UI: マルチエージェントダッシュボード（7-4-3）

Hub-Spokeパターンで動作する複数のSpokeエージェントの状態を一元管理し、
状態変更をリアルタイムにUI層へ通知する。WebSocketやSSEを通じて
フロントエンドに配信することで、ユーザーがシステム全体を俯瞰できる。

実行前にA2Aサーバー（ポート8001・8002）を起動しておくこと。
"""

import asyncio
from dataclasses import dataclass


@dataclass
class AgentStatus:
    """各エージェントの状態を管理する"""
    name: str
    url: str
    state: str = "idle"
    last_message: str = ""
    task_id: str | None = None


class MultiAgentDashboard:
    """マルチエージェントの状態を集約するダッシュボード"""

    def __init__(self):
        self.agents: dict[str, AgentStatus] = {}
        self._callbacks: list = []

    def register_agent(self, name: str, url: str):
        """エージェントを登録する"""
        self.agents[name] = AgentStatus(name=name, url=url)

    def on_update(self, callback):
        """状態更新のコールバックを登録する"""
        self._callbacks.append(callback)

    async def _notify(self):
        """登録されたコールバックに状態更新を通知する"""
        status_list = [
            {
                "name": a.name,
                "state": a.state,
                "last_message": a.last_message,
            }
            for a in self.agents.values()
        ]
        for cb in self._callbacks:
            await cb(status_list)

    async def execute_on_agent(self, agent_name: str, message: str):
        """指定されたエージェントにタスクを送信し、ストリーミングで進捗を追跡する"""
        from a2a.client import ClientFactory, create_text_message_object
        from a2a.types import TaskState, TaskStatusUpdateEvent

        agent = self.agents[agent_name]
        client = await ClientFactory.connect(agent.url)

        agent.state = TaskState.working.value
        await self._notify()

        request = create_text_message_object(content=message)
        async for event in client.send_message(request):
            if isinstance(event, tuple):
                _task, update = event
                if isinstance(update, TaskStatusUpdateEvent):
                    agent.state = update.status.state.value
                    if update.status.message:
                        agent.last_message = " ".join(
                            p.root.text for p in update.status.message.parts
                            if hasattr(p.root, "text")
                        )
                    await self._notify()

        return agent.state


async def main() -> None:
    """ダッシュボードの動作確認（コンソール出力版の補完コード）"""
    dashboard = MultiAgentDashboard()
    dashboard.register_agent("expense_agent", "http://localhost:8001")
    dashboard.register_agent("approval_agent", "http://localhost:8002")

    async def print_status(status_list: list[dict[str, str]]) -> None:
        # 本番ではWebSocket/SSEでフロントエンドに配信する部分
        for status in status_list:
            print(f"  {status['name']}: {status['state']} {status['last_message']}")
        print("---")

    dashboard.on_update(print_status)

    final_state = await dashboard.execute_on_agent(
        "expense_agent", "2026年7月10日の交通費1280円を登録してください"
    )
    print(f"最終状態: {final_state}")


if __name__ == "__main__":
    asyncio.run(main())
