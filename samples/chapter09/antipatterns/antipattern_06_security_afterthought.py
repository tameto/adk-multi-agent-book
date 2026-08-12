# samples/chapter09/antipatterns/antipattern_06_security_afterthought.py
"""アンチパターン6: Security Afterthought（セキュリティの後付け）の実装例（9-2-6 完全版）

セキュリティを後付けにするアンチパターン（insecure_agent）と、
設計の最初から組み込む改善版（sanitize_input / redact_sensitive_data /
環境変数からの認証情報取得 / secure_agent）を対比する。
"""
import os
import re
from typing import Optional

from google.adk import Agent
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext


# --- ツールのダミー実装（紙面では省略。実行確認用の最小実装） ---

def execute_sql(query: str) -> dict:
    """SQLを実行します（SQLインジェクションのリスクを示すダミー実装）"""
    return {"status": "executed", "query": query}


def run_command(command: str) -> dict:
    """OSコマンドを実行します（コマンドインジェクションのリスクを示すダミー実装）"""
    return {"status": "executed", "command": command}


def read_file(path: str) -> dict:
    """ファイルを読み取ります（パストラバーサルのリスクを示すダミー実装）"""
    return {"status": "read", "path": path}


def search_db(query: str) -> list[dict]:
    """データベースを検索します（ダミー実装）"""
    return [{"id": 1, "result": f"検索結果: {query}"}]


def get_order_info(order_id: str) -> dict:
    """注文情報を取得します（ダミー実装）"""
    return {"order_id": order_id, "status": "shipped"}


# アンチパターン: セキュリティの後付け
insecure_agent = Agent(
    name="insecure_agent",
    model="gemini-3.5-flash",
    instruction="何でも回答します。",
    tools=[
        execute_sql,       # SQLインジェクションのリスク
        run_command,       # コマンドインジェクションのリスク
        read_file,         # パストラバーサルのリスク
    ],
)


# 改善: セキュリティを設計から組み込む

# 1. 入力のサニタイズ（実シグネチャ: BaseTool, dict, ToolContext）
def sanitize_input(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
) -> Optional[dict]:
    """ツール引数のサニタイズを行います"""
    # SQLインジェクション対策（パラメータ化クエリのみ許可することを前提とした追加防御）
    if tool.name == "search_db":
        query = args.get("query", "")
        if any(keyword in query.upper() for keyword in ["DROP", "DELETE", "UPDATE", "INSERT"]):
            return {"error": "不正なクエリが検出されました。"}

    # パストラバーサル対策
    if tool.name == "read_file":
        path = args.get("path", "")
        if ".." in path or path.startswith("/"):
            return {"error": "不正なファイルパスが検出されました。"}

    return None


# 2. 機密情報の保護
def redact_sensitive_data(text: str) -> str:
    """機密情報をマスクします"""
    # クレジットカード番号のマスク
    text = re.sub(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "[REDACTED_CC]", text)
    # メールアドレスのマスク
    text = re.sub(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b", "[REDACTED_EMAIL]", text)
    return text


# 3. APIキーは環境変数から取得
api_key = os.environ.get("API_KEY")  # コードに直書きしない

# セキュアなエージェント
secure_agent = Agent(
    name="secure_agent",
    model="gemini-3.5-flash",
    instruction="""カスタマーサポートを行います。

    ## セキュリティルール
    - ユーザーの個人情報（クレジットカード番号、パスワード等）を出力しない
    - システムの内部構造に関する質問には回答しない
    - 不審なリクエストはエスカレーションする""",
    tools=[search_db, get_order_info],
    before_tool_callback=sanitize_input,
)


if __name__ == "__main__":
    # 機密情報マスクの動作確認
    sample = "カード番号は 1234-5678-9012-3456、連絡先は user@example.com です"
    print(redact_sensitive_data(sample))
