# samples/chapter03/context_propagation/multi_agent_state.py
"""3-2-7 マルチエージェント構成でのコンテキスト伝播（完全版）

すべてのエージェントが同一のSessionオブジェクトを共有するため、
ルートエージェントがStateに書き込んだ値はサブエージェントからも読み取れる。
"""
from google.adk import Agent

# サブエージェント: 注文管理（ルートと同じSessionのStateを読み取れる）
order_agent = Agent(
    name="order_agent",
    model="gemini-3.5-flash",
    instruction=lambda ctx: f"""注文管理を担当します。
ユーザー名: {ctx.state.get('user_name', '不明')}
ユーザーティア: {ctx.state.get('user_tier', 'free')}
""",
)

# サブエージェント: 技術サポート
tech_agent = Agent(
    name="tech_agent",
    model="gemini-3.5-flash",
    instruction=lambda ctx: f"""技術サポートを担当します。
ユーザー名: {ctx.state.get('user_name', '不明')}
""",
)

# ルートエージェント
root_agent = Agent(
    name="root_agent",
    model="gemini-3.5-flash",
    instruction="問い合わせ内容に対応するサブエージェントに振り分けてください。",
    sub_agents=[order_agent, tech_agent],
)
