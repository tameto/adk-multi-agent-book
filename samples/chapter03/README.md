# 第3章 Context Engineering & Agent Skills

LLMに何を渡すかを設計するためのサンプルです。Contextの4種類（InvocationContext／ReadonlyContext／CallbackContext／ToolContext）、Instructionの静的・動的・グローバルの書き分け、4種類のコールバック、Agent Skillsの定義と読み込みを収録しています。ハンズオンの成果物は`support_agent/`で、スキル3つとコンテキスト制御コールバックを組み込んだカスタマーサポートエージェントです。

## 収録内容

| ディレクトリ／ファイル | 内容 |
|---|---|
| `support_agent/` | ハンズオン成果物。コンテキスト最適化カスタマーサポートエージェント |
| `skills/order-management/` | 注文管理スキル（`SKILL.md` + `references/cancel-policy.md`） |
| `skills/product-inquiry/` | 商品問い合わせスキル（`SKILL.md` + `assets/category-list.md`） |
| `skills/review-analysis/` | 商品レビュー分析スキル（`SKILL.md` + `references/output-format.md`） |
| `review_analysis_example/` | スキルをEnd-to-Endで組み込む手順の例（`load_skill_from_dir`） |
| `context_types/custom_agent_example.py` | InvocationContextを直接操作するカスタムエージェント |
| `context_types/callback_context_example.py` | CallbackContextでStateを書き込み、LlmResponseを差し替える |
| `context_types/tool_context_artifact.py` | ToolContextのArtifact操作 |
| `context_propagation/state_scopes.py` | `user:`／session／`temp:`のStateスコープの使い分け |
| `context_propagation/multi_agent_state.py` | マルチエージェント構成でのコンテキスト伝播 |
| `instructions/static_instruction.py` | 静的Instruction（文字列リテラル） |
| `instructions/dynamic_instruction.py` | 動的Instruction（ReadonlyContextを受け取るcallable） |
| `instructions/global_instruction.py` | グローバルInstruction（GlobalInstructionPluginへの静的登録） |
| `instructions/global_instruction_dynamic.py` | グローバルInstruction（callable版） |
| `instructions/instruction_templates.py` | 再利用可能な3つのテンプレートパターン |
| `callbacks_examples/before_model.py`ほか | 4種類のコールバックと合成パターン、ガードレール応用 |
| `callbacks_examples/tests/test_callbacks.py` | コールバックのユニットテスト |
| `skill_patterns/shared_library.py` | 共通スキルライブラリの参照 |
| `skill_patterns/conditional_loading.py` | 権限に応じたスキルの条件付き読み込み |
| `skill_patterns/versioning.py` | スキルのバージョニングとA/Bテスト |

## セットアップ

```bash
cd samples/chapter03
pip install -r requirements.txt

cd support_agent
cp .env.example .env
```

APIキーだけで動きます。Google Cloudプロジェクトは不要です。

## 実行

```bash
cd samples/chapter03
adk run support_agent
```

`support_agent`は`instruction=build_instruction`でcallableを渡す動的Instructionを使います。ADK v2.2.0の`/apps/{app_name}/app-info` APIは`instruction`を文字列として扱うため、`adk web`ではエージェント情報の表示が失敗する場合があります。動作確認は`adk run`を主経路にしてください。

コールバックのテストはpytestで実行します。

```bash
cd samples/chapter03/callbacks_examples
pytest tests/
```

## スキルの配置について

スキル本体（`SKILL.md`とその参照ファイル）は`skills/`にまとめ、スキルが使う関数ツールはエージェント側の`tools.py`に置いています。スキルディレクトリ内にPythonコードを置かない構成です。`review_analysis_example/`は、この分離を保ったままスキルを組み込む手順を独立したディレクトリで示したものです。
