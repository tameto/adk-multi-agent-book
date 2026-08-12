# hitl_approval.py
# 2-4-8. Human-in-the-Loop統合（完全版）
# LongRunningFunctionToolで人間の承認ステップを処理フローに組み込む。

import uuid

from google.adk import Agent
from google.adk.tools import FunctionTool, LongRunningFunctionTool
from google.adk.tools.tool_context import ToolContext

# --- ここから補完: 紙面では省略されている承認依頼の発行処理のダミー実装 ---


async def send_approval_request(action: str, requester: str | None) -> str:
    """承認依頼を発行する（ダミー実装）。

    実際の実装ではSlack通知・メール・管理画面等へ承認依頼を送信する。

    Args:
        action: 承認を求めるアクション名
        requester: 依頼者のユーザーID

    Returns:
        承認依頼ID"""
    approval_id = f"approval-{uuid.uuid4().hex[:8]}"
    print(f"承認依頼を発行しました: id={approval_id}, action={action}, requester={requester}")
    return approval_id


def get_order(order_id: str) -> dict:
    """注文情報を取得する（ダミー実装）。

    Args:
        order_id: 注文ID

    Returns:
        注文情報"""
    return {"order_id": order_id, "status": "confirmed", "total_price": 120000}


# 注文管理用ツール（紙面のorder_toolsに対応するダミー）
order_tools = FunctionTool(func=get_order)

# --- ここまで補完 ---


async def request_human_approval(action: str, tool_context: ToolContext) -> dict:
    """人間の承認を要求するツール（LongRunningFunctionTool用）

    LongRunningFunctionTool は、ツール側で承認結果まで待機しません。
    まず承認依頼を発行してIDを返し、Runner はランを一時停止して
    クライアントに「承認を待っている」状態を通知します。
    クライアント側で承認結果を取得し、`function_response` を Runner に
    返すことでランが再開されます。

    Args:
        action: 承認を求めるアクション名

    Returns:
        承認依頼のIDと初期ステータスを含む辞書"""
    # 承認要求を発行（Slack通知・メール・管理画面等への通知）
    approval_id = await send_approval_request(
        action=action,
        requester=tool_context.state.get("user_id"),
    )

    # ここで結果を待機せず、依頼IDを返してツール呼び出しを終了する
    return {
        "status": "pending",
        "approval_id": approval_id,
    }


# HITLツール
approval_tool = LongRunningFunctionTool(func=request_human_approval)

# HITLを組み込んだエージェント
agent = Agent(
    name="cautious_agent",
    model="gemini-3.5-flash",
    instruction="""あなたは注文管理エージェントです。
以下のアクションを実行する前に、必ずrequest_human_approvalツールで承認を得てください:
- 10万円以上の注文のキャンセル
- 返金処理
- 顧客情報の変更""",
    tools=[approval_tool, order_tools],
)

# adk run / adk web から参照できるようroot_agentとして公開する（補完）
root_agent = agent

if __name__ == "__main__":
    # 定義内容の確認（対話実行は adk run / adk web を使用）
    print(f"エージェント: {agent.name}")
    print("HITLツール: request_human_approval（LongRunningFunctionTool）")
