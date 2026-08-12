# samples/chapter06/infra_monitor/__init__.py
"""第6章 ハンズオン: インフラ監視エージェント（MCP + CLIラッパー）"""

from . import agent as agent
from .agent import root_agent

__all__ = ["agent", "root_agent"]
