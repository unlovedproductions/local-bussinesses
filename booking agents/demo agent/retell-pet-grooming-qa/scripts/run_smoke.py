#!/usr/bin/env python3
"""Run first three smoke tests A01,A02,A05 in readonly mode."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import load_settings
from src.qa_orchestrator import QAOrchestrator
from src.safety import preflight_readonly


def main() -> int:
    settings = load_settings()
    decision = preflight_readonly(settings)
    if not decision.allowed:
        print("Smoke blocked by preflight:")
        for r in decision.reasons:
            print(" -", r)
        print("Configure credentials, then re-run. No fabricated PASS.")
        # Still record blocked outcomes locally for dashboard honesty
    orch = QAOrchestrator(settings)
    summary = orch.run(ids="A01,A02,A05", mode="readonly", max_calls=3)
    print(json.dumps(summary, indent=2))
    statuses = {r["status"] for r in summary["results"]}
    if statuses <= {"BLOCKED", "NOT_APPLICABLE"}:
        print("Smoke finished without live passes — configure phone/QA caller and ACK_TARGET_NUMBER.")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
