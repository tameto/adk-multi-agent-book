# samples/chapter06/cli_terraform.py
"""TerraformをADKエージェントのツールとして統合する例"""

import json
import os
import re
import subprocess

from google.adk import Agent


TERRAFORM_DIR = os.environ.get("TERRAFORM_DIR", "/workspace/terraform")


def terraform_show() -> dict:
    """現在のTerraform状態を表示する

    Returns:
        現在のインフラ状態（JSON形式）"""
    cmd = ["terraform", "show", "-json"]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=TERRAFORM_DIR,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {"error": result.stderr}
    except subprocess.TimeoutExpired:
        return {"error": "タイムアウト"}


def terraform_plan() -> dict:
    """Terraformの実行計画を表示する

    Returns:
        作成・変更・削除されるリソースの計画"""
    cmd = ["terraform", "plan", "-json", "-no-color"]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=TERRAFORM_DIR,
        )
        return {
            "plan_output": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"error": "タイムアウト（120秒）"}


def terraform_output(output_name: str = "") -> dict:
    """Terraformのoutput値を取得する

    Args:
        output_name: 取得するoutput名（空文字列で全output）

    Returns:
        Output値"""
    cmd = ["terraform", "output", "-json"]
    if output_name:
        if not re.match(r'^[a-zA-Z0-9_-]+$', output_name):
            return {"error": "不正なoutput名です"}
        cmd.append(output_name)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15,
            cwd=TERRAFORM_DIR,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {"error": result.stderr}
    except subprocess.TimeoutExpired:
        return {"error": "タイムアウト"}


# Terraform運用エージェント
terraform_agent = Agent(
    name="terraform_agent",
    model="gemini-3.5-flash",
    instruction="""あなたはTerraformで管理されたインフラの状態確認と計画策定を行うエージェントです。

    ## 利用可能なツール
    - terraform_show: 現在のインフラ状態を確認
    - terraform_plan: 変更計画を確認（実行はしない）
    - terraform_output: Output値の取得

    ## 注意事項
    - terraform applyは実行しません（計画の確認まで）
    - インフラの変更が必要な場合は、計画内容を説明した上でユーザーに判断を委ねます
    - 機密情報（APIキー、パスワード等）がoutputに含まれる場合は、マスクして表示します""",
    tools=[terraform_show, terraform_plan, terraform_output],
)
