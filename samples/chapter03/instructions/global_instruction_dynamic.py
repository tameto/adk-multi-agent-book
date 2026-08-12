# samples/chapter03/instructions/global_instruction_dynamic.py
"""3-3-3 グローバルInstruction（動的・完全版）

グローバルInstructionは、GlobalInstructionPlugin に文字列リテラルまたは
callableを渡して定義できる。
"""
from google.adk import Agent
from google.adk.apps import App
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.plugins.global_instruction_plugin import GlobalInstructionPlugin

# サブエージェント: 注文管理（global_instruction.py と同じ定義）
order_agent = Agent(
    name="order_agent",
    model="gemini-3.5-flash",
    instruction="""注文に関する問い合わせに対応します。
- 注文状況の確認
- キャンセル処理
- 配送状況の追跡""",
)

# サブエージェント: 返品管理（global_instruction.py と同じ定義）
return_agent = Agent(
    name="return_agent",
    model="gemini-3.5-flash",
    instruction="""返品・交換に関する問い合わせに対応します。
- 返品条件の確認
- 返品手続きの案内
- 交換処理""",
)


def build_global_instruction(ctx: ReadonlyContext) -> str:
    """動的グローバルInstruction"""
    company_name = ctx.state.get("company_name", "ECストア")
    support_hours = ctx.state.get("support_hours", "9:00-18:00")

    return f"""## {company_name} 全エージェント共通ルール
- 営業時間: {support_hours}
- 応答は日本語で行う
- 回答には根拠を示す"""

root_agent = Agent(
    name="root_agent",
    model="gemini-3.5-flash",
    instruction="あなたは顧客サポートのコーディネーターです。問い合わせ内容に対応する担当エージェントに振り分けてください。",
    sub_agents=[order_agent, return_agent],
)

app = App(
    name="support_app_dynamic",
    root_agent=root_agent,
    plugins=[GlobalInstructionPlugin(global_instruction=build_global_instruction)],
)
