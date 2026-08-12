# samples/chapter07/patterns/stage3_server.py
"""3台目のA2Aサーバー（レポート生成・ポート8003）

hub_spoke.py と pipeline.py は8001〜8003の3台構成を前提にしている。
run_servers.py が起動するのは8001（経費精算）と8002（承認）の2台のため、
このサーバーを別ターミナルで起動して3台構成を作る。

実行方法:
    python patterns/stage3_server.py
"""

import uvicorn
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# レポート生成エージェント
report_agent = Agent(
    name="report_agent",
    model="gemini-3.5-flash",
    instruction=(
        "あなたはレポート生成の専門エージェントです。"
        "渡された分析結果から、簡潔なレポート文書を作成してください。"
        "レポートは200文字以内にまとめてください。"
    ),
)

# Agent Card（a2a-sdk 0.3.x仕様。urlとAgentSkill.tagsは必須）
AGENT_CARD = AgentCard(
    name="レポート生成エージェント",
    description="分析結果からレポート文書を生成する専門エージェント",
    url="http://localhost:8003",
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=["text"],
    default_output_modes=["text"],
    skills=[
        AgentSkill(
            id="generate-report",
            name="レポート生成",
            description="分析結果を受け取り、レポート文書を生成する",
            tags=["report", "generation"],
        )
    ],
)

# ADKエージェントをA2Aサーバー（Starletteアプリ）に変換
app = to_a2a(report_agent, host="0.0.0.0", port=8003, agent_card=AGENT_CARD)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
