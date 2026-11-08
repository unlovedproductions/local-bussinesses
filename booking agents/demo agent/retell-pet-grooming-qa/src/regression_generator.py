"""Generate regression selections from failed results."""
from __future__ import annotations

from typing import Any

SUITE_NEIGHBORS = {
    "A": ["A01", "A02", "A05"],
    "B": ["B12"],
    "C": ["C01", "C05", "C06", "C11"],
    "D": ["D01", "D02", "D06", "D12"],
    "E": ["E01", "E06", "E10"],
    "F": ["F01", "F05", "F06"],
    "G": ["G01", "G06", "G10"],
    "H": ["H01", "H02", "H03", "H10"],
    "I": ["I01", "I06", "I10"],
    "J": ["J01", "J04", "J07"],
}


def generate_regression_plan(results: list[dict[str, Any]]) -> dict[str, Any]:
    failed = [r for r in results if r.get("status") == "FAIL"]
    selected: list[str] = []
    workflows: list[str] = []
    for r in failed:
        tid = r.get("test_id")
        if tid:
            selected.append(tid)
        suite = (tid or "?")[0]
        workflows.append(suite)
        selected.extend(SUITE_NEIGHBORS.get(suite, []))
        for x in r.get("regression_tests") or []:
            selected.append(x)
        for d in r.get("defects") or []:
            selected.extend(d.get("regression_test_ids") or [])
    # unique preserve order
    seen = set()
    ordered = []
    for tid in selected:
        if tid not in seen:
            seen.add(tid)
            ordered.append(tid)
    return {
        "failed_test_ids": [r.get("test_id") for r in failed],
        "affected_workflows": sorted(set(workflows)),
        "recommended_retests": ordered,
        "unresolved_high_severity": [
            r.get("test_id") for r in failed if r.get("severity") in {"P0", "P1"}
        ],
    }


def compare_runs(before: list[dict[str, Any]], after: list[dict[str, Any]]) -> list[dict[str, Any]]:
    before_map = {r.get("test_id"): r for r in before}
    after_map = {r.get("test_id"): r for r in after}
    ids = sorted(set(before_map) | set(after_map))
    rows = []
    for tid in ids:
        b = before_map.get(tid)
        a = after_map.get(tid)
        rows.append(
            {
                "test_id": tid,
                "before_status": (b or {}).get("status"),
                "after_status": (a or {}).get("status"),
                "before_severity": (b or {}).get("severity"),
                "after_severity": (a or {}).get("severity"),
                "changed": (b or {}).get("status") != (a or {}).get("status"),
            }
        )
    return rows
