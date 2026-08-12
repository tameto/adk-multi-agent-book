"""第2章 ハンズオン: 旅行プランナーエージェント

SequentialAgent + ParallelAgent を組み合わせたマルチエージェント構成。
これらのTemplate WorkflowはADK v2.2.0でも利用できる。複雑な分岐や再開が必要な場合はWorkflow Runtimeを検討する。
3つの調査エージェントが並列で情報を収集し、その結果をもとに
日程表の作成 → 予算レポートの作成を順次実行する。

実行方法:
    adk run travel_planner
    # Workflow rootのため、v2.2.0では adk run での確認を推奨
"""

from google.adk import Agent
from google.adk.agents import ParallelAgent, SequentialAgent

from . import tools

# --- 調査フェーズ: 3つの専門エージェントが並列で情報を収集 ---

spot_researcher = Agent(
    model="gemini-3.5-flash",
    name="spot_researcher",
    instruction=(
        "あなたは観光スポットの専門家です。"
        "ユーザーの旅行先と好みに基づいて、おすすめの観光スポットを検索してください。"
        "検索結果をもとに、各スポットの特徴と所要時間を簡潔にまとめてください。"
    ),
    tools=[tools.search_spots],
    output_key="spots_result",
)

restaurant_researcher = Agent(
    model="gemini-3.5-flash",
    name="restaurant_researcher",
    instruction=(
        "あなたはグルメの専門家です。"
        "ユーザーの旅行先と食の好みに基づいて、おすすめのレストランを検索してください。"
        "検索結果をもとに、各レストランの特徴と価格帯を簡潔にまとめてください。"
    ),
    tools=[tools.search_restaurants],
    output_key="restaurants_result",
)

transport_researcher = Agent(
    model="gemini-3.5-flash",
    name="transport_researcher",
    instruction=(
        "あなたは交通手段の専門家です。"
        "ユーザーの出発地と目的地に基づいて、利用可能な交通手段を検索してください。"
        "検索結果をもとに、各手段の所要時間・料金・おすすめ度を簡潔にまとめてください。"
    ),
    tools=[tools.search_transport],
    output_key="transport_result",
)

# 3つの調査エージェントを並列実行
research_phase = ParallelAgent(
    name="research_phase",
    sub_agents=[spot_researcher, restaurant_researcher, transport_researcher],
)

# --- 計画フェーズ: 調査結果を統合して計画を立てる ---

schedule_planner = Agent(
    model="gemini-3.5-flash",
    name="schedule_planner",
    instruction=(
        "あなたは旅行スケジュールの作成担当です。"
        "これまでの調査結果（観光スポット・レストラン・交通手段）をもとに、"
        "効率的な日程表を作成してください。"
        "以下の形式で出力してください:\n"
        "- 日ごとに時間帯を区切る（午前・昼・午後・夕方・夜）\n"
        "- 各時間帯にスポットまたはレストランを配置\n"
        "- 移動時間も考慮する"
    ),
    output_key="schedule_result",
)

budget_reporter = Agent(
    model="gemini-3.5-flash",
    name="budget_reporter",
    instruction=(
        "あなたは旅行予算の計算担当です。"
        "これまでの調査結果と作成された日程表をもとに、"
        "旅行全体の概算予算を計算してください。"
        "以下の項目ごとに金額を算出し、合計を出してください:\n"
        "- 交通費（往復 + 現地移動）\n"
        "- 食費（朝食・昼食・夕食 × 日数）\n"
        "- 入場料・アクティビティ費\n"
        "- 合計（税・チップ込みの概算）"
    ),
    output_key="budget_result",
)

# --- ルートエージェント: 全体を順次実行 ---

root_agent = SequentialAgent(
    name="travel_planner",
    sub_agents=[research_phase, schedule_planner, budget_reporter],
    description="旅行プランナー: 調査→日程作成→予算計算を順次実行するエージェント",
)
