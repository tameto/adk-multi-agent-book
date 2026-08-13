# 第5章 評価・ガードレール・HITL

エージェントの品質を測り、危険な出力を止め、人間の判断に戻すためのサンプルです。`adk eval`の評価セットとCI統合、入力・出力・ツールの3層ガードレール、承認フロー（HITL）を収録しています。ハンズオンの成果物は`expense_agent/`で、プロンプトインジェクション検出・PII漏えい防止・高額経費の承認フローを1つのエージェントに組み込んだ経費精算エージェントです。

## 収録内容

| ディレクトリ／ファイル | 内容 |
|---|---|
| `expense_agent/` | ハンズオン成果物。ガードレールとHITLを組み込んだ経費精算エージェント |
| `eval/eval_set.json` | 評価セット（正常系・異常系・Jailbreak試行） |
| `eval/eval_config.json` | 評価基準（`tool_trajectory_avg_score` 0.8、`response_match_score` 0.6） |
| `guardrails/input_guardrails.py` | before_model_callbackによる入力フィルタリング |
| `guardrails/output_guardrails.py` | after_model_callbackによる出力検証 |
| `guardrails/tool_guardrails.py` | ツールコールバックによる操作制御 |
| `guardrails/layered_guardrails.py` | 複数ガードレールを重ねるレイヤード構成 |
| `guardrails/context_aware_guardrails.py` | Stateに応じて判定を変えるコンテキスト依存ガードレール |
| `guardrails/soft_block.py` | 拒否せず代替案を返すソフトブロック |
| `guardrails/dlp_guardrail.py` | Cloud DLP APIを使った機密情報検出（発展） |
| `guardrails/agent.py` | ガードレールを適用したエージェント定義 |
| `hitl/approval_flow.py` | ApprovalManagerによる同期承認フロー |
| `hitl/async_approval.py` | Firestoreを使った非同期承認フロー（発展） |
| `hitl/escalation.py` | エスカレーション設計 |
| `hitl/dashboard_data.py` | 承認ダッシュボードのデータ取得（発展） |
| `hitl/agent.py`／`hitl/tools.py` | HITL対応エージェントと承認対象の業務ツール |
| `custom_metrics.py` | ドメイン固有の数値正確性を評価するカスタムメトリクス |
| `scripts/analyze_persona_results.py` | ペルソナ評価結果の分析と改善提案の生成 |
| `scripts/eval_regression.py` | ベースラインとの比較による回帰チェック |
| `scripts/check_eval_thresholds.py` | 評価結果の閾値チェック |
| `ci/agent-eval.yml` | GitHub Actionsのワークフロー定義 |
| `tests/test_guardrails.py` | ガードレールのユニットテスト |

## セットアップ

```bash
cd samples/chapter05
pip install -r requirements.txt

cd expense_agent
cp .env.example .env
```

`requirements.txt`はADKの`eval` extraとpytestを含みます。`google-cloud-dlp`と`google-cloud-firestore`は発展サンプル（`guardrails/dlp_guardrail.py`、`hitl/async_approval.py`、`hitl/dashboard_data.py`）を動かす場合にだけ必要です。

## 実行

経費精算エージェントを対話実行します。

```bash
cd samples/chapter05
adk run expense_agent
```

評価セットを実行します。

```bash
cd samples/chapter05
adk eval ./expense_agent eval/eval_set.json \
  --config_file_path=eval/eval_config.json
```

スコアが低い項目を特定してInstructionまたはガードレールを直し、再度評価するサイクルを回します。

ガードレールのユニットテストはGCP接続なしで実行できます。

```bash
cd samples/chapter05
pytest tests/test_guardrails.py -v
```

`guardrails/`と`hitl/`はどちらも`root_agent`を公開しているため、単体で`adk run guardrails`／`adk run hitl`としても動かせます。

## Google Cloudが必要なサンプル

`guardrails/dlp_guardrail.py`はCloud DLP APIと環境変数`GOOGLE_CLOUD_PROJECT`が必要です。`hitl/async_approval.py`と`hitl/dashboard_data.py`はFirestoreを使います。どちらもGoogle Cloudプロジェクトと課金の有効化が前提です。それ以外のサンプルはAPIキーだけで動きます。
