# agent_tool_experts.py
# 2-6-3. AgentTool: エージェントをツールとして利用（完全版）
# 専門家エージェントをAgentToolでツール化し、メインエージェントから呼び出す。
# sub_agents（制御の委譲）と異なり、呼び出し元に結果が返る。

from google.adk import Agent
from google.adk.tools import AgentTool

# 専門家エージェント: 税務計算
tax_calculator = Agent(
    name="tax_calculator",
    model="gemini-3.5-flash",
    instruction="""あなたは税務計算の専門家です。
与えられた金額と条件に基づいて、正確な税額を計算してください。
消費税、所得税、住民税の計算に対応しています。""",
)

# 専門家エージェント: 法務相談
legal_advisor = Agent(
    name="legal_advisor",
    model="gemini-3.5-flash",
    instruction="""あなたは法務アドバイザーです。
契約条件、利用規約、法的リスクについてアドバイスしてください。""",
)

# メインエージェント: 必要に応じて専門家をツールとして呼び出す
main_agent = Agent(
    name="business_consultant",
    model="gemini-3.5-flash",
    instruction="""あなたはビジネスコンサルタントです。
税務に関する質問にはtax_calculatorツールを、法務に関する質問にはlegal_advisorツールを使用してください。""",
    tools=[
        AgentTool(agent=tax_calculator),
        AgentTool(agent=legal_advisor),
    ],
)

# adk run / adk web から参照できるようroot_agentとして公開する（補完）
root_agent = main_agent

if __name__ == "__main__":
    # 定義内容の確認（対話実行は adk run / adk web を使用）
    print(f"メインエージェント: {main_agent.name}")
    print(f"専門家ツール: {tax_calculator.name} / {legal_advisor.name}")
