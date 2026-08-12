# samples/chapter10/secure_agent/escalation.py
"""段階的エスカレーション実装（10-4-2節）

異常の深刻度に応じて防御を段階的に強化する。
Level 1（警告）→ Level 2（制限）→ Level 3（停止）→ Level 4（人間介入）と
昇格し、誤検知による過剰な停止を避けつつ本物の脅威には即座に対応する。
"""
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import IntEnum

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types

logger = logging.getLogger(__name__)

JST = timezone(timedelta(hours=9))


class EscalationLevel(IntEnum):
    """エスカレーションレベル"""
    NORMAL = 0
    WARNING = 1
    RESTRICTED = 2
    STOPPED = 3
    HUMAN_ESCALATION = 4


@dataclass
class UserIncidentTracker:
    """ユーザーごとのインシデント追跡"""
    warning_count: int = 0
    last_warning_time: datetime | None = None
    restricted_tools: set[str] = field(default_factory=set)
    current_level: EscalationLevel = EscalationLevel.NORMAL


class EscalationManager:
    """段階的エスカレーションを管理する"""

    def __init__(self):
        self._trackers: dict[str, UserIncidentTracker] = {}
        self.warning_to_restrict_threshold = 3       # 警告3回で制限に昇格
        self.warning_window = timedelta(minutes=10)  # 警告カウントのウィンドウ

    def get_tracker(self, user_id: str) -> UserIncidentTracker:
        """ユーザーのインシデントトラッカーを取得する"""
        if user_id not in self._trackers:
            self._trackers[user_id] = UserIncidentTracker()
        return self._trackers[user_id]

    def escalate(self, user_id: str, reason: str) -> EscalationLevel:
        """インシデントを報告し、エスカレーションレベルを判定する"""
        tracker = self.get_tracker(user_id)
        now = datetime.now(JST)

        # ウィンドウ外の古い警告はリセット
        if (
            tracker.last_warning_time
            and now - tracker.last_warning_time > self.warning_window
        ):
            tracker.warning_count = 0

        tracker.warning_count += 1
        tracker.last_warning_time = now

        # 閾値に基づいてレベルを昇格
        if tracker.warning_count >= self.warning_to_restrict_threshold:
            if tracker.current_level < EscalationLevel.RESTRICTED:
                tracker.current_level = EscalationLevel.RESTRICTED
                logger.warning(
                    "ユーザー %s をLevel 2（制限）に昇格: %s", user_id, reason
                )
        elif tracker.current_level < EscalationLevel.WARNING:
            tracker.current_level = EscalationLevel.WARNING
            logger.warning(
                "ユーザー %s をLevel 1（警告）に設定: %s", user_id, reason
            )
        return tracker.current_level

    def force_stop(self, user_id: str, reason: str) -> None:
        """強制的にLevel 3（停止）に設定する"""
        tracker = self.get_tracker(user_id)
        tracker.current_level = EscalationLevel.STOPPED
        logger.critical(
            "ユーザー %s を強制停止（Level 3）: %s", user_id, reason
        )

    def escalate_to_human(self, user_id: str, reason: str) -> None:
        """Level 4（人間介入）に設定する"""
        tracker = self.get_tracker(user_id)
        tracker.current_level = EscalationLevel.HUMAN_ESCALATION
        logger.critical(
            "ユーザー %s を人間介入（Level 4）に設定: %s", user_id, reason
        )


# エスカレーションマネージャーのインスタンス
escalation_mgr = EscalationManager()


def escalation_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> LlmResponse | None:
    """エスカレーションレベルに基づいてリクエストを制御する

    before_model_callback に登録して使う。
    """
    user_id = callback_context.state.get("user_id", "unknown")
    tracker = escalation_mgr.get_tracker(user_id)

    if tracker.current_level == EscalationLevel.STOPPED:
        # Level 3: LLMを呼び出さず、利用不可の固定応答を返す
        return LlmResponse(content=types.Content(
            role="model",
            parts=[types.Part(text="セキュリティ上の理由により、現在このサービスはご利用いただけません。")],
        ))

    if tracker.current_level == EscalationLevel.HUMAN_ESCALATION:
        # Level 4: オペレーター接続を案内する固定応答を返す
        return LlmResponse(content=types.Content(
            role="model",
            parts=[types.Part(
                text="この操作は人間のオペレーターによる確認が必要です。"
                "担当者に接続しますので、しばらくお待ちください。"
            )],
        ))

    return None
