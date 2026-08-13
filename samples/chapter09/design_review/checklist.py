# samples/chapter09/design_review/checklist.py
"""設計レビューチェックリスト定義

第9章の設計原則10選に基づくチェックリスト。
本文の表9-4〜表9-8で定義した5観点29項目に対応する。
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
    # アーキテクチャ（本文 表9-4 のID体系に合わせる）
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
        name="オーケストレーション",
        description="Sequential／Parallel／Loopを用途に応じて使い分けている",
        severity="high",
    ),
    CheckItem(
        id="A-4",
        category="architecture",
        name="疎結合",
        description="エージェント間の依存がA2A／State経由に限定されている",
        severity="medium",
    ),
    CheckItem(
        id="A-5",
        category="architecture",
        name="スケーラビリティ",
        description="各エージェントを独立してスケールできる",
        severity="medium",
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
        id="S-3",
        category="security",
        name="Prompt Injection",
        description="Prompt Injection対策（ガードレール等）が実装されている",
        severity="high",
    ),
    CheckItem(
        id="S-4",
        category="security",
        name="認証情報管理",
        description="APIキーや認証情報がコードに直書きされていない",
        severity="high",
    ),
    CheckItem(
        id="S-5",
        category="security",
        name="データ保護",
        description="機密情報がログに出力されていない",
        severity="high",
    ),
    CheckItem(
        id="S-6",
        category="security",
        name="権限制御",
        description="before_tool_callbackで書き込み操作の権限チェックが実装されている",
        severity="medium",
    ),
    CheckItem(
        id="S-7",
        category="security",
        name="Kill Switch",
        description="緊急停止の仕組みが実装されている",
        severity="medium",
    ),
    CheckItem(
        id="S-8",
        category="security",
        name="出力フィルタリング",
        description="LLMの出力に機密情報が含まれていないことを確認している",
        severity="medium",
    ),

    # 運用（本文 表9-6 のID体系に合わせる）
    CheckItem(
        id="O-1",
        category="operations",
        name="可観測性",
        description="ログ・トレース・メトリクスが実装されている",
        severity="medium",
    ),
    CheckItem(
        id="O-2",
        category="operations",
        name="エラーハンドリング",
        description="すべてのツールにエラーハンドリングが実装されている",
        severity="high",
    ),
    CheckItem(
        id="O-3",
        category="operations",
        name="フォールバック",
        description="外部サービス障害時のフォールバックが設計されている",
        severity="medium",
    ),
    CheckItem(
        id="O-4",
        category="operations",
        name="ループ防止",
        description="LoopAgent使用時にmax_iterationsが設定されている",
        severity="high",
    ),
    CheckItem(
        id="O-5",
        category="operations",
        name="セッション管理",
        description="本番環境で永続化SessionServiceが使用されている",
        severity="high",
    ),

    # コスト（本文 表9-7 のID体系に合わせる）
    CheckItem(
        id="C-1",
        category="cost",
        name="モデル選択",
        description="検証対象モデルが明示され、古いモデル名が残っていない",
        severity="medium",
    ),
    CheckItem(
        id="C-2",
        category="cost",
        name="キャッシュ",
        description="繰り返しリクエストのキャッシュが実装されている",
        severity="low",
    ),
    CheckItem(
        id="C-3",
        category="cost",
        name="Compaction",
        description="長い会話を想定する場合にCompactionが設定されている",
        severity="low",
    ),
    CheckItem(
        id="C-4",
        category="cost",
        name="コスト上限",
        description="セッションあたりのコスト上限が設定されている",
        severity="medium",
    ),
    CheckItem(
        id="C-5",
        category="cost",
        name="コスト監視",
        description="コストのリアルタイム監視が設定されている",
        severity="low",
    ),

    # 品質（本文 表9-8 のID体系に合わせる）
    CheckItem(
        id="Q-1",
        category="quality",
        name="評価セット",
        description="adk evalの評価ケースが最低30件用意されている（別途手動確認）",
        severity="medium",
    ),
    CheckItem(
        id="Q-2",
        category="quality",
        name="正常系テスト",
        description="主要ユースケースのテストが評価セットに含まれている",
        severity="medium",
    ),
    CheckItem(
        id="Q-3",
        category="quality",
        name="異常系テスト",
        description="エラーケースのテストが評価セットに含まれている",
        severity="medium",
    ),
    CheckItem(
        id="Q-4",
        category="quality",
        name="セキュリティテスト",
        description="Prompt Injection等のテストが評価セットに含まれている",
        severity="high",
    ),
    CheckItem(
        id="Q-5",
        category="quality",
        name="回帰テスト",
        description="過去のバグに対する回帰テストが評価セットに含まれている",
        severity="low",
    ),
]


def get_checklist_by_category(category: str) -> list[CheckItem]:
    """カテゴリ別のチェックリストを取得する"""
    return [item for item in DESIGN_CHECKLIST if item.category == category]


def get_all_categories() -> list[str]:
    """全カテゴリ名を取得する"""
    return sorted(set(item.category for item in DESIGN_CHECKLIST))
