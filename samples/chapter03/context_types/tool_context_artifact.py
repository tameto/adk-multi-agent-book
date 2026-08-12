# samples/chapter03/context_types/tool_context_artifact.py
# 3-2-5. ToolContext（完全版）
# ToolContext クラス自体（save_artifact / load_artifact / list_artifacts を含む）は
# ADK本体（google.adk.tools.tool_context）が提供するクラスのため、本ファイルには収録しない。
"""ToolContextのArtifact操作を使ったツール関数のサンプル"""
from google.adk import Agent
from google.adk.tools import ToolContext
from google.genai import types  # 補完: 紙面の断片では省略されているimport


async def generate_report(
    query: str,
    tool_context: ToolContext,
) -> dict:
    """レポートを生成してArtifactとして保存するツール"""
    # レポートの内容を生成
    report_content = f"# 分析レポート\n\nクエリ: {query}\n\n結果: ..."

    # ArtifactとしてMarkdownファイルを保存（from_textはキーワード専用引数）
    artifact = types.Part.from_text(text=report_content)
    version = await tool_context.save_artifact("report.md", artifact)

    # Stateに最新バージョンを記録
    tool_context.state["latest_report_version"] = version

    return {
        "status": "success",
        "filename": "report.md",
        "version": version,
    }


# 補完: 紙面ではツール関数のみ掲載。エージェントへの組み込み例。
# Artifactを保存するため、Runner側でartifact_serviceの構成が必要になる。
agent = Agent(
    name="report_agent",
    model="gemini-3.5-flash",
    instruction="ユーザーの依頼に応じて generate_report ツールでレポートを作成してください。",
    tools=[generate_report],
)
