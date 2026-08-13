# 5-3-6. シミュレーション結果の分析と改善
# 紙面の掲載パス: scripts/analyze_persona_results.py
"""ペルソナ評価結果の分析"""
import json
from pathlib import Path


def analyze_results(results_path: str) -> dict:
    """ペルソナ評価結果を分析し、改善提案を生成する"""
    with open(results_path) as f:
        results = json.load(f)

    analysis: dict[str, list] = {
        "weak_personas": [],
        "efficiency_issues": [],
        "safety_breaches": [],
    }

    for persona_result in results.get("persona_results", []):
        name = persona_result["name"]
        score = persona_result["score"]
        turns = persona_result["turns"]
        max_turns = persona_result["max_turns"]

        # パターン1: スコアが低いペルソナを特定
        if score < 0.7:
            analysis["weak_personas"].append({
                "name": name,
                "score": score,
                "suggestion": "Instructionの改善またはツール追加を検討",
            })

        # パターン2: ターン効率が悪いケースを特定
        if turns > max_turns * 0.8:
            analysis["efficiency_issues"].append({
                "name": name,
                "turns": turns,
                "max_turns": max_turns,
                "suggestion": "応答の簡潔化またはインタラクション設計の見直し",
            })

        # パターン3: 安全性違反を特定
        if not persona_result.get("safety_maintained", True):
            analysis["safety_breaches"].append({
                "name": name,
                "suggestion": "ガードレールの追加が必要",
            })

    return analysis


if __name__ == "__main__":
    import sys

    # 使用例: python scripts/analyze_persona_results.py persona_results.json
    path = sys.argv[1] if len(sys.argv) > 1 else "persona_results.json"
    if Path(path).exists():
        print(json.dumps(analyze_results(path), ensure_ascii=False, indent=2))
    else:
        print(f"結果ファイルが見つかりません: {path}")
