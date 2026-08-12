# 5-4-4. ツールコールバックによる操作制御
"""ツールガードレールの実装"""
import re

from google.adk.tools import BaseTool, ToolContext


def before_tool_guardrail(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
) -> dict | None:
    """ツール呼び出し前のガードレール

    Returns:
        None: ツール呼び出しを許可
        dict: ツール呼び出しをブロックし、この結果を返す
    """
    tool_name = tool.name

    # 高リスクツールの制限
    high_risk_tools = ["delete_user", "transfer_funds", "execute_sql"]
    if tool_name in high_risk_tools:
        # レート制限チェック
        call_count = tool_context.state.get(f"_tool_call_count_{tool_name}", 0)
        if call_count >= 3:
            return {
                "error": f"ツール '{tool_name}' の呼び出し回数が"
                "上限に達しました。管理者に連絡してください。"
            }
        tool_context.state[f"_tool_call_count_{tool_name}"] = call_count + 1

    # SQLインジェクション検出
    if tool_name == "execute_sql":
        query = args.get("query", "")
        if _detect_sql_injection(query):
            return {
                "error": "安全でないSQLクエリが検出されました。"
                "パラメータ化クエリを使用してください。"
            }

    # パス・トラバーサル検出
    if tool_name in ["read_file", "write_file"]:
        file_path = args.get("path", "")
        if ".." in file_path or file_path.startswith("/etc"):
            return {
                "error": "不正なファイルパスが検出されました。"
            }

    return None


def after_tool_guardrail(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
    tool_response: dict,
) -> dict | None:
    """ツール呼び出し後のガードレール

    Returns:
        None: ツール結果をそのまま使用
        dict: 修正されたツール結果
    """
    # ツール結果からのPII漏えいを防止
    if isinstance(tool_response, dict):
        sanitized = _sanitize_tool_result(tool_response)
        if sanitized != tool_response:
            return sanitized

    return None


def _detect_sql_injection(query: str) -> bool:
    """SQLインジェクションの兆候を検出する"""
    dangerous_patterns = [
        "DROP TABLE",
        "DELETE FROM",
        "UPDATE .* SET",
        "INSERT INTO",
        "--",
        ";",
        "UNION SELECT",
    ]
    query_upper = query.upper()
    return any(p in query_upper for p in dangerous_patterns)


def _sanitize_tool_result(result: dict) -> dict:
    """ツール結果から機密情報を除去する"""
    sanitized = {}
    for key, value in result.items():
        if isinstance(value, str):
            # クレジットカード番号のマスキング
            value = re.sub(
                r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}',
                "[カード番号]",
                value,
            )
            # APIキーのマスキング
            value = re.sub(
                r'(?:api[_-]?key|token|secret)[=:]\s*\S+',
                "[認証情報]",
                value,
                flags=re.IGNORECASE,
            )
        sanitized[key] = value
    return sanitized
