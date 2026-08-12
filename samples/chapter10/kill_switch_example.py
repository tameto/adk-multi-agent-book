# samples/chapter10/kill_switch_example.py
"""Kill Switch（緊急停止機構）の実装例（10-4-1 完全版）

グローバル / エージェント単位 / ツール単位の3スコープで停止を制御する KillSwitch と、
before_model_callback / before_tool_callback での強制停止ポイントを実装する。
紙面で省略した deactivate 系・activate 系メソッドを含む完全版。
統合版は secure_agent/kill_switch.py を参照。
"""
from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools import ToolContext, BaseTool
from google.genai import types
import threading


class KillSwitch:
    """エージェントの緊急停止機構"""

    def __init__(self):
        self._lock = threading.Lock()
        # グローバルKill Switch: Trueで全エージェント停止
        self._global_kill = False
        # エージェント単位のKill Switch
        self._agent_kills: set[str] = set()
        # ツール単位のKill Switch
        self._tool_kills: set[str] = set()

    def activate_global(self) -> None:
        """全エージェントを停止する"""
        with self._lock:
            self._global_kill = True

    def deactivate_global(self) -> None:
        """全エージェントの停止を解除する"""
        with self._lock:
            self._global_kill = False

    def activate_agent(self, agent_name: str) -> None:
        """特定のエージェントを停止する"""
        with self._lock:
            self._agent_kills.add(agent_name)

    def deactivate_agent(self, agent_name: str) -> None:
        """特定のエージェントの停止を解除する"""
        with self._lock:
            self._agent_kills.discard(agent_name)

    def activate_tool(self, tool_name: str) -> None:
        """特定のツールを無効化する"""
        with self._lock:
            self._tool_kills.add(tool_name)

    def deactivate_tool(self, tool_name: str) -> None:
        """特定のツールの無効化を解除する"""
        with self._lock:
            self._tool_kills.discard(tool_name)

    def is_agent_killed(self, agent_name: str) -> bool:
        """エージェントが停止状態かを判定する"""
        with self._lock:
            return self._global_kill or agent_name in self._agent_kills

    def is_tool_killed(self, tool_name: str) -> bool:
        """ツールが無効化されているかを判定する"""
        with self._lock:
            return self._global_kill or tool_name in self._tool_kills


# グローバルなKill Switchインスタンス
kill_switch = KillSwitch()


def before_model_kill_switch(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> LlmResponse | None:
    """モデル呼び出し前のKill Switchチェック"""
    agent_name = callback_context.agent_name
    if kill_switch.is_agent_killed(agent_name):
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(
                    text="現在、このエージェントはメンテナンス中のため利用できません。"
                    "しばらく時間をおいてから再度お試しください。"
                )],
            )
        )
    return None


def before_tool_kill_switch(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
) -> dict | None:
    """ツール呼び出し前のKill Switchチェック

    シグネチャ: (BaseTool, dict, ToolContext) -> Optional[dict]"""
    if kill_switch.is_tool_killed(tool.name):
        return {
            "error": f"ツール '{tool.name}' は現在無効化されています。"
        }
    return None
