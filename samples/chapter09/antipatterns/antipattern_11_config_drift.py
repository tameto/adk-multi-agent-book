# samples/chapter09/antipatterns/antipattern_11_config_drift.py
"""アンチパターン11: Config Drift（設定のドリフト）の実装例（9-2-11 完全版）

設定をコードに直書きするアンチパターン（bad_agent）と、
環境変数から読み込む設定クラスへ外部化する改善版（AgentConfig）を対比する。
紙面で省略した cost_limit_usd / log_level / session_db_url の環境変数化を含む完全版。
"""
import os
from dataclasses import dataclass

# Agent の import は紙面では省略
from google.adk import Agent

# アンチパターン: 設定をコードに直書き
bad_agent = Agent(
    name="agent",
    model="gemini-3.5-flash",  # 環境によって変えたいが直書き
    instruction="...",
)

# 改善: 設定を外部化
@dataclass
class AgentConfig:
    """エージェントの設定を環境変数から読み込みます"""
    model: str = os.environ.get("AGENT_MODEL", "gemini-3.5-flash")
    max_turns: int = int(os.environ.get("AGENT_MAX_TURNS", "10"))
    cost_limit_usd: float = float(os.environ.get("AGENT_COST_LIMIT", "1.0"))
    log_level: str = os.environ.get("AGENT_LOG_LEVEL", "INFO")
    session_db_url: str = os.environ.get("SESSION_DB_URL", "sqlite:///dev.db")

config = AgentConfig()

# 設定オブジェクトを使ってエージェントを構築
agent = Agent(
    name="configurable_agent",
    model=config.model,
    instruction="...",
)
