"""Sandbox-only fault injection interface."""
from __future__ import annotations

from typing import Any


class FaultInjectionAdapter:
    """Inject faults only into approved sandbox services via TEST_ADAPTER_URL."""

    def __init__(self, adapter_url: str | None):
        self.adapter_url = (adapter_url or "").rstrip("/")

    @property
    def available(self) -> bool:
        return bool(self.adapter_url)

    def inject(self, fault_type: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.available:
            return {
                "ok": False,
                "status": "BLOCKED",
                "error": "Fault injection adapter unavailable; configure TEST_ADAPTER_URL for sandbox only",
                "fault_type": fault_type,
            }
        import httpx
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                f"{self.adapter_url}/faults",
                json={"fault_type": fault_type, "context": context or {}},
            )
        if resp.status_code >= 400:
            return {"ok": False, "status": "BLOCKED", "error": resp.text, "fault_type": fault_type}
        data = resp.json()
        data.setdefault("ok", True)
        return data

    def prove_fault(self, fault_id: str) -> dict[str, Any]:
        if not self.available:
            return {"ok": False, "proven": False, "error": "adapter unavailable"}
        import httpx
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(f"{self.adapter_url}/faults/{fault_id}")
        if resp.status_code >= 400:
            return {"ok": False, "proven": False, "error": resp.text}
        return resp.json()
