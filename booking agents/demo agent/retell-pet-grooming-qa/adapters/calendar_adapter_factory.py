"""Factory: prefer discovered provider; never invent connectivity."""
from __future__ import annotations

from typing import Any

from adapters.base_calendar import BaseCalendarAdapter
from src.config import Settings, load_business


class BlockedCalendarAdapter(BaseCalendarAdapter):
    provider_name = "blocked"

    def __init__(self, reason: str):
        self.reason = reason

    def healthcheck(self) -> dict[str, Any]:
        return {"ok": False, "provider": self.provider_name, "error": self.reason}

    def snapshot(self, *, calendar_id: str | None = None):
        raise RuntimeError(self.reason)

    def get_event(self, event_id: str):
        raise RuntimeError(self.reason)


def create_calendar_adapter(settings: Settings) -> BaseCalendarAdapter:
    business = load_business(settings)
    integrations = business.get("supported_integrations") or {}
    provider = (integrations.get("calendar_provider") or "").lower()
    if provider in {"cal.com", "calcom"} or settings.calcom_api_key:
        if not settings.calcom_api_key:
            return BlockedCalendarAdapter(
                "Cal.com identified as booking provider but CALCOM_API_KEY is not configured"
            )
        from adapters.calcom_adapter import CalComAdapter
        return CalComAdapter(settings)
    return BlockedCalendarAdapter(
        "Calendar provider not identified or credentials unavailable; "
        "inspect Retell tools and set provider adapter"
    )
