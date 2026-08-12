# samples/chapter03/instructions/global_instruction.py
"""3-3-3 グローバルInstruction（静的・完全版）

同じアプリケーション内の Agent に共通ルールとして渡されるInstruction。
ADK v2.2.0では GlobalInstructionPlugin を App に登録して設定する。
"""
from google.adk import Agent
from google.adk.apps import App
from google.adk.plugins.global_instruction_plugin import GlobalInstructionPlugin

# サブエージェント: 注文管理
order_agent = Agent(
    name="order_agent",
    model="gemini-3.5-flash",
    instruction="""注文に関する問い合わせに対応します。
- 注文状況の確認
- キャンセル処理
- 配送状況の追跡""",
)

# サブエージェント: 返品管理
return_agent = Agent(
    name="return_agent",
    model="gemini-3.5-flash",
    instruction="""返品・交換に関する問い合わせに対応します。
- 返品条件の確認
- 返品手続きの案内
- 交換処理""",
)

# ルートエージェント: 業務固有のルーティングInstructionだけを持つ
root_agent = Agent(
    name="root_agent",
    model="gemini-3.5-flash",
    instruction="あなたは顧客サポートのコーディネーターです。問い合わせ内容に対応する担当エージェントに振り分けてください。",
    sub_agents=[order_agent, return_agent],
)

# グローバルInstructionはAppレベルのPluginで全エージェントに適用する
app = App(
    name="support_app",
    root_agent=root_agent,
    plugins=[
        GlobalInstructionPlugin(
            global_instruction="""## 全エージェント共通ルール
- 応答は日本語で行う
- 個人情報の取り扱いに最大限注意する
- 不明点はエスカレーションする
- 回答には必ず根拠を示す
- 攻撃的な言葉遣いをしない"""
        )
    ],
)
