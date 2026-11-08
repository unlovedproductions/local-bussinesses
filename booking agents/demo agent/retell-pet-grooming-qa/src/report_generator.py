"""Generate QA report artifacts."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.scoring import aggregate_run
from src.storage import run_dir, write_json


def generate_reports(settings, run_id: str, results: list[dict[str, Any]], cases: list[dict[str, Any]]) -> dict[str, Path]:
    d = run_dir(settings, run_id) / "reports"
    agg = aggregate_run(results)
    by_id = {r.get("test_id"): r for r in results}

    scorecard = {
        "title": "Executive Scorecard",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "overall_qa_score": agg["score"]["overall"],
        "interpretation": agg["score"]["interpretation"],
        "production_readiness": agg["score"]["production_readiness"],
        "tests_planned": len(cases),
        "tests_executed": agg["executed"],
        "counts": agg["counts"],
        "pass_rate": agg["pass_rate"],
        "severities": agg["severities"],
        "critical_risks": [
            r for r in results if r.get("severity") in {"P0", "P1"} or r.get("status") == "FAIL"
        ],
        "recommended_next_actions": _next_actions(agg, results),
    }
    p1 = d / "executive_scorecard.json"
    write_json(p1, scorecard)
    (d / "executive_scorecard.md").write_text(_scorecard_md(scorecard))

    matrix = []
    for c in cases:
        r = by_id.get(c["id"], {})
        matrix.append(
            {
                "test_id": c["id"],
                "suite": c.get("suite"),
                "scenario": c.get("title"),
                "status": r.get("status", "NOT_RUN"),
                "expected_result": c.get("expected_behavior"),
                "actual_result": r.get("observed_behavior") or r.get("actual_behavior"),
                "severity": r.get("severity"),
                "call_id": (r.get("call_ids") or {}).get("receptionist") or (r.get("call_ids") or {}).get("outbound"),
                "evidence_reference": r.get("evidence_path"),
                "recommended_fix": r.get("recommended_fix"),
            }
        )
    p2 = d / "test_matrix.json"
    write_json(p2, matrix)

    audits = []
    for r in results:
        if r.get("status") in {"NOT_RUN", "BLOCKED"} and not r.get("transcript"):
            continue
        audits.append(
            {
                "test_id": r.get("test_id"),
                "persona": r.get("persona"),
                "scenario": r.get("title"),
                "transcript": r.get("transcript"),
                "timestamps": r.get("timestamps"),
                "duration": r.get("duration"),
                "tool_calls": r.get("tool_events"),
                "integration_outcomes": r.get("verification"),
                "findings": r.get("observed_behavior"),
                "defects": r.get("defects"),
            }
        )
    p3 = d / "conversation_audit.json"
    write_json(p3, audits)

    remediation = {"groups": _group_fixes(results)}
    p4 = d / "remediation_plan.json"
    write_json(p4, remediation)

    from src.regression_generator import generate_regression_plan
    regression = generate_regression_plan(results)
    p5 = d / "regression_plan.json"
    write_json(p5, regression)

    return {
        "executive_scorecard": p1,
        "test_matrix": p2,
        "conversation_audit": p3,
        "remediation_plan": p4,
        "regression_plan": p5,
    }


def _next_actions(agg: dict[str, Any], results: list[dict[str, Any]]) -> list[str]:
    actions = []
    if agg["counts"].get("BLOCKED"):
        actions.append("Resolve BLOCKED scenarios: credentials, sandbox proof, adapters, phone numbers.")
    if agg["severities"].get("P0"):
        actions.append("Do not promote to production until all P0 defects are fixed and retested.")
    if agg["counts"].get("FAIL"):
        actions.append("Apply remediation plan on staging; run regression selection.")
    if agg["score"]["overall"] is None:
        actions.append("Configure judge model and collect complete evidence before trusting overall score.")
    if not actions:
        actions.append("Expand coverage beyond smoke tests; keep sandbox gates enabled.")
    return actions


def _scorecard_md(s: dict[str, Any]) -> str:
    lines = [
        f"# {s['title']}",
        "",
        f"- Run: `{s['run_id']}`",
        f"- Overall QA score: {s['overall_qa_score']} ({s['interpretation']})",
        f"- Production readiness: **{s['production_readiness']}**",
        f"- Planned: {s['tests_planned']}",
        f"- Executed: {s['tests_executed']}",
        f"- Pass rate: {s['pass_rate']}",
        f"- Counts: `{json.dumps(s['counts'])}`",
        f"- Severities: `{json.dumps(s['severities'])}`",
        "",
        "## Recommended next actions",
    ]
    for a in s["recommended_next_actions"]:
        lines.append(f"- {a}")
    return "\n".join(lines) + "\n"


def _group_fixes(results: list[dict[str, Any]]) -> dict[str, list[str]]:
    groups = {
        "Retell system prompt": [],
        "Knowledge base": [],
        "Conversation flow": [],
        "Speech recognition": [],
        "Booking tools": [],
        "CRM tools": [],
        "Transfers": [],
        "Security and authorization": [],
        "Latency": [],
    }
    for r in results:
        if r.get("status") != "FAIL":
            continue
        fix = r.get("recommended_fix") or "Investigate failure with transcript and backend evidence."
        suite = (r.get("test_id") or "?")[0]
        mapping = {
            "A": "Conversation flow",
            "B": "Speech recognition",
            "C": "Knowledge base",
            "D": "Booking tools",
            "E": "CRM tools",
            "F": "Conversation flow",
            "G": "Conversation flow",
            "H": "Security and authorization",
            "I": "Transfers",
            "J": "Booking tools",
        }
        groups[mapping.get(suite, "Conversation flow")].append(f"{r.get('test_id')}: {fix}")
    return {k: v for k, v in groups.items() if v}
