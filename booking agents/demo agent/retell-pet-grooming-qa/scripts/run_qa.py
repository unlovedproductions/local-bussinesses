#!/usr/bin/env python3
"""Run selected QA scenarios."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import load_settings
from src.qa_orchestrator import QAOrchestrator


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", required=True, help="Comma-separated IDs or ALL")
    parser.add_argument("--max-calls", type=int, default=None)
    parser.add_argument("--mode", choices=["readonly", "sandbox"], default="readonly")
    args = parser.parse_args()
    settings = load_settings()
    if args.max_calls is not None:
        settings.max_calls = args.max_calls
    orch = QAOrchestrator(settings)
    summary = orch.run(ids=args.ids, mode=args.mode, max_calls=args.max_calls)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
