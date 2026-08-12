# sequential_pipeline.py
# 2-4-1. SequentialAgent: 順次実行（完全版）
# データ収集 → データ分析 → レポート生成のパイプラインを構築する。
# SequentialAgentはTemplate Workflowとして利用できる。複雑な分岐や再開が必要な場合はWorkflow Runtimeを検討する。

from google.adk import Agent
from google.adk.agents import SequentialAgent

# ステップ1: データ収集
collector = Agent(
    name="data_collector",
    model="gemini-3.5-flash",
    instruction="ユーザーの質問に関連するデータを収集してください。",
    output_key="collected_data",
)

# ステップ2: データ分析
analyzer = Agent(
    name="data_analyzer",
    model="gemini-3.5-flash",
    instruction="収集されたデータを分析し、主要な傾向とインサイトを抽出してください。",
    output_key="analysis_result",
)

# ステップ3: レポート生成
reporter = Agent(
    name="report_generator",
    model="gemini-3.5-flash",
    instruction="分析結果をもとに、経営層向けのレポートを作成してください。",
    output_key="final_report",
)

# パイプライン構築
pipeline = SequentialAgent(
    name="analysis_pipeline",
    sub_agents=[collector, analyzer, reporter],
)

# adk run / adk web から参照できるようroot_agentとして公開する（補完）
root_agent = pipeline

if __name__ == "__main__":
    # 定義内容の確認（対話実行は adk run / adk web を使用）
    print(f"パイプライン: {pipeline.name}")
    print(f"サブエージェント: {[agent.name for agent in pipeline.sub_agents]}")
