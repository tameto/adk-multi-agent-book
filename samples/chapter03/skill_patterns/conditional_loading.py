# samples/chapter03/skill_patterns/conditional_loading.py
"""3-5-4 パターン2: スキルの条件付き読み込み（完全版）

ユーザーの権限やエージェントの設定に応じて、
読み込むスキルを動的に切り替えるパターン。
"""
from pathlib import Path

from google.adk import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset

SKILLS_DIR = Path("./skills")


def create_agent_with_skills(user_role: str) -> Agent:
    """ユーザーの権限に応じたスキルでエージェントを構築する"""
    # 全ユーザーに共通のスキル
    skills = [
        load_skill_from_dir(SKILLS_DIR / "product-inquiry"),
        load_skill_from_dir(SKILLS_DIR / "faq"),
    ]

    # 権限に応じたスキルの追加
    if user_role in ("standard", "premium", "admin"):
        skills.append(load_skill_from_dir(SKILLS_DIR / "order-management"))

    if user_role in ("premium", "admin"):
        skills.append(load_skill_from_dir(SKILLS_DIR / "priority_support"))

    if user_role == "admin":
        skills.append(load_skill_from_dir(SKILLS_DIR / "admin_operations"))

    return Agent(
        name="support_agent",
        model="gemini-3.5-flash",
        instruction="あなたはカスタマーサポートエージェントです。",
        tools=[SkillToolset(skills=skills)],
    )
