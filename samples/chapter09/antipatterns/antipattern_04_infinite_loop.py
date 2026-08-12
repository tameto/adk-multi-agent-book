# samples/chapter09/antipatterns/antipattern_04_infinite_loop.py
"""アンチパターン4: Infinite Loop（無限ループ）の実装例（9-2-4 完全版）

停止条件のないループ（bad_loop）と、3層の防御による改善を対比する。
- 改善1: 既存LoopAgentコードではmax_iterationsを設定（safe_loop）
- 改善2: AgentのInstructionに終了条件を明記（research_agent）
- 改善3: before_tool_callbackでループを検知（detect_loop）

紙面では bad_loop / safe_loop → research_agent の順で提示しているが、
本ファイルでは参照解決のため research_agent / analysis_agent を先に定義する。
"""
from google.adk import Agent
from google.adk.agents import LoopAgent


# --- ツール・エージェントのダミー実装（紙面では省略。実行確認用の最小実装） ---

def search_tool(query: str) -> list[dict]:
    """情報を検索します（ダミー実装）"""
    return [{"title": "検索結果", "snippet": f"{query} に関する情報"}]


def create_research_agent(name: str = "research_agent") -> Agent:
    """終了条件をInstructionに明記した調査エージェントを生成する"""
    return Agent(
        name=name,
        model="gemini-3.5-flash",
        instruction="""調査を行います。

    ## 終了条件
    以下のいずれかに該当する場合、調査を終了してください:
    - 十分な情報が得られた場合
    - 3回検索しても新しい情報が見つからない場合
    - ユーザーの質問に回答できる情報が揃った場合

    終了時は「調査完了」と明記してください。""",
        tools=[search_tool],
    )


def create_analysis_agent(name: str = "analysis_agent") -> Agent:
    """調査結果を要約する分析エージェントを生成する"""
    return Agent(
        name=name,
        model="gemini-3.5-flash",
        instruction="調査結果を分析し、要点をまとめます。",
    )


# 改善2: AgentにInstructionで終了条件を明記
research_agent = create_research_agent()
analysis_agent = create_analysis_agent()

# アンチパターン: 停止条件のないループ
bad_loop = LoopAgent(
    name="bad_loop",
    sub_agents=[research_agent, analysis_agent],
    # max_iterations を指定していない → 無限ループのリスク
)

# 改善1: LoopAgentにmax_iterationsを設定
# LoopAgentはTemplate Workflowとして利用できる。既存コードの改善例として示す。
safe_loop = LoopAgent(
    name="safe_loop",
    sub_agents=[
        create_research_agent("safe_research_agent"),
        create_analysis_agent("safe_analysis_agent"),
    ],
    max_iterations=5,  # 最大5回で強制終了
)


# 改善3: before_tool_callbackでループを検知（実シグネチャ: BaseTool, dict, ToolContext）
def detect_loop(tool, args, tool_context):
    """同一ツール・同一引数の連続呼び出しを検知して停止します"""
    call_history = tool_context.state.get("_call_history", [])
    current_call = {"tool": tool.name, "args": str(args)}
    call_history.append(current_call)
    tool_context.state["_call_history"] = call_history

    # 直近3回が同一呼び出しならループと判定
    if len(call_history) >= 3:
        last_three = call_history[-3:]
        if all(c == last_three[0] for c in last_three):
            return {
                "error": "ループを検知しました。同じ操作が3回連続しています。",
                "suggestion": "別のアプローチを試みるか、ユーザーに確認してください。",
            }
    return None
