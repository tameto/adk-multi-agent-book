# 5-1-8. CI/CDパイプラインへの統合
# 紙面の掲載パス: scripts/check_eval_thresholds.py
"""評価結果の閾値チェックスクリプト

`adk eval` が書き出す EvalSetResult 形式のJSON
（既定は <agent_dir>/.adk/eval_history/*.evalset_result.json）を読み、
メトリクスごとの閾値を満たしているかを判定する。
"""
import json
import sys
from pathlib import Path

# メトリクスごとの合格閾値（response_evaluation_score のみ 1-5 スケール、他は 0-1 スケール）
THRESHOLDS = {
    "tool_trajectory_avg_score": 0.8,
    "response_match_score": 0.7,
    "response_evaluation_score": 3.5,
}


def collect_scores(results: dict) -> dict[str, list[float]]:
    """EvalSetResult形式のJSONからメトリクス名ごとのスコアを集める"""
    scores: dict[str, list[float]] = {}
    for case_result in results.get("eval_case_results", []):
        for metric_result in case_result.get("overall_eval_metric_results", []):
            metric_name = metric_result.get("metric_name")
            score = metric_result.get("score")
            # スコアが算出できなかったメトリクスは None で入るため除外する
            if metric_name is None or score is None:
                continue
            scores.setdefault(metric_name, []).append(float(score))
    return scores


def check_thresholds(results_dir: str) -> bool:
    """評価結果が閾値を満たしているかチェックする"""
    results_path = Path(results_dir)
    all_passed = True
    checked_files = 0

    for result_file in sorted(results_path.glob("*.json")):
        results = json.loads(result_file.read_text(encoding="utf-8"))
        scores = collect_scores(results)
        if not scores:
            continue
        checked_files += 1

        for metric_name, threshold in THRESHOLDS.items():
            if metric_name not in scores:
                # 評価設定に含まれないメトリクスはスキップする
                continue
            # 評価ケースをまたいだ平均スコアで判定する
            score = sum(scores[metric_name]) / len(scores[metric_name])
            if score < threshold:
                print(
                    f"FAIL: {result_file.name} - "
                    f"{metric_name}: {score:.2f} < {threshold:.2f}"
                )
                all_passed = False
            else:
                print(
                    f"PASS: {result_file.name} - "
                    f"{metric_name}: {score:.2f} >= {threshold:.2f}"
                )

    if checked_files == 0:
        # 対象ファイルが1件もない場合は素通りさせずCIを失敗させる
        print(f"FAIL: 評価結果のJSONが見つかりません: {results_path}")
        return False

    return all_passed


if __name__ == "__main__":
    results_dir = (
        sys.argv[1] if len(sys.argv) > 1 else "expense_agent/.adk/eval_history"
    )
    if not check_thresholds(results_dir):
        # 閾値未達のメトリクスがあればCIを失敗させる
        sys.exit(1)
