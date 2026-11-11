"""Cal.com v2 calendar verification adapter (discovered provider for Taft demo)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from adapters.base_calendar import BaseCalendarAdapter, CalendarSnapshot
from src.config import Settings


class CalComAdapter(BaseCalendarAdapter):
    provider_name = "cal.com"

    def __init__(self, settings: Settings):
        self.settings = settings
        if not settings.calcom_api_key:
            raise RuntimeError("CALCOM_API_KEY is required for Cal.com verification")
        self.base = settings.calcom_api_base.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {settings.calcom_api_key}",
            "cal-api-version": settings.calcom_api_version,
            "Content-Type": "application/json",
            "Accept": "application/json",
            # Cloudflare blocks bare urllib/httpx clients without a UA (error 1010).
            "User-Agent": "Mozilla/5.0 (compatible; retell-pet-grooming-qa/1.0)",
        }

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        with httpx.Client(timeout=45.0) as client:
            resp = client.get(f"{self.base}{path}", headers=self.headers, params=params)
        if resp.status_code >= 400:
            raise RuntimeError(f"Cal.com GET {path} failed: HTTP {resp.status_code} {resp.text[:500]}")
        return resp.json()

    def healthcheck(self) -> dict[str, Any]:
        try:
            data = self._get("/bookings", params={"take": 1})
            return {"ok": True, "provider": self.provider_name, "sample": bool(data)}
        except Exception as exc:
            return {"ok": False, "provider": self.provider_name, "error": str(exc)}

    def snapshot(self, *, calendar_id: str | None = None) -> CalendarSnapshot:
        calendar_id = calendar_id or self.settings.calcom_sandbox_calendar_id or self.settings.calcom_event_type_id
        params: dict[str, Any] = {"take": 100}
        # Prefer event type filter when available
        if self.settings.calcom_event_type_id:
            # Some Cal.com deployments accept eventTypeId; keep raw list if rejected.
            params["eventTypeId"] = self.settings.calcom_event_type_id
        try:
            data = self._get("/bookings", params=params)
        except RuntimeError:
            data = self._get("/bookings", params={"take": 100})
        events = data.get("data") if isinstance(data, dict) else data
        if not isinstance(events, list):
            events = []
        return CalendarSnapshot(
            provider=self.provider_name,
            calendar_id=str(calendar_id or ""),
            captured_at=datetime.now(timezone.utc).isoformat(),
            events=events,
            raw={"count": len(events)},
        )

    def get_event(self, event_id: str) -> dict[str, Any] | None:
        data = self._get(f"/bookings/{event_id}")
        if isinstance(data, dict):
            return data.get("data") or data
        return None
