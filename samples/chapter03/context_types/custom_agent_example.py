# samples/chapter03/context_types/custom_agent_example.py
# 3-2-2. InvocationContext（完全版）
# InvocationContext クラス自体はADK本体（google.adk.agents.invocation_context）が
# 提供するクラスのため、本ファイルには収録しない。
"""InvocationContextを直接操作するカスタムエージェントのサンプル"""
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types
from typing import AsyncIterator


class MyCustomAgent(BaseAgent):
    """InvocationContextを直接操作するカスタムエージェント"""

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncIterator[Event]:
        # 実行IDを使ったログ出力
        print(f"実行開始: {ctx.invocation_id}")

        # セッションからState値を読み取る
        user_tier = ctx.session.state.get("user_tier", "free")

        # RunConfigからLLM呼び出し回数の上限を参照する
        max_llm_calls = ctx.run_config.max_llm_calls

        # カスタムロジック...
        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            content=types.Content(
                parts=[types.Part(text=f"ユーザーティア: {user_tier}")]
            ),
        )


# 補完: 紙面ではクラス定義のみ掲載。Runnerに渡す際はインスタンス化して使う。
my_custom_agent = MyCustomAgent(name="my_custom_agent")
