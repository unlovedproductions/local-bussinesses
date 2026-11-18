#!/usr/bin/env python3
"""M5–M14 acceptance harness — exercises managed workflows without live provider calls."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COORD = ROOT / "coordination" / "scripts" / "coord.py"
CHECK = ROOT / "scripts" / "documentation" / "check_docs.py"
TEST_COORD = ROOT / "coordination" / "scripts" / "test_coord.py"


def run(args: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    full = os.environ.copy()
    if env:
        full.update(env)
    return subprocess.run(
        args,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env=full,
    )


def must_ok(proc: subprocess.CompletedProcess[str], label: str) -> None:
    if proc.returncode != 0:
        raise SystemExit(f"FAIL {label}: {proc.stderr or proc.stdout}")


def main() -> int:
    results: list[dict[str, str]] = []

    proc = run([sys.executable, str(TEST_COORD)])
    must_ok(proc, "test_coord")
    results.append({"id": "coord_unit", "result": "PASS"})

    proc = run([sys.executable, str(CHECK)])
    must_ok(proc, "check_docs")
    results.append({"id": "docs_drift", "result": "PASS"})

    proc = run([sys.executable, str(COORD), "memory-status"])
    must_ok(proc, "memory-status")
    mem = json.loads(proc.stdout)
    if not mem.get("semantic_memory", {}).get("config_present"):
        raise SystemExit("FAIL memory config missing")
    results.append({"id": "m5_memory_status", "result": "PASS"})

    proc = run([sys.executable, str(COORD), "integrations"])
    must_ok(proc, "integrations")
    integ = json.loads(proc.stdout)
    ids = {i["id"] for i in integ.get("integrations", [])}
    for required in ("retell-ai", "calcom", "supermemory", "erpnext"):
        if required not in ids:
            raise SystemExit(f"FAIL missing integration {required}")
    results.append({"id": "m6_integrations", "result": "PASS"})

    # Rejected integration cannot be enabled
    proposal = {
        "id": "test-tool-m14",
        "name": "Test Tool",
        "provider": "example",
        "purpose": "acceptance harness only",
        "status": "REJECTED",
        "essential": False,
        "agents": ["coordinator"],
        "permissions": [],
        "data_accessed": [],
        "auth": "none",
        "costs": "none",
        "notes": "ephemeral",
        "proposed_by": "coordinator",
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
        json.dump(proposal, tmp)
        tmp_path = tmp.name
    try:
        must_ok(
            run([sys.executable, str(COORD), "integration-propose", "--file", tmp_path]),
            "integration-propose",
        )
        bad = run(
            [
                sys.executable,
                str(COORD),
                "integration-set-status",
                "--id",
                "test-tool-m14",
                "--status",
                "ENABLED",
                "--agent",
                "coordinator",
            ]
        )
        if bad.returncode == 0:
            raise SystemExit("FAIL rejected integration was enabled")
        results.append({"id": "m6_approval_enforcement", "result": "PASS"})
    finally:
        Path(tmp_path).unlink(missing_ok=True)
        # remove ephemeral integration
        data = json.loads((ROOT / "coordination/config/integrations.json").read_text(encoding="utf-8"))
        data["integrations"] = [i for i in data["integrations"] if i.get("id") != "test-tool-m14"]
        (ROOT / "coordination/config/integrations.json").write_text(
            json.dumps(data, indent=2) + "\n", encoding="utf-8"
        )
        for path in (ROOT / "coordination/approvals/records").glob("APR-test-tool-m14-*.json"):
            path.unlink(missing_ok=True)

    proc = run([sys.executable, str(COORD), "workflows"])
    must_ok(proc, "workflows")
    if json.loads(proc.stdout)["count"] < 8:
        raise SystemExit("FAIL expected >=8 workflows")
    results.append({"id": "m7_workflows", "result": "PASS"})

    proc = run([sys.executable, str(COORD), "recovery-status"])
    must_ok(proc, "recovery-status")
    results.append({"id": "m9_recovery_status", "result": "PASS"})

    proc = run([sys.executable, str(COORD), "ops"])
    must_ok(proc, "ops")
    results.append({"id": "m13_ops", "result": "PASS"})

    # Research -> development style handoff (file bus)
    hid = "HANDOFF-M14-RESEARCH-LOOP"
    handoff_path = ROOT / "coordination" / "handoffs" / f"{hid}.json"
    if handoff_path.exists():
        handoff_path.unlink()
    must_ok(
        run(
            [
                sys.executable,
                str(COORD),
                "handoff-create",
                "--id",
                hid,
                "--sender",
                "market-research",
                "--recipient",
                "voice-development",
                "--subject",
                "M14 research-to-dev loop",
                "--requested-action",
                "Acknowledge sample feature evaluation request",
                "--background",
                "Acceptance harness — synthetic",
                "--priority",
                "P3",
            ]
        ),
        "handoff-create",
    )
    must_ok(
        run(
            [
                sys.executable,
                str(COORD),
                "handoff-transition",
                "--id",
                hid,
                "--agent",
                "voice-development",
                "--status",
                "ACKNOWLEDGED",
            ]
        ),
        "handoff-ack",
    )
    must_ok(
        run(
            [
                sys.executable,
                str(COORD),
                "handoff-transition",
                "--id",
                hid,
                "--agent",
                "voice-development",
                "--status",
                "IN_PROGRESS",
            ]
        ),
        "handoff-start",
    )
    must_ok(
        run(
            [
                sys.executable,
                str(COORD),
                "handoff-transition",
                "--id",
                hid,
                "--agent",
                "voice-development",
                "--status",
                "COMPLETED",
                "--summary",
                "Synthetic evaluation recorded for harness",
                "--evidence",
                "scripts/uan/run_m5_m14_acceptance.py",
            ]
        ),
        "handoff-complete",
    )
    results.append({"id": "m14_research_dev_loop", "result": "PASS"})

    # Doc impact style task
    plan = run(
        [
            sys.executable,
            str(COORD),
            "plan",
            "--objective",
            "documentation recovery release",
            "--dispatch",
        ]
    )
    must_ok(plan, "plan-dispatch")
    payload = json.loads(plan.stdout)
    if "documentation" not in payload.get("recommended_agents", []):
        raise SystemExit("FAIL documentation not recommended for doc objective")
    # cleanup created tasks
    for tid in payload.get("created_tasks") or []:
        for folder in (
            ROOT / "coordination/tasks/records",
            ROOT / "coordination/tasks/claims",
        ):
            p = folder / f"{tid}.json"
            if p.exists():
                p.unlink()
        for path in (ROOT / "coordination/tasks/attempts").glob(f"ATT-{tid}-*.json"):
            path.unlink(missing_ok=True)
    results.append({"id": "m14_doc_routing", "result": "PASS"})

    report = {
        "suite": "M5-M14",
        "overall": "PASS",
        "results": results,
        "limitations": [
            "No live Retell/Cal.com calls executed",
            "Supermemory MCP write verified separately in session; not from this script",
            "DR_EXPORT_DIR / secondary mirror still operator-owned",
        ],
    }
    out = ROOT / "docs" / "verification" / "M5_M14_ACCEPTANCE_RESULTS.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
