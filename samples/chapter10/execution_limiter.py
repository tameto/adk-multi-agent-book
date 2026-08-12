from google.adk import Agent
from google.adk.tools import ToolContext, BaseTool


class ExecutionLimiter:
    """セッションあたりのツール実行回数を制限する"""

    def __init__(self, max_calls_per_session: int = 50, max_calls_per_tool: int = 10):
        self.max_calls_per_session = max_calls_per_session
        self.max_calls_per_tool = max_calls_per_tool

    def check_limit(
        self,
        tool: BaseTool,
        args: dict,
        tool_context: ToolContext,
    ) -> dict | None:
        """ツール実行回数の上限チェック

        before_tool_callback のメソッド参照として登録する場合、
        シグネチャ: (BaseTool, dict, ToolContext) -> Optional[dict]
        """
        # セッション全体の呼び出し回数
        total_key = "_total_tool_calls"
        total_calls = tool_context.state.get(total_key, 0)
        if total_calls >= self.max_calls_per_session:
            return {
                "error": f"セッションあたりのツール実行上限 "
                         f"({self.max_calls_per_session}回) に達しました。"
            }

        # ツール単位の呼び出し回数
        tool_key = f"_tool_calls_{tool.name}"
        tool_calls = tool_context.state.get(tool_key, 0)
        if tool_calls >= self.max_calls_per_tool:
            return {
                "error": f"ツール '{tool.name}' の実行上限 "
                         f"({self.max_calls_per_tool}回) に達しました。"
            }

        # カウントを更新
        tool_context.state[total_key] = total_calls + 1
        tool_context.state[tool_key] = tool_calls + 1

        return None  # 制限内であれば実行を続行


limiter = ExecutionLimiter(max_calls_per_session=50, max_calls_per_tool=10)
