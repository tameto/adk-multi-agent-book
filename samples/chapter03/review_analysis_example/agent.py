# samples/chapter03/review_analysis_example/agent.py
"""3-5-6 Step 5: エージェントへの組み込み（完全版）

スキルを load_skill_from_dir() で読み込み、
関数ツールと並列に tools= へ登録する。
スキル本体は samples/chapter03/skills/review-analysis/ に配置している。
"""
from pathlib import Path

from google.adk import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset

try:
    from .tools import analyze_reviews, get_review_trends
except ImportError:
    from tools import analyze_reviews, get_review_trends

# スキルの読み込み
review_skill = load_skill_from_dir(
    Path(__file__).resolve().parent.parent / "skills" / "review-analysis"
)
skill_toolset = SkillToolset(skills=[review_skill])

# エージェントに組み込む
product_agent = Agent(
    name="product_agent",
    model="gemini-3.5-flash",
    instruction="商品に関する問い合わせに対応するエージェントです。",
    tools=[skill_toolset, analyze_reviews, get_review_trends],
)

root_agent = product_agent
