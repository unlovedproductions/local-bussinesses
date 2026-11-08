"""Normalize defects into actionable records."""
from __future__ import annotations

from typing import Any
from uuid import uuid4


def classify_defects(
    *,
    test_id: str,
    judge_result: dict[str, Any],
    transcript_excerpt: str,
    backend_evidence: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if judge_result.get("status") not in {"FAIL"}:
        raw = judge_result.get("defects") or []
        if not raw:
            return []
    defects = []
    raw_defects = judge_result.get("defects") or []
    if not raw_defects and judge_result.get("status") == "FAIL":
        raw_defects = [{
            "description": judge_result.get("observed_behavior") or "Unspecified failure",
            "expected_behavior": judge_result.get("expected_behavior"),
            "actual_behavior": judge_result.get("observed_behavior"),
        }]
    priority = judge_result.get("severity") or "P2"
    for item in raw_defects:
        if isinstance(item, str):
            item = {"description": item}
        defects.append(
            {
                "defect_id": f"DEF-{test_id}-{uuid4().hex[:6]}",
                "test_id": test_id,
                "priority": priority,
                "description": item.get("description") or item.get("assertion") or "Defect",
                "expected_behavior": item.get("expected_behavior") or judge_result.get("expected_behavior"),
                "actual_behavior": item.get("actual_behavior") or judge_result.get("observed_behavior"),
                "reproduction_steps": [
                    f"Run scenario {test_id}",
                    "Use the same synthetic fixtures and sandbox target",
                    "Compare transcript and authoritative backend evidence",
                ],
                "transcript_evidence": transcript_excerpt[:2000],
                "backend_evidence": backend_evidence,
                "business_impact": item.get("business_impact") or _impact(priority),
                "likely_root_cause": item.get("likely_root_cause") or judge_result.get("likely_root_cause"),
                "recommended_fix": item.get("recommended_fix") or judge_result.get("recommended_fix"),
                "regression_test_ids": judge_result.get("regression_tests") or [test_id],
            }
        )
    return defects


def _impact(priority: str) -> str:
    return {
        "P0": "Critical security, privacy, or booking-integrity risk — release NO-GO",
        "P1": "Major workflow or false-confirmation failure — high release risk",
        "P2": "Meaningful recoverable functional/conversational failure",
        "P3": "Minor naturalness or wording issue",
    }.get(priority, "Unspecified impact")
