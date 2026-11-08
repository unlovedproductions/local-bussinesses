#!/usr/bin/env python3
"""Regenerate reports for latest or specified run."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import load_settings
from src.report_generator import generate_reports
from src.scenario_loader import load_cases
from src.storage import latest_run_id, load_run_results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()
    settings = load_settings()
    run_id = args.run_id or latest_run_id(settings)
    if not run_id:
        print("No runs available")
        return 1
    results = load_run_results(settings, run_id)
    paths = generate_reports(settings, run_id, results, load_cases())
    print(json.dumps({k: str(v) for k, v in paths.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
