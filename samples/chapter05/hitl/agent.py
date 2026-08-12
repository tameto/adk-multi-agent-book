# 5-5-3. ADKでのHITL実装（承認フローを処理するエージェント）
# 紙面の掲載パス: agent.py（samples/chapter05 ディレクトリから実行する前提）
"""HITL対応エージェントの定義"""
import json
from typing import Optional

from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types

try:
    from .approval_flow import ApprovalManager
    from .tools import transfer_funds, delete_records, update_user_role
except ImportError:
    from hitl.approval_flow import ApprovalManager
    from hitl.tools import transfer_funds, delete_records, update_user_role

approval_manager = ApprovalManager()


def handle_approval_input(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """ユーザーの承認/拒否入力を処理する"""
    pending = callback_context.state.get("_pending_approval")
    if not pending:
        return None

    approval_request = json.loads(pending)

    last_message = _get_last_user_message(llm_request)
    if not last_message:
        return None

    # 承認の処理
    expected_approval = f"承認: {approval_request['request_id']}"
    if expected_approval in last_message:
        tool_name = approval_request["tool_name"]
        callback_context.state[f"_approval_{tool_name}"] = True
        callback_context.state["_pending_approval"] = None

        return LlmResponse(
            content=types.Content(
                parts=[
                    types.Part(
                        text=f"承認されました。"
                        f"{tool_name}を実行します。"
                    )
                ],
                role="model",
            )
        )

    # 拒否の処理
    if "拒否" in last_message:
        callback_context.state["_pending_approval"] = None
        return LlmResponse(
            content=types.Content(
                parts=[
                    types.Part(
                        text="操作が拒否されました。"
                        "他にお手伝いできることはありますか？"
                    )
                ],
                role="model",
            )
        )

    return None


def _get_last_user_message(llm_request):
    """最新のユーザーメッセージを取得"""
    if not llm_request.contents:
        return None
    for content in reversed(llm_request.contents):
        if content.role == "user":
            for part in content.parts:
                if part.text:
                    return part.text
    return None


# HITL対応エージェントの定義
agent = Agent(
    name="hitl_agent",
    model="gemini-3.5-flash",
    instruction=(
        "あなたは業務システムの操作を支援するエージェントです。"
        "ユーザーのリクエストに応じて、必要なツールを使用して操作を実行します。"
        "送金はtransfer_funds、レコード削除はdelete_records、"
        "権限変更はupdate_user_roleを使用してください。"
        "高リスクな操作は人間の承認が必要です。"
    ),
    tools=[transfer_funds, delete_records, update_user_role],
    before_model_callback=handle_approval_input,
    before_tool_callback=approval_manager.before_tool_callback,
)

root_agent = agent
