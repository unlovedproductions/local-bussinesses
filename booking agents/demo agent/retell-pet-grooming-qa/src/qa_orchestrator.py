"""Test orchestrator — loads scenarios, enforces safety, runs calls, judges, stores."""
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from adapters.controlled_audio import ControlledAudioAdapter
from adapters.fault_injection import FaultInjectionAdapter
from adapters.integration_verifier import IntegrationVerifier
from src.call_correlator import correlate_inbound
from src.config import Settings, load_business, load_qa_vars, load_test_settings
from src.defect_classifier import classify_defects
from src.deterministic_assertions import run_deterministic_assertions, transcript_text
from src.evidence_collector import collect_call_evidence, persist_evidence
from src.qa_judge import judge_scenario
from src.report_generator import generate_reports
from src.retell_client import RetellAPIError, RetellClient
from src.safety import assess_scenario
from src.scenario_loader import capability_na_reason, load_cases, render_qa_case, select_cases
from src.storage import new_run_id, save_result, write_json, run_dir


class QAOrchestrator:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.business = load_business(settings)
        self.qa_vars = load_qa_vars(settings)
        self.test_settings = load_test_settings(settings)
        self.cases = load_cases(settings.cases_path)
        self.spent_usd = 0.0
        self.call_count = 0

    def run(
        self,
        *,
        ids: str,
        mode: str,
        max_calls: int | None = None,
        run_id: str | None = None,
    ) -> dict[str, Any]:
        if max_calls is not None:
            self.settings.max_calls = max_calls
        run_id = run_id or new_run_id()
        selected = select_cases(self.cases, ids)
        run_dir(self.settings, run_id)
        write_json(
            run_dir(self.settings, run_id) / "meta.json",
            {
                "run_id": run_id,
                "mode": mode,
                "ids": ids,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "max_calls": self.settings.max_calls,
            },
        )
        results: list[dict[str, Any]] = []
        for scenario in selected:
            if self.call_count >= self.settings.max_calls and scenario.get("mode") in {"VOICE", "AUDIO", "FAULT", "DROP"}:
                # Still allow pure blocked recording without placing calls? Mark remaining blocked.
                result = self._blocked(scenario, [f"MAX_CALLS={self.settings.max_calls} reached"])
                save_result(self.settings, run_id, result)
                results.append(result)
                continue
            result = self.run_one(scenario, run_mode=mode, run_id=run_id)
            save_result(self.settings, run_id, result)
            results.append(result)
        reports = generate_reports(self.settings, run_id, results, self.cases)
        summary = {
            "run_id": run_id,
            "results": [
                {"test_id": r.get("test_id"), "status": r.get("status"), "severity": r.get("severity")}
                for r in results
            ],
            "reports": {k: str(v) for k, v in reports.items()},
        }
        write_json(run_dir(self.settings, run_id) / "summary.json", summary)
        return summary

    def run_one(self, scenario: dict[str, Any], *, run_mode: str, run_id: str) -> dict[str, Any]:
        test_id = scenario["id"]
        caps = self.test_settings.get("capabilities") or {}
        na = capability_na_reason(scenario, caps)
        # CRM-required creates without CRM => NOT_APPLICABLE (honest)
        oracles = scenario.get("required_oracles") or []
        if any(o.startswith("crm.") and o.endswith(("create", "update", "callback", "dedupe")) for o in oracles):
            if not caps.get("crm", False) and "recovery" not in oracles and "crm.no_write" not in oracles:
                return self._na(scenario, "CRM not configured on this receptionist; cannot verify CRM writes")

        decision = assess_scenario(scenario, self.settings, run_mode=run_mode, call_count=self.call_count)
        if not decision.allowed:
            return self._blocked(scenario, decision.reasons)

        mode = (scenario.get("mode") or "").upper()
        if mode == "AUDIO":
            return self._run_audio(scenario, run_id=run_id)
        if mode == "FAULT":
            return self._run_fault(scenario, run_id=run_id)
        if mode == "DROP":
            return self._run_drop(scenario, run_id=run_id)
        return self._run_voice(scenario, run_id=run_id)

    def _base_result(self, scenario: dict[str, Any]) -> dict[str, Any]:
        return {
            "test_id": scenario["id"],
            "suite": scenario.get("suite"),
            "title": scenario.get("title"),
            "persona": scenario.get("persona"),
            "mode": scenario.get("mode"),
            "safety_level": scenario.get("safety_level"),
            "expected_behavior": scenario.get("expected_behavior"),
            "status": "NOT_RUN",
            "severity": "NONE",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _blocked(
        self,
        scenario: dict[str, Any],
        reasons: list[str],
        partial: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        r = self._base_result(scenario)
        r.update(
            {
                "status": "BLOCKED",
                "observed_behavior": "; ".join(reasons),
                "block_reasons": reasons,
                "task_completed": False,
                "defects": [],
                "dimension_scores": {},
                "confidence": 1.0,
            }
        )
        if partial:
            r.update(partial)
        return r

    def _na(self, scenario: dict[str, Any], reason: str) -> dict[str, Any]:
        r = self._base_result(scenario)
        r.update(
            {
                "status": "NOT_APPLICABLE",
                "observed_behavior": reason,
                "severity": "NONE",
                "task_completed": None,
                "defects": [],
                "dimension_scores": {},
                "confidence": 1.0,
            }
        )
        return r

    def _budget_ok(self) -> bool:
        return self.spent_usd < self.settings.max_run_spend_usd

    def _run_voice(self, scenario: dict[str, Any], *, run_id: str) -> dict[str, Any]:
        if not self._budget_ok():
            return self._blocked(scenario, [f"MAX_RUN_SPEND_USD={self.settings.max_run_spend_usd} exceeded"])

        needs_calendar = any(
            o.startswith("calendar.") for o in (scenario.get("required_oracles") or [])
        )
        before = None
        verifier = None
        if needs_calendar or scenario.get("safety_level") == "SANDBOX":
            try:
                verifier = IntegrationVerifier(self.settings)
                before = verifier.capture_snapshot()
                if before.get("status") == "BLOCKED" and needs_calendar:
                    return self._blocked(scenario, before.get("verification_errors") or ["calendar snapshot blocked"])
            except Exception as exc:
                if needs_calendar:
                    return self._blocked(scenario, [f"Calendar verifier unavailable: {exc}"])

        try:
            client = RetellClient(self.settings)
        except RetellAPIError as exc:
            return self._blocked(scenario, [str(exc)])

        qa_case = render_qa_case(scenario, self.qa_vars)
        idem = f"qa-{scenario['id']}-{uuid4().hex[:10]}"
        metadata = {
            "qa_run_id": run_id,
            "qa_test_id": scenario["id"],
            "qa_safety_level": scenario.get("safety_level"),
        }

        try:
            if self.settings.retell_call_mode == "phone":
                outbound = client.create_phone_call(
                    from_number=self.settings.qa_outbound_number,
                    to_number=self.settings.receptionist_phone_number,
                    override_agent_id=self.settings.qa_caller_agent_id,
                    metadata=metadata,
                    retell_llm_dynamic_variables={"qa_case": qa_case},
                    idempotency_key=idem,
                )
            else:
                return self._blocked(
                    scenario,
                    [
                        "VOICE Retell-to-Retell requires RETELL_CALL_MODE=phone with authorized numbers; "
                        "web mode is not a substitute for the QA caller agent"
                    ],
                )
        except RetellAPIError as exc:
            return self._blocked(scenario, [f"create-phone-call failed: {exc}", str(exc.body)])

        self.call_count += 1
        outbound_id = outbound.get("call_id")
        max_wait = min(
            int(scenario.get("max_duration_seconds") or self.settings.max_call_duration_seconds) + 60,
            self.settings.max_call_duration_seconds + 120,
        )
        try:
            outbound_final = client.wait_for_call_end(outbound_id, timeout_seconds=max_wait)
        except RetellAPIError as exc:
            return self._blocked(scenario, [str(exc)], partial={"outbound_call_id": outbound_id})

        # Cost tracking if present (Retell often returns cents-like combined_cost)
        cost = ((outbound_final.get("call_cost") or {}).get("combined_cost"))
        if isinstance(cost, (int, float)):
            # Docs show integer unit costs; treat as USD cents if > 10 else USD
            self.spent_usd += (cost / 100.0) if cost > 10 else float(cost)

        time.sleep(float(self.test_settings.get("call_settle_seconds") or 8))
        corr = correlate_inbound(
            client,
            outbound_call=outbound_final,
            receptionist_agent_id=self.settings.receptionist_agent_id,
            window_ms=int(self.test_settings.get("correlation_window_seconds") or 120) * 1000,
        )
        if corr.get("status") != "OK":
            result = self._blocked(scenario, [corr.get("reason") or "correlation failed"])
            result["call_ids"] = {"outbound": outbound_id}
            result["correlation"] = corr
            return result

        inbound = corr["inbound_call"]
        inbound_id = inbound.get("call_id")
        try:
            if (inbound.get("call_status") or "").lower() not in {"ended", "error"}:
                inbound = client.wait_for_call_end(inbound_id, timeout_seconds=max_wait)
        except RetellAPIError:
            inbound = client.get_call(inbound_id)

        receptionist_evidence = collect_call_evidence(client, inbound_id)
        outbound_evidence = collect_call_evidence(client, outbound_id)

        after = None
        verification = None
        if verifier is not None:
            after = verifier.capture_snapshot()
            verification = verifier.verify(
                run_id=run_id,
                test_id=scenario["id"],
                receptionist_call_id=inbound_id,
                expected_outcome={},
                required_oracles=scenario.get("required_oracles") or [],
                before_snapshot=before,
                after_snapshot=after,
                tool_events=receptionist_evidence.get("tool_events") or [],
                sandbox_calendar_id=self.settings.calcom_sandbox_calendar_id,
            )

        deterministic = run_deterministic_assertions(
            scenario,
            business=self.business,
            transcript=receptionist_evidence.get("transcript"),
            verification=verification,
        )
        judge = judge_scenario(
            self.settings,
            scenario,
            business=self.business,
            transcript=receptionist_evidence.get("transcript"),
            call_metadata={
                "outbound": outbound_evidence,
                "inbound": {
                    k: receptionist_evidence.get(k)
                    for k in (
                        "call_id",
                        "call_status",
                        "duration_ms",
                        "disconnection_reason",
                        "latency",
                        "recording_url",
                    )
                },
            },
            verification=verification,
            deterministic=deterministic,
        )
        defects = classify_defects(
            test_id=scenario["id"],
            judge_result=judge,
            transcript_excerpt=transcript_text(receptionist_evidence.get("transcript") or []),
            backend_evidence=verification,
        )
        evidence = {
            "outbound": outbound_evidence,
            "receptionist": receptionist_evidence,
            "before_snapshot": before,
            "after_snapshot": after,
            "verification": verification,
            "deterministic": deterministic,
        }
        evidence_path = persist_evidence(self.settings, run_id, scenario["id"], evidence)

        result = self._base_result(scenario)
        result.update(
            {
                "status": judge.get("status"),
                "severity": judge.get("severity") or "NONE",
                "task_completed": judge.get("task_completed"),
                "observed_behavior": judge.get("observed_behavior"),
                "expected_behavior": judge.get("expected_behavior") or scenario.get("expected_behavior"),
                "evidence": judge.get("evidence"),
                "evidence_path": evidence_path,
                "defects": defects,
                "likely_root_cause": judge.get("likely_root_cause"),
                "recommended_fix": judge.get("recommended_fix"),
                "regression_tests": judge.get("regression_tests") or [],
                "dimension_scores": judge.get("dimension_scores") or {},
                "confidence": judge.get("confidence"),
                "call_ids": {"outbound": outbound_id, "receptionist": inbound_id},
                "transcript": receptionist_evidence.get("transcript"),
                "tool_events": receptionist_evidence.get("tool_events"),
                "verification": verification,
                "duration": receptionist_evidence.get("duration_ms"),
                "timestamps": {
                    "outbound_start": outbound_evidence.get("start_timestamp"),
                    "inbound_start": receptionist_evidence.get("start_timestamp"),
                },
            }
        )
        return result

    def _run_audio(self, scenario: dict[str, Any], *, run_id: str) -> dict[str, Any]:
        adapter = ControlledAudioAdapter(self.settings.test_adapter_url)
        outcome = adapter.run_scenario(scenario)
        if not outcome.get("ok"):
            return self._blocked(scenario, [outcome.get("error") or "audio adapter failed"])
        # If adapter returns transcript/evidence, judge it
        transcript = outcome.get("transcript")
        deterministic = run_deterministic_assertions(
            scenario, business=self.business, transcript=transcript, verification=None
        )
        judge = judge_scenario(
            self.settings,
            scenario,
            business=self.business,
            transcript=transcript,
            call_metadata=outcome.get("metadata"),
            verification=None,
            deterministic=deterministic,
        )
        result = self._base_result(scenario)
        result.update(judge)
        result["adapter"] = "controlled_audio"
        persist_evidence(self.settings, run_id, scenario["id"], {"audio": outcome, "judge": judge})
        return result

    def _run_fault(self, scenario: dict[str, Any], *, run_id: str) -> dict[str, Any]:
        fault = FaultInjectionAdapter(self.settings.test_adapter_url)
        injected = fault.inject("scenario_fault", {"test_id": scenario["id"]})
        if not injected.get("ok"):
            return self._blocked(scenario, [injected.get("error") or "fault injection unavailable"])
        fault_id = injected.get("fault_id")
        proof = fault.prove_fault(fault_id) if fault_id else {"proven": False}
        if not proof.get("proven"):
            return self._blocked(scenario, ["Fault injection could not be independently proven"])
        # After proven fault, execute voice path if phone configured
        voice = self._run_voice(scenario, run_id=run_id)
        voice["fault_injection"] = {"injected": injected, "proof": proof}
        return voice

    def _run_drop(self, scenario: dict[str, Any], *, run_id: str) -> dict[str, Any]:
        adapter = ControlledAudioAdapter(self.settings.test_adapter_url)
        if not adapter.available:
            return self._blocked(scenario, ["DROP requires controlled disconnect adapter (TEST_ADAPTER_URL)"])
        outcome = adapter.run_scenario({**scenario, "action": "disconnect_before_confirmation"})
        if not outcome.get("ok"):
            return self._blocked(scenario, [outcome.get("error") or "drop adapter failed"])
        # Verify calendar unchanged when required
        verification = None
        if any(o.startswith("calendar.") for o in (scenario.get("required_oracles") or [])):
            try:
                verifier = IntegrationVerifier(self.settings)
                before = verifier.capture_snapshot()
                after = before  # disconnect should not create; compare identical snapshot ids
                verification = verifier.verify(
                    run_id=run_id,
                    test_id=scenario["id"],
                    receptionist_call_id=outcome.get("call_id"),
                    expected_outcome={},
                    required_oracles=scenario.get("required_oracles") or [],
                    before_snapshot=before,
                    after_snapshot=after,
                    tool_events=[],
                )
            except Exception as exc:
                return self._blocked(scenario, [str(exc)])
        deterministic = run_deterministic_assertions(
            scenario,
            business=self.business,
            transcript=outcome.get("transcript"),
            verification=verification,
        )
        judge = judge_scenario(
            self.settings,
            scenario,
            business=self.business,
            transcript=outcome.get("transcript"),
            call_metadata=outcome,
            verification=verification,
            deterministic=deterministic,
        )
        result = self._base_result(scenario)
        result.update(judge)
        result["verification"] = verification
        persist_evidence(self.settings, run_id, scenario["id"], {"drop": outcome, "verification": verification})
        return result
