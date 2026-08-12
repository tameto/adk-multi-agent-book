# samples/chapter10/indirect_injection_guard.py
"""間接プロンプトインジェクション対策の実装例（10-2-2 完全版）

after_tool_callback でツール結果を検証・サニタイズし、データソース経由で
注入された悪意あるプロンプトをLLMのコンテキストに渡る前に除去する。
紙面で省略したパターンリストの全項目と、dict 内の文字列値をサニタイズする処理を含む完全版。
他のガードレールと統合した実装は secure_agent/callbacks.py を参照。
"""
import re

from google.adk.tools import BaseTool, ToolContext


# ツール結果に含まれる危険パターン
TOOL_RESULT_PATTERNS: list[re.Pattern] = [
    re.compile(r"\[SYSTEM\]", re.IGNORECASE),
    re.compile(r"\[INST\]", re.IGNORECASE),
    re.compile(r"<\|im_start\|>system", re.IGNORECASE),
    re.compile(
        # 修飾語の繰り返しを許容し "ignore all previous instructions" も
        # 検出する（prompt_injection_guard.py と同一パターン）
        r"(ignore|disregard)\s+((all|previous|above|prior)\s+)+"
        r"(instructions|rules|context)",
        re.IGNORECASE,
    ),
]


def sanitize_tool_output(text: str) -> str:
    """ツール出力から危険なパターンを除去する"""
    sanitized = text
    for pattern in TOOL_RESULT_PATTERNS:
        sanitized = pattern.sub("[FILTERED]", sanitized)
    return sanitized


def after_tool_guard(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
    tool_response: dict,
) -> dict | None:
    """ツール実行後にレスポンスを検証・サニタイズするガードレール

    シグネチャ: (BaseTool, dict, ToolContext, dict) -> Optional[dict]
    検出した場合はサニタイズ後の dict を返し、検出なしなら None を返す。"""
    if not isinstance(tool_response, dict):
        return None

    sanitized: dict = {}
    for key, value in tool_response.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_tool_output(value)
        else:
            sanitized[key] = value

    # 何らかの置換が発生した場合のみサニタイズ済みを返す
    return sanitized if sanitized != tool_response else None
