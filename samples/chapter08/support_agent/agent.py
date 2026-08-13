# samples/chapter08/support_agent/agent.py
"""Agent Engineデプロイ用カスタマーサポートエージェント

ルーティングと専門エージェントを分け、各Agentでgemini-3.5-flashを
明示するマルチエージェント構成の例。
"""
import json
import logging
import sys

from google.adk import Agent

from .tools import escalate_to_human, get_order_status, search_faq

# --- 構造化ログの設定 ---


class StructuredFormatter(logging.Formatter):
    """Cloud Logging向けの構造化フォーマッタ"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "component": record.name,
        }
        # カスタム属性の追加
        for attr in (
            "agent_name",
            "session_id",
            "user_id",
            "event",
            "reason",
            "tool_name",
        ):
            if hasattr(record, attr):
                log_entry[attr] = getattr(record, attr)
        return json.dumps(log_entry, ensure_ascii=False)


def _get_logger(name: str) -> logging.Logger:
    """構造化ロガーを取得する"""
    _logger = logging.getLogger(name)
    if not _logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        _logger.addHandler(handler)
        _logger.setLevel(logging.INFO)
    return _logger


logger = _get_logger("support_agent")

# --- サブエージェント定義 ---

# FAQエージェント: 定型の質問に回答（短いInstruction + FAQ検索）
faq_agent = Agent(
    name="faq_agent",
    model="gemini-3.5-flash",
    instruction="""あなたはFAQ担当のサポートエージェントです。

## 役割
- よくある質問（返品、送料、支払い方法、配送日数など）に回答する
- search_faqツールでFAQデータベースを検索し、回答を返す
- FAQに該当しない質問には「この質問はFAQに該当しません」と回答する

## 注意事項
- 事実のみを回答し、推測は行わない
- 回答は簡潔にまとめる""",
    tools=[search_faq],
    output_key="faq_response",
)

# 調査エージェント: 複雑な問い合わせに対応（同じモデルで専門ツールを分離）
investigation_agent = Agent(
    name="investigation_agent",
    model="gemini-3.5-flash",
    instruction="""あなたは調査担当のサポートエージェントです。

## 役割
- 注文に関する問い合わせを調査する
- get_order_statusツールで注文情報を取得し、状況を説明する
- 対応が困難な場合はescalate_to_humanで人間のオペレーターに転送する

## 注意事項
- 注文IDが不明な場合は、ユーザーに確認を依頼する
- 個人情報（氏名、住所、電話番号）を回答に含めない
- 解決困難な場合は無理に回答せず、エスカレーションする""",
    tools=[get_order_status, escalate_to_human],
    output_key="investigation_response",
)

# --- ルートエージェント ---

root_agent = Agent(
    name="support_router",
    model="gemini-3.5-flash",
    instruction="""あなたはカスタマーサポートのルーティングエージェントです。

## 役割
ユーザーの問い合わせ内容を分析し、適切なサブエージェントに振り分けます。

## 振り分けルール
1. **faq_agent**: 返品、送料、支払い方法、配送日数などのよくある質問
2. **investigation_agent**: 注文ステータスの確認、注文に関するトラブル、
   複雑な問い合わせ

## 注意事項
- 挨拶や雑談には自分で応答し、サブエージェントには振り分けない
- 判断に迷う場合はinvestigation_agentに振り分ける""",
    sub_agents=[faq_agent, investigation_agent],
)
