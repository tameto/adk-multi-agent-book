"""評価用ターゲット: ツール数過多のエージェント

9-4 ハンズオン `adk eval` 用の異常系サンプル。
A-2（ツール数制限）違反を意図的に含んでいる。
"""
from google.adk import Agent


# AST 解析用のダミー関数群（実行しない）
def search_db(q: str) -> str:
    return ""


def fetch_user(uid: str) -> dict:
    return {}


def update_user(uid: str, data: dict) -> None:
    return None


def create_order(uid: str, items: list[str]) -> dict:
    return {}


def cancel_order(order_id: str) -> None:
    return None


def send_email(to: str, body: str) -> None:
    return None


def send_sms(to: str, body: str) -> None:
    return None


def generate_report(topic: str) -> str:
    return ""


def translate(text: str, lang: str) -> str:
    return ""


def summarize(text: str) -> str:
    return ""


def analyze_sentiment(text: str) -> float:
    return 0.0


def schedule_task(cron: str, name: str) -> None:
    return None


# アンチパターン: 12個のツールを1エージェントに詰め込む（A-2違反）
root_agent = Agent(
    name="swiss_army_agent",
    model="gemini-3.5-flash",
    instruction="ユーザーのあらゆるリクエストに応えます。",
    tools=[
        search_db, fetch_user, update_user,
        create_order, cancel_order,
        send_email, send_sms,
        generate_report, translate, summarize,
        analyze_sentiment, schedule_task,
    ],
)
