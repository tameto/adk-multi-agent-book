# 5-4-3. after_model_callbackによる出力検証
"""出力ガードレールの実装"""
import re
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse
from google.genai import types


def output_quality_guardrail(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> Optional[LlmResponse]:
    """出力の品質と安全性をチェックするガードレール

    Returns:
        None: チェック通過（出力をそのまま使用)
        LlmResponse: 修正された応答
    """
    response_text = _extract_response_text(llm_response)
    if not response_text:
        return None

    # PII（個人情報）の検出とマスキング
    masked_text, pii_found = _mask_pii(response_text)
    if pii_found:
        return _create_response(masked_text)

    # 禁止表現の検出
    if _contains_prohibited_content(response_text):
        return _create_response(
            "申し訳ございませんが、ご要望に沿った応答を生成できませんでした。"
            "別の形でお手伝いできることはありますか？"
        )

    # ハルシネーション疑いの検出
    if _detect_hallucination_signals(response_text):
        # ハルシネーション疑いをメタデータに記録
        callback_context.state["_hallucination_warning"] = True

    # チェック通過
    return None


def _extract_response_text(
    response: LlmResponse,
) -> Optional[str]:
    """レスポンスからテキストを抽出する"""
    if not response.content or not response.content.parts:
        return None
    for part in response.content.parts:
        if part.text:
            return part.text
    return None


def _mask_pii(text: str) -> tuple[str, bool]:
    """PIIを検出してマスキングする"""
    pii_found = False

    # メールアドレスのマスキング
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    if re.search(email_pattern, text):
        text = re.sub(email_pattern, "[メールアドレス]", text)
        pii_found = True

    # 電話番号のマスキング（日本の電話番号パターン）
    phone_pattern = r'0\d{1,4}-?\d{1,4}-?\d{4}'
    if re.search(phone_pattern, text):
        text = re.sub(phone_pattern, "[電話番号]", text)
        pii_found = True

    # マイナンバー形式のマスキング
    mynumber_pattern = r'\d{4}\s?\d{4}\s?\d{4}'
    if re.search(mynumber_pattern, text):
        text = re.sub(mynumber_pattern, "[ID番号]", text)
        pii_found = True

    return text, pii_found


def _contains_prohibited_content(text: str) -> bool:
    """禁止コンテンツを検出する"""
    # 差別的表現、暴力的表現等のチェック
    prohibited_patterns = [
        r'殺[すし]',
        r'死[ねぬ]',
    ]
    return any(re.search(p, text) for p in prohibited_patterns)


def _detect_hallucination_signals(text: str) -> bool:
    """ハルシネーションの兆候を検出する"""
    hallucination_signals = [
        "確認はできていませんが",
        "おそらく",
        "記憶によれば",
        "一般的には",
    ]
    signal_count = sum(1 for s in hallucination_signals if s in text)
    # 複数のシグナルが検出された場合に疑いありとする
    return signal_count >= 2


def _create_response(text: str) -> LlmResponse:
    """テキストからLlmResponseを生成する"""
    return LlmResponse(
        content=types.Content(
            parts=[types.Part(text=text)],
            role="model",
        )
    )
