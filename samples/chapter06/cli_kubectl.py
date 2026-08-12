# samples/chapter06/cli_kubectl.py
"""kubectlをADKエージェントのツールとして統合する例"""

import json
import re
import subprocess

from google.adk import Agent


# kubectlの許可コマンド（secretsは漏洩リスクが大きいため意図的に除外）
ALLOWED_KUBECTL_COMMANDS = {
    "get": ["pods", "services", "deployments", "nodes", "namespaces",
            "configmaps", "ingress", "events"],
    "describe": ["pod", "service", "deployment", "node"],
    "logs": [],  # Pod名を直接指定
    "top": ["pods", "nodes"],
}


def kubectl_get(
    resource_type: str,
    namespace: str = "default",
    label_selector: str = "",
) -> dict:
    """Kubernetesリソースの一覧を取得する

    Args:
        resource_type: リソースタイプ（pods, services, deployments等）
        namespace: 対象のNamespace
        label_selector: ラベルセレクター（例: "app=nginx"）

    Returns:
        リソース一覧（JSON形式）"""
    if resource_type not in ALLOWED_KUBECTL_COMMANDS.get("get", []):
        return {"error": f"取得できないリソースタイプです: {resource_type}"}

    if not re.match(r'^[a-zA-Z0-9_-]+$', namespace):
        return {"error": "不正なNamespace名です"}

    cmd = ["kubectl", "get", resource_type, "-n", namespace, "-o", "json"]

    if label_selector:
        if re.match(r'^[a-zA-Z0-9_./-]+=[\w./-]+$', label_selector):
            cmd.extend(["-l", label_selector])
        else:
            return {"error": "不正なラベルセレクター形式です"}

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {"error": result.stderr}
    except subprocess.TimeoutExpired:
        return {"error": "タイムアウト"}


def kubectl_describe(resource_type: str, name: str, namespace: str = "default") -> dict:
    """Kubernetesリソースの詳細情報を取得する

    Args:
        resource_type: リソースタイプ（pod, service, deployment等）
        name: リソース名
        namespace: 対象のNamespace

    Returns:
        リソースの詳細情報"""
    if resource_type not in ALLOWED_KUBECTL_COMMANDS.get("describe", []):
        return {"error": f"詳細を表示できないリソースタイプです: {resource_type}"}

    if not re.match(r'^[a-zA-Z0-9_.-]+$', name):
        return {"error": "不正なリソース名です"}

    if not re.match(r'^[a-zA-Z0-9_-]+$', namespace):
        return {"error": "不正なNamespace名です"}

    cmd = ["kubectl", "describe", resource_type, name, "-n", namespace]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            return {"output": result.stdout}
        return {"error": result.stderr}
    except subprocess.TimeoutExpired:
        return {"error": "タイムアウト"}


def kubectl_logs(
    pod_name: str,
    namespace: str = "default",
    container: str = "",
    tail_lines: int = 100,
) -> dict:
    """Podのログを取得する

    Args:
        pod_name: Pod名
        namespace: 対象のNamespace
        container: コンテナ名（マルチコンテナPodの場合）
        tail_lines: 取得する最終行数（デフォルト100）

    Returns:
        Podのログ"""
    if not re.match(r'^[a-zA-Z0-9_.-]+$', pod_name):
        return {"error": "不正なPod名です"}

    if not re.match(r'^[a-zA-Z0-9_-]+$', namespace):
        return {"error": "不正なNamespace名です"}

    # tail_linesの範囲制限
    tail_lines = max(1, min(tail_lines, 1000))

    cmd = ["kubectl", "logs", pod_name, "-n", namespace,
           f"--tail={tail_lines}"]

    if container:
        if re.match(r'^[a-zA-Z0-9_.-]+$', container):
            cmd.extend(["-c", container])
        else:
            return {"error": "不正なコンテナ名です"}

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            return {"logs": result.stdout}
        return {"error": result.stderr}
    except subprocess.TimeoutExpired:
        return {"error": "タイムアウト"}


# Kubernetes運用エージェント
k8s_agent = Agent(
    name="k8s_operator",
    model="gemini-3.5-flash",
    instruction="""あなたはKubernetesクラスタの監視・トラブルシューティングを行うエージェントです。

    ## 利用可能なツール
    - kubectl_get: リソースの一覧取得
    - kubectl_describe: リソースの詳細表示
    - kubectl_logs: Podのログ取得

    ## トラブルシューティングの手順
    1. まずPodの状態を確認（kubectl_get pods）
    2. 異常なPodがあれば詳細を確認（kubectl_describe）
    3. 必要に応じてログを確認（kubectl_logs）
    4. Eventも確認し、問題の原因を特定する

    ## 制約
    - リソースの作成・変更・削除は行いません（読み取りのみ）
    - 全NamespaceのPodを参照する場合は namespace="default" 以外も指定してください""",
    tools=[kubectl_get, kubectl_describe, kubectl_logs],
)
