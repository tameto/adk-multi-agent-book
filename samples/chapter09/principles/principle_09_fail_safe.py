# samples/chapter09/principles/principle_09_fail_safe.py
"""原則9: フェイルセーフ（Fail-Safe Design）の実装例（9-1-9 完全版）

3つのレイヤーでフェイルセーフを実装する。
- レイヤー1: ツールレベルのリトライとフォールバック
- レイヤー2: エージェントレベルのループ検知
- レイヤー3: システムレベルのKill Switch
"""
from typing import Optional

from google.adk import Agent
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext


# --- 外部サービスのダミー実装（紙面では省略。実行確認用の最小実装） ---

class _DummySearchEngine:
    """検索エンジンのダミー実装。本番ではAPIクライアントに置き換える"""

    def __init__(self, name: str) -> None:
        self.name = name

    def search(self, query: str, timeout: float = 5.0) -> list[dict]:
        """検索を実行します（ダミー実装。失敗時はTimeoutErrorを送出する想定）"""
        return [{"engine": self.name, "result": f"{query} の検索結果"}]


class _DummyCache:
    """インメモリキャッシュのダミー実装。本番ではRedis等に置き換える"""

    def __init__(self) -> None:
        self._store: dict[str, object] = {}

    def get(self, key: str) -> object | None:
        return self._store.get(key)

    def set(self, key: str, value: object, ttl: int = 3600) -> None:
        self._store[key] = value


class _DummyFeatureFlags:
    """フィーチャーフラグストアのダミー実装。本番では外部ストアから取得する"""

    def is_enabled(self, flag_name: str, **attributes: str) -> bool:
        return False  # デフォルトはKill Switch無効


primary_search_engine = _DummySearchEngine("primary")
secondary_search_engine = _DummySearchEngine("secondary")
cache = _DummyCache()
feature_flags = _DummyFeatureFlags()


# レイヤー1: ツールレベルのリトライとフォールバック

def search_with_fallback(query: str) -> dict:
    """フォールバック付きの検索ツール"""
    # プライマリ検索エンジンを試行
    try:
        results = primary_search_engine.search(query, timeout=5.0)
        return {"source": "primary", "results": results}
    except TimeoutError:
        pass  # フォールバックへ

    # フォールバック: セカンダリ検索エンジン
    try:
        results = secondary_search_engine.search(query, timeout=10.0)
        return {"source": "secondary", "results": results}
    except TimeoutError:
        pass  # キャッシュへ

    # 最終フォールバック: キャッシュから返す
    cached = cache.get(f"search:{query}")
    if cached:
        return {"source": "cache", "results": cached, "warning": "キャッシュからの結果です"}

    # すべて失敗
    return {"error": "検索サービスが一時的に利用できません。しばらくしてから再試行してください。"}


# レイヤー2: エージェントレベルのループ検知

MAX_TOOL_CALLS_PER_TURN = 10  # 1ターンあたりの最大ツール呼び出し回数
MAX_CONSECUTIVE_ERRORS = 3     # 連続エラーの上限


def loop_detection_callback(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
) -> Optional[dict]:
    """無限ループとエラーの連続を検知して停止します"""
    # ツール呼び出しカウンターを更新
    call_count = tool_context.state.get("_tool_call_count", 0) + 1
    tool_context.state["_tool_call_count"] = call_count

    # 最大呼び出し回数を超えた場合は停止
    if call_count > MAX_TOOL_CALLS_PER_TURN:
        return {
            "error": f"安全制限: 1ターンあたりのツール呼び出し回数が上限（{MAX_TOOL_CALLS_PER_TURN}）に達しました。",
            "action": "ユーザーに状況を説明し、手動での対応を促してください。",
        }

    # 同一ツール・同一引数の連続呼び出しを検知
    last_call = tool_context.state.get("_last_tool_call")
    current_call = f"{tool.name}:{args}"

    if last_call == current_call:
        repeat_count = tool_context.state.get("_repeat_count", 0) + 1
        tool_context.state["_repeat_count"] = repeat_count

        if repeat_count >= MAX_CONSECUTIVE_ERRORS:
            return {
                "error": f"ループ検知: {tool.name}が同じ引数で{repeat_count}回連続で呼び出されました。",
                "action": "異なるアプローチを試みるか、ユーザーに確認してください。",
            }
    else:
        tool_context.state["_repeat_count"] = 0

    tool_context.state["_last_tool_call"] = current_call
    return None


# レイヤー3: システムレベルのKill Switch

def kill_switch_callback(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
) -> Optional[dict]:
    """Kill Switchが有効な場合、すべてのツール呼び出しを停止します"""
    # Kill Switchの状態を外部ストアから取得
    kill_switch_active = feature_flags.is_enabled(
        "agent_kill_switch",
        agent_name=tool_context.agent_name,
    )

    if kill_switch_active:
        return {
            "error": "システム管理者によりエージェントの操作が一時停止されています。",
            "action": "ユーザーに手動での対応をお願いしてください。",
        }
    return None


# フェイルセーフを統合したエージェント
safe_agent = Agent(
    name="safe_agent",
    model="gemini-3.5-flash",
    instruction="""ユーザーの検索リクエストに対応します。
    エラーが発生した場合は、ユーザーにわかりやすく状況を説明してください。
    同じ操作を3回以上繰り返さないでください。""",
    tools=[search_with_fallback],
    before_tool_callback=kill_switch_callback,  # Kill Switchを最優先でチェック
)
