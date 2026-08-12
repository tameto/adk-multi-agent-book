# samples/chapter02/instruction_examples.py
# 2-3-2. instructionの書き方（動的instruction）/ 2-3-4. output_keyとoutput_schema（完全版）
# 紙面では断片で掲載しているコードのimport・前段エージェント定義を補完している。
"""動的instruction（コールバック関数）の完全版サンプル

- dynamic_instruction: セッションStateに応じて指示を切り替える（2-3-2）
- planner_instruction: 前段エージェントの output_key をStateから参照する（2-3-4）
"""
from google.adk import Agent
from google.adk.agents.readonly_context import ReadonlyContext


# --- 2-3-2. 動的instruction（コールバック関数） ---

def dynamic_instruction(ctx: ReadonlyContext) -> str:
    """ユーザーの属性に応じて指示を動的に生成する"""
    user_tier = ctx.state.get("user_tier", "standard")
    language = ctx.state.get("language", "ja")

    base = "あなたはカスタマーサポートエージェントです。"

    if user_tier == "premium":
        base += "\nこのユーザーはプレミアム会員です。優先対応してください。"
        base += "\n返金・交換は即時承認できます。"
    else:
        base += "\n返金・交換はチケットを作成してエスカレーションしてください。"

    if language == "en":
        base += "\nRespond in English."

    return base


agent = Agent(
    name="customer_support",
    model="gemini-3.5-flash",
    instruction=dynamic_instruction,
)


# --- 2-3-4. output_keyとoutput_schema（動的instructionでstateから前段の結果を取得） ---

# 補完: 前段のエージェント定義（紙面の output_key 説明で掲載しているコード）。
# 実行後、state["research_result"] に出力テキストが保存される。
researcher = Agent(
    name="researcher",
    model="gemini-3.5-flash",
    instruction="旅行先の情報を調査してください。",
    output_key="research_result",
)


def planner_instruction(ctx: ReadonlyContext) -> str:
    research = ctx.state.get("research_result", "調査結果がありません")
    return f"""以下の調査結果をもとにスケジュールを作成してください。

調査結果:
{research}"""


planner = Agent(
    name="planner",
    model="gemini-3.5-flash",
    instruction=planner_instruction,
    output_key="schedule",
)
