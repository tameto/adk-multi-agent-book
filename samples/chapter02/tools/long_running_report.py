# long_running_report.py
# 2-6-5. LongRunningFunctionTool: 長時間実行タスク（完全版）
# 完了まで時間がかかるタスク（数秒〜数分）を非同期に実行する。
# 中間状態の報告とポーリングをサポートする。

import asyncio

from google.adk.tools import LongRunningFunctionTool


async def generate_report(
    topic: str,
    pages: int,
) -> dict:
    """指定されたトピックについてレポートを生成する。

    Args:
        topic: レポートのトピック
        pages: 生成するページ数

    Returns:
        生成されたレポート"""
    # 長時間の処理をシミュレート
    sections = []
    for i in range(pages):
        await asyncio.sleep(2)  # 各ページの生成に2秒
        sections.append(f"Section {i+1}: {topic}の分析...")

    return {
        "status": "completed",
        "topic": topic,
        "pages": pages,
        "sections": sections,
    }


# LongRunningFunctionToolの作成
report_tool = LongRunningFunctionTool(func=generate_report)

if __name__ == "__main__":
    # ツール関数の動作確認（2ページ分・約4秒）
    result = asyncio.run(generate_report(topic="AIエージェント市場", pages=2))
    print(result)
