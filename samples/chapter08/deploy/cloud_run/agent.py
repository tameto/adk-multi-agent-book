# samples/chapter08/deploy/cloud_run/agent.py
"""Cloud Runデプロイ用のエージェント定義

app.pyが `from agent import root_agent` で読み込む最小構成のエージェント。
実際のデプロイでは、samples/chapter08/support_agent/ のエージェント定義を
このディレクトリに配置して差し替える。
"""
from google.adk import Agent

root_agent = Agent(
    name="support_agent",
    model="gemini-3.5-flash",
    instruction="""あなたはカスタマーサポートエージェントです。
ユーザーの問い合わせに簡潔に回答してください。
事実のみを回答し、推測は行わないでください。""",
)
