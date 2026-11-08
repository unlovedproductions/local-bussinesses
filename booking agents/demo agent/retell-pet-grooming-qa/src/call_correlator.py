"""Correlate QA outbound call with receptionist inbound call."""
from __future__ import annotations

from typing import Any

from src.retell_client import RetellClient


def correlate_inbound(
    client: RetellClient,
    *,
    outbound_call: dict[str, Any],
    receptionist_agent_id: str,
    window_ms: int = 120_000,
) -> dict[str, Any]:
    """Find matching inbound receptionist call. Ambiguity => BLOCKED."""
    start = outbound_call.get("start_timestamp")
    if start is None:
        # Some payloads use start_timestamp_ms
        start = outbound_call.get("start_timestamp_ms")
    if start is None:
        return {"status": "BLOCKED", "reason": "Outbound call missing start timestamp", "candidates": []}

    payload = {
        "filter_criteria": {
            "agent_id": [receptionist_agent_id],
            "direction": ["inbound"],
        },
        "sort_order": "descending",
        "limit": 25,
    }
    try:
        listed = client.list_calls(payload)
    except Exception as exc:
        return {"status": "BLOCKED", "reason": f"list-calls failed: {exc}", "candidates": []}

    calls = listed.get("calls") if isinstance(listed, dict) else listed
    if not isinstance(calls, list):
        calls = []

    candidates = []
    for c in calls:
        if not isinstance(c, dict):
            continue
        ts = c.get("start_timestamp") or c.get("start_timestamp_ms") or 0
        try:
            ts_i = int(ts)
            start_i = int(start)
        except (TypeError, ValueError):
            continue
        if abs(ts_i - start_i) <= window_ms:
            candidates.append(c)

    # Also match by to/from numbers when present
    out_from = outbound_call.get("from_number")
    out_to = outbound_call.get("to_number")
    number_matched = []
    for c in candidates:
        if out_from and c.get("to_number") == out_from:
            number_matched.append(c)
        elif out_to and c.get("from_number") == out_to:
            number_matched.append(c)

    pool = number_matched or candidates
    if len(pool) == 1:
        return {"status": "OK", "inbound_call": pool[0], "candidates": pool}
    if len(pool) == 0:
        return {"status": "BLOCKED", "reason": "No inbound receptionist call found in correlation window", "candidates": []}
    return {
        "status": "BLOCKED",
        "reason": f"Ambiguous correlation: {len(pool)} inbound candidates",
        "candidates": [{"call_id": c.get("call_id"), "start_timestamp": c.get("start_timestamp")} for c in pool],
    }
