# samples/chapter06/tool_audit.py
"""ツール呼び出しの監査ログ"""

import json
import logging
from datetime import datetime, timezone

from google.adk.tools import BaseTool
from google.adk.tools.tool_context import ToolContext

logger = logging.getLogger("tool_audit")


async def audit_tool_callback(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
):
    """ツール呼び出しを監査ログに記録するコールバック"""
    audit_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent_name": tool_context.agent_name,
        "tool_name": tool.name,
        "tool_input": args,
    }
    # 実運用では session_id/user_id も tool_context から取得してログに含める

    # 構造化ログとして出力（Cloud Loggingと統合可能）
    logger.info(json.dumps(audit_entry, ensure_ascii=False))

    return None  # ツール呼び出しを続行
