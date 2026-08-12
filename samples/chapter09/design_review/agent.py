# samples/chapter09/design_review/agent.py
"""設計レビュー自動化エージェント

SequentialAgentで3つのサブエージェント（分析→レビュー→レポート生成）を連携。
SequentialAgentはTemplate Workflowとして利用できる。複雑な分岐や再開が必要な場合はWorkflow Runtimeを検討する。
ADKエージェントのソースコードを分析し、設計原則への準拠度をチェックする。
"""
from google.adk import Agent
from google.adk.agents import SequentialAgent

from .tools import analyze_ast, check_design_rules, list_files, read_source_file

# --- サブエージェント定義 ---

# 分析エージェント: ソースコードの読み取りとAST解析
code_analyzer = Agent(
    name="code_analyzer",
    model="gemini-3.5-flash",
    instruction="""ソースコードを分析するエージェントです。

## 手順
1. read_source_fileでファイルを読み取る
2. analyze_astでコード構造を解析する
3. 解析結果をoutput_keyに出力する

ユーザーが指定したファイルパスからソースコードを読み取り、
AST解析結果だけをJSON形式で出力してください。
設計レビュー、改善提案、モデル推奨、Markdownレポートは書かないでください。""",
    tools=[read_source_file, analyze_ast],
    output_key="analysis_result",
)

# レビューエージェント: 設計原則への準拠チェック
design_reviewer = Agent(
    name="design_reviewer",
    model="gemini-3.5-flash",
    instruction="""設計原則への準拠をレビューするエージェントです。

## 手順
1. Stateのanalysis_resultから解析結果を読み取る
2. check_design_rulesを1回呼び、analysis_resultをそのまま渡す
3. 評価セットなど補助ファイルの存在確認が必要な場合だけlist_filesを呼ぶ
4. チェック結果に基づいて、追加の所見を記述する

使用できるツールはcheck_design_rulesとlist_filesだけです。
read_source_fileやanalyze_astは前段のcode_analyzer専用のため、このエージェントでは呼び出しません。

## レビュー観点
- アーキテクチャ: 単一責任、ツール数、Instruction長
- セキュリティ: 最小権限、コールバック、入力検証
- 運用: 可観測性、エラーハンドリング、ループ防止
- コスト: モデル選択の妥当性
- 品質: 評価セットの有無

自動チェックで検出できない観点も含めて、包括的にレビューしてください。
モデル名の提案が必要な場合は、本書の標準であるgemini-3.5-flashだけを使ってください。
gemini-1.5-flash、gemini-2.5-flash、gemini-3-flash-previewなど古いモデル名は補完しないでください。""",
    tools=[check_design_rules, list_files],
    output_key="review_result",
)

# レポートエージェント: レビュー結果をMarkdownに整形
report_generator = Agent(
    name="report_generator",
    model="gemini-3.5-flash",
    instruction="""レビュー結果をMarkdownレポートにフォーマットするエージェントです。

## 出力フォーマット
以下のMarkdown形式でレポートを生成してください。

```
# 設計レビューレポート

## サマリー
（全体の評価を3行以内で記述）

## チェック結果

### アーキテクチャ
| # | チェック項目 | 結果 | 詳細 |
|---|---|---|---|
| A-1 | 単一責任 | 適合/要改善/未対応 | ... |

### セキュリティ
（同様のテーブル）

### 運用
（同様のテーブル）

### コスト
（同様のテーブル。該当する指摘がない場合も「該当なし」と記述）

### 品質
（同様のテーブル。Q-1などqualityカテゴリの指摘を必ず含める）

## 改善提案
1. （優先度順に改善提案を記述）
```

Stateのreview_resultを読み取り、findingsに含まれるruleを省略せずに上記フォーマットでレポートを生成してください。
モデル名やルールIDはreview_resultまたは解析対象コードに含まれる文字列を使い、古い例を補完しないでください。
モデル提案が必要な場合はreview_result.model_policy.allowed_recommendationsの値だけを使用し、
review_result.model_policy.forbidden_recommendationsに含まれるモデル名は出力しないでください。""",
    output_key="review_report",
)

# --- パイプライン ---

# 3つのエージェントをSequentialAgentで連携（既存テンプレートWorkflow例）
root_agent = SequentialAgent(
    name="design_review_pipeline",
    sub_agents=[code_analyzer, design_reviewer, report_generator],
)
