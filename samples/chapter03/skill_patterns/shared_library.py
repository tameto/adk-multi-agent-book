# samples/chapter03/skill_patterns/shared_library.py
"""3-5-4 パターン1: 共通スキルライブラリ（完全版）

組織内で頻繁に使用するスキル（認証、通知、ログ記録など）を
共通ライブラリとして管理し、複数のエージェントから参照するパターン。
※ ./common_skills と ./domain_skills は組織内のスキルライブラリを想定した例
"""
from pathlib import Path

from google.adk import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset


def create_shared_library_agents(
    common: Path = Path("./common_skills"),
    domain: Path = Path("./domain_skills"),
) -> tuple[Agent, Agent]:
    """共通スキルライブラリを読み込み、2種類のエージェントを構築する"""
    # 共通スキルライブラリから読み込み
    auth_skill = load_skill_from_dir(common / "authentication")
    notification_skill = load_skill_from_dir(common / "notification")

    # ドメイン固有スキル
    order_skill = load_skill_from_dir(domain / "order-management")

    # エージェント A: カスタマーサポート
    support_agent = Agent(
        name="support_agent",
        model="gemini-3.5-flash",
        instruction="...",
        tools=[
            SkillToolset(skills=[auth_skill, notification_skill, order_skill]),
        ],
    )

    # エージェント B: 社内管理ツール（共通スキルを再利用）
    admin_agent = Agent(
        name="admin_agent",
        model="gemini-3.5-flash",
        instruction="...",
        tools=[SkillToolset(skills=[auth_skill, notification_skill])],
    )

    return support_agent, admin_agent
