# samples/chapter03/skill_patterns/versioning.py
"""3-5-4 パターン3: スキルのバージョニング（完全版）

スキルのバージョンを管理し、A/Bテストや段階的ロールアウトに対応するパターン。
バージョン情報は SKILL.md の metadata.version に記録しつつ、
ディレクトリ名を分けて物理的に切り替える。
"""
from pathlib import Path

from google.adk.skills import load_skill_from_dir

SKILLS_DIR = Path("./skills")


def load_versioned_skill(skill_name: str, version: str = "v1"):
    """バージョン付きディレクトリからスキルを読み込む（kebab-caseで統一）"""
    return load_skill_from_dir(SKILLS_DIR / f"{skill_name}-{version}")


def select_skill_version(user_id: str) -> str:
    """ユーザーIDのハッシュで v1 / v2 を振り分ける"""
    if hash(user_id) % 2 == 0:
        return "v1"
    return "v2"
