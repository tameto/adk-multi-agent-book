# 5-1-8. CI/CDパイプラインへの統合
# 紙面の掲載パス: scripts/check_eval_thresholds.py
"""評価結果の閾値チェックスクリプト"""
import json
import sys
from pathlib import Path

# メトリクスごとの合格閾値（response_evaluation_score のみ 1-5 スケール、他は 0-1 スケール）
THRESHOLDS = {
    "tool_trajectory_avg_score": 0.8,
    "response_match_score": 0.7,
    "response_evaluation_score": 3.5,
}


def check_thresholds(results_dir: str) -> bool:
    """評価結果が閾値を満たしているかチェックする"""
    results_path = Path(results_dir)
    all_passed = True

    for result_file in results_path.glob("*.json"):
        with open(result_file) as f:
            results = json.load(f)

        for metric_name, threshold in THRESHOLDS.items():
            score = results.get("metrics", {}).get(metric_name, 0)
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

    return all_passed


if __name__ == "__main__":
    results_dir = sys.argv[1] if len(sys.argv) > 1 else "eval_results/"
    if not check_thresholds(results_dir):
        # 閾値未達のメトリクスがあればCIを失敗させる
        sys.exit(1)
