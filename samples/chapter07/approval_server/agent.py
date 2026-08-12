# samples/chapter07/approval_server/agent.py
"""承認A2Aサーバーエージェント

A2Aサーバーとして動作し、経費精算の承認フローを管理する。
ポート8002で起動する。

ADKの to_a2a() ヘルパーを使い、ADKエージェントを
A2Aプロトコル対応の Starlette アプリに変換して uvicorn で公開する。

※ ADK v2.2.0 のA2A実装は experimental（@a2a_experimental）。
※ a2a-sdk 0.3.x では AgentCard.url はトップレベル必須フィールド。
"""

import os
import sys

import uvicorn
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

try:
    from .tools import check_approval_status, submit_approval
except ImportError:
    current_dir = os.path.dirname(__file__)
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    sys.modules.pop("tools", None)
    from tools import check_approval_status, submit_approval

# 承認エージェントの定義
approval_agent = Agent(
    name="approval_agent",
    model="gemini-3.5-flash",
    instruction="""あなたは経費精算の承認を管理する専門エージェントです。
経費の承認申請を受け付け、承認ルールに基づいて処理します。

## できること
- 承認申請の受付（submit_approval）: 経費IDと金額に基づいて承認フローを開始する
- 承認ステータスの確認（check_approval_status）: 承認IDで進捗を確認する

## 承認ルール
- 5,000円以下: 自動承認
- 5,001円〜50,000円: 上長承認が必要
- 50,001円以上: 部長承認が必要

## 注意事項
- 承認ルールは厳密に適用する
- 承認待ちの場合はその旨をユーザーに明確に伝える
""",
    tools=[submit_approval, check_approval_status],
)

# ADK Web / adk run からも同じ業務エージェントを読み込めるようにする
root_agent = approval_agent

# Agent Card の定義（a2a-sdk 0.3.x 仕様に準拠）
AGENT_CARD = AgentCard(
    name="承認エージェント",
    description="経費精算の承認フローを管理する専門エージェント",
    url="http://localhost:8002",  # トップレベル必須フィールド
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=["text"],
    default_output_modes=["text"],
    skills=[
        AgentSkill(
            id="submit-approval",
            name="承認申請",
            description="経費IDと金額を受け取り、承認ルールに基づいて承認フローを開始する",
            tags=["approval", "submit"],  # tags は必須
            examples=[
                "経費EXP-003の承認申請を出してください。金額は8500円です",
                "EXP-005（65000円）の承認をお願いします",
            ],
        ),
        AgentSkill(
            id="check-approval",
            name="承認ステータス確認",
            description="承認IDを指定して承認の進捗状況を確認する",
            tags=["approval", "status"],
            examples=[
                "承認APR-001のステータスを教えてください",
            ],
        ),
    ],
)

# ADKエージェントを A2Aサーバー対応の Starlette アプリに変換
app = to_a2a(
    approval_agent,
    host="0.0.0.0",
    port=8002,
    agent_card=AGENT_CARD,
)


def main() -> None:
    """A2Aサーバーを起動する"""
    print("[INFO] 承認A2Aサーバーを起動します: http://0.0.0.0:8002")
    uvicorn.run(app, host="0.0.0.0", port=8002)


if __name__ == "__main__":
    main()
