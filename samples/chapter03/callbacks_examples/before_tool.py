# samples/chapter03/callbacks_examples/before_tool.py
"""3-4-3 before_tool_callback（完全版）

ツール関数の呼び出し直前に実行されるコールバック。
ツールの引数検証や権限チェックに使用する。
"""
from google.adk.tools import BaseTool, ToolContext
from typing import Optional

def authorize_tool_call(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
) -> Optional[dict]:
    """ツール呼び出し前に権限チェックを行うコールバック"""
    user_role = tool_context.state.get("user_role", "viewer")
    tool_name = tool.name

    # 書き込み系ツールの権限チェック
    write_tools = ["cancel_order", "process_refund", "update_shipping"]
    if tool_name in write_tools and user_role == "viewer":
        return {
            "error": "権限不足です。この操作には管理者権限が必要です。"
        }

    # 引数のバリデーション
    if tool_name == "cancel_order":
        order_id = args.get("order_id", "")
        if not order_id.startswith("ORD-"):
            return {
                "error": f"無効な注文ID形式です: {order_id}。ORD-で始まるIDを指定してください。"
            }

    # ツール呼び出しをログに記録
    call_log = tool_context.state.get("tool_call_log", [])
    call_log.append({"tool": tool_name, "args": args})
    tool_context.state["tool_call_log"] = call_log

    return None  # Noneを返すとツール呼び出しが続行される
