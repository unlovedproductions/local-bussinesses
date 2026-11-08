#!/usr/bin/env python3
"""Read-only / sandbox preflight checks. Fail closed."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import load_business, load_settings
from src.safety import preflight_readonly, preflight_sandbox


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["readonly", "sandbox"], default="readonly")
    args = parser.parse_args()
    settings = load_settings()
    business = load_business(settings)
    print("Business:", business.get("business_name"))
    print("Calendar provider:", (business.get("supported_integrations") or {}).get("calendar_provider"))
    print("Receptionist agent example:", (business.get("retell") or {}).get("receptionist_agent_id"))
    decision = preflight_readonly(settings) if args.mode == "readonly" else preflight_sandbox(settings)
    print(f"Preflight mode={args.mode} status={decision.status}")
    for r in decision.reasons:
        print(" -", r)
    if not decision.allowed:
        print("PREFLIGHT BLOCKED (fail closed)")
        return 1
    # Optional live Retell inspect without mutating
    if settings.retell_api_key and settings.receptionist_agent_id:
        try:
            from src.retell_client import RetellClient
            client = RetellClient(settings)
            agent = client.get_agent(settings.receptionist_agent_id)
            print("Retell agent reachable:", agent.get("agent_id") or agent.get("agent_name") or "ok")
        except Exception as exc:
            print("Retell inspect warning:", exc)
            if args.mode == "sandbox":
                print("PREFLIGHT BLOCKED")
                return 1
    print("PREFLIGHT OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
