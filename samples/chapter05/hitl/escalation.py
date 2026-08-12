# 5-5-5. エスカレーション設計
"""エスカレーション設計の実装"""
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse
from google.genai import types


class EscalationManager:
    """エスカレーション管理"""

    # エスカレーションルール
    ESCALATION_RULES = {
        "confidence_low": {
            "description": "エージェントの確信度が低い",
            "threshold": 0.3,
            "escalation_level": "l1_support",
        },
        "consecutive_errors": {
            "description": "連続してエラーが発生",
            "threshold": 3,
            "escalation_level": "l2_support",
        },
        "user_frustration": {
            "description": "ユーザーの不満が検出された",
            "keywords": ["全然だめ", "使えない", "いい加減にして"],
            "escalation_level": "l1_support",
        },
        "sensitive_topic": {
            "description": "センシティブなトピックが検出された",
            "keywords": ["訴訟", "返金", "クレーム"],
            "escalation_level": "l2_support",
        },
    }

    def after_model_callback(
        self,
        callback_context: CallbackContext,
        llm_response: LlmResponse,
    ) -> Optional[LlmResponse]:
        """モデル応答後のエスカレーション判定"""
        response_text = self._extract_text(llm_response)
        if not response_text:
            return None

        # ユーザーの不満検出
        last_user_message = callback_context.state.get("_last_user_message", "")
        if self._detect_user_frustration(last_user_message):
            return self._escalate(
                callback_context,
                "user_frustration",
                "ご不便をおかけしております。担当者におつなぎします。",
            )

        # 連続エラー検出
        error_count = callback_context.state.get("_consecutive_errors", 0)
        if "申し訳" in response_text or "できません" in response_text:
            error_count += 1
            callback_context.state["_consecutive_errors"] = error_count
        else:
            callback_context.state["_consecutive_errors"] = 0

        if error_count >= self.ESCALATION_RULES["consecutive_errors"]["threshold"]:
            return self._escalate(
                callback_context,
                "consecutive_errors",
                "問題の解決に時間がかかっております。"
                "専門の担当者におつなぎします。",
            )

        # センシティブトピック検出
        if self._detect_sensitive_topic(last_user_message):
            return self._escalate(
                callback_context,
                "sensitive_topic",
                "このお問い合わせは専門の担当者が対応いたします。"
                "少々お待ちください。",
            )

        return None

    def _detect_user_frustration(self, text: str) -> bool:
        """ユーザーの不満を検出する"""
        keywords = self.ESCALATION_RULES["user_frustration"]["keywords"]
        return any(kw in text for kw in keywords)

    def _detect_sensitive_topic(self, text: str) -> bool:
        """センシティブなトピックを検出する"""
        keywords = self.ESCALATION_RULES["sensitive_topic"]["keywords"]
        return any(kw in text for kw in keywords)

    def _escalate(
        self,
        callback_context: CallbackContext,
        rule_name: str,
        user_message: str,
    ) -> LlmResponse:
        """エスカレーションを実行する"""
        rule = self.ESCALATION_RULES[rule_name]

        # エスカレーション情報をStateに保存
        callback_context.state["_escalation"] = {
            "rule": rule_name,
            "level": rule["escalation_level"],
            "description": rule["description"],
        }

        return LlmResponse(
            content=types.Content(
                parts=[types.Part(text=user_message)],
                role="model",
            )
        )

    def _extract_text(self, response: LlmResponse) -> Optional[str]:
        """レスポンスからテキストを抽出"""
        if not response.content or not response.content.parts:
            return None
        for part in response.content.parts:
            if part.text:
                return part.text
        return None
