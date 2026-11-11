"""Load and filter the 108-scenario manifest."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.config import Settings, load_qa_vars, load_settings


REQUIRED_FIELDS = [
    "id",
    "suite",
    "title",
    "mode",
    "safety_level",
    "persona",
    "caller_goal",
    "opening_statement",
    "caller_behavior",
    "required_fixtures",
    "expected_behavior",
    "acceptance_criteria",
    "required_evidence",
    "required_oracles",
    "max_duration_seconds",
    "stop_conditions",
    "status",
]


def load_cases(path: Path | None = None) -> list[dict[str, Any]]:
    settings = load_settings()
    path = path or settings.cases_path
    data = json.loads(Path(path).read_text())
    if not isinstance(data, list):
        raise ValueError("cases.json must be a list")
    return data


def validate_cases(cases: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    ids = [c.get("id") for c in cases]
    if len(cases) != 108:
        errors.append(f"Expected 108 cases, found {len(cases)}")
    if len(set(ids)) != len(ids):
        errors.append("Duplicate scenario IDs detected")
    for c in cases:
        cid = c.get("id", "<missing>")
        for field in REQUIRED_FIELDS:
            if field not in c:
                errors.append(f"{cid}: missing field {field}")
        mode = (c.get("mode") or "").upper()
        if mode not in {"VOICE", "AUDIO", "FAULT", "DROP"}:
            errors.append(f"{cid}: invalid mode {mode}")
        safety = (c.get("safety_level") or "").upper()
        if safety not in {"READ_ONLY", "SANDBOX"}:
            errors.append(f"{cid}: invalid safety_level {safety}")
    return errors


def select_cases(
    cases: list[dict[str, Any]],
    ids: str | list[str],
) -> list[dict[str, Any]]:
    if isinstance(ids, str):
        raw = [x.strip() for x in ids.split(",") if x.strip()]
    else:
        raw = list(ids)
    if len(raw) == 1 and raw[0].upper() == "ALL":
        return list(cases)
    wanted = set(raw)
    selected = [c for c in cases if c.get("id") in wanted]
    missing = wanted - {c.get("id") for c in selected}
    if missing:
        raise KeyError(f"Unknown scenario IDs: {sorted(missing)}")
    # Preserve requested order
    by_id = {c["id"]: c for c in selected}
    return [by_id[i] for i in raw if i in by_id]


def render_qa_case(scenario: dict[str, Any], qa_vars: dict[str, Any] | None = None) -> str:
    """Caller-facing scenario packet for {{qa_case}} — never includes judge criteria secrets beyond what caller needs."""
    qa_vars = qa_vars or load_qa_vars()
    pets = qa_vars.get("pets") or {}
    owners = qa_vars.get("owners") or {}
    packet = {
        "test_id": scenario["id"],
        "persona": scenario["persona"],
        "objective": scenario["caller_goal"],
        "opening_statement": scenario["opening_statement"],
        "behavior_rules": scenario["caller_behavior"],
        "mode": scenario["mode"],
        "safety_level": scenario["safety_level"],
        "stop_conditions": scenario["stop_conditions"],
        "max_duration_seconds": scenario["max_duration_seconds"],
        "synthetic_data": {
            "owner": owners.get("demo_tester") or owners.get("alex_reed"),
            "primary_pet": (
                pets.get("pepper")
                if scenario.get("id") in {"D01", "D07", "D03", "D04", "D08"}
                else pets.get("mochi")
            ),
            "pet_mochi": pets.get("mochi"),
            "pet_luna": pets.get("luna"),
            "pet_pepper": pets.get("pepper"),
            "service": qa_vars.get("service"),
            "unsupported_service": qa_vars.get("unsupported_service"),
            "slots": qa_vars.get("slots"),
            "note_mochi_overweight": "Mochi is 28 lbs — ineligible for auto-book; use Pepper for successful booking scenarios.",
        },
        "rules": [
            "You are the CALLER, not the receptionist.",
            "Do not reveal QA scoring criteria.",
            "Do not invent salon prices or policies.",
            "Never propose past dates; use relative future days from the live conversation.",
            "If READ_ONLY: decline bookings and external actions.",
            "If SANDBOX: use only approved synthetic fixtures.",
            "When booking, provide email unlovedproducts@gmail.com if asked.",
        ],
    }
    import json
    return json.dumps(packet, indent=2)


def capability_na_reason(scenario: dict[str, Any], capabilities: dict[str, Any]) -> str | None:
    oracles = scenario.get("required_oracles") or []
    if "calendar.cancel" in oracles and not capabilities.get("cancel_via_voice_tools", False):
        # Still runnable as honest-fallback test if SANDBOX reads available; not auto N/A.
        return None
    if "crm.create" in oracles or "crm.callback" in oracles:
        if not capabilities.get("crm", False):
            return "CRM integration not configured; mark NOT_APPLICABLE or test honest fallback only"
    if "transfer.attempt" in oracles or "transfer.fallback" in oracles:
        if not capabilities.get("live_transfer", False):
            return None  # honest fallback is a valid expected behavior for this demo
    if "notification.no_send" in oracles and not capabilities.get("notifications", False):
        return "Notification integration not configured"
    return None
