# samples/chapter05/expense_agent/agent.py
"""第5章 ハンズオン: 経費精算エージェント

評価・ガードレール・HITLを組み込んだ経費精算エージェント。
- before_model_callback: 入力ガードレール（プロンプトインジェクション検出）と
  HITL承認入力の処理
- after_model_callback: 出力ガードレール（PII漏えい防止）
- before_tool_callback: HITL承認フロー（高額経費の承認）
"""

from google.adk import Agent
from google.genai.types import GenerateContentConfig

try:
    from .callbacks import (
        handle_hitl_approval_input,
        hitl_approval_callback,
        input_guardrail,
        output_guardrail,
    )
    from .tools import (
        approve_expense,
        query_expenses,
        reset_data,
        submit_expense,
    )
except ImportError:
    from callbacks import (
        handle_hitl_approval_input,
        hitl_approval_callback,
        input_guardrail,
        output_guardrail,
    )
    from tools import (
        approve_expense,
        query_expenses,
        reset_data,
        submit_expense,
    )

# 経費精算エージェントの定義
root_agent = Agent(
    name="expense_agent",
    model="gemini-3.5-flash",
    instruction="""あなたは経費精算を支援するエージェントです。
ユーザーの依頼に応じて、以下の操作を行います。

## できること
- 経費の申請（submit_expense）: 日付・カテゴリ・金額・説明を受け取り経費を申請する
- 経費の照会（query_expenses）: ユーザーIDと対象月を指定して経費一覧を取得する
- 経費の承認（approve_expense）: 経費IDを指定して経費を承認する

## 注意事項
- 金額は日本円（整数）で処理する
- カテゴリは「交通費」「会議費」「消耗品費」「通信費」「その他」のいずれかを使用する
- submit_expenseのdescriptionには、費目名ではなく業務目的・補足だけを入れる
- 「カテゴリは交通費、客先訪問の移動です」のようにカテゴリと説明が並ぶ場合、categoryは「交通費」、descriptionは「客先訪問の移動」とする
- ユーザーが具体的な情報を提供しない場合は、必要な情報を確認する
- 50万円以上の経費は承認フローが必要であることをユーザーに伝える
- 個人情報（メールアドレス、電話番号等）を応答に含めない
""",
    tools=[submit_expense, query_expenses, approve_expense],
    generate_content_config=GenerateContentConfig(temperature=0),
    # 入力ガードレールを先に通し、通過した入力だけを承認処理に渡す
    before_model_callback=[input_guardrail, handle_hitl_approval_input],
    after_model_callback=output_guardrail,
    before_tool_callback=hitl_approval_callback,
)
