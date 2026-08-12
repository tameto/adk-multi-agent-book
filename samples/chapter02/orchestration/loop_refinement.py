# loop_refinement.py
# 2-4-3. LoopAgent: 繰り返し実行（完全版）
# コード生成 → レビューの自己修正ループを構築する（最大3回）。
# LoopAgentはTemplate Workflowとして利用できる。実運用ではmax_iterationsなどの上限を必ず設定する。

from google.adk import Agent
from google.adk.agents import LoopAgent

# コード生成エージェント
code_generator = Agent(
    name="code_generator",
    model="gemini-3.5-flash",
    instruction="""ユーザーの要件に基づいてPythonコードを生成してください。
レビューフィードバックがある場合は、それを反映して修正してください。""",
    output_key="generated_code",
)

# コードレビューエージェント
code_reviewer = Agent(
    name="code_reviewer",
    model="gemini-3.5-flash",
    instruction="""生成されたコードをレビューしてください。
問題がなければ「APPROVED」とだけ応答してください。
問題がある場合は、具体的な修正点を指摘してください。""",
    output_key="review_result",
)

# ループ: 生成→レビューを繰り返す（最大3回）
code_loop = LoopAgent(
    name="code_refinement_loop",
    sub_agents=[code_generator, code_reviewer],
    max_iterations=3,
)

# adk run / adk web から参照できるようroot_agentとして公開する（補完）
root_agent = code_loop

if __name__ == "__main__":
    # 定義内容の確認（対話実行は adk run / adk web を使用）
    print(f"ループエージェント: {code_loop.name}（最大{code_loop.max_iterations}回）")
    print(f"サブエージェント: {[agent.name for agent in code_loop.sub_agents]}")
