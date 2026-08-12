# samples/chapter06/infra_monitor/tools.py
"""インフラ監視エージェントのkubectlラッパーツール

kubectlコマンドをADKエージェントのツールとして統合する。
本番ではsubprocess.runで実際のkubectlを実行するが、
ハンズオンではダミーデータを返す。
"""

import re
from datetime import datetime, timedelta

# パラメータのバリデーションパターン（英数字・ハイフン・アンダースコアのみ）
_SAFE_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")


def _validate_name(value: str, param_name: str) -> str | None:
    """パラメータ名のバリデーション

    Returns:
        None: バリデーション通過
        str: エラーメッセージ
    """
    if not _SAFE_NAME_PATTERN.match(value):
        return f"不正な{param_name}です。英数字・ハイフン・アンダースコアのみ使用できます。"
    return None


def kubectl_get_pods(namespace: str = "default") -> dict:
    """指定Namespaceのpod一覧を取得する（ダミー実装）

    本番環境では以下のコマンドを実行する:
    subprocess.run(["kubectl", "get", "pods", "-n", namespace, "-o", "json"],
                   timeout=15, capture_output=True, text=True)

    Args:
        namespace: KubernetesのNamespace名（デフォルト: default）

    Returns:
        Pod一覧を含む辞書
    """
    error = _validate_name(namespace, "Namespace名")
    if error:
        return {"error": error}

    # ダミーのPodデータ
    pods_db: dict[str, list[dict]] = {
        "default": [
            {
                "name": "api-gateway-abc12",
                "status": "Running",
                "restarts": 0,
                "age": "5d",
                "cpu": "120m",
                "memory": "256Mi",
            },
            {
                "name": "api-gateway-def34",
                "status": "Running",
                "restarts": 1,
                "age": "5d",
                "cpu": "115m",
                "memory": "248Mi",
            },
        ],
        "payments": [
            {
                "name": "payments-service-abc12",
                "status": "Running",
                "restarts": 3,
                "age": "3d",
                "cpu": "200m",
                "memory": "512Mi",
            },
            {
                "name": "payments-service-def34",
                "status": "Running",
                "restarts": 0,
                "age": "3d",
                "cpu": "180m",
                "memory": "480Mi",
            },
            {
                "name": "payments-service-ghi56",
                "status": "CrashLoopBackOff",
                "restarts": 15,
                "age": "3d",
                "cpu": "0m",
                "memory": "0Mi",
            },
        ],
        "monitoring": [
            {
                "name": "prometheus-server-abc12",
                "status": "Running",
                "restarts": 0,
                "age": "30d",
                "cpu": "500m",
                "memory": "2Gi",
            },
            {
                "name": "grafana-def34",
                "status": "Running",
                "restarts": 0,
                "age": "30d",
                "cpu": "100m",
                "memory": "256Mi",
            },
        ],
    }

    pods = pods_db.get(namespace, [])

    if not pods:
        return {
            "namespace": namespace,
            "pod_count": 0,
            "pods": [],
            "message": f"Namespace '{namespace}' にPodが見つかりません。",
        }

    return {
        "namespace": namespace,
        "pod_count": len(pods),
        "pods": pods,
    }


def kubectl_get_nodes() -> dict:
    """クラスタのNode状態を取得する（ダミー実装）

    本番環境では以下のコマンドを実行する:
    subprocess.run(["kubectl", "get", "nodes", "-o", "json"],
                   timeout=15, capture_output=True, text=True)

    Returns:
        Node一覧を含む辞書
    """
    nodes = [
        {
            "name": "node-pool-1-abc12",
            "status": "Ready",
            "roles": "worker",
            "version": "v1.29.4",
            "cpu_capacity": "8",
            "cpu_allocatable": "7.5",
            "memory_capacity": "32Gi",
            "memory_allocatable": "30Gi",
            "pods_running": 12,
        },
        {
            "name": "node-pool-1-def34",
            "status": "Ready",
            "roles": "worker",
            "version": "v1.29.4",
            "cpu_capacity": "8",
            "cpu_allocatable": "7.5",
            "memory_capacity": "32Gi",
            "memory_allocatable": "30Gi",
            "pods_running": 10,
        },
        {
            "name": "node-pool-1-ghi56",
            "status": "NotReady",
            "roles": "worker",
            "version": "v1.29.4",
            "cpu_capacity": "8",
            "cpu_allocatable": "0",
            "memory_capacity": "32Gi",
            "memory_allocatable": "0Gi",
            "pods_running": 0,
        },
    ]

    return {
        "node_count": len(nodes),
        "ready_count": sum(1 for n in nodes if n["status"] == "Ready"),
        "not_ready_count": sum(1 for n in nodes if n["status"] != "Ready"),
        "nodes": nodes,
    }


def kubectl_get_events(namespace: str = "default") -> dict:
    """指定Namespaceのイベントを取得する（ダミー実装）

    本番環境では以下のコマンドを実行する:
    subprocess.run(["kubectl", "get", "events", "-n", namespace,
                    "--sort-by='.lastTimestamp'", "-o", "json"],
                   timeout=15, capture_output=True, text=True)

    Args:
        namespace: KubernetesのNamespace名（デフォルト: default）

    Returns:
        イベント一覧を含む辞書
    """
    error = _validate_name(namespace, "Namespace名")
    if error:
        return {"error": error}

    now = datetime.now()

    events_db: dict[str, list[dict]] = {
        "default": [
            {
                "type": "Normal",
                "reason": "Scheduled",
                "object": "pod/api-gateway-abc12",
                "message": "Successfully assigned default/api-gateway-abc12 to node-pool-1-abc12",
                "timestamp": (now - timedelta(days=5)).isoformat(),
            },
        ],
        "payments": [
            {
                "type": "Warning",
                "reason": "BackOff",
                "object": "pod/payments-service-ghi56",
                "message": "Back-off restarting failed container",
                "timestamp": (now - timedelta(minutes=5)).isoformat(),
            },
            {
                "type": "Warning",
                "reason": "Unhealthy",
                "object": "pod/payments-service-ghi56",
                "message": "Liveness probe failed: connection refused",
                "timestamp": (now - timedelta(minutes=10)).isoformat(),
            },
            {
                "type": "Normal",
                "reason": "Pulled",
                "object": "pod/payments-service-abc12",
                "message": "Container image pulled successfully",
                "timestamp": (now - timedelta(days=3)).isoformat(),
            },
        ],
        "monitoring": [
            {
                "type": "Normal",
                "reason": "Scheduled",
                "object": "pod/prometheus-server-abc12",
                "message": "Successfully assigned monitoring/prometheus-server-abc12",
                "timestamp": (now - timedelta(days=30)).isoformat(),
            },
        ],
    }

    events = events_db.get(namespace, [])

    # Warning イベントの集計
    warnings = [e for e in events if e["type"] == "Warning"]

    return {
        "namespace": namespace,
        "event_count": len(events),
        "warning_count": len(warnings),
        "events": events,
    }
