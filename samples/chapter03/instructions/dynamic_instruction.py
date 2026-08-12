# samples/chapter03/instructions/dynamic_instruction.py
"""3-3-2 動的Instruction（完全版）

ReadonlyContextを引数として受け取り、実行時の状態に基づいて
Instructionを動的に生成する。Stateの読み取りのみが許可されるため、
Instruction生成の過程でStateが変更されることが型レベルで防止される。
"""
from google.adk import Agent
from google.adk.agents.readonly_context import ReadonlyContext

def build_dynamic_instruction(ctx: ReadonlyContext) -> str:
    """実行時の状態に基づいてInstructionを動的に生成する"""
    # Stateからユーザー情報を取得
    user_name = ctx.state.get("user_name", "ゲスト")
    user_tier = ctx.state.get("user_tier", "standard")
    order_history_count = ctx.state.get("order_count", 0)

    # ユーザーティアに応じた対応方針を設定
    if user_tier == "premium":
        tier_instruction = """## プレミアム会員への対応
- 最優先で対応してください
- 特別割引や優先配送の案内が可能です
- 返品期限を30日間に延長できます"""
    elif user_tier == "standard":
        tier_instruction = """## スタンダード会員への対応
- 通常の対応手順に従ってください
- 標準的な返品・交換ポリシーを適用します"""
    else:
        tier_instruction = """## ゲストユーザーへの対応
- 会員登録の案内を適宜行ってください
- 基本的な問い合わせのみ対応します"""

    # 注文履歴に応じた追加指示
    history_note = ""
    if order_history_count > 50:
        history_note = "\n- このユーザーはリピーターです。感謝の意を伝えてください"

    return f"""あなたはECサイトのカスタマーサポートエージェントです。
現在対応中のユーザー: {user_name}（{user_tier}会員）

{tier_instruction}
{history_note}

## 共通ルール
- 個人情報は絶対に聞き出さないでください
- 対応範囲外はエスカレーションしてください"""

# 動的Instruction: callableを渡す
support_agent = Agent(
    name="support_agent",
    model="gemini-3.5-flash",
    instruction=build_dynamic_instruction,
)
