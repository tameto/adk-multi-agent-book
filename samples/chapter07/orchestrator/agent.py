# samples/chapter07/orchestrator/agent.py
"""オーケストレーターエージェント（A2Aクライアント）

Hub-Spokeパターンのオーケストレーター。
ADK v2.2.0の RemoteA2aAgent を使い、A2Aサーバーとして動作する
経費精算エージェントと承認エージェントにリクエストを委譲する。
"""

from google.adk import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools import AgentTool

# A2Aサーバーのエンドポイント
EXPENSE_SERVER_URL = "http://localhost:8001"
APPROVAL_SERVER_URL = "http://localhost:8002"

# RemoteA2aAgent: A2Aサーバーをサブエージェントとして統合
# agent_card にURL文字列を渡すと、A2ACardResolver が自動的に Agent Card を取得する
expense_remote_agent = RemoteA2aAgent(
    name="expense_agent",
    description="経費データの登録と照会を行う専門エージェント。"
    "経費の登録（日付・カテゴリ・金額・説明）や経費一覧の照会（期間指定）を処理する。",
    agent_card=f"{EXPENSE_SERVER_URL}/.well-known/agent-card.json",
)

approval_remote_agent = RemoteA2aAgent(
    name="approval_agent",
    description="経費精算の承認フローを管理する専門エージェント。"
    "承認申請の受付（経費ID・金額・理由）や承認ステータスの確認を処理する。",
    agent_card=f"{APPROVAL_SERVER_URL}/.well-known/agent-card.json",
)

# オーケストレーターエージェントの定義
root_agent = Agent(
    name="orchestrator",
    model="gemini-3.5-flash",
    instruction="""あなたは経費精算システムのオーケストレーターエージェントです。
ユーザーのリクエストを適切な専門エージェントに委譲して処理します。

## 専門エージェント
1. **expense_agent**（経費精算エージェントツール）:
   - 経費の登録（日付・カテゴリ・金額・説明）
   - 経費一覧の照会（期間指定）

2. **approval_agent**（承認エージェントツール）:
   - 承認申請の受付（経費ID・金額・理由）
   - 承認ステータスの確認

## 判断基準
- 経費の登録・照会に関するリクエスト → expense_agent を呼び出す
- 承認申請・承認状況に関するリクエスト → approval_agent を呼び出す
- 「登録して承認申請も出して」のような複合リクエストの場合:
  1. まず expense_agent で経費を登録する
  2. 登録結果から経費IDと金額を取得する
  3. 取得した経費ID・金額・理由を使って approval_agent で承認申請を出す
  4. expense_agent と approval_agent の両方の結果を確認してから最終回答する

## 注意事項
- 各エージェントの応答をユーザーにわかりやすく要約して伝える
- エラーが発生した場合は、具体的な対処法とともにユーザーに伝える
""",
    # 複合リクエストでは、1ターン内で複数のリモートA2Aエージェントを
    # 順番に呼び出せるよう AgentTool として公開する。
    tools=[
        AgentTool(agent=expense_remote_agent),
        AgentTool(agent=approval_remote_agent),
    ],
)
