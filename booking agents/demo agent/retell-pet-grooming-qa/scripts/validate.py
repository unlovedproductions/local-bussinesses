#!/usr/bin/env python3
"""Validate the 108-scenario manifest."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.scenario_loader import load_cases, validate_cases


def main() -> int:
    cases = load_cases()
    errors = validate_cases(cases)
    print(f"Scenarios: {len(cases)}")
    print(f"Unique IDs: {len({c['id'] for c in cases})}")
    suites = {}
    for c in cases:
        suites[c["suite"]] = suites.get(c["suite"], 0) + 1
    print("Suite counts:", suites)
    if errors:
        print("VALIDATION FAILED")
        for e in errors:
            print(" -", e)
        return 1
    print("VALIDATION OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
