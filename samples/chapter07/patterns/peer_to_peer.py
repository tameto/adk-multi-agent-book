# samples/chapter07/patterns/peer_to_peer.py
"""Peer-to-Peerパターン（7-3-3）

中央のオーケストレーターを介さず、エージェント同士が直接通信する構成。
このエージェント（data_processor）はA2Aサーバーとして公開されつつ、
他のA2Aエージェント（validation / notification）を RemoteA2aAgent 経由で呼び出す。

実行前に validation_agent（ポート8002）と notification_agent（ポート8003）を
起動しておくこと。
"""

import uvicorn
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from google.adk import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools import AgentTool

# 他のエージェントを RemoteA2aAgent で統合
validator_remote = RemoteA2aAgent(
    name="validation_agent",
    description="データの妥当性を検証する",
    agent_card="http://localhost:8002/.well-known/agent-card.json",
)

notifier_remote = RemoteA2aAgent(
    name="notification_agent",
    description="通知を送信する",
    agent_card="http://localhost:8003/.well-known/agent-card.json",
)

# データ処理エージェント（A2Aサーバーかつ他のA2Aを呼び出す）
data_processor = Agent(
    name="data_processor",
    model="gemini-3.5-flash",
    instruction="""あなたはデータ処理エージェントです。

受け取ったデータを処理します。処理の過程で:
1. validation_agent でデータの妥当性を検証してください
2. 処理完了後、notification_agent で結果を通知してください""",
    tools=[
        AgentTool(agent=validator_remote),
        AgentTool(agent=notifier_remote),
    ],
)

# このエージェント自体もA2Aサーバーとして公開
agent_card = AgentCard(
    name="data-processor",
    description="データの処理・変換を行うエージェント",
    url="http://localhost:8001",
    version="1.0.0",
    # streaming=Falseだと単一POSTで多段委譲の完了を待つため
    # a2a-sdk既定タイムアウトを超えやすい。SSEで逐次返すTrueにする
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=["text"],
    default_output_modes=["text"],
    skills=[
        AgentSkill(
            id="process-data",
            name="データ処理",
            description="構造化データの処理と変換を行う",
            tags=["data", "processing"],
        )
    ],
)

app = to_a2a(data_processor, host="0.0.0.0", port=8001, agent_card=agent_card)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
