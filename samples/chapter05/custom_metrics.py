# 5-2-6. カスタムメトリクスの実装
# 紙面の掲載パス: custom_metrics.py
# eval_config.json では custom_metrics.domain_accuracy.code_config.name を
# "custom_metrics.domain_accuracy"（<module_path>.<function_name>）と指定する。
"""ドメイン固有の数値正確性を評価するカスタムメトリクス関数"""
import re
from typing import Optional

from google.adk.evaluation.eval_case import ConversationScenario, Invocation
from google.adk.evaluation.eval_metrics import EvalMetric
from google.adk.evaluation.evaluator import (
    EvaluationResult,
    EvalStatus,
    PerInvocationResult,
)


def _extract_numbers(text: str) -> list[float]:
    """テキストから数値を抽出する(カンマ区切り対応)"""
    pattern = r"[\d,]+\.?\d*"
    numbers: list[float] = []
    for m in re.findall(pattern, text):
        try:
            numbers.append(float(m.replace(",", "")))
        except ValueError:
            continue
    return numbers


def domain_accuracy(
    eval_metric: EvalMetric,
    actual_invocations: list[Invocation],
    expected_invocations: Optional[list[Invocation]],
    conversation_scenario: Optional[ConversationScenario] = None,
) -> EvaluationResult:
    """応答内の数値を参照応答と照合する(許容誤差1%で一致判定)"""
    threshold = (
        eval_metric.criterion.threshold
        if eval_metric.criterion and eval_metric.criterion.threshold is not None
        else 0.8
    )
    per_invocation_results: list[PerInvocationResult] = []
    total_score = 0.0

    for actual, expected in zip(actual_invocations, expected_invocations or []):
        actual_text = (
            actual.final_response.parts[0].text if actual.final_response else ""
        )
        expected_text = (
            expected.final_response.parts[0].text if expected.final_response else ""
        )

        expected_numbers = _extract_numbers(expected_text)
        actual_numbers = _extract_numbers(actual_text)

        if not expected_numbers:
            # 参照応答に数値が含まれなければ満点扱い
            score = 1.0
        else:
            matches = sum(
                1
                for ref in expected_numbers
                if any(
                    abs(ref - act) / max(abs(ref), 1e-10) < 0.01
                    for act in actual_numbers
                )
            )
            score = matches / len(expected_numbers)

        total_score += score
        status = EvalStatus.PASSED if score >= threshold else EvalStatus.FAILED
        per_invocation_results.append(
            PerInvocationResult(
                actual_invocation=actual,
                expected_invocation=expected,
                score=score,
                eval_status=status,
            )
        )

    overall_score = (
        total_score / len(per_invocation_results)
        if per_invocation_results
        else 0.0
    )
    overall_status = (
        EvalStatus.PASSED if overall_score >= threshold else EvalStatus.FAILED
    )

    return EvaluationResult(
        overall_score=overall_score,
        overall_eval_status=overall_status,
        per_invocation_results=per_invocation_results,
    )


# ============================================================
# 5-2-7. メトリクス設計の実践パターン
# パターン3: 回帰テストとスナップショット（完全版）
# 紙面の掲載パス: scripts/eval_regression.py
# ============================================================
# 補完: 以下のimportはこのセクションでのみ使用するため、末尾追記に合わせてここに置く。
import json
from pathlib import Path


def compare_with_baseline(
    current_results: dict,
    baseline_path: str,
    regression_threshold: float = 0.05,
) -> list[str]:
    """現在の評価結果をベースラインと比較する"""
    baseline_file = Path(baseline_path)
    if not baseline_file.exists():
        return []

    with open(baseline_file) as f:
        baseline = json.load(f)

    regressions = []
    for metric_name, current_score in current_results.get("metrics", {}).items():
        baseline_score = baseline.get("metrics", {}).get(metric_name, 0)
        diff = baseline_score - current_score

        if diff > regression_threshold:
            regressions.append(
                f"回帰検出: {metric_name} "
                f"{baseline_score:.2f} → {current_score:.2f} "
                f"(差分: -{diff:.2f})"
            )

    return regressions
