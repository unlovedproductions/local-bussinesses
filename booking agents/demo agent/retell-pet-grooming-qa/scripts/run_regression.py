#!/usr/bin/env python3
"""Run regression selection from latest run's regression plan."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import load_settings
from src.qa_orchestrator import QAOrchestrator
from src.storage import latest_run_id, load_run_results
from src.regression_generator import generate_regression_plan


def main() -> int:
    settings = load_settings()
    run_id = latest_run_id(settings)
    if not run_id:
        print("No prior QA runs found")
        return 1
    results = load_run_results(settings, run_id)
    plan = generate_regression_plan(results)
    ids = plan.get("recommended_retests") or []
    if not ids:
        print("No failed tests to regress")
        print(json.dumps(plan, indent=2))
        return 0
    print("Regression IDs:", ",".join(ids))
    orch = QAOrchestrator(settings)
    # Preserve original results; new run_id
    summary = orch.run(ids=",".join(ids), mode="sandbox" if settings.allow_sandbox_writes else "readonly")
    print(json.dumps({"prior_run": run_id, "plan": plan, "new_run": summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
