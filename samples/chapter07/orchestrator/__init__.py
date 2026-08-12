# samples/chapter07/orchestrator/__init__.py
"""第7章 ハンズオン: オーケストレーターエージェント（A2Aクライアント）"""

from . import agent as agent
from .agent import root_agent

__all__ = ["agent", "root_agent"]
