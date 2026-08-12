# 第9章 設計原則 & アンチパターン

エージェント設計の原則と、現場で繰り返し見かける失敗パターンを、動くコードで対比するサンプルです。原則側は「なぜそう書くか」を実装で示し、アンチパターン側は問題のあるコードと改善版を同じファイルに並べています。ハンズオンの成果物は`design_review/`で、ADKエージェントのソースコードをAST解析し、設計原則への準拠度をチェックする設計レビュー自動化エージェントです。

## 収録内容

| ディレクトリ／ファイル | 内容 |
|---|---|
| `design_review/agent.py` | ハンズオン成果物。分析 → レビュー → レポート生成の3段SequentialAgent |
| `design_review/tools.py` | AST解析・ソース読み取り・設計ルールチェックのツール群 |
| `design_review/checklist.py` | 設計原則10選に基づくチェックリスト定義 |
| `principles/principle_01_single_responsibility.py` | 原則1：単一責任エージェント |
| `principles/principle_02_least_privilege.py` | 原則2：最小権限 |
| `principles/principle_03_idempotency.py` | 原則3：冪等性（冪等キーとupsert） |
| `principles/principle_04_observability.py` | 原則4：可観測性（カスタムメトリクスの記録） |
| `principles/principle_05_graduated_autonomy.py` | 原則5：段階的自律性（自律レベル×リスクレベル） |
| `principles/principle_09_fail_safe.py` | 原則9：フェイルセーフ（3レイヤーの防御） |
| `principles/principle_10_cost_aware.py` | 原則10：コスト意識（責務分離・キャッシュ・監視） |
| `antipatterns/antipattern_01_god_agent.py` | God Agentと責務分割による改善 |
| `antipatterns/antipattern_04_infinite_loop.py` | 無限ループと3層の停止条件 |
| `antipatterns/antipattern_06_security_afterthought.py` | セキュリティの後付けと設計時からの組み込み |
| `antipatterns/antipattern_11_config_drift.py` | 設定の直書きと環境変数への外部化 |
| `test_target_agent.py` | レビュー対象のサンプル（原則違反を意図的に含む） |
| `eval/eval_set.json` | 評価セット（正常系1件、異常系2件） |
| `eval/eval_config.json` | 評価基準（`response_match_score` 0.5） |
| `eval/test_target_bad.py` | 評価用ターゲット：ツール数過多（A-2違反） |
| `eval/test_target_insecure.py` | 評価用ターゲット：入力検証と権限制御の欠如（S-2／S-6違反） |

`principles/`と`antipatterns/`には、紙面で完全版を示した項目を収録しています。番号は本文の原則番号・アンチパターン番号に対応するため、連番が飛んでいる箇所があります。

## セットアップ

```bash
cd samples/chapter09
pip install -r requirements.txt

cd design_review
cp .env.example .env
```

APIキーだけで動きます。Google Cloudプロジェクトは不要です。`requirements.txt`はADKの`eval` extraを指定しています。

## 実行

設計レビューエージェントを対話実行し、レビュー対象のファイルパスを渡します。

```bash
cd samples/chapter09
adk run design_review
```

```text
ユーザー: test_target_agent.py をレビューしてください
エージェント: [read_source_file → analyze_ast → check_design_rules 呼び出し]
→ APIキーの直書き、ツール数過多、コールバック未設定を指摘したMarkdownレポート
```

`design_review`のRootは`SequentialAgent`です。ADK v2.2.0の`/apps/{app_name}/app-info` APIはRootを`LlmAgent`として扱うため、`adk web`ではエージェント情報の表示が失敗する場合があります。動作確認は`adk run`または`adk eval`を主経路にしてください。

評価セットを実行します。

```bash
cd samples/chapter09
adk eval ./design_review eval/eval_set.json \
  --config_file_path=eval/eval_config.json
```

ADK v2.2.0の`adk eval`は`root_agent`を公開するエージェントディレクトリを引数に取ります。実行するとEval Run SummaryにTests passed／Tests failedが出力されます。

## レビュー対象のサンプルについて

`test_target_agent.py`、`eval/test_target_bad.py`、`eval/test_target_insecure.py`の3ファイルは、設計レビューエージェントの入力として使うためのものです。APIキーの直書き、危険ツールの付与、コールバック未設定といった問題を意図的に埋め込んでいます。実行を想定した実装ではないため、これらを他のプロジェクトの雛形として流用しないでください。
