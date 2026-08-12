# custom_agent.py
# 2-4-5. BaseAgent継承: カスタムエージェントで独自ロジック（完全版）
# 条件分岐パイプラインと、多数決（Voting）の2つの実装例。

from typing import AsyncIterator

from google.adk import Agent
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event


class ConditionalPipelineAgent(BaseAgent):
    """条件に基づいて異なるパイプラインを実行するカスタムエージェント"""

    fast_path: BaseAgent      # 簡易パイプライン
    detailed_path: BaseAgent  # 詳細パイプライン
    classifier: BaseAgent     # 分類エージェント

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncIterator[Event]:
        """カスタム実行ロジック"""
        # ステップ1: 入力を分類
        async for event in self.classifier.run_async(ctx):
            yield event

        # ステップ2: 分類結果に基づいてパイプラインを選択
        complexity = ctx.session.state.get("complexity", "simple")

        if complexity == "complex":
            # 複雑な入力 → 詳細パイプライン
            async for event in self.detailed_path.run_async(ctx):
                yield event
        else:
            # 簡単な入力 → 簡易パイプライン
            async for event in self.fast_path.run_async(ctx):
                yield event


class VotingAgent(BaseAgent):
    """複数のエージェントの回答から多数決で最終回答を決定する"""

    voters: list[BaseAgent]
    judge: BaseAgent  # 多数決の判定を行うエージェント

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncIterator[Event]:
        # 全投票者を並列実行（簡略化のため順次で示す）
        for voter in self.voters:
            async for event in voter.run_async(ctx):
                yield event

        # 判定エージェントが最終回答を決定
        async for event in self.judge.run_async(ctx):
            yield event


# --- ここから補完: カスタムエージェントの組み立て例（紙面には未掲載） ---

# 入力の複雑さを分類するエージェント
classifier = Agent(
    name="classifier",
    model="gemini-3.5-flash",
    instruction="""ユーザーの入力の複雑さを判定し、simple または complex のどちらかだけを出力してください。""",
    output_key="complexity",
)

# 簡易パイプライン（短いInstructionで即答）
fast_path = Agent(
    name="fast_path",
    model="gemini-3.5-flash",
    instruction="ユーザーの質問に簡潔に回答してください。",
)

# 詳細パイプライン（同じモデルで段階的に回答）
detailed_path = Agent(
    name="detailed_path",
    model="gemini-3.5-flash",
    instruction="ユーザーの質問を分解し、根拠を示しながら詳細に回答してください。",
)

root_agent = ConditionalPipelineAgent(
    name="conditional_pipeline",
    classifier=classifier,
    fast_path=fast_path,
    detailed_path=detailed_path,
)

if __name__ == "__main__":
    # 定義内容の確認（対話実行は adk run / adk web を使用）
    print(f"カスタムエージェント: {root_agent.name}")
    print(f"分類: {classifier.name} → fast: {fast_path.name} / detailed: {detailed_path.name}")
