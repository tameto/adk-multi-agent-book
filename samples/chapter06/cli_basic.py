# samples/chapter06/cli_basic.py
"""CLIツールをADKエージェントのツールとして統合する基本パターン"""

import subprocess
import shlex

from google.adk import Agent


def run_gcloud_command(command: str) -> dict:
    """gcloud CLIコマンドを実行する

    Args:
        command: 実行するgcloudサブコマンド（例: "compute instances list"）

    Returns:
        コマンドの実行結果（stdout, stderr, return_code）"""
    # コマンド文字列を安全に分割
    args = ["gcloud"] + shlex.split(command) + ["--format=json"]

    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=30,  # 30秒でタイムアウト
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "コマンドがタイムアウトしました（30秒）",
            "return_code": -1,
        }


# gcloudツールを使うエージェント
gcloud_agent = Agent(
    name="gcloud_agent",
    model="gemini-3.5-flash",
    instruction="""あなたはGoogle Cloudリソースの管理を支援するエージェントです。

    gcloudコマンドを使ってリソースの参照・管理を行います。

    ## 使用可能なコマンド
    - compute instances list: VMインスタンスの一覧
    - compute instances describe INSTANCE_NAME: VMの詳細
    - run services list: Cloud Runサービスの一覧
    - sql instances list: Cloud SQLインスタンスの一覧
    - container clusters list: GKEクラスタの一覧

    ## 禁止事項
    - delete / destroy を含むコマンドは実行しない
    - IAMポリシーの変更は行わない
    - プロジェクトやリージョンの設定変更は行わない""",
    tools=[run_gcloud_command],
)
