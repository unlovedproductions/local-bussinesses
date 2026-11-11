"""Hard programmatic safety gates. Fail closed."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.config import Settings, load_sandbox_proof, load_test_settings


@dataclass
class SafetyDecision:
    allowed: bool
    status: str  # OK | BLOCKED
    reasons: list[str] = field(default_factory=list)

    def raise_if_blocked(self) -> None:
        if not self.allowed:
            raise PermissionError("; ".join(self.reasons) or "Blocked by safety policy")


def _all_proof_checks(proof: dict[str, Any] | None) -> bool:
    if not proof:
        return False
    checks = proof.get("proof_checks") or {}
    required = [
        "staging_agent_confirmed",
        "sandbox_calendar_id_matches",
        "booking_tools_inspected",
        "verification_adapter_configured",
        "synthetic_fixtures_exist",
        "side_effects_isolated",
        "production_calendar_not_targeted",
    ]
    return all(bool(checks.get(k)) for k in required) and bool(proof.get("approved"))


def assess_scenario(
    scenario: dict[str, Any],
    settings: Settings,
    *,
    run_mode: str,
    call_count: int,
) -> SafetyDecision:
    reasons: list[str] = []
    mode = (scenario.get("mode") or "").upper()
    safety = (scenario.get("safety_level") or "").upper()
    run_mode = run_mode.lower()
    test_settings = load_test_settings(settings)

    if call_count >= settings.max_calls:
        reasons.append(f"MAX_CALLS limit reached ({settings.max_calls})")

    if run_mode == "readonly" and safety == "SANDBOX":
        reasons.append("SANDBOX scenario blocked in readonly mode")

    if safety == "SANDBOX":
        if not settings.allow_sandbox_writes:
            reasons.append("ALLOW_SANDBOX_WRITES is not YES")
        proof = load_sandbox_proof(settings)
        if not _all_proof_checks(proof):
            reasons.append("sandbox_proof incomplete or not approved (provider proof required)")
        else:
            expected_agent = (proof or {}).get("staging_receptionist_agent_id") or ""
            if expected_agent and settings.receptionist_agent_id and expected_agent != settings.receptionist_agent_id:
                reasons.append("RECEPTIONIST_AGENT_ID does not match staging agent in sandbox_proof")
            expected_cal = (proof or {}).get("sandbox_calendar_id") or ""
            if expected_cal and settings.calcom_sandbox_calendar_id and expected_cal != settings.calcom_sandbox_calendar_id:
                reasons.append("CALCOM_SANDBOX_CALENDAR_ID does not match sandbox_proof")

    if mode == "VOICE":
        if settings.retell_call_mode == "phone":
            if not settings.ack_target_number:
                reasons.append("ACK_TARGET_NUMBER is not YES")
            if not settings.receptionist_phone_number:
                reasons.append("RECEPTIONIST_PHONE_NUMBER missing")
            if not settings.qa_outbound_number:
                reasons.append("QA_OUTBOUND_NUMBER missing")
            if not settings.qa_caller_agent_id:
                reasons.append("QA_CALLER_AGENT_ID missing")
        elif settings.retell_call_mode == "web":
            if not settings.receptionist_agent_id:
                reasons.append("RECEPTIONIST_AGENT_ID missing for web call mode")
        else:
            reasons.append(f"Unknown RETELL_CALL_MODE={settings.retell_call_mode}")

    if mode == "AUDIO" and test_settings.get("block_audio_without_adapter", True):
        if not settings.test_adapter_url:
            reasons.append("AUDIO mode requires TEST_ADAPTER_URL controlled-audio adapter")

    if mode == "FAULT" and test_settings.get("block_fault_without_adapter", True):
        if not settings.test_adapter_url:
            reasons.append("FAULT mode requires TEST_ADAPTER_URL fault-injection adapter")

    if mode == "DROP" and test_settings.get("block_drop_without_adapter", True):
        if not settings.test_adapter_url:
            reasons.append("DROP mode requires TEST_ADAPTER_URL disconnect adapter")

    # Capability-aware N/A hints are handled by orchestrator; safety only blocks unsafe exec.
    if not settings.retell_api_key and mode in {"VOICE"}:
        reasons.append("RETELL_API_KEY missing")

    if reasons:
        return SafetyDecision(allowed=False, status="BLOCKED", reasons=reasons)
    return SafetyDecision(allowed=True, status="OK", reasons=[])


def preflight_readonly(settings: Settings) -> SafetyDecision:
    reasons = []
    if not settings.retell_api_key:
        reasons.append("RETELL_API_KEY missing")
    if not settings.receptionist_agent_id:
        reasons.append("RECEPTIONIST_AGENT_ID missing")
    if reasons:
        return SafetyDecision(False, "BLOCKED", reasons)
    return SafetyDecision(True, "OK", [])


def preflight_sandbox(settings: Settings) -> SafetyDecision:
    base = preflight_readonly(settings)
    reasons = list(base.reasons)
    if not settings.allow_sandbox_writes:
        reasons.append("ALLOW_SANDBOX_WRITES is not YES")
    if not settings.ack_target_number and settings.retell_call_mode == "phone":
        reasons.append("ACK_TARGET_NUMBER is not YES")
    if not _all_proof_checks(load_sandbox_proof(settings)):
        reasons.append("sandbox_proof not fully approved")
    if not settings.calcom_api_key:
        reasons.append("CALCOM_API_KEY missing for calendar verification")
    if reasons:
        return SafetyDecision(False, "BLOCKED", reasons)
    return SafetyDecision(True, "OK", [])
