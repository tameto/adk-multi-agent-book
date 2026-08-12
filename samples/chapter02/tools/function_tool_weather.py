# function_tool_weather.py
# 2-6-2. FunctionTool: Python関数のツール化（基本形・完全版）
# Python関数をFunctionToolに変換し、LLMから呼び出せるようにする。

from google.adk import Agent
from google.adk.tools import FunctionTool


def get_weather(city: str, date: str) -> dict:
    """指定された都市の天気予報を取得する。

    Args:
        city: 天気を知りたい都市名（例: 東京、大阪、京都）
        date: 日付（YYYY-MM-DD形式、例: 2026-04-15）

    Returns:
        天気情報を含む辞書"""
    # 実際の実装ではWeather APIを呼び出す
    return {
        "city": city,
        "date": date,
        "weather": "晴れ",
        "temperature_high": 22,
        "temperature_low": 12,
        "precipitation_percent": 10,
    }


# FunctionToolの作成
weather_tool = FunctionTool(func=get_weather)

# エージェントに渡す
agent = Agent(
    name="weather_agent",
    model="gemini-3.5-flash",
    instruction="ユーザーが天気を聞いたら、get_weatherツールで調べてから回答してください。",
    tools=[weather_tool],
)

# adk run / adk web から参照できるようroot_agentとして公開する（補完）
root_agent = agent

if __name__ == "__main__":
    # ツール関数の動作確認（対話実行は adk run / adk web を使用）
    print(get_weather(city="京都", date="2026-04-15"))
