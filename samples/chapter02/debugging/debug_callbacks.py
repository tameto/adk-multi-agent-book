# debug_callbacks.py
# 2-5-3. デバッグ手法: コールバックによるログ挿入（完全版）
# before_model / after_model / before_tool の3つのコールバックで
# LLM呼び出しとツール呼び出しの入出力をログに出力する。

import logging

from google.adk import Agent

logger = logging.getLogger(__name__)


def debug_before_model(callback_context, llm_request):
    """LLM呼び出し前のデバッグログ

    ADK v2.2.0 は before_model_callback を
    callback_context=..., llm_request=... のキーワード引数で呼ぶ。
    第1引数名は callback_context に合わせる必要がある。
    """
    logger.debug(f"[{callback_context.agent_name}] LLM呼び出し前")
    # State は dict() では変換できない（keys()非対応）。to_dict() を使う。
    logger.debug(f"  State: {callback_context.state.to_dict()}")
    logger.debug(f"  入力トークン数（概算）: {len(str(llm_request)) // 4}")
    return None


def debug_after_model(callback_context, llm_response):
    """LLM呼び出し後のデバッグログ"""
    logger.debug(f"[{callback_context.agent_name}] LLM呼び出し後")
    if llm_response.content and llm_response.content.parts:
        text = llm_response.content.parts[0].text
        logger.debug(f"  出力（先頭200文字）: {text[:200]}")
    return None


def debug_before_tool(tool, args, tool_context):
    """ツール実行前のデバッグログ（実シグネチャ: BaseTool, dict, ToolContext）"""
    logger.debug(f"[{tool_context.agent_name}] ツール呼び出し: {tool.name}")
    logger.debug(f"  引数: {args}")
    return None


agent = Agent(
    name="debug_agent",
    model="gemini-3.5-flash",
    # instructionは紙面では "..." と省略。以下は補完した例
    instruction="ユーザーの質問に回答してください。",
    before_model_callback=debug_before_model,
    after_model_callback=debug_after_model,
    before_tool_callback=debug_before_tool,
)

# adk run / adk web から参照できるようroot_agentとして公開する（補完）
root_agent = agent

if __name__ == "__main__":
    # 定義内容の確認（詳細ログ付きの対話確認は adk web . --log_level debug 等を使用）
    logging.basicConfig(level=logging.DEBUG)
    print(f"エージェント: {agent.name}")
    print("コールバック: debug_before_model / debug_after_model / debug_before_tool")
