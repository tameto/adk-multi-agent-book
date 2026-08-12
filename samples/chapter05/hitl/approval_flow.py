# 5-5-3. ADKでのHITL実装
"""Human-in-the-Loop承認フローの実装"""
import json
import uuid
from datetime import datetime

from google.adk.tools import BaseTool, ToolContext


class ApprovalManager:
    """HITL承認フローを管理するクラス"""

    # 承認が必要なツールとその条件
    APPROVAL_RULES = {
        "transfer_funds": {
            "condition": lambda args: args.get("amount", 0) >= 1000000,
            "message": "高額送金のため承認が必要です",
        },
        "delete_records": {
            "condition": lambda args: args.get("count", 0) >= 10,
            "message": "大量レコードの削除のため承認が必要です",
        },
        "update_user_role": {
            "condition": lambda args: True,  # 常に承認が必要
            "message": "権限変更のため承認が必要です",
        },
    }

    def before_tool_callback(
        self,
        tool: BaseTool,
        args: dict,
        tool_context: ToolContext,
    ) -> dict | None:
        """ツール実行前の承認チェック"""
        tool_name = tool.name
        rule = self.APPROVAL_RULES.get(tool_name)
        if not rule:
            return None  # 承認不要なツール

        if not rule["condition"](args):
            return None  # 条件を満たさないため承認不要

        # 既に承認済みかチェック
        approval_key = f"_approval_{tool_name}"
        if tool_context.state.get(approval_key):
            # 承認済みフラグをリセットして実行を許可
            tool_context.state[approval_key] = False
            return None

        # 承認リクエストを生成
        request_id = str(uuid.uuid4())[:8]
        approval_request = {
            "type": "approval_required",
            "request_id": request_id,
            "tool_name": tool_name,
            "tool_input": args,
            "message": rule["message"],
            "timestamp": datetime.now().isoformat(),
        }

        # 承認リクエストをStateに保存
        tool_context.state["_pending_approval"] = json.dumps(
            approval_request, ensure_ascii=False
        )

        return {
            "status": "approval_required",
            "message": (
                f"{rule['message']}\n\n"
                f"操作: {tool_name}\n"
                f"パラメータ: {json.dumps(args, ensure_ascii=False)}\n\n"
                f"承認する場合は「承認: {request_id}」と入力してください。\n"
                f"拒否する場合は「拒否」と入力してください。"
            ),
        }
