# samples/chapter03/support_agent/agent.py
"""コンテキスト最適化されたカスタマーサポートエージェント"""
from pathlib import Path

from google.adk import Agent
from google.adk.apps import App
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.plugins.global_instruction_plugin import GlobalInstructionPlugin
from google.adk.skills import load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset

try:
    from .callbacks import (
        authorize_tool_access,
        compose_before_model_callbacks,
        inject_order_context,
        rate_limit_check,
        trim_tool_response,
        validate_response_content,
    )
    from .tools import (
        cancel_order,
        get_order_status,
        get_product_details,
        search_products,
    )
except ImportError:
    from callbacks import (
        authorize_tool_access,
        compose_before_model_callbacks,
        inject_order_context,
        rate_limit_check,
        trim_tool_response,
        validate_response_content,
    )
    from tools import (
        cancel_order,
        get_order_status,
        get_product_details,
        search_products,
    )


def build_instruction(ctx: ReadonlyContext) -> str:
    """ユーザーの会員ティアに応じた動的Instructionを生成する"""
    user_name = ctx.state.get("user_name", "ゲスト")
    user_tier = ctx.state.get("user_tier", "free")

    # ティアごとの対応方針
    tier_policies = {
        "premium": """## プレミアム会員対応
- 最優先で対応してください
- 特別割引（最大20%）の案内が可能です
- 返品期限を30日間に延長できます
- 専任担当者へのエスカレーションが可能です""",
        "standard": """## スタンダード会員対応
- 通常の対応手順に従ってください
- 標準的な返品・交換ポリシーを適用します
- プレミアム会員への切り替え案内を適宜行ってください""",
        "free": """## 無料会員対応
- 基本的な問い合わせのみ対応します
- 会員登録の案内を行ってください
- 対応範囲外の場合はFAQページを案内します""",
    }

    policy = tier_policies.get(user_tier, tier_policies["free"])

    return f"""あなたはECサイト「TechShop」のカスタマーサポートエージェントです。

## Current Context
- ユーザー: {user_name}（{user_tier}会員）

{policy}

## 共通ルール
- 個人情報（パスワード、クレジットカード番号等）は聞き出さないでください
- 確認できた事実のみを伝えてください
- 日本語で回答してください
- 対応範囲外はエスカレーションツールを使用してください

## 応答形式
1. 問い合わせ内容の確認
2. 回答（箇条書き）
3. 追加の質問の確認

## 停止条件
- ユーザーの問い合わせに回答が完了した場合
- エスカレーションが必要と判断した場合
- ユーザーが終了を示す発言をした場合"""


# Agent Skillsの読み込み（experimental）
# SKILL.md を持つディレクトリは samples/chapter03/skills/ に配置している
SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"
order_skill = load_skill_from_dir(SKILLS_DIR / "order-management")
product_skill = load_skill_from_dir(SKILLS_DIR / "product-inquiry")

# SkillをToolsetとしてまとめ、Function Tools と並列にtools=へ渡す
skill_toolset = SkillToolset(skills=[order_skill, product_skill])

# ルートエージェントの定義
root_agent = Agent(
    name="support_agent",
    model="gemini-3.5-flash",
    instruction=build_instruction,
    tools=[
        skill_toolset,
        get_order_status,
        cancel_order,
        search_products,
        get_product_details,
    ],
    before_model_callback=compose_before_model_callbacks(
        rate_limit_check,
        inject_order_context,
    ),
    after_model_callback=validate_response_content,
    before_tool_callback=authorize_tool_access,
    after_tool_callback=trim_tool_response,
)

app = App(
    name="support_agent",
    root_agent=root_agent,
    plugins=[
        GlobalInstructionPlugin(
            global_instruction="""## 全エージェント共通ルール
- 応答は日本語で行う
- 個人情報の取り扱いに最大限注意する
- 回答には必ず根拠を示す"""
        )
    ],
)
