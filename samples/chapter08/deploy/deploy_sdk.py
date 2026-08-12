# samples/chapter08/deploy/deploy_sdk.py
"""Python SDKを使ったAgent Engineデプロイ

CLIの代わりにPython SDKでデプロイする場合の例。
CI/CDパイプラインに組み込む場合に有用。

依存:
    google-adk[gcp,otel-gcp]==2.2.0
    google-cloud-aiplatform[agent-engines]==1.153.1
    opentelemetry-exporter-otlp-proto-http==1.41.1
"""
import os
import sys

# samples/chapter08 を import path に追加して support_agent をロードできるようにする
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import vertexai
from vertexai import agent_engines

from support_agent.agent import root_agent

AGENT_ENGINE_REQUIREMENTS = [
    "google-adk[gcp,otel-gcp]==2.2.0",
    "google-cloud-aiplatform[agent-engines]==1.153.1",
    "opentelemetry-exporter-otlp-proto-http==1.41.1",
]


def _resource_name(agent_engine: object) -> str:
    """Agent Engineの完全リソース名をSDK世代差を吸収して取得する"""
    api_resource = getattr(agent_engine, "api_resource", None)
    name = getattr(api_resource, "name", None) or getattr(agent_engine, "name", None)
    if not name:
        raise AttributeError("Agent Engine resource name was not returned")
    return name


def _resource_attr(agent_engine: object, attr: str) -> str:
    """Agent Engineの表示属性をSDK世代差を吸収して取得する"""
    api_resource = getattr(agent_engine, "api_resource", None)
    value = getattr(api_resource, attr, None) or getattr(agent_engine, attr, None)
    return str(value) if value is not None else ""


def deploy_agent(
    project_id: str,
    location: str,
    staging_bucket: str,
    display_name: str = "customer-support-agent",
    env_vars: dict[str, str] | None = None,
) -> str:
    """エージェントをAgent Engineにデプロイする

    Args:
        project_id: Google CloudプロジェクトID
        location: デプロイ先リージョン
        staging_bucket: ステージング用のGCSバケット（例: "gs://my-bucket"）
        display_name: デプロイ名
        env_vars: Agent Runtimeへ渡す環境変数

    Returns:
        デプロイされたリソースの完全リソース名
    """
    # Vertex AI SDKクライアントの初期化（本書はgoogle-cloud-aiplatform 1.153.1で検証）
    client = vertexai.Client(project=project_id, location=location)

    print(f"Agent Engineにデプロイ中: {display_name}")
    print(f"  Project: {project_id}")
    print(f"  Region:  {location}")

    # ADKエージェントをAdkAppでラップしてデプロイ
    app = agent_engines.AdkApp(agent=root_agent)
    config: dict = {
        "display_name": display_name,
        "requirements": AGENT_ENGINE_REQUIREMENTS,
        "env_vars": {
            "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true",
            "OTEL_SEMCONV_STABILITY_OPT_IN": "gen_ai_latest_experimental",
            "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "EVENT_ONLY",
            **(env_vars or {}),
        },
        "staging_bucket": staging_bucket,
    }

    remote_agent = client.agent_engines.create(agent=app, config=config)
    resource_name = _resource_name(remote_agent)

    print(f"\nデプロイ完了: {resource_name}")
    return resource_name


def update_agent(
    project_id: str,
    location: str,
    resource_name: str,
    staging_bucket: str,
    requirements: list[str] | None = None,
) -> str:
    """デプロイ済みのエージェントを更新する

    Args:
        project_id: Google CloudプロジェクトID
        location: リージョン
        resource_name: 更新対象の完全リソース名
        staging_bucket: ステージング用のGCSバケット（例: "gs://my-bucket"）
        requirements: 更新後の依存パッケージ一覧（省略時は既定値を使用）

    Returns:
        更新されたリソースの完全リソース名
    """
    client = vertexai.Client(project=project_id, location=location)

    print(f"Agent Engineを更新中: {resource_name}")

    # 最新のエージェント実装でAdkAppを再構築して既存リソースを更新する
    app = agent_engines.AdkApp(agent=root_agent)
    config: dict = {
        "requirements": requirements or AGENT_ENGINE_REQUIREMENTS,
        "staging_bucket": staging_bucket,
    }

    remote_agent = client.agent_engines.update(
        name=resource_name,
        agent=app,
        config=config,
    )
    updated_resource_name = _resource_name(remote_agent)

    print(f"\n更新完了: {updated_resource_name}")
    return updated_resource_name


def list_deployed_agents(project_id: str, location: str) -> list[dict]:
    """デプロイ済みのエージェント一覧を取得する

    Args:
        project_id: Google CloudプロジェクトID
        location: リージョン

    Returns:
        デプロイ済みエージェントのリスト
    """
    client = vertexai.Client(project=project_id, location=location)
    engines = client.agent_engines.list()

    results = []
    for engine in engines:
        results.append({
            "name": _resource_attr(engine, "display_name"),
            "resource_name": _resource_name(engine),
            "create_time": _resource_attr(engine, "create_time"),
            "update_time": _resource_attr(engine, "update_time"),
        })
    return results


def delete_agent(project_id: str, location: str, resource_name: str) -> None:
    """デプロイ済みのエージェントを削除する

    Args:
        project_id: Google CloudプロジェクトID
        location: リージョン
        resource_name: 削除対象の完全リソース名
    """
    client = vertexai.Client(project=project_id, location=location)
    client.agent_engines.delete(name=resource_name, force=True)
    print(f"削除完了: {resource_name}")


if __name__ == "__main__":
    # 環境変数から設定を取得
    _project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    _location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

    if not _project:
        print("環境変数 GOOGLE_CLOUD_PROJECT を設定してください。")
        sys.exit(1)

    # デプロイ済みエージェントの一覧表示
    print("=== デプロイ済みエージェント ===")
    agents = list_deployed_agents(_project, _location)
    for agent in agents:
        print(f"  {agent['name']}: {agent['resource_name']}")

    if not agents:
        print("  （なし）")
