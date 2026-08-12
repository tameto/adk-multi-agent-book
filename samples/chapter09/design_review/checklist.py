# samples/chapter09/design_review/checklist.py
"""設計レビューチェックリスト定義

第9章の設計原則10選に基づくチェックリスト。
設計レビューエージェントのレビュー観点として使用する。
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class CheckItem:
    """チェック項目"""
    id: str
    category: str
    name: str
    description: str
    severity: str  # high / medium / low


# --- 設計原則チェックリスト ---
DESIGN_CHECKLIST: list[CheckItem] = [
    # アーキテクチャ
    CheckItem(
        id="A-1",
        category="architecture",
        name="単一責任",
        description="各エージェントが1つの明確な責務のみを持っている",
        severity="high",
    ),
    CheckItem(
        id="A-2",
        category="architecture",
        name="ツール数制限",
        description="1エージェントあたりのツール数が5個以下である",
        severity="medium",
    ),
    CheckItem(
        id="A-3",
        category="architecture",
        name="冪等性",
        description="ツール呼び出しが冪等に設計されている",
        severity="high",
    ),
    CheckItem(
        id="A-6",
        category="architecture",
        name="Instruction適正長",
        description="Instructionが500文字以下に収められている",
        severity="medium",
    ),

    # セキュリティ（本文 表9-5 のID体系に合わせる）
    CheckItem(
        id="S-1",
        category="security",
        name="最小権限",
        description="エージェントに必要最小限のツールのみ付与されている",
        severity="high",
    ),
    CheckItem(
        id="S-2",
        category="security",
        name="入力検証",
        description="before_model_callbackで入力のサニタイズ・検証が実装されている",
        severity="medium",
    ),
    CheckItem(
        id="S-4",
        category="security",
        name="認証情報管理",
        description="APIキーや認証情報がコードに直書きされていない",
        severity="high",
    ),
    CheckItem(
        id="S-6",
        category="security",
        name="権限制御",
        description="before_tool_callbackで書き込み操作の権限チェックが実装されている",
        severity="medium",
    ),

    # 運用
    CheckItem(
        id="O-1",
        category="operations",
        name="可観測性",
        description="ログ・トレース・メトリクスが実装されている",
        severity="medium",
    ),
    CheckItem(
        id="O-4",
        category="operations",
        name="ループ防止",
        description="LoopAgent使用時にmax_iterationsが設定されている",
        severity="high",
    ),

    # コスト
    CheckItem(
        id="C-1",
        category="cost",
        name="モデル選択",
        description="検証対象モデルが明示され、古いモデル名が残っていない",
        severity="medium",
    ),
    CheckItem(
        id="C-3",
        category="cost",
        name="Compaction",
        description="長い会話を想定する場合にCompactionが設定されている",
        severity="low",
    ),

    # 品質
    CheckItem(
        id="Q-1",
        category="quality",
        name="評価セット",
        description="adk evalの評価セットが用意されている（別途手動確認）",
        severity="medium",
    ),
    CheckItem(
        id="Q-2",
        category="quality",
        name="ハルシネーション対策",
        description="Instructionでツール使用と出典提示を明示している",
        severity="medium",
    ),
]


def get_checklist_by_category(category: str) -> list[CheckItem]:
    """カテゴリ別のチェックリストを取得する"""
    return [item for item in DESIGN_CHECKLIST if item.category == category]


def get_all_categories() -> list[str]:
    """全カテゴリ名を取得する"""
    return sorted(set(item.category for item in DESIGN_CHECKLIST))
