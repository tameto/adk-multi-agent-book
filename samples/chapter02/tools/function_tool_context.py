# function_tool_context.py
# 2-6-2. FunctionTool: ToolContextの活用（完全版）
# 引数に tool_context: ToolContext を含めると、ADKが実行時に自動注入する。
# ToolContextはLLMに公開されず、スキーマにも含まれない。

from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types


async def save_report(
    title: str,
    content: str,
    tool_context: ToolContext,
) -> dict:
    """レポートを保存する。

    Args:
        title: レポートタイトル
        content: レポート内容

    Returns:
        保存結果"""
    # Stateに保存
    tool_context.state["last_report_title"] = title

    # ArtifactとしてPart形式で保存（save_artifactはコルーチン）
    report_bytes = content.encode("utf-8")
    part = types.Part.from_bytes(data=report_bytes, mime_type="text/plain")
    version = await tool_context.save_artifact(
        filename=f"{title}.txt",
        artifact=part,
    )

    return {
        "status": "saved",
        "version": version,
    }


# FunctionTool化（補完: 紙面には未掲載）
save_report_tool = FunctionTool(func=save_report)

if __name__ == "__main__":
    # ToolContextはADKランタイムが注入するため、単体実行では定義の確認のみ行う
    print(f"ツール名: {save_report_tool.name}")
