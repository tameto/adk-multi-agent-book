# builtin_tools.py
# 2-6-6. 組み込みツール（完全版）
# google_search（Google検索）、BuiltInCodeExecutor（コード実行）、
# ExecuteBashTool（シェルコマンド実行）の3つの利用例。

from google.adk import Agent
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.tools import google_search
from google.adk.tools.bash_tool import ExecuteBashTool

# === google_search: Google検索 ===
# Gemini API版のgoogle_searchは単独ツールとしての利用が前提
research_agent = Agent(
    name="research_agent",
    model="gemini-3.5-flash",
    instruction="ユーザーの質問に答えるため、必要に応じてGoogle検索を活用してください。",
    tools=[google_search],
)

# === BuiltInCodeExecutor: コード実行 ===
# toolsではなくcode_executor引数に渡す点に注意
data_analyst = Agent(
    name="data_analyst",
    model="gemini-3.5-flash",
    instruction="""ユーザーのデータ分析要求に応えてください。
必要に応じてPythonコードを実行して計算してください。""",
    code_executor=BuiltInCodeExecutor(),
)

# === ExecuteBashTool: シェルコマンド実行 ===
# 本番環境での使用はコマンド制限・サンドボックス化を検討する（第10章参照）
bash_tool = ExecuteBashTool()

ops_agent = Agent(
    name="ops_agent",
    model="gemini-3.5-flash",
    instruction="システム管理タスクを実行してください。",
    tools=[bash_tool],
)

if __name__ == "__main__":
    # 定義内容の確認（対話実行は adk run / adk web を使用）
    for agent in (research_agent, data_analyst, ops_agent):
        print(f"エージェント: {agent.name}")
