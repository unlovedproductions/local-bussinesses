"""Controlled audio / telephony simulator interface."""
from __future__ import annotations

from typing import Any


class ControlledAudioAdapter:
    def __init__(self, adapter_url: str | None):
        self.adapter_url = (adapter_url or "").rstrip("/")

    @property
    def available(self) -> bool:
        return bool(self.adapter_url)

    def run_scenario(self, scenario: dict[str, Any]) -> dict[str, Any]:
        if not self.available:
            return {
                "ok": False,
                "status": "BLOCKED",
                "error": (
                    "Controlled audio adapter unavailable. Retell-to-Retell AI callers cannot "
                    "reliably reproduce acoustic conditions; configure TEST_ADAPTER_URL."
                ),
            }
        import httpx
        with httpx.Client(timeout=120.0) as client:
            resp = client.post(f"{self.adapter_url}/audio/run", json={"scenario": scenario})
        if resp.status_code >= 400:
            return {"ok": False, "status": "BLOCKED", "error": resp.text}
        return resp.json()
