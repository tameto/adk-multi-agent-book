# samples/chapter03/callbacks_examples/after_tool.py
"""3-4-4 after_tool_callback（完全版）

ツール関数の実行後に呼び出されるコールバック。
ツールの実行結果の加工やログ記録に使用する。
"""
from google.adk.tools import BaseTool, ToolContext
from typing import Optional

def process_tool_result(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
    tool_response: dict,
) -> Optional[dict]:
    """ツール実行結果を加工するコールバック"""
    tool_name = tool.name

    # APIレスポンスから不要なメタデータを除去
    if "metadata" in tool_response:
        del tool_response["metadata"]

    # 大きなレスポンスを要約（コンテキストウィンドウの節約）
    if tool_name == "search_products":
        results = tool_response.get("results", [])
        if len(results) > 5:
            # 上位5件のみを残す
            tool_response["results"] = results[:5]
            tool_response["note"] = f"全{len(results)}件中、上位5件を表示"

    # 実行結果をStateに記録
    tool_context.state[f"last_{tool_name}_result"] = tool_response

    return tool_response  # 加工後の結果を返す
