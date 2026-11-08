"""Independent integration verifier (deterministic; no LLM evidence)."""
from __future__ import annotations

from typing import Any

from adapters.calendar_adapter_factory import create_calendar_adapter
from adapters.provider_evidence import empty_blocked_evidence, snapshot_to_dict
from src.config import Settings


class IntegrationVerifier:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.adapter = create_calendar_adapter(settings)

    def verify(
        self,
        *,
        run_id: str,
        test_id: str,
        receptionist_call_id: str | None,
        expected_outcome: dict[str, Any],
        required_oracles: list[str],
        before_snapshot: dict[str, Any] | None,
        after_snapshot: dict[str, Any] | None,
        tool_events: list[dict[str, Any]] | None = None,
        sandbox_calendar_id: str | None = None,
    ) -> dict[str, Any]:
        health = self.adapter.healthcheck()
        if not health.get("ok"):
            return empty_blocked_evidence(
                health.get("error") or "Calendar adapter unhealthy",
                run_id=run_id,
                test_id=test_id,
                receptionist_call_id=receptionist_call_id,
            )

        assertions: list[dict[str, Any]] = []
        errors: list[str] = []
        before_ids = set((before_snapshot or {}).get("event_ids") or [])
        after_ids = set((after_snapshot or {}).get("event_ids") or [])
        created = sorted(after_ids - before_ids)
        removed = sorted(before_ids - after_ids)

        def add(name: str, passed: bool, detail: str) -> None:
            assertions.append({"name": name, "passed": passed, "detail": detail})
            if not passed:
                errors.append(f"{name}: {detail}")

        for oracle in required_oracles:
            if oracle == "calendar.create":
                add("exactly_one_new_event", len(created) == 1, f"created={created}")
            elif oracle == "calendar.no_create":
                add("no_new_events", len(created) == 0, f"created={created}")
            elif oracle == "calendar.cancel":
                # Prefer status change evidence over mere absence
                cancelled_flag = expected_outcome.get("cancelled_uid")
                if cancelled_flag:
                    try:
                        ev = self.adapter.get_event(str(cancelled_flag))
                        status = (ev or {}).get("status")
                        add(
                            "cancelled_status",
                            str(status).lower() in {"cancelled", "canceled"},
                            f"uid={cancelled_flag} status={status}",
                        )
                    except Exception as exc:
                        add("cancelled_status", False, str(exc))
                else:
                    add(
                        "cancel_evidence",
                        len(removed) >= 1 or any(
                            str((e or {}).get("status", "")).lower() in {"cancelled", "canceled"}
                            for e in (after_snapshot or {}).get("events") or []
                        ),
                        f"removed={removed}",
                    )
            elif oracle == "calendar.no_duplicate":
                add("no_duplicate_create", len(created) == 0, f"created={created}")
            elif oracle == "calendar.check":
                add("availability_evidence_present", after_snapshot is not None, "after snapshot required")
            elif oracle.startswith("calendar."):
                add(oracle, after_snapshot is not None, "snapshot present for calendar oracle")
            elif oracle.startswith("crm.") or oracle.startswith("transfer.") or oracle.startswith("notification."):
                add(oracle, False, f"Oracle {oracle} has no configured verifier; BLOCKED/NOT_APPLICABLE upstream")
            elif oracle in {"dialogue", "kb", "security", "recovery"}:
                # Conversational oracles judged elsewhere
                add(oracle, True, "deferred to transcript/judge")

        # Spoken success claim without backend create is handled by judge + these asserts.
        verified = all(a["passed"] for a in assertions) if assertions else False
        status = "PASS" if verified and not errors else ("FAIL" if assertions else "BLOCKED")
        # If only deferred conversational oracles, mark inconclusive for integration layer
        calendar_oracles = [o for o in required_oracles if o.startswith("calendar.")]
        if not calendar_oracles and not any(o.startswith(("crm.", "transfer.", "notification.")) for o in required_oracles):
            status = "NOT_APPLICABLE"
            verified = True

        return {
            "verified": verified and status in {"PASS", "NOT_APPLICABLE"},
            "status": status,
            "assertions": assertions,
            "before_snapshot": before_snapshot,
            "after_snapshot": after_snapshot,
            "tool_events": tool_events or [],
            "event_ids": {
                "before": sorted(before_ids),
                "after": sorted(after_ids),
                "created": created,
                "removed": removed,
            },
            "evidence_references": [
                f"provider:{getattr(self.adapter, 'provider_name', 'unknown')}",
                f"sandbox_calendar_id:{sandbox_calendar_id or self.settings.calcom_sandbox_calendar_id}",
                f"receptionist_call_id:{receptionist_call_id}",
            ],
            "verification_errors": errors,
            "run_id": run_id,
            "test_id": test_id,
        }

    def capture_snapshot(self) -> dict[str, Any]:
        try:
            snap = self.adapter.snapshot()
            return snapshot_to_dict(snap)
        except Exception as exc:
            return empty_blocked_evidence(str(exc))
