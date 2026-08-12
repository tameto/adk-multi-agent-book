# 5-4-2. ガードレールのエージェントへの適用
# 紙面の掲載パス: agent.py（samples/chapter05 ディレクトリから実行する前提）
"""ガードレール付きエージェントの定義"""
from google.adk import Agent

try:
    from .input_guardrails import input_safety_guardrail
    from .output_guardrails import output_quality_guardrail
except ImportError:
    from guardrails.input_guardrails import input_safety_guardrail
    from guardrails.output_guardrails import output_quality_guardrail

agent = Agent(
    name="guarded_agent",
    model="gemini-3.5-flash",
    instruction="あなたはカスタマーサポートのエージェントです。",
    before_model_callback=input_safety_guardrail,
    after_model_callback=output_quality_guardrail,
)

root_agent = agent
