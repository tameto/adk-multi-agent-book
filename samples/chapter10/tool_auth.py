from google.adk import Agent
from google.adk.tools import ToolContext, FunctionTool, BaseTool
from google.genai import types


# ツールごとの必要権限を定義
TOOL_PERMISSIONS: dict[str, list[str]] = {
    "read_customer_data": ["viewer", "editor", "admin"],
    "update_customer_data": ["editor", "admin"],
    "delete_customer_data": ["admin"],
    "export_all_data": ["admin"],
}


def before_tool_guard(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
) -> dict | None:
    """ツール呼び出し前に権限チェックを行うガードレール

    シグネチャ: (BaseTool, dict, ToolContext) -> Optional[dict]"""
    tool_name = tool.name
    # Session Stateからユーザーのロールを取得
    user_role = tool_context.state.get("user_role", "viewer")

    required_roles = TOOL_PERMISSIONS.get(tool_name, [])
    if required_roles and user_role not in required_roles:
        # 権限不足の場合、ツール実行をスキップしてエラーメッセージを返す
        return {
            "error": f"権限エラー: {tool_name} の実行には "
                     f"{required_roles} のいずれかのロールが必要です。"
                     f"現在のロール: {user_role}"
        }

    return None  # 権限があればツール実行を続行


def read_customer_data(customer_id: str) -> dict:
    """顧客データを読み取る"""
    return {"customer_id": customer_id, "name": "田中太郎", "status": "active"}


def update_customer_data(customer_id: str, field: str, value: str) -> dict:
    """顧客データを更新する"""
    return {"customer_id": customer_id, "updated": {field: value}}


def delete_customer_data(customer_id: str) -> dict:
    """顧客データを削除する"""
    return {"customer_id": customer_id, "deleted": True}


# 権限チェック付きエージェント
auth_agent = Agent(
    name="customer_service_agent",
    model="gemini-3.5-flash",
    instruction="あなたは顧客管理エージェントです。ユーザーの権限に応じて操作を実行してください。",
    tools=[read_customer_data, update_customer_data, delete_customer_data],
    before_tool_callback=before_tool_guard,
)
