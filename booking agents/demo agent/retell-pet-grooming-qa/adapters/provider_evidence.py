"""Build verification evidence objects without LLM fabrication."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from adapters.base_calendar import CalendarSnapshot


def snapshot_to_dict(snap: CalendarSnapshot) -> dict[str, Any]:
    return {
        "provider": snap.provider,
        "calendar_id": snap.calendar_id,
        "captured_at": snap.captured_at,
        "event_count": len(snap.events),
        "event_ids": [
            e.get("uid") or e.get("id") for e in snap.events if isinstance(e, dict)
        ],
        "events": snap.events,
        "raw": snap.raw,
    }


def empty_blocked_evidence(reason: str, **extra: Any) -> dict[str, Any]:
    return {
        "verified": False,
        "status": "BLOCKED",
        "assertions": [],
        "before_snapshot": None,
        "after_snapshot": None,
        "tool_events": [],
        "event_ids": [],
        "evidence_references": [],
        "verification_errors": [reason],
        "captured_at": datetime.now(timezone.utc).isoformat(),
        **extra,
    }
