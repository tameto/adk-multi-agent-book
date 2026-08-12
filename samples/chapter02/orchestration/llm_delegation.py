# llm_delegation.py
# 2-4-4. Agent委譲（sub_agents）: LLMによる動的選択（完全版）
# 各サブエージェントのdescriptionがLLMの委譲判断の根拠になる。

from google.adk import Agent

sales_agent = Agent(
    name="sales_agent",
    model="gemini-3.5-flash",
    description="商品の購入、注文状況の確認、配送に関する問い合わせに対応する",
    # instructionは紙面では "..." と省略。以下は補完した例
    instruction="""あなたは販売担当エージェントです。
商品の購入、注文状況の確認、配送に関する問い合わせに丁寧に対応してください。""",
)

technical_agent = Agent(
    name="technical_agent",
    model="gemini-3.5-flash",
    description="製品の技術的な問題、設定方法、トラブルシューティングに対応する",
    # instructionは紙面では "..." と省略。以下は補完した例
    instruction="""あなたは技術サポートエージェントです。
製品の技術的な問題、設定方法、トラブルシューティングを順序立てて案内してください。""",
)

billing_agent = Agent(
    name="billing_agent",
    model="gemini-3.5-flash",
    description="請求、支払い、返金、プランの変更に関する問い合わせに対応する",
    # instructionは紙面では "..." と省略。以下は補完した例
    instruction="""あなたは請求担当エージェントです。
請求、支払い、返金、プランの変更に関する問い合わせに正確に対応してください。""",
)

# ルートエージェント: LLMが対応するサブエージェントを選択
root_agent = Agent(
    name="customer_service",
    model="gemini-3.5-flash",
    instruction="""あなたはカスタマーサービスのメインエージェントです。
ユーザーの問い合わせ内容を把握し、対応するサブエージェントに委譲してください。
複数の話題が含まれる場合は、優先度の高い話題を先に扱ってください。""",
    sub_agents=[sales_agent, technical_agent, billing_agent],
)

if __name__ == "__main__":
    # 定義内容の確認（対話実行は adk run / adk web を使用）
    print(f"ルートエージェント: {root_agent.name}")
    print(f"委譲先: {[agent.name for agent in root_agent.sub_agents]}")
