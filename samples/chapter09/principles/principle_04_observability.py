# samples/chapter09/principles/principle_04_observability.py
"""原則4: 可観測性（Observability）の実装例（9-1-4 完全版）

ADK標準のOpenTelemetryトレーシングに加えて、
コールバックでカスタムメトリクス（呼び出し回数・レイテンシ・トークン量）を記録する。
"""
import logging
import time

from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from opentelemetry import metrics

# ロガーの設定
logger = logging.getLogger(__name__)


# --- ツールのダミー実装（紙面では省略。実行確認用の最小実装） ---

def search_products(query: str) -> list[dict]:
    """商品を検索します（ダミー実装）"""
    return [{"id": 1, "name": "商品A", "price": 1000}]


# OpenTelemetryのメトリクス
meter = metrics.get_meter("agent_metrics")
tool_call_counter = meter.create_counter(
    "agent.tool_calls",
    description="ツール呼び出し回数",
)
tool_latency_histogram = meter.create_histogram(
    "agent.tool_latency_ms",
    description="ツール実行のレイテンシ（ミリ秒）",
)
token_usage_counter = meter.create_counter(
    "agent.token_usage",
    description="トークン使用量",
)


# ツール呼び出し前のコールバック（計測開始）
def before_tool_with_metrics(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
):
    """ツール実行前にメトリクスを記録します"""
    # 開始時刻をStateに保存
    tool_context.state["_tool_start_time"] = time.time()

    # ツール呼び出しをカウント
    tool_call_counter.add(
        1,
        attributes={
            "agent_name": tool_context.agent_name,
            "tool_name": tool.name,
        },
    )

    logger.info(
        "ツール呼び出し開始",
        extra={
            "agent_name": tool_context.agent_name,
            "tool_name": tool.name,
            "tool_args": args,
        },
    )
    return None  # 通常通り実行を継続


# ツール呼び出し後のコールバック（計測終了）
def after_tool_with_metrics(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
    tool_response: dict,
):
    """ツール実行後にレイテンシを記録します"""
    start_time = tool_context.state.get("_tool_start_time", time.time())
    latency_ms = (time.time() - start_time) * 1000

    # レイテンシをヒストグラムに記録
    tool_latency_histogram.record(
        latency_ms,
        attributes={
            "agent_name": tool_context.agent_name,
            "tool_name": tool.name,
        },
    )

    logger.info(
        "ツール呼び出し完了",
        extra={
            "agent_name": tool_context.agent_name,
            "tool_name": tool.name,
            "latency_ms": latency_ms,
        },
    )
    return None


# LLM応答後のコールバック（トークン使用量を記録）
def after_model_with_metrics(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
):
    """LLM応答後にトークン使用量を記録します"""
    usage = llm_response.usage_metadata
    if usage:
        token_usage_counter.add(
            usage.total_token_count or 0,
            attributes={
                "agent_name": callback_context.agent_name,
                "token_type": "total",
            },
        )

    logger.info(
        "LLM応答受信",
        extra={
            "agent_name": callback_context.agent_name,
            "input_tokens": usage.prompt_token_count if usage else 0,
            "output_tokens": usage.candidates_token_count if usage else 0,
        },
    )
    return None


# 可観測性を組み込んだエージェント
observable_agent = Agent(
    name="observable_agent",
    model="gemini-3.5-flash",
    instruction="ユーザーの質問に回答します。",
    tools=[search_products],
    before_tool_callback=before_tool_with_metrics,
    after_tool_callback=after_tool_with_metrics,
    after_model_callback=after_model_with_metrics,
)
