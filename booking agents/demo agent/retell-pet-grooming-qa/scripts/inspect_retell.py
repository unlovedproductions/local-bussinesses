#!/usr/bin/env python3
"""Read-only Retell inspection."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import load_settings
from src.retell_client import RetellAPIError, RetellClient


def main() -> int:
    settings = load_settings()
    if not settings.retell_api_key:
        print("RETELL_API_KEY missing — cannot inspect")
        return 1
    if not settings.receptionist_agent_id:
        print("RECEPTIONIST_AGENT_ID missing")
        return 1
    try:
        client = RetellClient(settings)
        agent = client.get_agent(settings.receptionist_agent_id)
    except RetellAPIError as exc:
        print("Inspect failed:", exc)
        print(exc.body)
        return 1
    # Redact potentially sensitive prompt content lengths only
    safe = {
        "agent_id": agent.get("agent_id"),
        "agent_name": agent.get("agent_name"),
        "voice_id": agent.get("voice_id"),
        "language": agent.get("language"),
        "keys": sorted(agent.keys()),
    }
    # Tools if present
    for key in ("tools", "general_tools", "response_engine"):
        if key in agent:
            val = agent[key]
            if isinstance(val, list):
                safe[key] = [
                    (t.get("name") if isinstance(t, dict) else str(type(t))) for t in val
                ]
            elif isinstance(val, dict):
                safe[key] = {"keys": sorted(val.keys())}
    print(json.dumps(safe, indent=2))
    print("READ-ONLY inspect complete. Production prompt was not modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
