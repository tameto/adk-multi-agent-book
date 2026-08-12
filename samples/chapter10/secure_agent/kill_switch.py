# samples/chapter10/secure_agent/kill_switch.py
"""Kill Switch実装

エージェントの緊急停止機構。グローバル、エージェント単位、ツール単位で
停止を制御できる。LLMの判断に依存しない、コードレベルの強制停止。
"""
import logging
import threading

logger = logging.getLogger(__name__)


class KillSwitch:
    """緊急停止フラグの管理

    スレッドセーフな実装。本番環境では外部ストア（Redis等）に
    置き換えることを推奨。
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        # グローバルKill Switch: Trueで全エージェント停止
        self._global_kill = False
        # エージェント単位のKill Switch
        self._agent_kills: set[str] = set()
        # ツール単位のKill Switch
        self._tool_kills: set[str] = set()

    # --- 状態確認 ---

    def is_globally_killed(self) -> bool:
        """グローバルKill Switchの状態を返す"""
        with self._lock:
            return self._global_kill

    def is_agent_killed(self, agent_name: str) -> bool:
        """指定エージェントが停止状態か判定する"""
        with self._lock:
            return self._global_kill or agent_name in self._agent_kills

    def is_tool_killed(self, tool_name: str) -> bool:
        """指定ツールが停止状態か判定する"""
        with self._lock:
            return self._global_kill or tool_name in self._tool_kills

    # --- 停止操作 ---

    def activate_global(self, reason: str) -> None:
        """全エージェントを停止する"""
        with self._lock:
            self._global_kill = True
        logger.critical("グローバルKill Switch発動: %s", reason)

    def activate_agent(self, agent_name: str, reason: str) -> None:
        """指定エージェントを停止する"""
        with self._lock:
            self._agent_kills.add(agent_name)
        logger.critical(
            "エージェント '%s' を停止: %s", agent_name, reason
        )

    def activate_tool(self, tool_name: str, reason: str) -> None:
        """指定ツールを停止する"""
        with self._lock:
            self._tool_kills.add(tool_name)
        logger.warning("ツール '%s' を停止: %s", tool_name, reason)

    # --- 復元操作 ---

    def deactivate_global(self) -> None:
        """グローバルKill Switchを解除する"""
        with self._lock:
            self._global_kill = False
        logger.info("グローバルKill Switch解除")

    def deactivate_agent(self, agent_name: str) -> None:
        """指定エージェントの停止を解除する"""
        with self._lock:
            self._agent_kills.discard(agent_name)
        logger.info("エージェント '%s' の停止を解除", agent_name)

    def deactivate_tool(self, tool_name: str) -> None:
        """指定ツールの停止を解除する"""
        with self._lock:
            self._tool_kills.discard(tool_name)
        logger.info("ツール '%s' の停止を解除", tool_name)


# グローバルインスタンス
kill_switch = KillSwitch()
