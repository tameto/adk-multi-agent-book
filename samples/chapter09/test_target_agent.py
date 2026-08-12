"""設計レビュー対象のサンプルエージェント: 問題を含む実装例

このファイルは 9-4 ハンズオン「設計レビュー自動化エージェント」の
動作確認用ターゲットです。原則違反を意図的に埋め込んでいます。

- APIキーの直書き（最小権限違反、Secret Manager未使用）
- 過剰な責務（God Agent アンチパターン）
- 長大なInstruction（Prompt Spaghetti アンチパターン）
- 危険ツール（delete_records / drop_table）の付与
- before_tool_callback / after_model_callback なし（可観測性欠如）

実際にはこれらのツール関数は未定義のため、
設計レビューエージェントは AST 解析のみ行い実行はしません。
"""
from google.adk import Agent

API_KEY = "EXAMPLE_API_KEY_DO_NOT_USE"  # 問題: APIキーの直書き（ダミー値）


# 以下のツールは AST 解析用のダミー（実行しない）
def search_db(query: str) -> str:
    return ""


def generate_report(topic: str) -> str:
    return ""


def send_email(to: str, subject: str, body: str) -> str:
    return ""


def manage_files(path: str, action: str) -> str:
    return ""


def schedule_meeting(title: str, attendees: list[str]) -> str:
    return ""


def translate_text(text: str, lang: str) -> str:
    return ""


def analyze_data(dataset: str) -> dict:
    return {}


def generate_image(prompt: str) -> str:
    return ""


def convert_audio(src: str, dst: str) -> str:
    return ""


def delete_records(table: str, condition: str) -> str:
    return ""


def drop_table(table: str) -> str:
    return ""


root_agent = Agent(
    name="bad_example",
    model="gemini-3.5-flash",
    instruction="""あなたは万能アシスタントです。
    ユーザーの質問に回答し、データベースを検索し、
    レポートを作成し、メールを送信し、
    ファイルを管理し、スケジュールを調整し、
    翻訳を行い、データを分析し、
    画像を生成し、音声を変換してください。
    ...(非常に長いInstruction)""",
    tools=[
        search_db, generate_report, send_email,
        manage_files, schedule_meeting, translate_text,
        analyze_data, generate_image, convert_audio,
        delete_records, drop_table,  # 問題: 危険なツールの付与
    ],
    # 問題: before_tool_callback なし
    # 問題: after_model_callback なし（可観測性なし）
)
