# samples/chapter06/cli_secure.py
"""セキュリティを強化したCLIツール統合"""

import re
import shlex
import subprocess

from google.adk import Agent


# 許可するサブコマンドのホワイトリスト
ALLOWED_GCLOUD_SUBCOMMANDS = {
    "compute instances list",
    "compute instances describe",
    "run services list",
    "run services describe",
    "sql instances list",
    "container clusters list",
    "container clusters describe",
}


def safe_gcloud(subcommand: str, resource_name: str = "", flags: str = "") -> dict:
    """安全にgcloudコマンドを実行する

    Args:
        subcommand: 実行するサブコマンド（ホワイトリスト内のもの）
        resource_name: 対象リソース名（英数字・ハイフン・アンダースコアのみ）
        flags: 追加フラグ（--region, --zone等）

    Returns:
        コマンドの実行結果"""
    # サブコマンドのホワイトリスト検証
    if subcommand not in ALLOWED_GCLOUD_SUBCOMMANDS:
        return {
            "error": f"許可されていないサブコマンドです: {subcommand}",
            "allowed": list(ALLOWED_GCLOUD_SUBCOMMANDS),
        }

    # リソース名のバリデーション（英数字、ハイフン、アンダースコアのみ）
    if resource_name and not re.match(r'^[a-zA-Z0-9_-]+$', resource_name):
        return {"error": "リソース名に不正な文字が含まれています"}

    # フラグのバリデーション（--key=value形式のみ許可）
    safe_flags = []
    if flags:
        for flag in shlex.split(flags):
            if re.match(r'^--[a-z][a-z0-9-]*(=[\w./-]+)?$', flag):
                safe_flags.append(flag)
            else:
                return {"error": f"不正なフラグ形式です: {flag}"}

    # コマンドの組み立て（文字列結合ではなくリストで構築。shell=Trueは使わない）
    cmd = ["gcloud"] + subcommand.split()
    if resource_name:
        cmd.append(resource_name)
    cmd.extend(safe_flags)
    cmd.append("--format=json")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"error": "コマンドがタイムアウトしました"}


# セキュリティ強化されたエージェント
secure_gcloud_agent = Agent(
    name="secure_gcloud_agent",
    model="gemini-3.5-flash",
    instruction="""Google Cloudリソースの参照を行うエージェントです。
    safe_gcloudツールでリソース情報を取得します。
    利用できるサブコマンドはホワイトリストで制限されています。""",
    tools=[safe_gcloud],
)
