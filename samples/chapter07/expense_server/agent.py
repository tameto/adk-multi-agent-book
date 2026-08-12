# samples/chapter07/expense_server/agent.py
"""経費精算A2Aサーバーエージェント

A2Aサーバーとして動作し、経費データの登録・照会を行う。
ポート8001で起動する。

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
from google.adk.tools import request_input

try:
    from .tools import query_expenses, register_expense
except ImportError:
    current_dir = os.path.dirname(__file__)
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    sys.modules.pop("tools", None)
    from tools import query_expenses, register_expense

# 経費精算エージェントの定義
expense_agent = Agent(
    name="expense_agent",
    model="gemini-3.5-flash",
    instruction="""あなたは経費精算の専門エージェントです。
ユーザーの依頼に応じて、経費データの登録と照会を行います。

## できること
- 経費の登録（register_expense）: 日付・カテゴリ・金額・説明を受け取り登録する
- 経費の照会（query_expenses）: 対象期間を指定して一覧を取得する

## 注意事項
- 金額は日本円（整数）で処理する
- カテゴリは「交通費」「会議費」「消耗品費」「通信費」「その他」のいずれかを使用する
- 必要な情報（日付・カテゴリ・金額・説明）が不足している場合は、
  通常の文章で質問して完了せず、request_inputツールで不足項目を質問する
- request_inputを呼び出したら、そのターンでは登録処理を進めない
""",
    tools=[request_input, register_expense, query_expenses],
)

# ADK Web / adk run からも同じ業務エージェントを読み込めるようにする
root_agent = expense_agent

# Agent Card の定義（a2a-sdk 0.3.x 仕様に準拠）
AGENT_CARD = AgentCard(
    name="経費精算エージェント",
    description="経費データの登録と照会を行う専門エージェント",
    url="http://localhost:8001",  # トップレベル必須フィールド
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=["text"],
    default_output_modes=["text"],
    skills=[
        AgentSkill(
            id="register-expense",
            name="経費登録",
            description="日付・カテゴリ・金額・説明を受け取り、経費データをシステムに登録する",
            tags=["expense", "registration"],  # tags は必須
            examples=[
                "2026年7月10日の交通費1280円を登録してください",
                "2026年7月11日のランチ代2500円を会議費で登録して",
            ],
        ),
        AgentSkill(
            id="query-expenses",
            name="経費照会",
            description="指定した期間の経費一覧を取得する",
            tags=["expense", "query"],
            examples=[
                "先月の経費一覧を見せてください",
                "2025年7月の経費を照会して",
            ],
        ),
    ],
)

# ADKエージェントを A2Aサーバー対応の Starlette アプリに変換
# host / port は Agent Card の URL メタデータに反映される
app = to_a2a(
    expense_agent,
    host="0.0.0.0",
    port=8001,
    agent_card=AGENT_CARD,
)


def main() -> None:
    """A2Aサーバーを起動する"""
    print("[INFO] 経費精算A2Aサーバーを起動します: http://0.0.0.0:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)


if __name__ == "__main__":
    main()
