# nested_pipeline.py
# 2-4-6. ネスト: 入れ子構造（完全版）
# SequentialAgentの中にParallelAgentを配置する多層構造の例。
# SequentialAgent/ParallelAgentはTemplate Workflowとして利用できる。複雑な分岐や再開が必要な場合はWorkflow Runtimeを検討する。

from google.adk import Agent
from google.adk.agents import SequentialAgent, ParallelAgent
from google.adk.tools import FunctionTool

# --- ここから補完: 紙面では省略されている検索ツールのダミー実装 ---


def search_flight_options(origin: str, destination: str, date: str) -> list[dict]:
    """航空券の候補を検索する（ダミー実装）。

    Args:
        origin: 出発地
        destination: 到着地
        date: 出発日（YYYY-MM-DD形式）

    Returns:
        航空券情報のリスト"""
    return [{"flight": "NH101", "origin": origin, "destination": destination, "date": date}]


def search_hotel_options(city: str, check_in: str, check_out: str) -> list[dict]:
    """ホテルの候補を検索する（ダミー実装）。

    Args:
        city: 都市名
        check_in: チェックイン日（YYYY-MM-DD形式）
        check_out: チェックアウト日（YYYY-MM-DD形式）

    Returns:
        ホテル情報のリスト"""
    return [{"name": "サンプルホテル", "city": city}]


def search_activity_options(city: str) -> list[dict]:
    """アクティビティの候補を検索する（ダミー実装）。

    Args:
        city: 都市名

    Returns:
        アクティビティ情報のリスト"""
    return [{"name": "寺社めぐりツアー", "city": city}]


flight_tool = FunctionTool(func=search_flight_options)
hotel_tool = FunctionTool(func=search_hotel_options)
activity_tool = FunctionTool(func=search_activity_options)

# --- ここまで補完 ---

# === 並列検索フェーズ ===
flight_search = Agent(
    name="flight_search",
    model="gemini-3.5-flash",
    instruction="航空券を検索してください。",
    output_key="flights",
    tools=[flight_tool],
)

hotel_search = Agent(
    name="hotel_search",
    model="gemini-3.5-flash",
    instruction="ホテルを検索してください。",
    output_key="hotels",
    tools=[hotel_tool],
)

activity_search = Agent(
    name="activity_search",
    model="gemini-3.5-flash",
    instruction="アクティビティを検索してください。",
    output_key="activities",
    tools=[activity_tool],
)

research_phase = ParallelAgent(
    name="research_phase",
    sub_agents=[flight_search, hotel_search, activity_search],
)

# === プランニングフェーズ ===
planner = Agent(
    name="planner",
    model="gemini-3.5-flash",
    instruction="検索結果を統合して旅行プランを作成してください。",
    output_key="travel_plan",
)

# === レポート生成フェーズ ===
reporter = Agent(
    name="reporter",
    model="gemini-3.5-flash",
    instruction="旅行プランを読みやすいレポートにまとめてください。",
)

# === 全体パイプライン ===
root_agent = SequentialAgent(
    name="travel_pipeline",
    sub_agents=[research_phase, planner, reporter],
)

if __name__ == "__main__":
    # 定義内容の確認（対話実行は adk run / adk web を使用）
    print(f"全体パイプライン: {root_agent.name}")
    print(f"第1フェーズ（並列）: {[agent.name for agent in research_phase.sub_agents]}")
