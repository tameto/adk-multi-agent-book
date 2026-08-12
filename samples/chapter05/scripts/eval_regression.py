"""評価結果の回帰チェック

`adk eval` の評価結果をスナップショットとして保存し、
前回（ベースライン）との差分を検出する比較スクリプトです。
メトリクスごとにベースラインのスコアと比較し、
regression_threshold（既定0.05）を超えて低下していれば回帰として報告します。

使い方:
    python scripts/eval_regression.py <current_results.json> <baseline.json>
"""
import json
import sys
from pathlib import Path


def compare_with_baseline(
    current_results: dict,
    baseline_path: str,
    regression_threshold: float = 0.05,
) -> list[str]:
    """現在の評価結果をベースラインと比較する"""
    baseline_file = Path(baseline_path)
    if not baseline_file.exists():
        # ベースラインがない初回実行は回帰なしとして扱う
        return []
    baseline = json.loads(baseline_file.read_text())

    regressions = []
    for metric_name, current_score in current_results.get("metrics", {}).items():
        baseline_score = baseline.get("metrics", {}).get(metric_name, 0)
        diff = baseline_score - current_score
        if diff > regression_threshold:
            # スコア差分を整形して記録する
            regressions.append(
                f"回帰検出: {metric_name} "
                f"(ベースライン {baseline_score:.3f} → 現在 {current_score:.3f}, "
                f"低下幅 {diff:.3f})"
            )
    return regressions


def save_snapshot(current_results: dict, baseline_path: str) -> None:
    """現在の評価結果をベースラインとして保存する"""
    Path(baseline_path).write_text(
        json.dumps(current_results, ensure_ascii=False, indent=2)
    )


def main() -> int:
    """評価結果ファイルとベースラインを比較し、回帰があれば終了コード1を返す"""
    if len(sys.argv) != 3:
        print(__doc__)
        return 2

    current_path, baseline_path = sys.argv[1], sys.argv[2]
    current_results = json.loads(Path(current_path).read_text())

    regressions = compare_with_baseline(current_results, baseline_path)
    if regressions:
        for line in regressions:
            print(line)
        return 1

    # 回帰がなければ現在の結果を新しいベースラインとして保存する
    save_snapshot(current_results, baseline_path)
    print("回帰なし: ベースラインを更新しました")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
