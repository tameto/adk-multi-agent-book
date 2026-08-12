# samples/chapter10/prompt_injection_guard.py
"""プロンプトインジェクション対策（直接攻撃）の実装例（10-2-1 完全版）

before_model_callback で正規表現ベースの入力フィルタリングを行うガードレール。
紙面で省略したパターンリストの全項目と、ユーザーメッセージのテキスト抽出処理を含む完全版。
他のガードレールと統合した実装は secure_agent/callbacks.py を参照。
"""
from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types
import re


# 危険なパターンのリスト
INJECTION_PATTERNS: list[re.Pattern] = [
    re.compile(r"(指示|命令|ルール).*(無視|忘れ|リセット)", re.IGNORECASE),
    re.compile(r"システムプロンプト.*(表示|出力|教え)", re.IGNORECASE),
    re.compile(
        # 修飾語の繰り返しを許容する（indirect_injection_guard.py と
        # 同一パターン。disregard系の言い換えも検出する）
        r"(ignore|disregard)\s+((all|previous|above|prior)\s+)+"
        r"(instructions|rules|context)",
        re.IGNORECASE,
    ),
    re.compile(r"you\s+are\s+now\s+a", re.IGNORECASE),
    re.compile(r"(jailbreak|DAN|bypass)", re.IGNORECASE),
]


def detect_prompt_injection(user_input: str) -> bool:
    """ユーザー入力にプロンプトインジェクションのパターンが含まれるか判定する"""
    for pattern in INJECTION_PATTERNS:
        if pattern.search(user_input):
            return True
    return False


def before_model_guard(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> LlmResponse | None:
    """モデル呼び出し前にプロンプトインジェクションを検出するガードレール"""
    # 最新のユーザーメッセージを取得
    if not llm_request.contents:
        return None

    last_content = llm_request.contents[-1]
    if last_content.role != "user":
        return None

    # テキスト部分を結合して検査
    user_text = ""
    for part in last_content.parts:
        if hasattr(part, "text") and part.text:
            user_text += part.text

    if detect_prompt_injection(user_text):
        # インジェクション検出時はモデルを呼び出さず、固定レスポンスを返す
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text="申し訳ありませんが、そのリクエストには対応できません。")],
            )
        )

    return None  # 問題なければモデル呼び出しを続行


# ガードレールを組み込んだエージェント
secure_agent = Agent(
    name="secure_agent",
    model="gemini-3.5-flash",
    instruction="あなたはカスタマーサポートエージェントです。製品に関する質問に回答してください。",
    before_model_callback=before_model_guard,
)
