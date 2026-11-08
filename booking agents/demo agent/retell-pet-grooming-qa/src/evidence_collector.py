"""Collect call, tool, and calendar evidence."""
from __future__ import annotations

from typing import Any

from adapters.integration_verifier import IntegrationVerifier
from src.config import Settings
from src.retell_client import RetellClient
from src.storage import run_dir, write_json


def collect_call_evidence(client: RetellClient, call_id: str) -> dict[str, Any]:
    call = client.get_call(call_id)
    return {
        "call_id": call_id,
        "call_status": call.get("call_status"),
        "agent_id": call.get("agent_id"),
        "direction": call.get("direction"),
        "from_number": call.get("from_number"),
        "to_number": call.get("to_number"),
        "start_timestamp": call.get("start_timestamp") or call.get("start_timestamp_ms"),
        "end_timestamp": call.get("end_timestamp") or call.get("end_timestamp_ms"),
        "duration_ms": call.get("duration_ms"),
        "disconnection_reason": call.get("disconnection_reason"),
        "recording_url": call.get("recording_url"),
        "public_log_url": call.get("public_log_url"),
        "transcript": client.extract_transcript(call),
        "tool_events": client.extract_tool_calls(call),
        "latency": call.get("latency"),
        "call_cost": call.get("call_cost"),
        "call_analysis": call.get("call_analysis"),
        "raw_keys": sorted(call.keys()),
    }


def persist_evidence(settings: Settings, run_id: str, test_id: str, evidence: dict[str, Any]) -> str:
    path = run_dir(settings, run_id) / "evidence" / f"{test_id}.json"
    write_json(path, evidence)
    return str(path)


def collect_calendar_pair(settings: Settings) -> tuple[dict[str, Any], IntegrationVerifier]:
    verifier = IntegrationVerifier(settings)
    before = verifier.capture_snapshot()
    return before, verifier
