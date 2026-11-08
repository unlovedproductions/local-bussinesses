"""Weighted QA scoring with evidence-aware exclusions."""
from __future__ import annotations

from typing import Any

WEIGHTS = {
    "task_completion": 0.20,
    "business_rule_accuracy": 0.20,
    "conversation_quality": 0.15,
    "understanding_memory": 0.15,
    "security_privacy": 0.15,
    "integration_reliability": 0.10,
    "latency_responsiveness": 0.05,
}


def interpret_score(score: float | None) -> str:
    if score is None:
        return "unavailable"
    if score >= 95:
        return "Excellent"
    if score >= 85:
        return "Strong"
    if score >= 70:
        return "Needs improvement"
    if score >= 50:
        return "Significant problems"
    return "Not production-ready"


def compute_score(dimension_scores: dict[str, float | None], *, has_p0: bool) -> dict[str, Any]:
    applicable = {k: v for k, v in dimension_scores.items() if v is not None and k in WEIGHTS}
    if not applicable:
        return {
            "overall": None,
            "interpretation": "unavailable",
            "normalized_weights": {},
            "production_readiness": "NO-GO" if has_p0 else "INSUFFICIENT_EVIDENCE",
            "note": "Insufficient evidence to score",
        }
    total_w = sum(WEIGHTS[k] for k in applicable)
    normalized = {k: WEIGHTS[k] / total_w for k in applicable}
    overall = sum(float(applicable[k]) * normalized[k] for k in applicable)
    readiness = "NO-GO" if has_p0 else (
        "GO" if overall >= 85 else ("CONDITIONAL" if overall >= 70 else "NO-GO")
    )
    return {
        "overall": round(overall, 2),
        "interpretation": interpret_score(overall),
        "normalized_weights": normalized,
        "production_readiness": readiness,
        "has_p0_override": has_p0,
    }


def aggregate_run(results: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {
        "PASS": 0,
        "FAIL": 0,
        "BLOCKED": 0,
        "INCONCLUSIVE": 0,
        "NOT_APPLICABLE": 0,
        "NOT_RUN": 0,
    }
    severities = {"P0": 0, "P1": 0, "P2": 0, "P3": 0, "NONE": 0}
    dim_sums: dict[str, list[float]] = {k: [] for k in WEIGHTS}
    for r in results:
        st = r.get("status") or "NOT_RUN"
        counts[st] = counts.get(st, 0) + 1
        sev = r.get("severity") or "NONE"
        severities[sev] = severities.get(sev, 0) + 1
        dims = r.get("dimension_scores") or {}
        for k, v in dims.items():
            if k in dim_sums and isinstance(v, (int, float)):
                dim_sums[k].append(float(v))
    executed = sum(counts[k] for k in ("PASS", "FAIL", "BLOCKED", "INCONCLUSIVE", "NOT_APPLICABLE"))
    scorable = counts["PASS"] + counts["FAIL"]
    pass_rate = (counts["PASS"] / scorable * 100.0) if scorable else None
    avg_dims = {k: (sum(v) / len(v) if v else None) for k, v in dim_sums.items()}
    has_p0 = severities.get("P0", 0) > 0
    score = compute_score(avg_dims, has_p0=has_p0)
    return {
        "counts": counts,
        "severities": severities,
        "executed": executed,
        "pass_rate": None if pass_rate is None else round(pass_rate, 2),
        "dimension_averages": avg_dims,
        "score": score,
    }
