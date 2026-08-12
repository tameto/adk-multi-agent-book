# samples/chapter09/principles/principle_01_single_responsibility.py
"""原則1: 単一責任エージェント（Single Responsibility Agent）の実装例（9-1-1 完全版）

1つのエージェントには1つの明確な責務だけを持たせ、
責務ごとに分割したエージェントをオーケストレーションで連携させる。
SequentialAgentはTemplate Workflowとして利用できる。責務分離のレビュー対象として扱う。
"""
from google.adk import Agent
from google.adk.agents import SequentialAgent


# --- ツールのダミー実装（紙面では省略。実行確認用の最小実装） ---

def search_db(query: str) -> list[dict]:
    """データベースを検索します（ダミー実装）"""
    return [{"id": 1, "title": f"検索結果: {query}"}]


def generate_report(data: str) -> dict:
    """検索結果をもとにレポートを生成します（ダミー実装）"""
    return {"report": f"レポート: {data}"}


def send_email(to: str, subject: str, body: str) -> dict:
    """レポートをメールで送信します（ダミー実装）"""
    return {"status": "sent", "to": to, "subject": subject}


def answer_question(question: str) -> dict:
    """質問に回答します（ダミー実装）"""
    return {"answer": f"回答: {question}"}


# 悪い例: 1つのエージェントに複数責務
bad_agent = Agent(
    name="do_everything_agent",
    model="gemini-3.5-flash",
    instruction="""あなたは万能アシスタントです。
    ユーザーの質問に回答し、データベースを検索し、
    レポートを作成し、メールを送信してください。""",
    tools=[search_db, generate_report, send_email, answer_question],
)

# 良い例: 責務ごとにエージェントを分割
# 検索エージェント
search_agent = Agent(
    name="search_agent",
    model="gemini-3.5-flash",
    instruction="ユーザーの要求に基づいてデータベースを検索し、結果を返します。",
    tools=[search_db],
)

# レポート生成エージェント
report_agent = Agent(
    name="report_agent",
    model="gemini-3.5-flash",
    instruction="検索結果をもとに、指定されたフォーマットでレポートを生成します。",
    tools=[generate_report],
)

# 通知エージェント
notification_agent = Agent(
    name="notification_agent",
    model="gemini-3.5-flash",
    instruction="生成されたレポートを指定された宛先にメールで送信します。",
    tools=[send_email],
)

# オーケストレーション
pipeline = SequentialAgent(
    name="report_pipeline",
    sub_agents=[search_agent, report_agent, notification_agent],
)
