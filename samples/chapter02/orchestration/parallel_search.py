# parallel_search.py
# 2-4-2. ParallelAgent: 並列実行（完全版）
# 航空券・ホテル・アクティビティの検索を並列に実行する。
# ParallelAgentはTemplate Workflowとして利用できる。複雑な分岐や再開が必要な場合はWorkflow Runtimeを検討する。

from google.adk import Agent
from google.adk.agents import ParallelAgent
from google.adk.tools import FunctionTool

# --- ここから補完: 紙面では省略されている検索ツールのダミー実装 ---


def search_flights(origin: str, destination: str, date: str) -> list[dict]:
    """航空券を検索する（ダミー実装）。

    Args:
        origin: 出発地（例: 東京）
        destination: 到着地（例: 京都）
        date: 出発日（YYYY-MM-DD形式）

    Returns:
        航空券情報のリスト"""
    # 実際の実装では航空券検索APIを呼び出す
    return [{"flight": "NH101", "origin": origin, "destination": destination, "date": date, "price": 25000}]


def search_hotels(city: str, check_in: str, check_out: str) -> list[dict]:
    """ホテルを検索する（ダミー実装）。

    Args:
        city: 都市名
        check_in: チェックイン日（YYYY-MM-DD形式）
        check_out: チェックアウト日（YYYY-MM-DD形式）

    Returns:
        ホテル情報のリスト"""
    # 実際の実装ではホテル検索APIを呼び出す
    return [{"name": "サンプルホテル", "city": city, "price_per_night": 12000}]


def search_activities(city: str, date: str) -> list[dict]:
    """観光アクティビティを検索する（ダミー実装）。

    Args:
        city: 都市名
        date: 日付（YYYY-MM-DD形式）

    Returns:
        アクティビティ情報のリスト"""
    # 実際の実装ではアクティビティ検索APIを呼び出す
    return [{"name": "寺社めぐりツアー", "city": city, "date": date, "price": 5000}]


flight_search_tool = FunctionTool(func=search_flights)
hotel_search_tool = FunctionTool(func=search_hotels)
activity_search_tool = FunctionTool(func=search_activities)

# --- ここまで補完 ---

# 航空券検索エージェント
flight_agent = Agent(
    name="flight_searcher",
    model="gemini-3.5-flash",
    instruction="指定された区間・日程の航空券を検索してください。",
    output_key="flight_options",
    tools=[flight_search_tool],
)

# ホテル検索エージェント
hotel_agent = Agent(
    name="hotel_searcher",
    model="gemini-3.5-flash",
    instruction="指定された都市・日程のホテルを検索してください。",
    output_key="hotel_options",
    tools=[hotel_search_tool],
)

# アクティビティ検索エージェント
activity_agent = Agent(
    name="activity_searcher",
    model="gemini-3.5-flash",
    instruction="指定された都市の観光アクティビティを検索してください。",
    output_key="activity_options",
    tools=[activity_search_tool],
)

# 並列実行
parallel_search = ParallelAgent(
    name="parallel_search",
    sub_agents=[flight_agent, hotel_agent, activity_agent],
)

# adk run / adk web から参照できるようroot_agentとして公開する（補完）
root_agent = parallel_search

if __name__ == "__main__":
    # 定義内容の確認（対話実行は adk run / adk web を使用）
    print(f"並列エージェント: {parallel_search.name}")
    print(f"サブエージェント: {[agent.name for agent in parallel_search.sub_agents]}")
