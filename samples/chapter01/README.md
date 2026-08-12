# 第1章 AIエージェントの全体像

ADKで最初のエージェントを動かすサンプルです。天気情報を返す関数ツールを1つ持つ最小構成から始め、観光情報のツールを足して2ツール構成に拡張するところまでを収録しています。`adk create`が生成するディレクトリ構造（`__init__.py`／`agent.py`／`.env`）をそのまま踏襲しているため、以降の章で繰り返し登場する形の出発点になります。

## 収録内容

| ファイル | 内容 |
|---|---|
| `hello_adk/agent.py` | 天気・観光情報エージェント（完全版）。`get_weather`と`get_sightseeing`の2ツールを持つ |
| `hello_adk/__init__.py` | `root_agent`を公開するパッケージ初期化 |
| `hello_adk/.env.example` | 環境変数のテンプレート |
| `requirements.txt` | 依存パッケージ（`google-adk==2.2.0`のみ） |

本文では`get_weather`だけの最小構成から解説を始めます。`agent.py`はその拡張を済ませた完成形に相当するため、写経の途中で本文とツール数が食い違っても問題ありません。

天気データと観光データはダミー実装です。東京・大阪・福岡・札幌の4都市だけを返し、外部APIは呼び出しません。実運用ではOpenWeatherMap等のAPI呼び出しに差し替えます。

## セットアップ

```bash
cd samples/chapter01
pip install -r requirements.txt

cd hello_adk
cp .env.example .env
```

`.env`に`GOOGLE_API_KEY`を設定してください。APIキーは https://aistudio.google.com/apikey から取得できます。Google Cloudプロジェクトは不要です。

## 実行

ターミナルで対話実行する場合は、章のディレクトリから`adk run`を使います。

```bash
cd samples/chapter01
adk run hello_adk
```

ブラウザの開発用Web UIで確認する場合は`adk web`を使います。起動後に http://localhost:8000 を開き、エージェント一覧から`hello_adk`を選びます。

```bash
cd samples/chapter01
adk web .
```

## 動作確認の例

```text
ユーザー: 東京の天気を教えて
エージェント: [get_weather 呼び出し]
→ 東京は晴れ、気温22度、湿度45%です

ユーザー: その天気に合う観光スポットは？
エージェント: [get_sightseeing 呼び出し]
→ 晴れているので屋外のスポットがおすすめです
```

ツールが呼ばれない場合は、Instructionにツールをいつ使うべきかが書かれているかを確認してください。ADKはツール関数のdocstringをLLMへの説明として使うため、docstringの記述もあわせて見直します。
